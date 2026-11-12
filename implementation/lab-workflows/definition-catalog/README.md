# Shared Definition placement

Define produces portable candidate packages. This shared Lab workflow verifies and materializes a package with the current Define AlchLang implementation, then enforces the compiled Lab.DefinitionCatalog.PlaceDefinition operation before placing files.

Use the pinned Node with cli.mjs --file REQUEST.json --dry-run first. The request has package (an existing portable Define package directory), workspace (an actual key such as product/craft), and optional original (the original Definition JSON for exact voice/owner comparison). Omit --dry-run to place candidates.

Placement is <workspace>/authority/definitions/<definition-name>/<version>/, with definition.json, generated DEFINITION.md, field-lineage.json and evidence.json. Known definitions use the selected maintenance-homes mapping. Bodies, versions, owners and voices are checked; path traversal and conflicting existing versions refuse writes. A fresh version directory is published by rename. No runtime code is copied.

This workflow does not sign owner decisions, mutate the canonical registry, change source cuts or activate a runtime. Those remain the existing shared Lab review/publication processes. The complete current-catalog rollout and its evidence are in work/plans/definition-catalog-v2-layout.

Names such as craft-method, person and definition-pack are used in directories and displayed first in indexes. Stable IDs remain inside records for exact references.
