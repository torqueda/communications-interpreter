"""Deterministic sentence splitter. Code numbers the sentences before any AI sees them."""
import re

# Abbreviations whose period must not end a sentence.
_ABBREVIATIONS = [
    "a.m.", "p.m.", "Dr.", "Mr.", "Mrs.", "Ms.", "St.", "Ave.", "Blvd.", "Rd.", "No.", "Nos.",
    "U.S.", "U.S.A.", "P.O.", "vs.", "etc.", "e.g.", "i.e.", "Inc.", "Co.", "Dept.", "Jan.", "Feb.",
    "Mar.", "Apr.", "Jun.", "Jul.", "Aug.", "Sep.", "Sept.", "Oct.", "Nov.", "Dec.", "Ext.", "Apt.",
]
_PLACEHOLDER = "․"  # one-dot leader, stands in for a protected period

_TERMINATORS = ".?!"
_BULLET = re.compile(r"^\s*([-*•]|\d+[.)])\s+")


def _protect(text: str) -> str:
    for abbr in _ABBREVIATIONS:
        text = re.sub(re.escape(abbr), abbr.replace(".", _PLACEHOLDER), text, flags=re.IGNORECASE)
    return text


def _join_wrapped_lines(text: str) -> list[str]:
    """Rebuild paragraphs: PDFs break lines mid-sentence, so join a line to the next one
    when it has no closing punctuation, the next line is not a bullet, and it is either
    long or the next line continues in lowercase."""
    units: list[str] = []
    for block in re.split(r"\n\s*\n", text.replace("\r\n", "\n").replace("\r", "\n")):
        current = ""
        for raw in block.split("\n"):
            line = raw.strip()
            if not line:
                continue
            if not current:
                current = line
                continue
            wrapped = (
                current[-1] not in _TERMINATORS + ":"
                and not _BULLET.match(line)
                and ((len(current) >= 30 and line[0].islower()) or len(current) >= 55)
            )
            if wrapped:
                current += " " + line
            else:
                units.append(current)
                current = line
        if current:
            units.append(current)
    return units


def split_sentences(text: str) -> list[str]:
    sentences: list[str] = []
    for unit in _join_wrapped_lines(text):
        protected = _protect(unit)
        parts = re.split(r'(?<=[.?!])["\')\]]*\s+(?=["\'(\[]?[A-Z0-9¿¡])', protected)
        for part in parts:
            part = re.sub(r"\s+", " ", part.replace(_PLACEHOLDER, ".")).strip()
            if part:
                sentences.append(part)
    return sentences
