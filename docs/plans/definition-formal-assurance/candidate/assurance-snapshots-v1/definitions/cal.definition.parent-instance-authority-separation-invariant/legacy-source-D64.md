## CAV2-D64: Recursive Instance Ownership Invariant

Status: active
Term: recursive instance ownership invariant
Aliases: instance ownership invariant, recursive ownership invariant, parent-instance ownership invariant, model-instance ownership invariant, capability instance ownership
Promoted: 2026-08-29 by owner-requested product-instance ownership modeling; definition authority only

### Normative Definition

The recursive instance ownership invariant is the must-hold CyberAlchemy v2
condition that a governed parent model and a locally owned instance remain
connected without collapsing their semantic authority, coordination boundary,
or lifecycle.

The parent-model owner holds scoped semantic authority for the shared contract
and the conditions under which it may be instantiated, specialized, or
composed. The named instance owner holds a separate scoped semantic authority
for the instance's local meaning, state, evidence, and lifecycle. Here,
`ownership` is shorthand for these explicit `CAV2-D34` authority claims; it is
not inferred from a folder, label, repository permission, or generic
responsibility. A Project carries the typed binding, goals, owners, evidence,
and challenge route that keep the instance connected to its purpose, but
Project membership or file placement does not itself create semantic,
adoption, or execution authority.

The parent and instance must be joined by an explicit `CAV2-D16` typed relation
bound to an exact parent version or state. The instance may narrow or realize
the parent contract only inside its declared specialization scope. It must not
silently redefine the parent. The parent must not absorb, overwrite, or treat
instance-local meaning as shared authority without the instance owner's route
and the applicable `CAV2-D48` promotion or adoption path.

### Invariant Statement

For a parent model `M`, owned instance `I`, coordinating Project `P`, and typed
binding `B`, the relationship is admissible only when:

```text
RecursiveInstanceBinding =
  (binding_id, project_ref, model_ref, model_version_ref,
   model_authority_claim, instance_ref, instance_kind,
   instance_authority_claim, relation_kind, inherited_contract_ref,
   extension_scope, adoption_decision_ref, adoption_owner_route,
   adoption_posture, conformance_ref, lifecycle_state, altitude,
   evidence_refs, challenge_route, drift_owner_route, drift_route,
   recomposition_route, recursion_budget_or_stop,
   terminal_owner_or_handoff, authority_effect)

valid(B) only if
  B.project_ref = P
  and B.model_ref = M
  and B.instance_ref = I
  and exact(B.model_version_ref)
  and typed_relation(B.relation_kind, I, M)
  and scoped_authority(B.model_authority_claim, M)
  and scoped_authority(B.instance_authority_claim, I)
  and exact(B.inherited_contract_ref)
  and within_scope(I, B.extension_scope)
  and owner_decided(B.adoption_decision_ref,
                    B.adoption_owner_route,
                    B.adoption_posture,
                    B.model_version_ref)
  and preserves_parent_meaning(I, M)
  and B.authority_effect = none

change(M) =/=> adopted_by(I)
change(I) =/=> promoted_into(M)
conforms(I, M) =/=> authority(I) or authority(M)
member_of(I, P) =/=> authority(I)

conflicts_with(I, B.inherited_contract_ref) => drift(I, M)
within(I, B.extension_scope) =/=> drift(I, M)

becomes_parent(I)
  => exists B_next:
       complete_recursive_binding(B_next)
       and altitude(B_next) > altitude(B)
       and bounded(B_next.recursion_budget_or_stop,
                   B_next.terminal_owner_or_handoff)
```

The model-authority lane and instance-authority lane remain distinct roles even
when the same actor currently fills both. Variation inside the declared
extension scope is local specialization, not drift. Conflict with the exact
adopted mandatory contract is drift and is routed to the named drift owner. If
the parent version, either authority claim, inherited contract, extension scope,
adoption decision, conformance relation, challenge route, drift route,
recomposition path, or recursive stop is missing or disputed, the binding is
residue or a blocker rather than an implicit ownership or authority transfer.

### Schema

