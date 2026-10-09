"""Synthetic corpora in the formats of CNEC 2.0, UNER and REDACT, and a scored stand-in model.

Every name and number is invented.
"""

import dataclasses
import json
import re
from pathlib import Path
from typing import Any

import pytest
from anonymizer.core.detect import models as models_module
from anonymizer.core.resources import Catalog, load_catalog

from experiments import systems as systems_module

CNEC_LINES = [
    "Včera přijel <P<pf Jan> <ps Novák>> do <gu Brna> .",
    "Volal <ps Svobodovi> na číslo <at 777 123 456> .",
    "Dopis poslali <pc Pražané> do <ic Nadace <P<pf Karla> <ps Dvořáka>>>"
    " v <A<gs Kounicova> <ah 12>> .",
    "Napište na <me info@example.cz> &amp; přijďte .",
]

UNER_TEXT = """# newdoc id = doc-a
# sent_id = a-1
# text = Ján Kováč prišiel do Bratislavy.
1\tJán\tB-PER\t-\t-
2\tKováč\tI-PER\t-\t-
3\tprišiel\tO\t-\t-
4\tdo\tO\t-\t-
5\tBratislavy\tB-LOC\t-\t-
6\t.\tO\t-\t-

# sent_id = a-2
# text = Pozdravuj Máriu.
1\tPozdravuj\tO\t-\t-
2\tMáriu\tB-PER\t-\t-
3\t.\tO\t-\t-

# newdoc id = doc-b
# sent_id = b-1
# text = Firma Tatra stojí.
1\tFirma\tO\t-\t-
2\tTatra\tB-ORG\t-\t-
3\tstojí\tO\t-\t-
4\t.\tO\t-\t-

"""


def redact_records() -> list[dict[str, Any]]:
    text = "Zákazník Jan Novák, e-mail jan.novak@example.cz, karta končí 1234."
    entities = [
        ("Full_Name", "Jan Novák"),
        ("First_Given_Name", "Jan"),
        ("Personal_Email_Address", "jan.novak@example.cz"),
        ("Credit_Card_Numbers", "1234"),
    ]
    records: list[dict[str, Any]] = [
        {
            "axes": {"language": "CS"},
            "text": text,
            "entities": [
                {
                    "entity_type": kind,
                    "entity_string": value,
                    "start": text.index(value),
                    "end": text.index(value) + len(value),
                }
                for kind, value in entities
            ]
            + [
                {
                    "entity_type": "Full_Name",
                    "entity_string": "Eva Malá",
                    "start": None,
                    "end": None,
                }
            ],
        },
        {"axes": {"language": "EN"}, "text": "John Smith", "entities": []},
    ]
    return records


class ScoredStandIn:
    """Finds fixed strings with fixed scores and honours the threshold, like GLiNER."""

    def __init__(self, found: dict[str, tuple[str, float]]) -> None:
        self.found = found
        self.calls = 0
        self.thresholds: list[float] = []

    def inference(
        self, texts: list[str], labels: list[str], *, threshold: float, flat_ner: bool
    ) -> list[list[dict[str, Any]]]:
        self.calls += 1
        self.thresholds.append(threshold)
        return [
            [
                {
                    "start": match.start(),
                    "end": match.end(),
                    "text": needle,
                    "label": label,
                    "score": score,
                }
                for needle, (label, score) in self.found.items()
                if label in labels and score > threshold
                for match in re.finditer(re.escape(needle), text)
            ]
            for text in texts
        ]


@pytest.fixture
def resource_root(tmp_path: Path) -> Path:
    """A storage root holding the three synthetic corpora where the catalog expects them."""
    root = tmp_path / "resources"
    plain = root / "data/cnec-2.0/Czech_Named_Entity_Corpus_2.0/cnec2.0/data/plain"
    plain.mkdir(parents=True)
    (plain / "named_ent_dtest.txt").write_text("\n".join(CNEC_LINES) + "\n", encoding="utf-8")
    (plain / "named_ent_etest.txt").write_text(CNEC_LINES[0] + "\n", encoding="utf-8")
    uner = root / "data/uner-sk-snk"
    uner.mkdir(parents=True)
    (uner / "sk_snk-ud-dev.iob2").write_text(UNER_TEXT, encoding="utf-8")
    redact = root / "data/redact"
    redact.mkdir(parents=True)
    (redact / "pii_benchmark_sample1000.json").write_text(
        json.dumps(redact_records(), ensure_ascii=False), encoding="utf-8"
    )
    return root


@pytest.fixture
def tuned_catalog(monkeypatch: pytest.MonkeyPatch) -> Catalog:
    """The shipped catalog with a fine-tuned GLiNER and a token classifier added."""
    shipped = load_catalog()
    base = shipped["gliner-multi-v2.1"]
    catalog = Catalog(
        {
            **shipped.resources,
            "gliner-cs-tuned": dataclasses.replace(base, id="gliner-cs-tuned"),
            "token-classifier": dataclasses.replace(
                base, id="token-classifier", engine="transformers", requires=()
            ),
        }
    )
    monkeypatch.setattr(models_module, "load_catalog", lambda: catalog)
    monkeypatch.setattr(systems_module, "load_catalog", lambda: catalog)
    return catalog
