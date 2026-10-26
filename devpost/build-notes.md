# Build Notes (read in the morning)

Learn-mode explanations, written as each slice finishes. For every slice: what changed, where the code is, how to try it yourself.
Start the app any time with: `source .venv/bin/activate && uvicorn app.main:app --reload`, then open http://localhost:8000.

## Slice 1 — Upload a letter and see numbered sentences
**What it does.** You drop a PDF or .txt letter on the page. The browser sends it to the server (`POST /api/explain`), our own code extracts the text and splits it into sentences, and each gets a number. Nothing here uses AI. The numbers matter: later, the translation, highlights and summary all point at "sentence 11" instead of copying text, which is how the app can prove each point comes from real text.

**Where the code is.**
- `app/main.py` — the FastAPI app: the `/api/explain` route, the error → HTTP status mapping, serving `static/`.
- `app/ingest.py` — detects PDF/TXT/image and pulls out text (PyMuPDF for PDFs). A PDF with no text layer becomes a page image for later.
- `app/segment.py` — the rule-based sentence splitter (handles "a.m.", "P.O.", wrapped PDF lines, phone numbers); tested in `tests/test_segment.py`.
- `static/` — the page (`index.html`, `styles.css` with the Clear paper tokens, `app.js`, `i18n.js`).

**Checked by me.** 17 pytest tests pass (splitter edge cases, ingest of TXT/PDF/scanned PDF/PNG/bad files); server starts cleanly; curl upload of the sample PDF and TXT returns numbered sentences; an empty file returns `cannot_read` (HTTP 422).

**Try it yourself.** Run the server, open http://localhost:8000, drop `test_letters/medicaid_notice.pdf`. You should see the left column of numbered sentences. Do the sentence boundaries look right to you (e.g. "P.O. Box 4410…" stays one sentence)?

## Slice 2 — Spanish translation next to the original, with matched highlights
**What it does.** After the sentences are numbered, the **Reader agent** (one Gemini call) gets them as `[1] text`, `[2] text`… and returns, as structured JSON: a Spanish translation of every numbered sentence, which sentences are the deadline / action / documents / contact, a bilingual summary citing sentence numbers, the deadline date, a scam check, and flags for "incomplete" and "not English". The page draws both letters and colors the same sentence number the same way in both columns, with an icon too (color is never the only signal).

**Discovered while building.** The Gemini key is valid. I used `gemini-2.5-flash` (available, stable); the account also lists newer Flash models, so you can change `GEMINI_MODEL` in `.env`. One call takes about 15–20 s on the sample letter. The API key currently comes from your shell environment (`GEMINI_API_KEY`); no `.env` file exists yet — for a fresh terminal, `cp .env.example .env` and paste the key.

**Where the code is.** `app/models.py` (all schemas; they double as the JSON schema Gemini must follow), `app/providers/gemini.py` (SDK call, 90 s timeout, one retry on bad JSON), `app/agents/reader.py` (the prompt — worth reading, it holds the rules), `app/pipeline.py`, and the rendering in `static/app.js`. Also `scripts/make_letters.py` and `test_letters/medicaid_notice.*`.

**Checked by me.** A fake provider (`tests/fakes.py`) lets tests run the pipeline without AI; 21 tests pass. A live Gemini run on the Medicaid letter returned valid output, every highlight id exists, all 17 sentences translated, deadline `2026-11-30`. A headless browser upload shows matching colors/icons in both columns with no console errors.

**Try it yourself.** Upload `test_letters/medicaid_notice.pdf`. With your translator's eye: is the Spanish tone/register right (usted, plain wording)? Does each highlight color/icon match in both columns? *(This is the planned "early feedback" checkpoint; I deferred it to your morning review.)*

## Slice 3 — Summary, "Show in letter", highlight clicks, and code checks
**What it does.** Below the letters is a summary (what it is, what to do, deadline, documents, who to contact). Each point has "Show in letter" which scrolls to and flashes its source sentences in both columns. Clicking (or Enter on) any highlighted sentence flashes its twin in the other column and shows a short tooltip. Behind this, `app/checks.py` runs **plain code, no AI**, on the Reader's output: every cited sentence id must exist; a summary point with no valid source is marked `verified: false`; the deadline's date must actually appear in the sentence the deadline point cites; duplicate/unknown highlights are dropped; and `deadline_passed` is computed by comparing dates with today. This is the "prove it traces back to real text" half of the kernel.

**Checked by me.** 31 tests (10 new for `checks.py`: bad ids, missing citations, date formats, past/future deadline, incomplete + image warnings). Headless browser: clicking a highlight shows the tooltip and flashes the twin; "Show in letter" flashes sentences in both columns; Start over clears the results and returns to the upload view; no console errors.

**Try it yourself.** On the results page click a yellow sentence on either side; click each "Mostrar en la carta" link. Does each land on the right sentences?

