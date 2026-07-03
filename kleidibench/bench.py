"""Run llama-bench for one (build x model) and parse the numbers.

We use llama-bench's machine-readable JSON output (`-o json`) so parsing is
robust across llama.cpp versions. Two standard tests:
    pp  (prompt processing)  -> prefill tokens/sec
    tg  (text generation)    -> decode tokens/sec

Peak RSS is captured by wrapping the run in GNU `time -v` where available.
Two isolation rules keep the JSON parse safe: stdout and stderr are captured
separately (llama.cpp logs go to stderr), and GNU time writes its report to a
temp file via `-o` rather than sharing a stream. `-v` support is probed once —
BSD/macOS `time` lacks it, so non-Linux dev boxes just skip RSS. The reported
value is whole-process peak RSS (model load + all reps, pp and tg), i.e. the
capacity-planning number for running this config, not a per-phase measurement.

TTFT is derived, not measured directly: at prefill throughput `pp_tps`, a prompt
of `n_prompt` tokens takes n_prompt / pp_tps seconds to reach first token. We
report TTFT@<n_prompt> so it is unambiguous, and None when prefill parsing
failed (never a fake-looking 0.0).
"""
from __future__ import annotations

import json
import re
import tempfile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional

from . import util
from .build import Build
from .quantize import ModelArtifact


@dataclass
class BenchResult:
    model: str
    quant: str
    build: str          # "repack-off" | "kleidiai-off" | "kleidiai-on"
    threads: int
    n_prompt: int
    n_gen: int
    prefill_tps: float
    decode_tps: float
    ttft_ms: Optional[float]
    peak_ram_gb: Optional[float]
    size_gb: float

    def to_dict(self) -> dict:
        return asdict(self)


_gnu_time_checked: Optional[str] = None


def _gnu_time() -> Optional[str]:
    """Path to a `time` binary that supports -v (GNU time), else None.
    macOS/BSD `time` has no -v; probe once instead of crashing mid-sweep."""
    global _gnu_time_checked
    if _gnu_time_checked is not None:
        return _gnu_time_checked or None
    cand = util.which("time") or ("/usr/bin/time" if Path("/usr/bin/time").exists() else None)
    if cand:
        probe = util.run([cand, "-v", "true"], capture=True, check=False)
        _gnu_time_checked = cand if probe.returncode == 0 else ""
    else:
        _gnu_time_checked = ""
    return _gnu_time_checked or None


def run_bench(build: Build, art: ModelArtifact, threads: int,
              n_prompt: int = 512, n_gen: int = 128,
              reps: int = 3) -> BenchResult:
    cmd_core = [
        str(build.llama_bench),
        "-m", str(art.path),
        "-t", str(threads),
        "-p", str(n_prompt),
        "-n", str(n_gen),
        "-r", str(reps),
        "-o", "json",
    ]

    peak_ram_gb: Optional[float] = None
    time_bin = _gnu_time()
    if time_bin:
        # GNU time report goes to its own file (-o): stdout stays pure JSON.
        # LC_ALL=C pins the "Maximum resident set size" wording for parsing.
        with tempfile.NamedTemporaryFile(mode="r", suffix=".time", delete=False) as tf:
            time_file = Path(tf.name)
        proc = util.run([time_bin, "-v", "-o", str(time_file), *cmd_core],
                        env={"LC_ALL": "C"}, capture=True, check=False)
        try:
            peak_ram_gb = _parse_peak_rss_gb(time_file.read_text())
        finally:
            time_file.unlink(missing_ok=True)
    else:
        proc = util.run(cmd_core, capture=True, check=False)

    if proc.returncode != 0:
        raise RuntimeError(
            f"llama-bench failed (exit {proc.returncode}) on {art.path.name} "
            f"[{build.label} t={threads}] — corrupt GGUF or OOM?\n"
            f"stderr tail: {(proc.stderr or '')[-500:]}")

    rows = json.loads(_extract_json(proc.stdout or ""))
    prefill_tps = _avg_ts(rows, kind="pp")
    decode_tps = _avg_ts(rows, kind="tg")
    ttft_ms = round(n_prompt / prefill_tps * 1000.0, 1) if prefill_tps > 0 else None

    return BenchResult(
        model=art.name, quant=art.quant, build=build.label, threads=threads,
        n_prompt=n_prompt, n_gen=n_gen,
        prefill_tps=round(prefill_tps, 2), decode_tps=round(decode_tps, 2),
        ttft_ms=ttft_ms, peak_ram_gb=peak_ram_gb, size_gb=art.size_gb,
    )


def _avg_ts(rows: List[dict], kind: str) -> float:
    """Pull avg tokens/sec for a pp (prefill) or tg (decode) row."""
    for r in rows:
        n_prompt = int(r.get("n_prompt", 0))
        n_gen = int(r.get("n_gen", 0))
        is_pp = n_prompt > 0 and n_gen == 0
        is_tg = n_gen > 0 and n_prompt == 0
        if (kind == "pp" and is_pp) or (kind == "tg" and is_tg):
            return float(r.get("avg_ts", 0.0))
    return 0.0


def _extract_json(text: str) -> str:
    """llama-bench prints a JSON array on stdout; slice defensively anyway."""
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(f"no JSON array in llama-bench stdout:\n{text[:500]}")
    return text[start:end + 1]


def _parse_peak_rss_gb(text: str) -> Optional[float]:
    m = re.search(r"Maximum resident set size \(kbytes\):\s*(\d+)", text)
    if m:
        return round(int(m.group(1)) / 1024 / 1024, 3)
    return None
