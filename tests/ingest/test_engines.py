"""Tests for the list of OCR engines a client can choose."""

import importlib.util
import sys
from pathlib import Path

import pytest
from anonymizer.core.ingest import (
    OCR_ENGINE_RESOURCES,
    OCR_ENGINES,
    load_ocr_engine,
    missing_ocr_files,
    ocr_engine_installed,
)
from anonymizer.core.resources import load_catalog


def test_every_engine_names_its_catalog_models():
    catalog = load_catalog()
    assert OCR_ENGINES.keys() == OCR_ENGINE_RESOURCES.keys()
    for resources in OCR_ENGINE_RESOURCES.values():
        assert all(catalog[resource_id].uses for resource_id in resources)


def test_unknown_engine_is_refused(tmp_path: Path):
    with pytest.raises(ValueError, match="unknown OCR engine 'tesseract'"):
        load_ocr_engine("tesseract", tmp_path)


def test_missing_models_are_listed_in_download_order(tmp_path: Path):
    assert missing_ocr_files("onnxtr", tmp_path) == list(OCR_ENGINE_RESOURCES["onnxtr"])


def test_no_models_are_missing_once_every_file_is_stored(tmp_path: Path):
    for resource in load_catalog().with_requirements(OCR_ENGINE_RESOURCES["onnxtr"][-1]):
        for item in resource.files:
            stored = resource.directory(tmp_path) / item.path
            stored.parent.mkdir(parents=True, exist_ok=True)
            stored.write_bytes(b"")
    assert missing_ocr_files("onnxtr", tmp_path) == []


def test_installed_is_checked_without_importing(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setitem(sys.modules, "onnxtr", None)
    assert ocr_engine_installed("onnxtr") is False
    monkeypatch.delitem(sys.modules, "onnxtr")
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: object())
    assert ocr_engine_installed("onnxtr") is True
