---
doc: spec
status: approved
---

# Communications Interpreter — Technical Spec

## How This Works, In Plain Language
Communications Interpreter is a small Python web server that runs on your laptop and serves one web page.

1. You open `http://localhost:8000` and drop in a letter (PDF, image, or plain text).
2. The page sends the file to the server. If it's a PDF or text file, **our own code** pulls out the text and splits it into numbered sentences. That numbered list is the ground truth.
3. The server asks the **Reader agent** (an AI model) to translate each numbered sentence into Spanish, mark which sentences are the deadline, the action, the documents, or the contact, write a short summary in both Spanish and English, and decide whether the letter looks like a scam. For a screenshot, the Reader also has to transcribe the image into numbered sentences first.
4. The server then asks a **Verifier agent** (a second, separate AI call) to check the Reader's work against the original: does each summary point say what its sentences actually say, is the translation faithful, and is the scam decision justified?
5. Finally, **plain code** (no AI) runs the hard checks: every sentence a summary point cites must exist in the original, and a deadline in the past gets flagged by comparing dates. Anything that fails is labeled "We could not verify this. Please check the original letter."
6. The page receives one JSON result and draws everything: the side-by-side letters, the color- and icon-matched highlights, the summary, and any warnings.

**Which AI runs the agents** is a setting in `.env`. **Gemini** is the default and handles PDFs, images, and text. **Ollama** runs a free local model for people without an API key; it handles text-based letters only, with lower quality.

**Why this shape:** one server, one page, no database, and no framework beyond FastAPI. The key design choice is that sentences are numbered by code before any AI sees them. Translation, highlights, and summary points all refer to sentence numbers, which makes lining up the two columns trivial and lets code (not just another AI) prove that every point traces back to real text. That is the kernel (`scope.md > The Unique Kernel`) built into the structure.

## The Core Journey Through the System
PRD ref: `prd.md > The Core Journey`.

1. **Open the app:** the browser loads `static/index.html`. With no saved language choice, the page shows the Español/English picker. The choice is kept in the browser's `localStorage` so it survives a reload. → `prd.md > Interface Language`
2. **Upload:** the person drops a file, and `app.js` POSTs it to `POST /api/explain` while the processing animation shows. → `prd.md > Uploading a Letter`, `prd.md > Processing Animation`
3. **Ingest:** `ingest.py` detects the type:
   - PDF → PyMuPDF extracts the text → `segment.py` splits it into numbered sentences.
   - TXT → read → segment.
   - Image → passed to the Reader for transcription (Gemini only), and the result carries an `image_source` notice.
   - Empty, unreadable, or no usable text → `cannot_read` error.
4. **Reader agent:** gets the numbered sentences (or the image) and returns `ReaderOutput`: language detected, whether the letter looks incomplete, the translated sentences, the highlight kind per sentence, bilingual summary items citing sentence IDs, the deadline as an ISO date, and the scam flag with reasons. Not English → `cannot_read`.
5. **Verifier agent:** gets the original sentences, the image if any, and the Reader output, and returns a verdict per summary item and highlight (`ok`, `fixed` with a correction, or `unverified`), plus a scam-decision review.
6. **Code checks (`checks.py`):** cited IDs must exist; fixes are applied; anything failing is set to `verified: false`; `deadline_passed` is computed against today's date; warnings are assembled (`past_deadline`, `incomplete`, `image_source`).
7. **Response:** a `LetterResult` JSON goes back to the page.
8. **Render:** `app.js` shows, in order:
   - the scam warning (if flagged), holding the rest until "I understand"
   - any caution boxes
   - the side-by-side letters, with highlights colored and iconed by kind
   - the summary with "Show in letter" links, and "could not verify" labels where needed

   → `prd.md > Scam Warning`, `prd.md > Side-by-Side Letters with Matched Highlights`, `prd.md > Summary with "Show in Letter"`, `prd.md > Letter Checking (Verifier)`
9. **Explore:** clicking a highlight finds the same sentence ID in the other column, flashes it, and shows the tooltip. This is purely client-side. → `prd.md > Highlight Interactions`
10. **Start over:** `app.js` clears the result from memory and the screen. The server kept nothing. → `prd.md > Start Over`

