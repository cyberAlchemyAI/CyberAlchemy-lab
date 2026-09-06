<!-- GENERATED FILE: edit definitions.json and run ../build.py. -->

# Craft First Capability Definition Prototypes

> Prototype meanings for construction and testing; not the Lab authority registry.

- Registry: `CAL-CML08-P0-DEFINITION-PROTOTYPES-EPOCH-001`
- Status: `prototype`
- Canonicality: `non-authoritative`
- Authority effect: `none`

## Index

| ID | Term | Version |
| --- | --- | --- |
| `cal.prototype.definition.definition-prototype` | Definition Prototype | `0.1.0-prototype.1` |
| `cal.prototype.definition.agent-ontology-scaffold` | Agent-Facing Ontology Scaffold | `0.1.0-prototype.1` |
| `cal.prototype.definition.product-capability-prototype` | Product Capability Prototype | `0.1.0-prototype.1` |
| `cal.prototype.definition.business-ontology-prototype` | Capability-Local Business Ontology Prototype | `0.1.0-prototype.1` |
| `cal.prototype.definition.domainspec-source-prototype` | Authored DomainSpec Source Prototype | `0.1.0-prototype.1` |
| `cal.prototype.definition.compiled-graph-prototype` | Compiled Graph Prototype | `0.1.0-prototype.1` |
| `cal.prototype.definition.system-ontology-prototype` | System Ontology Prototype | `0.1.0-prototype.1` |
| `cal.prototype.definition.implementation-prototype` | Implementation Prototype | `0.1.0-prototype.1` |
| `cal.prototype.definition.testable-product-candidate` | Testable Product Candidate | `0.1.0-prototype.1` |
| `cal.prototype.definition.product-test-evidence` | Product-Test Evidence | `0.1.0-prototype.1` |
| `cal.prototype.definition.product-approval` | Product Approval | `0.1.0-prototype.1` |
| `cal.prototype.definition.post-approval-authority-decision` | Post-Approval Authority Decision | `0.1.0-prototype.1` |

## Definition Prototype

- ID: `cal.prototype.definition.definition-prototype`
- Classification: `prototype-definition`
- Lifecycle: `prototype`
- Authority effect: `none`

### Scientific/formal voice

A Definition Prototype is a versioned, source-bound, challengeable meaning hypothesis for one construction epoch. It states scope, exclusions, boundaries, tests, and residue, may be revised without an authority decision before candidate freeze, and always has authority effect none.

```text
DefinitionPrototype(d,e) = (id, version, meaning, scope, exclusions, tests, sources, residue); authority_effect(d)=none; revise(d) => new_epoch_or_version(d), not admission(d).
```

Notation:

- `d` — One prototype meaning record.
- `e` — The product-construction epoch using it.

Testable conditions:

- All three voices exist.
- authority_effect equals none.
- Source bindings and non-collapse boundaries resolve.

### Plain-language voice

A Definition Prototype is the current best explicit meaning used to build and learn. It can change as the prototype teaches us more.

### CyberAlchemy Lab context

CML08-P0 uses these records to make the first Craft vertical buildable without putting unfinished meanings into the Lab authority registry.

### Boundaries

- Definition Prototype is not an admitted Definition.
- Validation of its shape is not semantic promotion.
- A later canonical Definition may preserve, revise, split, reclassify, collapse, or drop it.

### Four facets

- **Classification** — prototype meaning
- **Schema** — closed prototype-definition record
- **Human Projection** — generated explanation with three colocated voices
- **Machine Checkable** — versioned, source-bound, authority-effect-none

## Agent-Facing Ontology Scaffold

- ID: `cal.prototype.definition.agent-ontology-scaffold`
- Classification: `prototype-definition`
- Lifecycle: `prototype`
- Authority effect: `none`

### Scientific/formal voice

An Agent-Facing Ontology Scaffold is a non-authoritative, versioned navigation projection over exact prototype sources. Its nodes and relation hints help agents locate and trace construction material but cannot establish truth, admission, permission, or a reason to block work outside its declared dependencies.

```text
Scaffold(s)=(sources,nodes,hints,questions,evidence,challenges); authority_effect(s)=none; hint(s,a,b) =/=> canonical_relation(a,b); drift(x) blocks only if x in selected_dependencies(s).
```

