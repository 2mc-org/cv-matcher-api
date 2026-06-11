"""LangGraph checkpoint serde: JSON writes via extended JsonPlusSerializer."""

from __future__ import annotations

import json
import traceback
from datetime import date, datetime
from enum import Enum
from typing import Any
from uuid import UUID

from langchain_core.messages import BaseMessage, messages_to_dict
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.types import Interrupt
from pydantic import BaseModel

_JSON_TYPE = "json"


class _UseMsgpackFallback(Exception):
    """Signal from ``to_json_value`` that this write must use upstream msgpack."""


# For loads_typed only (legacy checkpoints written as msgpack + class extensions).
_LEGACY_ALLOWED_MSGPACK_MODULES: list[Any] = [
    # AsyncpgUUID,
    # ("app.job.models.base", "BaseJob"),
    # ("app.job.models.public", "JobPublic"),
    # ("app.job.models.base", "Job"),
    # ("app.client_identity.models.public", "ClientIdentityPublic"),
    # (
    #     "app.graph.job_page_handler.client_identify_graph.schemas.client_identity_schema",
    #     "ClientIdentitySchema",
    # ),
    # (
    #     "app.core.graphql.twenty.client.enums",
    #     "OpportunityProjectTypeEnum",
    # ),
]


def _exception_to_json(exc: BaseException) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "type": type(exc).__name__,
        "message": str(exc),
    }
    if exc.__traceback__ is not None:
        payload["traceback"] = "".join(
            traceback.format_exception(type(exc), exc, exc.__traceback__)
        )
    return payload


def to_json_value(value: Any) -> Any:
    """Recursively convert channel/checkpoint values to JSON-safe plain Python."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, Interrupt):
        raise _UseMsgpackFallback()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, BaseModel):
        return to_json_value(value.model_dump(mode="json"))
    if isinstance(value, BaseMessage):
        return messages_to_dict([value])[0]
    if isinstance(value, bytes):
        return value.decode("utf-8")
    if isinstance(value, dict):
        return {str(k): to_json_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_json_value(item) for item in value]
    if isinstance(value, BaseExceptionGroup):
        group_payload = _exception_to_json(value)
        group_payload["exceptions"] = [
            to_json_value(exc) for exc in value.exceptions
        ]
        return group_payload
    if isinstance(value, BaseException):
        return _exception_to_json(value)
    msg = f"Unsupported checkpoint value type: {type(value)!r}"
    raise TypeError(msg)


class GraphCheckpointJsonSerializer(JsonPlusSerializer):
    """JsonPlusSerializer that prefers ``json`` blobs for app/state types.

    ``Interrupt`` in the value tree raises ``_UseMsgpackFallback``; the whole write
    then uses upstream msgpack. Any other unsupported type raises ``TypeError``.
    """

    def __init__(self) -> None:
        super().__init__(
            allowed_msgpack_modules=_LEGACY_ALLOWED_MSGPACK_MODULES
        )

    def dumps_typed(self, obj: Any) -> tuple[str, bytes]:
        if obj is None or isinstance(obj, (bytes, bytearray)):
            return super().dumps_typed(obj)

        try:
            payload = json.dumps(
                to_json_value(obj),
                ensure_ascii=False,
            ).encode("utf-8")
        except _UseMsgpackFallback:
            return super().dumps_typed(obj)

        return _JSON_TYPE, payload
