# Measurement methodology

How KleidiBench produces its numbers, so results are reproducible and defensible.

## What "KleidiAI on/off" means

The **only** difference between the two builds is one CMake flag:

```
-DGGML_CPU_KLEIDIAI=ON    vs    -DGGML_CPU_KLEIDIAI=OFF
```

Both are `Release` + `GGML_NATIVE=ON` (compiler targets the host Arm core),
CPU-only (no CUDA/Metal), same commit, same machine, same model file. So any
delta is attributable to KleidiAI's optimized micro-kernels — no code changes,
which is exactly KleidiAI's design goal.

KleidiAI accelerates **`Q4_0`** weights: at model load, llama.cpp repacks them
into a KleidiAI-friendly layout and dispatches to kernels using `dotprod` on
Neoverse N1 (and `i8mm`/SVE on V1/V2). That is why the ON/OFF comparison is run
on the quantized models and the headline number is Q4_0.

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

Quantization trades quality for size/speed. To show the tradeoff honestly, run
`llama-perplexity` (built alongside) on a fixed corpus (e.g. wikitext-2) per
quant and add the column. KleidiBench builds the binary; the sweep hook is left
as a documented follow-up so a base run stays fast on the free tier.

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
