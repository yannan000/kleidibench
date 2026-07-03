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

# Canonical build ordering + chart fills: naive baseline -> default Arm path ->
# KleidiAI, so every chart reads left-to-right as "less optimized -> more".
_BUILD_ORDER = ("repack-off", "kleidiai-off", "kleidiai-on")
_BUILD_FILLS = {
    "repack-off": "#94a3b8",    # gray — naive baseline
    "kleidiai-off": "#66b2c2",  # light teal — llama.cpp default Arm path
    "kleidiai-on": "#0b7285",   # dark teal — KleidiAI
}


def _thread_scaling(results: List[dict], quant: str = "Q4_0"):
    """Group decode tok/s by thread count for one quant.

    Returns (builds, groups) where groups is
    [(group_label, [(build, decode_tps), ...]), ...] with threads ascending and
    series in _BUILD_ORDER. Empty when there's nothing to scale (no rows for the
    quant, or a single thread count — a one-cluster chart says nothing)."""
    rows = [r for r in results if r["quant"] == quant]
    threads = sorted({r["threads"] for r in rows})
    if len(threads) < 2:
        return [], []
    builds = [b for b in _BUILD_ORDER if any(r["build"] == b for r in rows)]
    groups = []
    for t in threads:
        series = []
        for b in builds:
            match = [r for r in rows if r["threads"] == t and r["build"] == b]
            if match:
                series.append((b, match[0]["decode_tps"]))
        groups.append((f"{t} thr", series))
    return builds, groups

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

    # Callouts for both quants where Arm gains live: Q4_0 (repack story) and
    # Q8_0 (KleidiAI's direct i8mm win — the default path doesn't repack Q8_0).
    speedups = {q: s for q in ("Q4_0", "Q8_0")
                if (s := kleidiai_speedup(results, q))}
    (out_dir / "report.md").write_text(_markdown(model, results, host, meta, speedups))
    (out_dir / "report.html").write_text(_html(model, results, host, meta, speedups))
    util.log(f"report -> {out_dir/'report.md'} and report.html")
    return out_dir


