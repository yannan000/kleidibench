# Demo video script — under 3 minutes

Judges aren't required to watch past 3:00, so the KleidiAI speedup number must
land **in the first 30 seconds**. Screen-record the terminal + browser
(QuickTime on macOS records both), no music (copyright rule), voiceover or
on-screen captions.

## Shot list

### 0:00–0:20 — The hook (report.html, already open)
Show `results/Qwen2.5-3B-Instruct/report.html` full screen. Cursor circles the
Q8_0 speedup callout.

> "Same model, same machine, same llama.cpp commit. The only difference is one
> CMake flag — Arm's KleidiAI kernels — and prompt processing jumps from 62 to
> 108 tokens a second. 1.7 times faster. This video shows the tool that
> measures it, a finding most benchmarks miss, and the free Arm hardware it
> all runs on."

### 0:20–0:50 — One command (terminal)
Type (don't paste) the command; time-lapse or jump-cut the run.

```
kleidibench run Qwen/Qwen2.5-0.5B-Instruct
```

> "KleidiBench builds llama.cpp three ways — a naive build, llama.cpp's
> default Arm path, and KleidiAI — quantizes any Hugging Face model down the
> F16 → Q8 → Q4 curve, benchmarks every combination, and writes the report you
> just saw. The three-way build is the point: it caught that at Q4, llama.cpp's
> default already matches KleidiAI — the real flag win lives at Q8."

### 0:50–1:30 — The free Arm part (browser: GitHub Actions tab)
Show the Actions run list, click into an arm64 job, point at `uname -m` →
`aarch64` in the log.

> "Here's the part I love: there is no server. This is a free GitHub Actions
> arm64 runner — real Neoverse cores, free for any public repo. Every push
> re-runs the benchmark; the results are committed back to the repo. Fork it,
> push, and CI hands you Arm numbers for your own model."

### 1:30–2:20 — Live inference (terminal via tmate, split pane)
Left pane: `llama-server` running (KleidiAI-on Q4_0 build). Right pane:

```
python3 demo/demo_client.py --stream "Explain what KleidiAI does in two sentences."
```

Let the tokens stream on camera; the client prints TTFT + tok/s at the end —
zoom on that line.

> "And it's not just a benchmark — this is llama.cpp's OpenAI-compatible
> server running the KleidiAI Q8_0 build — the config that won the leaderboard
> — live, on that same free Arm runner. Twenty-three tokens a second from a
> 3B model on a 4-core CPU, at zero dollars." *(Or use the 0.5B for a snappier
> on-camera feel: 132 tok/s.)*

### 2:20–2:50 — The leaderboard + close (browser: leaderboard.html)
Show the multi-model leaderboard, scroll the table.

> "Multiple models, one ranked leaderboard: decode speed, KleidiAI gain,
> cost per million tokens. Everything is MIT-licensed and reproducible with
> one command. KleidiBench: prove your LLM runs faster on Arm."

End card (2:50–3:00): repo URL `github.com/yannan000/kleidibench` + "Arm
Create: AI Optimization Challenge 2026 — Track 2: Cloud AI".

## Recording checklist

- [ ] Terminal font ≥ 16pt, dark theme, window ≥ 1280×720
- [ ] Hide personal info (menu bar, other tabs, notifications OFF)
- [ ] No copyrighted music; system sounds off
- [ ] Rehearse the tmate session first — start `demo-session` with
      `timeout_minutes: 60` so it doesn't die mid-take
- [ ] Upload to YouTube as **Public** (not unlisted-only per rules: "publicly
      visible"), title "KleidiBench — Arm AI Optimization Challenge 2026"
- [ ] Paste the link into docs/SUBMISSION.md and the Devpost form
