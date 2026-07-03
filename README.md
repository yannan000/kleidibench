# KleidiBench

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

## Headline results (fill in after first run)

Model: `meta-llama/Llama-3.2-3B` · Host: GitHub Actions `ubuntu-24.04-arm` (Ampere Altra, Neoverse N1, 4 vCPU) · llama.cpp `<commit>`

| Config | Size (GB) | Prefill tok/s | Decode tok/s | TTFT (ms) | Peak RAM (GB) |
|--------|----------:|--------------:|-------------:|----------:|--------------:|
| FP16 (KleidiAI off) | – | – | – | – | – |
| Q8_0 (KleidiAI off) | – | – | – | – | – |
| Q4_K_M (KleidiAI off) | – | – | – | – | – |
| Q4_0 (KleidiAI **off**) | – | – | – | – | – |
| Q4_0 (KleidiAI **on**) | – | – | – | – | – |

**KleidiAI speedup (Q4_0):** prefill `–×`, decode `–×`. _Numbers populate automatically into
`results/` when you run the harness._

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
kleidibench run meta-llama/Llama-3.2-3B    # -> results/<model>/report.md + report.html
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
    ├─ build.py     clone llama.cpp, cmake two builds: KleidiAI ON and OFF
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
| `demo/` | generic OpenAI-compatible chatbot endpoint served from the Arm runner |
| `results/` | committed report artifacts (tables, charts, leaderboard) |
| `.github/workflows/` | `benchmark.yml` (CI smoke test + full sweep), `demo-session.yml` (live SSH for the demo video) |
| `scripts/` | provisioning helper for an optional persistent Arm box (Oracle) |
| `docs/` | setup guide + measurement methodology |

## License

MIT — see [LICENSE](LICENSE).

## Author

Yoofi Annan
