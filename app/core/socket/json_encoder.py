"""Custom JSON encoder for Socket.IO with Pydantic model support"""

import json
from typing import Any

from pydantic import BaseModel


class PydanticJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that automatically serializes Pydantic models"""

    def default(self, o: Any) -> Any:
        # Check if it's a Pydantic model
        if isinstance(o, BaseModel):
            return o.model_dump()
        # Fall back to default JSON encoder
        return super().default(o)


class PydanticJSON:
    """JSON module wrapper that uses PydanticJSONEncoder"""

    @staticmethod
    def dumps(obj: Any, **kwargs: Any) -> str:
        kwargs.setdefault("cls", PydanticJSONEncoder)
        return json.dumps(obj, **kwargs)

    @staticmethod
    def loads(s: str, **kwargs: Any) -> Any:
        return json.loads(s, **kwargs)
