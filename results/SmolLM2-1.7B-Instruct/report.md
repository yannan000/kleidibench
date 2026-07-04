# KleidiBench report — SmolLM2-1.7B-Instruct

- **Host:** Arm Neoverse N2 · 4 cores · 15.6 GB · features: asimddp, i8mm, sve, sve2, bf16
- **llama.cpp:** 2d973636e
- **Run:** 2026-07-04T10:04:13

## Arm optimization gains (Q4_0)

- **KleidiAI vs llama.cpp default Arm path** — prefill 115.65 -> 116.91 tok/s (**1.01x**), decode 33.67 -> 35.52 tok/s (**1.05x**)
- **KleidiAI vs naive (no Arm repack)** — prefill 46.6 -> 116.91 tok/s (**2.51x**), decode 24.4 -> 35.52 tok/s (**1.46x**)
- Best at 4 threads.

## Arm optimization gains (Q8_0)

- **KleidiAI vs llama.cpp default Arm path** — prefill 102.86 -> 172.66 tok/s (**1.68x**), decode 32.65 -> 37.58 tok/s (**1.15x**)
- **KleidiAI vs naive (no Arm repack)** — prefill 56.02 -> 172.66 tok/s (**3.08x**), decode 26.5 -> 37.58 tok/s (**1.42x**)
- Best at 4 threads.

## Full sweep

| Quant | Build | Threads | Size (GB) | Prefill tok/s | Decode tok/s | TTFT (ms) | Peak RAM (GB) | Perplexity |
|-------|-------|--------:|----------:|--------------:|-------------:|----------:|--------------:|----------:|
| F16 | kleidiai-off | 4 | 3.19 | 40.0 | 18.61 | 12799.0 | 3.381 | 12.7264 |
| Q4_0 | kleidiai-off | 1 | 0.923 | 29.36 | 10.93 | 17437.6 | 2.019 | 14.2589 |
| Q4_0 | kleidiai-off | 2 | 0.923 | 58.47 | 18.85 | 8756.6 | 2.019 | 14.2589 |
| Q4_0 | kleidiai-off | 4 | 0.923 | 115.65 | 33.67 | 4427.0 | 2.018 | 14.2589 |
| Q4_0 | kleidiai-on | 1 | 0.923 | 29.53 | 11.46 | 17340.7 | 2.019 | 14.2589 |
| Q4_0 | kleidiai-on | 2 | 0.923 | 58.88 | 19.74 | 8695.6 | 2.019 | 14.2589 |
| Q4_0 | kleidiai-on | 4 | 0.923 | 116.91 | 35.52 | 4379.3 | 2.019 | 14.2589 |
| Q4_0 | repack-off | 1 | 0.923 | 11.65 | 7.31 | 43950.5 | 1.107 | 14.2589 |
| Q4_0 | repack-off | 2 | 0.923 | 23.37 | 12.64 | 21909.9 | 1.107 | 14.2589 |
| Q4_0 | repack-off | 4 | 0.923 | 46.6 | 24.4 | 10988.2 | 1.107 | 14.2589 |
| Q4_K_M | kleidiai-off | 1 | 0.983 | 19.66 | 9.13 | 26047.5 | 2.14 | 13.8006 |
| Q4_K_M | kleidiai-off | 2 | 0.983 | 39.11 | 16.65 | 13090.2 | 2.14 | 13.8006 |
| Q4_K_M | kleidiai-off | 4 | 0.983 | 77.2 | 30.89 | 6632.0 | 2.14 | 13.8006 |
| Q4_K_M | kleidiai-on | 1 | 0.983 | 19.6 | 8.74 | 26123.6 | 2.14 | 13.8006 |
| Q4_K_M | kleidiai-on | 2 | 0.983 | 39.0 | 16.04 | 13127.8 | 2.14 | 13.8006 |
| Q4_K_M | kleidiai-on | 4 | 0.983 | 77.18 | 29.68 | 6634.3 | 2.14 | 13.8006 |
| Q4_K_M | repack-off | 1 | 0.983 | 12.29 | 7.85 | 41651.8 | 1.167 | 13.8006 |
| Q4_K_M | repack-off | 2 | 0.983 | 24.67 | 13.79 | 20753.0 | 1.168 | 13.8006 |
| Q4_K_M | repack-off | 4 | 0.983 | 49.04 | 26.9 | 10441.1 | 1.167 | 13.8006 |
| Q8_0 | kleidiai-off | 1 | 1.695 | 26.07 | 9.73 | 19641.9 | 3.56 | 12.7592 |
| Q8_0 | kleidiai-off | 2 | 1.695 | 52.07 | 18.28 | 9832.5 | 3.559 | 12.7592 |
| Q8_0 | kleidiai-off | 4 | 1.695 | 102.86 | 32.65 | 4977.8 | 3.56 | 12.7592 |
| Q8_0 | kleidiai-on | 1 | 1.695 | 42.27 | 10.59 | 12113.9 | 3.479 | 12.7592 |
| Q8_0 | kleidiai-on | 2 | 1.695 | 87.03 | 21.06 | 5883.0 | 3.479 | 12.7592 |
| Q8_0 | kleidiai-on | 4 | 1.695 | 172.66 | 37.58 | 2965.3 | 3.478 | 12.7592 |
| Q8_0 | repack-off | 1 | 1.695 | 13.82 | 7.77 | 37053.5 | 1.883 | 12.7592 |
| Q8_0 | repack-off | 2 | 1.695 | 28.08 | 14.02 | 18232.2 | 1.883 | 12.7592 |
| Q8_0 | repack-off | 4 | 1.695 | 56.02 | 26.5 | 9139.5 | 1.883 | 12.7592 |

_TTFT is derived from prefill throughput at 512-token prompts. Peak RAM is whole-process peak RSS (model load + all reps)._

## Thread scaling (Q4_0 decode tok/s)

| Threads | repack-off | kleidiai-off | kleidiai-on |
|--------:|---:|---:|---:|
| 1 | 7.31 | 10.93 | 11.46 |
| 2 | 12.64 | 18.85 | 19.74 |
| 4 | 24.4 | 33.67 | 35.52 |
