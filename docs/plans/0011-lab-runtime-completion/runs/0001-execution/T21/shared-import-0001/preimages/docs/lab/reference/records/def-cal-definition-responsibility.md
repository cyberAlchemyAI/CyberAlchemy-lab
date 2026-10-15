[Documentation home](../../README.md)

# Responsibility

<a id="def-cal-definition-responsibility"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Responsibility

What a participant must answer for. Responsibility is distinct from permission to authorize particular actions.

**When it applies**

Use authority whenever a source, file, owner, process, gate, validator, or generated view would make something count. Ask: count for what scope, by which owner, through which surface, with which operation, and with what effect?

**Record formats**

[Responsibility · v1](type-cal-artifact-type-responsibility-v1.md#type-cal-artifact-type-responsibility-v1)

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

Responsibility says what someone must answer for, which is different from what they are allowed to authorize.

## Exact governing statement

Responsibility is the normalized definition identified by semantic.responsibility, owned within scope.shared-authority, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D34 without silently merging it with another target.

Target-specific normative meaning:

Responsibility is an owner-qualified obligation to perform, maintain, answer for, or route a declared outcome within a bounded scope; it does not by itself grant the authority needed to cause that outcome.

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
- This target remains distinct from the sibling targets semantic.authority, semantic.authority-claim reconstructed from CAV2-D34; shared source lineage does not merge their identities or validation purposes.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/responsibility/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.responsibility@1.0.0-candidate.1

**Content fingerprint · SHA-256**

aea6a0398ed4fef33aa20d73dae7b8c6163f61a667d01789ccc3562ba07910e2

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

[Return to this catalog](../definitions.md#catalog-definitions)
