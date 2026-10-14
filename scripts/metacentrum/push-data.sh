#!/bin/bash
# Copy the corpora and base models training reads from this Mac to MetaCentrum,
# then re-hash them there against the catalog. Run on the Mac, from the checkout.
set -euo pipefail

HOST=${HOST:-xszum00@skirit.metacentrum.cz}
STORE=${STORE:-/storage/budejovice1/home/xszum00}
DATASETS=(cnec-2.0 uner-sk-snk openpii-1m redact)
MODELS=(gliner-multi-v2.1 mdeberta-v3-base-tokenizer)

cd "$(git rev-parse --show-toplevel)"
# One ssh connection for every step, so the password is asked once.
SSH="ssh -o ControlMaster=auto -o ControlPath=$HOME/.ssh/cm-%C -o ControlPersist=10m"

$SSH "$HOST" "mkdir -p $STORE/root/data $STORE/root/models"
rsync -av --partial -e "$SSH" "${DATASETS[@]/#/data/}" "$HOST:$STORE/root/data/"
rsync -av --partial -e "$SSH" "${MODELS[@]/#/models/}" "$HOST:$STORE/root/models/"
$SSH "$HOST" "source $STORE/anonymizer/scripts/metacentrum/env.sh && cd \$REPO &&
    uv run --no-sync python scripts/download.py --root \$ROOT verify"
