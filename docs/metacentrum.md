# Training on MetaCentrum

How `python -m experiments train` runs on MetaCentrum's GPU nodes. The scripts
are in `scripts/metacentrum/`; only public corpora and synthetic data go
there, never real documents.

## How it works

You log in to a **frontend** (`skirit.metacentrum.cz`) and never compute
there. A **job** asks the PBS scheduler for a GPU, CPUs, memory, local scratch
disk and a time limit; PBS starts it on a free GPU node, possibly hours later,
and it runs whether you are logged in or not.

Everything lives on one storage, mounted on every frontend and node:

```
/storage/budejovice1/home/xszum00/
  anonymizer/   the git checkout and its .venv (code only)
  root/         resource root: data/ and models/ (base models, trained models,
                models/trained.json)
  results/      results/<name>.json and .md of every job
  logs/         each job's output, <job id>.pbs-m1.metacentrum.cz.OU
  cache/        the prediction cache of `experiments run`
  tools/        uv, its cache and its Python
```

A job (`train.pbs`) copies `root/data` and the base model into its scratch,
trains there with the scratch as the resource root, then moves the trained
model into `root/models/` and lists it in `root/models/trained.json`
(`keep_trained.py`, under a lock, since jobs finish side by side) and copies
the results into `results/`. PBS deletes the scratch when the job ends.

## Privacy

Homes are created readable by every MetaCentrum user (`drwxr-xr-x`, group
`meta`) with umask `0022`. `setup.sh` closes the storage home (`chmod 700`)
and `env.sh` sets `umask 077` for everything the scripts and jobs write. Other
users still see the job list (`qstat`: user, job name, resources) and command
lines on a frontend (`ps`), so neither may hold a password or personal data.
CESNET's administrators can read everything. Weights trained on CNEC or UNER
hold real public names: they stay in `root/models/` and never leave it.

## Once

1. On the frontend, clone and set up (installs uv, syncs the `train` group;
   rerun after every `git pull`):

   ```sh
   git clone https://github.com/martinszuc/anonymizer.git /storage/budejovice1/home/xszum00/anonymizer
   /storage/budejovice1/home/xszum00/anonymizer/scripts/metacentrum/setup.sh
   ```

2. On the Mac, copy the corpora and the base model (about 6 GB) and verify
   them there against the catalog; the password is asked once:

   ```sh
   scripts/metacentrum/push-data.sh
   ```

## Every run

On the frontend:

```sh
source /storage/budejovice1/home/xszum00/anonymizer/scripts/metacentrum/env.sh
cd $REPO
CLUSTER=any scripts/metacentrum/submit.sh experiments/configs/train-smoke.toml
qstat -x -u $USER                    # Q queued, R running, F finished
qstat -xf <job id> | grep Exit_status  # 0: it worked
tail -30 $LOGS/<job id>*.OU           # the GPU it ran on, the loss, the scores
```

The smoke run trains 40 steps; when it passes, submit the real runs pinned to
one cluster:

```sh
CLUSTER=fobos scripts/metacentrum/submit.sh experiments/configs/train-cs-sk-ce.toml base 1 2
```

`base` is the config's own seed, `1 2` its replicates (`<model>-s1`,
`<model>-s2`); each seed is its own job, and they run side by side. `qdel
<job id>` cancels one. Each job asks for 1 GPU with at least 16 GB, 4 CPUs,
32 GB of memory, 40 GB of scratch and 2 hours (`submit.sh`, `train.pbs`); a
2,000-step run took about 8 minutes of training on an L40S.

A pinned cluster must serve the `gpu` queue: `pbsnodes <node> | grep
queue_list` shows the queues of one of its nodes. galdor is not in `gpu`
(its nodes ran `gpu_long` jobs), and jobs pinned to it wait forever with `Not Running: Insufficient
amount of resource: queue_list` (`qstat -f <job id> | grep comment`). fobos
(NVIDIA L40S) serves `gpu`.

`--tag gpu` (`TAG`, the default) names the runs `<name>-gpu` and
`<model>-gpu`, so a config already run on the Mac keeps its results and model.
A config never run elsewhere is submitted with `TAG=` and keeps its name.

Run configs naming the trained models are scored on a CPU node (GLiNER
predicts on the CPU). Each config is its own job, started only after the one
before it ended, since they share the prediction cache:

```sh
scripts/metacentrum/evaluate.sh experiments/configs/rq6-gpu-dev.toml experiments/configs/rq7-dev.toml
```

On the Mac, copy the results of both kinds into `experiments/results/`; a
file already there is never replaced:

```sh
scripts/metacentrum/pull-results.sh
```

## Rules

- **One kind of machine per table.** Models compared in one table are trained
  on one cluster (`CLUSTER=`), and runs from the M4 Pro are not mixed in.
- **The checkout is the code that ran.** Results record its commit; pull and
  rerun `setup.sh` before submitting, not while jobs are queued.
- **Offline.** Jobs run with `HF_HUB_OFFLINE=1`; models load from `root/`
  only. The only downloads are uv and the Python packages in `setup.sh`.
