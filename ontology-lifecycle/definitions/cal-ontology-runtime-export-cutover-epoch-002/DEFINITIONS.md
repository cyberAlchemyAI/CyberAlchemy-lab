<!-- GENERATED FILE: edit definition-prototype.json and rerun validate.py. -->

# D65 epoch-002 definition prototype

- Prototype: `CAL-D65-EPOCH-002-DEFINITION-PROTOTYPE-001`
- Stage: `D65-S1`
- Status: `prototype`
- Next product frontier: `D65-S2`
- Product approval: `not-requested`
- Authority effect: `none`

## Prototype-First Construction

- ID: `cal.epoch-002.prototype-first-construction`
- Disposition: `reuse`
- Definition ref: `CAV2-D65`

Construction advances through inspectable definition, ontology, product, business, DomainSpec, compiled-system, implementation, and test prototypes until one exact product candidate can be frozen and tested. Product approval and every authority request occur only after those product tests pass.

Plain language: Build and test the whole candidate first; ask for approval only when the exact product is ready.

Boundary: It is not permission to admit, activate, export, migrate, cut over, publish, release, deploy, or create another external effect.

## Product Capability

- ID: `cal.epoch-002.product-capability`
- Disposition: `reuse`
- Definition ref: `CAV2-D67`

The stable product outcome for epoch 002 remains reconstruction of governed ontology state and bounded context projections from canonical event histories; the implementation and interface may change without silently changing that outcome.

Plain language: The capability says what useful result the product must provide, not which crate or adapter provides it.

Boundary: It is not a component, adapter, test receipt, permission, authority grant, deployment, or release state.

## Context Map

- ID: `cal.epoch-002.context-map`
- Disposition: `reuse`
- Definition ref: `cal.definition.context-map@2.0.0-candidate.1`

The Context Map is the sole canonical owner of exact endpoint membership and typed directional relationships. Endpoint contexts do not canonically backreference it; reverse membership is a disposable generated projection.

Plain language: The map owns who is connected and in which direction; the contexts do not duplicate that fact.

Boundary: It is not a runtime topology, import graph, ontology relation set, authority transfer, or cutover decision.

## Decision Evidence Envelope

- ID: `cal.epoch-002.decision-evidence-envelope`
- Disposition: `prototype`
- Definition ref: local prototype

A Decision Evidence Envelope is an immutable, digest-bound representation of one upstream Governance decision identity, subject, scope, outcome, effective boundary, challenge route, and evidence references that may be translated downstream without transferring decision authority.

Plain language: It carries proof of what Governance decided, while Governance keeps the authority to decide it.

Boundary: It is not the Governance Decision itself, a credential, an authority grant, an enforcement command, or permission to reinterpret the outcome.

## Versioned Adapter Export Candidate

- ID: `cal.epoch-002.versioned-adapter-export-candidate`
- Disposition: `prototype`
- Definition ref: local prototype

A Versioned Adapter Export Candidate is an isolated Rust package that exposes the context adapters through public symbols while preserving the admitted runtime and predecessor bytes unchanged and binding every exported symbol to one exact D65 candidate epoch.

Plain language: It is a new test crate for public adapters, not a rewrite of the runtime we already admitted.

Boundary: It is not an activated adapter, cutover, replacement of admitted bytes, publication, release, deployment, or stable API promise.

## Frozen Predecessor Compatibility

- ID: `cal.epoch-002.frozen-predecessor-compatibility`
- Disposition: `prototype`
- Definition ref: local prototype

Frozen Predecessor Compatibility is the testable property that a successor candidate preserves every selected admitted predecessor byte and reproduces all predecessor-observable replay and context results for inputs within the predecessor contract.

Plain language: The new candidate must keep the old accepted bytes untouched and still produce the same valid results.

Boundary: It is not semantic equivalence outside the selected contract, successor admission, product approval, cutover eligibility by itself, or permission to delete the predecessor.

## Cutover Rehearsal

- ID: `cal.epoch-002.cutover-rehearsal`
- Disposition: `prototype`
- Definition ref: local prototype

A Cutover Rehearsal is an isolated, reversible exercise that applies the candidate replacement procedure to non-live state, verifies expected projections and rollback, and proves restoration of every selected preimage digest without performing the real cutover.

Plain language: Practice the replacement and prove we can return to the exact starting bytes before deciding whether to do it for real.

Boundary: It is not a migration execution, live cutover, destructive action, product approval, publication, deployment, or external effect.

## Challenge route

Challenge reused meaning through its exact definition owner; challenge local prototype terms through the CyberAlchemy Lab Ontology Lifecycle Project owner. Changed selected source bytes require a successor definition-prototype epoch.

## Claim ceiling

A D65-S1 definition prototype bound to exact current source bytes. Validation may prove source currentness, closed term shape, and hostile rejection only; it does not canonize local prototype terms, approve the product, admit or activate the v2 map, export adapters, authorize cutover, publish, release, deploy, or create an external effect.
