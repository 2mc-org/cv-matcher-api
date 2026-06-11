from typing import Literal

from pydantic import BaseModel, Field

SioFormat = Literal["text", "markdown", "json"]


class SioEventBase(BaseModel):
    format: SioFormat = Field(
        default="text", description="Response format type"
    )
    model: str | None = Field(
        default=None, description="Schema name for json payload"
    )
