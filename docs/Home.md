# Support Ticket Classifier

A FastAPI endpoint that turns a raw support ticket into validated JSON (tags, priority, next action) through a provider-agnostic LLM door, with an eval script that scores it. Portfolio, Applied AI, by Maximus Friedrich Baluyot.

**Watch first:** [the 90-second film](https://github.com/Keshigami/ticket_classifier/blob/main/demo/film.mp4).

## Pages
- [Getting started](Getting-Started.md): run it in three commands, what you see, the API.
- [How it was built](How-It-Was-Built.md): from the brief to a running service, step by step.
- [Results](Results.md): the numbers and what they mean.
- [Limits and next steps](Limits-and-Next-Steps.md): what it cannot do yet.
- [The film](The-Film.md): what the four chapters show.

## The brief
Support teams lose about a fifth of their time reading tickets just to tag and prioritise them before anyone can
act. This service takes the ticket text and returns tags, a priority and one suggested next step as JSON that a
routing system can consume. Solved means a triage queue that is pre-labelled, measured against hand labels, and
cheap enough to run on every ticket.

## The one-line answer
8/8 · tickets back as valid JSON · offline, no key

## One honest limit
Offline says Low; the hand label says High.