Notation:

- `s` — One agent navigation scaffold.
- `hint` — A provisional relation aid, not an admitted semantic edge.

Testable conditions:

- canonicality equals non-authoritative.
- authority_effect equals none.
- No scaffold validation result grants admission.

### Plain-language voice

The scaffold is a map for agents. It helps them find and connect prototype material, but the map is not the territory or an approval gate.

### CyberAlchemy Lab context

CML08-P1 will project these prototype terms into a navigation scaffold after P0 passes; the suspended Python ontology runtime will not own or gate it.

### Boundaries

- Ontology Scaffold is not canonical truth or semantic authority.
- Scaffold currentness is not product approval.
- A scaffold cannot widen its selected dependency set implicitly.

### Four facets

- **Classification** — non-authoritative agent navigation
- **Schema** — versioned scaffold with exact sources and hints
- **Human Projection** — generated map explanation
- **Machine Checkable** — selected-dependency-closure, prototype-hint-relations, authority-effect-none

## Product Capability Prototype

- ID: `cal.prototype.definition.product-capability-prototype`
- Classification: `prototype-definition`
- Lifecycle: `prototype`
- Authority effect: `none`

### Scientific/formal voice

A Product Capability Prototype is a versioned hypothesis of a Product-owned outcome, participants, consumers, scope, exclusions, contracts, context policies, evidence route, and challenge route. It specializes CAV2-D67 for learning but is not adopted and selects no realization or permission.

```text
PCP=(id,product_ref,outcome,scope,exclusions,participants,consumers,contracts,context_policies,evidence,challenges); authority_effect(PCP)=none; PCP =/= ProductFeature; PCP =/= CapabilityInstance.
```

Notation:

- `PCP` — One provisional Product Capability outcome contract.

Testable conditions:

- Product Feature and Product Capability IDs cannot collapse.
- Capability Instance has a separate ID.
- No adoption or authority field is inferred.

### Plain-language voice

This is our current testable guess about what useful outcome Craft must enable, before deciding that the capability is final or adopted.

### CyberAlchemy Lab context

The first Craft prototype may explore System Construction, but the existing Product Feature name does not silently create this capability identity.

### Boundaries

- Product Capability Prototype is not Product Feature.
- Product Capability Prototype is not Capability Instance.
- A working implementation does not adopt the capability.

### Four facets

- **Classification** — Product-owned outcome hypothesis
- **Schema** — closed provisional capability contract
- **Human Projection** — generated outcome and boundary explanation
- **Machine Checkable** — product-anchor, identity-non-collapse, authority-effect-none

## Capability-Local Business Ontology Prototype

- ID: `cal.prototype.definition.business-ontology-prototype`
- Classification: `prototype-definition`
- Lifecycle: `prototype`
- Authority effect: `none`

### Scientific/formal voice

A Capability-Local Business Ontology Prototype is an exact, bounded, provisional semantic closure for one Product Capability Prototype and declared context posture. It contains only meanings needed to state and test that outcome and remains revisable and non-authoritative.

```text
BOP(c,e)=(concepts,relations,rules,constraints,language,sources,residue); closure(BOP) subset required_meaning(c); authority_effect(BOP)=none; BOP =/= SystemOntology.
```

Notation:

- `BOP` — One capability-local business meaning prototype.
- `c` — The Product Capability Prototype it serves.

Testable conditions:

- Every node supports a named capability obligation.
- Every source selector is exact.
- Business and system ontology identities remain distinct.

### Plain-language voice

This is the smallest shared model of the business meaning needed to test one capability—not a universal ontology of everything nearby.

### CyberAlchemy Lab context

CML09-P2 will build this closure only after the provisional Craft capability and context posture are explicit.

### Boundaries

- Business Ontology Prototype is not a global ontology import.
- It is not the compiled System Ontology Prototype.
- Context placement does not create its meaning.

### Four facets

- **Classification** — capability-local business meaning prototype
- **Schema** — bounded concepts, relations, rules, and sources
- **Human Projection** — generated vocabulary and scope explanation
- **Machine Checkable** — capability-closure, source-selection, business-system-separation

## Authored DomainSpec Source Prototype

