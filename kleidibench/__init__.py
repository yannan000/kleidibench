"""KleidiBench — benchmark LLM inference on Arm with KleidiAI + llama.cpp.

The package orchestrates upstream llama.cpp tools (llama-bench, llama-quantize,
convert_hf_to_gguf.py) — it does not reimplement inference. Each stage lives in
its own module:

    build.py     -> clone + cmake llama.cpp (KleidiAI ON and OFF)
    quantize.py  -> HF -> GGUF -> Q8_0 / Q4_K_M / Q4_0
    bench.py     -> run llama-bench, parse tok/s + RAM + TTFT
    perfix.py    -> optional Arm Performix profiling
    report.py    -> emit markdown + HTML leaderboard
    cli.py       -> `kleidibench run <model>` / `kleidibench sweep <config>`
"""

__version__ = "0.1.0"
