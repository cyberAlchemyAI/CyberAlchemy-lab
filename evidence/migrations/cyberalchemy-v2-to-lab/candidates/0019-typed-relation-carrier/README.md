# Typed Relation carrier

Exact source -> explicit relation kind and direction -> exact target -> binding checks.

A Typed Relation records a directed, owner-qualified connection with evidence and a declared effect. The source Typed Coupling Invariant requires these links to be explicit before a dependency can influence decisions. This carrier preserves both normalized D16 and D60 source selectors.

The implemented example is Gate Artifact Type -> binds Definition -> exact Gate Definition version. Its profile and relation kind use candidate identities; this batch admits no relation kind and does not construct any separate relation-kind target.

The checker binds both endpoint files by hash, checks their identities and type direction, and confirms the source declares exactly one matching Definition binding and reference. The source's recorded target hash and path must agree with the relation's target. Evidence files are hash-bound, duplicate evidence is rejected and relation identity cannot collapse into either endpoint.

This bounded profile accepts an Artifact Type/v2 source and a Definition/v1 target. It validates the target Definition schema and checks the source's root binding and relevant semantic binding fields. It does not fully revalidate an arbitrary source artifact package. The predecessor Gate package and its frozen materials are independently preserved and checked.

A verified connection does not interpret owner-local meaning, authenticate an owner, prove evidence relevance, validate the declared scope against endpoint scopes or execute the declared effect. The scope, owner route, challenge route and effect description remain assertions for review. Symmetric links, Project relationships, other endpoint types and other relation-kind profiles remain unsupported.

Run from the Lab root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0019-typed-relation-carrier/validate.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0019-typed-relation-carrier/check.py evidence/migrations/cyberalchemy-v2-to-lab/candidates/0019-typed-relation-carrier/artifact-types/typed-relation/v1/fixtures/valid/typed-relation-record.json
```

CLI status 0 means the directed binding conforms; 2 means invalid input or binding. Neither result grants authority.

Validation passes 14 behavioral tests and 8 invalid contract fixtures. It verifies the Typed Coupling Invariant Definition, its D16 source section and both normalized D16/D60 selectors. The selected Definition closure has no source-lineage residues; inherited predecessor records and the existing D53 overlay remain preserved. Generated files reproduce and the predecessor snapshot remains unchanged.

The 195-target ledger now has 13 admitted targets, 93 constructed candidates and 89 remaining scaffolds. Next: `type.lineage-map`.

The user's `next` authorizes construction and testing. A later reliance decision would approve using this particular typed link, with its exact endpoints, scope, owner route and declared effect. This candidate neither approves that reliance nor promotes either endpoint.
