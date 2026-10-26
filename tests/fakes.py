"""A fake provider so pipeline tests never call a real AI."""
from app.models import ReaderOutput, ScamCheck, Sentence, SummaryItem, Highlight, VerifierOutput


class FakeProvider:
    name = "fake"

    def __init__(self, reader=None, verifier=None):
        self.reader = reader
        self.verifier = verifier
        self.calls = []

    def generate_json(self, system, prompt, schema, image=None, image_mime="image/png"):
        self.calls.append(schema.__name__)
        if schema is ReaderOutput:
            return self.reader
        if schema is VerifierOutput:
            return self.verifier or VerifierOutput(
                items=[], translation_issues=[], scam_review="agree", scam_note_es=None, scam_note_en=None
            )
        raise AssertionError(schema)


def reader_output(n=3, **over) -> ReaderOutput:
    base = dict(
        language="English",
        is_letter=True,
        transcribed=None,
        translation=[Sentence(id=i, text=f"es{i}") for i in range(1, n + 1)],
        highlights=[Highlight(sentence_id=2, kind="deadline")],
        summary=[
            SummaryItem(kind="what", text_es="Un aviso", text_en="A notice", sentence_ids=[1]),
            SummaryItem(kind="deadline", text_es="Antes del 30", text_en="By the 30th", sentence_ids=[2]),
        ],
        deadline="2099-11-30",
        needs_action=True,
        incomplete=False,
        incomplete_reason_es=None,
        incomplete_reason_en=None,
        scam=ScamCheck(flagged=False, reasons_es=[], reasons_en=[]),
    )
    base.update(over)
    return ReaderOutput(**base)
