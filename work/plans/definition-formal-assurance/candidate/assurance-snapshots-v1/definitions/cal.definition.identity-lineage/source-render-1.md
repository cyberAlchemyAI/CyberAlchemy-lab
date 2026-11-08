<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Identity Lineage

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.identity-lineage`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:identity-lineage-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

Identity Lineage is a typed relation L over exact identity epochs. L binds a subject kind, predecessor and successor identities or epochs, lineage kind, owner decision, evidence, and non-effects. A same-identity rename preserves one identity across named epochs; it does not create a new Product, Project, Method, Goal, or Context. Lineage types are subject-kind specific unless an explicitly generalized contract is admitted.

```text
L = (lineage_id, subject_kind_definition_ref, predecessor_ref, successor_ref, lineage_kind, owner_decision_ref, evidence_refs, non_effects); same_identity_rename(a,b) => identity(a)=identity(b) and name(a)!=name(b); similar(a,b) =/=> same_identity(a,b).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| L | One Identity Lineage record. |
| a,b | Exact predecessor and successor identity epochs. |

### Boundary conditions

- The subject kind and lineage kind are explicit.
- The owner decision and evidence supporting continuity are bound.
- A context-specific lineage contract cannot govern Product lineage by analogy.

### Testable conditions

- Predecessor and successor references resolve exactly.
- The lineage record distinguishes same-identity rename from successor identity.
- No identity continuity is inferred from directory, shared owner, similar content, or label.

## Plain-language voice

Identity Lineage records what stayed the same and what changed across a rename or successor. Similar names or files are not enough; the continuity must be explicit and owned.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

CML-07 needs Product lineage to state that Craft is the current name of the same Product formerly called DomainSpec v2. The existing Context Lineage Record remains limited to Bounded Context evolution.

### Examples

- DomainSpec v2 to Craft is represented as a Product same-identity rename.
- Governance Context v1 to a successor context continues to use Context Lineage Record, not Product lineage.

## Applicability

An immutable, typed, evidence-backed continuity relation among exact identity epochs that states whether a change preserves identity, creates a successor identity, or records another declared lineage kind.

### Exclusions

- A generic alias list.
- Context Lineage Record used outside Context semantics.
- Identity equality inferred from similar names, paths, owners, content, or history.

## Boundaries

- Identity Lineage is not Alias inference.
- Product Identity Lineage is not Context Lineage Record.
- Identity Lineage is not admission, authority transfer, deletion, or automatic supersession.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole-json | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| candidate:cal.definition.product@1.0.0-candidate.1 | whole-json | `19c6b3bdb5e4c8515837d40c2b0a98b0fecb6edc3698aab359fa2a0d64d9a1cd` | `candidate-unadmitted` |
| candidate:CAL-CML07-CRAFT-IDENTITY-CHAIN-0001 | whole-json | `660f55a2e9583f950f4ec9b995dd2cf107be58e5bb91c32b33eaed6ce4cf75b6` | `candidate-unadmitted` |

## Primary consumers

- authority/artifact-types/identity-lineage/v1
- authority/lineage/craft/v1/lineage.json
- CAL-CML07-CRAFT-IDENTITY-CHAIN-0002

## Lookup and drift

- Index: `authority/definitions/candidates/0007-cml07-semantic-closure/DEFINITIONS-INDEX.md` / `cal.definition.identity-lineage@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0007-cml07-semantic-closure/drift-audit-postimage.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

No typed relations declared.

## Evidence

- SC-002
- SC-004

## Residue

- The identity-lineage Artifact Type and Craft lineage instance remain future S2 and S3 work.

## Claim ceiling

This candidate defines Identity Lineage semantics only. It does not decide or instantiate Craft Product continuity, supersession, deletion, or authority transfer.