## Slice 4 — A second agent checks the first
**What it does.** After the Reader, a separate **Verifier** call (skeptical-reviewer prompt, `app/agents/verifier.py`) sees the original sentences, the Reader's translation, highlights, summary and scam decision. It returns, for each summary point and highlight, `ok` / `fixed` (with a correction) / `unverified`, a list of sentences whose Spanish is unfaithful, and whether it agrees with the scam decision. `checks.apply_verifier` (code) merges that: `fixed` text replaces the original; `unverified` or *missing* verdicts become `verified: false` and show "Couldn't verify, check the original letter"; an unverified highlight is removed; mistranslated sentences get a small "check this sentence" label; if the Verifier disagrees on scam, the warning stays (or appears) with its note added as one more reason.

**Why it's a separate call.** The same model grading its own work in the same breath tends to agree with itself; a fresh call with a "find the errors" job is the pattern from your Benefits Navigator work.

**Checked by me.** 40 tests (9 new, using fake Verifier verdicts). **A planted-error eval** (`python evals/planted_errors.py`): runs the real Reader, then secretly changes the deadline date and a phone number in the summary and a date in one translated sentence, and checks that the real Verifier catches them. All 3 planted errors were caught (PASS ×3). A normal live run on the Medicaid letter now takes ~36 s (two calls) and everything came back verified.

**Try it yourself.** `python evals/planted_errors.py` — it's the "does the verifier actually work?" test for your hallucination-focused goals. Then consider: which other errors should be planted (a missing "not")?
## Slice 5 — Scam warning and the letter states
**What it does.** If the Reader (or the Verifier on disagreement) flags a letter, the page shows a red warning *first* with the specific reasons (cited by sentence number), advice to use the official website, and an "Entiendo / I understand" checkbox; the translation, highlights and summary stay hidden until it's ticked. Red is used only here and for red-flag highlights. Other states: past deadline and incomplete letters get a calm amber box; informational letters get an "action" point saying no action is needed; French or not-a-letter files show the can't-read message; provider/network errors show a message with Try again.

**Test letters (all made up)** in `test_letters/`: `medicaid_notice` (normal), `phishing_gift_cards`, `informational_received`, `past_deadline_school`, `missing_contact` (cuts off mid-sentence), `french_letter`, `clinic_shot` (rendered to a PNG screenshot too). Each has an `.expected.json` of properties it must have. `scripts/make_letters.py` regenerates the PDFs/PNG from the `.txt` sources.

