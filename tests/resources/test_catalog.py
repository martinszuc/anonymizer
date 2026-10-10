import copy
import json
from pathlib import Path
from typing import Any

import pytest
from anonymizer.core.resources import load_catalog, trained_catalog_path
from anonymizer.core.resources.catalog import parse_catalog

SHA256_HELLO = "5891b5b522d5df086d0ff0b110fbd9d21bb4fc7163af34d08286a2e846f6be03"

VALID: dict[str, Any] = {
    "schema": 1,
    "resource": [
        {
            "id": "tiny-model",
            "name": "Tiny model",
            "kind": "model",
            "uses": ["ner"],
            "source": "https://example.org/tiny",
            "version": "abc123",
            "licence": "MIT",
            "languages": ["cs", "sk"],
            "files": [
                {
                    "path": "weights.bin",
                    "url": "https://example.org/tiny/weights.bin",
                    "size": 6,
                    "sha256": SHA256_HELLO,
                }
            ],
        }
    ],
}


def _with(change: dict[str, Any], file_change: dict[str, Any] | None = None) -> dict[str, Any]:
    raw = copy.deepcopy(VALID)
    raw["resource"][0].update(change)
    if file_change is not None:
        raw["resource"][0]["files"][0].update(file_change)
    return raw


def test_shipped_catalog_is_valid():
    catalog = load_catalog()
    assert {"gliner-multi-v2.1", "redact", "cnec-2.0", "uner-sk-snk"} <= set(catalog.resources)


def test_shipped_catalog_pins_every_file_to_https():
    for resource in load_catalog().resources.values():
        for item in resource.files:
            assert item.url is not None
            assert item.url.startswith("https://")
            assert item.sha256 is not None or item.source_digest is not None


def test_shipped_corpora_naming_real_people_are_flagged():
    catalog = load_catalog()
    assert catalog["cnec-2.0"].real_personal_data
    assert catalog["uner-sk-snk"].real_personal_data
    assert not catalog["redact"].real_personal_data


def test_requirements_come_first():
    order = [resource.id for resource in load_catalog().with_requirements("gliner-multi-v2.1")]
    assert order == ["mdeberta-v3-base-tokenizer", "gliner-multi-v2.1"]


def test_kind_decides_directory():
    catalog = load_catalog()
    root = Path("/store")
    assert catalog["gliner-multi-v2.1"].directory(root) == root / "models" / "gliner-multi-v2.1"
    assert catalog["redact"].directory(root) == root / "data" / "redact"


def test_valid_entry_parses():
    resource = parse_catalog(VALID)["tiny-model"]
    assert resource.languages == ("cs", "sk")
    assert resource.size == 6
    assert resource.files[0].sha256 == SHA256_HELLO


def test_source_digest_alone_is_accepted():
    raw = _with({}, {"sha256": None, "source_digest": "md5:b1946ac92492d2347c6235b4d2611184"})
    del raw["resource"][0]["files"][0]["sha256"]
    item = parse_catalog(raw)["tiny-model"].files[0]
    assert item.sha256 is None
    assert item.source_digest == ("md5", "b1946ac92492d2347c6235b4d2611184")


def test_unknown_id_raises_key_error():
    with pytest.raises(KeyError, match="unknown resource"):
        parse_catalog(VALID)["missing"]


@pytest.mark.parametrize(
    ("change", "file_change", "message"),
    [
        ({"id": "Bad Id"}, None, "invalid resource id"),
        ({"kind": "tool"}, None, "kind must be"),
        ({"uses": []}, None, "uses must be"),
        ({"uses": ["translation"]}, None, "uses must be"),
        ({"languages": ["ces"]}, None, "languages"),
        ({"licence": ""}, None, "missing licence"),
        ({"source": "http://example.org"}, None, "source must be an HTTPS URL"),
        ({"files": []}, None, "no files"),
        ({}, {"path": "../escape.bin"}, "must be relative"),
        ({}, {"path": "/abs.bin"}, "must be relative"),
        ({}, {"path": "dir\\file.bin"}, "must be relative"),
        ({}, {"url": "http://example.org/weights.bin"}, "url must be HTTPS"),
        ({}, {"size": 0}, "size must be"),
        ({}, {"sha256": SHA256_HELLO.upper()}, "sha256 must be"),
        ({}, {"sha256": SHA256_HELLO[:-1]}, "sha256 must be"),
        ({}, {"source_digest": "sha1:" + "0" * 40}, "source_digest"),
        ({}, {"source_digest": "md5:" + "0" * 31}, "source_digest"),
        ({}, {"unpack": "rar"}, "unpack must be"),
        ({"requires": ["absent"]}, None, "requires unknown resource"),
    ],
)
def test_invalid_entries_are_refused(change, file_change, message):
    with pytest.raises(ValueError, match=message):
        parse_catalog(_with(change, file_change))


