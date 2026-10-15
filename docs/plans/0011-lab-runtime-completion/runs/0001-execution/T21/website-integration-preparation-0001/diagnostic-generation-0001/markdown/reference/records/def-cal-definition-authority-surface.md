[Documentation home](../../README.md)

# Authority Surface

<a id="def-cal-definition-authority-surface"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Authority Surface

# Authority Surface

An identified project document or record permitted to govern meaning, structural rules, acceptance decisions or contracts within a specified scope.

**When it applies**

Use authority layers to prevent research, inventory, ontology, observability, memory, generated projections, and implementation evidence from silently rewriting definitions or rules.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-authority-surface-section-2"></a>

## Source explanatory wording

An authority layer says which document is allowed to count.

<a id="def-cal-definition-authority-surface-section-3"></a>

## Exact governing statement

Authority Surface is the normalized definition identified by semantic.authority-surface, owned within scope.shared-authority, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D3 without silently merging it with another target.

Bound source-semantic basis:

An authority layer is a project-local surface that is allowed to define normative meaning, structural rules, promotion decisions, or contracts for a specific scope.

````
semantic.authority-surface := (semantic_kind=definition, carrier=type.definition, owner_scope=scope.shared-authority, source_set={CAV2-D3}). Identity, carrier, and owner scope are independent axes; equality of labels does not establish equality of concepts.
````

- An authority layer can cite evidence, but evidence does not become authority unless the responsible owner promotes it.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../assets/e439f0567385-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.authority-surface@1.0.0-candidate.1

**Content fingerprint · SHA-256**

e439f0567385b86c8102e2285764853f87f0c3946b45536e61b77d8fec033659

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use authority layers to prevent research, inventory, ontology, observability,\nmemory, generated projections, and implementation evidence from silently\nrewriting definitions or rules.",
  "authority_scope_ref": "scope.shared-authority",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