## Stack
- **Python 3.11+**: the learner's main language.
- **FastAPI** + **Uvicorn**: the web server and the JSON API. New to the learner, and a deliberate learning target (see Decisions). Docs: https://fastapi.tiangolo.com/
- **Pydantic v2**: data models for every agent output and the API response. It doubles as the JSON schema the models must follow. Docs: https://docs.pydantic.dev/
- **google-genai** (the Google Gen AI Python SDK): Gemini calls with structured JSON output and file and image input. Docs: https://ai.google.dev/gemini-api/docs, SDK: https://googleapis.github.io/python-genai/
- **Ollama** (local), called over its HTTP API with structured output via the `format` JSON schema. Docs: https://github.com/ollama/ollama/blob/main/docs/api.md
- **PyMuPDF**: PDF text extraction, and generating the PDF/PNG test letters. Docs: https://pymupdf.readthedocs.io/
- **python-dotenv**: loads `.env`. **httpx**: Ollama calls. **python-multipart**: FastAPI file uploads.
- **pytest**: unit tests. Docs: https://docs.pytest.org/
- **Frontend**: plain HTML, CSS, and JavaScript, no build step, served by FastAPI as static files. Learner accepted this over React (React would add a build step for a single page).

**Unverified, check at build start:**
- the current Gemini model names and prices (expected: a Flash-class model for both agents)
- the exact `google-genai` structured-output and file-upload syntax
- a suitable Ollama text model (e.g., Gemma 3 or Qwen 2.5 class) that handles Spanish acceptably

No lookups were done while writing this spec.

## Where It Runs and How Someone Tries It
- **Runtime:** local Python server and a browser. Requires Python 3.11+. For the Gemini mode, a Gemini API key; for the Ollama mode, Ollama installed with a model pulled.
- **Setup:**
  ```
  python -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  cp .env.example .env        # then put your key in .env
  uvicorn app.main:app --reload
  ```
  Open http://localhost:8000.
- **`.env` settings:** `PROVIDER=gemini|ollama`, `GEMINI_API_KEY=...`, `GEMINI_MODEL=...`, `OLLAMA_URL=http://localhost:11434`, `OLLAMA_MODEL=...`. `.env` is gitignored; `.env.example` (no secrets) is committed.
- **Demo recording:** run in Gemini mode and record:
  1. the language choice
  2. upload of the fabricated Medicaid-style PDF
  3. the side-by-side, with a click on the deadline highlight
  4. "Show in letter"
  5. the phishing letter's warning
- **Submission:** a short demo video plus a public GitHub repo. **No deployment** (learner choice); the README explains local setup for both modes and Ollama's limits.
- **GitHub:** the learner creates the GitHub repo and pushes **themselves**, with step-by-step guidance (learner request). `5-build` should walk them through `git init` and the first commit rather than doing it for them, and `6-ship` should walk them through creating the remote and pushing.

## Look and Feel
From `prd.md > Look and Feel` (Preset A, "Clear paper", reference: `devpost/style-options.html`). Implement as CSS custom properties in `static/styles.css`:
- **Colors:** `--bg #f3f5f8`, `--surface #ffffff`, `--ink #17223b`, `--muted #475268`, `--line #d3d9e4`, `--primary #1e3a8a`.
- **Highlight colors:** deadline `#ffe08a`, action `#ffc8b5`, documents `#dccdf6`, contact `#b5e5d6`.
- **Scam colors:** `--scam-bg #fdecea` / `--scam-ink #8f1d14`, used **only** for scam warnings and red-flag highlights.
- **Caution boxes** (past deadline, incomplete, image source): a calm amber style, e.g. background `#fff4d6` with text `#6b4a00`.
- **Type:** Atkinson Hyperlegible (Google Fonts) with a Verdana/sans-serif fallback; body 18px, line-height about 1.6.
- **Sizing:** tap targets at least 44px tall; text contrast at least 4.5:1; visible focus outlines.
- **Icons:** inline SVG for calendar (deadline), check (action), document, phone (contact), and warning (red flag), shown in every highlight and summary row. Color is never the only signal.
- **Line length (learner requirement):** cap text at about 62ch, **and** size the containers of short text blocks to that width or use `text-wrap: balance`/`pretty`, so no line ends early beside a large empty gap. Check the intro and the message boxes.
- **Layout:** fixed top bar (`position: sticky`) with the language toggle top-right. Letters in two columns, stacking under about 720px.
- **Tone:** calm, plain, reassuring, and formal copy in both languages (no contractions in English, "proceed with caution", "Por favor" on instructions in Spanish). Avoid generic AI styling (gradients, glowing dark mode, a card around everything).

## Components

