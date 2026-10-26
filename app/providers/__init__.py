from app import config
from app.errors import PipelineError


def get_provider():
    name = config.provider_name()
    if name == "gemini":
        from app.providers.gemini import GeminiProvider

        return GeminiProvider()
    if name == "ollama":
        from app.providers.ollama import OllamaProvider

        return OllamaProvider()
    raise PipelineError("provider_error", f"unknown PROVIDER '{name}'")
