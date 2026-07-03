#!/usr/bin/env bash
# OPTIONAL / appendix path. The primary way to run KleidiBench is the free
# GitHub Actions arm64 runners (see ../.github/workflows/ and docs/setup.md) —
# no signup, no capacity friction. Use this script only if you want a
# persistent Arm box of your own beyond CI.
#
# Provisions a fresh Oracle Cloud Always-Free Ampere A1 (Ubuntu 22.04/24.04 arm64)
# to run KleidiBench. Idempotent-ish; safe to re-run.
#
# Prereqs (do these in the Oracle web console first):
#   1. Create an Always-Free "Ampere" (VM.Standard.A1.Flex) instance, arm64 Ubuntu.
#   2. Add your SSH key; note the public IP.
#   3. (For the live demo) add an ingress rule for TCP 8080 to the VCN security list.
#   4. SSH in:  ssh ubuntu@<public-ip>   then run this script.
set -euo pipefail

echo "== KleidiBench: Oracle Ampere A1 setup =="
uname -m   # expect aarch64

echo "== apt deps =="
sudo apt-get update -y
sudo apt-get install -y \
  build-essential cmake git python3 python3-pip python3-venv \
  libgomp1 time pkg-config

# llama.cpp CPU build needs no CUDA/BLAS; KleidiAI is vendored via the
# GGML_CPU_KLEIDIAI cmake flag and fetched at configure time.

echo "== python venv =="
python3 -m venv ~/kb-venv
# shellcheck disable=SC1090
source ~/kb-venv/bin/activate
python -m pip install --upgrade pip

echo "== clone + install kleidibench =="
if [ ! -d ~/kleidibench ]; then
  echo ">> git clone <YOUR-REPO-URL> ~/kleidibench   # <-- edit this line"
  echo ">> (or scp the repo up)"
fi
if [ -d ~/kleidibench ]; then
  pip install -e ~/kleidibench
  pip install ~/kleidibench[hf] || true   # for HF download/convert on the box
fi

echo "== open firewall for the demo endpoint (optional) =="
sudo iptables -I INPUT -p tcp --dport 8080 -j ACCEPT || true

echo
echo "Done. Next:"
echo "  source ~/kb-venv/bin/activate"
echo "  kleidibench info"
echo "  huggingface-cli login       # if pulling gated models like Llama"
echo "  kleidibench run meta-llama/Llama-3.2-3B"
