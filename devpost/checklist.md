---
doc: checklist
status: approved
---

# Build Checklist

Build mode: learn (modified by the learner: explanations and how-to-test notes are written to `devpost/build-notes.md` for morning review instead of pausing after each slice)

## Slices

- [x] **1. Upload a PDF or text letter and see it as numbered sentences**
  Becomes usable: A running local web page where you drop in a PDF or .txt letter and see it split into numbered sentences in the left column, in the Clear paper look.
  Why now: Proves the whole path (browser → FastAPI → our own code → screen) and builds the kernel's foundation: sentences numbered by code before any AI sees them. Bootstrapping lives here.
  PRD ref: `prd.md > Uploading a Letter`, `prd.md > Screens and Layout`
  Spec ref: `spec.md > Where It Runs and How Someone Tries It`, `spec.md > Components` (Web Server, Ingest, Sentence Segmenter), `spec.md > File Structure`, `spec.md > Look and Feel`
  Build: Scaffold the folders, `requirements.txt`, `.env.example`, `config.py`; FastAPI app serving `static/`; `POST /api/explain` that ingests PDF/TXT and returns numbered sentences; `segment.py` with unit tests; a minimal page with the upload area and the left column.
  Verify (mechanical): `pytest` passes for the segmenter (abbreviations, phone numbers, line breaks); server starts with no errors; `curl` upload of a sample PDF and a .txt returns numbered sentences; an empty file returns `cannot_read`.
  Learner check: Run the server, open http://localhost:8000, drop in a sample letter, and say whether the sentences are split the way you'd expect and whether the page feels right.
  Commit: `Add upload page, ingest, and numbered sentences`

- [x] **2. The Spanish translation appears next to the original with matched highlights**
  Becomes usable: Upload a letter and get the side-by-side: Spanish on the right, key sentences colored and iconed the same in both columns. (Gemini mode.)
  Why now: The unique kernel and the biggest unknown (Gemini structured output, model names, quality). Doing it now surfaces bad news early.
  PRD ref: `prd.md > Side-by-Side Letters with Matched Highlights`, `prd.md > Processing Animation`
  Spec ref: `spec.md > Components` (Providers, Reader Agent), `spec.md > Data Model`, `spec.md > External Services and Dependencies`, `spec.md > Stack` (the "Unverified" list)
  Build: Verify current Gemini model names and SDK syntax first; `models.py`, `providers/gemini.py` (+ one retry), `agents/reader.py`, `pipeline.py` (ingest → segment → reader), highlight rendering with icons, and a simple processing animation. Create the Medicaid-style test letter.
  Verify (mechanical): Tests with a fake provider confirm the pipeline output shape; one live Gemini call on the Medicaid test letter returns valid `ReaderOutput` where every highlight ID exists in the original and every sentence has a translation.
  Learner check: Upload the Medicaid test letter. Check that the deadline in Spanish and in English has the same color and icon, and judge the translation quality with your translator's eye.
  Commit: `Add Reader agent and side-by-side highlighted translation`

- [x] **3. The summary and "Show in letter" work, with code-checked sources**
  Becomes usable: Under the letters, a summary (what it is, action, deadline, documents, contact) where each point links to and flashes its source sentences; clicking any highlight flashes its twin and shows a tooltip.
  Why now: Completes the "oh, that's cool" beat of the core journey. The code grounding check comes with it so no point ever shows an invented source.
  PRD ref: `prd.md > Summary with "Show in Letter"`, `prd.md > Highlight Interactions`
  Spec ref: `spec.md > Components` (Code Checks and Assembly, Page), `spec.md > The Core Journey Through the System` (steps 6, 8, 9)
  Build: `checks.py` (cited IDs must exist, `verified=false` handling, `deadline_passed`, warnings), `LetterResult` assembly, summary rendering, "Show in letter" scroll-and-flash, highlight click + tooltip.
  Verify (mechanical): Unit tests for `checks.py` (bad IDs, missing citations, past deadline); pipeline test with the fake provider returns a `LetterResult`; live run on the Medicaid letter has every non-"what" summary item citing existing sentences.
  Learner check: Click "Show in letter" on each point and click highlights in both columns; confirm each lands on the right sentence.
  Commit: `Add summary, Show in letter, and highlight interactions`

