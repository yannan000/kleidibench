# Devpost submission — KleidiBench

> Copy-paste source for the Devpost form. Placeholders marked `[[LIKE THIS]]`
> get filled from `results/` after the full-benchmark run.

---

## Project name

**KleidiBench**

## Elevator pitch (one line)

KleidiBench turns "should we run this LLM on Arm — and how?" from a week of
engineering into one free CI run that returns a decision, not just a number.

## Track

Cloud AI (Track 2)

---

## Project overview

**What we optimized:** CPU LLM inference on Arm Neoverse N2 — from 23.4 tok/s
prefill / 10.9 tok/s decode (F16, stock llama.cpp: the model as downloaded) to
**107.7 / 23.3 tok/s on Qwen2.5-3B: 4.6× prefill, 2.1× decode, at +1.3%
perplexity** — via three deliberate, individually measured technical changes:
quantization choice (Q8_0, the measured-fastest quant, not the reflexive
Q4_0), KleidiAI's i8mm microkernels (`GGML_CPU_KLEIDIAI=ON`, +73% prefill from
one CMake flag), and per-model thread tuning. Then we packaged the instrument
that found that recipe, so any developer can reproduce the optimization for
*their* model in one $0 CI run — and verified the recipe holds across 10
architectures (1.23–1.94× kernel gain).

**Why that matters — the real blocker to Arm adoption isn't speed, it's uncertainty.** Arm cloud
is marketed as 30–40% cheaper per vCPU, but teams don't capture that saving
because *"will OUR model perform?"* costs an engineer-week to answer properly:
build variants, quantize, control the variables, chase OOMs, interpret.

**KleidiBench collapses that week into one $0 CI run whose output is a serving
decision** — which quant, which build flag, how much RAM, what quality cost,
what $/million-tokens — not a wall of numbers. Fork the repo, push, and a free
GitHub Actions arm64 runner (real Neoverse N2, no cloud account, no quota)
hands you the verdict for *your* model. The benchmark re-runs automatically on
every commit.

How it earns the verdict: `kleidibench run <any-hf-model>`

1. builds llama.cpp three ways — naive (no Arm repack), llama.cpp's default
   Arm path, and KleidiAI (`GGML_CPU_KLEIDIAI`) — same commit, same flags otherwise
2. converts the model to GGUF and quantizes it (F16 → Q8_0 → Q4_K_M → Q4_0),
   or fetches pre-quantized GGUFs for day-one/oversize architectures
3. runs `llama-bench` across every (build × quant × thread-count) combination,
   plus perplexity per quant
4. emits dashboard-style `report.html` per model + a combined leaderboard —
   size, prefill/decode tok/s, TTFT, peak RAM, quality, $/million-tokens

