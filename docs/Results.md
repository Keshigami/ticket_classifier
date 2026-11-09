# Results

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
