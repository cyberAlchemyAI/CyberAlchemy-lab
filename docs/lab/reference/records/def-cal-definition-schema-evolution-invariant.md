[Documentation home](../../README.md)

# Schema Evolution Invariant

<a id="def-cal-definition-schema-evolution-invariant"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Schema Evolution Invariant

# Schema Evolution Invariant

Requires schema changes to retain provenance and declare how mistakes will be detected, or record the unresolved validation gap and its owner.

**When it applies**

Use schema amendment witness before changing frontmatter rules, ontology node schemas, inventory entry schemas, event catalogs, ledger row identity, machine envelopes, validation fixtures, or constitution-controlled structure. The minimum action is to say what changed, who owns it, what evidence justifies it, what may break, and what witness checks or carries the change.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-schema-evolution-invariant-section-2"></a>

## Source explanatory wording

If the shape changes, leave a receipt and show what will catch mistakes. If nothing catches them yet, say that out loud and assign the gap.

<a id="def-cal-definition-schema-evolution-invariant-section-3"></a>

## Exact governing statement

Schema Evolution Invariant is the normalized invariant identified by semantic.schema-evolution-invariant, owned within scope.shared-authority, and carried by type.invariant. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D25 without silently merging it with another target.

Bound source-semantic basis:

Schema amendment witness is the CyberAlchemy v2 rule that any schema, frontmatter, taxonomy, ontology, ledger, event, or machine-view change that affects validation or authority interpretation must carry both:

- an amendment record naming owner, scope, reason, changed shape, source evidence, compatibility effect, and rollout or rollback route - a witness naming the validator, runtime observation, fixture, review check, or typed residue that shows how the changed rule is enforced or why it cannot yet be enforced

````
For an authority-affecting shape change `s -> s'`, a valid amendment is:

```text
A = (owner, scope, source, delta, compatibility, witness, residue)
```

where `witness` may be deterministic, hybrid, review-based, or absent only when
the absence is typed as residue with owner and effect. The amendment is not
complete if the changed shape can govern downstream work but has no declared
enforcement or residue path.
````

- Schema amendment witness does not redefine generic `schema`; that term is defined by `CAV2-D56`. This definition governs the *change* of a schema, not its content. It also does not require a fully automated validator for every early rule. Review and typed residue are acceptable witnesses when the artifact is not yet implementation-backed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/schema-evolution-invariant/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.schema-evolution-invariant@1.0.0-candidate.1

**Content fingerprint · SHA-256**

e1c996eda39fa109bc0b689570ce1a6cdeb72796e667125a365679ad4da26088

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use schema amendment witness before changing frontmatter rules, ontology node\nschemas, inventory entry schemas, event catalogs, ledger row identity, machine\nenvelopes, validation fixtures, or constitution-controlled structure. The\nminimum action is to say what changed, who owns it, what evidence justifies it,\nwhat may break, and what witness checks or carries the change.",
  "authority_scope_ref": "scope.shared-authority",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
