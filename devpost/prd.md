---
doc: prd
status: approved
---

# Communications Interpreter — Product Requirements

A one-screen web app that turns an official English letter into plain Spanish: a side-by-side translation with key sentences color- and icon-matched across both languages, a short summary, and a scam warning when something looks wrong. For first-generation Hispanic immigrant adults who struggle with English and the bilingual family members who help them.
Source: `scope.md > The Unique Kernel`, `scope.md > Who It's For`.

## The Core Journey
Source: `scope.md > The Core Loop`, `scope.md > What "Working" Looks Like`.

1. **First open.** The person sees a language choice (Español / English) with a note that they can switch at any time.
2. **Upload screen.** In the chosen language: a greeting, a one-line explanation of what the app does, and a large upload area (drag a file in or click to browse; one PDF or one image).
3. **Processing.** A friendly animation plays while the letter is read, translated, and checked.
4. **Scam check (only if flagged).** A warning appears first, listing the specific reasons the letter was flagged and what to do instead. The person ticks "I understand" to see the translation.
5. **Results, on the same screen:**
   - Side by side: the original English letter on the left and the Spanish translation on the right. Key sentences are highlighted with matching colors and icons in both versions.
   - Below them: a short summary (what the letter is, what it asks, deadline, documents needed, who to contact), each point with a "Show in letter" link.
6. **Exploring.** Clicking a highlighted sentence flashes its twin in the other language and shows a short tooltip explaining what it is. "Show in letter" scrolls to the matching sentences and flashes them.
7. **Finishing.** "Start over" clears everything and returns to the upload screen. Nothing is saved.

**Success:** someone who can't read English knows what the letter is, whether they need to act, by when, with what, and who to contact, and can see exactly where in the original each fact came from.

## Screens and Layout
One screen; its content changes by state. No other pages.

- **Top bar** (always visible, stays fixed while scrolling): app name on the left, Español/English toggle in the top-right corner.
- **Body**, top to bottom: greeting and explanation → upload area → (scam warning, if flagged) → side-by-side letters → summary → Start over (centered) → "not legal advice" note.
- **Disclosures:** a link in the top bar or footer opens the disclosures and about text (what the app does, its limits, not legal advice, nothing stored). *Assumption: an expandable section or panel on the same screen, not a separate page.*
- **Narrow screens:** the two letters stack (original first, then translation).

## Look and Feel
Chosen direction: **Preset A, "Clear paper"** (see `devpost/style-options.html`).

- **Colors:** cool off-white background, white surfaces, deep ink-blue text and primary buttons. Soft highlighter-marker colors for highlight types: yellow = deadline, peach = what to do, lavender = documents, mint = contact. **Red is reserved for scam warnings only.**
- **Font:** Atkinson Hyperlegible throughout (designed for low-vision readers).
- **Readability for older adults:** body text about 18px; buttons and tap targets at least 44px tall; text contrast at least 4.5:1.
- **Color is never the only signal:** every highlight carries a small icon (calendar, check, document, phone, warning) that matches across both languages and the summary.
- **Line length without awkward gaps (learner requirement):** text blocks keep a comfortable reading width (about 60–70 characters per line), but the container is sized to that width, or the lines are balanced. A sentence should never end on a short leftover line with a big empty space beside it. Check this on short intro and explanation text especially.
- **Tone:** calm and reassuring, but formal and courteous: no contractions in English ("we will", not "we'll"), "proceed with caution" rather than "be careful", and "Por favor" on instructions in Spanish. Not bureaucratic. Avoid generic AI-app styling (gradients, glowing dark mode, everything in rounded cards).

## Features and Behavior

### Interface Language
- On first open, the person picks Español or English; a note says they can switch any time.
- The toggle is fixed in the top-right corner and stays visible while scrolling.
- Switching changes all interface text (labels, buttons, summary, warnings, tooltips) instantly, without losing the current results. The translation column is always Spanish; the original is always the uploaded English.
  - [ ] First open shows the choice and the "switch any time" note.
  - [ ] Switching mid-results changes the interface text and keeps the letters and summary on screen.
  - [ ] The toggle remains visible after scrolling to the bottom.

