# Criterion Rating carrier candidate

**Yes: a concrete Criterion Rating needs an Artifact Type contract.** Its [Definition record](../../../definition-records/criterion-rating/definition.json) supplies meaning; it does not constrain the machine fields of an individual rating.

The current Lab Artifact Type registry has no Criterion Rating carrier. The [Artifact Type Request](request.json) records that zero-match result against a pinned registry and explains why Measurement Result, Evaluation and Observation do not supply the needed contract. Its [generated view](REQUEST.md) is a reading aid.

The [candidate type descriptor](artifact.json) proposes `ea.artifact-type.criterion-rating/v1-candidate` with the [closed instance schema](schema.json). The [synthetic fixture](fixtures/synthetic-rating.json) demonstrates a single blind human `3` on one dimension. It is **not a participant rating**. The type requires exact scoring-run, response, case, rubric, dimension, rater, mode and source refs. It distinguishes numeric `0–4` from `NA` and `UNK`; `0–1` requires a cited missed opportunity, while `2–4` requires an evidence span. A model rating stays provisional. The descriptor also proposes an append-only version rule and a uniqueness key for implementation review.

This is an artifact-type **candidate in the project workspace**, not a Lab-admitted Artifact Type/v3 instance. The underlying `ea.criterion-rating` Definition is still candidate-unadmitted; inventing an admission decision reference to satisfy Lab/v3 would misstate its standing. A semantic owner must review that Definition first, then the Artifact Type owner can prepare an exact Lab/v3 candidate with its real binding, schema and registry route. A schema pass cannot establish cross-record reference closure or rater independence.

Run `python3 tools/validate_criterion_rating_carrier.py` from the project root. It verifies the Lab Artifact Type Request shape, pinned zero-match basis, Definition/schema digests, synthetic fixture and six negative cases. There are no live rating instances, calibrated score values or employment-use permissions.