def _speedup_md_lines(quant: str, speedup: dict) -> list:
    lines = [
        f"## Arm optimization gains ({quant})",
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
    return lines


def _markdown(model, results, host, meta, speedups) -> str:
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
    for quant, speedup in speedups.items():
        lines += _speedup_md_lines(quant, speedup)
    has_ppl = any(r.get("ppl") is not None for r in results)
    ppl_h = " Perplexity |" if has_ppl else ""
    ppl_a = "----------:|" if has_ppl else ""
    lines += [
        "## Full sweep",
        "",
        "| Quant | Build | Threads | Size (GB) | Prefill tok/s | Decode tok/s | "
        f"TTFT (ms) | Peak RAM (GB) |{ppl_h}",
        "|-------|-------|--------:|----------:|--------------:|-------------:|"
        f"----------:|--------------:|{ppl_a}",
    ]
    for r in sorted(results, key=lambda x: (x["quant"], x["build"], x["threads"])):
        ram = r["peak_ram_gb"] if r["peak_ram_gb"] is not None else "-"
        ppl_c = ""
        if has_ppl:
            ppl_c = f" {r['ppl'] if r.get('ppl') is not None else '-'} |"
        lines.append(
            f"| {r['quant']} | {r['build']} | {r['threads']} | {r['size_gb']} | "
            f"{r['prefill_tps']} | {r['decode_tps']} | {r['ttft_ms']} | {ram} |{ppl_c}"
        )
    lines += ["", f"_TTFT is derived from prefill throughput at "
                  f"{results[0]['n_prompt'] if results else 512}-token prompts._", ""]
    builds, groups = _thread_scaling(results, "Q4_0")
    if groups:
        lines += [
            "## Thread scaling (Q4_0 decode tok/s)",
            "",
            "| Threads | " + " | ".join(builds) + " |",
            "|--------:|" + "".join("---:|" for _ in builds),
        ]
        for glabel, series in groups:
            vals = dict(series)
            cells = " | ".join(str(vals.get(b, "-")) for b in builds)
            lines.append(f"| {glabel.split()[0]} | {cells} |")
        lines.append("")
    return "\n".join(lines)


def _html(model, results, host, meta, speedups) -> str:
    decode_rows = [r for r in results if r["build"] == "kleidiai-on"] or results
    chart = _svg_bars(
        [(f"{r['quant']}", r["decode_tps"]) for r in
         sorted(decode_rows, key=lambda x: x["decode_tps"])],
        title="Decode tok/s (KleidiAI on)")
    _, scaling_groups = _thread_scaling(results, "Q4_0")
    scaling_chart = _svg_grouped_bars(
        scaling_groups, title="Thread scaling — decode tok/s (Q4_0)")
    speed_html = ""
    speed_html = ""
    for quant, speedup in speedups.items():
        naive_html = ""
        if "decode_vs_naive" in speedup:
            naive_html = (
                f"<p><b>vs naive (no Arm repack)</b>: prefill "
                f"<span class='up'>{speedup['prefill_vs_naive']}&times;</span>, "
                f"decode <span class='up'>{speedup['decode_vs_naive']}&times;</span></p>"
            )
        speed_html += (
            f"<div class='callout'><h2>Arm optimization gains ({quant})</h2>"
            f"<p><b>Prefill</b>: {speedup['prefill_off']} &rarr; "
            f"{speedup['prefill_on']} tok/s "
            f"(<span class='up'>{speedup['prefill_speedup']}&times;</span>)</p>"
            f"<p><b>Decode</b>: {speedup['decode_off']} &rarr; "
            f"{speedup['decode_on']} tok/s "
            f"(<span class='up'>{speedup['decode_speedup']}&times;</span>)</p>"
            f"{naive_html}</div>"
        )
    has_ppl = any(r.get("ppl") is not None for r in results)
    ppl_th = "<th>Perplexity</th>" if has_ppl else ""
    trows = "".join(
        f"<tr><td>{r['quant']}</td>"
        f"<td>{r['build']}</td>"
        f"<td>{r['threads']}</td><td>{r['size_gb']}</td>"
        f"<td>{r['prefill_tps']}</td><td>{r['decode_tps']}</td>"
        f"<td>{r['ttft_ms']}</td>"
        f"<td>{r['peak_ram_gb'] if r['peak_ram_gb'] is not None else '-'}</td>"
        + (f"<td>{r['ppl'] if r.get('ppl') is not None else '-'}</td>" if has_ppl else "")
        + "</tr>"
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
{scaling_chart}
<table><thead><tr><th>Quant</th><th>Build</th><th>Threads</th><th>Size GB</th>
<th>Prefill t/s</th><th>Decode t/s</th><th>TTFT ms</th><th>Peak RAM GB</th>{ppl_th}</tr></thead>
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


def _svg_grouped_bars(groups, title="", width=760, plot_h=190, fills=None) -> str:
    """Grouped vertical bars, pure inline SVG (no JS), same spirit as _svg_bars.

    groups: [(group_label, [(series_label, value), ...]), ...] — one cluster per
    group, one bar per series. A legend row sits above the plot; each bar gets a
    value label on top and each cluster a label beneath the baseline."""
    groups = [(g, s) for g, s in groups if s]
    if not groups:
        return ""
    fills = fills or _BUILD_FILLS
    series_labels: list = []
    for _, series in groups:
        for name, _ in series:
            if name not in series_labels:
                series_labels.append(name)
    maxv = max(v for _, series in groups for _, v in series) or 1
    pad = 8
    title_h, legend_h = 28, 24
    base = title_h + legend_h + plot_h          # y of the baseline
    height = base + 26                          # room for group labels
    plot_w = width - pad * 2
    group_w = plot_w / len(groups)
    parts = [f'<svg viewBox="0 0 {width} {height}" width="100%" '
             f'xmlns="http://www.w3.org/2000/svg" role="img">',
             f'<text x="0" y="20" class="barlabel" font-weight="700">{title}</text>']
    # legend row
    lx = pad
    for name in series_labels:
        fill = fills.get(name, "#0b7285")
        parts.append(f'<rect x="{lx}" y="{title_h + 4}" width="12" height="12" '
                     f'rx="2" fill="{fill}"/>')
        parts.append(f'<text x="{lx + 17}" y="{title_h + 14}" '
                     f'class="barlabel">{name}</text>')
        lx += 17 + 7 * len(name) + 22
    # clusters
    bar_gap = 4
    for gi, (glabel, series) in enumerate(groups):
        n = len(series)
        bar_w = min(48, (group_w - 24 - bar_gap * (n - 1)) / n)
        cluster_w = bar_w * n + bar_gap * (n - 1)
        x0 = pad + gi * group_w + (group_w - cluster_w) / 2
        for si, (name, val) in enumerate(series):
            # leave 16px headroom above the tallest bar for its value label
            h = (plot_h - 16) * (val / maxv)
            x = x0 + si * (bar_w + bar_gap)
            parts.append(f'<rect x="{x:.1f}" y="{base - h:.1f}" '
                         f'width="{bar_w:.1f}" height="{h:.1f}" rx="3" '
                         f'fill="{fills.get(name, "#0b7285")}"/>')
            parts.append(f'<text x="{x + bar_w / 2:.1f}" y="{base - h - 4:.1f}" '
                         f'text-anchor="middle" class="barlabel">{val}</text>')
        parts.append(f'<text x="{pad + gi * group_w + group_w / 2:.1f}" '
                     f'y="{base + 18}" text-anchor="middle" '
                     f'class="barlabel">{glabel}</text>')
    parts.append(f'<line x1="{pad}" y1="{base}" x2="{width - pad}" y2="{base}" '
                 f'stroke="#d7deea"/>')
    parts.append("</svg>")
    return "".join(parts)
