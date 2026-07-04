# KleidiBench report — Qwythos-9B

- **Host:** Arm Neoverse N2 · 4 cores · 15.6 GB · features: asimddp, i8mm, sve, sve2, bf16
- **llama.cpp:** 2d973636e
- **Run:** 2026-07-04T15:24:08

## Full sweep

| Quant | Build | Threads | Size (GB) | Prefill tok/s | Decode tok/s | TTFT (ms) | Peak RAM (GB) | Perplexity |
|-------|-------|--------:|----------:|--------------:|-------------:|----------:|--------------:|----------:|
| Q4_K_M | kleidiai-off | 2 | 5.243 | 10.97 | 3.43 | 46691.7 | 10.039 | 8.6281 |
| Q4_K_M | kleidiai-off | 4 | 5.243 | 21.57 | 6.48 | 23734.5 | 10.039 | 8.6281 |
| Q4_K_M | kleidiai-on | 2 | 5.243 | 10.98 | 3.43 | 46633.2 | 10.039 | 8.6281 |
| Q4_K_M | kleidiai-on | 4 | 5.243 | 21.63 | 6.49 | 23672.0 | 10.039 | 8.6281 |
| Q4_K_M | repack-off | 2 | 5.243 | 6.16 | 3.01 | 83051.0 | 5.5 | 8.6281 |
| Q4_K_M | repack-off | 4 | 5.243 | 12.24 | 5.91 | 41816.9 | 5.5 | 8.6281 |

_TTFT is derived from prefill throughput at 512-token prompts. Peak RAM is whole-process peak RSS (model load + all reps)._