### Uploading a Letter
Source: `scope.md > The POC Boundary` (single-file upload).
- One PDF or one image, by drag-and-drop or by clicking the area to browse. Plain-text (.txt) files are also accepted (added in `4-spec` for the free local mode).
- The upload area is the most prominent element on the screen before results appear.
- **Image upload notice** (added in `4-spec`): when the upload is an image, a small calm caution box explains that the app had to read the text from a picture, which is less reliable than a real text document, and suggests uploading the PDF if they have it.
  - [ ] Dropping or choosing a PDF starts processing.
  - [ ] Dropping or choosing a PNG/JPG screenshot starts processing.
  - [ ] Image uploads show the image-reading caution box with the results; PDF uploads don't.

### Processing Animation
- A friendly animation plays while the app works, so the person knows it hasn't frozen.
  - [ ] The animation appears immediately after upload and disappears when results or a message appear.

### Side-by-Side Letters with Matched Highlights
Source: `scope.md > The Unique Kernel`.
- The original (left) and the Spanish translation (right) are shown in full.
- Key sentences (deadline, what to do, documents needed, contact) are highlighted in both versions with the same color and icon. The lines don't need to align; the matching color and icon show they're the same information.
  - [ ] Every highlight in the translation has a matching highlight in the original, with the same color and icon.
  - [ ] Every highlighted sentence in the original actually appears in the uploaded letter (no invented text).

### Highlight Interactions
- Clicking (or tapping, or pressing Enter on) a highlighted sentence:
  1. flashes its twin in the other language, and
  2. shows a short tooltip in the interface language explaining what it is ("This is your deadline", "This is who to contact", …).
  - [ ] Clicking a highlight in either column flashes the matching sentence in the other column.
  - [ ] A tooltip appears near the clicked sentence and goes away on its own.

### Summary with "Show in Letter"
- Below the letters: what the letter is, what it asks, deadline, documents needed, and who to contact. Only items that apply are shown.
- Each point (except "what it is") has its icon and a "Show in letter" link that scrolls to the matching sentences and flashes them in both columns.
  - [ ] Every summary point except "what it is" links to at least one highlighted sentence.
  - [ ] "Show in letter" scrolls the matching sentence into view and flashes it in both columns.

