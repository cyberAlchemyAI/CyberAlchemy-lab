[Documentation home](../../README.md)

# Intent

<a id="def-cal-definition-intent"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Intent

The desired outcome and constraints before a particular solution is selected.

**When it applies**

When making the need and purpose explicit before choosing how to respond.

**Record formats**

[Intent · v1](type-cal-artifact-type-intent-v1.md#type-cal-artifact-type-intent-v1)

**[In the Northstar incident](../../tutorials/incident-walkthrough.md)**

Customers need complete eligible data; this need frames the investigation and possible responses.

**Common mistake**

Treating the need itself as an accepted implementation plan.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

Intent is what the work is trying to make possible before we know the final shape.

## Exact governing statement

Intent is the normalized definition identified by semantic.intent, owned within scope.coordination, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D39 without silently merging it with another target.

Bound source-semantic basis:

Intent is the declared purpose, desired capability, problem pressure, or change direction that orients a CyberAlchemy v2 method before the exact output shape, artifact, gate, or implementation path is fully settled.

Intent must be attributable, bounded enough to route, revisable under discovery, and traceable to the artifacts, decisions, residue, or next routes that claim to satisfy it. An intent may be refined, split, renamed, or rejected, but it must not be silently replaced by an artifact or implementation convenience.

````
An admissible intent record has at least:

```text
Intent = (source, purpose, scope, constraints, target_pressure,
          current_output_hypothesis, revision_route)
```

The `current_output_hypothesis` may change as discovery proceeds. The intent
remains traceable only if the revision route records why the output changed.
````

- Intent is not a requirement, not an artifact, not proof, not a command to mutate, and not automatic scope approval. It orients work; gates, authority, evidence, and later artifact definitions decide what can count.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/intent/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.intent@1.0.0-candidate.1

**Content fingerprint · SHA-256**

cce7b46ddc9bf4f7b42038c15da1380573e58d9bb2919d86b94a7c1738325c0b

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use intent at the start of definition, design, research, planning,\nimplementation, validation, or handoff work. Intent keeps the work oriented\nwhile discovery decides whether the right output is a definition, constitution,\nmethod, work-pack, validation report, code change, or deferred question.",
  "authority_scope_ref": "scope.coordination",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
