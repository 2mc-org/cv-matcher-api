"""Service for the ``match_profiles`` node: cv_search tool + profile ranking."""

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
from app.graph.cv_search_graph.prompts.match_profiles import (
    get_match_profiles_system_prompt,
    get_match_profiles_user_prompt,
)
from app.graph.cv_search_graph.schemas.cv_profile_match_schema import (
    CvProfileMatchResult,
)
from app.graph.cv_search_graph.tools.cv_search_tool import build_cv_search_tool

logger = logging.getLogger(__name__)


class ProfileMatchService:
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
            response_format=CvProfileMatchResult,
        )

    async def match(
        self,
        state: GraphState,
        user_message: str,
    ) -> CvProfileMatchResult:
        try:
            result = await self._agent.ainvoke(
                {
                    "messages": [
                        SystemMessage(
                            content=get_match_profiles_system_prompt()
                        ),
                        HumanMessage(
                            content=get_match_profiles_user_prompt(
                                user_message
                            ),
                        ),
                    ],
                },
                version="v2",
            )
        except Exception as e:
            logger.error("match_profiles error: %s", e, exc_info=True)
            raise

        return parse_structured_result(result.value)