- ID: `cal.prototype.definition.domainspec-source-prototype`
- Classification: `prototype-definition`
- Lifecycle: `prototype`
- Authority effect: `none`

### Scientific/formal voice

An Authored DomainSpec Source Prototype is the machine-canonical typed intent for one prototype epoch. It binds the selected capability and business prototypes, declares exact language and compiler profiles, and is the sole authored source of its compiled graph and system-ontology projections for that epoch.

```text
DSP_e = authored(intent,contracts,constraints,profiles,sources); Graph_e=compile(DSP_e); SystemOntology_e=project(Graph_e); edit(Graph_e or SystemOntology_e) forbidden as authored change.
```

Notation:

- `DSP_e` — Authored DomainSpec prototype source for epoch e.

Testable conditions:

- Compiler inputs resolve.
- Generated outputs reproduce.
- No generated artifact is accepted as competing authored source.

### Plain-language voice

This is the editable typed blueprint. The graph and system model are built from it and are never edited as competing blueprints.

### CyberAlchemy Lab context

The first Craft thin vertical will place its authored prototype source inside the prototype epoch until final candidate placement is selected.

### Boundaries

- Authored DomainSpec Source Prototype is not Compiled Graph Prototype.
- It is not System Ontology Prototype.
- Prototype source validity does not approve a product.

### Four facets

- **Classification** — authored typed-intent prototype
- **Schema** — closed source/profile/input contract
- **Human Projection** — generated blueprint explanation
- **Machine Checkable** — authored-generated-direction, profile-exactness, compiler-input-closure

## Compiled Graph Prototype

- ID: `cal.prototype.definition.compiled-graph-prototype`
- Classification: `prototype-definition`
- Lifecycle: `prototype`
- Authority effect: `none`

### Scientific/formal voice

A Compiled Graph Prototype is an immutable derived projection of one exact DomainSpec source digest and compiler profile digest. It exposes normalized typed nodes and relations for construction but owns no meaning independently of those inputs.

```text
CG=compile(DSP@d, Compiler@c); same(d,c) => byte_equal(CG); change(CG) requires change(DSP or Compiler); authority_effect(CG)=none.
```

Notation:

- `CG` — One compiled graph prototype.
- `d` — The exact authored source digest.
- `c` — The exact compiler profile digest.

Testable conditions:

- Trace resolves to exact source.
- Two-run identity passes.
- Graph contains no untraceable node or edge.

### Plain-language voice

The compiled graph is the reproducible machine form built from the typed blueprint. If it needs changing, change the blueprint or compiler—not the graph by hand.

### CyberAlchemy Lab context

CML09-P2 will use this graph as the exact bridge between Craft DomainSpec source and the System Ontology Prototype.

### Boundaries

- Compiled Graph Prototype is not authored DomainSpec source.
- It is not System Ontology Prototype.
- Determinism is product evidence, not authority.

### Four facets

- **Classification** — deterministic generated construction graph
- **Schema** — typed nodes, edges, provenance, and compiler binding
- **Human Projection** — generated graph summary
- **Machine Checkable** — source-trace, two-run-byte-identity, no-hand-edit

## System Ontology Prototype

- ID: `cal.prototype.definition.system-ontology-prototype`
- Classification: `prototype-definition`
- Lifecycle: `prototype`
- Authority effect: `none`

### Scientific/formal voice

A System Ontology Prototype is a non-authoritative deterministic projection from an exact Compiled Graph Prototype that organizes implementation-facing obligations and trace links for one product epoch. It cannot introduce requirements absent from the authored DomainSpec closure.

```text
SOP=system_project(CG@g); obligations(SOP) subset traceable(CG); same(g,projector) => byte_equal(SOP); authority_effect(SOP)=none.
```

Notation:

- `SOP` — One system ontology prototype.
- `g` — The exact compiled graph digest.

Testable conditions:

- Trace coverage is total.
- Two-run identity passes.
- Business and system meanings remain distinct.

### Plain-language voice

This is the implementation-facing map generated from the compiled blueprint. It organizes what must be built without inventing new product meaning.

### CyberAlchemy Lab context

Craft implementation prototypes will bind to exact obligations in this projection, while the capability-local business model remains a separate upstream prototype.

### Boundaries

- System Ontology Prototype is not Business Ontology Prototype.
- It is not an implementation or runtime.
- It cannot acquire authority from generated completeness.

