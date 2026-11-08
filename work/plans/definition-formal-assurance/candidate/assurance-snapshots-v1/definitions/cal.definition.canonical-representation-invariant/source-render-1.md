<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Canonical Representation Invariant

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.canonical-representation-invariant`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope.shared-authority`
- Lifecycle posture reference: `candidate:artifact-reconstruction-l1/v1`

## Scientific/formal voice

Canonical Representation Invariant is the normalized invariant identified by semantic.canonical-representation-invariant, owned within scope.shared-authority, and carried by type.invariant. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D51 without silently merging it with another target.

Target-specific normative meaning:

Canonical Representation Invariant requires each artifact to have exactly one declared machine-canonical representation; human views and convenience labels are generated projections, directory placement cannot establish type or authority, and every admitted canonical kind must bind an owner-approved process origin with an honest assurance level.

Bound source-semantic basis:

A canonical artifact is an artifact instance whose **kind is a member of the
canonical-kind enumeration** ([../../ontology/canonical-kinds/CANONICAL-KINDS.md](../../ontology/canonical-kinds/CANONICAL-KINDS.md))
and whose responsible owner has admitted an exact `process_origin` declaration
that names one allowed producer and process for that kind. It therefore carries
a defined type (a `CAV2-D21` classification/schema facet that is bound, not left
as residue) and an owner-declared process origin.

The strength of support for the origin declaration is recorded separately as
`origin_assurance`:

- `declared` means an owner or source made the exact origin statement;
- `integrity-bound` means a verifier confirmed that the statement and bound
  artifact-state bytes match an L1 integrity mechanism; and
- `actor-attested` means an identified actor attested the exact tuple under a
  bound L2 identity policy and external signature.

`actor-attested` is a defined future level, not a currently available result.
No assurance level proves that the named process actually executed, that the
statement is true, or that the artifact is correct or authoritative.

Canonical-ness is therefore the property of *being typed and carrying an
owner-admitted, allowed process-origin declaration with an honest assurance
level*. It is **decoupled from authority** — a canonical artifact may be
non-authoritative and still canonical. An artifact whose kind is not in the
enumeration, or whose exact origin does not resolve to an owner-approved producer
for that kind, is non-canonical or remains blocked as typed residue.

```text
```text
OriginAssurance = { declared, integrity-bound, actor-attested }

allowed_origin(a)
  <-> (producer_ref(a), process_ref(a), process_version_ref(a))
      in allowed_origins(canonical_kind(a))

canonical(a)
  <-> canonical_kind(a) in CanonicalKinds
      and owner_admitted(a)
      and allowed_origin(a)
      and origin_assurance(a) in OriginAssurance

CanonicalKinds  superset-of  AuthorityKinds   (every authority-kind is a canonical-kind;
                                               not every canonical-kind bears authority)
