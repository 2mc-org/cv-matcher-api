"""Routing actions produced by classify_intent."""

from __future__ import annotations

from enum import StrEnum


class CvSearchIntentRoute(StrEnum):
    VALIDATION_ERROR = "validation_error"
    OFF_TOPIC_ERROR = "off_topic_error"
    RAG_SEARCH = "rag_search"
    ANSWER = "answer"
