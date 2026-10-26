import json

import httpx
import pytest

from app.errors import PipelineError
from app.models import Sentence
from app.providers.ollama import OllamaProvider


def provider_with(handler, monkeypatch):
    def fake_post(url, json=None, timeout=None):
        return handler(url, json)

    monkeypatch.setattr(httpx, "post", fake_post)
    return OllamaProvider()


def reply(content):
    return httpx.Response(200, json={"message": {"content": content}}, request=httpx.Request("POST", "http://x"))


def test_request_shape_and_parse(monkeypatch):
    seen = {}

    def handler(url, body):
        seen.update(url=url, body=body)
        return reply(json.dumps({"id": 1, "text": "hola"}))

    out = provider_with(handler, monkeypatch).generate_json("sys", "hi", Sentence)
    assert out == Sentence(id=1, text="hola")
    assert seen["url"].endswith("/api/chat")
    assert seen["body"]["stream"] is False
    assert seen["body"]["format"]["title"] == "Sentence"
    assert seen["body"]["messages"][0]["role"] == "system"


def test_retries_once_on_invalid_json(monkeypatch):
    replies = iter(["not json", json.dumps({"id": 2, "text": "ok"})])
    out = provider_with(lambda u, b: reply(next(replies)), monkeypatch).generate_json("s", "p", Sentence)
    assert out.id == 2


def test_two_invalid_replies_is_provider_error(monkeypatch):
    with pytest.raises(PipelineError) as e:
        provider_with(lambda u, b: reply("nope"), monkeypatch).generate_json("s", "p", Sentence)
    assert e.value.code == "provider_error"


def test_image_is_unsupported(monkeypatch):
    with pytest.raises(PipelineError) as e:
        provider_with(lambda u, b: reply("{}"), monkeypatch).generate_json("s", "p", Sentence, image=b"x")
    assert e.value.code == "unsupported_in_mode"


def test_connection_error_is_provider_error(monkeypatch):
    def boom(u, b):
        raise httpx.ConnectError("down")

    with pytest.raises(PipelineError) as e:
        provider_with(boom, monkeypatch).generate_json("s", "p", Sentence)
    assert e.value.code == "provider_error"
