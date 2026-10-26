# Communications Interpreter

Upload an official English letter (PDF, screenshot, or text) and get it back in plain Spanish: a side-by-side translation with the important sentences color- and icon-matched in both languages, a short summary (what it is, what to do, by when, with what, who to contact), and a warning when the letter looks like a scam.

Built for first-generation Hispanic immigrant adults who struggle with English and the bilingual family members who help them. The interface switches between Español and English.

> **Not legal advice.** The explanation can contain mistakes. Always confirm dates, amounts and phone numbers with the original letter or the agency. All sample letters in this repo are made up.

## How it works (the part worth knowing)

1. **Code numbers the sentences first.** PDFs and text are split into numbered sentences by plain code before any AI sees them.
2. **Reader agent** (an AI call) translates each numbered sentence, marks the deadline / action / documents / contact sentences, writes a bilingual summary that *cites sentence numbers*, and makes a scam decision with reasons.
3. **Verifier agent** (a second, separate AI call) checks the Reader's work against the original: is each point faithful, is the translation faithful, is the scam decision justified?
4. **Plain code checks** (no AI): every cited sentence must exist, a deadline date must appear in the sentence it cites, a deadline in the past is flagged. Anything not confirmed is shown with *"We could not verify this. Please check the original letter"* instead of being trusted or hidden.
5. The page draws everything. Clicking a highlight flashes its twin in the other language; "Show in letter" jumps to the source sentences.

Nothing is stored. The letter lives in memory for one request; only your language choice is kept in the browser.

## Run it

Requires Python 3.11+.

```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then put your key in .env
uvicorn app.main:app --reload
```

Open http://localhost:8000.

In every new terminal, run `source .venv/bin/activate` first. The packages live in that virtual environment, and the `python` command also only exists inside it (outside, use `python3`, which will not find the packages).

### Settings (`.env`)

| Setting | Meaning |
|---|---|
| `PROVIDER` | `gemini` (default) or `ollama` |
| `GEMINI_API_KEY` | your key from https://aistudio.google.com/ (never commit it; `.env` is git-ignored) |
| `GEMINI_MODEL` | default `gemini-2.5-flash` |
| `OLLAMA_URL`, `OLLAMA_MODEL` | defaults `http://localhost:11434` and `qwen2.5:7b-instruct` |

### Two modes

- **Gemini (default):** handles PDFs, text, screenshots, and scanned PDFs. About 30–40 seconds per letter (two AI calls), a fraction of a cent.
- **Ollama (free, local):** `ollama pull qwen2.5:7b-instruct`, run `ollama serve`, set `PROVIDER=ollama`. **Text letters only** (PDFs with a text layer, `.txt`), no screenshots. Quality is lower and it is **slow**: a few minutes per letter on a laptop. Nothing leaves your machine.

## Tests and trial letters

```
pytest                              # unit tests, no AI, no network
python evals/run_evals.py           # real AI over every letter in test_letters/ (a few cents)
python evals/run_evals.py --provider ollama   # text letters, local, slow
python evals/planted_errors.py      # does the Verifier catch planted mistakes?
python scripts/make_letters.py      # regenerate the PDFs/PNG from the .txt letters
```

`test_letters/` has made-up letters for the scenarios that matter, each with an `.expected.json`: a normal notice with a deadline, an informational notice, a past deadline, a cut-off letter, a French letter, a screenshot, a scanned PDF, a legitimate letter that talks about payment (must *not* be flagged), and two scams (gift cards, a fake delivery link).

## Limits and what's next

- Letters must be in English. Other languages show a "can't be read" message for now.
- One file at a time; a letter split across several screenshots is not supported yet.
- Photos of paper letters are not a supported input yet (screenshots and scans are).
- Possible later: save the deadline to a calendar, history (needs a privacy design), more languages, read-aloud.

## Project layout

```
app/        FastAPI server, pipeline, agents (reader, verifier), providers (gemini, ollama), code checks
static/     the one-page interface (HTML, CSS, JS, all strings in es + en)
tests/      pytest
test_letters/, evals/, scripts/   trial letters, evals, helpers
devpost/    planning documents from the hackathon
```
