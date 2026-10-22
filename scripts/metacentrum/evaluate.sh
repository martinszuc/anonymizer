#!/bin/bash
# Submit an `experiments run` per run config, each on a GPU node. Run on a frontend:
#
#   scripts/metacentrum/evaluate.sh experiments/configs/rq6-gpu-dev.toml experiments/configs/rq7-dev.toml
#
# CLUSTER (default fobos, where the models were trained) pins every job to one
# GPU cluster, since scores compared in one table come from one kind of card;
# CLUSTER=any lets PBS pick (smoke tests). The results land beside the training
# results; pull-results.sh fetches both. Configs naming the same models share
# the prediction cache, so each job waits for the one before it
# (depend=afterany) instead of running side by side.
# COMMAND=errors runs `experiments errors` instead (what kind of names each
# system misses and wrongly flags); the default is `run`.
# AFTER=<job id>[:<job id>...] makes the first wait for training jobs to succeed:
# a model replaced while a run reads it would cache the new model's predictions
# under the old model's version.
set -euo pipefail
source "$(dirname "$0")/env.sh"

if [ $# -lt 1 ]; then
    sed -n '2,16p' "$0" >&2
    exit 2
fi
for config in "$@"; do
    require_config "$config"
done
cluster=${CLUSTER:-fobos}
select="select=1:ncpus=4:ngpus=1:gpu_mem=16gb:mem=32gb"
if [ "$cluster" != any ]; then
    select+=":cluster=$cluster"
fi

mkdir -p "$LOGS"
depend=${AFTER:+afterok:$AFTER}
for config in "$@"; do
    job=$(qsub -N "$(basename "$config" .toml)${COMMAND:+-$COMMAND}" -v "STORE=$STORE,CONFIG=$config,COMMAND=${COMMAND:-run}" \
        -l "$select" -o "$LOGS/" ${depend:+-W depend=$depend} \
        "$REPO/scripts/metacentrum/run.pbs")
    depend=afterany:$job
    echo "$job $config"
done
