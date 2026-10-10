import hashlib
import io
import zipfile
from pathlib import Path

import pytest
from anonymizer.core.resources import (
    Catalog,
    ChecksumError,
    NotDownloadableError,
    PinRequiredError,
    Resource,
    ResourceFile,
    fetch_resource,
    fetch_with_requirements,
    resource_status,
    verify_resource,
)

HELLO = b"hello\n"
# Digests of HELLO from outside Python: `shasum -a 256`, `md5`, `git hash-object`.
SHA256_HELLO = "5891b5b522d5df086d0ff0b110fbd9d21bb4fc7163af34d08286a2e846f6be03"
MD5_HELLO = "b1946ac92492d2347c6235b4d2611184"
GIT_SHA1_HELLO = "ce013625030ba8dba906f756967f9e9ca394464a"
URL = "https://example.org/hello.txt"


class FakeServer:
    """Serves bytes by URL from memory and records every request."""

    def __init__(self, payloads: dict[str, bytes]) -> None:
        self.payloads = payloads
        self.requests: list[str] = []

    def __call__(self, url: str) -> io.BytesIO:
        self.requests.append(url)
        return io.BytesIO(self.payloads[url])


class BrokenStream(io.BytesIO):
    def read(self, size: int | None = -1, /) -> bytes:
        if self.tell() > 0:
            raise OSError("connection reset")
        return super().read(2)


def _resource(*files: ResourceFile, kind: str = "dataset") -> Resource:
    return Resource(
        id="sample",
        name="Sample",
        kind=kind,  # type: ignore[arg-type]
        uses=("benchmark",),
        source="https://example.org",
        version="1",
        licence="MIT",
        languages=("cs",),
        files=files,
    )


def _hello(**overrides: object) -> ResourceFile:
    fields: dict[str, object] = {
        "path": "hello.txt",
        "url": URL,
        "size": len(HELLO),
        "sha256": SHA256_HELLO,
    }
    fields.update(overrides)
    return ResourceFile(**fields)  # type: ignore[arg-type]


def _leftovers(directory: Path) -> list[str]:
    return sorted(path.name for path in directory.rglob("*.part"))


def test_download_verifies_and_stores(tmp_path):
    server = FakeServer({URL: HELLO})
    result = fetch_resource(_resource(_hello()), tmp_path, opener=server)
    assert (tmp_path / "data" / "sample" / "hello.txt").read_bytes() == HELLO
    assert result.downloaded == ("hello.txt",)
    assert result.pinned == {}


def test_model_goes_to_models_directory(tmp_path):
    fetch_resource(_resource(_hello(), kind="model"), tmp_path, opener=FakeServer({URL: HELLO}))
    assert (tmp_path / "models" / "sample" / "hello.txt").exists()


@pytest.mark.parametrize(
    "payload",
    [b"hellO\n", b"hello", b"hello\n\n", b""],
    ids=["same-size-different", "shorter", "longer", "empty"],
)
def test_mismatch_is_refused_and_removed(tmp_path, payload):
    with pytest.raises(ChecksumError):
        fetch_resource(_resource(_hello()), tmp_path, opener=FakeServer({URL: payload}))
    directory = tmp_path / "data" / "sample"
    assert not (directory / "hello.txt").exists()
    assert _leftovers(tmp_path) == []


def test_interrupted_download_leaves_nothing(tmp_path):
    def opener(url: str) -> BrokenStream:
        return BrokenStream(HELLO)

    with pytest.raises(OSError, match="connection reset"):
        fetch_resource(_resource(_hello()), tmp_path, opener=opener)
    assert not (tmp_path / "data" / "sample" / "hello.txt").exists()
    assert _leftovers(tmp_path) == []


def test_verified_file_is_not_downloaded_again(tmp_path):
    fetch_resource(_resource(_hello()), tmp_path, opener=FakeServer({URL: HELLO}))
    server = FakeServer({})
    result = fetch_resource(_resource(_hello()), tmp_path, opener=server)
    assert server.requests == []
    assert result.present == ("hello.txt",)


def test_tampered_stored_file_is_reported(tmp_path):
    fetch_resource(_resource(_hello()), tmp_path, opener=FakeServer({URL: HELLO}))
    (tmp_path / "data" / "sample" / "hello.txt").write_bytes(b"HELLO\n")
    with pytest.raises(ChecksumError, match="SHA-256"):
        fetch_resource(_resource(_hello()), tmp_path, opener=FakeServer({}))
    assert "hello.txt" in verify_resource(_resource(_hello()), tmp_path)


@pytest.mark.parametrize(
    "digest",
    [("md5", MD5_HELLO), ("git-sha1", GIT_SHA1_HELLO)],
    ids=["md5", "git-sha1"],
)
def test_unpinned_file_needs_pin(tmp_path, digest):
    item = _hello(sha256=None, source_digest=digest)
    server = FakeServer({URL: HELLO})
    with pytest.raises(PinRequiredError):
        fetch_resource(_resource(item), tmp_path, opener=server)
    assert server.requests == []


