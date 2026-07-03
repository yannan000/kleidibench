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
| Q4_0 prefill | 70.3 tok/s | 70.8 tok/s | 1.01× |
| **Q8_0 prefill** | **62.5 tok/s** | **107.9 tok/s** | **1.73×** |
| Q8_0 decode | 20.4 tok/s | 23.0 tok/s | 1.13× |

Why: llama.cpp's **default** aarch64 CPU backend already runtime-repacks Q4_0
weights into blocked layouts and dispatches `i8mm`/dotprod GEMM kernels — so at
Q4_0, KleidiAI and the default path are two implementations of the same idea
and land within 1% of each other. At **Q8_0 the default path does not repack**,
while KleidiAI's `i8mm` micro-kernels do kick in — a genuine 1.73× prefill win
from one build flag.

Practical takeaway: **if you serve Q8_0 on Arm, build with KleidiAI — it is
free speed.** Q8_0+KleidiAI was the fastest configuration we measured for
*every* model in the sweep (e.g. 3B: 23.0 tok/s decode vs 19.7 for Q4_0),
while also being the highest-quality quant. If RAM allows, it dominates.

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

## 4. Quantization is still the biggest single lever

3B model, best build per quant, 4 threads:

| Quant | Size | Prefill | Decode | Peak RAM |
|-------|-----:|--------:|-------:|---------:|
| F16 | 5.75 GB | 23.6 | 10.7 | 5.9 GB |
| Q8_0 (KleidiAI) | 3.06 GB | 107.9 | 23.0 | 6.1 GB |
| Q4_0 (KleidiAI) | 1.70 GB | 70.8 | 19.7 | 3.5 GB |

F16 → Q4_0: **3.4× smaller, 3.0× faster prefill, 1.8× faster decode**. Note the
RAM subtlety: Q8_0's *runtime* peak RAM is as high as F16-off-disk-size because
of the repacked copies — on RAM-constrained hosts Q4_0 wins on footprint even
though Q8_0 wins on speed.

## 5. Free CI runners are viable Arm benchmark hardware

Every number above came from GitHub's free `ubuntu-24.04-arm` runners: Neoverse
N2 with `i8mm`/SVE2 — newer instructions than Oracle's free Ampere Altra (N1,
dotprod only). Run-to-run variance across our repetitions stayed within a few
percent (llama-bench reports averaged reps). For relative comparisons — build
vs build, quant vs quant, on the same job — CI runners are more than adequate,
and they make the benchmark **reproducible by anyone with a GitHub account**.

---

*Reproduce: fork the repo, push, and the smoke test re-derives the pattern; or
dispatch the `benchmark` workflow for the full sweep. Methodology details in
[methodology.md](methodology.md).*
