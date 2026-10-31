from harness.sampling import SampleSummary, summarize_samples

HEADER = "ts,mem_used_mib,vram_used_mib,gtt_used_mib,tctl_c,edge_c,sclk_mhz,cpu_mhz_avg\n"


def test_peaks_across_rows():
    csv = HEADER + (
        "1,1000,200,300,60.0,50.0,800,2000\n"
        "2,3000,100,900,72.5,55.0,1200,3000\n"
        "3,2000,500,100,65.0,52.0,900,2500\n"
    )
    s = summarize_samples(csv)
    assert s == SampleSummary(
        peak_mem_mib=3000, peak_gpu_mem_mib=1000, max_tctl_c=72.5, throttled=False
    )


def test_empty_field_ignored():
    csv = HEADER + (
        "1,1000,,,60.0,,800,2000\n"
        "2,1500,400,100,,50.0,800,2000\n"
    )
    s = summarize_samples(csv)
    assert s.peak_mem_mib == 1500
    assert s.peak_gpu_mem_mib == 500
    assert s.max_tctl_c == 60.0


def test_header_only_is_all_none():
    s = summarize_samples(HEADER)
    assert s == SampleSummary(None, None, None, False)


def test_throttle_threshold():
    assert summarize_samples(HEADER + "1,1,1,1,95.0,,,\n").throttled is True
    assert summarize_samples(HEADER + "1,1,1,1,94.9,,,\n").throttled is False
