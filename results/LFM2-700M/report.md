# KleidiBench report — LFM2-700M

- **Host:** Arm Neoverse N2 · 4 cores · 15.6 GB · features: asimddp, i8mm, sve, sve2, bf16
- **llama.cpp:** 2d973636e
- **Run:** 2026-07-04T18:24:43

## Arm optimization gains (Q4_0)

- **KleidiAI vs llama.cpp default Arm path** — prefill 356.65 -> 360.1 tok/s (**1.01x**), decode 74.69 -> 75.14 tok/s (**1.01x**)
- **KleidiAI vs naive (no Arm repack)** — prefill 127.38 -> 360.1 tok/s (**2.83x**), decode 52.59 -> 75.14 tok/s (**1.43x**)
- Best at 4 threads.

## Arm optimization gains (Q8_0)

- **KleidiAI vs llama.cpp default Arm path** — prefill 304.15 -> 588.75 tok/s (**1.94x**), decode 73.43 -> 88.3 tok/s (**1.2x**)
- **KleidiAI vs naive (no Arm repack)** — prefill 152.72 -> 588.75 tok/s (**3.86x**), decode 54.94 -> 88.3 tok/s (**1.61x**)
- Best at 4 threads.

## Full sweep

| Quant | Build | Threads | Size (GB) | Prefill tok/s | Decode tok/s | TTFT (ms) | Peak RAM (GB) | Perplexity |
|-------|-------|--------:|----------:|--------------:|-------------:|----------:|--------------:|----------:|
| F16 | kleidiai-off | 4 | 1.385 | 110.51 | 40.81 | 4633.0 | 1.477 | 29.3653 |
| Q4_0 | kleidiai-off | 1 | 0.416 | 93.67 | 22.84 | 5465.9 | 0.909 | 31.6759 |
| Q4_0 | kleidiai-off | 2 | 0.416 | 186.02 | 40.8 | 2752.4 | 0.909 | 31.6759 |
| Q4_0 | kleidiai-off | 4 | 0.416 | 356.65 | 74.69 | 1435.6 | 0.909 | 31.6759 |
| Q4_0 | kleidiai-on | 1 | 0.416 | 94.73 | 23.37 | 5404.9 | 0.909 | 31.6759 |
| Q4_0 | kleidiai-on | 2 | 0.416 | 187.89 | 41.44 | 2725.0 | 0.909 | 31.6759 |
| Q4_0 | kleidiai-on | 4 | 0.416 | 360.1 | 75.14 | 1421.8 | 0.909 | 31.6759 |
| Q4_0 | repack-off | 1 | 0.416 | 31.93 | 16.64 | 16035.0 | 0.5 | 31.6759 |
| Q4_0 | repack-off | 2 | 0.416 | 63.96 | 27.67 | 8005.0 | 0.5 | 31.6759 |
| Q4_0 | repack-off | 4 | 0.416 | 127.38 | 52.59 | 4019.5 | 0.5 | 31.6759 |
| Q4_K_M | kleidiai-off | 1 | 0.436 | 58.09 | 19.27 | 8814.1 | 0.951 | 30.3522 |
| Q4_K_M | kleidiai-off | 2 | 0.436 | 115.15 | 35.85 | 4446.2 | 0.951 | 30.3522 |
| Q4_K_M | kleidiai-off | 4 | 0.436 | 223.52 | 64.29 | 2290.6 | 0.951 | 30.3522 |
| Q4_K_M | kleidiai-on | 1 | 0.436 | 58.07 | 19.91 | 8816.5 | 0.95 | 30.3522 |
| Q4_K_M | kleidiai-on | 2 | 0.436 | 115.1 | 35.69 | 4448.2 | 0.95 | 30.3522 |
| Q4_K_M | kleidiai-on | 4 | 0.436 | 223.6 | 64.91 | 2289.8 | 0.95 | 30.3522 |
| Q4_K_M | repack-off | 1 | 0.436 | 35.19 | 17.9 | 14549.7 | 0.521 | 30.3522 |
| Q4_K_M | repack-off | 2 | 0.436 | 69.58 | 31.27 | 7358.8 | 0.521 | 30.3522 |
| Q4_K_M | repack-off | 4 | 0.436 | 136.11 | 56.75 | 3761.8 | 0.521 | 30.3522 |
| Q8_0 | kleidiai-off | 1 | 0.737 | 80.0 | 21.53 | 6400.1 | 1.548 | 29.2029 |
| Q8_0 | kleidiai-off | 2 | 0.737 | 160.67 | 40.38 | 3186.6 | 1.548 | 29.2029 |
| Q8_0 | kleidiai-off | 4 | 0.737 | 304.15 | 73.43 | 1683.4 | 1.548 | 29.2029 |
| Q8_0 | kleidiai-on | 1 | 0.737 | 154.67 | 24.97 | 3310.3 | 1.509 | 29.2029 |
| Q8_0 | kleidiai-on | 2 | 0.737 | 314.03 | 48.03 | 1630.4 | 1.509 | 29.2029 |
| Q8_0 | kleidiai-on | 4 | 0.737 | 588.75 | 88.3 | 869.6 | 1.509 | 29.2029 |
| Q8_0 | repack-off | 1 | 0.737 | 37.96 | 17.65 | 13487.1 | 0.822 | 29.2029 |
| Q8_0 | repack-off | 2 | 0.737 | 78.05 | 29.16 | 6560.0 | 0.822 | 29.2029 |
| Q8_0 | repack-off | 4 | 0.737 | 152.72 | 54.94 | 3352.6 | 0.822 | 29.2029 |

_TTFT is derived from prefill throughput at 512-token prompts. Peak RAM is whole-process peak RSS (model load + all reps)._

## Thread scaling (Q4_0 decode tok/s)

| Threads | repack-off | kleidiai-off | kleidiai-on |
|--------:|---:|---:|---:|
| 1 | 16.64 | 22.84 | 23.37 |
| 2 | 27.67 | 40.8 | 41.44 |
| 4 | 52.59 | 74.69 | 75.14 |
