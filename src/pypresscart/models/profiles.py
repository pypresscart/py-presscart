"""Profile models."""

from __future__ import annotations

from datetime import datetime

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


__all__ = ["Profile"]
