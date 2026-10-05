"""Downloading models from the review window, with a tiny catalog and a fake server.

The catalog carries the real model ids, so the window's features find them,
but each file is a few bytes served from memory: nothing touches the network.
"""

import hashlib
import io
import threading
from pathlib import Path

import pytest
import webview
from anonymizer.core.resources import Catalog, Resource, ResourceFile
from anonymizer.ui import api
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
    "kraken-blla": b"segmenter",
    "kraken-ppocr-v6-medium": b"line recognizer",
}
CATALOG = Catalog(
    {
        "mdeberta-v3-base-tokenizer": _resource("mdeberta-v3-base-tokenizer"),
        "gliner-multi-v2.1": _resource("gliner-multi-v2.1", ("mdeberta-v3-base-tokenizer",)),
        "onnxtr-fast-base": _resource("onnxtr-fast-base"),
        "onnxtr-parseq-multilingual-v1": _resource(
            "onnxtr-parseq-multilingual-v1", ("onnxtr-fast-base",)
        ),
        "kraken-blla": _resource("kraken-blla"),
        "kraken-ppocr-v6-medium": _resource("kraken-ppocr-v6-medium", ("kraken-blla",)),
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
    assert [feature["feature"] for feature in review.models()] == [
        "names",
        "ocr-onnxtr",
        "ocr-kraken",
    ]
    ocr = _feature(review.models(), "ocr-onnxtr")
    assert ocr["title"] == "Scanned pages: OnnxTR"
    assert ocr["description"] == api.OCR_CHOICES["onnxtr"].description
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
    kraken = _feature(review.models(), "ocr-kraken")
    assert kraken["install_command"] == "uv sync --group ocr-kraken"
    assert [model["id"] for model in kraken["models"]] == ["kraken-blla", "kraken-ppocr-v6-medium"]


def test_each_ocr_engine_downloads_on_its_own(review: ReviewApi, server: FakeServer):
    models = review.download_models("ocr-kraken")
    assert server.requests == [
        "https://example.org/kraken-blla.bin",
        "https://example.org/kraken-ppocr-v6-medium.bin",
    ]
    assert _feature(models, "ocr-kraken")["missing_bytes"] == 0
    assert _feature(models, "ocr-onnxtr")["missing_bytes"] > 0


def test_download_fetches_only_that_feature_verified_and_reports_progress(
    review: ReviewApi, server: FakeServer, tmp_path: Path
):
    told: list[tuple[str, int, int]] = []
    models = review.download_models("ocr-onnxtr", lambda *step: told.append(step))
    ocr = _feature(models, "ocr-onnxtr")
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
    assert told[-1] == ("ocr-onnxtr", total, total)
    received = [step[1] for step in told]
    assert received == sorted(received)
    assert _feature(models, "names")["missing_bytes"] > 0


def test_stored_models_are_verified_not_downloaded_again(review: ReviewApi, server: FakeServer):
    review.download_models("ocr-onnxtr")
    server.requests.clear()
    told: list[tuple[str, int, int]] = []
    review.download_models("ocr-onnxtr", lambda *step: told.append(step))
    assert server.requests == []
    assert told == [("ocr-onnxtr", 0, 0)]


def test_a_file_that_does_not_match_its_checksum_is_refused_and_removed(tmp_path: Path):
    tampered = FakeServer()
    tampered.payloads["https://example.org/onnxtr-fast-base.bin"] = b"detectoR"
    review = ReviewApi(tmp_path, catalog=CATALOG, opener=tampered)
    with pytest.raises(ReviewError, match="the download failed"):
        review.download_models("ocr-onnxtr")
    assert not any((tmp_path / "models").rglob("*.bin"))
    assert not any((tmp_path / "models").rglob("*.part"))
    # The failed download let go of its models: another may start.
    assert review._downloading == set()


def test_an_unknown_feature_is_refused(review: ReviewApi, server: FakeServer):
    with pytest.raises(ReviewError, match="unknown feature 'datasets'"):
        review.download_models("datasets")
    assert server.requests == []


class HeldServer(FakeServer):
    """Holds the name model's download open until released, so another can run meanwhile."""

    def __init__(self) -> None:
        super().__init__()
        self.holding = threading.Event()
        self.release = threading.Event()

    def __call__(self, url: str) -> io.BytesIO:
        if "gliner" in url:
            self.holding.set()
            assert self.release.wait(timeout=10)
        return super().__call__(url)


def test_features_sharing_no_model_download_side_by_side(tmp_path: Path):
    server = HeldServer()
    review = ReviewApi(tmp_path, catalog=CATALOG, opener=server)
    names = threading.Thread(target=review.download_models, args=("names",))
    names.start()
    try:
        assert server.holding.wait(timeout=10)
        assert _feature(review.download_models("ocr-onnxtr"), "ocr-onnxtr")["missing_bytes"] == 0
        with pytest.raises(ReviewError, match="already running"):
            review.download_models("names")
    finally:
        server.release.set()
        names.join(timeout=10)
    assert _feature(review.models(), "names")["missing_bytes"] == 0
    assert review._downloading == set()


def test_the_window_tells_the_page_once_per_percent(tmp_path: Path, server: FakeServer):
    window = StandInWindow()
    api = WindowApi(ReviewApi(tmp_path, catalog=CATALOG, opener=server))
    api._attach(window)  # type: ignore[arg-type]
    api.download_models("ocr-onnxtr")
    told = [detail for event, detail in window.events_told() if event == "download"]
    assert told[-1] == {"feature": "ocr-onnxtr", "received": 26, "total": 26}
    percents = [detail["received"] * 100 // detail["total"] for detail in told]
    assert len(percents) == len(set(percents))
    assert _feature(api.models(), "ocr-onnxtr")["missing_bytes"] == 0


def test_a_chosen_folder_is_used_now_and_by_later_runs(tmp_path: Path, server: FakeServer):
    review = ReviewApi(tmp_path / "first", catalog=CATALOG, opener=server)
    review.download_models("ocr-onnxtr")
    assert _feature(review.models(), "ocr-onnxtr")["missing_bytes"] == 0
    status = review.choose_models_folder(str(tmp_path / "second"))
    assert status["models_folder"] == str((tmp_path / "second" / "models").resolve())
    # Nothing was moved: the new folder has no models yet.
    assert _feature(review.models(), "ocr-onnxtr")["missing_bytes"] > 0
    later = ReviewApi(catalog=CATALOG, opener=server)
    assert later.status()["models_folder"] == status["models_folder"]


def test_models_loaded_from_the_old_folder_are_dropped(tmp_path: Path):
    review = ReviewApi(tmp_path / "first", catalog=CATALOG)
    review._model = object()  # type: ignore[assignment]
    review._ocr["onnxtr"] = object()  # type: ignore[assignment]
    review.choose_models_folder(str(tmp_path / "second"))
    assert review._model is None
    assert review._ocr == {}


def test_the_folder_cannot_change_during_a_download(tmp_path: Path):
    review = ReviewApi(tmp_path / "first", catalog=CATALOG)
    review._downloading.add("onnxtr-fast-base")
    with pytest.raises(ReviewError, match="wait for the download"):
        review.choose_models_folder(str(tmp_path / "second"))
    assert review.status()["models_folder"] == str(tmp_path / "first" / "models")


def test_the_window_asks_for_a_folder(tmp_path: Path):
    window = StandInWindow(answers=[(str(tmp_path / "chosen"),), None])
    api = WindowApi(ReviewApi(tmp_path / "first", catalog=CATALOG))
    api._attach(window)  # type: ignore[arg-type]
    status = api.choose_models_folder()
    assert status is not None
    assert status["models_folder"] == str((tmp_path / "chosen" / "models").resolve())
    assert window.asked[0]["dialog"] == webview.FileDialog.FOLDER
    assert api.choose_models_folder() is None  # cancelled: nothing changes
    assert api.status()["models_folder"] == status["models_folder"]
