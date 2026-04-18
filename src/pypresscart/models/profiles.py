"""Profile models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import field_validator

from pypresscart.models._common import PresscartModel


class Profile(PresscartModel):
    """Record returned by ``GET /teams/{team_id}/profiles``."""

    id: str
    name: str | None = None
    legal_company_name: str | None = None
    type: str | None = None
    logo: str | None = None
    location: str | None = None
    overview: str | None = None
    products_and_services: str | None = None
    google_drive_link: str | None = None
    writing_samples: str | None = None
    primary_goals: list[str] = []
    website_url: str | None = None
    team_id: str | None = None
    brand_tone_and_voice_id: str | None = None
    last_generated_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    @field_validator("primary_goals", mode="before")
    @classmethod
    def _accept_pg_or_json_array(cls, v: Any) -> Any:
        """Accept both JSON arrays and Postgres-array literals.

        The Presscart API currently returns ``primary_goals`` as a Postgres
        array literal (``"{A,B,C}"``) instead of the JSON array (``["A","B","C"]``)
        promised by the public docs. This validator normalizes both shapes so
        the field always ends up as a ``list[str]``:

            ``["A", "B"]``      → passed through as a list
            ``"{A,B}"``         → parsed to ``["A", "B"]``
            ``"{}"`` / ``""``   → ``[]``
            anything else       → left alone (Pydantic will raise)

        This is a server-side bug on Presscart's side (tracked as issue #2
        on the repo). Once the API is corrected, this validator becomes a
        no-op for the JSON path and can be removed.
        """
        if v is None:
            return []
        if isinstance(v, str):
            s = v.strip()
            if not s:
                return []
            if s.startswith("{") and s.endswith("}"):
                inner = s[1:-1].strip()
                if not inner:
                    return []
                return [item.strip().strip('"') for item in inner.split(",")]
        return v


__all__ = ["Profile"]
