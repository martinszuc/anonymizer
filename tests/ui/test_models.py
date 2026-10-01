"""Downloading models from the review window, with a tiny catalog and a fake server.

The catalog carries the real model ids, so the window's features find them,
but each file is a few bytes served from memory: nothing touches the network.
"""

import hashlib
import io
from pathlib import Path

import pytest
from anonymizer.core.resources import Catalog, Resource, ResourceFile
from anonymizer.ui.api import ReviewApi, ReviewError
from anonymizer.ui.app import WindowApi

from tests.ui.test_app import StandInWindow


def _file(resource_id: str, payload: bytes) -> ResourceFile:
    return ResourceFile(
        path=f"{resource_id}.bin",
        url=f"https://example.org/{resource_id}.bin",
        size=len(payload),
        sha256=hashlib.sha256(payload).hexdigest(),
    )


def _resource(resource_id: str, requires: tuple[str, ...] = ()) -> Resource:
    return Resource(
        id=resource_id,
        name=resource_id.replace("-", " "),
        kind="model",
        uses=("ocr-recognition",),
        source=f"https://example.org/{resource_id}",
        version="1",
        licence="Apache-2.0",
        languages=("cs",),
        files=(_file(resource_id, PAYLOADS[resource_id]),),
        requires=requires,
    )


PAYLOADS = {
    "mdeberta-v3-base-tokenizer": b"tokenizer",
    "gliner-multi-v2.1": b"name model weights",
    "onnxtr-fast-base": b"detector",
    "onnxtr-parseq-multilingual-v1": b"recognizer weights",
}
CATALOG = Catalog(
    {
        "mdeberta-v3-base-tokenizer": _resource("mdeberta-v3-base-tokenizer"),
        "gliner-multi-v2.1": _resource("gliner-multi-v2.1", ("mdeberta-v3-base-tokenizer",)),
        "onnxtr-fast-base": _resource("onnxtr-fast-base"),
        "onnxtr-parseq-multilingual-v1": _resource(
            "onnxtr-parseq-multilingual-v1", ("onnxtr-fast-base",)
        ),
    }
)


class FakeServer:
    """Serves the payloads by URL and records each request."""

    def __init__(self, payloads: dict[str, bytes] | None = None) -> None:
        self.payloads = payloads or {
            f"https://example.org/{key}.bin": value for key, value in PAYLOADS.items()
        }
        self.requests: list[str] = []

    def __call__(self, url: str) -> io.BytesIO:
        self.requests.append(url)
        return io.BytesIO(self.payloads[url])


@pytest.fixture
def server() -> FakeServer:
    return FakeServer()


@pytest.fixture
def review(tmp_path: Path, server: FakeServer) -> ReviewApi:
    return ReviewApi(tmp_path, catalog=CATALOG, opener=server)


def _feature(models: list[dict], key: str) -> dict:
    (feature,) = [item for item in models if item["feature"] == key]
    return feature


def test_models_lists_each_feature_with_requirements_first(review: ReviewApi):
    ocr = _feature(review.models(), "ocr")
    assert ocr["title"] == "Scanned pages"
    assert ocr["install_command"] == "uv sync --group ocr-onnxtr"
    assert [model["id"] for model in ocr["models"]] == [
        "onnxtr-fast-base",
        "onnxtr-parseq-multilingual-v1",
    ]
    assert {model["state"] for model in ocr["models"]} == {"absent"}
    assert ocr["missing_bytes"] == len(b"detector") + len(b"recognizer weights")
    first = ocr["models"][0]
    assert (first["licence"], first["languages"], first["size"]) == ("Apache-2.0", ["cs"], 8)
    assert _feature(review.models(), "names")["install_command"] == "uv sync --group ner"


def test_download_fetches_only_that_feature_verified_and_reports_progress(
    review: ReviewApi, server: FakeServer, tmp_path: Path
):
    told: list[tuple[str, int, int]] = []
    models = review.download_models("ocr", lambda *step: told.append(step))
    ocr = _feature(models, "ocr")
    assert {model["state"] for model in ocr["models"]} == {"present"}
    assert ocr["missing_bytes"] == 0
    assert server.requests == [
        "https://example.org/onnxtr-fast-base.bin",
        "https://example.org/onnxtr-parseq-multilingual-v1.bin",
    ]
    assert (tmp_path / "models" / "onnxtr-fast-base" / "onnxtr-fast-base.bin").read_bytes() == (
        b"detector"
    )
    total = len(b"detector") + len(b"recognizer weights")
    assert told[-1] == ("ocr", total, total)
    received = [step[1] for step in told]
    assert received == sorted(received)
    assert _feature(models, "names")["missing_bytes"] > 0


def test_stored_models_are_verified_not_downloaded_again(review: ReviewApi, server: FakeServer):
    review.download_models("ocr")
    server.requests.clear()
    told: list[tuple[str, int, int]] = []
    review.download_models("ocr", lambda *step: told.append(step))
    assert server.requests == []
    assert told == [("ocr", 0, 0)]


def test_a_file_that_does_not_match_its_checksum_is_refused_and_removed(tmp_path: Path):
    tampered = FakeServer()
    tampered.payloads["https://example.org/onnxtr-fast-base.bin"] = b"detectoR"
    review = ReviewApi(tmp_path, catalog=CATALOG, opener=tampered)
    with pytest.raises(ReviewError, match="the download failed"):
        review.download_models("ocr")
    assert not any((tmp_path / "models").rglob("*.bin"))
    assert not any((tmp_path / "models").rglob("*.part"))
    # The failed download released the lock: another may start.
    assert review._downloading.acquire(blocking=False)


def test_an_unknown_feature_is_refused(review: ReviewApi, server: FakeServer):
    with pytest.raises(ReviewError, match="unknown feature 'datasets'"):
        review.download_models("datasets")
    assert server.requests == []


def test_a_second_download_while_one_runs_is_refused(review: ReviewApi, server: FakeServer):
    review._downloading.acquire()
    try:
        with pytest.raises(ReviewError, match="already running"):
            review.download_models("ocr")
    finally:
        review._downloading.release()
    assert server.requests == []


def test_the_window_tells_the_page_once_per_percent(tmp_path: Path, server: FakeServer):
    window = StandInWindow()
    api = WindowApi(ReviewApi(tmp_path, catalog=CATALOG, opener=server))
    api._attach(window)  # type: ignore[arg-type]
    api.download_models("ocr")
    told = [detail for event, detail in window.events_told() if event == "download"]
    assert told[-1] == {"feature": "ocr", "received": 26, "total": 26}
    percents = [detail["received"] * 100 // detail["total"] for detail in told]
    assert len(percents) == len(set(percents))
    assert _feature(api.models(), "ocr")["missing_bytes"] == 0
