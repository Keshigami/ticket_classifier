# How it was built

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

## Tech stack
| Layer | Choice | Why |
|---|---|---|
| Language and runtime | Python 3.11 via uv | one lockfile, same across the portfolio |
| Model or core logic | `common/llm.py` `complete_json` (Anthropic Haiku default; OpenAI / Gemini via env; offline fallback) | no provider code in the app, no key in source, tests run with no network |
| Interface | FastAPI + one HTML page on `common/ui.css` | no build step; `#input`, `#run`, `#result` for scripted demos |
| Data | `examples.json`, 8 hand-labelled tickets | enough for a smoke eval; the eval script scales to a larger file |
| Tests | pytest + FastAPI TestClient (7 tests) | API, validation, HTML page, eval file |

## Libraries
`fastapi` (routes and OpenAPI), `uvicorn` (server), `pydantic` (TicketResult validation and normalisation),
`anthropic` / `openai` / `google-genai` (providers behind the shared door), `httpx` (TestClient), `pytest`, `ruff`.
