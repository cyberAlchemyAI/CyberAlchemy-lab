[Documentation home](../../README.md)

# Canonical Representation Invariant

<a id="def-cal-definition-canonical-representation-invariant"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Canonical Representation Invariant

Requires one designated machine representation for each artifact and an owner-approved process-origin declaration for its kind. Generated human views do not gain independent authority, and origin assurance does not establish truth.

**When it applies**

Use when deciding whether a document is a first-class typed artifact or an ungoverned working note. Ask: does it instantiate an enumerated canonical kind, does its owner admit one exact allowed origin, and does the record state how strongly that origin statement is supported? Under the current review-mode posture, `declared` is sufficient for owner admission, but the artifact must be described as owner-declared rather than mechanically verified process output.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

Store one machine truth, generate the readable view from it, and never let the folder name or generated text become a second authority.

## Exact governing statement

Canonical Representation Invariant is the normalized invariant identified by semantic.canonical-representation-invariant, owned within scope.shared-authority, and carried by type.invariant. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D51 without silently merging it with another target.

Target-specific normative meaning:

Canonical Representation Invariant requires each artifact to have exactly one declared machine-canonical representation; human views and convenience labels are generated projections, directory placement cannot establish type or authority, and every admitted canonical kind must bind an owner-approved process origin with an honest assurance level.

Bound source-semantic basis:

A canonical artifact is an artifact instance whose **kind is a member of the canonical-kind enumeration** (Canonical kinds) and whose responsible owner has admitted an exact `process_origin` declaration that names one allowed producer and process for that kind. It therefore carries a defined type (a `CAV2-D21` classification/schema facet that is bound, not left as residue) and an owner-declared process origin.

The strength of support for the origin declaration is recorded separately as `origin_assurance`:

- `declared` means an owner or source made the exact origin statement; - `integrity-bound` means a verifier confirmed that the statement and bound artifact-state bytes match an L1 integrity mechanism; and - `actor-attested` means an identified actor attested the exact tuple under a bound L2 identity policy and external signature.

`actor-attested` is a defined future level, not a currently available result. No assurance level proves that the named process actually executed, that the statement is true, or that the artifact is correct or authoritative.

Canonical-ness is therefore the property of *being typed and carrying an owner-admitted, allowed process-origin declaration with an honest assurance level*. It is **decoupled from authority** — a canonical artifact may be non-authoritative and still canonical. An artifact whose kind is not in the enumeration, or whose exact origin does not resolve to an owner-approved producer for that kind, is non-canonical or remains blocked as typed residue.

````
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
````

- Canonical artifact is **not** authority and **not** "canonical source": the store's existing *canonical source*, *canonical section*, and *canonical definition* (alias of `CAV2-D33`) use *canonical = the authoritative version*; this term uses *canonical = has a canonical form + owner-admitted process-origin declaration* and is explicitly decoupled from authority. The legacy alias `process-born` must not be used to imply observed execution unless a separately governed execution witness supports that claim. It is **not** the enumeration itself — that is the set of kinds in `CANONICAL-KINDS.md`; a canonical artifact is a member instance. It does not promote anything: earning authority is `CAV2-D48`, being a recognized kind is `CAV2-D49`. Origin assurance is not proof, trust, validation, truth, discharge, promotion, adoption, or publication. Prior 2026-06-21 review prose that used "canonical artifact" to mean "target-owned / deployed authority" is the *authoritative-version* sense and predates this term (recorded in [DEFINITION-DRIFT-AUDIT.md](../../../../authority/definitions/DEFINITION-DRIFT-AUDIT.md)).
- This target remains distinct from the sibling targets semantic.artifact reconstructed from CAV2-D51; shared source lineage does not merge their identities or validation purposes.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/canonical-representation-invariant/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.canonical-representation-invariant@1.0.0-candidate.1

**Content fingerprint · SHA-256**

36d484e269e9aeb79e2e4653874062157a07cc6a04d5edacfaa3502b441bbe76

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use when deciding whether a document is a first-class typed artifact or an\nungoverned working note. Ask: does it instantiate an enumerated canonical kind,\ndoes its owner admit one exact allowed origin, and does the record state how\nstrongly that origin statement is supported? Under the current review-mode\nposture, `declared` is sufficient for owner admission, but the artifact must be\ndescribed as owner-declared rather than mechanically verified process output.\n\nUse `integrity-bound` only when the exact statement and artifact-state bytes have\na valid L1 verifier receipt. Reserve `actor-attested` for a real L2 external\nsignature and identity-policy receipt; no current artifact may claim it merely\nbecause the level is defined.",
  "authority_scope_ref": "scope.shared-authority",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
