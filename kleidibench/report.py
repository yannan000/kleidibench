"""Emit the benchmark report: results.json + report.md + report.html.

The report is the deliverable. It shows, for one model:
  - a table of every (quant x KleidiAI on/off) config
  - the headline KleidiAI speedup on Q4_0 (prefill and decode)
  - simple inline-SVG bar charts (no external plotting dependency)

report.html is a standalone leaderboard you can screenshot for the demo video.
"""
from __future__ import annotations

from pathlib import Path
from typing import List

from . import util


# --------------------------------------------------------------------------- #
# Aggregation
# --------------------------------------------------------------------------- #

def kleidiai_speedup(results: List[dict], quant: str = "Q4_0") -> dict:
    """Compute speedups for a given quant at its best thread count.

    Two comparisons: KleidiAI-on vs llama.cpp's default Arm path (kleidiai-off),
    and — when a repack-off naive run exists — Arm-optimized-total vs naive,
    which shows the full journey from generic kernels to KleidiAI."""
    on = _best(results, quant, "kleidiai-on")
    off = _best(results, quant, "kleidiai-off")
    if not on or not off:
        return {}
    out = {
        "quant": quant,
        "prefill_on": on["prefill_tps"], "prefill_off": off["prefill_tps"],
        "decode_on": on["decode_tps"], "decode_off": off["decode_tps"],
        "prefill_speedup": _ratio(on["prefill_tps"], off["prefill_tps"]),
        "decode_speedup": _ratio(on["decode_tps"], off["decode_tps"]),
        "threads": on["threads"],
    }
    naive = _best(results, quant, "repack-off")
    if naive:
        out.update({
            "prefill_naive": naive["prefill_tps"],
            "decode_naive": naive["decode_tps"],
            "prefill_vs_naive": _ratio(on["prefill_tps"], naive["prefill_tps"]),
            "decode_vs_naive": _ratio(on["decode_tps"], naive["decode_tps"]),
        })
    return out


def _best(results, quant, build):
    rows = [r for r in results if r["quant"] == quant and r["build"] == build]
    return max(rows, key=lambda r: r["decode_tps"], default=None)


def _ratio(a, b):
    return round(a / b, 2) if b else 0.0


# --------------------------------------------------------------------------- #
# Writers
# --------------------------------------------------------------------------- #

def write_report(model: str, results: List[dict], host: dict, meta: dict) -> Path:
    out_dir = util.RESULTS / model
    out_dir.mkdir(parents=True, exist_ok=True)

    util.save_json(out_dir / "results.json",
                   {"model": model, "host": host, "meta": meta, "results": results})

    speedup = kleidiai_speedup(results, "Q4_0")
    (out_dir / "report.md").write_text(_markdown(model, results, host, meta, speedup))
    (out_dir / "report.html").write_text(_html(model, results, host, meta, speedup))
    util.log(f"report -> {out_dir/'report.md'} and report.html")
    return out_dir


def _markdown(model, results, host, meta, speedup) -> str:
    lines = [
        f"# KleidiBench report — {model}",
        "",
        f"- **Host:** {host.get('cpu_model')} · {host.get('cores')} cores · "
        f"{host.get('total_ram_gb')} GB · features: "
        f"{', '.join(host.get('features') or ['n/a'])}",
        f"- **llama.cpp:** {meta.get('llama_commit')}",
        f"- **Run:** {meta.get('timestamp')}",
        "",
    ]
    if speedup:
        lines += [
            "## Arm optimization gains (Q4_0)",
            "",
            f"- **KleidiAI vs llama.cpp default Arm path** — prefill "
            f"{speedup['prefill_off']} -> {speedup['prefill_on']} tok/s "
            f"(**{speedup['prefill_speedup']}x**), decode "
            f"{speedup['decode_off']} -> {speedup['decode_on']} tok/s "
            f"(**{speedup['decode_speedup']}x**)",
        ]
        if "decode_vs_naive" in speedup:
            lines += [
                f"- **KleidiAI vs naive (no Arm repack)** — prefill "
                f"{speedup['prefill_naive']} -> {speedup['prefill_on']} tok/s "
                f"(**{speedup['prefill_vs_naive']}x**), decode "
                f"{speedup['decode_naive']} -> {speedup['decode_on']} tok/s "
                f"(**{speedup['decode_vs_naive']}x**)",
            ]
        lines += [f"- Best at {speedup['threads']} threads.", ""]
    lines += [
        "## Full sweep",
        "",
        "| Quant | Build | Threads | Size (GB) | Prefill tok/s | Decode tok/s | "
        "TTFT (ms) | Peak RAM (GB) |",
        "|-------|-------|--------:|----------:|--------------:|-------------:|"
        "----------:|--------------:|",
    ]
    for r in sorted(results, key=lambda x: (x["quant"], x["build"], x["threads"])):
        ram = r["peak_ram_gb"] if r["peak_ram_gb"] is not None else "-"
        lines.append(
            f"| {r['quant']} | {r['build']} | {r['threads']} | {r['size_gb']} | "
            f"{r['prefill_tps']} | {r['decode_tps']} | {r['ttft_ms']} | {ram} |"
        )
    lines += ["", f"_TTFT is derived from prefill throughput at "
                  f"{results[0]['n_prompt'] if results else 512}-token prompts._", ""]
    return "\n".join(lines)


