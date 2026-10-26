from datetime import date

from app.checks import build_result, date_appears_in, parse_deadline
from app.models import Highlight, ScamCheck, Sentence, SummaryItem
from tests.fakes import reader_output

ORIG = [Sentence(id=1, text="This is a notice."), Sentence(id=2, text="Reply by November 30, 2026."), Sentence(id=3, text="Call 555.")]
TODAY = date(2026, 10, 26)


def item(kind, ids, text="x"):
    return SummaryItem(kind=kind, text_es=text, text_en=text, sentence_ids=ids)


def run(**over):
    return build_result(ORIG, reader_output(3, **over), "fake", today=TODAY)


def test_cited_ids_must_exist():
    r = run(summary=[item("what", [1]), item("action", [2, 99])])
    assert r.summary[1].sentence_ids == [2]
    assert r.summary[1].verified is False


def test_non_what_item_without_citation_is_unverified():
    r = run(summary=[item("what", []), item("contact", [])])
    assert r.summary[0].verified is True
    assert r.summary[1].verified is False


def test_good_items_stay_verified():
    r = run(summary=[item("what", [1]), item("contact", [3])])
    assert all(s.verified for s in r.summary)


def test_unknown_highlight_dropped_and_duplicates_collapsed():
    r = run(highlights=[Highlight(sentence_id=2, kind="deadline"), Highlight(sentence_id=2, kind="action"), Highlight(sentence_id=7, kind="docs")])
    assert [(h.sentence_id, h.kind) for h in r.highlights] == [(2, "deadline")]


def test_deadline_passed_and_warning():
    r = run(deadline="2026-10-01")
    assert r.deadline_passed and "past_deadline" in r.warnings


def test_future_deadline_not_passed():
    r = run(deadline="2026-11-30")
    assert not r.deadline_passed and r.warnings == []


def test_deadline_date_must_appear_in_cited_sentence():
    r = run(deadline="2026-11-30", summary=[item("what", [1]), item("deadline", [3])])
    assert r.summary[1].verified is False
    r = run(deadline="2026-11-30", summary=[item("what", [1]), item("deadline", [2])])
    assert r.summary[1].verified is True


def test_bad_deadline_string_is_none():
    assert parse_deadline("soon") is None
    assert run(deadline="soon").deadline is None


def test_incomplete_warning_and_image_warning():
    r = build_result(ORIG, reader_output(3, incomplete=True), "fake", image_source=True, today=TODAY)
    assert set(r.warnings) == {"incomplete", "image_source"}


def test_date_formats():
    d = date(2026, 11, 30)
    assert date_appears_in(d, ["by Nov. 30"]) and date_appears_in(d, ["on 11/30/2026"]) and date_appears_in(d, ["30 November"])
    assert not date_appears_in(d, ["by December 3"])