def test_file_without_any_checksum_is_refused():
    raw = copy.deepcopy(VALID)
    del raw["resource"][0]["files"][0]["sha256"]
    with pytest.raises(ValueError, match="needs sha256 or source_digest"):
        parse_catalog(raw)


def test_wrong_schema_is_refused():
    with pytest.raises(ValueError, match="unsupported catalog schema"):
        parse_catalog({**VALID, "schema": 2})


def test_duplicate_id_is_refused():
    raw = copy.deepcopy(VALID)
    raw["resource"].append(copy.deepcopy(raw["resource"][0]))
    with pytest.raises(ValueError, match="duplicate resource id"):
        parse_catalog(raw)


def test_duplicate_file_path_is_refused():
    raw = copy.deepcopy(VALID)
    raw["resource"][0]["files"].append(copy.deepcopy(raw["resource"][0]["files"][0]))
    with pytest.raises(ValueError, match="duplicate file path"):
        parse_catalog(raw)


def test_requirement_cycle_is_refused():
    raw = copy.deepcopy(VALID)
    second = copy.deepcopy(raw["resource"][0])
    second["id"] = "other-model"
    second["requires"] = ["tiny-model"]
    raw["resource"][0]["requires"] = ["other-model"]
    raw["resource"].append(second)
    with pytest.raises(ValueError, match="requirement cycle"):
        parse_catalog(raw)


def trained_entry(**change: Any) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "id": "gliner-cs-tuned",
        "name": "GLiNER fine-tuned for Czech",
        "kind": "model",
        "uses": ["ner"],
        "engine": "gliner",
        "trained": True,
        "source": "experiments/results/train-cs.json",
        "version": SHA256_HELLO,
        "licence": "LicenseRef-Trained-Locally",
        "languages": ["cs", "sk"],
        "requires": ["mdeberta-v3-base-tokenizer"],
        "files": [{"path": "model.safetensors", "size": 6, "sha256": SHA256_HELLO}],
    }
    entry.update(change)
    return entry


def store_trained(root: Path, *entries: dict[str, Any]) -> None:
    path = trained_catalog_path(root)
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"schema": 1, "resource": list(entries)}), encoding="utf-8")


class TestTrainedModels:
    def test_a_roots_trained_models_join_the_shipped_catalog(self, tmp_path: Path):
        store_trained(tmp_path, trained_entry())
        catalog = load_catalog(root=tmp_path)
        trained = catalog["gliner-cs-tuned"]
        assert trained.trained
        assert trained.files[0].url is None
        assert [resource.id for resource in catalog.with_requirements(trained.id)] == [
            "mdeberta-v3-base-tokenizer",
            "gliner-cs-tuned",
        ]
        assert "gliner-cs-tuned" not in load_catalog().resources

    def test_a_root_without_trained_models_reads_the_shipped_catalog(self, tmp_path: Path):
        assert load_catalog(root=tmp_path) == load_catalog()

    @pytest.mark.parametrize(
        ("change", "message"),
        [
            ({"id": "gliner-multi-v2.1"}, "duplicate resource id"),
            ({"trained": False}, "sets trained = true"),
            ({"kind": "dataset"}, "only a model can be trained"),
            (
                {
                    "files": [
                        {
                            "path": "model.safetensors",
                            "url": "https://example.org/m",
                            "size": 6,
                            "sha256": SHA256_HELLO,
                        }
                    ]
                },
                "has no url",
            ),
            (
                {
                    "files": [
                        {"path": "model.safetensors", "size": 6, "source_digest": "md5:" + "0" * 32}
                    ]
                },
                "needs its sha256",
            ),
        ],
    )
    def test_invalid_trained_entries_are_refused(
        self, tmp_path: Path, change: dict[str, Any], message: str
    ):
        store_trained(tmp_path, trained_entry(**change))
        with pytest.raises(ValueError, match=message):
            load_catalog(root=tmp_path)

    def test_the_shipped_catalog_lists_no_trained_model(self):
        with pytest.raises(ValueError, match=r"only a storage root's trained\.json"):
            parse_catalog(_with({"trained": True}))
