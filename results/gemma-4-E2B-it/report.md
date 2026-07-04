# KleidiBench report — gemma-4-E2B-it

- **Host:** Arm Neoverse N2 · 4 cores · 15.6 GB · features: asimddp, i8mm, sve, sve2, bf16
- **llama.cpp:** 2d973636e
- **Run:** 2026-07-04T15:56:10

## Arm optimization gains (Q4_0)

- **KleidiAI vs llama.cpp default Arm path** — prefill 46.23 -> 46.45 tok/s (**1.0x**), decode 23.39 -> 23.28 tok/s (**1.0x**)
- **KleidiAI vs naive (no Arm repack)** — prefill 27.67 -> 46.45 tok/s (**1.68x**), decode 17.37 -> 23.28 tok/s (**1.34x**)
- Best at 4 threads.

## Arm optimization gains (Q8_0)

- **KleidiAI vs llama.cpp default Arm path** — prefill 44.57 -> 55.87 tok/s (**1.25x**), decode 20.84 -> 23.32 tok/s (**1.12x**)
- **KleidiAI vs naive (no Arm repack)** — prefill 31.35 -> 55.87 tok/s (**1.78x**), decode 16.89 -> 23.32 tok/s (**1.38x**)
- Best at 4 threads.

## Full sweep

| Quant | Build | Threads | Size (GB) | Prefill tok/s | Decode tok/s | TTFT (ms) | Peak RAM (GB) | Perplexity |
|-------|-------|--------:|----------:|--------------:|-------------:|----------:|--------------:|----------:|
| Q4_0 | kleidiai-off | 1 | 2.833 | 12.35 | 7.34 | 41462.8 | 4.218 | 76.8164 |
| Q4_0 | kleidiai-off | 2 | 2.833 | 24.58 | 13.06 | 20834.1 | 4.218 | 76.8164 |
| Q4_0 | kleidiai-off | 4 | 2.833 | 46.23 | 23.39 | 11075.9 | 4.218 | 76.8164 |
| Q4_0 | kleidiai-on | 1 | 2.833 | 12.39 | 7.44 | 41314.6 | 4.218 | 76.8164 |
| Q4_0 | kleidiai-on | 2 | 2.833 | 24.69 | 13.24 | 20734.1 | 4.218 | 76.8164 |
| Q4_0 | kleidiai-on | 4 | 2.833 | 46.45 | 23.28 | 11021.5 | 4.218 | 76.8164 |
| Q4_0 | repack-off | 1 | 2.833 | 7.14 | 5.18 | 71669.8 | 3.055 | 76.8164 |
| Q4_0 | repack-off | 2 | 2.833 | 14.32 | 9.26 | 35753.5 | 3.055 | 76.8164 |
| Q4_0 | repack-off | 4 | 2.833 | 27.67 | 17.37 | 18500.6 | 3.055 | 76.8164 |
| Q4_K_M | kleidiai-off | 1 | 2.893 | 10.09 | 6.61 | 50718.9 | 4.362 | 91.9976 |
| Q4_K_M | kleidiai-off | 2 | 2.893 | 20.06 | 11.95 | 25517.4 | 4.362 | 91.9976 |
| Q4_K_M | kleidiai-off | 4 | 2.893 | 38.08 | 21.4 | 13446.8 | 4.362 | 91.9976 |
| Q4_K_M | kleidiai-on | 1 | 2.893 | 10.08 | 6.55 | 50803.8 | 4.362 | 91.9976 |
| Q4_K_M | kleidiai-on | 2 | 2.893 | 20.06 | 11.99 | 25521.1 | 4.362 | 91.9976 |
| Q4_K_M | kleidiai-on | 4 | 2.893 | 38.14 | 21.38 | 13425.9 | 4.362 | 91.9976 |
| Q4_K_M | repack-off | 1 | 2.893 | 7.51 | 5.36 | 68175.6 | 3.117 | 91.9976 |
| Q4_K_M | repack-off | 2 | 2.893 | 14.96 | 9.87 | 34235.3 | 3.117 | 91.9976 |
| Q4_K_M | repack-off | 4 | 2.893 | 28.74 | 18.11 | 17812.9 | 3.116 | 91.9976 |
| Q8_0 | kleidiai-off | 1 | 4.702 | 11.85 | 6.44 | 43207.7 | 7.158 | 97.2733 |
| Q8_0 | kleidiai-off | 2 | 4.702 | 23.63 | 11.79 | 21670.7 | 7.158 | 97.2733 |
| Q8_0 | kleidiai-off | 4 | 4.702 | 44.57 | 20.84 | 11486.8 | 7.158 | 97.2733 |
| Q8_0 | kleidiai-on | 1 | 4.702 | 15.01 | 7.22 | 34101.1 | 7.044 | 97.2733 |
| Q8_0 | kleidiai-on | 2 | 4.702 | 30.04 | 13.04 | 17045.0 | 7.044 | 97.2733 |
| Q8_0 | kleidiai-on | 4 | 4.702 | 55.87 | 23.32 | 9164.6 | 7.043 | 97.2733 |
| Q8_0 | repack-off | 1 | 4.702 | 8.18 | 5.18 | 62623.5 | 4.924 | 97.2733 |
| Q8_0 | repack-off | 2 | 4.702 | 16.31 | 9.17 | 31393.9 | 4.924 | 97.2733 |
| Q8_0 | repack-off | 4 | 4.702 | 31.35 | 16.89 | 16331.5 | 4.924 | 97.2733 |

_TTFT is derived from prefill throughput at 512-token prompts. Peak RAM is whole-process peak RSS (model load + all reps)._

## Thread scaling (Q4_0 decode tok/s)

| Threads | repack-off | kleidiai-off | kleidiai-on |
|--------:|---:|---:|---:|
| 1 | 5.18 | 7.34 | 7.44 |
| 2 | 9.26 | 13.06 | 13.24 |
| 4 | 17.37 | 23.39 | 23.28 |
