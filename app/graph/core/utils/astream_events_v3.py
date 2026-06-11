from __future__ import annotations

from collections.abc import AsyncIterator, Callable, Sequence
from typing import TYPE_CHECKING, Any, cast

from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
from langgraph.runtime import RunControl
from langgraph.stream.run_stream import (
    AsyncGraphRunStream as _AsyncGraphRunStream,
)
from langgraph.types import All, Command
from pydantic import BaseModel

if TYPE_CHECKING:

    class AsyncGraphRunStream[StateT](_AsyncGraphRunStream):
        async def output(  # pyright: ignore[reportIncompatibleMethodOverride]
            self,
        ) -> StateT | None: ...

        @property
        def values(self) -> AsyncIterator[StateT]: ...

else:
    AsyncGraphRunStream = _AsyncGraphRunStream


async def astream_events_v3[
    StateT: BaseModel,
    ContextT: BaseModel | None,
    InputT: BaseModel,
    OutputT: BaseModel,
](
    graph: CompiledStateGraph[StateT, ContextT, InputT, OutputT],
    input: InputT | Command | None,
    config: RunnableConfig | None = None,
    *,
    context: ContextT | None = None,
    interrupt_before: All | Sequence[str] | None = None,
    interrupt_after: All | Sequence[str] | None = None,
    control: RunControl | None = None,
    transformers: Sequence[Callable[[tuple[str, ...]], Any]] | None = None,
    **kwargs: Any,
) -> AsyncGraphRunStream[OutputT]:
    stream = await graph.astream_events(
        input,
        config,
        version="v3",
        context=context,
        interrupt_before=interrupt_before,
        interrupt_after=interrupt_after,
        control=control,
        transformers=transformers,
        **kwargs,
    )
    return cast(Any, stream)
