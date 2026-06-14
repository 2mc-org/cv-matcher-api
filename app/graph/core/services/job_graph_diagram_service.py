from __future__ import annotations

import re
from collections.abc import Iterator
from functools import cache
from typing import ClassVar, Protocol, Self, cast

from langchain_core.runnables.graph import Graph as RunnableGraph
from langchain_core.runnables.graph import Node as RunnableNode
from langchain_core.runnables.graph_mermaid import draw_mermaid_png

from app.graph.core.types.compiled_graph import CompiledGraph


class _NestedGraphDrawable(Protocol):
    """Compiled graph API used for Mermaid xray expansion (not on PregelProtocol)."""

    def get_graph(self, *, xray: int | bool = False) -> RunnableGraph: ...

    def get_subgraphs(
        self,
        *,
        namespace: str | None = None,
        recurse: bool = False,
    ) -> Iterator[tuple[str, Self]]: ...


_ERROR_HANDLER_MARKER = "__error_handler__"


def _subgraph_drawable(
    compiled: _NestedGraphDrawable, *, xray: int
) -> RunnableGraph:
    """Prepare subgraph drawable for inlining (respects xray depth budget)."""
    return _expand_compiled_subgraph(compiled, xray=xray, depth_remaining=xray)


def _expand_compiled_subgraph(
    compiled: _NestedGraphDrawable,
    *,
    xray: int,
    depth_remaining: int,
) -> RunnableGraph:
    """Expand nested subgraphs only while depth budget remains."""
    drawable = compiled.get_graph(xray=xray)
    if depth_remaining <= 0:
        return drawable
    for child_name, child in compiled.get_subgraphs():
        child_drawable = _expand_compiled_subgraph(
            child,
            xray=xray,
            depth_remaining=depth_remaining - 1,
        )
        drawable = _inline_collapsed_subgraph(
            drawable,
            node_name=child_name,
            subgraph=child_drawable,
        )
    return drawable


@cache
def _parent_graph_edge_labels() -> dict[str, str]:
    """Lazy import: routing modules pull ServicesContainer if imported too early."""
    # isort: off
    from app.graph.error_guard.routing import ErrorsGuardRouting
    # isort: on

    return {
        route.value: label
        for labels in (ErrorsGuardRouting.EDGE_LABELS,)
        for route, label in labels.items()
    }


def _inline_collapsed_subgraph(
    parent: RunnableGraph,
    *,
    node_name: str,
    subgraph: RunnableGraph,
) -> RunnableGraph:
    """Replace a collapsed subgraph node when ``error_handler`` breaks LangGraph xray."""
    prefix = f"{node_name}:"
    if node_name not in parent.nodes or any(
        nid.startswith(prefix) for nid in parent.nodes
    ):
        return parent

    # Orphan nodes (no edges) break xray inlining; hide during inline, restore after.
    touched = {
        nid
        for edge in subgraph.edges
        for nid in (edge.source, edge.target)
        if nid in subgraph.nodes
    }
    orphans: list[tuple[str, RunnableNode]] = []
    for node_id in list(subgraph.nodes):
        if node_id in ("__start__", "__end__") or node_id in touched:
            continue
        orphans.append((node_id, subgraph.nodes.pop(node_id)))

    if len(subgraph.nodes) <= 1:
        for node_id, node in orphans:
            subgraph.nodes[node_id] = node
        return parent

    subgraph.trim_first_node()
    subgraph.trim_last_node()
    parent.nodes.pop(node_name, None)
    first, last = parent.extend(subgraph, prefix=node_name)

    entry_id = first.id if first is not None else f"{prefix}__start__"
    exit_id = last.id if last is not None else f"{prefix}__end__"

    for idx, edge in enumerate(parent.edges):
        if edge.source == node_name:
            edge = edge.copy(source=exit_id)
        if edge.target == node_name:
            edge = edge.copy(target=entry_id)
        parent.edges[idx] = edge

    for node_id, node in orphans:
        prefixed_id = f"{prefix}{node_id}"
        parent.nodes[prefixed_id] = RunnableNode(
            id=prefixed_id,
            name=node.name,
            data=node.data,
            metadata=node.metadata,
        )
    return parent


def _strip_error_handler_from_mermaid(mermaid: str) -> str:
    return "\n".join(
        line
        for line in mermaid.splitlines()
        if _ERROR_HANDLER_MARKER not in line
    )


_NODE_DEF_RE = re.compile(r"^(\s*)([\w]+)\((.+)\)(;?)\s*$")


def _sanitize_mermaid_node_labels(mermaid: str) -> str:
    """Mermaid.ink rejects node labels that contain unbalanced ``(`` inside ``id(label)``."""
    lines: list[str] = []
    for line in mermaid.splitlines():
        if "-->" in line or line.strip().startswith("classDef"):
            lines.append(line)
            continue
        match = _NODE_DEF_RE.match(line)
        if not match:
            lines.append(line)
            continue
        indent, node_id, label, semi = match.groups()
        label = label.replace("(", "«").replace(")", "»")
        lines.append(f"{indent}{node_id}({label}){semi}")
    return "\n".join(lines)


def _sanitize_mermaid_edge_labels(mermaid: str) -> str:
    """Colons inside ``-. |label| .->`` break Mermaid edge parsing."""
    return re.sub(
        r"(&nbsp;)([^&]+)(&nbsp;)",
        lambda match: (
            f"{match.group(1)}{match.group(2).replace(':', ' · ')}{match.group(3)}"
        ),
        mermaid,
    )


