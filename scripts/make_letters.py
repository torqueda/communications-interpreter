"""Render the .txt test letters in test_letters/ into PDFs (and a PNG screenshot) with PyMuPDF."""
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parent.parent / "test_letters"


def render_pdf(text: str, out: Path) -> None:
    doc = pymupdf.open()
    rect = pymupdf.Rect(54, 54, 558, 738)
    remaining = text
    while remaining:
        page = doc.new_page()
        used = page.insert_textbox(rect, remaining, fontsize=11, fontname="helv")
        if used >= 0:
            break
        # Overflowed: write what fits by lines, then continue on the next page.
        lines = remaining.split("\n")
        fit = len(lines)
        while fit > 1:
            probe = pymupdf.open().new_page()
            if probe.insert_textbox(rect, "\n".join(lines[:fit]), fontsize=11, fontname="helv") >= 0:
                break
            fit -= 1
        page.clean_contents()
        remaining = "\n".join(lines[fit:])
    doc.save(out)


def render_png(text: str, out: Path) -> None:
    doc = pymupdf.open()
    page = doc.new_page(width=420, height=560)
    page.insert_textbox(pymupdf.Rect(24, 24, 396, 536), text, fontsize=11, fontname="helv")
    page.get_pixmap(dpi=130).save(out)


def render_scanned_pdf(text: str, out: Path) -> None:
    """A PDF that is only a picture of the page (no text layer), like a scan."""
    page_png = pymupdf.open().new_page(width=595, height=842)
    page_png.insert_textbox(pymupdf.Rect(54, 54, 541, 788), text, fontsize=11, fontname="helv")
    pix = page_png.get_pixmap(dpi=130)
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    page.insert_image(page.rect, stream=pix.tobytes("png"))
    doc.save(out)


def main() -> None:
    for txt in sorted(ROOT.glob("*.txt")):
        body = txt.read_text(encoding="utf-8")
        if txt.stem.endswith("_scan"):
            render_scanned_pdf(body, txt.with_suffix(".pdf"))
        else:
            render_pdf(body, txt.with_suffix(".pdf"))
        if txt.stem.endswith("_shot"):
            render_png(body, txt.with_suffix(".png"))
        print("rendered", txt.stem)


if __name__ == "__main__":
    main()
