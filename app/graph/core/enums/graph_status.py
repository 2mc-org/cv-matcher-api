from enum import StrEnum


class GraphStatus(StrEnum):
    """Lifecycle status for a graph."""

    QUEUED = "queued"
    """Graph run not started yet (or not picked up after restart)."""

    RUNNING = "running"
    """Graph is executing."""

    AWAITING_CUSTOMER = "awaiting_customer"
    """Graph finished with blocking questions; manager must collect customer replies."""

    COMPLETED = "completed"
    """Graph finished successfully with output ready."""

    FAILED = "failed"
    """Graph ended with an error; details may be logged separately."""

    CANCELLED = "cancelled"
    """Soft-cancelled via API; no further mutations on this job."""
