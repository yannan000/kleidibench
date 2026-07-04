# KleidiBench report — Qwen2.5-3B-Instruct

- **Host:** Arm Neoverse N2 · 4 cores · 15.6 GB · features: asimddp, i8mm, sve, sve2, bf16
- **llama.cpp:** d4cff114c
- **Run:** 2026-07-04T01:35:54

## Arm optimization gains (Q4_0)

- **KleidiAI vs llama.cpp default Arm path** — prefill 70.17 -> 70.85 tok/s (**1.01x**), decode 19.32 -> 19.37 tok/s (**1.0x**)
- **KleidiAI vs naive (no Arm repack)** — prefill 27.8 -> 70.85 tok/s (**2.55x**), decode 13.74 -> 19.37 tok/s (**1.41x**)
- Best at 4 threads.

## Arm optimization gains (Q8_0)

- **KleidiAI vs llama.cpp default Arm path** — prefill 62.22 -> 107.72 tok/s (**1.73x**), decode 20.27 -> 23.28 tok/s (**1.15x**)
- **KleidiAI vs naive (no Arm repack)** — prefill 33.13 -> 107.72 tok/s (**3.25x**), decode 14.74 -> 23.28 tok/s (**1.58x**)
- Best at 4 threads.

## Full sweep

| Quant | Build | Threads | Size (GB) | Prefill tok/s | Decode tok/s | TTFT (ms) | Peak RAM (GB) | Perplexity |
|-------|-------|--------:|----------:|--------------:|-------------:|----------:|--------------:|----------:|
| F16 | kleidiai-off | 4 | 5.754 | 23.43 | 10.86 | 21849.1 | 5.918 | 16.8845 |
| Q4_0 | kleidiai-off | 1 | 1.698 | 17.8 | 5.72 | 28760.2 | 3.536 | 20.2735 |
| Q4_0 | kleidiai-off | 2 | 1.698 | 35.47 | 10.28 | 14435.6 | 3.536 | 20.2735 |
| Q4_0 | kleidiai-off | 4 | 1.698 | 70.17 | 19.32 | 7296.1 | 3.536 | 20.2735 |
| Q4_0 | kleidiai-on | 1 | 1.698 | 17.94 | 5.96 | 28535.1 | 3.536 | 20.2735 |
| Q4_0 | kleidiai-on | 2 | 1.698 | 35.73 | 10.49 | 14327.7 | 3.536 | 20.2735 |
| Q4_0 | kleidiai-on | 4 | 1.698 | 70.85 | 19.37 | 7226.8 | 3.536 | 20.2735 |
| Q4_0 | repack-off | 1 | 1.698 | 6.89 | 3.98 | 74298.7 | 1.857 | 20.2735 |
| Q4_0 | repack-off | 2 | 1.698 | 13.96 | 7.17 | 36667.8 | 1.857 | 20.2735 |
| Q4_0 | repack-off | 4 | 1.698 | 27.8 | 13.74 | 18420.2 | 1.856 | 20.2735 |
| Q4_K_M | kleidiai-off | 1 | 1.797 | 11.75 | 5.09 | 43582.2 | 3.731 | 18.1105 |
| Q4_K_M | kleidiai-off | 2 | 1.797 | 23.29 | 9.37 | 21979.1 | 3.731 | 18.1105 |
| Q4_K_M | kleidiai-off | 4 | 1.797 | 46.23 | 17.59 | 11076.1 | 3.731 | 18.1105 |
| Q4_K_M | kleidiai-on | 1 | 1.797 | 11.67 | 4.94 | 43858.4 | 3.731 | 18.1105 |
| Q4_K_M | kleidiai-on | 2 | 1.797 | 23.36 | 9.37 | 21920.1 | 3.731 | 18.1105 |
| Q4_K_M | kleidiai-on | 4 | 1.797 | 46.09 | 17.57 | 11108.8 | 3.731 | 18.1105 |
| Q4_K_M | repack-off | 1 | 1.797 | 7.32 | 4.32 | 69964.7 | 1.952 | 18.1105 |
| Q4_K_M | repack-off | 2 | 1.797 | 14.6 | 7.88 | 35066.8 | 1.952 | 18.1105 |
| Q4_K_M | repack-off | 4 | 1.797 | 29.05 | 15.17 | 17624.2 | 1.952 | 18.1105 |
| Q8_0 | kleidiai-off | 1 | 3.06 | 15.69 | 5.78 | 32622.6 | 6.25 | 17.1097 |
| Q8_0 | kleidiai-off | 2 | 3.06 | 31.37 | 10.97 | 16322.4 | 6.25 | 17.1097 |
| Q8_0 | kleidiai-off | 4 | 3.06 | 62.22 | 20.27 | 8228.8 | 6.25 | 17.1097 |
| Q8_0 | kleidiai-on | 1 | 3.06 | 26.49 | 6.53 | 19327.8 | 6.085 | 17.1097 |
| Q8_0 | kleidiai-on | 2 | 3.06 | 54.19 | 12.51 | 9448.0 | 6.085 | 17.1097 |
| Q8_0 | kleidiai-on | 4 | 3.06 | 107.72 | 23.28 | 4752.9 | 6.085 | 17.1097 |
| Q8_0 | repack-off | 1 | 3.06 | 8.25 | 4.32 | 62057.5 | 3.219 | 17.1097 |
| Q8_0 | repack-off | 2 | 3.06 | 16.61 | 7.74 | 30822.5 | 3.214 | 17.1097 |
| Q8_0 | repack-off | 4 | 3.06 | 33.13 | 14.74 | 15452.6 | 3.219 | 17.1097 |

_TTFT is derived from prefill throughput at 512-token prompts. Peak RAM is whole-process peak RSS (model load + all reps)._

## Thread scaling (Q4_0 decode tok/s)

| Threads | repack-off | kleidiai-off | kleidiai-on |
|--------:|---:|---:|---:|
| 1 | 3.98 | 5.72 | 5.96 |
| 2 | 7.17 | 10.28 | 10.49 |
| 4 | 13.74 | 19.32 | 19.37 |
