# Recover Recent Repository Context imported

Existing definitions and model rules -> explicit acceptance requirements -> candidate import.

This Capability finds recent committed changes for an explicitly named project or path. It reports provenance and limits, keeps working-tree observations separate, and does not restore task intent or a lost session.

The missing acceptance field is now mapped from six normative source definitions and three authored AlchLang rules. Those requirements cover commit/change meaning, explicit scope, bounded metadata, freshness, explicit cache refresh, matching snapshot bindings, bounded history (at most 100 commits and 1,000 files), and read-only observation.

The original Capability, definitions and model remain unchanged. Input/output strings are descriptions, not fabricated registry IDs. The cache refresh requirement does not grant permission to refresh: importing this candidate executes no query, refresh or hook installation.

[result.json](result.json) contains the exact mappings and source bindings. [imports.json](imports.json) contains the 23 previous candidates plus this one. The new store is `.local/capability-inventory-import-0010/imports.json`.

Six import checks passed: deterministic replay, missing Definition rejection, missing model-rule rejection, changed-bound rejection, query-mutation rejection, and equality between the stored import and report. The combined graph validates. [verification.json](verification.json) binds the result. Source runtime product tests were not rerun; these checks establish import integrity, not runtime conformance or operational approval.

Queue: **24 imported candidates / 21 blocked declarations**. Next is Provide Governed System Building Access, whose recorded gap is an unresolved service-request input contract. Candidate Definition admission and operational activation remain separate.
