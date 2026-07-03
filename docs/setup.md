# Setup guide

KleidiBench is developed on any machine but **benchmarked on real Arm64 CPU**.
The primary path uses **GitHub's free arm64-hosted runners** — zero signup
beyond the GitHub account you already need to submit this repo, zero cost, zero
capacity/verification friction. An Oracle Ampere A1 (or any Arm64 Linux host —
Graviton, Axion, a Raspberry Pi) works identically if you'd rather have a
persistent box; see [the Oracle appendix](#appendix-persistent-arm-box-oracle-ampere-a1)
below.

## Primary path: GitHub Actions arm64 runners

Public repos get free, GA, standard 4-vCPU `ubuntu-24.04-arm` / `ubuntu-22.04-arm`
runners — real Arm64, no emulation. Three workflows are already wired up in
[`.github/workflows/`](../.github/workflows/):

| Workflow | Trigger | What it does |
|----------|---------|---------------|
| `benchmark.yml` → `smoke-test` | every push/PR | tiny ungated model, proves build → convert → quantize → bench → report works on Arm. No secrets needed. |
| `benchmark.yml` → `full-benchmark` | manual (`workflow_dispatch`) | runs the real sweep (`configs/quick.yaml` or `leaderboard.yaml`) and commits `results/` back to the repo |
| `demo-session.yml` | manual | opens a private SSH session (via `tmate`, access limited to you) on an arm64 runner so you can drive `llama-server` live and screen-record it for the submission video |

### 1. Push this repo to GitHub (public, for the license to be detectable)

```bash
gh repo create kleidibench --public --source=. --remote=origin --push
```

### 2. Watch the smoke test run automatically

Every push triggers `smoke-test` — check the **Actions** tab. Green run = the
whole pipeline works on Arm64.

### 3. (Optional) Add HF_TOKEN for gated models

Llama models are gated on Hugging Face. In **Settings → Secrets and variables →
Actions**, add a secret `HF_TOKEN` with a Hugging Face read token (accept the
model license on huggingface.co first). Ungated alternatives that need no
token: `Qwen/Qwen2.5-3B`, `Qwen/Qwen2.5-1.5B`, `Qwen/Qwen2.5-0.5B-Instruct`.

### 4. Run the real benchmark sweep

**Actions tab → benchmark → Run workflow**, set `config` to
`configs/quick.yaml` (one model) or `configs/leaderboard.yaml` (multi-model),
leave `commit_results: true`. When it finishes, `results/<model>/report.md`
and `report.html` are committed straight into the repo.

### 5. Record the live demo

**Actions tab → demo-session → Run workflow.** The job log prints a one-time
`ssh <session>@nyc1.tmate.io` command — only you (the triggering GitHub user)
can connect. Once in:

```bash
kleidibench run <model>              # if not already built from step 4
# start llama-server per demo/server.md, then, in another terminal on the
# same runner (open a second tmate pane, or ssh again):
python3 demo/demo_client.py --stream "Explain what KleidiAI does."
```

Screen-record your local terminal while connected — that's your <3-min demo
footage of the project "functioning on the device for which it was built" (a
real Arm64 CPU), satisfying the submission requirement without hosting
anything 24/7.

## Local dev loop (no Arm needed)

Everything except the actual `llama-bench` numbers can be developed and unit
tested on any machine, including this project's Intel x86 Mac:

```bash
python3 -m pip install -e .
kleidibench info          # host detection; correctly reports non-Arm here
python3 -m py_compile kleidibench/*.py
```

## Troubleshooting

- **OOM on a 3B+ model** — GitHub arm64 runners have limited RAM; stick to
  1–3B models, or use `configs/ci-smoke.yaml`'s 0.5B model for quick checks.
- **`llama-bench` not found** — the build target failed; check the workflow's
  cmake step log.
- **Gated model 401** — set the `HF_TOKEN` repo secret and accept the model's
  license on huggingface.co.
- **tmate session times out** — re-run `demo-session` with a larger
  `timeout_minutes` input.

---

## Appendix: persistent Arm box (Oracle Ampere A1)

Only needed if you want an always-on Arm server beyond CI (e.g. to keep a demo
endpoint reachable outside of a recording session).

1. Sign up at cloud.oracle.com (Always-Free tier).
2. Create a **VM.Standard.A1.Flex** instance, **Ubuntu 24.04 (aarch64)**.
   Free tier is **2 OCPU / 12 GB** for new tenancies as of June 2026 — fine for
   1–3B models.
3. Upload your SSH key; open ingress for TCP 8080 if hosting the demo endpoint.
4. `ssh ubuntu@<ip>`, then `bash scripts/oracle_setup.sh`.
5. `source ~/kb-venv/bin/activate && kleidibench info` — expect `asimddp`
   (dotprod) in `features`; Oracle's Altra does **not** have `i8mm`/`sve`
   (that's Graviton3/4-only), so KleidiAI's win here is the dotprod path.

Known friction: identity verification can reject signups, and A1 capacity in
popular regions sometimes needs a few retries. If it's fighting you, use the
GitHub Actions path above instead — it satisfies every submission requirement.