### Scam Warning
Source: learner addition during scope, `scope.md > The POC Boundary`.
- When a letter looks malicious, a warning appears **before** the translation, listing the specific reasons (e.g., gift-card payment, a web address that isn't .gov, extreme urgency, a request for a Social Security number).
- It says the app can be wrong and tells them to contact the agency through its official website, not the details in the letter.
- The warning box is centered on the page.
- An "I understand" checkbox reveals the translation and summary. Red flags are highlighted in the letters with the warning color and icon.
- Reasons are shown, not just a label, because the agents can mistakenly flag an official letter or miss a malicious one; the person needs to judge for themselves.
  - [ ] The test phishing letter shows the warning with specific reasons before anything else.
  - [ ] The translation is hidden until "I understand" is ticked.
  - [ ] Normal official test letters do not show the warning.

### Letter Checking (Verifier)
Source: `scope.md > The Unique Kernel`.
- Before results appear, a second check confirms that each summary point and highlight is supported by a sentence in the original, and reviews the scam decision.
- Points the verifier confirms (or corrects) appear normally.
- A point the verifier can't confirm or fix is **still shown, with a visible label**: "We could not verify this. Please check the original letter" (in the interface language). Uncertainty is shown, not hidden.
  - [ ] Across the test letters, no summary point appears without a matching sentence in the original unless it carries the "could not verify" label.
  - [ ] When a point fails verification, the label appears next to it in both interface languages.

### Start Over
- **Start over:** clears the letter and results and returns to the upload screen.
- Nothing is saved.
  - [ ] After Start over, no part of the previous letter remains on screen.

### Disclosures
- A "not legal advice" note is always visible under the results.
- The disclosures section explains what the app does, that results can be wrong, that nothing is stored, and that it is not legal advice.
  - [ ] The note and disclosures are available in both interface languages.

## States and Boundaries
- **First open:** language choice, then the upload screen.
- **Ready to upload:** greeting, explanation, upload area. No results area yet.
- **Processing:** animation; upload area inactive.
- **Normal letter with action needed:** full results.
- **Informational letter (nothing to do)**, e.g., an "we received your application" notice: the summary still conveys what the message means and states clearly that no further steps are needed from them at this time.
- **Past deadline:** the deadline is still shown, plus a small warning box above the summary explaining that the date has already passed.
- **Missing information / incomplete letter** (e.g., a partial screenshot with no contact details, or text that's cut off): a small warning box explaining that the letter appears incomplete and what seems to be missing, suggesting they check that the whole letter was uploaded.
- **Warning boxes** (past deadline, incomplete letter) use a calm caution style, not red; red stays reserved for scam warnings.
- **Possible scam:** warning first, then results after "I understand."
- **Can't be read** (blank, unreadable, not a letter, or not in English): the message "No pudimos leer este documento. Por favor, verifique el tipo e idioma del documento e intente nuevamente." (English: "We could not read this document. Please verify the type and language of the document and try again."); no results are shown. Non-English letters get this same message for now (final decision during testing).
- **Something went wrong while processing:** the same calm message style, with an option to try again.
- **Persistence:** none. Nothing survives Start over or closing the tab.

## Product Decisions
- Interface language is chosen on first open and switchable any time from a fixed top-right toggle, because both the adult and a bilingual helper use the app.
- Full side-by-side translation (not just a summary), with matched color + icon highlights instead of line-by-line alignment.
- Summary points link back via "Show in letter" (kernel: every point traced to its source).
- Clicking a highlight does both: flashes its twin and shows a tooltip.
- Scam letters still get translated; the warning comes first with reasons and an "I understand" check, because the agents can be wrong in either direction.
- Non-English letters show the generic "can't be read" message for now; revisit during testing depending on time.
- One exit option: a centered "Start over" button. A "Close" button that redirected to cat-bounce.com was cut after the learner's review of the built app.
- Visual direction: Preset A ("Clear paper") with Atkinson Hyperlegible.
- No storage of letters in the proof of concept.
- Unverifiable points are shown with a "We could not verify this. Please check the original letter" label rather than dropped: surfacing uncertainty beats hiding it.
- Informational letters still get their meaning explained, plus a clear "no further steps needed at this time."
- Past deadlines and incomplete letters get a small warning box explaining the issue.

## What We're Building
Everything under **Features and Behavior**, covering the states above, plus a set of made-up test letters: normal with follow-up, informational, past deadline, missing contact info, not in English (French), obvious phishing, and any added during testing. All demo letters are fabricated.

## Deferred From the POC
- **Multiple screenshots of one letter, possibly out of order:** a different input problem with its own failure cases (`scope.md > Later`).
- **Follow-up and supporting letters linked to an earlier letter:** needs memory across uploads, like history.
- **History tabs (past letters and sessions):** requires storing sensitive letters and a privacy design.
- **Save deadline to calendar:** `scope.md > Later`.
- **Photos of physical paper letters:** README next step only.
- **Translating non-English letters:** placeholder message for now.

## Possible Later Enhancements
- Support for more source and target languages.
- Read-aloud of the Spanish summary for people who find reading difficult.
- A dedicated, specific message for non-English letters instead of the generic "can't be read."

## Non-Goals
- Legal advice or recommendations beyond what the letter itself says.
- Contacting agencies on the user's behalf.
- Accounts, logins, or saving anything.
- Monetization (`scope.md > Explicitly Cut`).
- Handling real people's letters during the hackathon; demo letters are fabricated.

## Open Questions
- **Disclosures placement:** assumed to open on the same screen (expandable section or panel); approved as-is, final form can be settled in `4-spec`.
- **Project name:** decided: Communications Interpreter / Interpretador de Comunicaciones.
- **Non-English letters:** final message decided during testing; not blocking.
