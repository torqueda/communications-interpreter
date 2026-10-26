"""Run the real pipeline over every test letter and print a pass/fail table.

  python evals/run_evals.py                 # Gemini (PDFs + the PNG screenshot)
  python evals/run_evals.py --provider ollama   # text letters only, from the .txt sources
  python evals/run_evals.py medicaid        # only letters whose name contains this text

Each letter has an <name>.expected.json with the properties it must have. Costs a few cents in Gemini mode.
"""
import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

try:
    import dotenv  # noqa: F401
except ModuleNotFoundError:
    sys.exit("Missing packages. Run inside the project's virtual environment:\n"
             "  source .venv/bin/activate   (first time: python3 -m venv .venv && pip install -r requirements.txt)\n"
             "then run this script again with `python`.")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

TODAY = date(2026, 10, 26)  # fixed so "deadline passed" expectations don't drift over time
LETTERS = ROOT / "test_letters"


def source_file(stem: str, expected: dict, provider: str) -> Path | None:
    if provider == "ollama":
        return None if expected.get("image") else LETTERS / f"{stem}.txt"
    return LETTERS / f"{stem}.png" if expected.get("image") else LETTERS / f"{stem}.pdf"


def check(expected: dict, result, error: str | None) -> list[str]:
    """Return the list of failed expectations (empty = pass)."""
    fails: list[str] = []
    if not expected["result"]:
        if error != expected.get("error", "cannot_read"):
            fails.append(f"expected error {expected.get('error')}, got {error or 'a result'}")
        return fails
    if error:
        return [f"unexpected error {error}"]
    for key in ("scam", "needs_action", "deadline", "deadline_passed"):
        if key in expected:
            actual = result.scam.flagged if key == "scam" else getattr(result, key)
            if actual != expected[key]:
                fails.append(f"{key}: expected {expected[key]}, got {actual}")
    for w in expected.get("warnings_include", []):
        if w not in result.warnings:
            fails.append(f"missing warning {w}")
    ids = {s.id for s in result.original}
    for item in result.summary:
        if item.kind != "what" and item.verified and not item.sentence_ids:
            fails.append(f"summary '{item.kind}' has no source sentence and no 'couldn't verify' label")
        if any(i not in ids for i in item.sentence_ids):
            fails.append(f"summary '{item.kind}' cites a sentence that does not exist")
    if result.scam.flagged and not result.scam.reasons_en:
        fails.append("scam flagged without reasons")
    return fails


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("name", nargs="?", default="")
    ap.add_argument("--provider", choices=["gemini", "ollama"], default=None)
    args = ap.parse_args()
    if args.provider:
        os.environ["PROVIDER"] = args.provider

    from app import config
    from app.errors import PipelineError
    from app.pipeline import run_pipeline
    from app.providers import get_provider

    provider_name = config.provider_name()

    jobs = []
    for exp_path in sorted(LETTERS.glob("*.expected.json")):
        stem = exp_path.name.removesuffix(".expected.json")
        if args.name not in stem:
            continue
        expected = json.loads(exp_path.read_text())
        src = source_file(stem, expected, provider_name)
        if src is None or not src.exists():
            print(f"SKIP  {stem} (no source for {provider_name} mode)")
            continue
        jobs.append((stem, expected, src))

    def run(job):
        stem, expected, src = job
        try:
            result, error = run_pipeline(src.name, src.read_bytes(), get_provider(), today=TODAY), None
        except PipelineError as exc:
            result, error = None, exc.code
        except Exception as exc:  # keep the table going
            result, error = None, f"crash: {exc}"
        return stem, check(expected, result, error)

    with ThreadPoolExecutor(max_workers=3) as pool:
        rows = list(pool.map(run, jobs))

    failed = 0
    print(f"\nProvider: {provider_name}\n")
    for stem, fails in rows:
        print(f"{'PASS' if not fails else 'FAIL'}  {stem}")
        for f in fails:
            print(f"        - {f}")
        failed += bool(fails)
    print(f"\n{len(rows) - failed}/{len(rows)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
