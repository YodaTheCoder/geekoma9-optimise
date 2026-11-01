from __future__ import annotations

import http.client
import http.server
import importlib.util
import json
import socket
import threading
from pathlib import Path

import pytest

from harness.usage import UsageSummary, summarize_usage

_PROXY_PATH = Path(__file__).resolve().parent.parent / "harness" / "remote_scripts" / "usage_proxy.py"
_spec = importlib.util.spec_from_file_location("usage_proxy", _PROXY_PATH)
usage_proxy = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(usage_proxy)
extract_usage = usage_proxy.extract_usage


def test_extract_openai_json():
    body = json.dumps({"usage": {"prompt_tokens": 12, "completion_tokens": 34}}).encode()
    assert extract_usage(body, "application/json") == (12, 34)


def test_extract_openai_sse_last_chunk_usage():
    body = (
        b'data: {"choices":[{"delta":{"content":"hi"}}]}\n\n'
        b'data: {"choices":[],"usage":{"prompt_tokens":100,"completion_tokens":7}}\n\n'
        b"data: [DONE]\n\n"
    )
    assert extract_usage(body, "text/event-stream") == (100, 7)


def test_extract_anthropic_sse():
    body = (
        b"event: message_start\n"
        b'data: {"type":"message_start","message":{"usage":{"input_tokens":250,"output_tokens":1}}}\n\n'
        b"event: content_block_delta\n"
        b'data: {"type":"content_block_delta","delta":{"text":"x"}}\n\n'
        b"event: message_delta\n"
        b'data: {"type":"message_delta","usage":{"output_tokens":42}}\n\n'
        b"event: message_stop\n"
        b'data: {"type":"message_stop"}\n\n'
    )
    assert extract_usage(body, "text/event-stream") == (250, 42)


def test_extract_ollama_ndjson():
    body = (
        b'{"message":{"content":"a"},"done":false}\n'
        b'{"message":{"content":""},"done":true,"prompt_eval_count":55,"eval_count":9}\n'
    )
    assert extract_usage(body, "application/x-ndjson") == (55, 9)


def test_extract_ollama_json():
    body = json.dumps({"done": True, "prompt_eval_count": 5, "eval_count": 6}).encode()
    assert extract_usage(body, "application/json") == (5, 6)


def test_extract_unknown_body():
    assert extract_usage(b"hello world", "text/plain") == (None, None)
    assert extract_usage(b"", "") == (None, None)
    assert extract_usage(b'{"foo": 1}', "application/json") == (None, None)


def test_summarize_arithmetic():
    lines = "\n".join(
        json.dumps(d)
        for d in [
            {"path": "/a", "status": 200, "duration_s": 3.0, "ttft_s": 1.0,
             "prompt_tokens": 1000, "gen_tokens": 40, "upstream_error": False},
            {"path": "/a", "status": 200, "duration_s": 7.0, "ttft_s": 3.0,
             "prompt_tokens": 3000, "gen_tokens": 120, "upstream_error": False},
        ]
    )
    s = summarize_usage(lines + "\n")
    assert s == UsageSummary(requests=2, prompt_tokens=4000, gen_tokens=160,
                             pp_tps=1000.0, tg_tps=160 / 6, upstream_errors=0)


def test_summarize_counts_errors_and_unknown_tokens():
    lines = "\n".join(
        json.dumps(d)
        for d in [
            {"path": "/a", "status": 502, "duration_s": 0.01, "ttft_s": None,
             "prompt_tokens": None, "gen_tokens": None, "upstream_error": True},
            {"path": "/b", "status": 200, "duration_s": 1.0, "ttft_s": 0.5,
             "prompt_tokens": None, "gen_tokens": None, "upstream_error": False},
        ]
    )
    s = summarize_usage(lines)
    assert s.requests == 2
    assert s.upstream_errors == 1
    assert s.prompt_tokens is None and s.gen_tokens is None
    assert s.pp_tps is None and s.tg_tps is None


def test_summarize_empty():
    assert summarize_usage("") == UsageSummary(0, None, None, None, None, 0)


# ---------------------------------------------------------------- live

def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _rows(log, n, timeout=5.0):
    import time
    end = time.time() + timeout
    while time.time() < end:
        if log.exists():
            rows = [json.loads(l) for l in log.read_text().splitlines() if l.strip()]
            if len(rows) >= n:
                return rows
        time.sleep(0.05)
    raise AssertionError(f"log never reached {n} rows")


