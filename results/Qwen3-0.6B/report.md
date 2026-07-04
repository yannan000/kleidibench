# KleidiBench report — Qwen3-0.6B

- **Host:** Arm Neoverse N2 · 4 cores · 15.6 GB · features: asimddp, i8mm, sve, sve2, bf16
- **llama.cpp:** 2d973636e
- **Run:** 2026-07-04T17:39:24

## Arm optimization gains (Q4_0)

- **KleidiAI vs llama.cpp default Arm path** — prefill 175.7 -> 176.87 tok/s (**1.01x**), decode 68.1 -> 70.44 tok/s (**1.03x**)
- **KleidiAI vs naive (no Arm repack)** — prefill 108.83 -> 176.87 tok/s (**1.63x**), decode 57.48 -> 70.44 tok/s (**1.23x**)
- Best at 4 threads.

## Arm optimization gains (Q8_0)

- **KleidiAI vs llama.cpp default Arm path** — prefill 167.05 -> 204.92 tok/s (**1.23x**), decode 78.05 -> 88.96 tok/s (**1.14x**)
- **KleidiAI vs naive (no Arm repack)** — prefill 119.81 -> 204.92 tok/s (**1.71x**), decode 54.65 -> 88.96 tok/s (**1.63x**)
- Best at 4 threads.

## Full sweep

| Quant | Build | Threads | Size (GB) | Prefill tok/s | Decode tok/s | TTFT (ms) | Peak RAM (GB) | Perplexity |
|-------|-------|--------:|----------:|--------------:|-------------:|----------:|--------------:|----------:|
| F16 | kleidiai-off | 4 | 1.406 | 98.54 | 43.97 | 5195.6 | 1.543 | 46.5377 |
| Q4_0 | kleidiai-off | 1 | 0.437 | 44.59 | 22.38 | 11481.2 | 0.848 | 53.1725 |
| Q4_0 | kleidiai-off | 2 | 0.437 | 88.84 | 38.93 | 5763.4 | 0.848 | 53.1725 |
| Q4_0 | kleidiai-off | 4 | 0.437 | 175.7 | 68.1 | 2914.1 | 0.848 | 53.1725 |
| Q4_0 | kleidiai-on | 1 | 0.437 | 44.73 | 23.0 | 11445.8 | 0.848 | 53.1725 |
| Q4_0 | kleidiai-on | 2 | 0.437 | 89.33 | 40.63 | 5731.2 | 0.848 | 53.1725 |
| Q4_0 | kleidiai-on | 4 | 0.437 | 176.87 | 70.44 | 2894.7 | 0.848 | 53.1725 |
| Q4_0 | repack-off | 1 | 0.437 | 27.49 | 18.36 | 18622.8 | 0.569 | 53.1725 |
| Q4_0 | repack-off | 2 | 0.437 | 54.84 | 31.81 | 9335.7 | 0.569 | 53.1725 |
| Q4_0 | repack-off | 4 | 0.437 | 108.83 | 57.48 | 4704.4 | 0.569 | 53.1725 |
| Q4_K_M | kleidiai-off | 1 | 0.451 | 36.55 | 20.34 | 14006.8 | 0.876 | 53.3748 |
| Q4_K_M | kleidiai-off | 2 | 0.451 | 72.82 | 36.98 | 7030.9 | 0.876 | 53.3748 |
| Q4_K_M | kleidiai-off | 4 | 0.451 | 144.03 | 65.35 | 3554.8 | 0.876 | 53.3748 |
| Q4_K_M | kleidiai-on | 1 | 0.451 | 36.54 | 19.76 | 14010.8 | 0.876 | 53.3748 |
| Q4_K_M | kleidiai-on | 2 | 0.451 | 72.8 | 36.39 | 7033.2 | 0.876 | 53.3748 |
| Q4_K_M | kleidiai-on | 4 | 0.451 | 144.35 | 63.08 | 3546.9 | 0.876 | 53.3748 |
| Q4_K_M | repack-off | 1 | 0.451 | 28.37 | 19.2 | 18048.6 | 0.583 | 53.3748 |
| Q4_K_M | repack-off | 2 | 0.451 | 56.13 | 32.11 | 9121.3 | 0.583 | 53.3748 |
| Q4_K_M | repack-off | 4 | 0.451 | 111.11 | 57.39 | 4607.8 | 0.583 | 53.3748 |
| Q8_0 | kleidiai-off | 1 | 0.749 | 42.02 | 24.73 | 12184.0 | 1.4 | 46.5102 |
| Q8_0 | kleidiai-off | 2 | 0.749 | 84.09 | 45.61 | 6088.9 | 1.4 | 46.5102 |
| Q8_0 | kleidiai-off | 4 | 0.749 | 167.05 | 78.05 | 3065.0 | 1.4 | 46.5102 |
| Q8_0 | kleidiai-on | 1 | 0.749 | 51.79 | 28.85 | 9886.6 | 1.375 | 46.5102 |
| Q8_0 | kleidiai-on | 2 | 0.749 | 103.6 | 52.15 | 4942.1 | 1.375 | 46.5102 |
| Q8_0 | kleidiai-on | 4 | 0.749 | 204.92 | 88.96 | 2498.5 | 1.375 | 46.5102 |
| Q8_0 | repack-off | 1 | 0.749 | 30.39 | 19.23 | 16849.7 | 0.882 | 46.5102 |
| Q8_0 | repack-off | 2 | 0.749 | 60.42 | 30.27 | 8474.6 | 0.882 | 46.5102 |
| Q8_0 | repack-off | 4 | 0.749 | 119.81 | 54.65 | 4273.6 | 0.882 | 46.5102 |

_TTFT is derived from prefill throughput at 512-token prompts. Peak RAM is whole-process peak RSS (model load + all reps)._

## Thread scaling (Q4_0 decode tok/s)

| Threads | repack-off | kleidiai-off | kleidiai-on |
|--------:|---:|---:|---:|
| 1 | 18.36 | 22.38 | 23.0 |
| 2 | 31.81 | 38.93 | 40.63 |
| 4 | 57.48 | 68.1 | 70.44 |
