"""Run llama-bench for one (build x model) and parse the numbers.

We use llama-bench's machine-readable JSON output (`-o json`) so parsing is
robust across llama.cpp versions. Two standard tests:
    pp  (prompt processing)  -> prefill tokens/sec
    tg  (text generation)    -> decode tokens/sec

Peak RSS is captured by wrapping the run in GNU `/usr/bin/time -v` when present
(Linux Arm boxes have it); it degrades to None on hosts without it.

TTFT is derived, not measured directly: at prefill throughput `pp_tps`, a prompt
of `n_prompt` tokens takes n_prompt / pp_tps seconds to reach first token. We
report TTFT@<n_prompt> so it is unambiguous.
"""
from __future__ import annotations

import json
import re
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
    build: str          # "kleidiai-on" | "kleidiai-off"
    threads: int
    n_prompt: int
    n_gen: int
    prefill_tps: float
    decode_tps: float
    ttft_ms: float
    peak_ram_gb: Optional[float]
    size_gb: float

    def to_dict(self) -> dict:
        return asdict(self)


def run_bench(build: Build, art: ModelArtifact, threads: int,
              n_prompt: int = 512, n_gen: int = 128,
              reps: int = 3) -> BenchResult:
    time_bin = util.which("time") or _gnu_time()
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
    if time_bin:
        # /usr/bin/time -v writes RSS to stderr; llama-bench JSON goes to stdout.
        proc = util.run([time_bin, "-v", *cmd_core], capture=True, check=False)
        stdout = proc.stdout
        peak_ram_gb = _parse_peak_rss_gb(stdout)
        json_text = _extract_json(stdout)
    else:
        proc = util.run(cmd_core, capture=True, check=True)
        json_text = _extract_json(proc.stdout)

    rows = json.loads(json_text)
    prefill_tps = _avg_ts(rows, kind="pp")
    decode_tps = _avg_ts(rows, kind="tg")
    ttft_ms = (n_prompt / prefill_tps * 1000.0) if prefill_tps else 0.0

    return BenchResult(
        model=art.name, quant=art.quant, build=build.label, threads=threads,
        n_prompt=n_prompt, n_gen=n_gen,
        prefill_tps=round(prefill_tps, 2), decode_tps=round(decode_tps, 2),
        ttft_ms=round(ttft_ms, 1), peak_ram_gb=peak_ram_gb, size_gb=art.size_gb,
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
    """llama-bench prints a JSON array; GNU time may prepend/append lines."""
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(f"no JSON array in llama-bench output:\n{text[:500]}")
    return text[start:end + 1]


def _parse_peak_rss_gb(text: str) -> Optional[float]:
    m = re.search(r"Maximum resident set size \(kbytes\):\s*(\d+)", text)
    if m:
        return round(int(m.group(1)) / 1024 / 1024, 3)
    return None


def _gnu_time() -> Optional[str]:
    for cand in ("/usr/bin/time",):
        if Path(cand).exists():
            return cand
    return None
