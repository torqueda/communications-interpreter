import pymupdf
import pytest

from app.errors import PipelineError
from app.ingest import ingest


def make_pdf(text: str) -> bytes:
    doc = pymupdf.open()
    page = doc.new_page()
    if text:
        page.insert_textbox(pymupdf.Rect(54, 54, 558, 738), text, fontsize=11)
    return doc.tobytes()


def test_txt():
    out = ingest("a.txt", b"Please call us at once. Thank you very much.")
    assert out.kind == "text" and "call us" in out.text


def test_pdf_text_layer():
    out = ingest("a.pdf", make_pdf("Your coverage ends on November 30, 2026."))
    assert out.kind == "text" and "November 30" in out.text


def test_pdf_without_text_becomes_page_image():
    out = ingest("a.pdf", make_pdf(""))
    assert out.kind == "image" and out.page_image and out.image.startswith(b"\x89PNG")


def test_png_is_image():
    png = pymupdf.open().new_page().get_pixmap(dpi=20).tobytes("png")
    out = ingest("shot.png", png)
    assert out.kind == "image" and out.image_mime == "image/png"


@pytest.mark.parametrize("name,data", [("a.txt", b""), ("a.txt", b"  \n "), ("a.docx", b"PK123"), ("a.pdf", b"not a pdf")])
def test_cannot_read(name, data):
    with pytest.raises(PipelineError) as e:
        ingest(name, data)
    assert e.value.code == "cannot_read"
