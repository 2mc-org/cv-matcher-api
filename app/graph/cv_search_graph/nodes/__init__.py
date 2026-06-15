from enum import StrEnum


class CvSearchNodes(StrEnum):
    RESOLVE_PHASE = "resolve_phase"
    SUMMARIZE_MESSAGES = "summarize_messages"
    CLASSIFY_INTENT = "classify_intent"
    REJECT_INTENT = "reject_intent"
    MATCH_PROFILES = "match_profiles"
    FOLLOW_UP = "follow_up"
    FINALIZE_RESPONSE = "finalize_response"
