# Live demo: an OpenAI-compatible LLM endpoint on Arm

The WOW moment: a production-usable, streaming LLM API accelerated by
KleidiAI, running on a **free Arm64 CPU** — a GitHub Actions `ubuntu-24.04-arm`
runner, no cloud signup, no cost. This is `llama.cpp`'s built-in
OpenAI-compatible server — the same binary KleidiBench benchmarks.

## 1. Get a shell on the Arm runner

Trigger [`.github/workflows/demo-session.yml`](../.github/workflows/demo-session.yml)
(**Actions tab → demo-session → Run workflow**). The job log prints a one-time
`ssh <session>@nyc1.tmate.io` command, restricted to the triggering GitHub user.
Connect from your terminal — you're now on the Arm runner itself.

*(Running on your own persistent Arm box instead — see the
[Oracle appendix](../docs/setup.md#appendix-persistent-arm-box-oracle-ampere-a1)?
Same steps below, just swap `localhost` for the box's public IP and open the
firewall for port 8080.)*

## 2. Start the server

If you haven't already run `kleidibench run <model>` in this session, do that
first so the KleidiAI-on binary and GGUF exist. Then:

```bash
# paths follow the KleidiBench cache layout (~/.kleidibench)
~/.kleidibench/build-kleidiai-on/bin/llama-server \
  -m ~/.kleidibench/models/<model>-Q4_0.gguf \
  --host 127.0.0.1 --port 8080 \
  -t $(nproc) -c 4096 \
  --api-key demo-key            # optional; matches demo_client.py
```

## 3. Call it

Open a second pane in the same tmate session (or `ssh` again) and call the
endpoint from the runner itself — this is the footage for the video:

```bash
python3 demo/demo_client.py --base-url http://127.0.0.1:8080/v1 --stream \
  "Explain what KleidiAI does in two sentences."
```

The endpoint is OpenAI-compatible, so existing SDKs work unchanged:

```python
from openai import OpenAI
client = OpenAI(base_url="http://127.0.0.1:8080/v1", api_key="demo-key")
client.chat.completions.create(model="local", messages=[{"role":"user","content":"hi"}])
```

## 4. For the video

Screen-record your local terminal while connected via tmate: show tokens
streaming live, then flip to `report.html` to connect the demo's
responsiveness back to the measured KleidiAI speedup. Headline line:
*"This is running on a real Arm64 CPU that costs me nothing — no cloud
account, no server to maintain."*
