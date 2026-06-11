from enum import StrEnum


class CvChunkType(StrEnum):
    """Semantic section stored as one Qdrant point."""

    PROFILE = "profile"
    SKILLS = "skills"
    EMPLOYMENT = "employment"
    CERTIFICATE = "certificate"
