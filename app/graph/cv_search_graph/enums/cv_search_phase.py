"""Routing phase for one CV search turn (``cv_search_phase``)."""

from __future__ import annotations

from enum import StrEnum


class CvSearchPhase(StrEnum):
    SEARCH = "search"
    FOLLOW_UP = "follow_up"