### Four facets

- **Classification** — generated implementation-facing scaffold
- **Schema** — obligations, interfaces, constraints, and trace links
- **Human Projection** — generated system-model explanation
- **Machine Checkable** — graph-trace-totality, no-new-requirements, authority-effect-none

## Implementation Prototype

- ID: `cal.prototype.definition.implementation-prototype`
- Classification: `prototype-definition`
- Lifecycle: `prototype`
- Authority effect: `none`

### Scientific/formal voice

An Implementation Prototype is a versioned provisional realization bound to exact system-ontology obligations, source bytes, profiles, dependencies, tests, effects, and residue. It may be revised during prototype learning and cannot be activated for governed use by validation or proximity.

```text
IP=(source,bindings,profiles,deps,tests,effects,residue); satisfies_test(IP,t) =/=> activated(IP); authority_effect(IP)=none; change(IP) before freeze => prototype_revision.
```

Notation:

- `IP` — One implementation prototype.
- `t` — One bounded prototype test.

Testable conditions:

- Implementation trace coverage is measured.
- Undeclared effects fail.
- Passing tests do not create runtime authority.

### Plain-language voice

This is working code or behavior built to learn and test. It is not yet an activated or approved runtime.

### CyberAlchemy Lab context

The first Craft prototype will implement only the smallest final-path-neutral behavior needed for the L0 smoke result.

### Boundaries

- Implementation Prototype is not an activated runtime.
- It is not a Testable Product Candidate until frozen with every required component.
- A passing test does not approve the product.

### Four facets

- **Classification** — provisional executable realization
- **Schema** — source, obligations, profiles, effects, tests, and residue
- **Human Projection** — generated behavior and boundary explanation
- **Machine Checkable** — obligation-binding, effect-declaration, no-activation

## Testable Product Candidate

- ID: `cal.prototype.definition.testable-product-candidate`
- Classification: `prototype-definition`
- Lifecycle: `prototype`
- Authority effect: `none`

### Scientific/formal voice

A Testable Product Candidate is a deterministically frozen manifest that closes every candidate-bound prototype component, generated output, source selector, environment profile, test contract, placement, residue, and rollback boundary by exact identity and digest. Any bound-byte change invalidates the candidate and dependent evidence.

```text
TPC=freeze({component_i@digest_i}, environment@test_digest, contract@digest, rollback); change(any bound digest) => stale(TPC) and invalidate(evidence(TPC)); authority_effect(TPC)=none.
```

Notation:

- `TPC` — One exact immutable product-under-test manifest.

Testable conditions:

- Freeze reproduces byte-identically.
- Missing component fails closure.
- Changed component makes the candidate stale.

### Plain-language voice

This is the exact product package we agree to test. If any included byte changes, it is a different candidate and must be tested again.

### CyberAlchemy Lab context

CML11-P4 will freeze the first Craft candidate only after the complete prototype spine reaches TESTED_PROTOTYPE.

### Boundaries

- Testable Product Candidate is not a mutable prototype epoch.
- It is not Product-Test Evidence.
- It is not Product Approval or release state.

### Four facets

- **Classification** — immutable product-under-test manifest
- **Schema** — digest-closed components, environment, tests, placement, and rollback
- **Human Projection** — generated candidate manifest explanation
- **Machine Checkable** — closure, deterministic-freeze, stale-byte-invalidation

## Product-Test Evidence

- ID: `cal.prototype.definition.product-test-evidence`
- Classification: `prototype-definition`
- Lifecycle: `prototype`
- Authority effect: `none`

### Scientific/formal voice

Product-Test Evidence is a candidate-bound, contract-bound, environment-bound collect-all outcome set in which every required product test is PASS, FAIL, or NOT_EVALUABLE with causal detail. Only a complete current all-PASS set makes product approval eligible; it never performs approval.

```text
PTE=evaluate(TPC@c, Contract@t, Env@e) -> {outcome_i}; eligible(approval) iff complete(outcomes) and current(c,t,e) and forall required i: outcome_i=PASS; PTE =/=> ProductApproval.
```

Notation:

- `PTE` — The complete current product-test outcome set.
- `TPC` — The exact frozen candidate tested.

Testable conditions:

