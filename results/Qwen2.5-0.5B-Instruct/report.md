# KleidiBench report — Qwen2.5-0.5B-Instruct

- **Host:** Arm Neoverse N2 · 4 cores · 15.6 GB · features: asimddp, i8mm, sve, sve2, bf16
- **llama.cpp:** d4cff114c
- **Run:** 2026-07-03T20:48:49

## Arm optimization gains (Q4_0)

- **KleidiAI vs llama.cpp default Arm path** — prefill 360.89 -> 362.4 tok/s (**1.0x**), decode 127.45 -> 124.42 tok/s (**0.98x**)
- **KleidiAI vs naive (no Arm repack)** — prefill 179.62 -> 362.4 tok/s (**2.02x**), decode 84.33 -> 124.42 tok/s (**1.48x**)
- Best at 4 threads.

## Full sweep

| Quant | Build | Threads | Size (GB) | Prefill tok/s | Decode tok/s | TTFT (ms) | Peak RAM (GB) |
|-------|-------|--------:|----------:|--------------:|-------------:|----------:|--------------:|
| F16 | kleidiai-off | 1 | 0.926 | 41.82 | 19.88 | 12243.5 | 1.021 |
| F16 | kleidiai-off | 2 | 0.926 | 81.69 | 33.82 | 6267.4 | 1.021 |
| F16 | kleidiai-off | 4 | 0.926 | 162.55 | 63.26 | 3149.8 | 1.021 |
| Q4_0 | kleidiai-off | 1 | 0.328 | 93.5 | 40.43 | 5476.1 | 0.741 |
| Q4_0 | kleidiai-off | 2 | 0.328 | 182.87 | 72.14 | 2799.8 | 0.741 |
| Q4_0 | kleidiai-off | 4 | 0.328 | 360.89 | 127.45 | 1418.7 | 0.741 |
| Q4_0 | kleidiai-on | 1 | 0.328 | 94.11 | 41.77 | 5440.6 | 0.735 |
| Q4_0 | kleidiai-on | 2 | 0.328 | 183.99 | 72.32 | 2782.7 | 0.735 |
| Q4_0 | kleidiai-on | 4 | 0.328 | 362.4 | 124.42 | 1412.8 | 0.735 |
| Q4_0 | repack-off | 1 | 0.328 | 45.86 | 25.21 | 11163.7 | 0.421 |
| Q4_0 | repack-off | 2 | 0.328 | 90.47 | 44.49 | 5659.1 | 0.421 |
| Q4_0 | repack-off | 4 | 0.328 | 179.62 | 84.33 | 2850.4 | 0.421 |
| Q4_K_M | kleidiai-off | 1 | 0.37 | 33.85 | 24.53 | 15123.9 | 0.668 |
| Q4_K_M | kleidiai-off | 2 | 0.37 | 66.87 | 44.37 | 7656.4 | 0.668 |
| Q4_K_M | kleidiai-off | 4 | 0.37 | 132.89 | 80.8 | 3852.8 | 0.667 |
| Q4_K_M | kleidiai-on | 1 | 0.37 | 33.91 | 25.41 | 15099.8 | 0.687 |
| Q4_K_M | kleidiai-on | 2 | 0.37 | 66.85 | 45.65 | 7658.8 | 0.687 |
| Q4_K_M | kleidiai-on | 4 | 0.37 | 133.02 | 83.34 | 3849.1 | 0.687 |
| Q4_K_M | repack-off | 1 | 0.37 | 31.33 | 22.98 | 16340.9 | 0.464 |
| Q4_K_M | repack-off | 2 | 0.37 | 61.85 | 40.39 | 8278.8 | 0.464 |
| Q4_K_M | repack-off | 4 | 0.37 | 122.63 | 75.94 | 4175.0 | 0.464 |
| Q8_0 | kleidiai-off | 1 | 0.495 | 85.87 | 37.99 | 5962.7 | 1.072 |
| Q8_0 | kleidiai-off | 2 | 0.495 | 167.9 | 67.23 | 3049.4 | 1.073 |
| Q8_0 | kleidiai-off | 4 | 0.495 | 332.4 | 117.55 | 1540.3 | 1.072 |
| Q8_0 | kleidiai-on | 1 | 0.495 | 121.39 | 41.43 | 4218.0 | 1.051 |
| Q8_0 | kleidiai-on | 2 | 0.495 | 237.41 | 76.29 | 2156.6 | 1.051 |
| Q8_0 | kleidiai-on | 4 | 0.495 | 467.93 | 132.06 | 1094.2 | 1.051 |
| Q8_0 | repack-off | 1 | 0.495 | 53.14 | 26.65 | 9634.8 | 0.588 |
| Q8_0 | repack-off | 2 | 0.495 | 104.43 | 44.2 | 4903.0 | 0.588 |
| Q8_0 | repack-off | 4 | 0.495 | 207.03 | 81.86 | 2473.1 | 0.588 |

_TTFT is derived from prefill throughput at 512-token prompts._
