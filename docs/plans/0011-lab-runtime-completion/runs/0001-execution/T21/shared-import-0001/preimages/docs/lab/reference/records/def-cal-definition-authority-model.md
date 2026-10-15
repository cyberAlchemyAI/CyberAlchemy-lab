[Documentation home](../../README.md)

# Authority Model

<a id="def-cal-definition-authority-model"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Authority Model

Describes which kinds of records and decisions can govern a purpose, who owns them and the limits separating their authority.

**When it applies**

Use authority model when deciding whether a source fragment, definition candidate, ontology node, research finding, discipline, constitution rule, decision, spec, runtime contract, generated projection, validation result, or implementation artifact is allowed to influence CyberAlchemy v2 work.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

The authority model is the traffic map for what is allowed to count, who can make it count, and what it must not be confused with.

## Exact governing statement

Authority Model is the normalized definition identified by semantic.authority-model, owned within scope.shared-authority, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D41 without silently merging it with another target.

Bound source-semantic basis:

An authority model is the governed structure that classifies candidate material by authority kind, reliance posture, owner route, admissible movement, gate vocabulary, validation surface, and non-collapse rule so CyberAlchemy v2 can decide what may count for which purpose without letting evidence, ontology, research, generated projections, implementation success, or narrative repetition silently become authority.

An authority model must name the authority surfaces it coordinates, the route that owns each kind of promotion, the states or postures a candidate may occupy, the gates that control movement between states, and the boundary conditions that prevent one authority layer from overriding another.

````
For a candidate object `x`, a CyberAlchemy v2 authority model provides a routing
function:

```text
A(x) =
  (kind, posture, owner_route, allowed_use, blocked_use,
   gate, validation_surface, non_collapse_rules)
```

Movement is admissible only when the responsible `owner_route` records a gate
verdict and the candidate's `allowed_use` covers the intended downstream effect.
If a candidate crosses from evidence or model into local authority, the model
requires a promotion gate rather than implied authority by proximity.
````

- Authority model is not ontology by itself, not a schema by itself, not a decision, not access control, not proof, not a universal constitution, and not a license to promote all modeled material. It coordinates authority movement; the responsible owner routes still make the actual promotion decisions.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/authority-model/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.authority-model@1.0.0-candidate.1

**Content fingerprint · SHA-256**

f5bd332946ce774543f0749e873f9e68a11d6a669c779454c88495a10ee51e29

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use authority model when deciding whether a source fragment, definition\ncandidate, ontology node, research finding, discipline, constitution rule,\ndecision, spec, runtime contract, generated projection, validation result, or\nimplementation artifact is allowed to influence CyberAlchemy v2 work.\n\nThe authority model answers: what kind of thing is this, what may we rely on it\nfor, who owns the next move, which gate must run, and what must not be collapsed\ninto what?",
  "authority_scope_ref": "scope.shared-authority",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
