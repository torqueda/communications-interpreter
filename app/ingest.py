"""File type detection and text extraction."""
from dataclasses import dataclass

import pymupdf  # PyMuPDF

from app.errors import PipelineError

MIN_TEXT_CHARS = 20


@dataclass
class Ingested:
    kind: str  # "text" or "image"
    text: str = ""
    image: bytes | None = None
    image_mime: str = ""
    page_image: bool = False  # image rendered from a PDF with no text layer


def _kind_of(filename: str, data: bytes) -> str:
    name = (filename or "").lower()
    if data[:5] == b"%PDF-" or name.endswith(".pdf"):
        return "pdf"
    if data[:8] == b"\x89PNG\r\n\x1a\n" or name.endswith(".png"):
        return "png"
    if data[:3] == b"\xff\xd8\xff" or name.endswith((".jpg", ".jpeg")):
        return "jpg"
    if name.endswith(".txt"):
        return "txt"
    raise PipelineError("cannot_read", "unsupported file type")


def ingest(filename: str, data: bytes) -> Ingested:
    if not data:
        raise PipelineError("cannot_read", "empty file")
    kind = _kind_of(filename, data)

    if kind == "txt":
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = data.decode("latin-1")
        return _require_text(text)

    if kind in ("png", "jpg"):
        return Ingested(kind="image", image=data, image_mime="image/png" if kind == "png" else "image/jpeg")

    try:
        doc = pymupdf.open(stream=data, filetype="pdf")
    except Exception as exc:  # corrupt or encrypted
        raise PipelineError("cannot_read", f"bad PDF: {exc}") from exc
    text = "\n".join(page.get_text("text") for page in doc)
    if len(text.strip()) >= MIN_TEXT_CHARS:
        return Ingested(kind="text", text=text)
    if len(doc) == 0:
        raise PipelineError("cannot_read", "empty PDF")
    # No text layer: a scanned letter. Render page 1 so an image-capable reader can transcribe it.
    pix = doc[0].get_pixmap(dpi=150)
    return Ingested(kind="image", image=pix.tobytes("png"), image_mime="image/png", page_image=True)


def _require_text(text: str) -> Ingested:
    if len(text.strip()) < MIN_TEXT_CHARS:
        raise PipelineError("cannot_read", "no usable text")
    return Ingested(kind="text", text=text)
