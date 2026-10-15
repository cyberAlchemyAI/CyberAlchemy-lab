[Documentation home](../../README.md)

# Authority Claim

<a id="def-cal-definition-authority-claim"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Authority Claim

# Authority Claim

A statement of a particular right or responsibility within a stated scope, with the basis needed to assess it. Stating a claim does not validate it.

**When it applies**

Use authority whenever a source, file, owner, process, gate, validator, or generated view would make something count. Ask: count for what scope, by which owner, through which surface, with which operation, and with what effect?

**Record formats**

[Authority claim · v1](type-cal-artifact-type-authority-claim-v1.md#type-cal-artifact-type-authority-claim-v1)

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-authority-claim-section-2"></a>

## Source explanatory wording

It is a precise statement that someone has a particular right in a particular scope; making the statement does not prove it is valid.

<a id="def-cal-definition-authority-claim-section-3"></a>

## Exact governing statement

Authority Claim is the normalized definition identified by semantic.authority-claim, owned within scope.shared-authority, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D34 without silently merging it with another target.

Target-specific normative meaning:

An Authority Claim is an explicit, challengeable assertion that a named owner or owner route may perform a named operation over a named governed object within an exact scope, on a stated decision or evidence basis, with a declared effect.

Bound source-semantic basis:

Authority is the scoped right or responsibility to let a term, rule, status, artifact, relation, gate result, validation result, or mutation count for a declared CyberAlchemy v2 purpose.

An authority claim is valid only when it names the scope, owner or owner route, authority surface, governed object, allowed operation, evidence or decision basis, effect, and challenge or drift route. Authority may decide what counts inside its scope, but it does not automatically transfer across scopes, surfaces, owners, generated mirrors, or source spaces.

````
For an authority claim `A` over object `x`, CyberAlchemy v2 requires:

```text
A(x) = (scope, owner, surface, object, operation, basis, effect, challenge_route)
```

The claim is admissible only if `scope`, `owner`, `surface`, `operation`, and
`effect` are explicit. If any field is implicit, the authority claim becomes
candidate evidence or residue, not governing authority.
````

- Authority is not truth, confidence, maturity, popularity, file ownership, repository access, generated status, or implementation success. It may cite evidence and may be implemented by access controls, but neither evidence nor access control becomes authority without the scoped owner route.
- This target remains distinct from the sibling targets semantic.authority, semantic.responsibility reconstructed from CAV2-D34; shared source lineage does not merge their identities or validation purposes.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/authority-claim/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.authority-claim@1.0.0-candidate.1

**Content fingerprint · SHA-256**

16bcdd31f45a34fc062a8a316e5cc83814f1662049bb3d1f133329e746b83db4

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use authority whenever a source, file, owner, process, gate, validator, or\ngenerated view would make something count. Ask: count for what scope, by which\nowner, through which surface, with which operation, and with what effect?",
  "authority_scope_ref": "scope.shared-authority",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
