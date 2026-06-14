"""Parent graph input for resuming a CV search agent after an interrupt."""

from __future__ import annotations

from pydantic import BaseModel


class SubmitSearchCvExtraData(BaseModel):
    interrupt_id: str
    data: str
