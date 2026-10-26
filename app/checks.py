"""Plain-code grounding checks: no AI here. Proves cited sentences exist, dates line up,
and turns anything unconfirmed into verified=false."""
import re
from datetime import date

from app.models import Highlight, LetterResult, ReaderOutput, ScamCheck, Sentence, SummaryItem, VerifierOutput

MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august",
          "september", "october", "november", "december"]


def parse_deadline(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value.strip()[:10])
    except ValueError:
        return None


def date_appears_in(d: date, texts: list[str]) -> bool:
    """True if some text mentions this date as 'Month D', 'D Month', 'M/D', or ISO."""
    month = MONTHS[d.month - 1]
    short = month[:3]
    for text in texts:
        low = text.lower()
        if d.isoformat() in low:
            return True
        if re.search(rf"\b(?:{month}|{short}\.?)\s+{d.day}\b", low) or re.search(rf"\b{d.day}\s+(?:{month}|{short}\.?)\b", low):
            return True
        if re.search(rf"\b0?{d.month}[/-]0?{d.day}\b", low):
            return True
    return False


def _clean_highlights(reader: ReaderOutput, ids: set[int]) -> list[Highlight]:
    seen: set[int] = set()
    out: list[Highlight] = []
    for h in reader.highlights:
        if h.sentence_id in ids and h.sentence_id not in seen:
            seen.add(h.sentence_id)
            out.append(h)
    return out


def _clean_summary(items: list[SummaryItem], ids: set[int]) -> list[SummaryItem]:
    cleaned: list[SummaryItem] = []
    for item in items:
        valid = [i for i in dict.fromkeys(item.sentence_ids) if i in ids]
        grounded = len(valid) == len(set(item.sentence_ids)) and (bool(valid) or item.kind == "what")
        cleaned.append(item.model_copy(update={"sentence_ids": valid, "verified": item.verified and grounded}))
    return cleaned


def build_result(
    original: list[Sentence],
    reader: ReaderOutput,
    provider_name: str,
    image_source: bool = False,
    verifier: VerifierOutput | None = None,
    today: date | None = None,
) -> LetterResult:
    today = today or date.today()
    ids = {s.id for s in original}
    by_id = {s.id: s.text for s in original}

    highlights = _clean_highlights(reader, ids)
    summary = _clean_summary(reader.summary, ids)
    translation = [s for s in reader.translation if s.id in ids]
    scam = reader.scam

    deadline = parse_deadline(reader.deadline)
    if deadline:
        for i, item in enumerate(summary):
            if item.kind == "deadline" and item.verified:
                texts = [by_id[j] for j in item.sentence_ids]
                if not date_appears_in(deadline, texts):
                    summary[i] = item.model_copy(update={"verified": False})

    bad_translation: list[int] = []
    if verifier:
        highlights, summary, scam, bad_translation = apply_verifier(highlights, summary, scam, verifier, ids)

    passed = bool(deadline and deadline < today)
    warnings = []
    if passed:
        warnings.append("past_deadline")
    if reader.incomplete:
        warnings.append("incomplete")
    if image_source:
        warnings.append("image_source")

    return LetterResult(
        original=original,
        translation=translation,
        highlights=highlights,
        summary=summary,
        scam=scam,
        needs_action=reader.needs_action,
        deadline=deadline.isoformat() if deadline else None,
        deadline_passed=passed,
        warnings=warnings,
        incomplete_reason_es=reader.incomplete_reason_es,
        incomplete_reason_en=reader.incomplete_reason_en,
        unverified_translation_ids=bad_translation,
        provider=provider_name,
    )


def apply_verifier(highlights, summary, scam: ScamCheck, verifier: VerifierOutput, ids: set[int]):
    """Merge the Verifier's verdicts. Anything it did not confirm becomes verified=false."""
    verdicts = {item.ref.strip(): item for item in verifier.items}

    new_summary: list[SummaryItem] = []
    for i, item in enumerate(summary):
        v = verdicts.get(f"summary:{i}")
        if v is None or v.verdict == "unverified":
            item = item.model_copy(update={"verified": False})
        elif v.verdict == "fixed" and v.correction_es and v.correction_en:
            item = item.model_copy(update={"text_es": v.correction_es, "text_en": v.correction_en})
        elif v.verdict == "fixed":  # a fix was claimed but not provided: don't trust the text
            item = item.model_copy(update={"verified": False})
        new_summary.append(item)

    new_highlights = [
        h for h in highlights
        if not (verdicts.get(f"highlight:{h.sentence_id}") and verdicts[f"highlight:{h.sentence_id}"].verdict == "unverified")
    ]

    if verifier.scam_review == "disagree" and (verifier.scam_note_es or verifier.scam_note_en):
        # Keep the warning (or raise one) and show the Verifier's note as one more reason.
        scam = ScamCheck(
            flagged=True,
            reasons_es=[*scam.reasons_es, *([verifier.scam_note_es] if verifier.scam_note_es else [])],
            reasons_en=[*scam.reasons_en, *([verifier.scam_note_en] if verifier.scam_note_en else [])],
        )

    bad = sorted({i for i in verifier.translation_issues if i in ids})
    return new_highlights, new_summary, scam, bad
