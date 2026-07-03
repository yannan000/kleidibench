#!/usr/bin/env python3
"""Minimal OpenAI-compatible client for the KleidiBench demo endpoint.

Talks to the llama.cpp server (see server.md) with no third-party SDK — just
stdlib — so it runs on a bare Arm VM. Supports streaming so you can show tokens
arriving live in the demo video.

Usage:
    python3 demo_client.py "Explain KleidiAI in two sentences."
    python3 demo_client.py --base-url http://1.2.3.4:8080/v1 --stream "Hi"
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request


def chat(base_url: str, prompt: str, api_key: str, stream: bool,
         model: str = "local", max_tokens: int = 256) -> None:
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "stream": stream,
    }
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {api_key}"},
        method="POST",
    )

    t0 = time.time()
    first_token_at = None
    n_tokens = 0

    with urllib.request.urlopen(req) as resp:
        if not stream:
            data = json.loads(resp.read())
            print(data["choices"][0]["message"]["content"])
            return
        for raw in resp:
            line = raw.decode().strip()
            if not line or not line.startswith("data:"):
                continue
            body = line[len("data:"):].strip()
            if body == "[DONE]":
                break
            try:
                chunk = json.loads(body)
            except json.JSONDecodeError:
                continue
            delta = chunk["choices"][0].get("delta", {}).get("content", "")
            if delta:
                if first_token_at is None:
                    first_token_at = time.time()
                n_tokens += 1
                sys.stdout.write(delta)
                sys.stdout.flush()

    dt = time.time() - t0
    ttft = (first_token_at - t0) if first_token_at else dt
    tps = n_tokens / (dt - (ttft if first_token_at else 0)) if dt > ttft else 0.0
    print(f"\n\n[TTFT {ttft*1000:.0f} ms | {n_tokens} tok | {tps:.1f} tok/s]",
          file=sys.stderr)


def main() -> int:
    p = argparse.ArgumentParser(description="OpenAI-compatible demo client.")
    p.add_argument("prompt")
    p.add_argument("--base-url", default="http://localhost:8080/v1")
    p.add_argument("--api-key", default="demo-key")
    p.add_argument("--model", default="local")
    p.add_argument("--max-tokens", type=int, default=256)
    p.add_argument("--stream", action="store_true")
    args = p.parse_args()
    chat(args.base_url, args.prompt, args.api_key, args.stream,
         model=args.model, max_tokens=args.max_tokens)
    return 0


if __name__ == "__main__":
    sys.exit(main())
