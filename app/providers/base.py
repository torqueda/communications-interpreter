import json
from typing import Protocol

from pydantic import BaseModel, ValidationError


class Provider(Protocol):
    name: str

    def generate_json(
        self,
        system: str,
        prompt: str,
        schema: type[BaseModel],
        image: bytes | None = None,
        image_mime: str = "image/png",
    ) -> BaseModel: ...


def parse_or_none(schema: type[BaseModel], raw: str) -> BaseModel | None:
    """Validate raw model output against the schema; None if it is not valid."""
    try:
        return schema.model_validate(json.loads(raw))
    except (ValueError, ValidationError):
        return None
