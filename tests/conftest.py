"""Fixtures shared by every test."""

from collections.abc import Iterator

import pytest
from anonymizer.core.log import reset_logging


@pytest.fixture(autouse=True)
def _undo_logging_setup() -> Iterator[None]:
    """Undo `configure_logging`, which the commands call, so no test inherits its handlers."""
    yield
    reset_logging()
