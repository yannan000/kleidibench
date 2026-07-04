# KleidiBench report — Qwen2.5-1.5B-Instruct

- **Host:** Arm Neoverse N2 · 4 cores · 15.6 GB · features: asimddp, i8mm, sve, sve2, bf16
- **llama.cpp:** d4cff114c
- **Run:** 2026-07-04T00:17:32

## Arm optimization gains (Q4_0)

- **KleidiAI vs llama.cpp default Arm path** — prefill 130.85 -> 131.46 tok/s (**1.0x**), decode 36.02 -> 35.73 tok/s (**0.99x**)
- **KleidiAI vs naive (no Arm repack)** — prefill 55.81 -> 131.46 tok/s (**2.36x**), decode 26.64 -> 35.73 tok/s (**1.34x**)
- Best at 4 threads.

## Arm optimization gains (Q8_0)

- **KleidiAI vs llama.cpp default Arm path** — prefill 116.74 -> 186.27 tok/s (**1.6x**), decode 38.72 -> 44.55 tok/s (**1.15x**)
- **KleidiAI vs naive (no Arm repack)** — prefill 65.84 -> 186.27 tok/s (**2.83x**), decode 28.04 -> 44.55 tok/s (**1.59x**)
- Best at 4 threads.

## Full sweep

| Quant | Build | Threads | Size (GB) | Prefill tok/s | Decode tok/s | TTFT (ms) | Peak RAM (GB) | Perplexity |
|-------|-------|--------:|----------:|--------------:|-------------:|----------:|--------------:|----------:|
| F16 | kleidiai-off | 4 | 2.881 | 50.07 | 20.58 | 10224.9 | 3.023 | 20.0566 |
| Q4_0 | kleidiai-off | 1 | 0.871 | 34.55 | 10.53 | 14820.7 | 1.859 | 22.1234 |
| Q4_0 | kleidiai-off | 2 | 0.871 | 64.93 | 19.15 | 7885.5 | 1.859 | 22.1234 |
| Q4_0 | kleidiai-off | 4 | 0.871 | 130.85 | 36.02 | 3912.9 | 1.859 | 22.1234 |
| Q4_0 | kleidiai-on | 1 | 0.871 | 34.81 | 10.73 | 14709.5 | 1.859 | 22.1234 |
| Q4_0 | kleidiai-on | 2 | 0.871 | 57.91 | 19.4 | 8841.7 | 1.859 | 22.1234 |
| Q4_0 | kleidiai-on | 4 | 0.871 | 131.46 | 35.73 | 3894.6 | 1.859 | 22.1234 |
| Q4_0 | repack-off | 1 | 0.871 | 13.97 | 7.84 | 36649.5 | 1.001 | 22.1234 |
| Q4_0 | repack-off | 2 | 0.871 | 27.83 | 14.0 | 18397.2 | 1.001 | 22.1234 |
| Q4_0 | repack-off | 4 | 0.871 | 55.81 | 26.64 | 9174.6 | 1.001 | 22.1234 |
| Q4_K_M | kleidiai-off | 1 | 0.918 | 23.32 | 9.43 | 21954.7 | 1.954 | 21.6528 |
| Q4_K_M | kleidiai-off | 2 | 0.918 | 44.55 | 17.78 | 11492.5 | 1.954 | 21.6528 |
| Q4_K_M | kleidiai-off | 4 | 0.918 | 89.58 | 32.78 | 5715.7 | 1.954 | 21.6528 |
| Q4_K_M | kleidiai-on | 1 | 0.918 | 23.41 | 9.4 | 21872.1 | 1.955 | 21.6528 |
| Q4_K_M | kleidiai-on | 2 | 0.918 | 44.63 | 17.73 | 11472.8 | 1.954 | 21.6528 |
| Q4_K_M | kleidiai-on | 4 | 0.918 | 89.68 | 32.45 | 5709.1 | 1.954 | 21.6528 |
| Q4_K_M | repack-off | 1 | 0.918 | 15.08 | 8.38 | 33952.8 | 1.049 | 21.6528 |
| Q4_K_M | repack-off | 2 | 0.918 | 29.3 | 15.28 | 17476.4 | 1.049 | 21.6528 |
| Q4_K_M | repack-off | 4 | 0.918 | 58.55 | 29.1 | 8744.7 | 1.049 | 21.6528 |
| Q8_0 | kleidiai-off | 1 | 1.533 | 30.81 | 11.35 | 16620.3 | 3.186 | 20.0899 |
| Q8_0 | kleidiai-off | 2 | 1.533 | 58.27 | 21.39 | 8786.2 | 3.186 | 20.0899 |
| Q8_0 | kleidiai-off | 4 | 1.533 | 116.74 | 38.72 | 4385.8 | 3.186 | 20.0899 |
| Q8_0 | kleidiai-on | 1 | 1.533 | 49.45 | 12.75 | 10353.5 | 3.113 | 20.0899 |
| Q8_0 | kleidiai-on | 2 | 1.533 | 92.07 | 24.05 | 5560.7 | 3.114 | 20.0899 |
| Q8_0 | kleidiai-on | 4 | 1.533 | 186.27 | 44.55 | 2748.6 | 3.113 | 20.0899 |
| Q8_0 | repack-off | 1 | 1.533 | 16.66 | 8.36 | 30738.3 | 1.672 | 20.0899 |
| Q8_0 | repack-off | 2 | 1.533 | 32.73 | 14.83 | 15644.5 | 1.672 | 20.0899 |
| Q8_0 | repack-off | 4 | 1.533 | 65.84 | 28.04 | 7776.8 | 1.669 | 20.0899 |

_TTFT is derived from prefill throughput at 512-token prompts. Peak RAM is whole-process peak RSS (model load + all reps)._

## Thread scaling (Q4_0 decode tok/s)

| Threads | repack-off | kleidiai-off | kleidiai-on |
|--------:|---:|---:|---:|
| 1 | 7.84 | 10.53 | 10.73 |
| 2 | 14.0 | 19.15 | 19.4 |
| 4 | 26.64 | 36.02 | 35.73 |
