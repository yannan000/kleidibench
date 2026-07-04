# KleidiBench report — gemma-4-12B-it

- **Host:** Arm Neoverse N2 · 4 cores · 15.6 GB · features: asimddp, i8mm, sve, sve2, bf16
- **llama.cpp:** 2d973636e
- **Run:** 2026-07-04T07:27:22

## Arm optimization gains (Q4_0)

- **KleidiAI vs llama.cpp default Arm path** — prefill 16.34 -> 16.43 tok/s (**1.01x**), decode 5.82 -> 5.97 tok/s (**1.03x**)
- **KleidiAI vs naive (no Arm repack)** — prefill 6.88 -> 16.43 tok/s (**2.39x**), decode 3.85 -> 5.97 tok/s (**1.55x**)
- Best at 4 threads.

## Full sweep

| Quant | Build | Threads | Size (GB) | Prefill tok/s | Decode tok/s | TTFT (ms) | Peak RAM (GB) |
|-------|-------|--------:|----------:|--------------:|-------------:|----------:|--------------:|
| Q4_0 | kleidiai-off | 2 | 6.276 | 8.24 | 3.12 | 62125.4 | 12.727 |
| Q4_0 | kleidiai-off | 4 | 6.276 | 16.34 | 5.82 | 31338.1 | 12.727 |
| Q4_0 | kleidiai-on | 2 | 6.276 | 8.28 | 3.2 | 61833.6 | 12.727 |
| Q4_0 | kleidiai-on | 4 | 6.276 | 16.43 | 5.97 | 31162.1 | 12.727 |
| Q4_0 | repack-off | 2 | 6.276 | 3.46 | 1.99 | 147913.7 | 6.675 |
| Q4_0 | repack-off | 4 | 6.276 | 6.88 | 3.85 | 74382.2 | 6.675 |

_TTFT is derived from prefill throughput at 512-token prompts. Peak RAM is whole-process peak RSS (model load + all reps)._

## Thread scaling (Q4_0 decode tok/s)

| Threads | repack-off | kleidiai-off | kleidiai-on |
|--------:|---:|---:|---:|
| 2 | 1.99 | 3.12 | 3.2 |
| 4 | 3.85 | 5.82 | 5.97 |
