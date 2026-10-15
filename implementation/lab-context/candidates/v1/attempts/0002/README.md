# Exact context generator candidate

C08 extension to the verified Session consumer. Source files, immutable generator
manifests, candidate carrier bodies and observed test evidence are separate records.
All new carriers remain candidate-unadmitted; R08 is the owner review checkpoint.

## Inputs and outputs

`ContextSession` requires a pinned `VerifiedLegacyReadStore`, an independently
pinned C04 source snapshot, a `NativeReadStore` with externally supplied event,
request, binary and projection pins, and an independently selected generator
manifest and Implementation revision. Required current Principal, Context,
Project and Product Capability references must resolve by exact source revision.
Optional Agent Assignment/Profile/Delegation/Implementation references retain the
existing reference diagnostics; none grants execution permission.

Outputs are actual schema-validated candidate Context Request, Context View,
Ontology, Ontology Cut, Ontology View, Implementation and Typed Relation records.
The separate realization relation uses the existing ordered
Implementation-to-Product-Capability pair and its declared qualifier contract.
The generated Implementation has its own stable identity and candidate revision,
distinct from package version, executable manifest digest and related historical
Implementation records. No capability adoption or usefulness is claimed.

Every returned pack separates resolved governed source references, coeval
candidate references, byte-bound schema labels, verified native subject identities
and protocol Session/environment/policy/route references. A schema label bound
through an admitted carrier is not a separately admitted Schema artifact.

## Native ontology boundary

The small Rust bridge calls the existing `EventStore::load`, `ontology_at`,
`context_projection` and `governed_node_view`. It verifies actual semantic and
governance event chains and exact joins. The selected governance cursor is the
complete independently pinned governance prefix; the library's context selector
does not offer an independent historical governance cursor. Project history
cursors retain their own namespace and never supply an ontology cut.

The underlying library currently supports only its closed empty typed-property
profile and `test-complete-profile/v1` projection. The fixture contains two native
nodes and one native relation; these represent no domain Artifact instance.
O02 owns broader domain mappings and profile support; O03 owns ontology admission.
The Ontology carrier describes this bounded native read scope explicitly.

`NativeReadStore` verifies original bytes, copies them into an isolated read
snapshot, runs the pinned native executable, validates the independently pinned
projection and rechecks original event and executable bytes. The adapter exposes
no append, sealing, store mutation or activation interface. The native binary's
`seal-fixture` mode is a pure serialization helper for isolated verification;
it writes no store and grants no authority.

## Session lifecycle

Every consumption revalidates generator source/manifest/environment, source
snapshot, committed HEAD, configuration, Project State, native event closure and
projection. Drift or TTL expiry closes the Session and erases its short memory.
Short memory is bounded by the existing Session rules and excluded from every
carrier, returned context and fresh-process input. A later Session starts empty.
The consumer has no signing, dispatch, application, persistence or admission
methods. Exporting an observed fixture is a verifier operation, not Agent memory.

## Isolated verification

Build the native bridge with Cargo offline into a task-owned temporary build
directory. `build_package.py <native-executable>` stages a fresh numbered immutable
generator manifest. `verify_context.py <native-executable> <manifest>` runs the
candidate checks and all 13 existing Session guards, with a 480-second controller
budget, terminal logs and immutable numbered receipts. Fresh-process context
reconstruction and native replay are observed. Binary hashes bind the exact
observed build; reproducible builds or deployment are not claimed.

C09 integrates API dispatch and stronger artifact-reference handling. This package
does not activate the runtime, admit any candidate, or close those later criteria.