- Every required test ID appears once.
- Stale candidate or environment rejects currentness.
- Approval eligibility is false unless every required outcome passes.

### Plain-language voice

This is the complete, fresh report of how the exact frozen product performed against every required product test. It supports a decision but does not make it.

### CyberAlchemy Lab context

CML12-P5 will collect positive, hostile, determinism, stale-byte, rollback, and preapproval-authority-rejection outcomes for the first Craft candidate.

### Boundaries

- Product-Test Evidence is not generic Validation PASS.
- It is not Product Approval.
- It cannot authorize admission, activation, release, or deployment.

### Four facets

- **Classification** — complete current frozen-candidate evidence
- **Schema** — candidate, contract, environment, required outcomes, and residue
- **Human Projection** — generated product-test report
- **Machine Checkable** — collect-all, currentness, approval-eligibility-only

## Product Approval

- ID: `cal.prototype.definition.product-approval`
- Classification: `prototype-definition`
- Lifecycle: `prototype`
- Authority effect: `none`

### Scientific/formal voice

Product Approval is an owner-qualified decision that binds one exact Testable Product Candidate digest and one exact current complete Product-Test Evidence digest, records approve, reject, defer, or stop, and if approved has product-approval-only effect. It creates no operational authority.

```text
PA=(owner,TPC@c,PTE@e,outcome,invalidation); eligible(PA) iff all_required_tests_pass_current(e,c); approved(PA) =/=> authorized or admitted or activated or released or deployed.
```

Notation:

- `PA` — One exact Product-owner decision.

Testable conditions:

- Unknown future bytes cannot enter the decision.
- Changed bound bytes invalidate approval.
- Operational authority fields remain absent.

### Plain-language voice

The Product owner decides whether the exact tested product is good enough as a product result. Even yes does not mean it may be activated, published, or deployed.

### CyberAlchemy Lab context

CML13-P6 is the single human checkpoint in this construction chain and ends product construction without bundling operational permission.

### Boundaries

- Product Approval is not Product-Test Evidence.
- It is not admission or authority activation.
- It is not publication, release, deployment, or permission to execute.

### Four facets

- **Classification** — exact Product-owner decision
- **Schema** — owner, candidate digest, evidence digest, outcome, invalidation, and product-only effect
- **Human Projection** — generated decision explanation
- **Machine Checkable** — eligibility, exact-byte-binding, no-operational-authority

## Post-Approval Authority Decision

- ID: `cal.prototype.definition.post-approval-authority-decision`
- Classification: `prototype-definition`
- Lifecycle: `prototype`
- Authority effect: `none`

### Scientific/formal voice

A Post-Approval Authority Decision is an independently owned, exact-scope decision request and outcome for one operational effect that may be prepared only after exact Product Approval. Product Approval is a prerequisite but never satisfies or predicts its outcome.

```text
PAD=(effect,owner,target@digest,product_approval_ref,evidence,rollback,outcome); eligible(PAD) only if exact_product_approved; approved(PA) =/=> approved(PAD); each effect requires separate scope.
```

Notation:

- `PAD` — One separately governed post-product decision.
- `effect` — Admission, activation, cutover, publication, release, deployment, or another exact operational effect.

Testable conditions:

- Preapproval requests are rejected.
- One effect cannot authorize another.
- Product approval carries no inferred outcome.

### Plain-language voice

After the product is approved, the right owner must still separately decide each real-world action, such as activation, publication, or deployment.

### CyberAlchemy Lab context

These decisions are operational-support workflows outside the CML08-P0 through CML13-P6 product-construction chain.

### Boundaries

- Post-Approval Authority Decision is not Product Approval.
- It cannot be requested before exact product approval.
- Admission, activation, cutover, publication, release, and deployment remain separate effects.

### Four facets

- **Classification** — separate post-product operational decision
- **Schema** — effect, owner, exact target, product approval, evidence, rollback, and outcome
- **Human Projection** — generated authority-boundary explanation
- **Machine Checkable** — post-approval-eligibility, effect-separation, no-inference-from-product-approval

## Claim ceiling

These twelve records are non-authoritative Definition Prototypes for one Craft construction epoch. They do not modify the Lab Definition registry, admit meaning, activate an Artifact Type, approve a product, or grant operational authority.
