"""Does the Verifier catch mistakes? Runs the real Reader, plants known errors in its output,
then checks that the real Verifier + code checks flag them. Costs a few cents in Gemini mode."""
import sys
from pathlib import Path

try:
    import dotenv  # noqa: F401
except ModuleNotFoundError:
    sys.exit("Missing packages. Run inside the project's virtual environment:\n"
             "  source .venv/bin/activate   (first time: python3 -m venv .venv && pip install -r requirements.txt)\n"
             "then run this script again with `python`.")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.agents.reader import run_reader  # noqa: E402
from app.agents.verifier import run_verifier  # noqa: E402
from app.checks import build_result  # noqa: E402
from app.ingest import ingest  # noqa: E402
from app.models import number_sentences  # noqa: E402
from app.providers import get_provider  # noqa: E402
from app.segment import split_sentences  # noqa: E402

LETTER = Path(__file__).resolve().parent.parent / "test_letters" / "medicaid_notice.txt"


def main() -> int:
    provider = get_provider()
    original = number_sentences(split_sentences(ingest(LETTER.name, LETTER.read_bytes()).text))
    reader = run_reader(provider, original)

    # Plant three errors: a wrong date in the deadline summary, a wrong phone number in the
    # contact summary, and a wrong date in the translation of the deadline sentence.
    deadline_idx = next(i for i, s in enumerate(reader.summary) if s.kind == "deadline")
    contact_idx = next(i for i, s in enumerate(reader.summary) if s.kind == "contact")
    reader.summary[deadline_idx].text_es = "Debe enviar la información antes del 13 de diciembre de 2026."
    reader.summary[deadline_idx].text_en = "You must send the information before December 13, 2026."
    reader.summary[contact_idx].text_es = "Llame al 1-800-555-9999."
    reader.summary[contact_idx].text_en = "Call 1-800-555-9999."
    target = next(s for s in reader.translation if "30 de noviembre" in s.text)
    target.text = target.text.replace("30 de noviembre", "3 de noviembre")

    verifier = run_verifier(provider, original, reader)
    result = build_result(original, reader, provider.name, verifier=verifier)

    checks = {
        "wrong deadline summary is fixed or flagged": (not result.summary[deadline_idx].verified)
        or "13" not in result.summary[deadline_idx].text_en,
        "wrong phone summary is fixed or flagged": (not result.summary[contact_idx].verified)
        or "9999" not in result.summary[contact_idx].text_en,
        "mistranslated sentence is reported": target.id in result.unverified_translation_ids,
    }
    for name, ok in checks.items():
        print(("PASS " if ok else "FAIL ") + name)
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
