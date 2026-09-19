# Reference examples separated from capability imports

User correction: “i dont think they are capabilities just examples”. User direction: “do next”.

Customer Credit Release / Inventory Reservation / Production Rollback -> AlchLang reference examples -> supporting material rather than separate product capabilities.

All three now have category `reference-example` and status `retained-reference-example` in the current inventory. Source identities and historical evidence are preserved. Customer Credit Release is removed from the successor capability store; Inventory Reservation and Production Rollback leave the blocked capability queue. The frozen original import is historical and is superseded, not rewritten.

**32 imported capabilities / 9 blocked / 3 reference examples / 1 excluded experiment.** [Current inventory](inventory.json). [Example index](reference-examples.json). Current store: `.local/capability-inventory-import-0022/imports.json`.

[Verification](verification.json) checks exact reclassification scope, removal of only the credit reference, unchanged remaining imports, counts, graph validity and historical preservation. Reproduce with `PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/executions/0022-reference-example-reclassification/reclassify.py` from the Lab root.

## Open questions

Next blocked capability: Model Governed Domains (`CA2-CAP-ALCHLANG-MODEL-GOVERNED-DOMAINS`). Its recorded gap is an unresolved obligation registry reference. The examples remain available to support its review.
