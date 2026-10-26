import pytest

from app.errors import PipelineError
from app.pipeline import run_pipeline
from tests.fakes import FakeProvider, reader_output

LETTER = b"Your notice is here. You must reply by November 30. Call us for help."


def test_pipeline_returns_numbered_result():
    p = FakeProvider(reader=reader_output(3))
    r = run_pipeline("a.txt", LETTER, p)
    assert [s.id for s in r.original] == [1, 2, 3]
    assert [s.id for s in r.translation] == [1, 2, 3]
    assert r.highlights[0].sentence_id == 2
    assert r.provider == "fake"


def test_highlights_with_unknown_ids_are_dropped():
    from app.models import Highlight

    out = reader_output(3, highlights=[Highlight(sentence_id=2, kind="deadline"), Highlight(sentence_id=99, kind="action")])
    r = run_pipeline("a.txt", LETTER, FakeProvider(reader=out))
    assert [h.sentence_id for h in r.highlights] == [2]


def test_non_english_letter_cannot_be_read():
    with pytest.raises(PipelineError) as e:
        run_pipeline("a.txt", LETTER, FakeProvider(reader=reader_output(3, language="French")))
    assert e.value.code == "cannot_read"


def test_not_a_letter_cannot_be_read():
    with pytest.raises(PipelineError) as e:
        run_pipeline("a.txt", LETTER, FakeProvider(reader=reader_output(3, is_letter=False)))
    assert e.value.code == "cannot_read"
