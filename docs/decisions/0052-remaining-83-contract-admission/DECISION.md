# The 83 migration contracts are registered

Approved contracts -> scoped authoritative registry -> consumer integration.

**Contract admission** means the migration can resolve the exact approved record fields, profile parameters, relationship rules and navigation projections from one registry. All 26 Artifact Types, 25 profiles, 25 relation kinds and 7 derived views are admitted in the `cyberAlchemy-v2-to-CyberAlchemy-lab-migration` scope by this decision overlay.

**Consumer integration** means connecting code that processes actual migration records to those contracts. That is the next step. This admission does not activate domain actions or promote candidate Definitions and earlier carriers. Their recorded dependency status remains visible in the registry; illustrative records remain examples.

The migration ledger now distinguishes 13 previously admitted targets, 83 contracts admitted within migration scope, and 99 constructed candidates. The original 195-target denominator is preserved. Scoped contract admission does not claim global semantic closure.

The [registry](../../../authority/decisions/migration-contracts/v1/registry.json) binds every target and contract to the [existing approval](../0051-remaining-83-review-approval/decision.json). [decision.json](decision.json) binds that registry. [reconciliation.json](reconciliation.json) records the new state without rewriting earlier ledgers or the reviewed candidate snapshot.

Consumers can inspect an admitted contract through the validated lookup:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tooling/validators/migration_contracts.py type.product
```

Lookup verifies approval, registry and candidate integrity and returns the selected contract with its scope and dependencies. Unknown targets, out-of-scope requests and changed registry bytes are rejected. It grants no execution permission.

Validation: all 103 existing behavioral tests passed again; four resolver checks passed, including scope, unknown-target and tampering rejection. The exact reviewed snapshot remains unchanged. Evidence is in [receipts/validation.json](receipts/validation.json).
