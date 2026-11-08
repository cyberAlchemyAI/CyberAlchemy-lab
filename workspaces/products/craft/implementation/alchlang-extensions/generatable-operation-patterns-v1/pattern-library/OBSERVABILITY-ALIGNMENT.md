# Observability alignment

The CLI emits machine-readable pattern rows containing prerequisite states,
availability and blockers. Future generators must additionally expose:

- selected `pattern_id`, meta-type and binding IDs;
- generator version and input/output digests;
- validation and conformance result;
- generated artifact manifest;
- runtime facts appropriate to the pattern, such as Outbox publication lag,
  attempts and deduplication outcomes.

Observability is evidence only. It cannot promote stability or authorize an
effect.
