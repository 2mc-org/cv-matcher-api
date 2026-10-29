"""CV snapshot JSON models (``sample_profiles.json`` or a private snapshot)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CvSnapshotProfile(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: str
    full_name: str = Field(alias="fullName")
    title: str
    description: str


class CvSnapshotCertificate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    description: str


class CvSnapshotEmployment(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    company_name: str = Field(alias="companyName")
    job_title: str = Field(alias="jobTitle")
    description: str


class CvSnapshotEntry(BaseModel):
    """One CV profile from a snapshot JSON file."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    profile: CvSnapshotProfile
    skills: list[str]
    certificates: list[CvSnapshotCertificate]
    employment_history: list[CvSnapshotEmployment] = Field(
        alias="employmentHistory",
    )
