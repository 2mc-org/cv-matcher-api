"""Routing actions produced by classify_intent."""

from __future__ import annotations

from enum import StrEnum


class CvSearchIntentRoute(StrEnum):
    VALIDATION_ERROR = "intent:validation_error"
    OFF_TOPIC_ERROR = "intent:off_topic_error"
    MATCH_PROFILES = "intent:match_profiles"
    FOLLOW_UP = "intent:follow_up"
