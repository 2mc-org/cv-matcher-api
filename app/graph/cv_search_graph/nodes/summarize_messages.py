"""Summarize ``cv_search_messages`` via langmem ``asummarize_messages``."""

from __future__ import annotations

from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_core.messages.utils import count_tokens_approximately
from langmem.short_term import asummarize_messages
from pydantic import SecretStr

from app.core.environments import environments
from app.graph.core.states.graph_state import GraphState

summarization_model = ChatAnthropic(
    model_name="claude-haiku-4-5",
    api_key=SecretStr(environments.ANTHROPIC_API_KEY),
    temperature=0,
    timeout=None,
    stop=None,
).bind(max_tokens=500)


async def summarize_messages(state: GraphState) -> dict[str, Any]:
    result = await asummarize_messages(
        state.cv_search_messages,
        running_summary=state.cv_search_running_summary,
        model=summarization_model,
        max_tokens=1500,
        max_tokens_before_summary=3000,
        max_summary_tokens=500,
        token_counter=count_tokens_approximately,
    )
    if result.running_summary is not None:
        return state.with_updates(
            GraphState(
                cv_search_summarized_messages=result.messages,
                cv_search_running_summary=result.running_summary,
            ),
        )
    return state.with_updates(
        GraphState(cv_search_summarized_messages=result.messages),
    )
