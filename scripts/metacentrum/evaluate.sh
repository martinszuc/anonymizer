#!/bin/bash
# Submit an `experiments run` per run config. Run on a frontend:
#
#   scripts/metacentrum/evaluate.sh experiments/configs/rq6-gpu-dev.toml experiments/configs/rq7-dev.toml
#
# The results land beside the training results; pull-results.sh fetches both.
# Configs naming the same models share the prediction cache, so each job waits
# for the one before it (depend=afterany) instead of running side by side.
# AFTER=<job id>[:<job id>...] makes the first wait for training jobs to succeed:
# a model replaced while a run reads it would cache the new model's predictions
# under the old model's version.
set -euo pipefail
source "$(dirname "$0")/env.sh"

if [ $# -lt 1 ]; then
    sed -n '2,11p' "$0" >&2
    exit 2
fi
for config in "$@"; do
    require_config "$config"
done
mkdir -p "$LOGS"
depend=${AFTER:+afterok:$AFTER}
for config in "$@"; do
    job=$(qsub -N "$(basename "$config" .toml)" -v "STORE=$STORE,CONFIG=$config" \
        -l "select=1:ncpus=8:mem=48gb" -o "$LOGS/" ${depend:+-W depend=$depend} \
        "$REPO/scripts/metacentrum/run.pbs")
    depend=afterany:$job
    echo "$job $config"
done
