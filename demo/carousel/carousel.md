# Support ticket classifier · carousel

Spec: film/specs/portfolio__ticket_classifier.json · 8 slides, 1080x1350.

## 1/8 Hook

- Tags, priority, action: valid JSON, every time.

## 2/8 The question

- Two of eight are urgent.
- Does the schema hold with no key?
- #2 blank dashboard: 4 · 20% of total

## 3/8 What it does

- Support ticket classifier
- Portfolio · Applied AI
- Raw ticket in, validated JSON out, scored
- max@baluyot ~ $ curl -s localhost:8112/classify -H 'content-type: application/json' -d '{"ticket_text":"I was charged twice for my Pro subscription this month."}'

## 4/8 How it is built

- 1. examples.json, 8 hand-labelled tickets — fastapi
- 2. one prompt + a schema hint — fastapi
- 3. common/llm.py complete_json · offline fallback — fastapi · uvicorn · pydantic
- 4. FastAPI + one HTML page on common/ui.css — FastAPI
- 5. Dashboard — HTML + ui.css
- Unknown priority falls back to Medium

## 5/8 The result

- Offline eval · models/metrics.json · the floor
- tag F1, micro · 0.222 · > 0.90 wanted
- exact match · 0.00 · > 0.75 wanted
- valid JSON · 8 / 8 · 8 / 8 (highlighted)

## 6/8 The proof

- Ticket #1: billing, as JSON
- screen: portfolio/ticket_classifier/demo/poster.png

## 7/8 The answer and the limit

- 8/8
- tickets back as valid JSON · offline, no key
- Offline says Low; the hand label says High.
- And it ships.

## 8/8 Try it

- Try it: click ticket #2, read the JSON.
- max@baluyot ~ $ git clone https://github.com/Keshigami/ticket_classifier.git
- max@baluyot ~ $ just ticket_classifier-setup
- max@baluyot ~ $ just ticket_classifier-up
- github.com/Keshigami/ticket_classifier
- Maximus Friedrich Baluyot
- AI & ML Specialist · Applied AI · ML Engineering · Automation

_Maximus Friedrich Baluyot · Caltech CTME · PGC AIML_
