# Paths and settings shared by the MetaCentrum scripts, on the frontend and in jobs.
# Sourced, not run: `source scripts/metacentrum/env.sh`.

# One storage holds everything; a frontend's own home (`~`) differs per frontend.
STORE=${STORE:-/storage/budejovice1/home/$USER}
REPO=$STORE/anonymizer   # the git checkout and its .venv: code only
ROOT=$STORE/root         # the resource root: data/ and models/, never in git
RESULTS=$STORE/results   # results/<name>.json and .md of every job
LOGS=$STORE/logs         # the jobs' output
export STORE REPO ROOT RESULTS LOGS

# uv, its cache and its Python live in the storage, not in a frontend's home.
export PATH=$STORE/tools/bin:$PATH
export UV_CACHE_DIR=$STORE/tools/uv-cache
export UV_PYTHON_INSTALL_DIR=$STORE/tools/python

# Models load from the resource root only (CLAUDE.md: offline only).
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
# Debian has no plain "UTF-8" locale, which macOS sends over ssh.
export LANG=C.UTF-8 LC_ALL=C.UTF-8
# Homes are created readable by every MetaCentrum user; what we write is not.
umask 077
