"""Print the catalog ids of the models a training config starts from, one per line.

    python scripts/metacentrum/base_models.py <config>

The base model and everything it requires (its tokenizer), in the order the
catalog fetches them. `train.pbs` copies these folders from the storage's
resource root into the job's scratch, so a config naming another base (GLiNER
or XLM-RoBERTa large) needs no change to the job script.
"""

from __future__ import annotations

import sys
from pathlib import Path

from anonymizer.core.resources import load_catalog

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT))

from experiments.train import load_train_config  # noqa: E402


def base_models(config: Path) -> list[str]:
    """Return the ids of a training config's base model and its requirements."""
    base = load_train_config(config).base
    return [resource.id for resource in load_catalog().with_requirements(base)]


def main(argv: list[str]) -> int:
    """Run the command line; return the exit code."""
    if len(argv) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    for model_id in base_models(Path(argv[0])):
        print(model_id)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
