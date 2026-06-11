from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute

from app.core.socket.events.interrupt import SioInterruptEvent
from app.core.socket.events.message import SioEvent


def add_component_schema(schemas: dict[str, Any], model: type) -> None:
    schema = model.model_json_schema(
        ref_template="#/components/schemas/{model}"
    )
    schemas.update(schema.pop("$defs", {}))
    schemas[model.__name__] = schema


def generate_operation_id(route: APIRoute) -> str:
    """Generate stable operationId for OpenAPI schema."""
    tag_part = route.tags[0] if route.tags else "default"
    name_part = (
        route.name or route.path_format.strip("/").replace("/", "_") or "root"
    )
    # return f"{route.name}"
    return f"{tag_part}_{name_part}"


class CustomFastAPI(FastAPI):
    """FastAPI application with extended OpenAPI schema."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize FastAPI application with custom OpenAPI and operationId generator."""
        kwargs.setdefault("generate_unique_id_function", generate_operation_id)
        super().__init__(*args, **kwargs)

    def openapi(self) -> dict[str, Any]:
        """Generate OpenAPI schema with additional components (e.g. WebSocket models)."""
        if self.openapi_schema:
            return self.openapi_schema

        openapi_schema = get_openapi(
            title=self.title,
            version=self.version,
            description=self.description,
            routes=self.routes,
        )

        components = openapi_schema.setdefault("components", {})
        schemas = components.setdefault("schemas", {})

        add_component_schema(schemas, SioEvent)
        add_component_schema(schemas, SioInterruptEvent)

        self.openapi_schema = openapi_schema
        return openapi_schema
