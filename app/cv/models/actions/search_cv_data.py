"""Parent graph input for starting a CV search agent run."""

from __future__ import annotations

from pydantic import BaseModel


class SearchCvData(BaseModel):
    thread_id: str
    message: str
