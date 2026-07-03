"""Optional Arm Performix integration.

Arm Performix (https://developer.arm.com/servers-and-cloud-computing/arm-performix)
is Arm's performance-analysis toolkit for Neoverse cloud platforms. If it is
installed on the box, KleidiBench can wrap a benchmark run in it to capture
deep metrics (memory bandwidth, cache efficiency, CPU utilization) that explain
*why* KleidiAI is faster — great material for the write-up and demo video.

This is intentionally best-effort: if `performix` is not on PATH, we skip it and
the rest of the harness runs unchanged. The exact CLI surface is version-specific,
so the invocation is configurable via KLEIDIBENCH_PERFIX_CMD.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

from . import util


def available() -> bool:
    return util.which("performix") is not None


def profile(cmd: List[str], out_dir: Path, tag: str) -> Optional[Path]:
    """Run `cmd` under Performix, saving a report to out_dir/perfix-<tag>.

    Returns the report path, or None if Performix is unavailable. Override the
    wrapper with KLEIDIBENCH_PERFIX_CMD (use {out} and {cmd} placeholders)."""
    if not available():
        util.log("Arm Performix not found on PATH — skipping deep profile "
                 "(install it to enrich the report; see docs/methodology.md).")
        return None

    out_dir.mkdir(parents=True, exist_ok=True)
    report = out_dir / f"perfix-{tag}.txt"
    template = os.environ.get("KLEIDIBENCH_PERFIX_CMD")

    if template:
        full = template.format(out=str(report), cmd=" ".join(cmd))
        util.run(full)
    else:
        # Default guess: `performix record -o <report> -- <cmd>`.
        util.run(["performix", "record", "-o", str(report), "--", *cmd], check=False)

    util.log(f"Arm Performix profile -> {report}")
    return report if report.exists() else None
