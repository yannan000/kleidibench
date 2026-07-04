# KleidiBench report — granite-4.0-350m

- **Host:** Arm Neoverse N2 · 4 cores · 15.6 GB · features: asimddp, i8mm, sve, sve2, bf16
- **llama.cpp:** 2d973636e
- **Run:** 2026-07-04T18:07:35

## Arm optimization gains (Q4_0)

- **KleidiAI vs llama.cpp default Arm path** — prefill 343.62 -> 346.74 tok/s (**1.01x**), decode 105.24 -> 104.84 tok/s (**1.0x**)
- **KleidiAI vs naive (no Arm repack)** — prefill 205.13 -> 346.74 tok/s (**1.69x**), decode 94.15 -> 104.84 tok/s (**1.11x**)
- Best at 4 threads.

## Arm optimization gains (Q8_0)

- **KleidiAI vs llama.cpp default Arm path** — prefill 324.94 -> 408.03 tok/s (**1.26x**), decode 129.24 -> 151.49 tok/s (**1.17x**)
- **KleidiAI vs naive (no Arm repack)** — prefill 227.74 -> 408.03 tok/s (**1.79x**), decode 94.9 -> 151.49 tok/s (**1.6x**)
- Best at 4 threads.

## Full sweep

| Quant | Build | Threads | Size (GB) | Prefill tok/s | Decode tok/s | TTFT (ms) | Peak RAM (GB) | Perplexity |
|-------|-------|--------:|----------:|--------------:|-------------:|----------:|--------------:|----------:|
| F16 | kleidiai-off | 4 | 0.66 | 181.11 | 70.16 | 2827.1 | 0.731 | - |
| Q4_0 | kleidiai-off | 1 | 0.213 | 87.31 | 35.83 | 5864.3 | 0.491 | 54.5837 |
| Q4_0 | kleidiai-off | 2 | 0.213 | 173.87 | 60.07 | 2944.7 | 0.491 | 54.5837 |
| Q4_0 | kleidiai-off | 4 | 0.213 | 343.62 | 105.24 | 1490.0 | 0.491 | 54.5837 |
| Q4_0 | kleidiai-on | 1 | 0.213 | 87.72 | 36.24 | 5837.0 | 0.491 | 54.5837 |
| Q4_0 | kleidiai-on | 2 | 0.213 | 174.9 | 61.42 | 2927.4 | 0.491 | 54.5837 |
| Q4_0 | kleidiai-on | 4 | 0.213 | 346.74 | 104.84 | 1476.6 | 0.491 | 54.5837 |
| Q4_0 | repack-off | 1 | 0.213 | 51.58 | 30.41 | 9926.0 | 0.283 | 54.5837 |
| Q4_0 | repack-off | 2 | 0.213 | 103.25 | 51.2 | 4958.6 | 0.283 | 54.5837 |
| Q4_0 | repack-off | 4 | 0.213 | 205.13 | 94.15 | 2495.9 | 0.283 | 54.5837 |
| Q4_K_M | kleidiai-off | 1 | 0.221 | 69.65 | 33.56 | 7351.3 | 0.507 | 45.4574 |
| Q4_K_M | kleidiai-off | 2 | 0.221 | 138.64 | 57.68 | 3692.9 | 0.507 | 45.4574 |
| Q4_K_M | kleidiai-off | 4 | 0.221 | 274.46 | 105.61 | 1865.5 | 0.507 | 45.4574 |
| Q4_K_M | kleidiai-on | 1 | 0.221 | 69.64 | 33.58 | 7351.6 | 0.507 | 45.4574 |
| Q4_K_M | kleidiai-on | 2 | 0.221 | 138.82 | 58.64 | 3688.1 | 0.507 | 45.4574 |
| Q4_K_M | kleidiai-on | 4 | 0.221 | 273.53 | 99.81 | 1871.8 | 0.507 | 45.4574 |
| Q4_K_M | repack-off | 1 | 0.221 | 53.46 | 33.09 | 9576.6 | 0.291 | 45.4574 |
| Q4_K_M | repack-off | 2 | 0.221 | 105.69 | 54.16 | 4844.2 | 0.291 | 45.4574 |
| Q4_K_M | repack-off | 4 | 0.221 | 209.9 | 97.28 | 2439.3 | 0.291 | 45.4574 |
| Q8_0 | kleidiai-off | 1 | 0.352 | 82.65 | 46.68 | 6194.7 | 0.769 | 36.7455 |
| Q8_0 | kleidiai-off | 2 | 0.352 | 164.87 | 78.75 | 3105.5 | 0.769 | 36.7455 |
| Q8_0 | kleidiai-off | 4 | 0.352 | 324.94 | 129.24 | 1575.7 | 0.769 | 36.7455 |
| Q8_0 | kleidiai-on | 1 | 0.352 | 103.88 | 50.74 | 4928.7 | 0.753 | 36.7455 |
| Q8_0 | kleidiai-on | 2 | 0.352 | 207.44 | 91.33 | 2468.1 | 0.753 | 36.7455 |
| Q8_0 | kleidiai-on | 4 | 0.352 | 408.03 | 151.49 | 1254.8 | 0.753 | 36.7455 |
| Q8_0 | repack-off | 1 | 0.352 | 58.14 | 32.36 | 8806.1 | 0.422 | 36.7455 |
| Q8_0 | repack-off | 2 | 0.352 | 115.29 | 53.67 | 4440.8 | 0.422 | 36.7455 |
| Q8_0 | repack-off | 4 | 0.352 | 227.74 | 94.9 | 2248.2 | 0.422 | 36.7455 |

_TTFT is derived from prefill throughput at 512-token prompts. Peak RAM is whole-process peak RSS (model load + all reps)._

## Thread scaling (Q4_0 decode tok/s)

| Threads | repack-off | kleidiai-off | kleidiai-on |
|--------:|---:|---:|---:|
| 1 | 30.41 | 35.83 | 36.24 |
| 2 | 51.2 | 60.07 | 61.42 |
| 4 | 94.15 | 105.24 | 104.84 |
