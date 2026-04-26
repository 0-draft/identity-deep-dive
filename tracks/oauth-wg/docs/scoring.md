# Scoring

`scripts/score.py` determines priority by summing the following components.

## 1. Lifecycle (Datatracker states)

Higher values mean higher priority:

- In Last Call: +80
- In WG Last Call: +70
- IESG Evaluation: +70
- RFC Ed Queue: +65
- AD Evaluation: +55
- WG Consensus: Waiting for Write-Up: +50
- Submitted to IESG for Publication: +45
- Publication Requested: +40
- WG Document: +20
- I-D Exists only: +10

## 2. Recency

Points added based on how recently `updated_at` changed:

- Within 3 days: +25
- Within 7 days: +18
- Within 30 days: +8

## 3. Activity (14 days)

Per-repo activity reflected on the draft:

- org events
- recent PR
- recent issues

Points added: `min(30, activity_weight * 2)`.

## 4. Open Issues

- Over 30: +15
- Over 10: +8

## Output

`data/normalized/backlog.json`

- `candidates[]` output sorted by `score` in descending order
- Each candidate has `reasons[]` attached
