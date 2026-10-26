from app.segment import split_sentences


def test_basic_split():
    assert split_sentences("You must reply. Call us today!") == ["You must reply.", "Call us today!"]


def test_abbreviations_dont_split():
    text = "Call between 9 a.m. and 5 p.m. on weekdays. Ask for Dr. Smith."
    assert split_sentences(text) == [
        "Call between 9 a.m. and 5 p.m. on weekdays.",
        "Ask for Dr. Smith.",
    ]


def test_phone_numbers_and_urls_stay_whole():
    text = "Call 1-800-555-0123 or 555.123.4567. Visit www.example.gov/help today."
    assert split_sentences(text) == [
        "Call 1-800-555-0123 or 555.123.4567.",
        "Visit www.example.gov/help today.",
    ]


def test_wrapped_pdf_lines_are_joined():
    text = "We received your application and are\nreviewing it. You will hear from us soon."
    assert split_sentences(text) == [
        "We received your application and are reviewing it.",
        "You will hear from us soon.",
    ]


def test_short_lines_stay_separate():
    text = "Notice of Action\nDate: October 3, 2026\nDear Maria Lopez,\nYour benefits will end."
    assert split_sentences(text) == [
        "Notice of Action",
        "Date: October 3, 2026",
        "Dear Maria Lopez,",
        "Your benefits will end.",
    ]


def test_paragraph_break_splits():
    assert split_sentences("First paragraph without end\n\nSecond one.") == ["First paragraph without end", "Second one."]


def test_empty_input():
    assert split_sentences("  \n\n ") == []


def test_dates_with_numbers_after_period():
    assert split_sentences("Respond by Nov. 30, 2026. 3 documents are needed.") == [
        "Respond by Nov. 30, 2026.",
        "3 documents are needed.",
    ]


def test_po_box():
    assert split_sentences("P.O. Box 4410, Capital City") == ["P.O. Box 4410, Capital City"]
