# KleidiBench report — Qwen2.5-0.5B-Instruct

- **Host:** Arm Neoverse N2 · 4 cores · 15.6 GB · features: asimddp, i8mm, sve, sve2, bf16
- **llama.cpp:** d4cff114c
- **Run:** 2026-07-03T23:37:14

## Arm optimization gains (Q4_0)

- **KleidiAI vs llama.cpp default Arm path** — prefill 360.01 -> 363.17 tok/s (**1.01x**), decode 121.29 -> 121.64 tok/s (**1.0x**)
- **KleidiAI vs naive (no Arm repack)** — prefill 179.1 -> 363.17 tok/s (**2.03x**), decode 79.32 -> 121.64 tok/s (**1.53x**)
- Best at 4 threads.

## Arm optimization gains (Q8_0)

- **KleidiAI vs llama.cpp default Arm path** — prefill 331.4 -> 466.1 tok/s (**1.41x**), decode 113.96 -> 125.14 tok/s (**1.1x**)
- **KleidiAI vs naive (no Arm repack)** — prefill 205.13 -> 466.1 tok/s (**2.27x**), decode 79.41 -> 125.14 tok/s (**1.58x**)
- Best at 4 threads.

## Full sweep

| Quant | Build | Threads | Size (GB) | Prefill tok/s | Decode tok/s | TTFT (ms) | Peak RAM (GB) | Perplexity |
|-------|-------|--------:|----------:|--------------:|-------------:|----------:|--------------:|----------:|
| F16 | kleidiai-off | 4 | 0.926 | 158.36 | 61.79 | 3233.2 | 1.021 | 33.8761 |
| Q4_0 | kleidiai-off | 1 | 0.328 | 93.28 | 38.7 | 5489.1 | 0.741 | 39.8251 |
| Q4_0 | kleidiai-off | 2 | 0.328 | 182.46 | 68.76 | 2806.1 | 0.741 | 39.8251 |
| Q4_0 | kleidiai-off | 4 | 0.328 | 360.01 | 121.29 | 1422.2 | 0.741 | 39.8251 |
| Q4_0 | kleidiai-on | 1 | 0.328 | 93.95 | 40.42 | 5449.5 | 0.735 | 39.8251 |
| Q4_0 | kleidiai-on | 2 | 0.328 | 183.76 | 70.07 | 2786.2 | 0.735 | 39.8251 |
| Q4_0 | kleidiai-on | 4 | 0.328 | 363.17 | 121.64 | 1409.8 | 0.735 | 39.8251 |
| Q4_0 | repack-off | 1 | 0.328 | 45.76 | 24.72 | 11188.6 | 0.421 | 39.8251 |
| Q4_0 | repack-off | 2 | 0.328 | 90.25 | 42.55 | 5673.4 | 0.421 | 39.8251 |
| Q4_0 | repack-off | 4 | 0.328 | 179.1 | 79.32 | 2858.7 | 0.421 | 39.8251 |
| Q4_K_M | kleidiai-off | 1 | 0.37 | 33.78 | 24.54 | 15158.1 | 0.668 | 34.5209 |
| Q4_K_M | kleidiai-off | 2 | 0.37 | 66.79 | 44.02 | 7666.0 | 0.668 | 34.5209 |
| Q4_K_M | kleidiai-off | 4 | 0.37 | 132.61 | 80.65 | 3861.0 | 0.667 | 34.5209 |
| Q4_K_M | kleidiai-on | 1 | 0.37 | 33.83 | 25.01 | 15134.5 | 0.687 | 34.5209 |
| Q4_K_M | kleidiai-on | 2 | 0.37 | 66.73 | 44.05 | 7673.2 | 0.687 | 34.5209 |
| Q4_K_M | kleidiai-on | 4 | 0.37 | 131.56 | 77.94 | 3891.7 | 0.687 | 34.5209 |
| Q4_K_M | repack-off | 1 | 0.37 | 31.08 | 22.43 | 16475.3 | 0.464 | 34.5209 |
| Q4_K_M | repack-off | 2 | 0.37 | 61.69 | 38.93 | 8299.6 | 0.464 | 34.5209 |
| Q4_K_M | repack-off | 4 | 0.37 | 122.57 | 74.17 | 4177.1 | 0.464 | 34.5209 |
| Q8_0 | kleidiai-off | 1 | 0.495 | 85.6 | 37.35 | 5981.2 | 1.073 | 34.0355 |
| Q8_0 | kleidiai-off | 2 | 0.495 | 167.81 | 66.56 | 3051.1 | 1.073 | 34.0355 |
| Q8_0 | kleidiai-off | 4 | 0.495 | 331.4 | 113.96 | 1545.0 | 1.073 | 34.0355 |
| Q8_0 | kleidiai-on | 1 | 0.495 | 120.94 | 40.62 | 4233.5 | 1.051 | 34.0355 |
| Q8_0 | kleidiai-on | 2 | 0.495 | 236.84 | 73.92 | 2161.8 | 1.051 | 34.0355 |
| Q8_0 | kleidiai-on | 4 | 0.495 | 466.1 | 125.14 | 1098.5 | 1.051 | 34.0355 |
| Q8_0 | repack-off | 1 | 0.495 | 52.99 | 25.63 | 9661.3 | 0.588 | 34.0355 |
| Q8_0 | repack-off | 2 | 0.495 | 103.34 | 42.55 | 4954.6 | 0.588 | 34.0355 |
| Q8_0 | repack-off | 4 | 0.495 | 205.13 | 79.41 | 2495.9 | 0.588 | 34.0355 |

_TTFT is derived from prefill throughput at 512-token prompts. Peak RAM is whole-process peak RSS (model load + all reps)._

## Thread scaling (Q4_0 decode tok/s)

| Threads | repack-off | kleidiai-off | kleidiai-on |
|--------:|---:|---:|---:|
| 1 | 24.72 | 38.7 | 40.42 |
| 2 | 42.55 | 68.76 | 70.07 |
| 4 | 79.32 | 121.29 | 121.64 |
