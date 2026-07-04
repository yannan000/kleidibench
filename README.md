# KleidiBench

[![benchmark](https://github.com/yannan000/kleidibench/actions/workflows/benchmark.yml/badge.svg)](https://github.com/yannan000/kleidibench/actions/workflows/benchmark.yml)

**One command to prove how much faster your LLM runs on Arm with KleidiAI.**

KleidiBench quantizes any Hugging Face LLM, builds `llama.cpp` **with and without** Arm's
[KleidiAI](https://gitlab.arm.com/kleidi/kleidiai) micro-kernels, benchmarks every combination on
an Arm64 CPU, and emits a reproducible **markdown + HTML report** — model size, prefill tok/s,
decode tok/s, time-to-first-token, peak RAM, and cost-per-million-tokens.

Everything in this repo runs on **free GitHub Actions arm64 runners**
(`ubuntu-24.04-arm`, real Arm64 CPU, GA and free for public repos — no signup,
no paid cloud, no persistent server required). No GPU. Just Arm CPUs, in CI.

> Submission for the **Arm Create: AI Optimization Challenge 2026**, Track 2 (Cloud AI).

---

## Why it should win

- **Measurable optimization, not vibes.** Every claim is a number from `llama-bench`, reproducible
  with one command on a free Arm box.
- **Leans on Arm's own stack.** KleidiAI via `llama.cpp`'s `GGML_CPU_KLEIDIAI` flag, plus optional
  [Arm Performix](https://developer.arm.com/servers-and-cloud-computing/arm-performix) deep profiling.
- **A reusable artifact.** Point `kleidibench` at *your* model and get *your* Arm numbers. The tool
  outlives the hackathon.
- **Genuinely $0.** No cloud signup, no capacity waitlists — real Arm64 CPU via free GitHub Actions runners.

---

## Headline results (real, from CI)

Model: `Qwen/Qwen2.5-3B-Instruct` · Host: GitHub Actions `ubuntu-24.04-arm` (**Arm Neoverse N2**, 4 vCPU, `i8mm`+`sve2`) · llama.cpp `d4cff114c` · 4 threads

| Config | Size (GB) | Prefill tok/s | Decode tok/s | Peak RAM (GB) | Perplexity |
|--------|----------:|--------------:|-------------:|--------------:|-----------:|
| F16 | 5.75 | 23.4 | 10.9 | 5.9 | 16.88 |
| Q4_0 — naive (no Arm repack) | 1.70 | 27.9 | 14.0 | 1.9 | 20.27 |
| Q4_0 — llama.cpp default Arm path | 1.70 | 70.2 | 19.3 | 3.5 | 20.27 |
| Q4_0 — **KleidiAI** | 1.70 | 70.9 | 19.4 | 3.5 | 20.27 |
| Q8_0 — KleidiAI **off** | 3.06 | 62.2 | 20.3 | 6.3 | 17.11 |
| Q8_0 — **KleidiAI on** | 3.06 | **107.7** | **23.3** | 6.1 | **17.11** |

Four honest takeaways:

- **KleidiAI's direct win is Q8_0: 1.73× prefill** (62.2 → 107.7 tok/s) — the fastest
  config overall, because llama.cpp's default path doesn't repack Q8_0 and KleidiAI's
  `i8mm` kernels do.
- **Q8_0 quality is nearly free**: +1.3% perplexity vs F16, while Q4_0 costs +20%.
  Fastest AND highest-quality quant — if RAM allows, Q8_0+KleidiAI dominates.
- **Arm-optimized kernels vs naive: up to 3.3× prefill** — at Q4_0, llama.cpp's
  default already ships Arm repack kernels that match KleidiAI within 1%; the 3-way
  build comparison keeps that visible instead of hiding it.
- **Quantization stacks on top: F16 → Q4_0 is 3.4× smaller and 3× faster prefill.**

Full sweeps for Qwen2.5 0.5B / 1.5B / 3B (thread scaling, TTFT, RAM, all three builds)
in [results/](results/), including the combined [leaderboard](results/leaderboard.md).
The full analysis — including why on/off-only benchmarks get this wrong — is in
**[docs/FINDINGS.md](docs/FINDINGS.md)**.

Models too big to convert on the host? KleidiBench also benches **pre-quantized
GGUFs** straight from community repos — that's how a **Gemma 4 12B** got measured
on a free 16 GB runner (see `configs/gemma4-12b.yaml`).

**Live (GitHub Pages):**
[interactive leaderboard](https://yannan000.github.io/kleidibench/results/leaderboard.html) ·
[3B report with charts](https://yannan000.github.io/kleidibench/results/Qwen2.5-3B-Instruct/report.html) ·
[demo chat UI](https://yannan000.github.io/kleidibench/demo/chat.html)

---

## Quick start

No Arm hardware required — push to GitHub and the free `ubuntu-24.04-arm`
runner does the rest:

```bash
gh repo create kleidibench --public --source=. --remote=origin --push
# Actions tab -> "benchmark" runs automatically on every push (smoke test)
# Actions tab -> "benchmark" -> Run workflow -> the real sweep, commits results/
# Actions tab -> "demo-session" -> Run workflow -> private SSH session to record the live demo
```

Prefer to run it yourself on any Arm64 Linux box?

```bash
git clone <this-repo> && cd kleidibench
python3 -m pip install -e .
kleidibench run Qwen/Qwen2.5-3B-Instruct   # ungated, no HF login needed
# -> results/<model>/report.md + report.html
kleidibench sweep configs/leaderboard.yaml # multi-model leaderboard
```

See [docs/setup.md](docs/setup.md) for the full walk-through (including a
persistent-Arm-box appendix) and [docs/methodology.md](docs/methodology.md)
for how the numbers are measured.

---

## What it does

```
kleidibench run <hf-model>
    │
    ├─ build.py     clone llama.cpp, cmake 3 builds: naive / default Arm / KleidiAI
    ├─ quantize.py  convert HF -> GGUF, quantize to Q8_0 / Q4_K_M / Q4_0
    ├─ bench.py     run llama-bench per (build × quant), parse tok/s + RAM
    ├─ perfix.py    (optional) capture Arm Performix profile
    └─ report.py    emit results/<model>/report.md + report.html leaderboard
```

## Repo layout

| Path | What |
|------|------|
| `kleidibench/` | the harness (Python) |
| `configs/` | sweep definitions (models, quant list, thread counts) |
| `demo/` | OpenAI-compatible endpoint on the Arm runner + browser chat UI ([chat.html](demo/chat.html)) with live TTFT/tok-s stats |
| `results/` | committed report artifacts (tables, charts, leaderboard) |
| `.github/workflows/` | `benchmark.yml` (CI smoke test + full sweep), `demo-session.yml` (live SSH for the demo video) |
| `scripts/` | provisioning helper for an optional persistent Arm box (Oracle) |
| `docs/` | setup guide + measurement methodology |

## License

MIT — see [LICENSE](LICENSE).

## Author

Yoofi Annan
