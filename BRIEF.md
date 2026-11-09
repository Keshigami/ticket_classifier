---
title: Support Ticket Classifier
group: portfolio
role: Applied AI
port: 8112
status: working
one_liner: A FastAPI endpoint that turns a raw support ticket into validated JSON (tags, priority, next action) through a provider-agnostic LLM door, with an eval script that scores it.
---
# Support Ticket Classifier

## Demo
<!-- demo:auto -->
![demo](demo/demo.gif)

Full walkthrough with captions: [demo/demo.mp4](demo/demo.mp4) (67 s, 1280x800, animated intro and end card). Run it yourself: `just setup && just up`, then open http://localhost:8112/.

Two-minute walkthrough:
1. Eight labelled sample tickets; one click classifies
2. A billing ticket: priority, tags and a suggested action, as JSON
3. Technical and urgent: a blank dashboard after login
4. A feature request: low priority
5. The raw JSON the inbox would route on
6. The badge says which provider and model answered
7. Or paste your own ticket and press Classify
<!-- /demo:auto -->

## Brief
Support teams lose about a fifth of their time reading tickets just to tag and prioritise them before anyone can
act. This service takes the ticket text and returns tags, a priority and one suggested next step as JSON that a
routing system can consume. Solved means a triage queue that is pre-labelled, measured against hand labels, and
cheap enough to run on every ticket.

## Tech stack
| Layer | Choice | Why |
|---|---|---|
| Language and runtime | Python 3.11 via uv | one lockfile, same across the portfolio |
| Model or core logic | `common/llm.py` `complete_json` (Anthropic Haiku default; OpenAI / Gemini via env; offline fallback) | no provider code in the app, no key in source, tests run with no network |
| Interface | FastAPI + one HTML page on `common/ui.css` | no build step; `#input`, `#run`, `#result` for scripted demos |
| Data | `examples.json`, 8 hand-labelled tickets | enough for a smoke eval; the eval script scales to a larger file |
| Tests | pytest + FastAPI TestClient (7 tests) | API, validation, HTML page, eval file |

## Libraries used
`fastapi` (routes and OpenAPI), `uvicorn` (server), `pydantic` (TicketResult validation and normalisation),
`anthropic` / `openai` / `google-genai` (providers behind the shared door), `httpx` (TestClient), `pytest`, `ruff`.

## How it was built
1. Read the original `main.py`: OpenAI `gpt-3.5-turbo` in JSON mode, `eval()` on the model output, a hard-coded mock
   when the key was missing, and a JSON root route. The README promised >90% accuracy with no eval.
2. Moved the LLM call to `common/llm.py` with a schema hint (`tags`, `priority`, `suggested_action`); dropped the
   OpenAI SDK import and the `eval()`.
3. Added `TicketResult` validators: tags lowercased and de-duplicated, unknown priorities fall back to Medium, empty
   tags become `other`, and the response carries `provider` and `model` so the UI can show what answered.
4. Wrote the HTML page (textarea, eight one-click sample tickets, result card, raw JSON, provider badge) on the shared
   `ui.css`, plus `/health`, `/examples` and `/static`.
5. Wrote `eval.py`: priority accuracy, micro tag precision/recall/F1, exact match, latency, written to
   `models/metrics.json`; it runs offline (deterministic floor) and with a key (real score).
6. Tests and ruff; `just` recipes for setup, test, up (pid file), down and eval.

## Results
From `models/metrics.json` on this machine, offline mode (no key available in the build environment):

| Metric | Offline | What a good number is |
|---|---|---|
| priority_accuracy | 0.25 | > 0.85 |
| tag_f1 (micro) | 0.222 | > 0.90 |
| exact_match | 0.0 | > 0.75 |
| mean_latency_s | 0.0 | < 2 s with a real model |

Offline, the door answers the first option of every field, so 0.25 is the share of tickets labelled `Low` and the
tag score is the share tagged `billing`. The real number needs `ANTHROPIC_API_KEY=... just ticket_classifier-eval`,
which overwrites the file with the provider and model named inside it.

## Demo details
- Run: `just ticket_classifier-setup && just ticket_classifier-up`, open `http://localhost:8112/`.
- Two-minute walkthrough: (1) read the header badge, it says offline or the model name; (2) click sample #2, the
  outage ticket, and look at priority and tags in the result card; (3) click sample #6, a two-tag ticket, and show
  the raw JSON; (4) `curl localhost:8112/health` and open `models/metrics.json`.
- Video clip: `demo/clips/portfolio__ticket_classifier.webm`.
- Sample inputs: `examples.json` (8 tickets with gold tags and priority). Offline, every ticket returns
  `billing / Low` with a placeholder action; with a key, #2 and #5 should come back Urgent, #3 Low.

## Limits and next steps
- Offline mode is a placeholder, not a classifier; it exists so the demo and tests never need a key.
- Eight examples measure plumbing, not accuracy; a 200-ticket labelled set with a confusion matrix is the next step.
- No few-shot examples in the prompt yet; tag drift on niche technical tickets is the known weak spot.
- Routing after classification (CRM, queue) is not built; the API is the contract for it.
