# KleidiBench report — Phi-3.5-mini-instruct

- **Host:** Arm Neoverse N2 · 4 cores · 15.6 GB · features: asimddp, i8mm, sve, sve2, bf16
- **llama.cpp:** 2d973636e
- **Run:** 2026-07-04T11:46:38

## Arm optimization gains (Q4_0)

- **KleidiAI vs llama.cpp default Arm path** — prefill 53.97 -> 54.38 tok/s (**1.01x**), decode 17.76 -> 18.57 tok/s (**1.05x**)
- **KleidiAI vs naive (no Arm repack)** — prefill 21.28 -> 54.38 tok/s (**2.56x**), decode 11.63 -> 18.57 tok/s (**1.6x**)
- Best at 4 threads.

## Arm optimization gains (Q8_0)

- **KleidiAI vs llama.cpp default Arm path** — prefill 47.35 -> 81.78 tok/s (**1.73x**), decode 13.62 -> 16.78 tok/s (**1.23x**)
- **KleidiAI vs naive (no Arm repack)** — prefill 24.49 -> 81.78 tok/s (**3.34x**), decode 11.96 -> 16.78 tok/s (**1.4x**)
- Best at 4 threads.

## Full sweep

| Quant | Build | Threads | Size (GB) | Prefill tok/s | Decode tok/s | TTFT (ms) | Peak RAM (GB) | Perplexity |
|-------|-------|--------:|----------:|--------------:|-------------:|----------:|--------------:|----------:|
| F16 | kleidiai-off | 4 | 7.118 | 16.7 | 7.96 | 30653.2 | 7.399 | 8.9838 |
| Q4_0 | kleidiai-off | 1 | 2.027 | 13.57 | 5.29 | 37727.4 | 4.176 | 9.7101 |
| Q4_0 | kleidiai-off | 2 | 2.027 | 27.28 | 10.15 | 18769.6 | 4.176 | 9.7101 |
| Q4_0 | kleidiai-off | 4 | 2.027 | 53.97 | 17.76 | 9487.4 | 4.176 | 9.7101 |
| Q4_0 | kleidiai-on | 1 | 2.027 | 13.7 | 5.6 | 37370.7 | 4.176 | 9.7101 |
| Q4_0 | kleidiai-on | 2 | 2.027 | 27.43 | 10.31 | 18665.0 | 4.176 | 9.7101 |
| Q4_0 | kleidiai-on | 4 | 2.027 | 54.38 | 18.57 | 9415.3 | 4.176 | 9.7101 |
| Q4_0 | repack-off | 1 | 2.027 | 5.26 | 3.47 | 97278.3 | 2.304 | 9.7101 |
| Q4_0 | repack-off | 2 | 2.027 | 10.72 | 6.36 | 47773.7 | 2.304 | 9.7101 |
| Q4_0 | repack-off | 4 | 2.027 | 21.28 | 11.63 | 24063.4 | 2.304 | 9.7101 |
| Q4_K_M | kleidiai-off | 1 | 2.232 | 8.82 | 3.91 | 58031.4 | 4.587 | 9.3564 |
| Q4_K_M | kleidiai-off | 2 | 2.232 | 17.74 | 7.38 | 28867.3 | 4.587 | 9.3564 |
| Q4_K_M | kleidiai-off | 4 | 2.232 | 35.08 | 13.46 | 14596.7 | 4.587 | 9.3564 |
| Q4_K_M | kleidiai-on | 1 | 2.232 | 8.47 | 3.91 | 60439.1 | 4.587 | 9.3564 |
| Q4_K_M | kleidiai-on | 2 | 2.232 | 17.75 | 7.51 | 28851.9 | 4.587 | 9.3564 |
| Q4_K_M | kleidiai-on | 4 | 2.232 | 35.15 | 13.67 | 14566.3 | 4.587 | 9.3564 |
| Q4_K_M | repack-off | 1 | 2.232 | 5.33 | 3.57 | 96096.6 | 2.51 | 9.3564 |
| Q4_K_M | repack-off | 2 | 2.232 | 10.71 | 6.59 | 47806.4 | 2.51 | 9.3564 |
| Q4_K_M | repack-off | 4 | 2.232 | 21.27 | 12.17 | 24065.8 | 2.51 | 9.3564 |
| Q8_0 | kleidiai-off | 1 | 3.782 | 10.16 | 3.78 | 50407.1 | 7.596 | 8.9632 |
| Q8_0 | kleidiai-off | 2 | 3.782 | 23.73 | 6.9 | 21572.5 | 7.596 | 8.9632 |
| Q8_0 | kleidiai-off | 4 | 3.782 | 47.35 | 13.62 | 10812.1 | 7.595 | 8.9632 |
| Q8_0 | kleidiai-on | 1 | 3.782 | 16.77 | 4.47 | 30524.7 | 7.411 | 8.9632 |
| Q8_0 | kleidiai-on | 2 | 3.782 | 40.65 | 8.98 | 12595.9 | 7.411 | 8.9632 |
| Q8_0 | kleidiai-on | 4 | 3.782 | 81.78 | 16.78 | 6260.6 | 7.411 | 8.9632 |
| Q8_0 | repack-off | 1 | 3.782 | 6.02 | 3.53 | 85080.6 | 4.039 | 8.9632 |
| Q8_0 | repack-off | 2 | 3.782 | 12.21 | 6.17 | 41949.7 | 4.059 | 8.9632 |
| Q8_0 | repack-off | 4 | 3.782 | 24.49 | 11.96 | 20908.4 | 4.059 | 8.9632 |

_TTFT is derived from prefill throughput at 512-token prompts. Peak RAM is whole-process peak RSS (model load + all reps)._

## Thread scaling (Q4_0 decode tok/s)

| Threads | repack-off | kleidiai-off | kleidiai-on |
|--------:|---:|---:|---:|
| 1 | 3.47 | 5.29 | 5.6 |
| 2 | 6.36 | 10.15 | 10.31 |
| 4 | 11.63 | 17.76 | 18.57 |