- [x] **4. A second agent verifies the first and unconfirmed points are labeled**
  Becomes usable: Every result has been reviewed by a separate Verifier call; fixes are applied and anything unconfirmed shows "Couldn't verify, check the original."
  Why now: This is the other half of the kernel (trust you can inspect). Doing it right after the summary lets us feed it real outputs.
  PRD ref: `prd.md > Letter Checking (Verifier)`
  Spec ref: `spec.md > Components` (Verifier Agent, Code Checks and Assembly)
  Build: `agents/verifier.py`, wire into the pipeline and `checks.py` (apply `fixed`, mark `unverified`), the label in the page. Fake-provider tests for each verdict.
  Verify (mechanical): Tests with a fake Verifier returning `ok`, `fixed`, `unverified` produce the right `verified` flags and corrections; a live run on the Medicaid letter completes with both agents.
  Learner check: Upload the letter, then try the planted-error test letter (a deliberately mistranslated sample) and confirm the label shows on the wrong point.
  Commit: `Add Verifier agent and unverified labels`

- [x] **5. Scam warning, plus the letter states**
  Becomes usable: A phishing letter triggers the warning first with reasons and an "I understand" gate. Informational, past-deadline, incomplete, non-English, and unreadable letters each behave as the PRD says.
  Why now: These are the trial scenarios you care most about, and they depend on the full pipeline now being in place.
  PRD ref: `prd.md > Scam Warning`, `prd.md > States and Boundaries`
  Spec ref: `spec.md > Components` (Reader, Verifier scam review, Web Server errors), `spec.md > Important Failure Modes`
  Build: Scam gate and red-flag highlights, caution boxes (past deadline, incomplete, image source reserved), `cannot_read` and `provider_error` messages with Try again, 90s timeout. Add the remaining test letters (phishing, informational, past deadline, missing contact, French).
  Verify (mechanical): Live run over each test letter, checking against expected properties (phishing flagged with reasons, others not flagged, past-deadline warning present, French → `cannot_read`, informational → no action); tests for error codes.
  Learner check: Upload the phishing letter and the past-deadline letter. Is the warning clear and calm? Is anything in the red/amber wording confusing?
  Commit: `Add scam warning and letter states`

- [x] **6. Spanish/English interface, Start over, Close, and disclosures**
  Becomes usable: First open asks Español/English, the toggle stays top-right, text switches instantly without losing results; Start over and Close clear everything; disclosures and "not legal advice" are available.
  Why now: Interface-level polish on a working core. Waiting until here avoids rewriting strings while the screens were still changing.
  PRD ref: `prd.md > Interface Language`, `prd.md > Start Over and Close`, `prd.md > Disclosures`
  Spec ref: `spec.md > Components` (Page), `spec.md > Look and Feel`
  Build: `i18n.js` with every string in both languages, language picker + `localStorage`, sticky top bar, Start over / Close (cat-bounce.com), disclosures panel, line-length rules (about 62ch, balanced text).
  Verify (mechanical): Script checks that `es` and `en` have identical keys; served page loads with no console errors; manual-style check of results state before and after toggling language.
  Learner check: Switch languages mid-results, scroll down and confirm the toggle stays visible, then try Start over and Close. Check the short text blocks for awkward line gaps.
  Commit: `Add language toggle, Start over, Close, and disclosures`

- [x] **7. Screenshots and scanned PDFs work (Gemini mode)**
  Becomes usable: A PNG/JPG screenshot (or a PDF with no text layer) is read, transcribed, explained, and shows the image-reading caution box.
  Why now: Most risk-heavy input, and it only makes sense once the text path is solid.
  PRD ref: `prd.md > Uploading a Letter` (image notice)
  Spec ref: `spec.md > Components` (Ingest, Reader), `spec.md > Important Failure Modes` (no text layer)
  Build: Image upload path, transcription by the Reader, Verifier comparing against the image, `image_source` warning, scanned-PDF fallback via a rendered page image, `GET /api/config`.
  Verify (mechanical): `make_letters.py` generates a PNG test letter; live run returns transcribed sentences and an `image_source` warning; a text-layer-free PDF takes the image path.
  Learner check: Upload the PNG screenshot and check the caution box and whether the transcription matches what you see.
  Commit: `Add image and scanned PDF support`

- [x] **8. Free local mode with Ollama (text letters)**
  Becomes usable: Setting `PROVIDER=ollama` runs the same text-letter flow with a local model; images show the "needs Gemini mode" message.
  Why now: Independent of the main journey, so it comes after everything the demo needs.
  PRD ref: `prd.md > Uploading a Letter`
  Spec ref: `spec.md > Components` (Providers), `spec.md > External Services and Dependencies` (Ollama)
  Build: `providers/ollama.py` with the `format` schema and retry; image rejection in Ollama mode; pick and pull a suitable model.
  Verify (mechanical): Fake-HTTP test for the Ollama request/response shape; live run of the Medicaid text letter in Ollama mode returns a valid result or a clean `provider_error`.
  Learner check: Switch `.env` to Ollama, upload a text letter, and judge whether the quality is acceptable for a free mode.
  Commit: `Add Ollama provider`

