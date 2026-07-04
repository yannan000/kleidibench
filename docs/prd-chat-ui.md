# PRD — KleidiBench demo chat UI (v2 redesign)

**Deliverable:** a redesigned `demo/chat.html` — one self-contained HTML file.
**Owner:** Yoofi Annan · **Repo:** github.com/yannan000/kleidibench (MIT)
**Deadline context:** Arm AI Optimization Challenge 2026, submission video due Aug 14.

---

## 1. What this is

KleidiBench benchmarks LLM inference on Arm CPUs. Its demo runs llama.cpp's
OpenAI-compatible server on a free Arm64 machine; `chat.html` is the visual
front end used in a **<3-minute judged demo video**. The page's job is to make
one claim land on camera: *"a real LLM is streaming from a $0 Arm CPU, and
here are the live performance numbers."*

A working v1 exists at `demo/chat.html` (functional, plain). This PRD is for a
v2 that looks like a product, not a test harness.

## 2. Hard constraints (non-negotiable)

1. **One file, fully self-contained.** Inline CSS + one inline `<script>`. No
   CDNs, fonts, images, fetch/XHR to any host except the user-configured API
   base URL. Must work opened from `file://`, a local static server, and
   GitHub Pages (it is deployed at
   `https://yannan000.github.io/kleidibench/demo/chat.html`).
2. **No frameworks, no build step.** Vanilla JS. The repo has zero Node
   tooling and must stay that way.
3. **Protocol parity with v1** (verified against a real llama-server):
   - POST `{baseUrl}/chat/completions`, body
     `{model:"local", stream:true, messages:[full conversation]}`
   - Optional `Authorization: Bearer <key>`; if the key field is empty, omit
     the header entirely
   - SSE parsing: buffer on newlines across reads; `data:` lines; ignore
     chunks whose `choices[0].delta.content` is null/absent; stop on `[DONE]`
   - On request failure: render an inline error message AND pop the failed
     user message from the API history so a retry doesn't double-send
4. **Metrics must be measured the same way** as `demo/demo_client.py` so
   terminal and browser agree on camera: TTFT = first content delta − request
   start; tokens = number of content deltas; tok/s = (n−1)/(last−first delta).
5. **Accessibility/recording floor:** legible at 720p in a half-screen
   window; visible focus states; respects `prefers-color-scheme` (both modes
   must look intentional); respects `prefers-reduced-motion`.

## 3. Brand / voice

- Product: **KleidiBench** — subtitle used today: *"LLM on a free Arm64 CPU"*.
- Accent color `#0b7285` (teal) — used across all report artifacts; keep it as
  the anchor, extend the palette as needed (current pairing: `#66b2c2` light
  teal, `#94a3b8` gray on charts).
- Tone: engineering-honest. No fake sparkle, no "AI magic" tropes. The
  numbers ARE the design story.

## 4. Users & the one scenario that matters

Primary: the founder recording the demo video (screen-recorded browser,
~1280×720 or larger, possibly zoomed). Secondary: judges/devs who fork the
repo and open the page themselves.

**Hero scenario (design for exactly this):** page opens → looks credible at
first glance → user types a prompt → tokens visibly stream → when generation
ends, the **TTFT / tok/s / token-count stat line** is the most eye-catching
element on screen → user sends a second prompt and the header badge updates,
showing the machine is consistently fast.

## 5. Functional requirements

| # | Requirement |
|---|-------------|
| F1 | Message list: user right / assistant left, streaming text appears live with a subtle cursor while generating |
| F2 | Per-response stat line: `TTFT 312 ms · 68.0 tok/s · 142 tokens` — style this as the hero element (chip/pill treatment, animate its arrival unless reduced-motion) |
| F3 | Header perf badge: last TTFT + tok/s, dimmed placeholder before first response |
| F4 | Settings: Base URL (default `http://127.0.0.1:8080/v1`) and API key (default `demo-key`) — visible but visually secondary; consider a collapsible row so the recording stays clean |
| F5 | Input: textarea, Enter sends / Shift+Enter newline, auto-grow (cap ~5 lines), Send disabled while streaming |
| F6 | Empty state: short hint that names llama.cpp + KleidiAI + Arm so the video's opening frame carries the message |
| F7 | Error state: inline system bubble ("Can't reach the server — is llama-server running? See server.md"), never console-only |
| F8 | A "Stop" affordance while streaming (abort the fetch) — v1 lacks this and it's the riskiest live-demo moment |
| F9 | Optional, nice-to-have: a tiny footer line "Served by llama.cpp + KleidiAI on Arm · github.com/yannan000/kleidibench" |

## 6. Design direction (open to interpretation)

- Feels like a **performance instrument**, not a chatbot toy: think dashboard
  restraint — generous whitespace, strong numeric typography (tabular
  numerals), one accent color doing real work.
- The stat line/badge treatment is where design effort pays off most.
  Consider: count-up animation on tok/s, a subtle bar/spark under the badge —
  but only if it stays honest and calm (reduced-motion fallback required).
- Dark mode is likely what gets recorded — design dark-first, verify light.
- Avoid: gradients-everywhere, glassmorphism clichés, emoji as UI, anything
  that reads "template".

## 7. Non-goals

- No conversation persistence, markdown rendering, code highlighting, model
  picker, multi-session, mobile-first work (desktop recording is the target;
  don't actively break mobile, don't invest in it).
- No changes to the API server, demo_client.py, or any other repo file.

## 8. Acceptance checklist

- [ ] Single file replaces `demo/chat.html`; no external requests (grep for
      `http` finds only the default base-URL value and comments)
- [ ] Parses well-formed (python `html.parser` clean); one `<script>`
- [ ] Works against a real llama-server: streams, stats match demo_client.py
      within rounding, empty-key omits auth header, error + retry path clean
- [ ] Both color schemes screenshot-worthy at 720p; focus states visible;
      reduced-motion honored
- [ ] Stop button aborts mid-stream without corrupting conversation state
- [ ] Reads as "credible product" in the first second of a cold viewing

## 9. Reference materials in the repo

- Current implementation: `demo/chat.html` (v1 — keep its protocol logic as
  the spec-in-code)
- Server + CORS verification notes: `demo/server.md`
- Visual language of the report artifacts: `results/leaderboard.html`,
  `kleidibench/report.py` (the `_html` writer)
- Metrics reference client: `demo/demo_client.py`
