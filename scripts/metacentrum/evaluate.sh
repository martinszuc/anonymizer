#!/bin/bash
# Submit an `experiments run` per run config. Run on a frontend:
#
#   scripts/metacentrum/evaluate.sh experiments/configs/rq6-gpu-dev.toml experiments/configs/rq7-dev.toml
#
# The results land beside the training results; pull-results.sh fetches both.
# Configs naming the same models share the prediction cache, so each job waits
# for the one before it (depend=afterany) instead of running side by side.
set -euo pipefail
source "$(dirname "$0")/env.sh"

if [ $# -lt 1 ]; then
    sed -n '2,8p' "$0" >&2
    exit 2
fi
mkdir -p "$LOGS"
previous=
for config in "$@"; do
    previous=$(qsub -N "$(basename "$config" .toml)" -v "STORE=$STORE,CONFIG=$config" \
        -l "select=1:ncpus=8:mem=48gb" -o "$LOGS/" ${previous:+-W depend=afterany:$previous} \
        "$REPO/scripts/metacentrum/run.pbs")
    echo "$previous $config"
done
