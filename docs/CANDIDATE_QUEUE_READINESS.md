# Candidate Queue Readiness

The discovery queue has a separate readiness gate from production readiness.

This distinction matters:

- **candidate readiness** means there is enough discovery coverage to justify manual review;
- **production readiness** means reviewed places have actually been promoted and are usable by travelers.

The candidate gate requires:

- at least one restaurant in every target corridor province,
- at least one mosque in every target corridor province,
- accommodation candidates in at least two target provinces.

Run:

```bash
cd apps/api
python -m app.tools.candidate_queue_readiness \
  ../../database/seeds/pilot_candidates_review_queue.csv
```

Passing this gate does **not** make the public pilot ready. Coordinates, evidence,
duplicate checks and admin approval are still required before promotion.
