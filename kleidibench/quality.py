"""Measure quantization quality via perplexity on a small bundled corpus.

Quantization trades accuracy for size/speed; perplexity over a fixed text is
the cheapest way to put a number on that loss so the report can show the full
size-vs-speed-vs-quality curve. We run llama-perplexity with a small chunk
budget (--chunks 8) so the sweep stays tolerable on free-tier Arm VMs — the
absolute PPL is corpus-dependent anyway; what matters is the delta between
F16 and each quant on the SAME corpus.

The corpus ships inside the package (kleidibench/data/corpus.txt) so quality
runs need no network — the harness must work on an air-gapped or bare CI box.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from . import util

# Keep the run short: 8 chunks of the default 512-token context is enough to
# separate F16 from Q4_0 while staying under a couple of minutes on small cores.
CHUNKS = 8


def get_corpus() -> Path:
    """Path to the bundled evaluation text (packaged, never downloaded)."""
    return Path(__file__).parent / "data" / "corpus.txt"


def measure_perplexity(perplexity_bin: Path, model_path: Path, corpus: Path,
                       threads: int) -> Optional[float]:
    """Run llama-perplexity and parse the final PPL estimate.

    Returns None on any failure (binary error, unparseable output) rather than
    raising — a quality miss on one quant must not kill the whole sweep.
    """
    cmd = [
        str(perplexity_bin),
        "-m", str(model_path),
        "-f", str(corpus),
        "-t", str(threads),
        "--chunks", str(CHUNKS),
    ]
    try:
        proc = util.run(cmd, capture=True, check=False)
    except Exception as e:  # e.g. binary missing on a partial build
        util.log(f"perplexity run failed for {model_path.name}: {e}")
        return None

    out = proc.stdout or ""
    if proc.returncode != 0:
        util.log(f"llama-perplexity exited {proc.returncode} for "
                 f"{model_path.name}:\n{out[-500:]}")
        return None

    # Upstream prints "Final estimate: PPL = 12.3456 +/- 0.15" but the exact
    # wording has drifted across releases — match just the PPL assignment and
    # take the last occurrence (intermediate estimates print the same shape).
    matches = re.findall(r"PPL\s*=\s*([0-9]+(?:\.[0-9]+)?)", out)
    if not matches:
        util.log(f"could not parse PPL from llama-perplexity output for "
                 f"{model_path.name}:\n{out[-500:]}")
        return None
    return float(matches[-1])
