"""Support Ticket Classifier API: POST /classify, GET / (HTML page), GET /examples, GET /health.

Run: uv run uvicorn main:app --port 8112
"""
from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from classifier import PRIORITIES, TAGS, TicketResult, classify, llm

HERE = Path(__file__).resolve().parent
EXAMPLES = json.loads((HERE / "examples.json").read_text())

app = FastAPI(title="Support Ticket Classifier API", version="1.0.0")
STATIC = HERE / "static"
if not (STATIC / "ui.css").exists():  # shared look lives in common/ui.css; copy once
    STATIC.mkdir(exist_ok=True)
    (STATIC / "ui.css").write_text((HERE.parents[1] / "common" / "ui.css").read_text())
app.mount("/static", StaticFiles(directory=STATIC), name="static")


class TicketRequest(BaseModel):
    ticket_text: str


@app.get("/health")
def health():
    p = llm.provider()
    return {"ok": True, "service": "ticket_classifier", "model_loaded": p != "offline",
            "provider": p, "model": llm.model()}


@app.get("/examples")
def examples():
    return EXAMPLES


@app.post("/classify", response_model=TicketResult)
def classify_ticket(req: TicketRequest):
    try:
        return classify(req.ticket_text)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:  # provider/network errors
        raise HTTPException(status_code=502, detail=f"LLM call failed: {e}") from e


@app.get("/", response_class=HTMLResponse)
def root():
    meta = {"provider": llm.provider(), "model": llm.model(), "tags": TAGS, "priorities": PRIORITIES, "port": 8112}
    return (HERE / "index.html").read_text().replace("__META__", json.dumps(meta))