@pytest.mark.parametrize(
    "digest",
    [("md5", MD5_HELLO), ("git-sha1", GIT_SHA1_HELLO)],
    ids=["md5", "git-sha1"],
)
def test_pin_verifies_source_digest_and_reports_sha256(tmp_path, digest):
    item = _hello(sha256=None, source_digest=digest)
    result = fetch_resource(_resource(item), tmp_path, pin=True, opener=FakeServer({URL: HELLO}))
    assert result.pinned == {"hello.txt": SHA256_HELLO}


@pytest.mark.parametrize(
    "digest",
    [("md5", "0" * 32), ("git-sha1", "0" * 40)],
    ids=["md5", "git-sha1"],
)
def test_pin_refuses_source_digest_mismatch(tmp_path, digest):
    item = _hello(sha256=None, source_digest=digest)
    with pytest.raises(ChecksumError, match="does not match the source"):
        fetch_resource(_resource(item), tmp_path, pin=True, opener=FakeServer({URL: HELLO}))
    assert not (tmp_path / "data" / "sample" / "hello.txt").exists()


def test_both_digests_must_match(tmp_path):
    item = _hello(source_digest=("md5", "0" * 32))
    with pytest.raises(ChecksumError, match="md5"):
        fetch_resource(_resource(item), tmp_path, opener=FakeServer({URL: HELLO}))


def _zip(members: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as bundle:
        for name, content in members.items():
            bundle.writestr(name, content)
    return buffer.getvalue()


ARCHIVE_URL = "https://example.org/corpus.zip"


def _archive_item(payload: bytes) -> ResourceFile:
    return ResourceFile(
        path="corpus.zip",
        url=ARCHIVE_URL,
        size=len(payload),
        sha256=hashlib.sha256(payload).hexdigest(),
        unpack="zip",
    )


def test_archive_is_unpacked_after_verification(tmp_path):
    payload = _zip({"corpus/train.txt": "Příliš žluťoučký kůň".encode()})
    item = _archive_item(payload)
    fetch_resource(_resource(item), tmp_path, opener=FakeServer({ARCHIVE_URL: payload}))
    extracted = tmp_path / "data" / "sample" / "corpus" / "corpus" / "train.txt"
    assert extracted.read_text(encoding="utf-8") == "Příliš žluťoučký kůň"


def test_archive_member_escaping_destination_is_refused(tmp_path):
    payload = _zip({"../../escaped.txt": b"x"})
    item = _archive_item(payload)
    with pytest.raises(ChecksumError, match="escapes"):
        fetch_resource(_resource(item), tmp_path, opener=FakeServer({ARCHIVE_URL: payload}))
    assert not list(tmp_path.rglob("escaped.txt"))
    assert not (tmp_path / "data" / "sample" / "corpus").exists()


def test_status_and_verify_report_missing_files(tmp_path):
    second = _hello(path="second.txt", url="https://example.org/second.txt")
    resource = _resource(_hello(), second)
    assert resource_status(resource, tmp_path) == "absent"
    fetch_resource(_resource(_hello()), tmp_path, opener=FakeServer({URL: HELLO}))
    assert resource_status(resource, tmp_path) == "partial"
    assert verify_resource(resource, tmp_path) == {"second.txt": "missing"}


def _catalog_with_requirement(base_file: ResourceFile) -> Catalog:
    base = _resource(base_file, kind="model")
    needed = Resource(**{**base.__dict__, "id": "needed", "files": (_hello(path="needed.txt"),)})
    top = Resource(**{**base.__dict__, "id": "top", "requires": ("needed",)})
    return Catalog({"needed": needed, "top": top})


def test_requirements_are_fetched_first_and_verified(tmp_path: Path):
    catalog = _catalog_with_requirement(_hello())
    server = FakeServer({URL: HELLO})
    results = fetch_with_requirements(catalog, "top", tmp_path, opener=server)
    assert [result.downloaded for result in results] == [("needed.txt",), ("hello.txt",)]
    assert (tmp_path / "models" / "needed" / "needed.txt").read_bytes() == HELLO
    assert (tmp_path / "models" / "top" / "hello.txt").read_bytes() == HELLO


def test_an_unpinned_file_refuses_before_any_download(tmp_path: Path):
    catalog = _catalog_with_requirement(_hello(sha256=None, source_digest=("md5", MD5_HELLO)))
    server = FakeServer({URL: HELLO})
    with pytest.raises(PinRequiredError, match="top"):
        fetch_with_requirements(catalog, "top", tmp_path, opener=server)
    assert server.requests == []


def test_a_trained_model_is_verified_but_never_downloaded(tmp_path: Path):
    trained = Resource(**{**_resource(_hello(url=None), kind="model").__dict__, "trained": True})
    server = FakeServer({})
    with pytest.raises(NotDownloadableError, match="trained on this machine"):
        fetch_resource(trained, tmp_path, opener=server)
    assert server.requests == []
    stored = tmp_path / "models" / "sample" / "hello.txt"
    stored.parent.mkdir(parents=True)
    stored.write_bytes(HELLO)
    assert fetch_resource(trained, tmp_path, opener=server).present == ("hello.txt",)
    stored.write_bytes(b"hellO\n")
    with pytest.raises(ChecksumError):
        fetch_resource(trained, tmp_path, opener=server)
