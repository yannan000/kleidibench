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
    """Compute speedups for a given quant, like-for-like: all builds compared
    at the SAME thread count (the max shared by on and off rows). Picking each
    build's own best threads independently could inflate the ratio if one
    scales worse under contention.

    Two comparisons: KleidiAI-on vs llama.cpp's default Arm path (kleidiai-off),
    and — when a repack-off naive run exists at that thread count —
    Arm-optimized-total vs naive, the full journey from generic kernels."""
    t = _max_shared_threads(results, quant, "kleidiai-on", "kleidiai-off")
    if t is None:
        return {}
    on = _at(results, quant, "kleidiai-on", t)
    off = _at(results, quant, "kleidiai-off", t)
    out = {
        "quant": quant,
        "prefill_on": on["prefill_tps"], "prefill_off": off["prefill_tps"],
        "decode_on": on["decode_tps"], "decode_off": off["decode_tps"],
        "prefill_speedup": _ratio(on["prefill_tps"], off["prefill_tps"]),
        "decode_speedup": _ratio(on["decode_tps"], off["decode_tps"]),
        "threads": t,
    }
    naive = _at(results, quant, "repack-off", t)
    if naive:
        out.update({
            "prefill_naive": naive["prefill_tps"],
            "decode_naive": naive["decode_tps"],
            "prefill_vs_naive": _ratio(on["prefill_tps"], naive["prefill_tps"]),
            "decode_vs_naive": _ratio(on["decode_tps"], naive["decode_tps"]),
        })
    return out


def _max_shared_threads(results, quant, *builds):
    """Highest thread count at which every named build has a row for quant."""
    sets = [{r["threads"] for r in results
             if r["quant"] == quant and r["build"] == b} for b in builds]
    shared = set.intersection(*sets) if sets else set()
    return max(shared) if shared else None


