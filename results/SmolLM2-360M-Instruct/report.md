# KleidiBench report — SmolLM2-360M-Instruct

- **Host:** Arm Neoverse N2 · 4 cores · 15.6 GB · features: asimddp, i8mm, sve, sve2, bf16
- **llama.cpp:** 2d973636e
- **Run:** 2026-07-04T17:55:16

## Arm optimization gains (Q4_0)

- **KleidiAI vs llama.cpp default Arm path** — prefill 275.51 -> 277.35 tok/s (**1.01x**), decode 132.62 -> 122.48 tok/s (**0.92x**)
- **KleidiAI vs naive (no Arm repack)** — prefill 163.04 -> 277.35 tok/s (**1.7x**), decode 97.57 -> 122.48 tok/s (**1.26x**)
- Best at 4 threads.

## Arm optimization gains (Q8_0)

- **KleidiAI vs llama.cpp default Arm path** — prefill 260.65 -> 327.91 tok/s (**1.26x**), decode 130.02 -> 152.83 tok/s (**1.18x**)
- **KleidiAI vs naive (no Arm repack)** — prefill 182.71 -> 327.91 tok/s (**1.79x**), decode 100.0 -> 152.83 tok/s (**1.53x**)
- Best at 4 threads.

## Full sweep

| Quant | Build | Threads | Size (GB) | Prefill tok/s | Decode tok/s | TTFT (ms) | Peak RAM (GB) | Perplexity |
|-------|-------|--------:|----------:|--------------:|-------------:|----------:|--------------:|----------:|
| F16 | kleidiai-off | 4 | 0.676 | 145.23 | 77.64 | 3525.5 | 0.746 | 19.0483 |
| Q4_0 | kleidiai-off | 1 | 0.213 | 77.62 | 48.74 | 6596.4 | 0.493 | 21.8353 |
| Q4_0 | kleidiai-off | 2 | 0.213 | 154.19 | 78.5 | 3320.6 | 0.493 | 21.8353 |
| Q4_0 | kleidiai-off | 4 | 0.213 | 275.51 | 132.62 | 1858.4 | 0.493 | 21.8353 |
| Q4_0 | kleidiai-on | 1 | 0.213 | 78.24 | 51.43 | 6544.1 | 0.491 | 21.8353 |
| Q4_0 | kleidiai-on | 2 | 0.213 | 155.33 | 81.48 | 3296.2 | 0.491 | 21.8353 |
| Q4_0 | kleidiai-on | 4 | 0.213 | 277.35 | 122.48 | 1846.0 | 0.491 | 21.8353 |
| Q4_0 | repack-off | 1 | 0.213 | 43.64 | 32.15 | 11732.2 | 0.283 | 21.8353 |
| Q4_0 | repack-off | 2 | 0.213 | 87.14 | 51.8 | 5875.3 | 0.282 | 21.8353 |
| Q4_0 | repack-off | 4 | 0.213 | 163.04 | 97.57 | 3140.4 | 0.282 | 21.8353 |
| Q4_K_M | kleidiai-off | 1 | 0.252 | 32.93 | 29.24 | 15548.4 | 0.424 | 19.5913 |
| Q4_K_M | kleidiai-off | 2 | 0.252 | 65.72 | 50.5 | 7790.5 | 0.424 | 19.5913 |
| Q4_K_M | kleidiai-off | 4 | 0.252 | 124.84 | 89.89 | 4101.1 | 0.424 | 19.5913 |
| Q4_K_M | kleidiai-on | 1 | 0.252 | 32.84 | 28.37 | 15591.0 | 0.422 | 19.5913 |
| Q4_K_M | kleidiai-on | 2 | 0.252 | 65.72 | 49.78 | 7790.2 | 0.422 | 19.5913 |
| Q4_K_M | kleidiai-on | 4 | 0.252 | 124.93 | 88.23 | 4098.4 | 0.421 | 19.5913 |
| Q4_K_M | repack-off | 1 | 0.252 | 31.27 | 29.52 | 16374.2 | 0.321 | 19.5913 |
| Q4_K_M | repack-off | 2 | 0.252 | 61.95 | 48.85 | 8264.7 | 0.321 | 19.5913 |
| Q4_K_M | repack-off | 4 | 0.252 | 117.93 | 90.04 | 4341.6 | 0.321 | 19.5913 |
| Q8_0 | kleidiai-off | 1 | 0.36 | 73.15 | 46.15 | 6999.0 | 0.785 | 19.0957 |
| Q8_0 | kleidiai-off | 2 | 0.36 | 145.34 | 80.51 | 3522.7 | 0.785 | 19.0957 |
| Q8_0 | kleidiai-off | 4 | 0.36 | 260.65 | 130.02 | 1964.3 | 0.785 | 19.0957 |
| Q8_0 | kleidiai-on | 1 | 0.36 | 94.81 | 51.37 | 5400.4 | 0.769 | 19.0957 |
| Q8_0 | kleidiai-on | 2 | 0.36 | 187.8 | 92.38 | 2726.3 | 0.77 | 19.0957 |
| Q8_0 | kleidiai-on | 4 | 0.36 | 327.91 | 152.83 | 1561.4 | 0.769 | 19.0957 |
| Q8_0 | repack-off | 1 | 0.36 | 49.72 | 32.84 | 10297.4 | 0.429 | 19.0957 |
| Q8_0 | repack-off | 2 | 0.36 | 98.36 | 53.56 | 5205.4 | 0.429 | 19.0957 |
| Q8_0 | repack-off | 4 | 0.36 | 182.71 | 100.0 | 2802.2 | 0.429 | 19.0957 |

_TTFT is derived from prefill throughput at 512-token prompts. Peak RAM is whole-process peak RSS (model load + all reps)._

## Thread scaling (Q4_0 decode tok/s)

| Threads | repack-off | kleidiai-off | kleidiai-on |
|--------:|---:|---:|---:|
| 1 | 32.15 | 48.74 | 51.43 |
| 2 | 51.8 | 78.5 | 81.48 |
| 4 | 97.57 | 132.62 | 122.48 |
