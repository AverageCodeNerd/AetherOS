#!/usr/bin/env bash
set -euo pipefail

sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  build-essential \
  ca-certificates \
  curl \
  debootstrap \
  genisoimage \
  git \
  live-build \
  nodejs \
  npm \
  ovmf \
  python3 \
  python3-pil \
  qemu-system-x86 \
  qemu-utils \
  wget \
  xorriso

echo "AETHER OS build tooling is installed."
