from typing import Any, cast

from sqlmodel import SQLModel

UNSET = object()


def clone_field[T: SQLModel](model: type[T], set_default: Any = UNSET) -> Any:
    # Create a temporary subclass to trigger __init_subclass__
    TempSubclass = cast(type[T], type("TempSubclass", (model,), {}))

    # Get the field name from the original model
    field_name = next(iter(model.model_fields.keys()))

    # Get the field from the temporary subclass (after __init_subclass__ has run)
    field_info = TempSubclass.model_fields[field_name]

    if set_default is not UNSET and set_default is not Ellipsis:
        field_info.default = set_default
        field_info.default_factory = None

    return field_info
