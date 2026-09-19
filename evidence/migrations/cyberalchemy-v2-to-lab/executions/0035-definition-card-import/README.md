# Definition collectible-card candidate imported

Definition -> base image -> visual variants -> numbered copies -> first mint locks collection -> card transfer/trade.

The user selected the collection lock rule: after the first mint, artwork, variants and edition sizes are fixed. Changed artwork or additional copies require a new collection. Actual images and quantities remain configurable inputs for later collections.

This local successor replaces the original one-per-definition concept with collectible editions and permits NFT transfer without granting definition rights or KEP access. The original source record remains unchanged and is retained as provenance. A new local capability node identity distinguishes the revised semantics from the source candidate.

[Selection](selection.json). [Imported candidate](result.json). All 20 missing semantic reference IDs now have explicit local candidate bindings. These descriptions are not executable API schemas, deployed services or proof of wallet/transaction security. Other baseline proposal details remain reviewable candidate requirements, not separately asserted user decisions.

**41 imported capabilities / 0 blocked / 3 reference examples / 1 excluded experiment.** [Final known-declaration inventory](inventory.json). Store: `.local/capability-inventory-import-0035/imports.json`.

[Verification](verification.json) checks deterministic replay, the selected lock rule, reference closure, exact queue transition, historical preservation and combined graph validity. Run `PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/executions/0035-definition-card-import/verify.py` from the Lab root.

## Open questions

Runtime implementation, artwork, edition settings, trading mechanisms, provider selection and security validation remain future work. No mint, trade, payment, private-content publication or deployment occurred. This completes the known capability-description queue, not migration or validation of all executable source systems. Historical bulk scan coverage and parse limitations still apply.
