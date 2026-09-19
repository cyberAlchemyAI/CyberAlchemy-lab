# Lineage Map carrier

Legacy identity -> accepted disposition -> complete normalized successor set -> exact indexed records.

A Lineage Map preserves the relationship between legacy identities and declared successors without transferring authority. This carrier follows the accepted D9 reclassification and binds the source-qualified CyberAlchemy Repository Identity Definition as its concrete source context.

The example covers CAV2-D9 and CAV2-D34. D9 reclassifies to two targets: repository identity and Lineage Map. D34 splits to five targets: Authority, Authority Claim and Responsibility meanings, plus Authority Claim and Responsibility carriers. Every declared successor must remain present; no successor is selected automatically.

The checker binds the exact accepted normalization and frozen target index. For each explicitly covered legacy identity it checks the disposition, complete successor set, successor file hash, target identity and indexed status. Duplicate mappings, omitted successors and substituted target files are rejected. Lookup outside the declared coverage fails explicitly.

The targets are active names in the accepted normalization, but the bound files are prototype scaffolds. The checker reports that recorded status. It does not resolve current admission, claim the scaffolds are governing artifacts or replace later construction evidence. Even a one-target mapping does not establish identity equivalence.

This bounded profile is a one-step map over an explicitly selected subset of the normalization. It does not discover history, infer renames, traverse multiple generations, model withdrawal, prove full migration coverage or authenticate its owner route. It preserves dispositions including split and collapse without inventing one-to-one identity continuity.

Run from the Lab root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0020-lineage-map-carrier/validate.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0020-lineage-map-carrier/check.py evidence/migrations/cyberalchemy-v2-to-lab/candidates/0020-lineage-map-carrier/artifact-types/lineage-map/v1/fixtures/valid/lineage-map-record.json CAV2-D34
```

Omit the legacy ID to inspect the whole declared map. CLI status 0 means mapping conformance; 2 means invalid input or an identity outside coverage. Neither grants authority.

Validation passes 14 behavioral tests and 8 invalid contract fixtures. It verifies the repository identity Definition and its D9 section, the normalized D9 scaffold selector, accepted normalization and target index. The selected Definition closure has no source-lineage residues; inherited predecessor records and the existing D53 overlay remain preserved. Generated files reproduce and the predecessor snapshot remains unchanged.

The 195-target ledger now has 13 admitted targets, 94 constructed candidates and 88 remaining scaffolds. Next: `type.withdrawal-record`.

The user's `next` authorizes construction and testing. A later reliance decision would approve using these exact mappings to locate successor identities. It would not by itself approve successor admission, identity equivalence or inherited authority.
