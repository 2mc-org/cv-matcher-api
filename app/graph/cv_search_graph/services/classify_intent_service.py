"""Service for the ``classify_intent`` node: structured intent classification."""

from __future__ import annotations

import logging

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import SecretStr

from app.core.environments import environments
from app.graph.core.states.graph_state import GraphState
from app.graph.cv_search_graph.prompts.classify import (
    get_classify_system_prompt,
    get_classify_user_prompt,
)
from app.graph.cv_search_graph.schemas.cv_search_intent_schema import (
    CvSearchIntent,
)

logger = logging.getLogger(__name__)


class ClassifyIntentService:
    def __init__(self) -> None:
        self._router = ChatAnthropic(
            model_name="claude-haiku-4-5",
            api_key=SecretStr(environments.ANTHROPIC_API_KEY),
            temperature=0,
            timeout=None,
            stop=None,
        ).with_structured_output(CvSearchIntent)

    async def classify(
        self,
        state: GraphState,
        user_message: str,
    ) -> CvSearchIntent:
        try:
            result = await self._router.ainvoke(
                [
                    SystemMessage(content=get_classify_system_prompt()),
                    HumanMessage(
                        content=get_classify_user_prompt(state, user_message),
                    ),
                ],
            )
        except Exception as e:
            logger.error("classify_intent error: %s", e, exc_info=True)
            raise

        return CvSearchIntent.model_validate(result)
