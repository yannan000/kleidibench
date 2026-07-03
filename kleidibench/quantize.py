"""Convert a Hugging Face model to GGUF and quantize it to several formats.

Pipeline:
    HF repo  --convert_hf_to_gguf.py-->  <model>-F16.gguf  (the baseline)
             --llama-quantize-------->    <model>-Q8_0.gguf
                                          <model>-Q4_K_M.gguf
                                          <model>-Q4_0.gguf   <- KleidiAI's sweet spot

We keep F16 as the quality/size baseline and sweep down from there so the report
can show the size-vs-speed-vs-quality tradeoff curve.
"""
from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from . import util, build as build_mod

# Default quant sweep. Q4_0 is listed last and is the one KleidiAI accelerates.
DEFAULT_QUANTS = ["Q8_0", "Q4_K_M", "Q4_0"]


@dataclass
class ModelArtifact:
    name: str          # short name, e.g. "Llama-3.2-3B"
    quant: str         # "F16", "Q8_0", "Q4_K_M", "Q4_0"
    path: Path
    size_bytes: int

    @property
    def size_gb(self) -> float:
        return round(self.size_bytes / 1024 ** 3, 3)


def short_name(hf_repo: str) -> str:
    return hf_repo.rstrip("/").split("/")[-1]


def _download_hf(hf_repo: str) -> Path:
    """Download an HF repo snapshot. Requires the [hf] extra (huggingface_hub)."""
    try:
        from huggingface_hub import snapshot_download
    except ImportError as e:  # pragma: no cover - depends on optional extra
        raise SystemExit(
            "huggingface_hub not installed. Either `pip install kleidibench[hf]` "
            "or pre-download the model and pass --local-dir."
        ) from e
    util.log(f"downloading {hf_repo} ...")
    local = snapshot_download(
        repo_id=hf_repo,
        allow_patterns=["*.safetensors", "*.json", "*.model", "tokenizer*", "*.txt"],
    )
    return Path(local)


def _ensure_convert_deps() -> None:
    """convert_hf_to_gguf.py needs torch/transformers/gguf etc. Install
    llama.cpp's own pinned requirements file on first use so the harness works
    on a bare host (CI runner, fresh VM) without a manual pip step."""
    if importlib.util.find_spec("torch") and importlib.util.find_spec("gguf"):
        return
    req = util.LLAMA_SRC / "requirements" / "requirements-convert_hf_to_gguf.txt"
    if req.exists():
        util.log("installing llama.cpp converter requirements (torch etc.) ...")
        util.run([sys.executable, "-m", "pip", "install", "-q", "-r", str(req)])
    else:  # older checkouts shipped a single top-level requirements.txt
        util.run([sys.executable, "-m", "pip", "install", "-q",
                  "torch", "numpy", "sentencepiece", "transformers",
                  "gguf", "protobuf"])


def convert_to_f16(hf_repo: str, local_dir: Optional[Path] = None) -> ModelArtifact:
    """Produce the F16 GGUF baseline from an HF checkpoint."""
    util.ensure_dirs()
    name = short_name(hf_repo)
    src = Path(local_dir) if local_dir else _download_hf(hf_repo)

    convert = util.LLAMA_SRC / "convert_hf_to_gguf.py"
    if not convert.exists():
        raise FileNotFoundError(
            f"{convert} missing — run build first so llama.cpp is cloned."
        )
    out = util.MODELS / f"{name}-F16.gguf"
    if not out.exists():
        _ensure_convert_deps()
        util.run([sys.executable, str(convert), str(src), "--outfile", str(out),
                  "--outtype", "f16"])
    return _artifact(name, "F16", out)


def quantize(f16: ModelArtifact, quants: List[str], quantize_bin: Path) -> List[ModelArtifact]:
    """Quantize the F16 baseline into each requested format."""
    arts = [f16]
    for q in quants:
        out = util.MODELS / f"{f16.name}-{q}.gguf"
        if not out.exists():
            util.run([str(quantize_bin), str(f16.path), str(out), q])
        arts.append(_artifact(f16.name, q, out))
    return arts


def _artifact(name: str, quant: str, path: Path) -> ModelArtifact:
    return ModelArtifact(name=name, quant=quant, path=path,
                         size_bytes=path.stat().st_size if path.exists() else 0)


def prepare_models(hf_repo: str, quants: Optional[List[str]] = None,
                   local_dir: Optional[Path] = None,
                   quantize_bin: Optional[Path] = None) -> List[ModelArtifact]:
    """Full prep: F16 baseline + quant sweep. `quantize_bin` from a Build
    (KleidiAI has no effect on quantization itself, so either build works)."""
    quants = quants or DEFAULT_QUANTS
    f16 = convert_to_f16(hf_repo, local_dir=local_dir)
    if quantize_bin is None:
        raise ValueError("quantize_bin required — pass build['off'].llama_quantize")
    return quantize(f16, quants, quantize_bin)