**Why it should win:** it answers the question that decides migrations, and it
keeps paying after the decision — day-one coverage of brand-new architectures
(we benchmarked Gemma 4 before HF→GGUF converter support existed), an Arm
performance-regression watchdog when pointed at llama.cpp nightlies, and a
3-way methodology that structurally prevents the misleading on/off benchmarks
common in this space (it's what surfaced the Q8_0 finding below). A benchmark
result, a de-risking instrument, and permanent ecosystem infrastructure — in
one repo.

## Measured results — baseline → optimized

Host: GitHub Actions `ubuntu-24.04-arm` (**Arm Neoverse N2**, 4 vCPU,
`dotprod`+`i8mm`+`sve2`) · llama.cpp `d4cff114c` · 3 quants × 3 builds ×
1/2/4 threads × 3 reps per model

The end-to-end optimization on the worked example (Qwen2.5-3B), each step
isolated by the 3-way build design:

| | Configuration | Size | Prefill | Decode | Perplexity |
|---|---|---:|---:|---:|---:|
| Baseline | F16, stock llama.cpp (model as downloaded) | 5.75 GB | 23.4 t/s | 10.9 t/s | 16.88 |
| + quantize to Q8_0 | fastest measured quant, near-free quality | 3.06 GB | 62.2 t/s | 20.3 t/s | 17.11 |
| + KleidiAI kernels | `GGML_CPU_KLEIDIAI=ON` (i8mm repack) | 3.06 GB | **107.7 t/s** | **23.3 t/s** | 17.11 |
| **Net** | three changes, all measured | **1.9× smaller** | **4.6×** | **2.1×** | **+1.3%** |

The same kernel gain, replicated across model scale:

| Model | KleidiAI vs naive (Q4_0, prefill / decode) | KleidiAI direct win (Q8_0 prefill) | Best decode tok/s | F16 → Q4_0 size |
|-------|-------------------------------------------:|-----------------------------------:|------------------:|----------------:|
| Qwen2.5-0.5B | ~2.0× / ~1.5× | 1.41× | 125.1 | 0.93 → 0.33 GB |
| Qwen2.5-1.5B | ~2.4× / ~1.3× | 1.60× | 44.6 | 2.9 → 0.9 GB |
| Qwen2.5-3B | **2.5× / 1.4×** | **1.73×** (62.2 → 107.7 tok/s) | 23.3 | 5.75 → 1.70 GB |

Quality is measured too (perplexity, bundled corpus): on the 3B, **Q8_0 costs
only +1.3% vs F16 while being the fastest config**; Q4_0 is 3.4× smaller at
+20%. The full size/speed/quality curve is in every report.

The committed leaderboard now spans **13 models across 7 lineages, 0.35B→12B**:
the three Qwen sizes above, SmolLM2-1.7B, Phi-3.5-mini, the complete
**Gemma 4 ladder (E2B / E4B / 12B)** — benchmarked days after release, before
converter support existed, via KleidiBench's pre-quantized GGUF mode — and
Qwythos-9B, the #1-trending model on Hugging Face at time of writing. Plus a **same-parameter 0.5B cohort** (five architectures at fixed scale): the Q8_0
KleidiAI prefill gain reproduced in **all 10 architectures measured (1.23–1.94×)** —
with Liquid's LFM2 hybrid-conv taking both the biggest gain (1.94×) and the fastest
prefill in the dataset (588.8 tok/s).

The nuanced finding most entries won't have: at Q4_0, llama.cpp's *default*
build already ships Arm repack kernels that match KleidiAI within 1% — the
real ON/OFF flag win lives at **Q8_0 (1.73× prefill)**, where the default path
doesn't repack and KleidiAI's `i8mm` kernels take over. KleidiBench's 3-way
build comparison (naive / default / KleidiAI) is what makes both stories
visible and honest.

Full sweep (quant curve, thread scaling, RAM, TTFT) in
[`results/`](../results/) — committed to the repo, regenerated by CI.

## Who it's for

**Anyone deciding how to run an LLM on Arm gets their answer as a reproducible
report in one command, on hardware that costs nothing.**

- **Teams evaluating Arm migration** — "is Graviton/Axion actually cheaper for
  *our* model?" Fork, push, and CI returns tok/s, TTFT, RAM, and
  $/million-tokens on real Arm silicon — the numbers that go in the migration
  proposal — before renting a single instance.
- **Teams already serving on Arm CPUs** — the sweep answers the config
  question directly. Our own data reduces to a decision tree: serve
  **Q8_0 + KleidiAI** if you have ~2× the file size in RAM (fastest, +1.3%
  perplexity vs F16); **Q4_0** if RAM-tight (3.4× smaller, +20%); build with
  `GGML_CPU_REPACK=OFF` only when footprint beats speed (halves resident RAM).
- **Model publishers and quant makers** — add real Arm numbers to a model card
  without owning Arm hardware; the CI workflow is a copy-paste template.
- **The Arm ecosystem itself** — reproducible third-party evidence of where
  KleidiAI wins (Q8_0: 1.73×) *and* where it's already matched by llama.cpp's
  default path (Q4_0) — pointed at nightly llama.cpp, the same workflow is an
  Arm performance-regression watchdog.
- **Learners** — the cheapest lab there is for "what does quantization
  actually trade?": a size/speed/quality curve on real hardware for $0.

## Functionality / output — three deliverables in one repo

**1 · The harness** (the reusable artifact) · **2 · The findings** (the
measured claims) · **3 · The live demo** (the numbers, running):

- **The harness**: `kleidibench` CLI (`run`, `sweep`, `leaderboard`, `info`) —
  MIT-licensed Python, dependency-light (PyYAML only), orchestrates upstream
  llama.cpp binaries rather than reimplementing inference. Includes the
  pre-quantized GGUF mode (day-one/oversize architectures) and the CI template
  (`.github/workflows/benchmark.yml`) that turns any public repo into an Arm
  benchmark lab — smoke test on every push, full sweeps on dispatch, results
  committed back automatically.
- **The findings**: committed dashboard artifacts under `results/` (per-model
  reports + combined leaderboard: decode tok/s, KleidiAI gain, $/Mtok) and the
  seven-finding analysis in `docs/FINDINGS.md` — the Q8_0 1.73× win, the ~3B
  decode crossover, repack's 2× RAM cost, the 0.54% noise floor.
- **The live demo**: `llama.cpp`'s OpenAI-compatible server serving the
  **optimized configuration from the story above** (Q8_0 + KleidiAI, the
  measured-fastest config) on an arm64 runner, driven
  by a self-contained browser chat UI (`demo/chat.html`) showing live TTFT and
  tok/s per response, or the terminal client (`demo/demo_client.py`)
  (`demo-session.yml` opens the interactive session).

## Setup instructions

See [docs/setup.md](setup.md). Shortest path:

```bash
# fork/clone, then:
gh repo create <you>/kleidibench --public --source=. --push
# -> Actions tab: "benchmark" smoke test runs automatically on real Arm64
# -> Actions tab: "benchmark" -> Run workflow -> full sweep, commits results/
```

Or on any Arm64 Linux box: `pip install -e . && kleidibench run <hf-model>`.

## What's next

- **More Arm targets, same harness**: the tool already decodes Neoverse
  N1/N2/V1/V2 — running the identical sweep on Graviton4 (`i8mm`+SVE at scale)
  and Axion would turn the leaderboard into a cross-cloud Arm buying guide.
- **SME2 tracking**: as SME2-capable Arm cores reach servers, the 3-way build
  comparison is exactly the instrument to measure what KleidiAI's SME2 kernels
  add — zero harness changes needed.
- **Regression watchdog**: the CI smoke test already re-benchmarks on every
  push; pointing it at nightly llama.cpp master would catch Arm performance
  regressions upstream before releases ship.
- **Arm Performix integration** is already stubbed (`--perfix`) for deep
  memory-bandwidth/cache profiling where the toolkit is installed.

## Built with

llama.cpp · KleidiAI (`GGML_CPU_KLEIDIAI`) · GitHub Actions arm64 runners
(`ubuntu-24.04-arm`) · Python · GGUF quantization (Q8_0 / Q4_K_M / Q4_0) ·
tmate · Arm Performix (optional deep profiling)

## Links

- Repo: https://github.com/yannan000/kleidibench (public, MIT)
- Live leaderboard: https://yannan000.github.io/kleidibench/results/leaderboard.html
- Live 3B report (charts + thread scaling): https://yannan000.github.io/kleidibench/results/Qwen2.5-3B-Instruct/report.html
- Findings writeup (learning-ready): https://github.com/yannan000/kleidibench/blob/main/docs/FINDINGS.md
- Demo video: [[YOUTUBE LINK]]
- CI runs (live benchmark evidence): https://github.com/yannan000/kleidibench/actions
