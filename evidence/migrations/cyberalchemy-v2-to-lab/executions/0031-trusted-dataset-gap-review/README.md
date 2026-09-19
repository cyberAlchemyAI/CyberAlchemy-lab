# Materialize Trusted Dataset — prepared, Product unresolved

Bounded source data -> deterministic transformation -> validation -> published dataset or quarantine -> recoverable history.

The six source invariants are preserved as acceptance conditions. The implementation-layering document declares a capability-scoped owner role, which is explicitly projected into the prepared candidate. Fifteen matching source JSON/Markdown files were checked; no explicit Product or parent-capability binding was found in the capability-bearing records. Search scope and limitations are recorded in [result.json](result.json).

The required schema now reports only `product_ref` missing. The unresolved decision is which Product owns this capability. Its dependency on the work orchestrator does not establish that ownership. No Product assignment was invented.

**39 imported / 2 reviewed blockers / 3 reference examples / 1 excluded.** [Current inventory](inventory.json). Current store remains `.local/capability-inventory-import-0030/imports.json`. No dataset execution or publication occurred.

[Verification](verification.json) covers replay, exact schema gap, queue isolation, unchanged imported store and complete review of remaining blocked declarations. Reproduce preparation with `PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/executions/0031-trusted-dataset-gap-review/review.py` from the Lab root.

## Open questions

The capability queue has no unreviewed blocked declarations remaining. Two reviewed items need Product decisions:

- Trusted Dataset: choose its owning Product.
- Definition NFT: establish Product and contract meaning, including retry/uniqueness, storage and wallet verification choices.

Historical bulk scan limitations still apply; this completes review of the known declaration queue, not a claim that every source file or runtime capability has been migrated.
