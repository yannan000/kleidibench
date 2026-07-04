# KleidiBench report — gemma-4-E4B-it

- **Host:** Arm Neoverse N2 · 4 cores · 15.6 GB · features: asimddp, i8mm, sve, sve2, bf16
- **llama.cpp:** 2d973636e
- **Run:** 2026-07-04T14:52:09

## Arm optimization gains (Q4_0)

- **KleidiAI vs llama.cpp default Arm path** — prefill 27.96 -> 28.1 tok/s (**1.01x**), decode 12.53 -> 12.49 tok/s (**1.0x**)
- **KleidiAI vs naive (no Arm repack)** — prefill 15.23 -> 28.1 tok/s (**1.85x**), decode 9.07 -> 12.49 tok/s (**1.38x**)
- Best at 4 threads.

## Arm optimization gains (Q8_0)

- **KleidiAI vs llama.cpp default Arm path** — prefill 26.97 -> 36.57 tok/s (**1.36x**), decode 10.99 -> 12.45 tok/s (**1.13x**)
- **KleidiAI vs naive (no Arm repack)** — prefill 17.52 -> 36.57 tok/s (**2.09x**), decode 8.93 -> 12.45 tok/s (**1.39x**)
- Best at 4 threads.

## Full sweep

| Quant | Build | Threads | Size (GB) | Prefill tok/s | Decode tok/s | TTFT (ms) | Peak RAM (GB) | Perplexity |
|-------|-------|--------:|----------:|--------------:|-------------:|----------:|--------------:|----------:|
| Q4_0 | kleidiai-off | 1 | 4.504 | 7.34 | 3.63 | 69719.4 | 7.097 | 29.7249 |
| Q4_0 | kleidiai-off | 2 | 4.504 | 14.63 | 6.72 | 34990.1 | 7.097 | 29.7249 |
| Q4_0 | kleidiai-off | 4 | 4.504 | 27.96 | 12.53 | 18313.3 | 7.097 | 29.7249 |
| Q4_0 | kleidiai-on | 1 | 4.504 | 7.37 | 3.69 | 69429.3 | 7.097 | 29.7249 |
| Q4_0 | kleidiai-on | 2 | 4.504 | 14.69 | 6.83 | 34854.2 | 7.097 | 29.7249 |
| Q4_0 | kleidiai-on | 4 | 4.504 | 28.1 | 12.49 | 18218.4 | 7.097 | 29.7249 |
| Q4_0 | repack-off | 1 | 4.504 | 3.91 | 2.55 | 130970.7 | 4.641 | 29.7249 |
| Q4_0 | repack-off | 2 | 4.504 | 7.81 | 4.78 | 65524.9 | 4.747 | 29.7249 |
| Q4_0 | repack-off | 4 | 4.504 | 15.23 | 9.07 | 33623.3 | 4.743 | 29.7249 |
| Q4_K_M | kleidiai-off | 1 | 4.635 | 5.81 | 3.18 | 88150.0 | 7.348 | 31.2324 |
| Q4_K_M | kleidiai-off | 2 | 4.635 | 11.58 | 6.04 | 44224.8 | 7.436 | 31.2324 |
| Q4_K_M | kleidiai-off | 4 | 4.635 | 22.3 | 11.05 | 22958.4 | 7.436 | 31.2324 |
| Q4_K_M | kleidiai-on | 1 | 4.635 | 5.81 | 3.22 | 88049.3 | 7.437 | 31.2324 |
| Q4_K_M | kleidiai-on | 2 | 4.635 | 11.56 | 6.04 | 44285.5 | 7.436 | 31.2324 |
| Q4_K_M | kleidiai-on | 4 | 4.635 | 22.29 | 11.03 | 22973.3 | 7.437 | 31.2324 |
| Q4_K_M | repack-off | 1 | 4.635 | 4.09 | 2.7 | 125281.9 | 4.825 | 31.2324 |
| Q4_K_M | repack-off | 2 | 4.635 | 8.15 | 5.05 | 62839.1 | 4.879 | 31.2324 |
| Q4_K_M | repack-off | 4 | 4.635 | 15.85 | 9.42 | 32304.1 | 4.879 | 31.2324 |
| Q8_0 | kleidiai-off | 1 | 7.63 | 7.03 | 3.18 | 72841.1 | 12.442 | 29.0211 |
| Q8_0 | kleidiai-off | 2 | 7.63 | 14.08 | 6.08 | 36368.2 | 12.442 | 29.0211 |
| Q8_0 | kleidiai-off | 4 | 7.63 | 26.97 | 10.99 | 18981.3 | 12.442 | 29.0211 |
| Q8_0 | kleidiai-on | 1 | 7.63 | 9.6 | 3.57 | 53314.3 | 12.19 | 29.0211 |
| Q8_0 | kleidiai-on | 2 | 7.63 | 19.34 | 6.77 | 26479.7 | 12.19 | 29.0211 |
| Q8_0 | kleidiai-on | 4 | 7.63 | 36.57 | 12.45 | 14000.9 | 12.19 | 29.0211 |
| Q8_0 | repack-off | 1 | 7.63 | 4.5 | 2.63 | 113795.5 | 7.718 | 29.0211 |
| Q8_0 | repack-off | 2 | 7.63 | 9.0 | 4.77 | 56884.1 | 7.874 | 29.0211 |
| Q8_0 | repack-off | 4 | 7.63 | 17.52 | 8.93 | 29217.2 | 7.874 | 29.0211 |

_TTFT is derived from prefill throughput at 512-token prompts. Peak RAM is whole-process peak RSS (model load + all reps)._

## Thread scaling (Q4_0 decode tok/s)

| Threads | repack-off | kleidiai-off | kleidiai-on |
|--------:|---:|---:|---:|
| 1 | 2.55 | 3.63 | 3.69 |
| 2 | 4.78 | 6.72 | 6.83 |
| 4 | 9.07 | 12.53 | 12.49 |
