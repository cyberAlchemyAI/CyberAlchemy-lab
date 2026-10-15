[Documentation home](../../README.md)

# Artifact Lifetime

<a id="def-cal-definition-artifact-lifetime"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Artifact Lifetime

Distinguishes temporary work products from standing references maintained over time. Temporary work may preserve competing interpretations; standing references must not retain live simultaneous contradictions. Recorded supersession is permitted.

**When it applies**

Assign durability per canonical-kind as a default (spec / definition / constitution / decision / axiom / ledger -> perennial; discovery / research / session -> ephemeral), overridable per instance with an owner note. When reviewing a perennial artifact, treat a live contradiction as a defect to resolve; when reviewing an ephemeral one, treat contradictions as legitimate exploration to preserve.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

Some documents are meant to be used and then set aside once they have done their job (a discovery); others are meant to stand and be kept true (a spec). The first kind is allowed to argue with itself; the second is not — though a logbook is still allowed to record that things changed over time.

## Exact governing statement

Artifact Lifetime is the normalized definition identified by semantic.artifact-lifetime, owned within scope.shared-authority, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D52 without silently merging it with another target.

Bound source-semantic basis:

Artifact durability is the axis that classifies a `CAV2-D51` canonical artifact by **intended lifespan** — `ephemeral` (a work-product meant to be produced, consumed, and retired) or `perennial` (a standing reference meant to endure and be maintained). Durability is **orthogonal** to the `authority_kind` (`CAV2-D49`) and to maturity/status (`CAV2-D23`): two artifacts of the same kind may differ in durability — a discovery and an inventory index are both `Evidence`, yet the discovery is ephemeral and the index is perennial.

Durability carries one **contradiction-tolerance** obligation (typed coupling, `CAV2-D16`):

- an **ephemeral** artifact **may hold live contradictions** — competing hypotheses and unresolved tensions are expected and preserved; - a **perennial** artifact **must not hold live simultaneous contradictions**. *Temporal supersession* — a later entry overriding an earlier one in an append-only record (`CAV2-D26` ledger), or a decision record narrating the contradiction it resolved (`CAV2-D36`) — is **not** a live contradiction and is permitted.

````
```text
durability(a) in { ephemeral, perennial }
durability(a)  orthogonal-to  authority_kind(a)   (CAV2-D29: independent of authority-kind)
durability(a)  orthogonal-to  status(a)         (CAV2-D23: independent of maturity)
perennial(a)   ->  not ( a holds live  P and not-P simultaneously )
ephemeral(a)   ->  a may hold live  P and not-P
temporal supersession ( E_t overrides E_{t-1} ) is not a live contradiction
```
````

- Artifact durability is **not** maturity/status (`CAV2-D23`): a mature discovery is still ephemeral, a draft spec is still perennial. It is **not** authority: perennial does not mean authoritative (a perennial spec may still be a candidate). It is **not** regenerability: a projection is derived and regenerable, which is a separate property, not "ephemeral" — durability is about intended lifespan, not whether the artifact can be rebuilt. The two-value set may later gain an append-only/monotonic third value if the ledger case proves the live-vs-temporal refinement insufficient; that is an owner-gated extension.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/artifact-lifetime/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.artifact-lifetime@1.0.0-candidate.1

**Content fingerprint · SHA-256**

c7f9bf9037bb22ac39cb4e1e5530dbca4a330fa6e231da343945d76ebef523bf

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Assign durability per canonical-kind as a default (spec / definition /\nconstitution / decision / axiom / ledger -> perennial; discovery / research /\nsession -> ephemeral), overridable per instance with an owner note. When reviewing\na perennial artifact, treat a live contradiction as a defect to resolve; when\nreviewing an ephemeral one, treat contradictions as legitimate exploration to\npreserve.",
  "authority_scope_ref": "scope.shared-authority",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
