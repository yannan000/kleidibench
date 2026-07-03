# Measurement methodology

How KleidiBench produces its numbers, so results are reproducible and defensible.

## The 3-way build comparison

Three builds of the same llama.cpp commit, differing only in CMake flags:

| Variant | Flags | What it represents |
|---------|-------|--------------------|
| `repack-off` (naive) | `-DGGML_CPU_KLEIDIAI=OFF -DGGML_CPU_REPACK=OFF` | generic CPU kernels, no Arm-specific weight repacking |
| `kleidiai-off` | `-DGGML_CPU_KLEIDIAI=OFF` | llama.cpp's **default**: its own aarch64 runtime-repack kernels |
| `kleidiai-on` | `-DGGML_CPU_KLEIDIAI=ON` | Arm's KleidiAI micro-kernels |

All are `Release` + `GGML_NATIVE=ON` (compiler targets the host Arm core),
CPU-only, same commit, same machine, same model file.

Why three and not two: modern llama.cpp already ships optimized aarch64 repack
kernels *in its default build*, so "KleidiAI off" is **not** a naive baseline —
an on/off-only comparison understates what Arm-optimized code paths deliver.
The naive build shows the full journey (generic → llama.cpp Arm repack →
KleidiAI) and keeps the headline honest: we report both "KleidiAI vs default"
and "KleidiAI vs naive".

KleidiAI accelerates **`Q4_0`** weights: at model load, llama.cpp repacks them
into a KleidiAI-friendly layout and dispatches to kernels using
`dotprod`/`i8mm`/SVE/SME depending on the host core. That is why the comparison
runs on quantized models and the headline number is Q4_0. (F16 is benched once,
on the default build — neither repack path touches it.)

## Metrics

| Metric | Source | Notes |
|--------|--------|-------|
| Prefill tok/s | `llama-bench` pp test, `avg_ts` | prompt processing throughput |
| Decode tok/s | `llama-bench` tg test, `avg_ts` | token generation throughput |
| TTFT (ms) | derived | `n_prompt / prefill_tps` at the reported prompt length |
| Peak RAM (GB) | `/usr/bin/time -v` max RSS | whole-process resident set |
| Size (GB) | GGUF file size on disk | |

`llama-bench` is invoked with `-o json` and `-r <reps>` (default 3); we read the
averaged `avg_ts` it reports. Defaults: `-p 512 -n 128`.

## Controls for fair numbers

- **Warm cache**: `-r 3` repetitions; llama-bench discards obvious outliers.
- **Thread sweep**: 1 → half → full cores, so throughput-vs-threads is explicit
  rather than a single cherry-picked point.
- **Same everything**: identical commit/model/flags across ON and OFF.
- **Pinning (optional)**: for the tightest numbers, run under
  `taskset -c 0-<n>` and disable other workloads on the box.

## Quality (perplexity) — optional

Quantization trades quality for size/speed. With `--quality` (or `quality:
true` in a sweep config), KleidiBench runs `llama-perplexity --chunks 4` per
quant on a small bundled corpus (`kleidibench/data/corpus.txt`, no network
needed) and adds a Perplexity column to the report. Absolute PPL is
corpus-dependent; the meaningful signal is the **delta** between F16 and each
quant on the same corpus. Quality is measured once per quant on the default
build — quantization changes the math, KleidiAI only changes the speed.

## Arm Performix (optional deep profile)

With `--perfix`, KleidiBench wraps the Q4_0 / KleidiAI-on run in
[Arm Performix](https://developer.arm.com/servers-and-cloud-computing/arm-performix)
to capture memory bandwidth, cache efficiency, and CPU utilization — evidence of
*why* KleidiAI wins. The exact CLI is version-specific; override the invocation
with `KLEIDIBENCH_PERFIX_CMD` (placeholders `{out}` and `{cmd}`).

## Reproducing a published result

Every `results/<model>/results.json` records host info, llama.cpp commit, and
run parameters. Re-run `kleidibench run <model>` on the same instance type and
expect numbers within run-to-run noise (a few %).
