"""Shared fixtures for live-API integration tests.

Every test module in this package is marked ``integration`` and pulls the
:func:`live_client` fixture. If ``PRESSCART_API_TOKEN`` is not set (directly
or via ``tests/integration/.env.local``), the fixture raises ``pytest.skip``
so the whole module is cleanly skipped — CI stays green without a token.

Run them manually once you have a token:

    export PRESSCART_API_TOKEN=pc_...
    uv run pytest -m integration -v -s
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import pytest

from pypresscart import PresscartClient


def _load_env_local(path: Path) -> None:
    """Tiny .env loader so we don't add python-dotenv as a dep."""
    if not path.exists():
        return
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


# Load once at import time so that every fixture/test sees the same env.
_load_env_local(Path(__file__).resolve().parent / ".env.local")


@pytest.fixture(scope="session")
def api_token() -> str:
    """Skip the integration suite if no token is available."""
    token = os.environ.get("PRESSCART_API_TOKEN")
    if not token:
        pytest.skip(
            "PRESSCART_API_TOKEN not set; set it in the environment or in "
            "tests/integration/.env.local to run integration tests.",
            allow_module_level=True,
        )
    return token


@pytest.fixture(scope="session")
def live_client(api_token: str) -> Iterator[PresscartClient]:
    """One PresscartClient shared across the whole integration session."""
    client = PresscartClient(api_token=api_token)
    try:
        yield client
    finally:
        client.close()
