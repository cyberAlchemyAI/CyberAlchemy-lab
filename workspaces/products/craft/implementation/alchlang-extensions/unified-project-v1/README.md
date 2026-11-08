# Unified pricing function candidate

The same declarative pricing source now builds through one DomainSpec project. The project declares its composition alongside its core nodes. Compilation validates typed core bindings, mappings, quantified queries, rules, results, integration configuration and derived ontology dependencies. Standard build/verify generates and checks the composition artifacts; Alch packages them with the transport and tracing runtimes.

Read [quantity-price.alch](quantity-price.alch), the [pipeline guide](../../alchlang/docs/UNIFIED-PROJECT.md), or the generated [project declaration](/home/vlad_/projects/cyberAlchemy-v2/language/capabilities/alchlang/plans/general-compiler-v1/extensions/unified-project-v1/evidence/bundle/domain/project/project.json). The [compilation certificate](/home/vlad_/projects/cyberAlchemy-v2/language/capabilities/alchlang/plans/general-compiler-v1/extensions/unified-project-v1/evidence/bundle/domain/certificate.json) includes one composition validation result separately from the four core nodes and their meta-type obligations.

## Current validation

110 Alch tests and 45 focused DomainSpec tests passed, with both builds and Alch typechecking. Logs are in `evidence/`. The final bundle passed standard DomainSpec verification, all 20 pricing fixture comparisons and its exact file-inventory check. See [product-test.json](/home/vlad_/projects/cyberAlchemy-v2/language/capabilities/alchlang/plans/general-compiler-v1/extensions/unified-project-v1/evidence/product-test.json) and [the recorded invocation](/home/vlad_/projects/cyberAlchemy-v2/language/capabilities/alchlang/plans/general-compiler-v1/extensions/unified-project-v1/evidence/quoted-trace.json): quantity 15 selects tier10 at USD 8.00 and returns USD 120.00.

Rejection tests cover missing/symbolic composition sources, unbound roots, incorrect core selectors, same-type property swaps, incorrect calculation arguments, schema/type mismatches, integration selector errors, altered ontology dependencies, missing compiled compositions and artifact tampering. Existing project/v1 regressions remain passing.

`validate.mjs` builds and validates this evidence in a fresh extension directory; its exclusive writes intentionally refuse to overwrite an existing candidate. `candidate.json` binds the selected implementation, tests, documentation and evidence bytes. Earlier candidates remain unchanged.

## Construction and operational support

Product construction reached a locally tested candidate. Product approval is not recorded. Release/deployment preparation remains deferred operational support owned by the release/deployment owner, with no dependency on this completed prototype stage. No remote provider or Medusa service oracle was run in this slice.

## Open Questions

One composition per project and TypeScript exact UInt64 / Node HTTP are supported. Legacy project instantiation and checked assurance interchange reject this profile until their formalization scope is extended. The composition certificate is typed compilation evidence, not a Lean proof of the complete function. Source provenance does not independently prove business meaning. Ontology admission, meta-type factory automation, signed production traces and provider deployment remain future work.
