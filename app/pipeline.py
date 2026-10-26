"""ingest → segment → reader → (verifier) → checks. Nothing is kept after the request."""
from datetime import date

from app.agents.reader import run_reader
from app.errors import PipelineError
from app.ingest import ingest
from app.agents.verifier import run_verifier
from app.checks import build_result
from app.models import LetterResult, number_sentences
from app.segment import split_sentences


def run_pipeline(filename: str, data: bytes, provider, today: date | None = None) -> LetterResult:
    ingested = ingest(filename, data)

    if ingested.kind == "image":
        if provider.name != "gemini":
            raise PipelineError("unsupported_in_mode", "image reading needs Gemini mode")
        original = None
        reader = run_reader(provider, None, image=ingested.image, image_mime=ingested.image_mime)
        original = reader.transcribed or []
    else:
        original = number_sentences(split_sentences(ingested.text))
        if not original:
            raise PipelineError("cannot_read", "no sentences")
        reader = run_reader(provider, original)

    if not reader.is_letter or not reader.language.lower().startswith("en"):
        raise PipelineError("cannot_read", f"not an English letter ({reader.language})")
    if not original:
        raise PipelineError("cannot_read", "nothing transcribed")

    verifier = run_verifier(provider, original, reader, image=ingested.image, image_mime=ingested.image_mime)
    return build_result(original, reader, provider.name, image_source=ingested.kind == "image", verifier=verifier, today=today)
