"""Routing actions produced by classify_intent."""

from __future__ import annotations

from enum import StrEnum


class CvSearchIntentRoute(StrEnum):
    VALIDATION_ERROR = "intent:validation_error"
    OFF_TOPIC_ERROR = "intent:off_topic_error"
    RAG_SEARCH = "intent:rag_search"
    ANSWER = "intent:answer"
