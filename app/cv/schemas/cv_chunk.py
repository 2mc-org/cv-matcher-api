"""Chunk models for Qdrant ingest and retrieval."""

# from __future__ import annotations

import uuid
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, computed_field

from app.cv.enums.chunk_type import CvChunkType
from app.cv.schemas.cv_snapshot import (
    CvSnapshotCertificate,
    CvSnapshotEmployment,
    CvSnapshotEntry,
    CvSnapshotProfile,
)

type CvChunkPayload = Annotated[
    CvProfileChunkPayload
    | CvSkillsChunkPayload
    | CvEmploymentChunkPayload
    | CvCertificateChunkPayload,
    Field(discriminator="chunk_type"),
]

CV_CHUNK_PAYLOAD_ADAPTER: TypeAdapter[CvChunkPayload] = TypeAdapter(
    CvChunkPayload
)


class CvChunkPayloadBase(BaseModel):
    """Fields shared by every Qdrant point payload."""

    model_config = ConfigDict(extra="forbid")

    profile_id: str
    full_name: str

    @computed_field
    @property
    def point_id(self) -> uuid.UUID:
        digest_input = self.model_dump_json(
            exclude={"point_id"},
            ensure_ascii=False,
        )
        return uuid.uuid5(uuid.NAMESPACE_OID, digest_input)


class CvProfileChunkPayload(CvChunkPayloadBase):
    """Maps to ``CvSnapshotProfile`` (``title`` only; ``description`` excluded)."""

    chunk_type: Literal[CvChunkType.PROFILE] = CvChunkType.PROFILE
    title: str

    @classmethod
    def from_snapshot(cls, entry: CvSnapshotEntry) -> Self:
        profile = entry.profile
        return cls(
            profile_id=profile.id,
            full_name=profile.full_name,
            title=profile.title,
        )

    @property
    def text(self) -> str:
        return self.title


class CvSkillsChunkPayload(CvChunkPayloadBase):
    """Maps to ``CvSnapshotEntry.skills``."""

    chunk_type: Literal[CvChunkType.SKILLS] = CvChunkType.SKILLS
    skills: list[str]

    @classmethod
    def from_snapshot(cls, entry: CvSnapshotEntry) -> Self:
        profile = entry.profile
        return cls(
            profile_id=profile.id,
            full_name=profile.full_name,
            skills=entry.skills,
        )

    @property
    def text(self) -> str:
        return ", ".join(self.skills)


class CvEmploymentChunkPayload(CvChunkPayloadBase):
    """Maps to ``CvSnapshotEmployment``."""

    chunk_type: Literal[CvChunkType.EMPLOYMENT] = CvChunkType.EMPLOYMENT
    company_name: str
    job_title: str
    description: str

    @classmethod
    def from_snapshot(
        cls,
        profile: CvSnapshotProfile,
        employment: CvSnapshotEmployment,
    ) -> Self:
        return cls(
            profile_id=profile.id,
            full_name=profile.full_name,
            company_name=employment.company_name,
            job_title=employment.job_title,
            description=employment.description,
        )

    @property
    def text(self) -> str:
        return "\n".join(
            [
                f"Company: {self.company_name}",
                f"Job Title: {self.job_title}",
                f"Description: {self.description}",
            ],
        )


class CvCertificateChunkPayload(CvChunkPayloadBase):
    """Maps to ``CvSnapshotCertificate``."""

    chunk_type: Literal[CvChunkType.CERTIFICATE] = CvChunkType.CERTIFICATE
    name: str
    description: str

    @classmethod
    def from_snapshot(
        cls,
        profile: CvSnapshotProfile,
        certificate: CvSnapshotCertificate,
    ) -> Self:
        return cls(
            profile_id=profile.id,
            full_name=profile.full_name,
            name=certificate.name,
            description=certificate.description,
        )

    @property
    def text(self) -> str:
        return "\n".join(
            [
                f"Name: {self.name}",
                f"Description: {self.description}",
            ],
        )
