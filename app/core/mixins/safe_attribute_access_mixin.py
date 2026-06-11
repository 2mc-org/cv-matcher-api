import typing
from collections.abc import Iterable
from typing import Any

from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.base import Mapped


def _safe_getattribute(self: Any, item: str) -> object:
    if item == "model_fields":
        # NOTE: The 'sqlmodel_update' method causes the PydanticDeprecatedSince211 warning:
        # Accessing the 'model_fields' attribute on the instance is deprecated.

        # Safely get model_fields from the class, or None if not present
        return getattr(self.__class__, "model_fields", None)

    try:
        # return super(type(self), self).__getattribute__(item)
        return object.__getattribute__(self, item)
    except InvalidRequestError:
        tp = self.__class__.__annotations__.get(item)
        if tp is not None and _is_iterable_mapped(tp):
            return []
        return None


def _is_iterable_mapped(tp: Any) -> bool:
    origin = typing.get_origin(tp)
    if origin is Mapped:
        args = typing.get_args(tp)
        if args:
            inner_type = args[0]
            inner_origin = typing.get_origin(inner_type)
            if inner_origin in (list, set, tuple):
                return True
            if (
                isinstance(inner_type, type)
                and issubclass(inner_type, Iterable)
                and not issubclass(inner_type, (str, bytes))
            ):
                return True
    return False


class SafeAttributeAccessMixin:
    """Mixin for SQLModel instances with lazy='raise' relationships.

      ``__getattribute__`` is attached in ``__init_subclass__`` so static analyzers
    (basedpyright/pyright) keep declared field types on subclasses instead of
      inferring a union from the hook body (``Any | list | None`` for every access).
    """

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        cls.__getattribute__ = _safe_getattribute  # type: ignore[method-assign]