def _start(handler, log):
    upstream = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=upstream.serve_forever, daemon=True).start()
    proxy = usage_proxy.make_server("127.0.0.1", 0,
                                    f"http://127.0.0.1:{upstream.server_address[1]}", str(log))
    threading.Thread(target=proxy.serve_forever, daemon=True).start()
    return upstream, proxy


def _stop(*servers):
    for s in servers:
        s.shutdown()
        s.server_close()


class _Stub(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        self.rfile.read(n)
        body = json.dumps({"usage": {"prompt_tokens": 11, "completion_tokens": 22}}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


@pytest.mark.live
def test_proxy_live(tmp_path):
    upstream = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _Stub)
    threading.Thread(target=upstream.serve_forever, daemon=True).start()
    log = tmp_path / "usage.jsonl"
    proxy = usage_proxy.make_server("127.0.0.1", 0,
                                    f"http://127.0.0.1:{upstream.server_address[1]}", str(log))
    threading.Thread(target=proxy.serve_forever, daemon=True).start()
    port = proxy.server_address[1]
    try:
        c = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
        c.request("POST", "/v1/chat/completions", body=b'{"x":1}',
                  headers={"Content-Type": "application/json"})
        r = c.getresponse()
        assert r.status == 200
        assert json.loads(r.read())["usage"]["prompt_tokens"] == 11
        c.close()
        rows = _rows(log, 1)
        assert len(rows) == 1
        assert rows[0]["status"] == 200 and rows[0]["upstream_error"] is False
        assert rows[0]["path"] == "/v1/chat/completions"
        assert (rows[0]["prompt_tokens"], rows[0]["gen_tokens"]) == (11, 22)
        assert rows[0]["ttft_s"] is not None

        upstream.shutdown()
        upstream.server_close()
        c = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
        c.request("POST", "/v1/chat/completions", body=b"{}")
        r = c.getresponse()
        r.read()
        assert r.status == 502
        c.close()
        rows = _rows(log, 2)
        assert len(rows) == 2
        assert rows[1]["status"] == 502 and rows[1]["upstream_error"] is True
    finally:
        proxy.shutdown()
        proxy.server_close()


@pytest.mark.live
def test_proxy_streams_incrementally(tmp_path):
    release = threading.Event()

    class SSE(http.server.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *a):
            pass

        def do_POST(self):
            self.rfile.read(int(self.headers.get("Content-Length", 0)))
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Transfer-Encoding", "chunked")
            self.end_headers()

            def chunk(b: bytes):
                self.wfile.write(b"%x\r\n%s\r\n" % (len(b), b))
                self.wfile.flush()

            chunk(b'data: {"choices":[{"delta":{"content":"a"}}]}\n\n')
            release.wait(10)
            chunk(b'data: {"usage":{"prompt_tokens":3,"completion_tokens":4}}\n\n')
            self.wfile.write(b"0\r\n\r\n")
            self.wfile.flush()

    upstream = http.server.ThreadingHTTPServer(("127.0.0.1", 0), SSE)
    threading.Thread(target=upstream.serve_forever, daemon=True).start()
    log = tmp_path / "usage.jsonl"
    proxy = usage_proxy.make_server("127.0.0.1", 0,
                                    f"http://127.0.0.1:{upstream.server_address[1]}", str(log))
    threading.Thread(target=proxy.serve_forever, daemon=True).start()
    try:
        c = http.client.HTTPConnection("127.0.0.1", proxy.server_address[1], timeout=10)
        c.request("POST", "/x", body=b"{}")
        r = c.getresponse()
        first = r.read1(4096)  # arrives before upstream finishes
        assert b'"content":"a"' in first
        release.set()
        rest = r.read()
        assert b"completion_tokens" in rest
        c.close()
    finally:
        release.set()
        proxy.shutdown()
        proxy.server_close()
        upstream.shutdown()
        upstream.server_close()
    import time
    for _ in range(50):
        if log.exists() and log.read_text().strip():
            break
        time.sleep(0.05)
    row = json.loads(log.read_text().splitlines()[0])
    assert (row["prompt_tokens"], row["gen_tokens"]) == (3, 4)


@pytest.mark.live
def test_upstream_dies_mid_stream_is_upstream_error(tmp_path):
    got_first = threading.Event()

    class Dies(http.server.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *a):
            pass

        def do_POST(self):
            self.rfile.read(int(self.headers.get("Content-Length", 0)))
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Transfer-Encoding", "chunked")
            self.end_headers()
            b = b'data: {"choices":[]}\n\n'
            self.wfile.write(b"%x\r\n%s\r\n" % (len(b), b))
            self.wfile.flush()
            got_first.wait(10)  # the client has the first chunk, so ttft is recorded
            # hard reset (RST) without terminating the chunked body
            self.connection.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER,
                                       b"\x01\x00\x00\x00\x00\x00\x00\x00")
            self.connection.close()
            self.close_connection = True

    log = tmp_path / "usage.jsonl"
    upstream, proxy = _start(Dies, log)
    try:
        c = http.client.HTTPConnection("127.0.0.1", proxy.server_address[1], timeout=10)
        c.request("POST", "/x", body=b"{}")
        r = c.getresponse()
        assert b"choices" in r.read1(4096)
        got_first.set()
        try:
            r.read()
        except http.client.IncompleteRead:
            pass
        c.close()
        row = _rows(log, 1)[0]
        assert row["status"] == 200 and row["upstream_error"] is True
        assert row["ttft_s"] is not None
    finally:
        _stop(proxy, upstream)


