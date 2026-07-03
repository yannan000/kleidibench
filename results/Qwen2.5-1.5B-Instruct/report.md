# KleidiBench report — Qwen2.5-1.5B-Instruct

- **Host:** Arm Neoverse N2 · 4 cores · 15.6 GB · features: asimddp, i8mm, sve, sve2, bf16
- **llama.cpp:** d4cff114c
- **Run:** 2026-07-03T21:32:41

## Arm optimization gains (Q4_0)

- **KleidiAI vs llama.cpp default Arm path** — prefill 130.64 -> 131.38 tok/s (**1.01x**), decode 35.88 -> 35.96 tok/s (**1.0x**)
- **KleidiAI vs naive (no Arm repack)** — prefill 55.75 -> 131.38 tok/s (**2.36x**), decode 26.79 -> 35.96 tok/s (**1.34x**)
- Best at 4 threads.

## Full sweep

| Quant | Build | Threads | Size (GB) | Prefill tok/s | Decode tok/s | TTFT (ms) | Peak RAM (GB) |
|-------|-------|--------:|----------:|--------------:|-------------:|----------:|--------------:|
| F16 | kleidiai-off | 1 | 2.881 | 13.14 | 6.03 | 38959.2 | 3.024 |
| F16 | kleidiai-off | 2 | 2.881 | 25.13 | 10.98 | 20371.6 | 3.023 |
| F16 | kleidiai-off | 4 | 2.881 | 50.15 | 20.56 | 10209.4 | 3.023 |
| Q4_0 | kleidiai-off | 1 | 0.871 | 34.52 | 10.56 | 14831.7 | 1.859 |
| Q4_0 | kleidiai-off | 2 | 0.871 | 64.8 | 19.14 | 7901.2 | 1.859 |
| Q4_0 | kleidiai-off | 4 | 0.871 | 130.64 | 35.88 | 3919.3 | 1.859 |
| Q4_0 | kleidiai-on | 1 | 0.871 | 34.77 | 10.82 | 14725.8 | 1.859 |
| Q4_0 | kleidiai-on | 2 | 0.871 | 65.26 | 19.48 | 7845.8 | 1.859 |
| Q4_0 | kleidiai-on | 4 | 0.871 | 131.38 | 35.96 | 3897.2 | 1.859 |
| Q4_0 | repack-off | 1 | 0.871 | 14.17 | 7.91 | 36124.6 | 1.001 |
| Q4_0 | repack-off | 2 | 0.871 | 27.76 | 14.03 | 18443.9 | 1.001 |
| Q4_0 | repack-off | 4 | 0.871 | 55.75 | 26.79 | 9183.8 | 1.001 |
| Q4_K_M | kleidiai-off | 1 | 0.918 | 23.37 | 9.37 | 21910.0 | 1.954 |
| Q4_K_M | kleidiai-off | 2 | 0.918 | 44.58 | 17.65 | 11485.9 | 1.954 |
| Q4_K_M | kleidiai-off | 4 | 0.918 | 89.43 | 32.96 | 5725.0 | 1.954 |
| Q4_K_M | kleidiai-on | 1 | 0.918 | 23.39 | 9.37 | 21892.2 | 1.955 |
| Q4_K_M | kleidiai-on | 2 | 0.918 | 44.52 | 17.74 | 11500.2 | 1.954 |
| Q4_K_M | kleidiai-on | 4 | 0.918 | 89.48 | 32.88 | 5722.1 | 1.954 |
| Q4_K_M | repack-off | 1 | 0.918 | 15.08 | 8.51 | 33952.3 | 1.049 |
| Q4_K_M | repack-off | 2 | 0.918 | 29.21 | 15.33 | 17526.6 | 1.049 |
| Q4_K_M | repack-off | 4 | 0.918 | 58.43 | 28.98 | 8762.8 | 1.049 |
| Q8_0 | kleidiai-off | 1 | 1.533 | 30.95 | 11.58 | 16543.1 | 3.181 |
| Q8_0 | kleidiai-off | 2 | 1.533 | 58.5 | 21.56 | 8752.4 | 3.186 |
| Q8_0 | kleidiai-off | 4 | 1.533 | 116.95 | 39.78 | 4378.0 | 3.186 |
| Q8_0 | kleidiai-on | 1 | 1.533 | 50.19 | 12.92 | 10201.4 | 3.113 |
| Q8_0 | kleidiai-on | 2 | 1.533 | 92.4 | 24.41 | 5540.9 | 3.114 |
| Q8_0 | kleidiai-on | 4 | 1.533 | 185.92 | 44.98 | 2753.9 | 3.113 |
| Q8_0 | repack-off | 1 | 1.533 | 17.07 | 8.63 | 29986.1 | 1.672 |
| Q8_0 | repack-off | 2 | 1.533 | 33.04 | 15.18 | 15496.1 | 1.672 |
| Q8_0 | repack-off | 4 | 1.533 | 66.26 | 28.64 | 7727.7 | 1.672 |

_TTFT is derived from prefill throughput at 512-token prompts._
