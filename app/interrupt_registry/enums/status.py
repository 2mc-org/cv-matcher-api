from enum import StrEnum


class InterruptRegistryStatus(StrEnum):
    """Resume lifecycle for a registered graph interrupt."""

    PENDING = "pending"
    CONSUMED = "consumed"
