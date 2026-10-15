[Documentation home](../../README.md)

# Authority

<a id="def-cal-definition-authority"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Authority

# Authority

The scoped right or responsibility to decide what a term, rule, record, relationship, result or change may count as for a stated purpose.

**When it applies**

When asking what can govern a meaning, rule or effect within a declared scope.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**[In the Northstar incident](../../tutorials/incident-walkthrough.md)**

The accepted definition governs meaning; a separate scoped delegation permits the investigation actions.

**Common mistake**

Inferring deployment permission from definition acceptance.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-authority-section-2"></a>

## Source explanatory wording

Authority says who may decide what counts, for which purpose and within which boundary.

<a id="def-cal-definition-authority-section-3"></a>

## Exact governing statement

Authority is the normalized definition identified by semantic.authority, owned within scope.shared-authority, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D34 without silently merging it with another target.

Target-specific normative meaning:

Authority is an owner-qualified and scope-bounded right or responsibility to decide what a declared term, rule, status, artifact, relation, result, or mutation is permitted to count as for one purpose.

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
- This target remains distinct from the sibling targets semantic.authority-claim, semantic.responsibility reconstructed from CAV2-D34; shared source lineage does not merge their identities or validation purposes.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../assets/9266097c000d-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.authority@1.0.0-candidate.1

**Content fingerprint · SHA-256**

9266097c000d2e22ad253ac5df402f729e7284a6990edcd723968dbf0f023e7d

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
