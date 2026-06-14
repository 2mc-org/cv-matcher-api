"""Parse structured output from LangChain agents."""

from __future__ import annotations

from langchain.agents.middleware.types import _OutputAgentState
from pydantic import BaseModel


def parse_structured_result[ResponseT: BaseModel](
    result: _OutputAgentState[ResponseT],
) -> ResponseT:
    structured = result.get("structured_response")
    if structured is None:
        msg = "Agent missing structured_response"
        raise ValueError(msg)

    return structured
