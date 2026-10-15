[Documentation home](../../README.md)

# Parent-Instance Authority Separation Invariant

<a id="def-cal-definition-parent-instance-authority-separation-invariant"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Parent-Instance Authority Separation Invariant

Keeps the owner and authority of a shared parent model separate from those of a local instance. An explicit binding records their relationship without letting either silently rewrite the other.

**When it applies**

Use this invariant when CyberAlchemy defines a reusable product, capability, method, ontology, or other parent model and a Project creates or evolves a locally owned instance. Register the exact parent version, instance package, both authority claims, inherited contract, extension scope, adoption decision, specialization relation, conformance evidence, challenge and drift routes, recomposition path, and recursive stop in the Project. Route shared-model changes to the parent owner and instance-local changes to the instance owner.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

The parent owns the blueprint. The local capability owns its built instance. The Project keeps the labeled connection between them. Neither side may quietly rewrite the other.

## Exact governing statement

Parent-Instance Authority Separation Invariant is the normalized invariant identified by semantic.parent-instance-authority-separation-invariant, owned within scope.shared-authority, and carried by type.invariant. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D64 without silently merging it with another target.

Bound source-semantic basis:

The recursive instance ownership invariant is the must-hold CyberAlchemy v2 condition that a governed parent model and a locally owned instance remain connected without collapsing their semantic authority, coordination boundary, or lifecycle.

The parent-model owner holds scoped semantic authority for the shared contract and the conditions under which it may be instantiated, specialized, or composed. The named instance owner holds a separate scoped semantic authority for the instance's local meaning, state, evidence, and lifecycle. Here, `ownership` is shorthand for these explicit `CAV2-D34` authority claims; it is not inferred from a folder, label, repository permission, or generic responsibility. A Project carries the typed binding, goals, owners, evidence, and challenge route that keep the instance connected to its purpose, but Project membership or file placement does not itself create semantic, adoption, or execution authority.

The parent and instance must be joined by an explicit `CAV2-D16` typed relation bound to an exact parent version or state. The instance may narrow or realize the parent contract only inside its declared specialization scope. It must not silently redefine the parent. The parent must not absorb, overwrite, or treat instance-local meaning as shared authority without the instance owner's route and the applicable `CAV2-D48` promotion or adoption path.

````
semantic.parent-instance-authority-separation-invariant := (semantic_kind=invariant, carrier=type.invariant, owner_scope=scope.shared-authority, source_set={CAV2-D64}). Identity, carrier, and owner scope are independent axes; equality of labels does not establish equality of concepts.
````

- This invariant is not authority, ownership by file location, Project authority, repository access, inheritance by naming, schema conformance, implementation success, automatic adoption, or promotion. It does not require every artifact to have a parent model, make every capability a Project, or make every instance canonical. It governs only relationships where downstream work relies on a parent model and an independently scoped owned instance remaining connected. It is not a Discipline (`CAV2-D50`). A later Discipline may steward recurring binding audits and hardening, and a Constitution may enforce selected bindings, but neither is created or adopted by this definition.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/parent-instance-authority-separation-invariant/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.parent-instance-authority-separation-invariant@1.0.0-candidate.1

**Content fingerprint · SHA-256**

abf1ae8f7112b09fd349848b44794b71b89aa77db07d54d3bae12b317832bfc4

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use this invariant when CyberAlchemy defines a reusable product, capability,\nmethod, ontology, or other parent model and a Project creates or evolves a\nlocally owned instance. Register the exact parent version, instance package,\nboth authority claims, inherited contract, extension scope, adoption decision,\nspecialization relation, conformance evidence, challenge and drift routes,\nrecomposition path, and recursive stop in the Project. Route shared-model\nchanges to the parent owner and instance-local changes to the instance owner.",
  "authority_scope_ref": "scope.shared-authority",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
