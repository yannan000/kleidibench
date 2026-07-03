"""Shared helpers: command execution, workspace paths, and Arm host detection."""
from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

# --------------------------------------------------------------------------- #
# Workspace layout
# --------------------------------------------------------------------------- #

# Everything KleidiBench downloads/builds lives under one cache dir so a run is
# easy to reproduce and easy to wipe. Override with KLEIDIBENCH_HOME.
HOME = Path(os.environ.get("KLEIDIBENCH_HOME", Path.home() / ".kleidibench")).expanduser()
LLAMA_SRC = HOME / "llama.cpp"          # upstream checkout
BUILD_ON = HOME / "build-kleidiai-on"   # cmake build dir, GGML_CPU_KLEIDIAI=ON
BUILD_OFF = HOME / "build-kleidiai-off"  # cmake build dir, GGML_CPU_KLEIDIAI=OFF
MODELS = HOME / "models"                 # gguf files

# results/ is committed to the repo, so it lives next to the package, not in HOME.
REPO_ROOT = Path(__file__).resolve().parent.parent
RESULTS = REPO_ROOT / "results"


def ensure_dirs() -> None:
    for d in (HOME, MODELS, RESULTS):
        d.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------------------------------- #
# Logging + command execution
# --------------------------------------------------------------------------- #

def log(msg: str) -> None:
    print(f"[kleidibench] {msg}", flush=True)


def run(cmd, cwd: Optional[Path] = None, env: Optional[dict] = None,
        capture: bool = False, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command, streaming or capturing output.

    Pass a list (preferred) or a string. Raises on non-zero exit when check=True.
    """
    shell = isinstance(cmd, str)
    printable = cmd if shell else " ".join(str(c) for c in cmd)
    log(f"$ {printable}")
    full_env = {**os.environ, **(env or {})}
    return subprocess.run(
        cmd, cwd=str(cwd) if cwd else None, env=full_env, shell=shell,
        text=True, check=check,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
    )


def which(name: str) -> Optional[str]:
    return shutil.which(name)


# --------------------------------------------------------------------------- #
# Host / Arm feature detection
# --------------------------------------------------------------------------- #

@dataclass
class HostInfo:
    arch: str
    is_arm: bool
    cpu_model: str
    cores: int
    total_ram_gb: float
    features: list = field(default_factory=list)   # dotprod, i8mm, sve, sve2, bf16
    has_dotprod: bool = False
    has_i8mm: bool = False
    has_sve: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


_ARM_FEATURES = ("asimddp", "i8mm", "sve", "sve2", "bf16")
# /proc/cpuinfo names differ slightly from the marketing names:
#   asimddp -> dotprod (Neoverse N1 has this)
#   i8mm    -> int8 matmul (Neoverse V1/V2, Graviton3/4 — NOT N1)


def detect_host() -> HostInfo:
    """Best-effort host + Arm feature detection. Works on Linux Arm boxes;
    degrades gracefully on the x86 dev Mac (is_arm=False)."""
    arch = platform.machine().lower()
    is_arm = arch in ("aarch64", "arm64")
    cpu_model = platform.processor() or "unknown"
    cores = os.cpu_count() or 1
    ram_gb = _total_ram_gb()
    features: list = []

    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.exists():
        text = cpuinfo.read_text(errors="ignore")
        for line in text.splitlines():
            if line.lower().startswith("features") and ":" in line:
                flags = line.split(":", 1)[1].split()
                features = [f for f in _ARM_FEATURES if f in flags]
                break
            if line.lower().startswith("model name") and ":" in line:
                cpu_model = line.split(":", 1)[1].strip()
        # Ampere Altra often reports "CPU implementer/part" rather than model name.
        if cpu_model in ("", "unknown"):
            impl = _grep_cpuinfo(text, "cpu implementer")
            part = _grep_cpuinfo(text, "cpu part")
            if impl or part:
                cpu_model = _decode_arm_part(impl, part)

    return HostInfo(
        arch=arch,
        is_arm=is_arm,
        cpu_model=cpu_model,
        cores=cores,
        total_ram_gb=round(ram_gb, 1),
        features=features,
        has_dotprod="asimddp" in features,
        has_i8mm="i8mm" in features,
        has_sve="sve" in features or "sve2" in features,
    )


def _grep_cpuinfo(text: str, key: str) -> str:
    for line in text.splitlines():
        if line.lower().startswith(key) and ":" in line:
            return line.split(":", 1)[1].strip()
    return ""


# Minimal decode table for the Arm cores KleidiBench is likely to meet.
_ARM_PARTS = {
    ("0x41", "0xd0c"): "Arm Neoverse N1 (e.g. Ampere Altra / Graviton2)",
    ("0x41", "0xd40"): "Arm Neoverse V1 (e.g. Graviton3)",
    ("0x41", "0xd4f"): "Arm Neoverse V2 (e.g. Graviton4)",
    ("0x41", "0xd49"): "Arm Neoverse N2",
    ("0xc0", "0xac3"): "Ampere Altra (Neoverse N1)",
}


def _decode_arm_part(impl: str, part: str) -> str:
    return _ARM_PARTS.get((impl.lower(), part.lower()), f"Arm core impl={impl} part={part}")


def _total_ram_gb() -> float:
    meminfo = Path("/proc/meminfo")
    if meminfo.exists():
        for line in meminfo.read_text().splitlines():
            if line.startswith("MemTotal"):
                kb = int(line.split()[1])
                return kb / 1024 / 1024
    # macOS / fallback
    try:
        out = subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True)
        return int(out.stdout.strip()) / 1024 / 1024 / 1024
    except Exception:
        return 0.0


def save_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str))


def load_json(path: Path):
    return json.loads(Path(path).read_text())


def timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
