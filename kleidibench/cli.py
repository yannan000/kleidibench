"""Command-line entrypoint: `kleidibench run <model>` / `kleidibench sweep <cfg>`.

`run`   — one model, full sweep (quants x KleidiAI on/off x thread counts),
          then write results/<model>/report.{md,html,json}.
`sweep` — a config file listing several models -> per-model reports + a
          combined leaderboard.
`info`  — print detected Arm host + features and exit (quick sanity check).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from . import util, build as build_mod, quantize as quant_mod, bench as bench_mod
from . import report as report_mod, perfix as perfix_mod, leaderboard as lb_mod
from . import quality as quality_mod


def _thread_counts(host, override: Optional[List[int]]) -> List[int]:
    if override:
        return override
    c = host.cores
    # A small scaling curve that always includes the full-core point.
    pts = sorted({1, max(1, c // 2), c})
    return [t for t in pts if t <= c]


def cmd_run(args) -> int:
    util.ensure_dirs()
    host = util.detect_host()
    if not host.is_arm and not args.allow_non_arm:
        util.log(f"host arch is '{host.arch}', not Arm. This benchmark is meant "
                 f"for Arm64. Re-run on the Arm box, or pass --allow-non-arm to force.")
        return 2

    quants = args.quants.split(",") if args.quants else quant_mod.DEFAULT_QUANTS
    threads = _thread_counts(host, [int(t) for t in args.threads.split(",")] if args.threads else None)

    util.log(f"host: {host.cpu_model} | {host.cores} cores | "
             f"features={host.features} | threads={threads} | quants={quants}")

    builds = build_mod.build_all(ref=args.llama_ref, jobs=args.jobs)
    arts = quant_mod.prepare_models(
        args.model, quants=quants,
        local_dir=Path(args.local_dir) if args.local_dir else None,
        quantize_bin=builds["off"].llama_quantize,
    )

    results: List[dict] = []
    for art in arts:
        # F16 only runs once (neither repack nor KleidiAI touch it); quantized
        # weights get the full 3-way comparison: naive -> repack -> KleidiAI.
        # F16 is also benched only at max threads — it is the size/quality
        # baseline, and its 1-thread runs dominate wall-clock on 3B+ models.
        f16 = art.quant == "F16"
        build_variants = ["off"] if f16 else ["naive", "off", "on"]
        art_threads = [threads[-1]] if f16 else threads
        for bv in build_variants:
            for t in art_threads:
                res = bench_mod.run_bench(builds[bv], art, threads=t,
                                          n_prompt=args.n_prompt, n_gen=args.n_gen,
                                          reps=args.reps)
                results.append(res.to_dict())

    # Optional quality pass: perplexity per quant (F16 included as the
    # reference point). KleidiAI does not change the math, only the speed, so
    # one build's binary suffices; max threads keeps the pass short.
    if args.quality:
        corpus = quality_mod.get_corpus()
        for art in arts:
            ppl = quality_mod.measure_perplexity(
                builds["off"].llama_perplexity, art.path, corpus,
                threads=threads[-1])
            for row in results:
                if row["quant"] == art.quant:
                    row["ppl"] = ppl

    # Optional Arm Performix deep profile on the Q4_0 / KleidiAI-on best case.
    if args.perfix:
        q4 = next((a for a in arts if a.quant == "Q4_0"), None)
        if q4:
            perfix_mod.profile(
                [str(builds["on"].llama_bench), "-m", str(q4.path),
                 "-t", str(threads[-1]), "-p", str(args.n_prompt), "-n", str(args.n_gen)],
                out_dir=util.RESULTS / quant_mod.short_name(args.model),
                tag="q4_0-kleidiai-on")

    meta = {"llama_commit": build_mod.llama_commit(), "timestamp": util.timestamp(),
            "n_prompt": args.n_prompt, "n_gen": args.n_gen, "reps": args.reps}
    report_mod.write_report(quant_mod.short_name(args.model), results,
                            host.to_dict(), meta)
    return 0


def cmd_sweep(args) -> int:
    import yaml
    cfg = yaml.safe_load(Path(args.config).read_text())
    models = cfg.get("models", [])
    if not models:
        util.log(f"no models in {args.config}")
        return 2
    rc = 0
    for m in models:
        sub = argparse.Namespace(**vars(args))
        sub.model = m if isinstance(m, str) else m["repo"]
        sub.local_dir = None if isinstance(m, str) else m.get("local_dir")
        sub.quants = cfg.get("quants") and ",".join(cfg["quants"]) or args.quants
        sub.threads = cfg.get("threads") and ",".join(map(str, cfg["threads"])) or args.threads
        rc |= cmd_run(sub)
    lb_mod.build_leaderboard(price_per_hour=cfg.get("price_per_hour", 0.0))
    return rc


def cmd_leaderboard(args) -> int:
    out = lb_mod.build_leaderboard(price_per_hour=args.price_per_hour)
    return 0 if out else 2


def cmd_info(args) -> int:
    host = util.detect_host()
    import json
    print(json.dumps(host.to_dict(), indent=2))
    print("Arm Performix on PATH:", perfix_mod.available())
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="kleidibench",
                                description="Benchmark LLM inference on Arm with KleidiAI.")
    sub = p.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--quants", help="comma list, e.g. Q8_0,Q4_K_M,Q4_0")
    common.add_argument("--threads", help="comma list of thread counts")
    common.add_argument("--n-prompt", type=int, default=512, dest="n_prompt")
    common.add_argument("--n-gen", type=int, default=128, dest="n_gen")
    common.add_argument("--reps", type=int, default=3)
    common.add_argument("--jobs", type=int, default=None, help="parallel build jobs")
    common.add_argument("--llama-ref", default=None, help="pin a llama.cpp git ref")
    common.add_argument("--local-dir", default=None, help="use a pre-downloaded HF dir")
    common.add_argument("--perfix", action="store_true", help="capture Arm Performix profile")
    common.add_argument("--quality", action="store_true",
                        help="measure perplexity per quant (slower)")
    common.add_argument("--allow-non-arm", action="store_true",
                        help="run on a non-Arm host (dev/testing only)")

    r = sub.add_parser("run", parents=[common], help="benchmark one model")
    r.add_argument("model", help="HF repo id, e.g. meta-llama/Llama-3.2-3B")
    r.set_defaults(func=cmd_run)

    s = sub.add_parser("sweep", parents=[common], help="benchmark models from a config")
    s.add_argument("config", help="YAML config, e.g. configs/leaderboard.yaml")
    s.set_defaults(func=cmd_sweep)

    i = sub.add_parser("info", help="print detected Arm host info")
    i.set_defaults(func=cmd_info)

    l = sub.add_parser("leaderboard",
                       help="rebuild results/leaderboard.{md,html} from existing results")
    l.add_argument("--price-per-hour", type=float, default=0.0, dest="price_per_hour",
                   help="instance $/hr for the $/Mtok column (default 0 = free host)")
    l.set_defaults(func=cmd_leaderboard)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
