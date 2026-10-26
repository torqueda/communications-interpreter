---
doc: scope
status: approved
---

# Communications Interpreter

Upload an official English letter and get it back in plain Spanish: a side-by-side translation with the important sentences color-matched across both languages, and a short summary of what the letter is, what it asks, by when, and who to contact.

## The Unique Kernel
The family doesn't have to know how to prompt, what to ask, or how to check the answer. Every letter goes through the same purpose-built workflow: the important information is extracted, **every point is traced back to the exact sentence it came from** (color-coded in both the original and the translation), a verifier agent checks the output, and suspicious letters get flagged as possible scams. It's a free tool, not a product: "if you need help with this specific scenario, here's a tool you or your family can use."

## Who It's For
First-generation Hispanic immigrant adults who struggle with English, and the bilingual family members who help them. One example: a parent gets a Medicaid notice in their online portal, downloads it as a PDF or takes a screenshot, and needs to know whether it's urgent and what to do. Today they guess, wait for a relative to read it, or paste it into a general chatbot without knowing whether to trust the answer. Because both the adult and the helper use it, the interface switches between English and Spanish.

## The Core Loop
Open the app, then drop in or browse for a letter (PDF or image). A friendly animation plays while it works. On the same screen they see:
- The original on the left and the Spanish translation on the right. Key sentences (deadlines, required documents, contacts) are highlighted in matching colors so they can see it's the same information in both languages.
- Below that, a short summary: what the letter is, what it asks, and, when relevant, what to do, by when, with what documents, and who to contact.
- A clear warning if the letter looks like phishing or a scam.

They come back whenever another letter arrives.

## Inspiration & Identity
Warm and reassuring, not bureaucratic. A greeting and a brief explanation of what the app does, one prominent upload area, a "cute animation" while it works. Everything happens on one screen, plus a disclosures/about section ("not legal advice"). Draws on the learner's translator experience and their Benefits Navigator multi-agent project.

## Why This Matters to the Learner
It combines their part-time translation work, their Benefits Navigator master's project, and their research on LLM hallucinations and how to fix them. It's a portfolio piece, possibly developed further afterward, but "I don't want to give an incomplete app to people that need help." Older adults and people still learning English are "particularly vulnerable" to malicious letters. This time they want to "run more trial cases, contemplating more potential scenarios for right and wrong outcomes."

## What "Working" Looks Like
A made-up, confusing, official-looking letter (e.g., a Medicaid-style notice) is uploaded as a PDF or screenshot. Within a minute the screen shows the color-matched side-by-side and a short summary of what to do, by when, and who to contact. **The "oh, that's cool" beat:** a color-coded deadline in the Spanish text matches the same color in the English original, so anyone can check it.

It also behaves sensibly across a set of trial letters:
- a normal letter requiring follow-up
- an informational letter with no action needed
- a past deadline
- missing contact information (e.g., a partial screenshot)
- a letter not in English (e.g., French)
- an obvious phishing or scam letter
- others identified during planning

## The POC Boundary
- Single-file upload: one PDF or one image
- Side-by-side original and Spanish translation with color-matched highlights of key sentences (they don't need to line up line-by-line)
- Structured summary: what it is, what it asks, deadline, required documents, who to contact
- Verifier agent that checks the translation and extraction
- Scam/phishing flag
- English/Spanish interface toggle
- Disclosures section with a "not legal advice" note
- A set of made-up test letters covering the scenarios above
- All demo letters are fabricated; no real personal data

## Later
- Multiple screenshots of one letter, including out-of-order parts (documented so it isn't forgotten)
- History tabs: previously uploaded documents and past sessions (requires storing sensitive letters, so needs a privacy design)
- Save the deadline to a calendar
- Photos of physical paper letters as a first-class input (mentioned in the README as a next step, not stubbed in code)
- Hardening for real users before recommending it to anyone

## Explicitly Cut
- A code skeleton for physical-letter capture: costs build time without showing up in the demo; documented under Later instead
- Monetization: deliberately free; the goal is access, not a product to sell
