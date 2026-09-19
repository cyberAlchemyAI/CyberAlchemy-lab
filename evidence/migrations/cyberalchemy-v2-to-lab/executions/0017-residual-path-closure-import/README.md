# Residual Path Closure imported as a candidate

Declared failure scenario -> owned safe outcome -> verification obligation -> supporting evidence or explicit gap.

A path is one declared scenario. A residue is the safe state that should remain after disruption. Closure means each relevant path is connected to its required outcome, checks, and evidence; excluded paths require a reason. This capability checks a finite declared set, not every conceivable failure.

The missing Product field was recoverable from explicit construction provenance: `profile.json` links this capability file and a digest-bound DomainSpec Product Thesis. The import projects the thesis document identity, purpose, boundary, and declared owner into a Product record. This is a source-linked projection, not an inference from directory placement. The Capability owner remains `CTX-DSV2-EVF`.

`normal_intent` -> outcome; `testable_candidate` -> acceptance condition; `non_goals` -> exclusions. Source records and lifecycle are preserved in [result.json](result.json).

**28 imported candidates / 16 blocked / 1 excluded.** [Current inventory](inventory.json). The learning experiment remains excluded. Store: `.local/capability-inventory-import-0017/imports.json`.

[Verification](verification.json) covers replay, wrong capability links, stale thesis digests, queue isolation, store preservation, and combined graph validation. Run `PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/executions/0017-residual-path-closure-import/verify.py` from the repository root.

This imports the capability description. It does not approve the source prototype or establish runtime evidence coverage. The source example has blocked readiness; its evaluator was not rerun.

## Open questions

Runtime evidence and harness ownership remain with the source package's `OPEN-QUESTIONS.md`. Next unreviewed blocked declaration: `CA2-CAP-ALCHLANG-DISCOVER-GENERATABLE-OPERATION-PATTERNS`.
