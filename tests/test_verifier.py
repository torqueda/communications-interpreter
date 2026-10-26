from datetime import date

from app.checks import build_result
from app.models import Highlight, ScamCheck, Sentence, SummaryItem, VerifierItem, VerifierOutput
from app.pipeline import run_pipeline
from tests.fakes import FakeProvider, reader_output

ORIG = [Sentence(id=1, text="A notice."), Sentence(id=2, text="Reply by November 30, 2026."), Sentence(id=3, text="Call 555.")]
TODAY = date(2026, 10, 1)


def vout(items=(), issues=(), review="agree", note_es=None, note_en=None):
    return VerifierOutput(items=list(items), translation_issues=list(issues), scam_review=review, scam_note_es=note_es, scam_note_en=note_en)


def vi(ref, verdict, es=None, en=None):
    return VerifierItem(ref=ref, verdict=verdict, correction_es=es, correction_en=en)


def reader():
    return reader_output(
        3,
        highlights=[Highlight(sentence_id=2, kind="deadline"), Highlight(sentence_id=3, kind="contact")],
        summary=[
            SummaryItem(kind="what", text_es="a", text_en="a", sentence_ids=[1]),
            SummaryItem(kind="deadline", text_es="b", text_en="b", sentence_ids=[2]),
            SummaryItem(kind="contact", text_es="c", text_en="c", sentence_ids=[3]),
        ],
    )


def build(v):
    return build_result(ORIG, reader(), "fake", verifier=v, today=TODAY)


def test_ok_verdicts_keep_everything_verified():
    v = vout([vi("summary:0", "ok"), vi("summary:1", "ok"), vi("summary:2", "ok"), vi("highlight:2", "ok"), vi("highlight:3", "ok")])
    r = build(v)
    assert all(s.verified for s in r.summary) and len(r.highlights) == 2


def test_unverified_summary_item_is_marked():
    r = build(vout([vi("summary:0", "ok"), vi("summary:1", "unverified"), vi("summary:2", "ok")]))
    assert [s.verified for s in r.summary] == [True, False, True]


def test_missing_verdict_counts_as_unverified():
    r = build(vout([vi("summary:0", "ok")]))
    assert [s.verified for s in r.summary] == [True, False, False]


def test_fixed_applies_correction():
    r = build(vout([vi("summary:0", "ok"), vi("summary:1", "fixed", "corregido", "fixed"), vi("summary:2", "ok")]))
    assert r.summary[1].text_es == "corregido" and r.summary[1].verified


def test_fixed_without_correction_is_unverified():
    r = build(vout([vi("summary:0", "ok"), vi("summary:1", "fixed"), vi("summary:2", "ok")]))
    assert r.summary[1].verified is False


def test_unverified_highlight_is_removed():
    r = build(vout([vi("summary:0", "ok"), vi("summary:1", "ok"), vi("summary:2", "ok"), vi("highlight:3", "unverified")]))
    assert [h.sentence_id for h in r.highlights] == [2]


def test_translation_issues_reported_only_for_real_ids():
    assert build(vout(issues=[2, 99])).unverified_translation_ids == [2]


def test_scam_disagreement_adds_reason_and_flags():
    r = build(vout(review="disagree", note_es="Pide tarjetas de regalo", note_en="Asks for gift cards"))
    assert r.scam.flagged and r.scam.reasons_en == ["Asks for gift cards"]


def test_pipeline_calls_reader_then_verifier():
    p = FakeProvider(reader=reader_output(3))
    run_pipeline("a.txt", b"A notice is here. Reply by November 30. Call 555-0100 now.", p)
    assert p.calls == ["ReaderOutput", "VerifierOutput"]
