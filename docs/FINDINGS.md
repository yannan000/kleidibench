# Findings: where Arm CPU inference speed actually comes from

Measured with KleidiBench on GitHub Actions `ubuntu-24.04-arm` runners —
**Arm Neoverse N2**, 4 vCPU, features `dotprod, i8mm, sve, sve2, bf16` —
llama.cpp `d4cff114c`, Qwen2.5 0.5B/1.5B/3B, 3 reps per point. Raw data in
[`results/`](../results/).

## 1. KleidiAI's headline win is Q8_0, not Q4_0

The common mental model is "flip `GGML_CPU_KLEIDIAI=ON`, Q4_0 gets faster."
What we measured on the 3B model at 4 threads:

| Quant | KleidiAI OFF (default) | KleidiAI ON | Direct gain |
|-------|-----------------------:|------------:|------------:|
| Q4_0 prefill | 70.2 tok/s | 70.9 tok/s | 1.01× |
| **Q8_0 prefill** | **62.2 tok/s** | **107.7 tok/s** | **1.73×** |
| Q8_0 decode | 20.3 tok/s | 23.3 tok/s | 1.15× |

Why: llama.cpp's **default** aarch64 CPU backend already runtime-repacks Q4_0
weights into blocked layouts and dispatches `i8mm`/dotprod GEMM kernels — so at
Q4_0, KleidiAI and the default path are two implementations of the same idea
and land within 1% of each other. At **Q8_0 the default path does not repack**,
while KleidiAI's `i8mm` micro-kernels do kick in — a genuine 1.73× prefill win
from one build flag.

Practical takeaway: **if you serve Q8_0 on Arm, build with KleidiAI — it is
free speed.** Q8_0+KleidiAI was the fastest configuration we measured for
*every* model in the sweep (e.g. 3B: 23.3 tok/s decode vs 19.4 for Q4_0),
while also being the highest-quality quant (+1.3% perplexity vs F16 — see
finding 4). If RAM allows, it dominates.

## 2. "Optimized for Arm" is mostly the repack path — and it's huge

Disabling all Arm weight-repacking (`-DGGML_CPU_REPACK=OFF`, our "naive" build)
shows what the Arm-specific work is collectively worth on Q4_0 (3B, 4t):

| Build | Prefill tok/s | Decode tok/s |
|-------|--------------:|-------------:|
| naive (no repack) | 27.9 | 14.0 |
| llama.cpp default Arm path | 70.3 | 19.6 |
| KleidiAI | 70.8 | 19.7 |

**2.5× prefill / 1.4× decode** between naive and Arm-optimized. Any benchmark
that only compares "KleidiAI on vs off" silently rides on top of the default
repack path and concludes "KleidiAI does nothing" — which is both true (at
Q4_0) and deeply misleading (see finding 1). A fair Arm benchmark needs the
third, naive baseline. That is why KleidiBench builds llama.cpp three ways.

## 3. Prefill scales with threads almost perfectly; decode doesn't

3B Q4_0, KleidiAI build:

| Threads | Prefill tok/s (scaling) | Decode tok/s (scaling) |
|--------:|------------------------:|-----------------------:|
| 1 | 18.0 (1.0×) | 5.9 (1.0×) |
| 2 | 35.8 (2.0×) | 10.6 (1.8×) |
| 4 | 70.8 (3.9×) | 19.7 (3.3×) |

Prefill is compute-bound (GEMM) and eats cores linearly; decode is increasingly
memory-bandwidth-bound. Cloud sizing implication: **more vCPUs keep helping
time-to-first-token, but decode throughput saturates** — for chat workloads
dominated by decode, several small Arm instances beat one big one at equal
total cores.

## 4. Quantization is still the biggest single lever — and quality is measurable

3B model, best build per quant, 4 threads, perplexity via `llama-perplexity`
on a fixed corpus (lower = better; the delta vs F16 is what matters):

| Quant | Size | Prefill | Decode | Peak RAM | Perplexity (Δ vs F16) |
|-------|-----:|--------:|-------:|---------:|----------------------:|
| F16 | 5.75 GB | 23.4 | 10.9 | 5.9 GB | 16.88 (—) |
| Q8_0 (KleidiAI) | 3.06 GB | 107.7 | 23.3 | 6.1 GB | 17.11 (**+1.3%**) |
| Q4_K_M | 1.80 GB | 46.1 | 17.6 | 3.7 GB | 18.11 (+7.3%) |
| Q4_0 (KleidiAI) | 1.70 GB | 70.9 | 19.4 | 3.5 GB | 20.27 (+20.1%) |

F16 → Q4_0: **3.4× smaller, 3.0× faster prefill, 1.8× faster decode** — at a
real 20% perplexity cost. Two nuances the quality column exposes:

- **Q8_0's quality is nearly free (+1.3%)** while also being the fastest config
  measured (finding 1). If RAM allows, Q8_0+KleidiAI dominates on every axis
  except footprint.
- **Q4_K_M beats Q4_0 on quality (+7% vs +20%) but loses on speed** (no
  repack/KleidiAI path for K-quants) — the classic K-quant tradeoff, now with
  numbers on both sides.

RAM subtlety: Q8_0's *runtime* peak RSS is as high as F16's because of the
repacked weight copies — on RAM-constrained hosts Q4_0 wins on footprint even
though Q8_0 wins on speed and quality.

## 5. Arm repack buys speed with RAM — 2× resident memory

The optimization has a price nobody quotes: repacked weights are a *copy*.
Gemma 4 12B, Q4_0 (6.3 GB on disk), 4 threads:

| Build | Prefill tok/s | Decode tok/s | Peak RSS |
|-------|--------------:|-------------:|---------:|
| naive (no repack) | 6.9 | 3.9 | **6.7 GB** |
| llama.cpp default / KleidiAI | 16.4 | 6.0 | **12.7 GB** |

Same pattern at every size we measured (3B: 1.9 vs 3.5 GB). Deployment
implication: on RAM-constrained hosts, `-DGGML_CPU_REPACK=OFF` runs models
the optimized build cannot hold — the 12B fit our 15.6 GB runner with just
2.9 GB to spare *because* Q8_0 and anything larger was impossible. Size your
Arm instances for ~2× the GGUF file size if you want the fast path.

## 6. Free CI runners are viable Arm benchmark hardware

Every number above came from GitHub's free `ubuntu-24.04-arm` runners: Neoverse
N2 with `i8mm`/SVE2 — newer instructions than Oracle's free Ampere Altra (N1,
dotprod only). And we measured the noise, not just asserted it: the identical
3B sweep run twice, hours apart, on two different runner instances agreed to
**median 0.54% / max 2.96%** across all 28 configurations (see
[methodology](methodology.md)) — an order of magnitude below the smallest
effect reported here. For relative comparisons — build vs build, quant vs
quant — CI runners are more than adequate, and they make the benchmark
**reproducible by anyone with a GitHub account**.

---

*Reproduce: fork the repo, push, and the smoke test re-derives the pattern; or
dispatch the `benchmark` workflow for the full sweep. Methodology details in
[methodology.md](methodology.md).*
