#!/bin/bash
# Prepare MetaCentrum for training: folders, uv, and the checkout's train environment.
# Run on a frontend after cloning, and again after every `git pull`.
set -euo pipefail
source "$(dirname "$0")/env.sh"

# The uv this repository is developed with, from its official release, checked
# against the release's published SHA-256 before it is unpacked.
UV_VERSION=0.12.17
UV_ARCHIVE=uv-x86_64-unknown-linux-gnu.tar.gz
UV_SHA256=fa82fd8dde8e8eefdecada6aa0889666556cfceb690d06e0c3bca49eb3070a63

mkdir -p "$ROOT/data" "$ROOT/models" "$RESULTS" "$LOGS" "$STORE/tools/bin"
chmod 700 "$STORE"
if [ "$(uv --version 2>/dev/null | cut -d' ' -f2)" != "$UV_VERSION" ]; then
    archive=$STORE/tools/$UV_ARCHIVE
    curl -LsSf -o "$archive" \
        "https://github.com/astral-sh/uv/releases/download/$UV_VERSION/$UV_ARCHIVE"
    echo "$UV_SHA256  $archive" | sha256sum --check --quiet
    tar -xzf "$archive" -C "$STORE/tools/bin" --strip-components=1
    rm "$archive"
fi

cd "$REPO"
uv sync --locked --group train
uv run --no-sync python -c \
    "import torch; print('torch', torch.__version__, 'built for CUDA', torch.version.cuda)"
