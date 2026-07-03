# KleidiBench report — Qwen2.5-3B-Instruct

- **Host:** Arm Neoverse N2 · 4 cores · 15.6 GB · features: asimddp, i8mm, sve, sve2, bf16
- **llama.cpp:** d4cff114c
- **Run:** 2026-07-03T22:58:41

## Arm optimization gains (Q4_0)

- **KleidiAI vs llama.cpp default Arm path** — prefill 70.33 -> 70.81 tok/s (**1.01x**), decode 19.6 -> 19.71 tok/s (**1.01x**)
- **KleidiAI vs naive (no Arm repack)** — prefill 27.92 -> 70.81 tok/s (**2.54x**), decode 13.95 -> 19.71 tok/s (**1.41x**)
- Best at 4 threads.

## Full sweep

| Quant | Build | Threads | Size (GB) | Prefill tok/s | Decode tok/s | TTFT (ms) | Peak RAM (GB) |
|-------|-------|--------:|----------:|--------------:|-------------:|----------:|--------------:|
| F16 | kleidiai-off | 1 | 5.754 | 5.84 | 3.05 | 87719.3 | 5.918 |
| F16 | kleidiai-off | 2 | 5.754 | 11.75 | 5.66 | 43589.8 | 5.918 |
| F16 | kleidiai-off | 4 | 5.754 | 23.57 | 10.65 | 21722.0 | 5.918 |
| Q4_0 | kleidiai-off | 1 | 1.698 | 17.83 | 5.81 | 28716.5 | 3.536 |
| Q4_0 | kleidiai-off | 2 | 1.698 | 35.51 | 10.35 | 14419.0 | 3.536 |
| Q4_0 | kleidiai-off | 4 | 1.698 | 70.33 | 19.6 | 7280.4 | 3.536 |
| Q4_0 | kleidiai-on | 1 | 1.698 | 17.97 | 5.89 | 28499.5 | 3.536 |
| Q4_0 | kleidiai-on | 2 | 1.698 | 35.78 | 10.58 | 14309.7 | 3.536 |
| Q4_0 | kleidiai-on | 4 | 1.698 | 70.81 | 19.71 | 7230.2 | 3.536 |
| Q4_0 | repack-off | 1 | 1.698 | 7.0 | 4.06 | 73121.8 | 1.856 |
| Q4_0 | repack-off | 2 | 1.698 | 14.05 | 7.33 | 36434.8 | 1.857 |
| Q4_0 | repack-off | 4 | 1.698 | 27.92 | 13.95 | 18336.0 | 1.856 |
| Q4_K_M | kleidiai-off | 1 | 1.797 | 11.73 | 5.0 | 43666.2 | 3.731 |
| Q4_K_M | kleidiai-off | 2 | 1.797 | 23.38 | 9.42 | 21901.8 | 3.731 |
| Q4_K_M | kleidiai-off | 4 | 1.797 | 46.34 | 17.66 | 11049.1 | 3.731 |
| Q4_K_M | kleidiai-on | 1 | 1.797 | 11.75 | 4.94 | 43566.4 | 3.731 |
| Q4_K_M | kleidiai-on | 2 | 1.797 | 23.37 | 9.38 | 21906.6 | 3.731 |
| Q4_K_M | kleidiai-on | 4 | 1.797 | 46.24 | 17.67 | 11072.4 | 3.731 |
| Q4_K_M | repack-off | 1 | 1.797 | 7.36 | 4.33 | 69594.4 | 1.952 |
| Q4_K_M | repack-off | 2 | 1.797 | 14.69 | 7.93 | 34862.4 | 1.952 |
| Q4_K_M | repack-off | 4 | 1.797 | 29.16 | 15.2 | 17556.0 | 1.952 |
| Q8_0 | kleidiai-off | 1 | 3.06 | 15.76 | 5.85 | 32479.8 | 6.25 |
| Q8_0 | kleidiai-off | 2 | 3.06 | 31.5 | 11.0 | 16256.1 | 6.25 |
| Q8_0 | kleidiai-off | 4 | 3.06 | 62.48 | 20.35 | 8195.0 | 6.25 |
| Q8_0 | kleidiai-on | 1 | 3.06 | 26.95 | 6.4 | 18998.3 | 6.085 |
| Q8_0 | kleidiai-on | 2 | 3.06 | 54.34 | 12.15 | 9422.0 | 6.085 |
| Q8_0 | kleidiai-on | 4 | 3.06 | 107.87 | 22.95 | 4746.4 | 6.085 |
| Q8_0 | repack-off | 1 | 3.06 | 8.36 | 4.4 | 61232.4 | 3.219 |
| Q8_0 | repack-off | 2 | 3.06 | 16.68 | 7.84 | 30697.6 | 3.219 |
| Q8_0 | repack-off | 4 | 3.06 | 33.18 | 15.01 | 15428.7 | 3.219 |

_TTFT is derived from prefill throughput at 512-token prompts._
