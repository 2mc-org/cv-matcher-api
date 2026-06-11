from abc import ABC
from typing import ClassVar

from pydantic import ValidationInfo, field_validator


class NotNullMixin(ABC):
    not_null_fields: ClassVar[list[str]] = []

    @field_validator("*", mode="before")
    @classmethod
    def not_null_validator[T](cls, value: T, info: ValidationInfo) -> T:
        not_null_fields = getattr(cls, "not_null_fields", [])
        is_field_included = info.field_name in not_null_fields
        is_value_none = value is None

        if is_field_included and is_value_none:
            raise ValueError(f"Field '{info.field_name}' cannot be null.")
        return value
