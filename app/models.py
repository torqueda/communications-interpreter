"""Pydantic models: every agent output and the API response. They double as the JSON schema
the AI models must follow."""
from typing import Literal

from pydantic import BaseModel, Field

HighlightKind = Literal["deadline", "action", "docs", "contact", "flag"]
SummaryKind = Literal["what", "action", "deadline", "docs", "contact", "flag"]


class Sentence(BaseModel):
    id: int
    text: str


def number_sentences(texts: list[str]) -> list[Sentence]:
    return [Sentence(id=i, text=t) for i, t in enumerate(texts, start=1)]


class Highlight(BaseModel):
    sentence_id: int
    kind: HighlightKind


class SummaryItem(BaseModel):
    kind: SummaryKind
    text_es: str
    text_en: str
    sentence_ids: list[int]
    verified: bool = True


class ScamCheck(BaseModel):
    flagged: bool
    reasons_es: list[str]
    reasons_en: list[str]


class ReaderOutput(BaseModel):
    language: str = Field(description="Language the ORIGINAL letter is written in, e.g. 'English' or 'French' (not the language of your answer)")
    is_letter: bool = Field(description="True for any letter, notice, bill or reminder. False ONLY if clearly not a letter at all")
    transcribed: list[Sentence] | None = Field(
        description="Only for image input: the letter transcribed into numbered sentences. Otherwise null."
    )
    translation: list[Sentence]
    highlights: list[Highlight]
    summary: list[SummaryItem]
    deadline: str | None = Field(description="Response deadline as YYYY-MM-DD, or null")
    needs_action: bool
    incomplete: bool
    incomplete_reason_es: str | None
    incomplete_reason_en: str | None
    scam: ScamCheck


class VerifierItem(BaseModel):
    ref: str = Field(description="'summary:N' (0-based index in the summary list) or 'highlight:SENTENCE_ID'")
    verdict: Literal["ok", "fixed", "unverified"]
    correction_es: str | None
    correction_en: str | None


class VerifierOutput(BaseModel):
    items: list[VerifierItem]
    translation_issues: list[int] = Field(
        description="IDs of sentences whose Spanish translation is unfaithful to the original"
    )
    scam_review: Literal["agree", "disagree"]
    scam_note_es: str | None
    scam_note_en: str | None


Warning = Literal["past_deadline", "incomplete", "image_source"]


class LetterResult(BaseModel):
    original: list[Sentence]
    translation: list[Sentence]
    highlights: list[Highlight]
    summary: list[SummaryItem]
    scam: ScamCheck
    needs_action: bool
    deadline: str | None
    deadline_passed: bool
    warnings: list[Warning]
    incomplete_reason_es: str | None = None
    incomplete_reason_en: str | None = None
    unverified_translation_ids: list[int] = []
    provider: str


class ErrorResult(BaseModel):
    code: Literal["cannot_read", "unsupported_in_mode", "provider_error"]
