#!/bin/bash
# Copy the jobs' results from MetaCentrum into experiments/results/.
# Run on the Mac, from the checkout. Weights stay on MetaCentrum.
# A file already there is never replaced, so a run that was not tagged cannot
# overwrite the Mac's results of the same name; delete a file to fetch it again.
set -euo pipefail

HOST=${HOST:-xszum00@skirit.metacentrum.cz}
STORE=${STORE:-/storage/budejovice1/home/xszum00}

cd "$(git rev-parse --show-toplevel)"
rsync -av --ignore-existing "$HOST:$STORE/results/" experiments/results/
