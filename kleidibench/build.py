"""Clone and build llama.cpp in three variants for a fair 3-way comparison.

    naive  (repack-off)   -DGGML_CPU_KLEIDIAI=OFF -DGGML_CPU_REPACK=OFF
    off    (kleidiai-off) -DGGML_CPU_KLEIDIAI=OFF   (llama.cpp default: its own
                          aarch64 runtime-repack kernels stay enabled)
    on     (kleidiai-on)  -DGGML_CPU_KLEIDIAI=ON

Why three: modern llama.cpp already ships optimized aarch64 repack kernels in
its default CPU backend, so "KleidiAI off" is NOT a naive baseline — comparing
only on/off understates what Arm-optimized code paths deliver overall. The
naive build (repack disabled too) shows the full journey: generic kernels ->
llama.cpp's Arm repack -> Arm's KleidiAI micro-kernels.

KleidiAI's kernels kick in for `Q4_0` weights (repacked at load time) using
dotprod/i8mm/SME depending on the core, so the deltas are most visible on the
Q4_0 model. (GGML_CPU_REPACK was formerly named GGML_CPU_AARCH64; we pass both
so older checkouts honor it — unknown CMake vars only warn.)
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from . import util

LLAMA_REPO = "https://github.com/ggml-org/llama.cpp.git"

# variant name -> (build dir, extra cmake flags, result label)
VARIANTS = {
    "naive": (util.BUILD_NAIVE,
              ["-DGGML_CPU_KLEIDIAI=OFF", "-DGGML_CPU_REPACK=OFF",
               "-DGGML_CPU_AARCH64=OFF"],
              "repack-off"),
    "off": (util.BUILD_OFF, ["-DGGML_CPU_KLEIDIAI=OFF"], "kleidiai-off"),
    "on": (util.BUILD_ON, ["-DGGML_CPU_KLEIDIAI=ON"], "kleidiai-on"),
}


@dataclass
class Build:
    label: str
    build_dir: Path
    llama_bench: Path
    llama_cli: Path
    llama_quantize: Path
    llama_perplexity: Path


def clone_llama(ref: Optional[str] = None) -> Path:
    """Clone (or reuse) the upstream llama.cpp checkout. Pin a ref for repro."""
    util.ensure_dirs()
    if not util.LLAMA_SRC.exists():
        util.run(["git", "clone", LLAMA_REPO, str(util.LLAMA_SRC)])
    if ref:
        util.run(["git", "fetch", "--all", "--tags"], cwd=util.LLAMA_SRC)
        util.run(["git", "checkout", ref], cwd=util.LLAMA_SRC)
    commit = util.run(["git", "rev-parse", "--short", "HEAD"], cwd=util.LLAMA_SRC,
                      capture=True).stdout.strip()
    util.log(f"llama.cpp @ {commit}")
    return util.LLAMA_SRC


def llama_commit() -> str:
    try:
        return util.run(["git", "rev-parse", "--short", "HEAD"], cwd=util.LLAMA_SRC,
                        capture=True).stdout.strip()
    except Exception:
        return "unknown"


def _cmake_build(variant: str, jobs: Optional[int] = None) -> Build:
    build_dir, extra_flags, label = VARIANTS[variant]
    jobs = jobs or util.detect_host().cores

    # Configure. CPU-only (no CUDA/Metal) — this is a cloud CPU benchmark.
    util.run([
        "cmake", "-S", str(util.LLAMA_SRC), "-B", str(build_dir),
        "-DCMAKE_BUILD_TYPE=Release",
        "-DGGML_NATIVE=ON",              # let the compiler target the host Arm core
        *extra_flags,
        "-DLLAMA_CURL=OFF",              # avoid libcurl dep on bare VMs
        "-DGGML_CUDA=OFF", "-DGGML_METAL=OFF",
    ])
    util.run([
        "cmake", "--build", str(build_dir), "--config", "Release",
        "-j", str(jobs),
        "--target", "llama-bench", "llama-cli", "llama-quantize", "llama-perplexity",
    ])

    bindir = build_dir / "bin"
    b = Build(
        label=label,
        build_dir=build_dir,
        llama_bench=_find(bindir, "llama-bench"),
        llama_cli=_find(bindir, "llama-cli"),
        llama_quantize=_find(bindir, "llama-quantize"),
        llama_perplexity=_find(bindir, "llama-perplexity"),
    )
    util.log(f"built {b.label}: {b.llama_bench}")
    return b


def _find(bindir: Path, name: str) -> Path:
    """llama.cpp has moved binary output paths over releases; search a bit."""
    for cand in (bindir / name, bindir.parent / name, bindir.parent / "bin" / name):
        if cand.exists():
            return cand
    hits = list(bindir.parent.rglob(name))
    if hits:
        return hits[0]
    raise FileNotFoundError(f"could not locate built binary '{name}' under {bindir.parent}")


def build_all(ref: Optional[str] = None, jobs: Optional[int] = None) -> dict:
    """Build all three variants. Returns {'naive'|'off'|'on': Build}."""
    clone_llama(ref)
    return {v: _cmake_build(v, jobs=jobs) for v in ("naive", "off", "on")}
