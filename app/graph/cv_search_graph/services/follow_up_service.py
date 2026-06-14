"""Service for the ``follow_up`` node: answer about shortlist with optional lookups."""

from __future__ import annotations

import logging

from langchain.agents import create_agent
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import SecretStr

from app.core.environments import environments
from app.cv.services.cv_search_service import CvSearchService
from app.graph.core.states.graph_state import GraphState
from app.graph.core.utils.parse_structured_result import parse_structured_result
from app.graph.cv_search_graph.prompts.follow_up import (
    get_follow_up_system_prompt,
    get_follow_up_user_prompt,
)
from app.graph.cv_search_graph.schemas.cv_follow_up_schema import (
    CvFollowUpResult,
)
from app.graph.cv_search_graph.tools.cv_search_tool import build_cv_search_tool

logger = logging.getLogger(__name__)


class FollowUpService:
    def __init__(self, cv_search_service: CvSearchService) -> None:
        self._agent = create_agent(
            model=ChatAnthropic(
                model_name="claude-haiku-4-5",
                api_key=SecretStr(environments.ANTHROPIC_API_KEY),
                temperature=0,
                timeout=None,
                stop=None,
            ),
            tools=[build_cv_search_tool(cv_search_service)],
            response_format=CvFollowUpResult,
        )

    async def answer(
        self,
        state: GraphState,
        user_message: str,
    ) -> CvFollowUpResult:
        try:
            result = await self._agent.ainvoke(
                {
                    "messages": [
                        SystemMessage(content=get_follow_up_system_prompt()),
                        *state.cv_search_summarized_messages,
                        HumanMessage(
                            content=get_follow_up_user_prompt(
                                state, user_message
                            ),
                        ),
                    ],
                },
                version="v2",
            )
        except Exception as e:
            logger.error("follow_up error: %s", e, exc_info=True)
            raise

        return parse_structured_result(result.value)
