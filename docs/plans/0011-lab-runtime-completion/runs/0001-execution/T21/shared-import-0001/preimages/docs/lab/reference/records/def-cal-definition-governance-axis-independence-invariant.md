[Documentation home](../../README.md)

# Governance-Axis Independence Invariant

<a id="def-cal-definition-governance-axis-independence-invariant"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Governance-Axis Independence Invariant

Requires kind, status, evidence confidence, commitment confidence, provenance and owner to remain distinct when they matter to a decision. One dimension cannot silently answer another: acceptance does not establish strong evidence.

**When it applies**

Use authority lifecycle axes when evaluating definitions, constitutions, axioms, ontology nodes, inventory cards, task results, schemas, and implementation claims. The reviewer should ask which axis is being advanced: source role, maturity, evidence, owner commitment, provenance, or canonical authority.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

"Useful", "trusted", "finished", "owned", and "canonical" are different words. Do not let one of them impersonate the others.

## Exact governing statement

Governance-Axis Independence Invariant is the normalized invariant identified by semantic.governance-axis-independence-invariant, owned within scope.shared-authority, and carried by type.invariant. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D23 without silently merging it with another target.

Bound source-semantic basis:

Authority lifecycle axis is the CyberAlchemy v2 rule that authority posture must separate at least these dimensions when they matter to a decision:

- role or kind - maturity or status - evidence confidence - commitment or conviction - provenance - owner

No one axis may silently stand in for another. A definition can be mature but weakly evidenced, an imported source can be well-evidenced but not locally canonical, an ontology candidate can be useful but unpromoted, and an owner can be committed to a hypothesis without that hypothesis becoming authority.

````
An authority-bearing artifact `a` has lifecycle posture:

```text
L(a) = (kind, status, evidence, commitment, provenance, owner, residue)
```

where each component may be known, unknown, deferred, or source-local. A
governance move is valid only if it changes the intended component and does not
imply changes to the others unless those changes are explicitly recorded.
````

- Authority lifecycle axis is not a complete status schema and does not make every artifact an ontology node. It gives the minimum separations that future schemas, ledgers, and constitutions must preserve.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/governance-axis-independence-invariant/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.governance-axis-independence-invariant@1.0.0-candidate.1

**Content fingerprint · SHA-256**

2249daf97a66af5bdf8b9ab0476b2dfa290e8e523cb0d94d8fe9978b1b845de8

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use authority lifecycle axes when evaluating definitions, constitutions, axioms,\nontology nodes, inventory cards, task results, schemas, and implementation\nclaims. The reviewer should ask which axis is being advanced: source role,\nmaturity, evidence, owner commitment, provenance, or canonical authority.",
  "authority_scope_ref": "scope.shared-authority",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
