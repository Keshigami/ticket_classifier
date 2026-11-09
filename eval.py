"""Score the classifier against the labelled tickets in examples.json and write models/metrics.json.

    uv run python eval.py            # offline: deterministic schema defaults, a floor to beat
    ANTHROPIC_API_KEY=... uv run python eval.py   # real scoring

Metrics: priority accuracy, tag precision / recall / F1 (micro over tag sets), exact match, mean latency.
"""
from __future__ import annotations

import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from classifier import classify, llm

HERE = Path(__file__).resolve().parent


def score(examples: list[dict], predict=classify) -> dict:
    tp = fp = fn = 0
    prio_ok = exact = 0
    latencies = []
    rows = []
    for ex in examples:
        t0 = time.perf_counter()
        res = predict(ex["ticket_text"])
        latencies.append(time.perf_counter() - t0)
        gold, pred = set(ex["tags"]), set(res.tags)
        tp += len(gold & pred)
        fp += len(pred - gold)
        fn += len(gold - pred)
        p_ok = res.priority == ex["priority"]
        prio_ok += p_ok
        exact += p_ok and gold == pred
        rows.append({"id": ex["id"], "gold_tags": sorted(gold), "pred_tags": sorted(pred),
                     "gold_priority": ex["priority"], "pred_priority": res.priority})
    n = len(examples)
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return {
        "provider": llm.provider(),
        "model": llm.model(),
        "n": n,
        "priority_accuracy": round(prio_ok / n, 3),
        "tag_precision": round(prec, 3),
        "tag_recall": round(rec, 3),
        "tag_f1": round(f1, 3),
        "exact_match": round(exact / n, 3),
        "mean_latency_s": round(sum(latencies) / n, 3),
        "evaluated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "rows": rows,
    }


def main(out: Path | None = None) -> dict:
    examples = json.loads((HERE / "examples.json").read_text())
    metrics = score(examples)
    out = out or HERE / "models" / "metrics.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(metrics, indent=2) + "\n")
    summary = {k: v for k, v in metrics.items() if k != "rows"}
    print(json.dumps(summary, indent=2))
    print(f"wrote {out}")
    return metrics


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
