# Pricing with a derived ontology

`quantity-price.alch` is the declarative pricing example with redundant ontology blocks and explicit IDs removed. Business descriptions remain where authored; structure is derived. The behavioral clauses, boundary schemas and integration bindings retain the predecessor's pricing scope.

Build or inspect using the commands in [the ontology guide](../../alchlang/docs/ONTOLOGY.md). The build emits `ontology.json` beside `behavior.mjs`. The `explain` command answers a named declaration from this same validated source model, including source evidence and dependencies.

## Evidence

Current validation: 105 tests passed, typecheck passed, and all 20 pricing fixtures passed against the final generated bundle.

`evidence/alch-tests.log` records the full regression suite, including derivation, provenance, annotation-free compilation, explicit overrides, identity ambiguity, deterministic IDs, rename continuity, read-only CLI inspection, generated artifact integrity and all 20 pricing fixtures. `evidence/bundle` is the current generated product candidate. `evidence/explain-cheapest.json` is an actual CLI response. `candidate.json` binds exact compiler, source, fixture and evidence bytes.

Previous extension candidates and their test evidence remain historical. No live provider, cloud deployment, ontology admission or product approval is asserted.

## Open questions

The plan and boundary are in [PLAN.md](PLAN.md). Property rename migration, whole-project certification of the composition/ontology extension, and runtime-trace explanations are future work. Generated descriptions remain structural; they do not substitute for business decisions.