@pytest.mark.live
def test_upstream_500_is_upstream_error(tmp_path):
    class Err(http.server.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *a):
            pass

        def do_POST(self):
            self.rfile.read(int(self.headers.get("Content-Length", 0)))
            self.send_response(500)
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(b"{}")

    log = tmp_path / "usage.jsonl"
    upstream, proxy = _start(Err, log)
    try:
        c = http.client.HTTPConnection("127.0.0.1", proxy.server_address[1], timeout=10)
        c.request("POST", "/x", body=b"{}")
        r = c.getresponse()
        r.read()
        assert r.status == 500
        c.close()
        row = _rows(log, 1)[0]
        assert row["status"] == 500 and row["upstream_error"] is True
    finally:
        _stop(proxy, upstream)


@pytest.mark.live
def test_keepalive_and_chunked_request_body(tmp_path):
    seen = []

    class Echo(http.server.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *a):
            pass

        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            seen.append((self.headers.get("Transfer-Encoding"), self.rfile.read(n)))
            body = b'{"prompt_eval_count":1,"eval_count":2}'
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    log = tmp_path / "usage.jsonl"
    upstream, proxy = _start(Echo, log)
    try:
        c = http.client.HTTPConnection("127.0.0.1", proxy.server_address[1], timeout=10)
        c.request("POST", "/a", body=b"first")
        r = c.getresponse()
        r.read()
        assert r.status == 200
        # second request on the same connection, with a chunked body
        c.request("POST", "/b", body=iter([b"he", b"llo"]), encode_chunked=True,
                  headers={"Transfer-Encoding": "chunked"})
        r = c.getresponse()
        assert r.read() == b'{"prompt_eval_count":1,"eval_count":2}'
        c.close()
        rows = _rows(log, 2)
        assert [x["path"] for x in rows] == ["/a", "/b"]
        assert seen[0][1] == b"first"
        assert seen[1] == (None, b"hello")  # decoded and re-sent with Content-Length
    finally:
        _stop(proxy, upstream)


def test_extraction_failure_still_logs_row(monkeypatch, tmp_path):
    monkeypatch.setattr(usage_proxy, "extract_usage",
                        lambda *a: (_ for _ in ()).throw(RecursionError()))
    log = tmp_path / "usage.jsonl"
    upstream, proxy = _start(_Stub, log)
    try:
        c = http.client.HTTPConnection("127.0.0.1", proxy.server_address[1], timeout=10)
        c.request("POST", "/x", body=b"{}")
        c.getresponse().read()
        c.close()
        row = _rows(log, 1)[0]
        assert row["status"] == 200 and row["prompt_tokens"] is None
    finally:
        _stop(proxy, upstream)


@pytest.mark.live
def test_capture_trim_keeps_tail_usage(monkeypatch, tmp_path):
    monkeypatch.setattr(usage_proxy, "MAX_CAPTURE", 300)
    pad = b'{"message":{"content":"' + b"x" * 100 + b'"},"done":false}\n'
    body = pad * 50 + b'{"done":true,"prompt_eval_count":77,"eval_count":88}\n'
    assert len(body) > 300 * 10

    class Big(http.server.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *a):
            pass

        def do_POST(self):
            self.rfile.read(int(self.headers.get("Content-Length", 0)))
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    log = tmp_path / "usage.jsonl"
    upstream, proxy = _start(Big, log)
    try:
        c = http.client.HTTPConnection("127.0.0.1", proxy.server_address[1], timeout=10)
        c.request("POST", "/x", body=b"{}")
        assert c.getresponse().read() == body  # client still gets the full body
        c.close()
        row = _rows(log, 1)[0]
        assert (row["prompt_tokens"], row["gen_tokens"]) == (77, 88)
    finally:
        _stop(proxy, upstream)