- [x] **9. Evals over all trial letters, and the README**
  Becomes usable: One command runs every test letter through the real pipeline and prints a pass/fail table; the README explains setup for both modes, limits, and not-legal-advice.
  Why now: This is your "run more trial cases" goal, and it needs the finished pipeline. Last so the README describes what exists.
  PRD ref: `prd.md > What We're Building`
  Spec ref: `spec.md > Components` (Test Letters and Evals), `spec.md > Where It Runs and How Someone Tries It`
  Build: `evals/run_evals.py` with an `expected.json` per letter, `--provider ollama` subset, README, final `.env.example` check.
  Verify (mechanical): `python evals/run_evals.py` runs and prints the table; `pytest` passes; a fresh venv install from `requirements.txt` starts the server.
  Learner check: Run the evals yourself and read the table: are these the right scenarios, and is any "pass" suspicious?
  Commit: `Add evals and README`

## Hands-on Checkpoints

- [x] Early usable behavior explored — covered by the learner's review of all slices (including the slice 2 translation and highlights); their feedback is under Revisions
- [x] Final kick-the-tires exploration and feedback completed

## Final Review

Verified after the learner's feedback: 46 unit tests pass; live evals 10/10 against Gemini with the renamed app and new wording.

- [x] Learner retries the revised behavior: formal wording in both languages, centered scam warning, fully visible flash outline, new can't-read message, single centered Start over button, new app name
- [x] Final review complete — feedback resolved and learner confirms ready to ship ("Everything looks good" after retrying the revisions)

## Code Tour and App Map

- [x] Learning activity complete — guided route, focused alternative, prior practice connected, or brief recap
- [x] Optional edit and transfer reflection addressed — offered/declined/already covered/not applicable as appropriate
- [x] `devpost/app-map.html` generated from finished code, checked, and shown, including a project-grounded practice to reuse

Activity and evidence: Brief evidence-based recap (focused alternative, no hands-on exercise). Practice: breaking the AI's output on purpose to test the Verifier — `evals/planted_errors.py` (3 of 3 planted errors caught), `tests/test_checks.py`, `tests/test_verifier.py`; the evals (`evals/run_evals.py`, 10/10) as the trial-case set.
Route and stops: Reference-only route in the map: `app/main.py` (`explain`), `app/pipeline.py` (`run_pipeline`), `app/checks.py` (`build_result`). Not toured interactively.
Edit outcome: Not applicable (no optional edit run; the focused alternative needed none).
Reflection: Offered at wrap-up; any answer belongs only in the ignored profile.
Activity mode: Recap, with `devpost/app-map.html` (checked: anchors match source, renders offline in light and dark, no horizontal scroll at 390 px).

## Revisions

- Git repo and commits deferred to the end — the learner asked to set up the repo last (spec also says they run `git init` themselves), so slices are verified and ticked but not committed until then; the last verified state is not git-recoverable meanwhile.
- Learner checks and the early/final hands-on checkpoints are deferred to the learner's morning review, per their request to build unattended overnight.
- Ollama time limit raised from the spec's ~90 s to 480 s per call — the local `qwen2.5:7b-instruct` model took about 3 minutes per call on this laptop (346 s for a whole letter, two calls), so a 90 s limit would always fail. Gemini keeps its 90 s limit. The README should say Ollama mode is slow.
- Reader prompt wording for `is_letter` and `language` tightened — the local model first reported its own answer language (Spanish) as the letter's language and called an ordinary notice "not a letter", both of which made valid letters fail as `cannot_read`.
- Close button removed, "Start over" centered — learner's review of the built app; `prd.md` and `spec.md` updated to match (the cat-bounce.com redirect is gone).
- Interface wording made formal and consistent (no English contractions, "proceed with caution", "Por favor" on Spanish instructions, new can't-read message) — learner feedback; PRD/spec tone and message text updated.
- Scam warning box centered, and the flashing outline raised above neighboring highlights (it was clipped behind the next highlighted sentence) — learner feedback.
- Project named Communications Interpreter / Interpretador de Comunicaciones (replaces the working title) — learner decision; code, README, scope, PRD and spec updated. The older `devpost/*.html` review copies still show the working title.
