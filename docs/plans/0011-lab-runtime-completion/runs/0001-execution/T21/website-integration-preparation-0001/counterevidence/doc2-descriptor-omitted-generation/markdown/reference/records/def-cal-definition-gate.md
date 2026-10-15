[Documentation home](../../README.md)

# Gate

<a id="def-cal-definition-gate"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Gate

# Gate

An owner-scoped checkpoint deciding or routing whether a candidate may proceed, proceed with named risk, stop or defer. Its criteria, evidence, verdicts and consequences must be explicit.

**When it applies**

Use a promotion gate whenever a claim would cross from source evidence, inventory, ontology, research, observability, or memory into definitions, constitutions, specs, capabilities, implementation, or public-facing material.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-gate-section-2"></a>

## Source explanatory wording

A promotion gate is the moment the project asks, "is this allowed to count now?" A gate is the checkpoint that says "go", "go with this named risk", "stop", or "send this to the right owner first."

<a id="def-cal-definition-gate-section-3"></a>

## Exact governing statement

Gate is the normalized definition identified by semantic.gate, owned within scope.shared-authority, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D5, CAV2-D37 without silently merging it with another target.

Bound source-semantic basis:

A promotion gate is an explicit owner route that decides whether evidence, candidate meaning, a recurring practice, or a structural rule may become local authority, implementation work, or standalone repository material.

A gate is an explicit checkpoint that decides or routes whether a candidate term, rule, artifact, relation, method, claim, mutation, or execution may continue, must continue with named risk, must stop, or must defer to another owner.

Every CyberAlchemy v2 gate must declare its owner route, scope, inputs, criteria, possible verdicts, required evidence, residue handling, record location, and downstream effect. Unless a narrower gate defines otherwise, the minimum verdict vocabulary is `pass`, `flag`, `block`, and `defer`.

````
A gate `G` is a decision function:

```text
G(scope, input, evidence, criteria) -> verdict
verdict in {pass, flag, block, defer}
```

The verdict is admissible only if it records owner route, evidence basis,
residue or risk when present, and downstream effect.
````

- The gate may return pass, flag, or block. A flag is not a silent pass; it carries named risk and follow-up.
- Gate is not bureaucracy, not a checklist item by itself, not permission without a record, and not proof of correctness. A gate may use validators or human decisions, but the gate is the recorded transition logic and effect.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../assets/29e494b465b0-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.gate@1.0.0-candidate.1

**Content fingerprint · SHA-256**

29e494b465b013fda1e0ed9eeb6dc8fc17126eb132e15bf153b58db6075e2b97

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use a promotion gate whenever a claim would cross from source evidence,\ninventory, ontology, research, observability, or memory into definitions,\nconstitutions, specs, capabilities, implementation, or public-facing material.\n\nUse gate for any controlled transition: promotion, schema amendment,\nimplementation mutation, validation acceptance, source import, extraction,\npublic/private boundary movement, or recursive method step. A gate is the place\nwhere ambiguity either receives permission, receives risk, stops, or changes\nowner.",
  "authority_scope_ref": "scope.shared-authority",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
