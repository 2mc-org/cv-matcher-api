import uuid
from uuid import UUID

from sqlmodel import Field, SQLModel


class IdField(SQLModel):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    """UUID primary key with auto-generation"""
