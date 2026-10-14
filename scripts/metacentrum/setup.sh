#!/bin/bash
# Prepare MetaCentrum for training: folders, uv, and the checkout's train environment.
# Run on a frontend after cloning, and again after every `git pull`.
set -euo pipefail
source "$(dirname "$0")/env.sh"

# The uv this repository is developed with; the installer comes from its official source.
UV_VERSION=0.12.17

mkdir -p "$ROOT/data" "$ROOT/models" "$RESULTS" "$LOGS" "$STORE/tools/bin"
chmod 700 "$STORE"
if [ "$(uv --version 2>/dev/null | cut -d' ' -f2)" != "$UV_VERSION" ]; then
    curl -LsSf "https://astral.sh/uv/$UV_VERSION/install.sh" |
        env UV_INSTALL_DIR="$STORE/tools/bin" UV_NO_MODIFY_PATH=1 sh
fi

cd "$REPO"
uv sync --locked --group train
uv run --no-sync python -c \
    "import torch; print('torch', torch.__version__, 'built for CUDA', torch.version.cuda)"