def _html(model, results, host, meta, speedup) -> str:
    decode_rows = [r for r in results if r["build"] == "kleidiai-on"] or results
    chart = _svg_bars(
        [(f"{r['quant']}", r["decode_tps"]) for r in
         sorted(decode_rows, key=lambda x: x["decode_tps"])],
        title="Decode tok/s (KleidiAI on)")
    speed_html = ""
    if speedup:
        naive_html = ""
        if "decode_vs_naive" in speedup:
            naive_html = (
                f"<p><b>vs naive (no Arm repack)</b>: prefill "
                f"<span class='up'>{speedup['prefill_vs_naive']}&times;</span>, "
                f"decode <span class='up'>{speedup['decode_vs_naive']}&times;</span></p>"
            )
        speed_html = (
            f"<div class='callout'><h2>Arm optimization gains (Q4_0)</h2>"
            f"<p><b>Prefill</b>: {speedup['prefill_off']} &rarr; "
            f"{speedup['prefill_on']} tok/s "
            f"(<span class='up'>{speedup['prefill_speedup']}&times;</span>)</p>"
            f"<p><b>Decode</b>: {speedup['decode_off']} &rarr; "
            f"{speedup['decode_on']} tok/s "
            f"(<span class='up'>{speedup['decode_speedup']}&times;</span>)</p>"
            f"{naive_html}</div>"
        )
    trows = "".join(
        f"<tr><td>{r['quant']}</td>"
        f"<td>{r['build']}</td>"
        f"<td>{r['threads']}</td><td>{r['size_gb']}</td>"
        f"<td>{r['prefill_tps']}</td><td>{r['decode_tps']}</td>"
        f"<td>{r['ttft_ms']}</td>"
        f"<td>{r['peak_ram_gb'] if r['peak_ram_gb'] is not None else '-'}</td></tr>"
        for r in sorted(results, key=lambda x: (x["quant"], x["build"], x["threads"]))
    )
    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>KleidiBench — {model}</title><style>
body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:860px;
margin:2rem auto;padding:0 1rem;color:#12203a}}
h1{{margin-bottom:.2rem}} .sub{{color:#5b6b86}}
table{{border-collapse:collapse;width:100%;margin-top:1rem}}
th,td{{border:1px solid #d7dEEA;padding:.4rem .6rem;text-align:right}}
th:first-child,td:first-child,th:nth-child(2),td:nth-child(2){{text-align:left}}
thead{{background:#0b7285;color:#fff}}
.callout{{background:#e7f5ff;border-left:4px solid #0b7285;padding:.6rem 1rem;
border-radius:6px;margin:1rem 0}}
.up{{color:#0b7285;font-weight:700}}
.bar{{fill:#0b7285}} .barlabel{{font-size:12px;fill:#12203a}}
</style></head><body>
<h1>KleidiBench &mdash; {model}</h1>
<p class="sub">{host.get('cpu_model')} &middot; {host.get('cores')} cores &middot;
{host.get('total_ram_gb')} GB &middot; llama.cpp {meta.get('llama_commit')} &middot;
{meta.get('timestamp')}</p>
{speed_html}
{chart}
<table><thead><tr><th>Quant</th><th>Build</th><th>Threads</th><th>Size GB</th>
<th>Prefill t/s</th><th>Decode t/s</th><th>TTFT ms</th><th>Peak RAM GB</th></tr></thead>
<tbody>{trows}</tbody></table>
<p class="sub">Generated by KleidiBench. Reproduce with
<code>kleidibench run &lt;model&gt;</code> on an Arm64 box.</p>
</body></html>"""


def _svg_bars(pairs, title="", width=760, bar_h=26, gap=10) -> str:
    if not pairs:
        return ""
    maxv = max(v for _, v in pairs) or 1
    label_w, val_w, pad = 120, 60, 8
    plot_w = width - label_w - val_w - pad * 2
    height = len(pairs) * (bar_h + gap) + 40
    parts = [f'<svg viewBox="0 0 {width} {height}" width="100%" '
             f'xmlns="http://www.w3.org/2000/svg" role="img">',
             f'<text x="0" y="20" class="barlabel" font-weight="700">{title}</text>']
    y = 34
    for name, val in pairs:
        w = int(plot_w * (val / maxv))
        parts.append(f'<text x="0" y="{y+bar_h*0.7:.0f}" class="barlabel">{name}</text>')
        parts.append(f'<rect x="{label_w}" y="{y}" width="{w}" height="{bar_h}" '
                     f'rx="3" class="bar"/>')
        parts.append(f'<text x="{label_w+w+pad}" y="{y+bar_h*0.7:.0f}" '
                     f'class="barlabel">{val}</text>')
        y += bar_h + gap
    parts.append("</svg>")
    return "".join(parts)
