"""Settings read from .env (never committed)."""
import os

from dotenv import load_dotenv

load_dotenv()


def provider_name() -> str:
    return os.getenv("PROVIDER", "gemini").strip().lower()


def gemini_key() -> str:
    return os.getenv("GEMINI_API_KEY", "").strip()


def gemini_model() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()


def ollama_url() -> str:
    return os.getenv("OLLAMA_URL", "http://localhost:11434").strip().rstrip("/")


def ollama_model() -> str:
    return os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct").strip()