canonical(a)   independent-of   authoritative(a)   (authority is earned via CAV2-D48)
```

Each canonical artifact declares exactly one `canonical_kind` and one exact
`process_origin` record, and inherits from its kind the `authority_kind` it rolls
up to and its `CAV2-D52` durability. The inherited fields are derived, not
asserted: an artifact cannot choose its `authority_kind`.

`allowed_origins(kind)` is intentionally set-valued because one kind may have
more than one allowed producer. The artifact still binds one exact producer,
process, version, and origin statement. The allowed set must come from a current
owner-approved source; the candidate canonical-kind table does not become
authority through this definition. An unresolved or candidate-only producer
cannot establish canonical origin.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| semantic.canonical-representation-invariant | Stable normalized identity for Canonical Representation Invariant. |
| CAV2-D51 | Bound CyberAlchemy-v2 source-definition identity. |

### Boundary conditions

- Canonical artifact is **not** authority and **not** "canonical source": the store's
existing *canonical source*, *canonical section*, and *canonical definition*
(alias of `CAV2-D33`) use *canonical = the authoritative version*; this term uses
*canonical = has a canonical form + owner-admitted process-origin declaration*
and is explicitly decoupled from authority. The legacy alias `process-born`
must not be used to imply observed execution unless a separately governed
execution witness supports that claim.

It is **not** the enumeration itself — that is the set of kinds in
`CANONICAL-KINDS.md`; a canonical artifact is a member instance. It does not
promote anything: earning authority is `CAV2-D48`, being a recognized kind is
`CAV2-D49`. Origin assurance is not proof, trust, validation, truth, discharge,
promotion, adoption, or publication. Prior 2026-06-21 review prose that used
"canonical artifact" to mean
"target-owned / deployed authority" is the *authoritative-version* sense and
predates this term (recorded in [DEFINITION-DRIFT-AUDIT.md](DEFINITION-DRIFT-AUDIT.md)).
- This target remains distinct from the sibling targets semantic.artifact reconstructed from CAV2-D51; shared source lineage does not merge their identities or validation purposes.

### Testable conditions

- The candidate identity remains cal.definition.canonical-representation-invariant.
- Every selected source-section digest remains current.
- The machine record validates against Definition/v1.
- The human projection is regenerated exactly from the machine record.

## Plain-language voice

Store one machine truth, generate the readable view from it, and never let the folder name or generated text become a second authority.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

In CyberAlchemy-lab migration work, Canonical Representation Invariant is a prototype meaning reconstructed from CAL-NORMALIZE-01. It remains non-authoritative until the correct Lab owner admits a fully validated candidate.

Source context retained for reconstruction:

In CyberAlchemy v2 this names the genus that sits above the
[AUTHORITY-MODEL Authority Kinds table](../AUTHORITY-MODEL.md#authority-kinds):
the fine artifact-types (discovery, research, axiom, ledger, spec, ...) enumerated
in [../../ontology/canonical-kinds/CANONICAL-KINDS.md](../../ontology/canonical-kinds/CANONICAL-KINDS.md), each
rolling up to a coarse `CAV2-D49` authority-kind and carrying a `CAV2-D52`
durability. It is the positive pole opposite `CAV2-D8` import candidate and
non-canonical working material: it lets the project say "this is a typed artifact
with an owner-declared origin" without claiming execution, correctness, or
authority. `CAV2-D35` remains the provenance trail; origin assurance only states
how the exact declaration is supported.

### Examples

- Resolve semantic.canonical-representation-invariant by its machine identity rather than its directory name.
- Challenge source drift through the L1 drift audit before relying on Canonical Representation Invariant.

## Applicability

Use when deciding whether a document is a first-class typed artifact or an
ungoverned working note. Ask: does it instantiate an enumerated canonical kind,
does its owner admit one exact allowed origin, and does the record state how
strongly that origin statement is supported? Under the current review-mode
posture, `declared` is sufficient for owner admission, but the artifact must be
described as owner-declared rather than mechanically verified process output.

Use `integrity-bound` only when the exact statement and artifact-state bytes have
a valid L1 verifier receipt. Reserve `actor-attested` for a real L2 external
signature and identity-policy receipt; no current artifact may claim it merely
because the level is defined.

### Exclusions

- Admission, activation, publication, release, deployment, and external effects.
- Meanings assigned to split or reclassified sibling targets unless explicitly referenced.

## Boundaries

- Canonical artifact is **not** authority and **not** "canonical source": the store's
existing *canonical source*, *canonical section*, and *canonical definition*
(alias of `CAV2-D33`) use *canonical = the authoritative version*; this term uses
*canonical = has a canonical form + owner-admitted process-origin declaration*
and is explicitly decoupled from authority. The legacy alias `process-born`
must not be used to imply observed execution unless a separately governed
execution witness supports that claim.

It is **not** the enumeration itself — that is the set of kinds in
`CANONICAL-KINDS.md`; a canonical artifact is a member instance. It does not
promote anything: earning authority is `CAV2-D48`, being a recognized kind is
`CAV2-D49`. Origin assurance is not proof, trust, validation, truth, discharge,
promotion, adoption, or publication. Prior 2026-06-21 review prose that used
"canonical artifact" to mean
"target-owned / deployed authority" is the *authoritative-version* sense and
predates this term (recorded in [DEFINITION-DRIFT-AUDIT.md](DEFINITION-DRIFT-AUDIT.md)).
- This target remains distinct from the sibling targets semantic.artifact reconstructed from CAV2-D51; shared source lineage does not merge their identities or validation purposes.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cyberalchemy-v2:CAV2-D51 | ## CAV2-D51: Canonical Artifact | `3e9d50b1154b58b938c164725ac8fabed16914538dda579cf89c671c13c5becc` | `candidate-unadmitted` |

## Primary consumers

- semantic.artifact-lifetime

## Lookup and drift

- Index: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/registry.json` / `cal.definition.canonical-representation-invariant@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.originates-from | cal.definition.canonical-representation-invariant | cyberalchemy-v2:CAV2-D51 | role:definition-owner |

## Evidence

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-canonical-representation-invariant/v1/artifact.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/receipts/validation.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/receipts/validation.json

## Residue

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json

## Claim ceiling

Candidate Definition reconstructed from an accepted normalization scaffold and exact CyberAlchemy-v2 source sections. It is not admitted and grants no implementation, migration, registry, publication, release, deployment, or external-effect authority.
