# Limits and next steps

- Offline mode is a placeholder, not a classifier; it exists so the demo and tests never need a key.
- Eight examples measure plumbing, not accuracy; a 200-ticket labelled set with a confusion matrix is the next step.
- No few-shot examples in the prompt yet; tag drift on niche technical tickets is the known weak spot.
- Routing after classification (CRM, queue) is not built; the API is the contract for it.
