#!/usr/bin/env python3
"""Transparent logging proxy between a coding agent and Ollama (stdlib only).

python3 usage_proxy.py --listen 127.0.0.1:11500 --upstream http://127.0.0.1:11434 --log usage.jsonl

Forwards every request unchanged, streams the response back chunk by chunk, and
appends one JSON line per completed request (flushed immediately):
path, status, duration_s, ttft_s, prompt_tokens, gen_tokens, streamed, upstream_error.

`streamed` is true for an SSE or NDJSON response; only those rows give token speeds
(a non-streamed reply's first byte arrives at the end). `upstream_error` is set for a
5xx, a failed or cut-off upstream connection, and an error reported in-band in a stream
(HTTP 200 with an `event: error` SSE line or a JSON event with a top-level "error").
"""
from __future__ import annotations

import argparse
import http.client
import http.server
import json
import threading
import time
import urllib.parse
import zlib

# Longer than the 2700 s attempt budget so the proxy never times out first.
UPSTREAM_TIMEOUT_S = 4 * 3600
HOP_BY_HOP = {
    "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailer", "transfer-encoding", "upgrade", "proxy-connection",
}
MAX_CAPTURE = 64 * 1024 * 1024  # usage copy keeps only the last this-many bytes
STREAM_TYPES = ("text/event-stream", "application/x-ndjson")


def _pick(d: dict, *keys: str):
    for k in keys:
        v = d.get(k)
        if isinstance(v, int) and not isinstance(v, bool):
            return v
    return None


def _usage_from_obj(obj) -> tuple[int | None, int | None]:
    if not isinstance(obj, dict):
        return None, None
    p = g = None
    # Ollama: top level
    p = _pick(obj, "prompt_eval_count")
    g = _pick(obj, "eval_count")
    # OpenAI / Anthropic: usage (Anthropic message_start nests it in message)
    for u in (obj.get("usage"), (obj.get("message") or {}).get("usage")
              if isinstance(obj.get("message"), dict) else None):
        if isinstance(u, dict):
            up = _pick(u, "prompt_tokens", "input_tokens")
            ug = _pick(u, "completion_tokens", "output_tokens")
            p = up if up is not None else p
            g = ug if ug is not None else g
    return p, g


def _stream_objs(text: str) -> list:
    """JSON objects from SSE `data:` lines or NDJSON lines."""
    objs = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("data:"):
            line = line[5:].strip()
        if not line or line == "[DONE]" or not line.startswith("{"):
            continue
        try:
            objs.append(json.loads(line))
        except ValueError:
            continue
    return objs


def inband_error(body: bytes) -> bool:
    """True if a streamed body reports an error in-band (SSE `event: error`, or an event
    object with a top-level "error" key, as Ollama sends when its runner dies)."""
    text = body.decode("utf-8", errors="replace")
    if any(line.strip() == "event: error" or line.strip() == "event:error"
           for line in text.splitlines()):
        return True
    return any(isinstance(o, dict) and "error" in o for o in _stream_objs(text))


def extract_usage(body: bytes, content_type: str = "") -> tuple[int | None, int | None]:
    """Return (prompt_tokens, gen_tokens) from an OpenAI/Anthropic/Ollama body, or Nones."""
    if not body:
        return None, None
    text = body.decode("utf-8", errors="replace")
    objs = []
    try:
        objs.append(json.loads(text))
    except ValueError:
        objs = _stream_objs(text)
    prompt = gen = None
    for o in objs:  # later events win (final usage chunk / message_delta / done:true)
        p, g = _usage_from_obj(o)
        prompt = p if p is not None else prompt
        gen = g if g is not None else gen
    return prompt, gen


class _Log:
    def __init__(self, path: str):
        self._f = open(path, "a", encoding="utf-8")
        self._lock = threading.Lock()

    def write(self, row: dict) -> None:
        with self._lock:
            self._f.write(json.dumps(row) + "\n")
            self._f.flush()


def _read_chunked(rfile) -> bytes:
    out = bytearray()
    while True:
        size = int(rfile.readline().split(b";")[0].strip() or b"0", 16)
        if size == 0:
            while rfile.readline().strip():  # trailers
                pass
            return bytes(out)
        out += rfile.read(size)
        rfile.readline()


class ProxyHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    upstream: urllib.parse.SplitResult
    log: _Log

    def log_message(self, *args):
        pass

    def _read_body(self) -> bytes:
        if "chunked" in self.headers.get("Transfer-Encoding", "").lower():
            return _read_chunked(self.rfile)
        n = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(n) if n else b""

    def _proxy(self) -> None:
        start = time.monotonic()
        row = {"path": self.path, "status": None, "duration_s": None, "ttft_s": None,
               "prompt_tokens": None, "gen_tokens": None, "streamed": False,
               "upstream_error": False}
        captured = bytearray()
        ctype = encoding = ""
        try:
            body = self._read_body()
            headers = {k: v for k, v in self.headers.items() if k.lower() not in HOP_BY_HOP
                       and k.lower() not in ("host", "content-length")}
            headers["Host"] = self.upstream.netloc
            if body or self.command in ("POST", "PUT", "PATCH"):
                headers["Content-Length"] = str(len(body))
            conn = http.client.HTTPConnection(
                self.upstream.hostname, self.upstream.port or 80, timeout=UPSTREAM_TIMEOUT_S)
            try:
                conn.request(self.command, self.path, body=body or None, headers=headers)
                resp = conn.getresponse()
            except (OSError, http.client.HTTPException):
                conn.close()
                row["upstream_error"] = True
                row["status"] = 502
                msg = b"usage_proxy: upstream connection failed\n"
                self.send_response(502)
                self.send_header("Content-Type", "text/plain")
                self.send_header("Content-Length", str(len(msg)))
                self.end_headers()
                self.wfile.write(msg)
                return
            row["status"] = resp.status
            ctype = resp.getheader("Content-Type", "")
            row["streamed"] = ctype.split(";")[0].strip().lower() in STREAM_TYPES
            encoding = (resp.getheader("Content-Encoding") or "").lower()
            self.send_response_only(resp.status, resp.reason)
            length = resp.getheader("Content-Length")
            for k, v in resp.getheaders():
                if k.lower() not in HOP_BY_HOP:
                    self.send_header(k, v)
            no_body = self.command == "HEAD" or resp.status in (204, 304) or resp.status < 200
            chunked = length is None and not no_body
            if chunked:
                self.send_header("Transfer-Encoding", "chunked")
            self.end_headers()
            try:
                while not no_body:
                    try:
                        data = resp.read1(65536)
                    except Exception:  # any failure reading upstream is an upstream error
                        row["upstream_error"] = True
                        self.close_connection = True
                        break
                    if not data:
                        break
                    if row["ttft_s"] is None:
                        row["ttft_s"] = round(time.monotonic() - start, 6)
                    captured += data
                    if len(captured) > MAX_CAPTURE:
                        del captured[:len(captured) - MAX_CAPTURE]  # keep the tail: usage comes last
                    try:
                        if chunked:
                            self.wfile.write(b"%x\r\n%s\r\n" % (len(data), data))
                        else:
                            self.wfile.write(data)
                        self.wfile.flush()
                    except OSError:  # client went away
                        self.close_connection = True
                        break
                else:
                    data = None
                if chunked and not row["upstream_error"] and not self.close_connection:
                    try:
                        self.wfile.write(b"0\r\n\r\n")
                        self.wfile.flush()
                    except OSError:
                        self.close_connection = True
            finally:
                conn.close()
        except (BrokenPipeError, ConnectionResetError):
            self.close_connection = True
        finally:
            row["duration_s"] = round(time.monotonic() - start, 6)
            if row["status"] is not None and row["status"] >= 500:
                row["upstream_error"] = True
            try:
                data = bytes(captured)
                if encoding in ("gzip", "deflate") and data:
                    data = zlib.decompress(data, 16 + zlib.MAX_WBITS if encoding == "gzip" else 15)
                row["prompt_tokens"], row["gen_tokens"] = extract_usage(data, ctype)
                if row["streamed"] and inband_error(data):
                    row["upstream_error"] = True
            except Exception:  # never let extraction stop the log line being written
                row["prompt_tokens"] = row["gen_tokens"] = None
            self.log.write(row)

    do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = do_HEAD = do_OPTIONS = _proxy


def make_server(host: str, port: int, upstream: str, log_path: str) -> http.server.ThreadingHTTPServer:
    handler = type("Handler", (ProxyHandler,), {
        "upstream": urllib.parse.urlsplit(upstream), "log": _Log(log_path)})
    srv = http.server.ThreadingHTTPServer((host, port), handler)
    srv.daemon_threads = True
    return srv


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--listen", default="127.0.0.1:11500")
    ap.add_argument("--upstream", default="http://127.0.0.1:11434")
    ap.add_argument("--log", required=True)
    a = ap.parse_args()
    host, _, port = a.listen.rpartition(":")
    make_server(host or "127.0.0.1", int(port), a.upstream, a.log).serve_forever()


if __name__ == "__main__":
    main()
