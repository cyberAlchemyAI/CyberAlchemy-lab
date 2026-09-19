# Agent Reasoning Engine — checked, repairs prepared

Request -> match capability -> construct context -> derive a supported judgment.

The source declares 136 business concepts, 153 business relationships, 77 system concepts and 67 bridge links. Business graph and bridge reference checks passed in the source validator. Full package validation remains BLOCK; this preparation does not create an imported context store.

Three repairs are required:

- The Product now lists both reasoning and interaction-context capabilities, but its schema still requires exactly the first. Both capabilities are already imported. `proposed-source-package.schema.json` changes only this exact membership constraint.
- Ten of 72 evidence selections are stale in the current checkout. Three exact versions were recovered from another local checkout; seven remain unresolved in the checked current, cya-orquestrator and domainspec-core locations. `evidence-recovery.json` records matches and `evidence-selections/` preserves their exact selected bytes. Unresolved fingerprints must be recovered or replaced through an explicit successor with reviewed support; refreshing hashes alone is insufficient.
- The admitted ontology contract caps both concepts and relationship IDs at 100. `proposed-ontology.schema.json` raises those limits to 1,000 and retains all other constraints. The active contract is frozen by exact approval bindings; this proposal does not substitute it in the registry.

`source-validation.json` preserves the full failing source check. `repair-plan.json` identifies the seven unresolved evidence references and the exact predecessor contract. `verify.py` tests snapshot integrity, graph structure, real graph acceptance under the proposal, rejected overflow/duplicates/authority escalation, Product capability membership and recovered fingerprints.

Next: finish evidence recovery or prepare justified successor bindings, then integrate the schema successors and repeat full package validation before importing. No runtime tests, source changes, contract admission or operational activation occurred.
