"""Shared helpers for LangGraph conditional-edge routing classes."""

from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass
from enum import StrEnum
from typing import ClassVar, cast


@dataclass(frozen=True, slots=True)
class RouteSpec:
    """One conditional branch: route key, target node (or END), Mermaid edge label."""

    route: StrEnum
    path: str
    edge_label: str


class ConditionalEdgeRouting:
    """Subclass declares nested ``Route`` + ``_SPECS``; base builds PATHS / EDGE_LABELS."""

    PATHS: ClassVar[dict[Hashable, str]]
    EDGE_LABELS: ClassVar[dict[StrEnum, str]]

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        specs: tuple[RouteSpec, ...] | None = cls.__dict__.get("_SPECS")
        if specs is None:
            return
        paths = {spec.route: spec.path for spec in specs}
        cls.PATHS = cast(dict[Hashable, str], paths)
        cls.EDGE_LABELS = {spec.route: spec.edge_label for spec in specs}
