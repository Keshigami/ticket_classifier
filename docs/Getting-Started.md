# Getting started

## What you need
- [uv](https://docs.astral.sh/uv/) and [just](https://github.com/casey/just). On a Mac: `brew install uv just`.
- Python 3.11 is installed by uv.
- No API key is required: without one the app runs in a deterministic offline mode and says so on screen. Set `ANTHROPIC_API_KEY` (or `LLM_PROVIDER=openai` with `OPENAI_API_KEY`, or `gemini` with `GOOGLE_API_KEY`) in your shell for real model answers.

## Three commands
```bash
git clone https://github.com/Keshigami/ticket_classifier.git && cd ticket_classifier
just setup
just up           # http://127.0.0.1:8112/  (just down to stop)
```
Everything the app needs is in the repo (synthetic sample data where a dataset is used).

## Commands
`just setup`, `just train` where a model is trained, `just up` / `just down`, `just test`, `just demo`.

## What you see
- Run: `just ticket_classifier-setup && just ticket_classifier-up`, open `http://localhost:8112/`.
- Two-minute walkthrough: (1) read the header badge, it says offline or the model name; (2) click sample #2, the
  outage ticket, and look at priority and tags in the result card; (3) click sample #6, a two-tag ticket, and show
  the raw JSON; (4) `curl localhost:8112/health` and open `models/metrics.json`.
- Video clip: `demo/clips/portfolio__ticket_classifier.webm`.
- Sample inputs: `examples.json` (8 tickets with gold tags and priority). Offline, every ticket returns
  `billing / Low` with a placeholder action; with a key, #2 and #5 should come back Urgent, #3 Low.

## Try this
Try it: click ticket #2, read the JSON.