Schema handle: `CAV2-D64-SCHEMA` — tracked in
[DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md). Status: tracked (documentary).
The Project package owns the first machine-checkable binding registry because
Project carries the durable coordination identity. `CAV2-PROJECT-SCHEMA-AMEND-D64-001`
adds binding references to the Project record and a closed registry shape, but
the registry currently contains no concrete binding.
`CAV2-GOAL-PACKAGE-SCHEMA-AMEND-D64-PREREQ-001` adds separate Project-owned
candidate registries for complete `CAV2-D34` claim tuples and exact inherited
contracts. These prerequisite records remain source-declared candidates: they
do not activate authority, admit a relation, record adoption, prove
conformance, or satisfy this invariant. The Governance ontology
registers this definition as `GOV-INV-CAV2-D64` and links it to the candidate
review rule `GOV-RULE-D64-BINDING-COMPLETE`; those records remain ontology
instances with no authority, adoption, enforcement, implementation, or Project
conformance effect.

`CAV2-GOAL-PACKAGE-SCHEMA-AMEND-D64-ADOPTION-CANDIDATE-001` first added one
Project-owned adoption-decision candidate envelope bound to the exact Define
model-version ref and inherited-contract digest.
`CAV2-GOAL-PACKAGE-SCHEMA-AMEND-D64-RELATION-CANDIDATE-001` then records the
user's `REL-INSTANCE-OF` choice as one directed, Project-owned semantic
relation candidate and binds that candidate into the envelope by ID and digest.
`CAV2-GOAL-PACKAGE-SCHEMA-AMEND-D64-RELATION-ADMISSION-001` preserves that
candidate and its digest, records the protected joint-owner `ADMIT-INSTANCE-OF`
decision, and adds a separately digested admitted-relation record. That exact
record supplies the `typed_relation(...)` conjunct for the named source, target,
versions, direction, kind, and inherited contract only. The envelope's selected
D48 adoption posture and owner decision remain null. Admission is not the
`owner_decided(...)` witness, conformance, authority activation, or a concrete
binding's `adoption_decision_ref`.

Field meanings:

- `binding_id` identifies the binding; `project_ref` identifies its coordinating
  Project; `model_ref` and `model_version_ref` identify the exact parent state.
- `model_authority_claim` and `instance_authority_claim` each carry the
  `CAV2-D34` scope, owner, surface, object, operation, basis, effect, and
  challenge route for their separate semantic lanes.
- `instance_ref` and `instance_kind` identify the local object;
  `relation_kind` types its directed connection to the parent.
- `inherited_contract_ref` identifies the mandatory adopted parent contract;
  `extension_scope` states where local specialization is allowed.
- `adoption_decision_ref`, `adoption_owner_route`, and `adoption_posture` bind
  adoption of the exact parent version to an owner decision rather than
  proximity or conformance.
- `conformance_ref`, `lifecycle_state`, `altitude`, and `evidence_refs` record
  checked relationship state without granting authority.
- `challenge_route`, `drift_owner_route`, and `drift_route` distinguish a
  challenge from contract drift and name who routes resolution.
- `recomposition_route` returns instance learning upstream only as a typed
  candidate; `recursion_budget_or_stop` and `terminal_owner_or_handoff` bound
  any instance that becomes a parent.
- `authority_effect` is `none` for the binding itself.

The current Define prerequisite candidate uses `cav2.define` as the parent and
`cav2.define.system-runtime.v1` as the local instance. It binds both to exact
profile states and selects `instance_of` only as an unadmitted semantic
candidate. The protected joint-owner decision now admits one separately digested
exact relation as the `typed_relation(...)` witness. `child-package` remains
separate topology evidence; authority-claim promotion, D48 adoption, conformance,
complete recursion termination, and terminal handoff remain unresolved. The exact
D48 adopt/reject/defer/stop gate is now presented to the `CyberAlchemy v2 Define
runtime owner`, but no option is selected; gate preparation is not the
`owner_decided(...)` witness. This is
typed-relation evidence only, not a `RecursiveInstanceBinding` or D64 satisfaction.

