"""Ollama (local, free) over its HTTP API with structured output. Text only."""
import httpx
from pydantic import BaseModel

from app import config
from app.errors import PipelineError
from app.providers.base import parse_or_none

TIMEOUT_S = 480  # a local 7B model is far slower than Gemini (about 3 minutes per call on this laptop)


class OllamaProvider:
    name = "ollama"

    def __init__(self) -> None:
        self.url = config.ollama_url()
        self.model = config.ollama_model()

    def generate_json(self, system, prompt, schema: type[BaseModel], image=None, image_mime="image/png"):
        if image is not None:
            raise PipelineError("unsupported_in_mode", "image reading needs Gemini mode")
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            "format": schema.model_json_schema(),
            "stream": False,
            "options": {"temperature": 0.1, "num_ctx": 8192},
        }
        for attempt in (1, 2):  # retry once on invalid JSON
            try:
                resp = httpx.post(f"{self.url}/api/chat", json=payload, timeout=TIMEOUT_S)
                resp.raise_for_status()
                content = resp.json()["message"]["content"]
            except (httpx.HTTPError, KeyError, ValueError) as exc:
                raise PipelineError("provider_error", f"Ollama call failed: {exc}") from exc
            parsed = parse_or_none(schema, content)
            if parsed is not None:
                return parsed
        raise PipelineError("provider_error", "Ollama returned invalid JSON twice")