# ---------------------------------------------------------------- streamed / in-band errors

inband_error = usage_proxy.inband_error


@pytest.mark.parametrize("body", [
    b'event: error\ndata: {"type":"error","error":{"type":"overloaded_error"}}\n\n',  # Anthropic
    b'data: {"choices":[{"delta":{"content":"hi"}}]}\n\ndata: {"error":{"message":"runner died"}}\n\n',
    b'{"model":"m","response":"a","done":false}\n{"error":"llama runner process has terminated"}\n',
])
def test_inband_error_detected(body):
    assert inband_error(body)


@pytest.mark.parametrize("body", [
    b'data: {"choices":[{"delta":{"content":"error"}}]}\n\ndata: [DONE]\n\n',
    b'{"model":"m","response":"error: x","done":true}\n',
    b'event: message_stop\ndata: {"type":"message_stop"}\n\n',
    b"",
])
def test_no_inband_error(body):
    assert not inband_error(body)


def _row(**kw):
    return json.dumps({"path": "/a", "status": 200, "upstream_error": False, **kw})


def test_summarize_tps_from_streamed_rows_only():
    lines = "\n".join([
        _row(duration_s=3.0, ttft_s=1.0, prompt_tokens=1000, gen_tokens=40, streamed=True),
        # non-streamed: ttft is about the whole duration, so its speeds are meaningless
        _row(duration_s=5.0, ttft_s=4.999, prompt_tokens=5000, gen_tokens=500, streamed=False),
        # rows from before the key existed were all streamed (OpenCode, Claude Code)
        _row(duration_s=7.0, ttft_s=3.0, prompt_tokens=3000, gen_tokens=120),
    ])
    s = summarize_usage(lines)
    assert s.prompt_tokens == 9000 and s.gen_tokens == 660
    assert s.pp_tps == pytest.approx(1000.0) and s.tg_tps == pytest.approx(160 / 6)


def test_summarize_no_streamed_rows_has_no_speeds():
    s = summarize_usage(_row(duration_s=5.0, ttft_s=4.9, prompt_tokens=10, gen_tokens=5,
                             streamed=False))
    assert s.prompt_tokens == 10 and s.gen_tokens == 5
    assert s.pp_tps is None and s.tg_tps is None


def _serve_body(ctype, body, chunked=True):
    class H(http.server.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *a):
            pass

        def do_POST(self):
            self.rfile.read(int(self.headers.get("Content-Length", 0)))
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            if chunked:
                self.send_header("Transfer-Encoding", "chunked")
                self.end_headers()
                self.wfile.write(b"%x\r\n%s\r\n0\r\n\r\n" % (len(body), body))
            else:
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
    return H


def _one_row(tmp_path, handler):
    log = tmp_path / "usage.jsonl"
    upstream, proxy = _start(handler, log)
    try:
        c = http.client.HTTPConnection("127.0.0.1", proxy.server_address[1], timeout=10)
        c.request("POST", "/x", body=b"{}")
        c.getresponse().read()
        c.close()
        return _rows(log, 1)[0]
    finally:
        _stop(proxy, upstream)


@pytest.mark.live
def test_proxy_flags_inband_stream_error(tmp_path):
    body = b'{"response":"a","done":false}\n{"error":"llama runner process has terminated"}\n'
    row = _one_row(tmp_path, _serve_body("application/x-ndjson", body))
    assert row["status"] == 200 and row["streamed"] is True and row["upstream_error"] is True


@pytest.mark.live
def test_proxy_logs_streamed_flag(tmp_path):
    row = _one_row(tmp_path, _serve_body("text/event-stream", b"data: {}\n\n"))
    assert row["streamed"] is True and row["upstream_error"] is False
    body = json.dumps({"usage": {"prompt_tokens": 1, "completion_tokens": 2}}).encode()
    (tmp_path / "b").mkdir()
    row = _one_row(tmp_path / "b", _serve_body("application/json", body, chunked=False))
    assert row["streamed"] is False and row["upstream_error"] is False


@pytest.mark.live
def test_non_streamed_error_key_is_not_inband_error(tmp_path):
    # a plain JSON reply is not a stream: only HTTP status decides (4xx is the agent's fault)
    row = _one_row(tmp_path, _serve_body("application/json", b'{"error":"x"}', chunked=False))
    assert row["streamed"] is False and row["upstream_error"] is False