### Axiom And Invariant Basis

The authority basis is `CAV2-D34` and `CAV2-D41`: authority moves only through
an explicit scoped owner route and does not transfer through proximity,
membership, generation, validation, or repeated use. `CAV2-D30` supplies the
bounded recursive separation of artifact, layer, owner, recomposition, and stop
condition. `CAV2-D16` requires the parent-instance wire to be typed and visible.

This definition specializes those existing principles for parent-model and
owned-instance relationships. It does not create a new authority kind.

### Validation Mode

Current validation mode: `review-only`.

The Governance ontology registration makes the invariant and its candidate
operational rule discoverable. The Project package can now validate the admitted
typed-relation witness plus the closed shape and reference closure of any registered
binding, but it has no concrete binding to evaluate. D48 owner adoption, conformance,
complete recursion termination, and terminal handoff remain absent, so CAV2-D64 is
not satisfied. This does not supply the unresolved source-owned semantic
version, exact grounding Governance Axiom, adopted Constitution membership,
enforcement binding, complete Define Project binding, kernel program, or runtime
integration.

A review checks that every load-bearing parent-instance relationship has the
complete `CAV2-D64-SCHEMA` binding, that both owner lanes resolve, that the
Project is not treated as an authority envelope, that parent and instance
changes do not propagate implicitly, that adoption binds an exact parent
version and owner decision, that inherited contract and extension scope are
separate, that drift and recomposition follow their named routes, and that
conformance claims remain inside their evidence. A later Project-package
validator may make these checks deterministic only after a separately reviewed
schema amendment witness.

### Operational Interpretation

Use this invariant when CyberAlchemy defines a reusable product, capability,
method, ontology, or other parent model and a Project creates or evolves a
locally owned instance. Register the exact parent version, instance package,
both authority claims, inherited contract, extension scope, adoption decision,
specialization relation, conformance evidence, challenge and drift routes,
recomposition path, and recursive stop in the Project. Route shared-model
changes to the parent owner and instance-local changes to the instance owner.

### Plain-Language Intuition

The parent owns the blueprint. The local capability owns its built instance.
The Project keeps the labeled connection between them. Neither side may quietly
rewrite the other.

### Domain-Context Voice

In CyberAlchemy v2, the product ontology is the intended owner surface for the
shared CyberAlchemy product model. A Define Project can coordinate the goals,
owners, evidence, and lifecycle for a Define product instance, while a
separately established Define instance owner would own that instance's business
meaning. The product ontology may register and constrain an adopted instance;
the Define instance may specialize the adopted product contract inside its
extension scope. Neither relationship lets the Project, ontology projection,
validation result, or runtime claim semantic authority it was not granted.

The current candidate profiles do not yet prove this binding: they do not carry
the complete version-exact adoption record and separately scoped instance-owner
claim required here. They are candidate evidence for the first application of
the invariant, not a conforming instance by declaration.

### Boundary

This invariant is not authority, ownership by file location, Project authority,
repository access, inheritance by naming, schema conformance, implementation
success, automatic adoption, or promotion. It does not require every artifact
to have a parent model, make every capability a Project, or make every instance
canonical. It governs only relationships where downstream work relies on a
parent model and an independently scoped owned instance remaining connected.

It is not a Discipline (`CAV2-D50`). A later Discipline may steward recurring
binding audits and hardening, and a Constitution may enforce selected bindings,
but neither is created or adopted by this definition.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md)
- [../../goals/README.md](../../goals/README.md)
- [../../ontology/product/README.md](../../ontology/product/README.md)
- [../../ontology/governance/invariants.json](../../ontology/governance/invariants.json)
- [../../ontology/governance/rules.json](../../ontology/governance/rules.json)
- [../../goals/ontology/project-instance-bindings.json](../../goals/ontology/project-instance-bindings.json)
- [../../goals/ontology/project-binding-schema-amendment.json](../../goals/ontology/project-binding-schema-amendment.json)
- [../../define/business-ontology/README.md](../../define/business-ontology/README.md)
