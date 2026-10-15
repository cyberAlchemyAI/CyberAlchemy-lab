[Documentation home](../../README.md)

# Contestability Policy

<a id="def-cal-definition-contestability-policy"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Contestability Policy

# Contestability Policy

Declares how a governed object’s meaning, state or claims may be challenged and who handles the response.

**When it applies**

Use challenge contract when a candidate ontology node, projection, definition proposal, constitution proposal, research claim, or authority artifact needs to say what kind of objection is valid and what happens next. A contradiction edge may block promotion; a validation edge may increase evidence support; a blocking question may defer the node; and unresolved challenge residue must remain attached until an owner route closes, waives, or demotes it.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-contestability-policy-section-2"></a>

## Source explanatory wording

It is the object's "how to disagree with me correctly" field.

<a id="def-cal-definition-contestability-policy-section-3"></a>

## Exact governing statement

Contestability Policy is the normalized policy identified by semantic.contestability-policy, owned within scope.shared-authority, and carried by type.policy. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D40 without silently merging it with another target.

Bound source-semantic basis:

A challenge contract is the explicit review surface attached to a CyberAlchemy v2 node, candidate, claim, or authority artifact that states how the object may be challenged, contradicted, validated, blocked, or routed for owner review without silently changing its meaning or confidence.

A challenge contract must declare the valid challenge response, admissible challenge modes, contradiction and validation links when present, owner route, resolution gate, blocking questions, and challenge residue route. It does not contain the object's own confidence or residue and does not introduce a third confidence axis. Object confidence remains a sibling posture using the `evidence_confidence` and `commitment_confidence` split governed by `CAV2-D23`.

````
An admissible challenge contract has at least:

```text
ChallengeContract =
  (challenge_response, valid_challenge_modes, contradiction_edges,
   validation_edges, owner_route, resolution_gate, blocking_questions,
   challenge_residue_route)
```

where `challenge_residue_route` says where unresolved challenge residue is
handled. The object's own confidence and residue are not part of the challenge
contract. When an object records confidence, active CyberAlchemy v2 uses
`evidence_confidence` for evidence support and `commitment_confidence` for
commitment posture.
````

- Challenge contract is not a verdict, not a confidence score, not proof of truth, not a promotion decision, and not an ontology-owned override of the relevant owner route. It names the challenge path; owner routes and gates still decide movement.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../assets/d17a657d3f55-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.contestability-policy@1.0.0-candidate.1

**Content fingerprint · SHA-256**

d17a657d3f5599de51e5f77be06984e9b15647e69028277310a850c74747fb39

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use challenge contract when a candidate ontology node, projection, definition\nproposal, constitution proposal, research claim, or authority artifact needs to\nsay what kind of objection is valid and what happens next. A contradiction\nedge may block promotion; a validation edge may increase evidence support; a\nblocking question may defer the node; and unresolved challenge residue must\nremain attached until an owner route closes, waives, or demotes it.",
  "authority_scope_ref": "scope.shared-authority",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
