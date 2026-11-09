<!-- public-top -->
# Support Ticket Classifier

A FastAPI endpoint that turns a raw support ticket into validated JSON (tags, priority, next action) through a provider-agnostic LLM door, with an eval script that scores it. Portfolio, Applied AI.

**Watch it first:** [the 90-second film](demo/film.mp4) (what it does, how it is built, the proof, the answer) or the [60-second cut](demo/film-60s.mp4). The plain walkthrough with captions is [demo/demo.mp4](demo/demo.mp4).

## Try it in three commands

```bash
git clone https://github.com/Keshigami/ticket_classifier.git && cd ticket_classifier
just setup        # creates the venv with uv (Python 3.11)
just up           # http://127.0.0.1:8112/  (just down to stop)
```

You need [uv](https://docs.astral.sh/uv/) and [just](https://github.com/casey/just) (`brew install uv just` on a Mac). Everything the app needs is in the repo (synthetic sample data where a dataset is used). No API key is required: without one the app runs in a deterministic offline mode and says so on screen. Set `ANTHROPIC_API_KEY` (or `LLM_PROVIDER=openai` with `OPENAI_API_KEY`, or `gemini` with `GOOGLE_API_KEY`) in your shell for real model answers. `just test` runs the lint and the offline tests.

Step by step: [docs/Getting-Started.md](docs/Getting-Started.md), then [how it was built](docs/How-It-Was-Built.md), [results](docs/Results.md), [limits](docs/Limits-and-Next-Steps.md) and [the film](docs/The-Film.md). The same pages are on the [wiki](https://github.com/Keshigami/ticket_classifier/wiki).
<!-- /public-top -->
# Support Ticket Classifier

## Demo walkthrough
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

Port 8112. FastAPI + one HTML page. LLM calls go through the repo's shared door (`common/llm.py`): Anthropic by
default, OpenAI or Gemini via env, and a deterministic offline mode when no key is set.

## 1. Problem Statement & Business Impact

- **The Problem**: High-volume support teams spend 20% of their time manually triaging and tagging tickets.
- **Goal**: Auto-tag and prioritize incoming tickets to reduce manual effort by 50%.
- **Metric of Success**: Accuracy > 90%, Latency < 2s per ticket.

## 2. Technical Solution

- **Approach**: A FastAPI endpoint asks the LLM for structured JSON (tags, priority, suggested action) with a schema
  hint, validates and normalises it with pydantic, and returns it for downstream routing.
- **Stack**: Python 3.11 (uv), FastAPI, pydantic v2, `common/llm.py` (anthropic / openai / google-genai SDKs), plain
  HTML + `common/ui.css` (no build step), pytest + TestClient, ruff.
- **Diagram**: [Webhook/Input] -> [FastAPI /classify] -> [common.llm.complete_json] -> [pydantic TicketResult] -> [Inbox Routing]

Tags: `billing, technical, feature_request, account, security, other`. Priority: `Low, Medium, High, Urgent`.

## 3. Evaluation & Results

`eval.py` scores the classifier on the 8 labelled tickets in `examples.json` and writes `models/metrics.json`
(priority accuracy, micro tag precision/recall/F1, exact match, mean latency, provider, model).

| Mode | priority_accuracy | tag_precision | tag_recall | tag_f1 | exact_match |
|---|---|---|---|---|---|
| offline (no key, this machine) | 0.25 | 0.25 | 0.20 | 0.222 | 0.0 |

The offline row is the floor: with no key the door answers the first option of every field (`billing`, `Low`), so
it is right only when the label happens to be that option. Run `ANTHROPIC_API_KEY=... just ticket_classifier-eval`
to overwrite the file with real numbers; a good result on this set is priority accuracy above 0.85 and tag F1 above
0.9 (the original README claimed >90% accuracy with GPT-3.5 but shipped no eval).

- **Tradeoffs**: The provider and model are chosen by env, not code, so cost tuning (Haiku vs Sonnet, gpt-4o-mini) is
  a one-line change. The original `eval()` of the model output was replaced with JSON parsing + pydantic validation.

## 4. How to run

```bash
just ticket_classifier-setup   # uv sync, copies common/ui.css into static/
just ticket_classifier-test    # ruff + 7 pytest tests, offline
just ticket_classifier-up      # background on :8112, pid in .pid, log in app.log
curl -s localhost:8112/health  # {"ok": true, "service": "ticket_classifier", "model_loaded": false, ...}
curl -s -X POST localhost:8112/classify -H 'content-type: application/json' \
  -d '{"ticket_text": "I was charged twice this month, please refund one invoice"}'
just ticket_classifier-eval    # writes models/metrics.json
just ticket_classifier-down
```

Set `ANTHROPIC_API_KEY` (or `OPENAI_API_KEY` / `GOOGLE_API_KEY`, or `LLM_PROVIDER` + `LLM_MODEL`) in the shell before
`-up` for real answers. No key is read from any file in this folder.

## 5. Two-minute interviewer walkthrough

1. Open `http://localhost:8112/`. The badge in the header shows the provider (`offline · deterministic` or the model).
2. Click sample ticket #2 ("dashboard shows a blank page... whole team is blocked"). The result card shows priority,
   tags as pills, the suggested action, latency and the raw JSON.
3. Paste your own ticket in the textarea and press Classify; try an ambiguous one ("invoice says my login is
   locked") and look at the multi-tag answer.
4. Open `/docs` for the OpenAPI page and `models/metrics.json` for the eval numbers; mention that `eval.py` reruns in
   seconds with a key.

## 6. What is real vs mocked

- Real: the HTTP API, the HTML page, the LLM call when a key is set, the pydantic normalisation (bad priorities fall
  back to Medium, tags are lowercased and de-duplicated), the eval script and its metrics file.
- Offline (no key): `common/llm.py` returns a deterministic schema-shaped answer, so every ticket gets `billing / Low`
  and a placeholder action. The page and the JSON say so.
- Not built: the inbox routing after classification (the diagram's last box) is out of scope here.

## 7. Case Study Narrative

- **Context**: Demonstrates applied NLP and LLM integration into standard software architectures.
- **Implementation**: A small API that takes unstructured text and returns schema-validated JSON for downstream automation.
- **Limitations**: 8 labelled examples is a smoke eval, not a benchmark; tag consistency depends on the system prompt.
- **Next Steps**: Few-shot examples in the prompt for niche technical queries; a 200-ticket labelled set and a
  confusion matrix in the metrics file.

## Standalone repo

Exported from Max's `caltech-capstone` workspace. `common/` is vendored (LLM door, UI tokens). Run: `just setup && just test && just up`.
LLM-backed features read `ANTHROPIC_API_KEY` (or `LLM_PROVIDER` + `OPENAI_API_KEY` / `GOOGLE_API_KEY`); with no key they run in a deterministic offline mode.
Film: `demo/film.mp4` (90 s, what it does, how it is built, the proof, the answer) and `demo/film-60s.mp4` (60 s cut); `demo/demo.mp4` is the plain walkthrough.
