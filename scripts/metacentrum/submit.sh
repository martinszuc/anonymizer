#!/bin/bash
# Submit one training job per seed. Run on a frontend:
#
#   CLUSTER=<name> scripts/metacentrum/submit.sh experiments/configs/train-cs-sk-ce.toml base 1 2
#
# "base" trains with the config's own seed and is the default when no seed is
# given. CLUSTER pins every job to one GPU cluster, since models compared in one
# table come from one kind of machine; CLUSTER=any lets PBS pick (smoke tests).
# TAG (default gpu) is passed as --tag, so a config run on the Mac before keeps
# its results and model; TAG= trains a config never run elsewhere under its name.
set -euo pipefail
source "$(dirname "$0")/env.sh"

if [ $# -lt 1 ] || [ -z "${CLUSTER:-}" ]; then
    sed -n '2,10p' "$0" >&2
    exit 2
fi
config=$1
shift
seeds=("${@:-base}")
tag=${TAG-gpu}

select="select=1:ncpus=4:ngpus=1:gpu_mem=16gb:mem=32gb:scratch_local=40gb"
if [ "$CLUSTER" != any ]; then
    select+=":cluster=$CLUSTER"
fi

mkdir -p "$LOGS"
for seed in "${seeds[@]}"; do
    name=$(basename "$config" .toml)${tag:+-$tag}
    variables="STORE=$STORE,CONFIG=$config,TAG=$tag"
    if [ "$seed" != base ]; then
        name+="-s$seed"
        variables+=",SEED=$seed"
    fi
    qsub -N "$name" -v "$variables" -l "$select" -o "$LOGS/" "$REPO/scripts/metacentrum/train.pbs"
done
