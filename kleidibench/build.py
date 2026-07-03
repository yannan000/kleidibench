"""Clone and build llama.cpp twice: KleidiAI ON and KleidiAI OFF.

The only difference between the two builds is the CMake flag
`-DGGML_CPU_KLEIDIAI=ON|OFF`. That is the whole point of KleidiBench: KleidiAI
accelerates Arm CPU inference with *no code changes* — you just flip a build
flag — and we measure exactly what that flag buys you.

KleidiAI's optimized kernels kick in for `Q4_0` weights (repacked at load time)
using dotprod on Neoverse N1 and i8mm/SVE on V1/V2. So the ON-vs-OFF delta is
most visible on the Q4_0 model.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from . import util

LLAMA_REPO = "https://github.com/ggml-org/llama.cpp.git"


@dataclass
class Build:
    kleidiai: bool
    build_dir: Path
    llama_bench: Path
    llama_cli: Path
    llama_quantize: Path
    llama_perplexity: Path

    @property
    def label(self) -> str:
        return "kleidiai-on" if self.kleidiai else "kleidiai-off"


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


def _cmake_build(kleidiai: bool, jobs: Optional[int] = None) -> Build:
    build_dir = util.BUILD_ON if kleidiai else util.BUILD_OFF
    flag = "ON" if kleidiai else "OFF"
    jobs = jobs or util.detect_host().cores

    # Configure. CPU-only (no CUDA/Metal) — this is a cloud CPU benchmark.
    util.run([
        "cmake", "-S", str(util.LLAMA_SRC), "-B", str(build_dir),
        "-DCMAKE_BUILD_TYPE=Release",
        "-DGGML_NATIVE=ON",              # let the compiler target the host Arm core
        f"-DGGML_CPU_KLEIDIAI={flag}",
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
        kleidiai=kleidiai,
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


def build_both(ref: Optional[str] = None, jobs: Optional[int] = None) -> dict:
    """Build both variants. Returns {'on': Build, 'off': Build}."""
    clone_llama(ref)
    return {
        "off": _cmake_build(kleidiai=False, jobs=jobs),
        "on": _cmake_build(kleidiai=True, jobs=jobs),
    }