class JobGraphDiagramService:
    """Render LangGraph parent diagram as PNG (Mermaid via LangGraph)."""

    _MERMAID_METADATA_PREFIXES: ClassVar[tuple[str, ...]] = (
        "description",
        "step",
    )
    _LANGGRAPH_NODE_ID_RE: ClassVar[re.Pattern[str]] = re.compile(
        r"(?<![\w])([\w]+(?:\\3a[\w]+)+)(?![\w])"
    )

    def __init__(self, graph: CompiledGraph) -> None:
        self._graph = graph

    def render_parent_png(
        self, *, xray: int = 2, wrap_label_n_words: int = 6
    ) -> bytes:
        drawable = self._drawable_for_parent(xray=xray)
        mermaid = self._mermaid_syntax(
            drawable,
            wrap_label_n_words=wrap_label_n_words,
        )
        try:
            return draw_mermaid_png(mermaid_syntax=mermaid)
        except ValueError:
            if xray <= 0:
                raise
            fallback = self._graph.get_graph(xray=xray)
            mermaid = self._mermaid_syntax(
                fallback,
                wrap_label_n_words=wrap_label_n_words,
            )
            return draw_mermaid_png(mermaid_syntax=mermaid)

    def _mermaid_syntax(
        self,
        drawable: RunnableGraph,
        *,
        wrap_label_n_words: int,
    ) -> str:
        mermaid = drawable.draw_mermaid(wrap_label_n_words=wrap_label_n_words)
        mermaid = _strip_error_handler_from_mermaid(mermaid)
        for key in self._MERMAID_METADATA_PREFIXES:
            mermaid = mermaid.replace(f"{key} = ", "")
        mermaid = _sanitize_mermaid_node_labels(mermaid)
        mermaid = self._apply_mermaid_edge_labels(
            mermaid,
            _parent_graph_edge_labels(),
        )
        mermaid = _sanitize_mermaid_edge_labels(mermaid)
        mermaid = self._apply_mermaid_node_aliases(mermaid, drawable)
        mermaid = _sanitize_mermaid_node_labels(mermaid)
        mermaid = _sanitize_mermaid_edge_labels(mermaid)
        return mermaid

    def _drawable_for_parent(self, *, xray: int) -> RunnableGraph:
        drawable = self._graph.get_graph(xray=xray)
        if xray <= 0:
            return drawable
        # Match LangGraph: parent ``xray=N`` expands each subgraph with ``xray=N-1``.
        subgraph_xray = max(0, xray - 1)
        for node_name, compiled in self._graph.get_subgraphs():
            drawable = _inline_collapsed_subgraph(
                drawable,
                node_name=node_name,
                subgraph=_subgraph_drawable(
                    cast(_NestedGraphDrawable, compiled),
                    xray=subgraph_xray,
                ),
            )
        return drawable

    def _humanize_langgraph_node_id(self, escaped_id: str) -> tuple[str, str]:
        parts = escaped_id.replace("\\3a", ":").split(":")
        leaf = parts[-1]
        if len(parts) >= 2:
            parent = parts[-2].removesuffix("_graph")
            if parent == leaf or leaf in parent:
                return parent.replace("-", "_"), parent
            return (
                f"{parent}_{leaf}".replace("-", "_"),
                f"{parent} → {leaf}",
            )
        return leaf.replace("-", "_"), leaf

    def _apply_mermaid_edge_labels(
        self, mermaid: str, labels: dict[str, str]
    ) -> str:
        for route_key, display in labels.items():
            mermaid = mermaid.replace(
                f"&nbsp;{route_key}&nbsp;", f"&nbsp;{display}&nbsp;"
            )
        return mermaid

    def _apply_mermaid_node_aliases(
        self, mermaid: str, drawable: RunnableGraph
    ) -> str:
        found = set(self._LANGGRAPH_NODE_ID_RE.findall(mermaid))
        if not found:
            return mermaid

        alias_map: dict[str, tuple[str, str]] = {}
        used_ids: set[str] = set()
        for old_id in found:
            if _ERROR_HANDLER_MARKER in old_id:
                continue
            safe_id, label = self._humanize_langgraph_node_id(old_id)
            base = safe_id
            n = 2
            while safe_id in used_ids:
                safe_id = f"{base}_{n}"
                n += 1
            used_ids.add(safe_id)
            colon_id = old_id.replace("\\3a", ":")
            node = drawable.nodes.get(colon_id)
            meta = node.metadata if node and node.metadata else None
            caption = label
            if meta:
                inner = "<br/>".join(f"{k} = {v}" for k, v in meta.items())
                caption = f"{label}<hr/><small><em>{inner}</em></small>"
            alias_map[old_id] = (safe_id, caption)

        result = mermaid
        for old_id in sorted(alias_map, key=len, reverse=True):
            result = result.replace(old_id, alias_map[old_id][0])

        defined = set(re.findall(r"^\t([A-Za-z0-9_]+)\(", result, re.MULTILINE))
        inject = [
            f"\t{safe_id}({caption})\n"
            for safe_id, caption in alias_map.values()
            if safe_id not in defined
        ]
        if inject:
            marker = "classDef default"
            result = (
                result.replace(marker, "".join(inject) + marker, 1)
                if marker in result
                else result + "".join(inject)
            )
        return result
