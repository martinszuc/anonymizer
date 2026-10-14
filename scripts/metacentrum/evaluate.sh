#!/bin/bash
# Submit an `experiments run` of a run config. Run on a frontend:
#
#   scripts/metacentrum/evaluate.sh experiments/configs/rq6-gpu-dev.toml
#
# The results land beside the training results; pull-results.sh fetches both.
# Configs naming the same models share the prediction cache: submit them one
# after another (qsub -W depend=afterany:<job id>), not side by side.
set -euo pipefail
source "$(dirname "$0")/env.sh"

if [ $# -ne 1 ]; then
    sed -n '2,8p' "$0" >&2
    exit 2
fi
name=$(basename "$1" .toml)
mkdir -p "$LOGS"
qsub -N "$name" -v "STORE=$STORE,CONFIG=$1" -l "select=1:ncpus=8:mem=48gb" -o "$LOGS/" \
    "$REPO/scripts/metacentrum/run.pbs"