**Checked by me.** `python evals/run_evals.py` over the real pipeline (fixed "today" of 2026-10-26 so date results don't drift): **7/7 passed** — the phishing letter is flagged with reasons, normal letters are not, the school letter shows `past_deadline`, the cut-off letter shows `incomplete`, French → `cannot_read`, informational → no action needed, and the PNG screenshot works (it already carries the `image_source` warning; slice 7 covers the rest). In a headless browser the phishing letter hides everything until the box is ticked, then reveals it; no console errors.

**Try it yourself.** Upload `phishing_gift_cards.pdf`, `past_deadline_school.pdf` and `french_letter.pdf`. Is the warning clear and calm? Is the wording of the red/amber boxes right in Spanish?
**Note for your testing mind.** Only one letter per scenario so far; more variants (a legitimate letter that mentions a payment, a scam without gift cards) would stress the scam check most. Worth adding.
## Slice 6 — Spanish/English interface, Start over, Close, disclosures
**What it does.** First visit shows an "Elija su idioma · Choose your language" picker with the "you can switch any time" note. After that, an Español/English toggle sits in the fixed top-right corner. Switching re-draws everything in the other language *without* losing the letters or summary (they live in a JS variable). The choice is the only thing saved (browser `localStorage`, key `lang`). Every string lives in `static/i18n.js`. "Start over" clears everything; "Close" clears it and goes to cat-bounce.com (demo joke). The footer always shows the not-legal-advice note, plus an expandable disclosures panel (what it does, can be wrong, not legal advice, nothing stored, and that the letter is sent to the configured AI provider).

**Checked by me.** A test that `es` and `en` have identical keys (41 tests total now). A headless-browser run (with the server's answer mocked so it's instant): picker on first open; choice survives reload; toggle still visible after scrolling to the bottom (top bar stays at y=0); switching to English mid-results keeps all letters and the "couldn't verify" labels; disclosures panel opens; Close lands on cat-bounce.com; no console errors.

**Update after your review:** the Close button was removed; Start over is centered; the wording is now formal (no contractions, "proceed with caution", "Por favor" on instructions).

**Try it yourself.** Open in a private window to see the first-open picker. Check the short text blocks (intro, boxes, footer) for awkward line gaps — I used `text-wrap: balance` and ~62-character widths, but your eye is the judge. Also: I added one disclosure you didn't ask for (the letter is sent to the AI provider) because it's true and matters for a privacy-minded tool.
## Slice 7 — Screenshots and scanned PDFs (Gemini mode)
**What it does.** A PNG/JPG, or a PDF that is really a scanned picture (no text layer), is handed to Gemini as an image. The Reader first **transcribes** it into numbered sentences, then everything else works on those numbers; the Verifier also gets the image to compare against. The results show an amber "We read the text from an image" caution (reading images is less reliable than real text). The left column shows the transcription, not the image itself (a spec decision: drawing highlights on an image needs text coordinates). In Ollama mode an image gets the "this mode can't read images" message.

**Checked by me.** `ingest` tests already cover PDF-without-text → page image. New made-up test letters: `clinic_shot.png` (a screenshot-style PNG) and `power_shutoff_scan.pdf` (a PDF containing only a picture; confirmed 0 text characters). Live evals: both PASS with the `image_source` warning. In the browser the PNG upload shows a transcription that matched the source sentence-for-sentence, plus the caution box.

**Try it yourself.** Upload `test_letters/clinic_shot.png` and `power_shutoff_scan.pdf`. Compare the left column to the image. Then try a real phone screenshot (use a made-up letter, not a real one).
## Slice 8 — Free local mode with Ollama
**What it does.** Set `PROVIDER=ollama` in `.env` and the very same pipeline (Reader, Verifier, code checks) runs on a local model through Ollama's HTTP API (`POST /api/chat` with the JSON schema in `format`). No key, no cost, nothing leaves your machine. Text letters only: a screenshot gives the "this mode can't read images" message. Code: `app/providers/ollama.py`.

**What I found.** Ollama wasn't running; I started it (`ollama serve`) and used the already-installed `qwen2.5:7b-instruct` (best Spanish of your installed models in my try; `llama3.2` was no faster and wrote worse Spanish: "tú", "recetas de sueldo"). Two prompt bugs only the small model exposed: it reported the language of its *answer* as the letter's language, and sometimes called a real notice "not a letter". Both made good letters fail as `cannot_read`. I tightened the Reader prompt (this also hardens the Gemini path). It is **slow**: the full Medicaid letter took 346 s on this laptop (two calls), so Ollama's time limit is 480 s per call, not the spec's 90 s (recorded under Revisions). After the fix the local run completed with all five summary points verified, no false scam flag, correct deadline.

**Checked by me.** 46 tests (5 new, fake HTTP: request shape, retry once on invalid JSON, two bad replies → `provider_error`, image rejected, connection error). One live end-to-end Ollama run on the Medicaid letter succeeded (above).

**Try it yourself.** `ollama serve`, set `PROVIDER=ollama` in `.env`, restart the server, upload `medicaid_notice.txt` and wait a few minutes. Decide whether the quality/time tradeoff is acceptable for a "free mode"; whether the README should recommend a different model is your call.
## Slice 9 — Evals over all trial letters, and the README
**What it does.** `python evals/run_evals.py` runs the real pipeline over every letter in `test_letters/` (3 at a time), checks each against its `.expected.json` (scam yes/no, needs action, deadline, deadline passed, required warnings, plus two universal properties: every non-"what" summary point cites an existing sentence or carries the "couldn't verify" label, and a scam flag always has reasons), and prints a pass/fail table. It uses a fixed "today" (2026-10-26) so past/future deadline expectations don't drift. `--provider ollama` runs the text letters locally. `README.md` explains how it works, setup for both modes, limits and the not-legal-advice note.

**I added two harder letters for your "run more trial cases" goal:** `legit_payment_notice` (a real-looking tax bill that mentions payment and says it does NOT accept gift cards — must not be flagged) and `phishing_delivery_link` (a scam with no gift cards: a fake redelivery fee on a `.top` link). 

**Checked by me.** 46 unit tests pass. **Live evals: 10/10 PASS** (normal, informational, past deadline, cut-off, French, PNG screenshot, scanned PDF, legit payment letter, two scams). A fresh virtualenv installed from `requirements.txt` starts the server and serves the page.

**Honest caveats.** 10/10 on 10 letters is encouraging, not proof: the AI is not deterministic, and one run per letter shows nothing about how often it fails. Worth running the evals a few times and adding nastier cases (borderline scams, long letters, bad scans). The Ollama eval subset was not run end to end (a single letter takes ~6 min on this laptop).

**Try it yourself.** `python evals/run_evals.py` and read the table: are these the right scenarios? Is any PASS suspicious?
## Extra — FastAPI walkthrough (your "useful unknown")
A private artifact using this project's real code: https://claude.ai/artifact/FwunEw2jHBrdfJPbZNYtJb — the app object, a route, file upload and the thread-pool detail, Pydantic models, the error handler, and serving the page; ends with a "try it from /docs" exercise.

## What's left for the morning (needs you)
1. Run the app and try the things above (early check on slice 2 and the final "kick the tires" review). Tell me anything to change.
2. Final Review confirmation, then the learning wrap-up and `devpost/app-map.html`, via `/5-build` again.
3. Git: `git init`, first commit, GitHub repo, push — you wanted to do this last. Nothing is committed yet. `.gitignore` already excludes `.env`, `.venv`, and your learner profile.
4. Then `/6-ship`.
