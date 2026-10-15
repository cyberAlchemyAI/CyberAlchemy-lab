# Live Machine Agent transport

Status: authored candidate; not frozen, executed or qualified.

The trusted host selects an actual live Session resource created by its selected
API implementation. The resource supplies the Agent Instance, Profile,
Assignment, source cut and accountable Principal. Caller strings and persisted
Session metadata cannot create this selection.

One transport peer may be created for each resource. Its Ed25519 key is generated
in RAM and belongs to that Session. A one-use host/connection nonce challenge
authenticates the peer. The resulting trusted context names the real Agent,
Session and Assignment, carries no governing roles, and permits a strict subset
of the parent's read operations with an action budget of zero.

Every use verifies the actual live resource and the parent's current policy and
source checks. The peer expires no later than its Session and parent grant. A
source or permission refusal invalidates the peer. Session disposal explicitly
invalidates the peer and drops its private-key references. No peer can be
recreated for that old resource, and saved metadata cannot rehydrate it.

Memory notes use the existing Session RAM resource. Durable continuity remains
Project State selected through fresh Context and Ontology Views. No key, notes
or RAM snapshot is serialized. Dropping a cryptography key reference is not a
claim that its underlying native memory was independently observed as zeroed.

The parent implementation must explicitly implement
`register_disposal_hook`. The current frozen API34 lacks that hook, so binding
there refuses. Integrating the hook and this factory requires an immutable API
successor and complete actual qualification. Source and channel callbacks are
not replaced.

Required evidence: real Session opening, signed Machine proof, actual API calls
with the bound Actor, spoof/replay/foreign-resource/refused-effect cases,
revocation and expiry, actual RAM-note disposal, private-key reference disposal,
and all inherited API/Session regressions. No public operation is added or
qualified by this authored kernel.

Authority effect: none. Final owner checkpoint remains R08.
