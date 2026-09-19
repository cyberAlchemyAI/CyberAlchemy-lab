# Verified Patch Candidates — offline successor import

Request -> bounded proposal -> exact action approval -> independent verification -> candidate or explicit failure.

This candidate imports ten business concepts, six source relationships and five generated system concepts. It uses the unchanged capability description and the exact current package inputs covered by 22 offline tests in 0054. Both model builds produced identical bytes, and restoration reproduces those outputs.

The successor profile explicitly limits verification to offline fixtures and injected clients. Original construction bindings, conformance records and frozen testable candidate are preserved under `historical/` inside the package; they are not current evidence. Missing historical L2 receipts and live-canary claims remain unverified. The source live validators were not run.

Source registries now explicitly pin current evidence versions; `successor-changes.json` records every changed fingerprint. The original profile is retained in `original-profile.json`. A new `offline-candidate.json` binds current candidate materials and predecessor test evidence, without manufacturing a historical receipt.

`validate_candidate.py` checks offline candidate identities, source and implementation hashes, graph closure, generated receipts, and non-authorizing/no-retry boundaries. It is distinct from the source live-canary validation procedure. Context and Ontology headers use existing admitted migration-scoped contracts; the model remains candidate-unadmitted.

The archive and manifest restore into `.local/ontology-context-import-0055/`. `verify.py` tests invalid graph identities, authority and live-claim escalation, changed fingerprints, automatic retries, exact source pointers and restored build equivalence. No live model, gateway restart, fixture mutation or operational activation occurs during this import. Verification uses the local external tsx loader as a build prerequisite.