### Web Server (`app/main.py`)
FastAPI app. Serves `static/` at `/`, and exposes:
- `POST /api/explain`: multipart `file`. Returns `LetterResult` (200) or `ErrorResult` (422 for `cannot_read`/`unsupported_in_mode`, 502 for `provider_error`).
- `GET /api/config`: returns `{provider, accepts: [...]}` so the page knows whether images are allowed in the current mode.

It calls the pipeline and keeps nothing between requests.
PRD ref: `prd.md > Uploading a Letter`, `prd.md > States and Boundaries`.

### Ingest (`app/ingest.py`)
Detects the file type by extension and content, then extracts text:
- PDF → PyMuPDF, page order
- TXT → UTF-8
- PNG/JPG → kept as bytes for the Reader
- Empty or near-empty text → `cannot_read`
- An image in Ollama mode → `unsupported_in_mode`

PRD ref: `prd.md > Uploading a Letter`, `prd.md > States and Boundaries` (can't be read).

### Sentence Segmenter (`app/segment.py`)
Splits text into `Sentence(id, text)` with a simple rule-based splitter (on `. ? !` plus line breaks, with care for abbreviations like "a.m.", "Dr.", and phone numbers). Deterministic and unit-tested. For images, the Reader returns the sentences directly.
PRD ref: `prd.md > Side-by-Side Letters with Matched Highlights`.

### Providers (`app/providers/`)
One interface: `generate_json(system: str, prompt: str, schema: type[BaseModel], image: bytes | None) -> BaseModel`.
- `gemini.py`: google-genai with JSON schema output; accepts an image.
- `ollama.py`: `POST /api/chat` with `format` set to the JSON schema; text only.
- `__init__.py`: picks the provider from `PROVIDER` in `.env`.

Each provider validates the output with Pydantic and retries once on invalid JSON.
PRD ref: supports every behavior that uses the agents.

### Reader Agent (`app/agents/reader.py`)
Prompt plus `ReaderOutput` schema. Tasks:
1. language check
2. transcription into numbered sentences (images only)
3. sentence-by-sentence Spanish translation that keeps IDs
4. highlight kind per sentence (`deadline | action | docs | contact | flag | none`)
5. bilingual summary items, each citing sentence IDs
6. deadline as an ISO date or null
7. informational or action needed
8. incomplete-letter signals
9. scam flag with reasons, in both languages

The prompt tells it to use only the letter's content and to say "no action needed at this time" for informational letters.
PRD ref: `prd.md > Side-by-Side Letters with Matched Highlights`, `prd.md > Summary with "Show in Letter"`, `prd.md > Scam Warning`, `prd.md > States and Boundaries`.

### Verifier Agent (`app/agents/verifier.py`)
A separate call with a skeptical-reviewer prompt. Input: the original sentences, the image if any, and the `ReaderOutput`. For each summary item and highlight it returns `ok | fixed(correction) | unverified`, plus `scam_review: agree | disagree(reason)`. On a disagreement, the scam warning still shows, with the verifier's note added as one more reason. That keeps the PRD's "show reasons, let the person judge" behavior.
PRD ref: `prd.md > Letter Checking (Verifier)`, `prd.md > Scam Warning`.

### Code Checks and Assembly (`app/checks.py`, `app/pipeline.py`)
`pipeline.py` runs ingest → segment → reader → verifier → checks. `checks.py`:
- rejects cited IDs that don't exist
- applies verifier fixes
- sets `verified=false` on any item that is unverified, has bad IDs, or has a summary with no cited sentence (except "what it is")
- computes `deadline_passed` from the date
- builds the warnings list

PRD ref: `prd.md > Letter Checking (Verifier)`, `prd.md > States and Boundaries`.

### Page (`static/index.html`, `static/app.js`, `static/styles.css`, `static/i18n.js`)
One screen with these views: language picker, upload, processing, message (`cannot_read`/error, with Try again), and results.
- `i18n.js` holds every interface string in `es` and `en`.
- `app.js` handles the upload, rendering, the scam acknowledgment gate, highlight click (flashing the twin ID plus a tooltip), "Show in letter" (scroll and flash), Start over, and the disclosures panel (an expandable section on the same screen).
- The language is stored in `localStorage`; everything else lives only in memory.

PRD ref: `prd.md > Interface Language`, `prd.md > Processing Animation`, `prd.md > Highlight Interactions`, `prd.md > Start Over`, `prd.md > Disclosures`, `prd.md > Screens and Layout`.

### Test Letters and Evals (`test_letters/`, `evals/run_evals.py`)
Made-up letters, each with an `expected.json` of properties. Examples: "scam flagged", "no action", "deadline 2026-11-30", "deadline passed", "incomplete warning", "cannot_read", "every summary item cites ≥1 sentence".
- `scripts/make_letters.py` renders the `.txt` sources into PDFs and a PNG with PyMuPDF.
- `run_evals.py` runs the real provider over all letters and prints a pass/fail table. It costs a few cents in Gemini mode.
- A small `--provider ollama` subset covers text letters only.

This is the learner's "run more trial cases" goal (`learner-profile.md`).
PRD ref: `prd.md > What We're Building`.

## Data Model
Pydantic models in `app/models.py`:

```
Sentence        { id: int, text: str }
Highlight       { sentence_id: int, kind: "deadline"|"action"|"docs"|"contact"|"flag" }
SummaryItem     { kind: "what"|"action"|"deadline"|"docs"|"contact"|"flag",
                  text_es: str, text_en: str, sentence_ids: [int], verified: bool = true }
ScamCheck       { flagged: bool, reasons_es: [str], reasons_en: [str] }
ReaderOutput    { language: str, transcribed: [Sentence] | null, translation: [Sentence],
                  highlights: [Highlight], summary: [SummaryItem], deadline: date | null,
                  needs_action: bool, incomplete: bool, incomplete_reason_es/en: str | null,
                  scam: ScamCheck }
VerifierOutput  { items: [{ ref: str, verdict: "ok"|"fixed"|"unverified", correction_es/en: str | null }],
                  scam_review: "agree"|"disagree", scam_note_es/en: str | null }
LetterResult    { original: [Sentence], translation: [Sentence], highlights: [Highlight],
                  summary: [SummaryItem], scam: ScamCheck, needs_action: bool,
                  deadline: date | null, deadline_passed: bool,
                  warnings: ["past_deadline"|"incomplete"|"image_source"], provider: str }
ErrorResult     { code: "cannot_read"|"unsupported_in_mode"|"provider_error" }
```

Where the data lives:
- **Uploaded file, extracted text, results:** in server memory for one request, then discarded. In the browser, in a JS variable until Start over or the tab closes. Nothing persists (`prd.md > States and Boundaries`).
- **Interface language:** `localStorage` key `lang`. It survives a reload; clearing it brings back the picker.
- **API key and provider:** `.env` on the learner's machine, never committed and never sent to the browser.

## File Structure
```
Build_With_AI_Basics/
├── app/
│   ├── main.py            # FastAPI app: routes, static files, error → HTTP status
│   ├── pipeline.py        # ingest → segment → reader → verifier → checks
│   ├── ingest.py          # file type detection, PDF/TXT text extraction
│   ├── segment.py         # deterministic sentence splitter
│   ├── checks.py          # code-level grounding checks, deadline_passed, warnings
│   ├── models.py          # Pydantic models (agent schemas + API response)
│   ├── config.py          # loads .env (provider, models, keys)
│   ├── agents/
│   │   ├── reader.py      # Reader prompt + call
│   │   └── verifier.py    # Verifier prompt + call
│   └── providers/
│       ├── __init__.py    # picks provider from PROVIDER
│       ├── gemini.py      # Gemini via google-genai (text, PDF text, images)
│       └── ollama.py      # Ollama via HTTP (text only)
├── static/
│   ├── index.html         # the one screen
│   ├── styles.css         # Preset A tokens and layout
│   ├── i18n.js            # all interface strings, es + en
│   └── app.js             # upload, render, highlights, scam gate, start over
├── test_letters/          # fabricated letters: .txt sources, generated .pdf/.png, expected.json
├── scripts/
│   └── make_letters.py    # renders .txt test letters into PDF/PNG
├── evals/
│   └── run_evals.py       # runs the real pipeline over test_letters, pass/fail table
├── tests/                 # pytest: segmenter, ingest, checks, pipeline with a fake provider
├── requirements.txt
├── .env.example           # PROVIDER, GEMINI_API_KEY, GEMINI_MODEL, OLLAMA_URL, OLLAMA_MODEL
├── .gitignore             # already ignores .env and devpost/learner-profile.md
├── README.md              # what it is, setup for both modes, Ollama limits, not legal advice
└── devpost/               # Devpost learning workspace
```

## External Services and Dependencies
- **Gemini API** (default). Auth with `GEMINI_API_KEY`.
  - **Calls:** two `generate_content` calls per letter (Reader, Verifier) with `response_mime_type: application/json` and a response schema derived from the Pydantic models. Images are sent as inline bytes, PDFs as extracted text.
  - **Cost:** paid from the learner's $8.52 credit. Flash-class pricing is expected to be well under one cent per letter; **verify at build start**.
  - **Rate limits:** depend on the account tier; verify.
  - Docs: https://ai.google.dev/gemini-api/docs, structured output: https://ai.google.dev/gemini-api/docs/structured-output
- **Ollama** (optional, local, free). `POST {OLLAMA_URL}/api/chat` with `{model, messages, format: <json schema>, stream: false}`, and the reply is read from `message.content`. No key needed. Text letters only in this project. Docs: https://github.com/ollama/ollama/blob/main/docs/api.md
- **Google Fonts:** Atkinson Hyperlegible via a stylesheet link, with a Verdana fallback if offline.
- **No hosting, no database, no other services.**

## Important Failure Modes
- **A model returns malformed or partial JSON** → retry once, then show the "something went wrong" message with Try again (`provider_error`). This is most likely with Ollama.
- **The Reader cites sentences that don't exist, or the verifier can't confirm a point** → the point is shown with "We could not verify this. Please check the original letter," never silently trusted.
- **A slow model (10–30 s for two calls)** → the processing animation keeps playing, and requests time out after about 90 s into `provider_error`.
- **A PDF with no text layer (a scanned image)** → in Gemini mode, send the rendered page image to the Reader as an image upload, with the `image_source` notice. In Ollama mode → `cannot_read`.

## What Was Simplified and Why
- **Sentence-level highlights** instead of exact phrase spans. Whole sentences make pairing across languages trivial and the grounding check exact. Phrase-level highlights would need character offsets in both languages.
- **No storage at all**, instead of history. This proves the kernel without handling sensitive letters (`prd.md > Deferred From the POC`).
- **A rule-based sentence splitter** instead of an NLP library. Official letters are formal prose, and edge cases get covered by unit tests.
- **Ollama mode limited to text letters**, instead of full parity. Local vision models are heavy and unreliable on letters, and the README explains this.
- **The left column shows a transcription for screenshots**, not the image itself with highlights. Drawing highlights on an image needs text position data. Mitigated by the verifier comparing against the image, plus the image-source notice.
- **No deployment.** A local run plus a recording satisfies the submission and avoids exposing the API key to strangers.

## Decisions and Open Issues
**Learner decisions:**
- **Stack:** Python + FastAPI + plain HTML/JS, accepted over React. FastAPI is new to the learner and doubles as a learning target.
- **Providers:** Gemini is the default (uses the existing $8.52 credit). Ollama is an optional free mode for people without an API key, limited to plain-text test letters and documented in the README.
- **Screenshot risk accepted (option a):** the verifier compares the transcription against the image, and a calm caution notice appears whenever an image is uploaded, explaining that reading an image is less reliable than real text. *(Added to `prd.md` as the image-upload notice.)*
- **Local only:** run locally and record; no deployment.
- **GitHub:** the learner sets up the repo and pushes themselves, with guidance.

**Implementation details derived from those decisions (agent-proposed, part of this review):**
- Code numbers the sentences before any AI call, and every output refers to sentence IDs.
- Two layers of checking: the Verifier agent for meaning, and plain code for existence and dates.
- `.txt` uploads are accepted (needed for Ollama mode). In Ollama mode, images get an "image reading needs Gemini mode" message.
- The language choice is kept in `localStorage`. This is a minor addition to "nothing persists": it stores no letter data.

**The useful unknown: FastAPI.** The learner hasn't used it. Resolution: once `app/main.py` and the first route exist in `5-build`, create a separate **FastAPI walkthrough artifact** that uses this project's real code (the routes, Pydantic models, file upload, static files, error handling, and how to try it from `/docs`). It's separate from the deliverables.

**Build workflow opportunities (learner goal: Claude capabilities not used before; decide in `5-build`):**
- a **hook** that runs `pytest` automatically after code edits
- **subagents** to draft the test letters in parallel
- `/code-review` on the finished code before shipping
- possibly a small project **skill** that runs the evals

**Open, not blocking:**
- (resolved) the project name: Communications Interpreter / Interpretador de Comunicaciones
- the final non-English message (decide during testing)
- the exact Gemini and Ollama model names (verify at build start)