def _at(results, quant, build, threads):
    for r in results:
        if r["quant"] == quant and r["build"] == build and r["threads"] == threads:
            return r
    return None


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
        ttft = r["ttft_ms"] if r.get("ttft_ms") is not None else "-"
        ppl_c = ""
        if has_ppl:
            ppl_c = f" {r['ppl'] if r.get('ppl') is not None else '-'} |"
        lines.append(
            f"| {r['quant']} | {r['build']} | {r['threads']} | {r['size_gb']} | "
            f"{r['prefill_tps']} | {r['decode_tps']} | {ttft} | {ram} |{ppl_c}"
        )
    lines += ["", f"_TTFT is derived from prefill throughput at "
                  f"{results[0]['n_prompt'] if results else 512}-token prompts. "
                  f"Peak RAM is whole-process peak RSS (model load + all reps)._", ""]
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
    # One bar per quant: KleidiAI-on rows at the max thread count only —
    # plotting every thread count repeats identical quant labels.
    decode_rows = [r for r in results if r["build"] == "kleidiai-on"] or results
    max_t = max((r["threads"] for r in decode_rows), default=0)
    decode_rows = [r for r in decode_rows if r["threads"] == max_t]
    chart = _svg_bars(
        [(f"{r['quant']}", r["decode_tps"]) for r in
         sorted(decode_rows, key=lambda x: x["decode_tps"])],
        title=f"Decode tok/s (KleidiAI on, {max_t} threads)")
    _, scaling_groups = _thread_scaling(results, "Q4_0")
    scaling_chart = _svg_grouped_bars(
        scaling_groups, title="Thread scaling — decode tok/s (Q4_0)")
    speed_html = ""
    for quant, speedup in speedups.items():
        bignums = ""
        if "decode_vs_naive" in speedup:
            bignums = (
                f"<div class='bignums'>"
                f"<div class='bignum'><div class='lab'>vs naive (no Arm repack)</div>"
                f"<div class='val'>{speedup['prefill_vs_naive']}&times;"
                f"<small>Prefill</small></div></div>"
                f"<div class='bignum'><div class='lab'>vs naive (no Arm repack)</div>"
                f"<div class='val'>{speedup['decode_vs_naive']}&times;"
                f"<small>Decode</small></div></div></div>"
            )
        speed_html += (
            f"<div class='card'><h2>{quant} quantization</h2>{bignums}"
            f"<div class='krow'><span>Prefill (tok/s)</span>"
            f"<span>{speedup['prefill_off']} &rarr; <b>{speedup['prefill_on']}</b> "
            f"<span class='up'>({speedup['prefill_speedup']}&times;)</span></span></div>"
            f"<div class='krow'><span>Decode (tok/s)</span>"
            f"<span>{speedup['decode_off']} &rarr; <b>{speedup['decode_on']}</b> "
            f"<span class='up'>({speedup['decode_speedup']}&times;)</span></span></div>"
            f"<div class='krow'><span>KleidiAI vs llama.cpp default</span>"
            f"<span>@ {speedup['threads']} threads</span></div></div>"
        )
    has_ppl = any(r.get("ppl") is not None for r in results)
    ppl_th = "<th>Perplexity</th>" if has_ppl else ""
    trows = "".join(
        f"<tr{' class=' + chr(34) + 'hl' + chr(34) if r['build'] == 'kleidiai-on' else ''}>"
        f"<td>{r['quant']}</td>"
        f"<td>{r['build']}</td>"
        f"<td>{r['threads']}</td><td>{r['size_gb']}</td>"
        f"<td>{r['prefill_tps']}</td><td>{r['decode_tps']}</td>"
        f"<td>{r['ttft_ms'] if r.get('ttft_ms') is not None else '-'}</td>"
        f"<td>{r['peak_ram_gb'] if r['peak_ram_gb'] is not None else '-'}</td>"
        + (f"<td>{r['ppl'] if r.get('ppl') is not None else '-'}</td>" if has_ppl else "")
        + "</tr>"
        for r in sorted(results, key=lambda x: (x["quant"], x["build"], x["threads"]))
    )
    chips = "".join(f"<span class='hchip'>{c}</span>" for c in (
        host.get("cpu_model"), f"{host.get('cores')} cores",
        f"{host.get('total_ram_gb')} GB", f"llama.cpp {meta.get('llama_commit')}"))
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>KleidiBench — {model}</title><style>{PAGE_CSS}</style></head><body>
<header><span class="brand">KleidiBench</span><span class="mtitle">{model}</span>
<span class="chips">{chips}</span><span class="stamp">{meta.get('timestamp')}</span></header>
<main>
<h1>Arm optimization gains</h1>
<p class="lede">Performance impact of Arm repack and KleidiAI kernels across
quantization levels. Reproduce with <code>kleidibench run &lt;model&gt;</code>.</p>
<div class="cards">{speed_html}</div>
<section class="panel">{chart}</section>
<section class="panel">{scaling_chart}</section>
<section class="panel"><table><thead><tr><th>Quant</th><th>Build</th><th>Threads</th>
<th>Size GB</th><th>Prefill t/s</th><th>Decode t/s</th><th>TTFT ms</th>
<th>Peak RAM GB</th>{ppl_th}</tr></thead>
<tbody>{trows}</tbody></table></section>
<p class="foot">Generated by <code>kleidibench</code> · benchmarked on a free
GitHub Actions arm64 runner · github.com/yannan000/kleidibench</p>
</main></body></html>"""


# "KleidiBench Visual System" — dark instrument theme (designed with Google
# Stitch, hand-ported; zero external resources). Shared by report + leaderboard.
PAGE_CSS = """
:root{--bg:#0a0c10;--surface:#111318;--panel:#14171c;--elev:#1e2024;
--outline:#2b3139;--text:#e2e2e8;--dim:#bec8cc;--muted:#889296;
--primary:#82d2e7;--primary-c:#0b7285;
--sans:"Geist",-apple-system,"Segoe UI",Roboto,sans-serif;
--mono:"JetBrains Mono",ui-monospace,"SF Mono",Menlo,Consolas,monospace}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);
font:400 15px/1.6 var(--sans);font-variant-numeric:tabular-nums}
header{display:flex;align-items:center;gap:14px;flex-wrap:wrap;
padding:14px 28px;background:var(--surface);border-bottom:1px solid var(--outline)}
.brand{font:700 18px/1 var(--mono);color:var(--primary);letter-spacing:-.02em}
.mtitle{font:600 15px/1 var(--sans);color:var(--text)}
.chips{display:flex;gap:8px;flex-wrap:wrap}
.hchip{font:400 12px/1 var(--mono);color:var(--dim);background:var(--elev);
border:1px solid var(--outline);border-radius:6px;padding:6px 10px;white-space:nowrap}
.stamp{margin-left:auto;font:400 12px/1 var(--mono);color:var(--muted)}
main{max-width:980px;margin:0 auto;padding:28px 28px 40px}
h1{font:600 28px/1.2 var(--sans);letter-spacing:-.02em;margin:.2em 0 .2em}
.lede{color:var(--muted);margin-top:0}
code{font:400 13px/1 var(--mono);color:var(--primary)}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));
gap:16px;margin:20px 0}
.card{background:var(--panel);border:1px solid var(--outline);
border-left:3px solid var(--primary-c);border-radius:10px;padding:18px 20px}
.card h2{font:600 11px/1 var(--mono);letter-spacing:.08em;text-transform:uppercase;
color:var(--muted);margin:0 0 14px}
.bignums{display:flex;gap:12px;margin-bottom:14px}
.bignum{flex:1;background:var(--elev);border-radius:8px;padding:12px 14px}
.bignum .lab{font:600 10px/1.3 var(--mono);letter-spacing:.06em;
text-transform:uppercase;color:var(--muted)}
.bignum .val{font:600 26px/1.2 var(--mono);color:var(--text)}
.bignum .val small{font-size:13px;color:var(--primary);margin-left:4px}
.krow{display:flex;justify-content:space-between;font:400 13px/1.9 var(--mono);
color:var(--muted)}
.krow b{color:var(--text);font-weight:600}
.krow .up{color:var(--primary);font-weight:600}
.panel{background:var(--panel);border:1px solid var(--outline);border-radius:10px;
padding:18px 20px;margin:16px 0;overflow-x:auto}
table{border-collapse:collapse;width:100%;font:400 13px/1.5 var(--mono)}
th{font:600 10px/1.3 var(--mono);letter-spacing:.08em;text-transform:uppercase;
color:var(--muted);text-align:right;padding:8px 10px;
border-bottom:1px solid var(--outline)}
td{color:var(--dim);text-align:right;padding:8px 10px;
border-bottom:1px solid rgba(43,49,57,.5)}
th:nth-child(-n+2),td:nth-child(-n+2){text-align:left}
tr:last-child td{border-bottom:none}
td:nth-child(2){color:var(--muted)}
tr.hl td{color:var(--text)} tr.hl td:nth-child(2){color:var(--primary)}
.foot{font:400 12px/1.6 var(--mono);color:var(--muted);margin-top:24px}
.bar{fill:#0b7285}.barlabel{font:400 12px var(--mono);fill:#bec8cc}
@media (prefers-color-scheme: light){
:root{--bg:#f4f6f8;--surface:#ffffff;--panel:#ffffff;--elev:#eef1f4;
--outline:#d5dde2;--text:#12203a;--dim:#3f4d63;--muted:#5b6b86;--primary:#0b7285}
.barlabel{fill:#3f4d63}}
"""


def _svg_bars(pairs, title="", width=760, bar_h=26, gap=10) -> str:
    if not pairs:
        return ""
    maxv = max(v for _, v in pairs) or 1
    # Label column sized to the longest name (~7.5px/char at 12px mono) so
    # long model names never run under the bars.
    label_w = max(120, min(320, int(max(len(n) for n, _ in pairs) * 7.5) + 12))
    val_w, pad = 60, 8
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
