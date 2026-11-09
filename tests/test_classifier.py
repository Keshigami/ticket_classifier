import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

import classifier  # noqa: E402
import eval as evalmod  # noqa: E402
from main import app  # noqa: E402


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "offline")
    for k in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GOOGLE_API_KEY"):
        monkeypatch.delenv(k, raising=False)


client = TestClient(app)


def test_classify_offline_is_deterministic():
    a = classifier.classify("I was charged twice, refund please")
    b = classifier.classify("I was charged twice, refund please")
    assert a == b
    assert a.priority in classifier.PRIORITIES
    assert a.tags and all(t in classifier.TAGS for t in a.tags)
    assert a.provider == "offline"


def test_classify_rejects_empty():
    with pytest.raises(ValueError):
        classifier.classify("   ")


def test_result_normalises_bad_values():
    r = classifier.TicketResult(tags="Billing, Feature Request", priority="urgent!", suggested_action="x")
    assert r.tags == ["billing", "feature_request"]
    assert r.priority == "Medium"  # unknown value falls back
    assert classifier.TicketResult(tags=[], priority="high").priority == "High"
    assert classifier.TicketResult(tags=[]).tags == ["other"]


def test_post_classify():
    r = client.post("/classify", json={"ticket_text": "Dashboard is down for everyone"})
    assert r.status_code == 200
    body = r.json()
    assert set(body) >= {"tags", "priority", "suggested_action", "provider", "model"}
    assert body["priority"] in classifier.PRIORITIES


def test_post_classify_empty_is_422():
    assert client.post("/classify", json={"ticket_text": ""}).status_code == 422


def test_root_html_and_examples():
    r = client.get("/")
    assert r.status_code == 200 and "<textarea" in r.text and "__META__" not in r.text
    ex = client.get("/examples").json()
    assert len(ex) == 8 and all({"ticket_text", "tags", "priority"} <= set(e) for e in ex)
    h = client.get("/health").json()
    assert h["ok"] is True and h["service"] == "ticket_classifier" and h["model_loaded"] is False


def test_eval_writes_metrics(tmp_path):
    out = tmp_path / "metrics.json"
    m = evalmod.main(out)
    data = json.loads(out.read_text())
    assert data["n"] == 8 and 0 <= data["priority_accuracy"] <= 1 and 0 <= data["tag_f1"] <= 1
    assert m["provider"] == "offline" and len(m["rows"]) == 8
