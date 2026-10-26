"""Gemini through the google-genai SDK, with structured JSON output and image input."""
from google import genai
from google.genai import types
from pydantic import BaseModel

from app import config
from app.errors import PipelineError
from app.providers.base import parse_or_none

TIMEOUT_MS = 90_000


class GeminiProvider:
    name = "gemini"

    def __init__(self) -> None:
        key = config.gemini_key()
        if not key:
            raise PipelineError("provider_error", "GEMINI_API_KEY is not set")
        self.client = genai.Client(api_key=key, http_options=types.HttpOptions(timeout=TIMEOUT_MS))
        self.model = config.gemini_model()

    def generate_json(self, system, prompt, schema: type[BaseModel], image=None, image_mime="image/png"):
        parts: list = []
        if image is not None:
            parts.append(types.Part.from_bytes(data=image, mime_type=image_mime))
        parts.append(prompt)
        cfg = types.GenerateContentConfig(
            system_instruction=system,
            response_mime_type="application/json",
            response_schema=schema,
            temperature=0.1,
        )
        for attempt in (1, 2):  # retry once on invalid JSON
            try:
                resp = self.client.models.generate_content(model=self.model, contents=parts, config=cfg)
            except Exception as exc:
                raise PipelineError("provider_error", f"Gemini call failed: {exc}") from exc
            parsed = parse_or_none(schema, resp.text or "")
            if parsed is not None:
                return parsed
        raise PipelineError("provider_error", "Gemini returned invalid JSON twice")
