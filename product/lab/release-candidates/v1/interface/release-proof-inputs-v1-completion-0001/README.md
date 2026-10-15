# T08 protected proof inputs and semantic graph component

This is a new candidate component. It changes no original v1 API reader, graph,
Vault or privacy scanner. Focused actual tests qualify its owned technical
fixtures only. Production API17 integration, current original source/permission
checks and complete final graph profiles remain the coordinator's work.

Checkpoint1: `ProtectedReader(selector_raw, grant_raw, CustodyAnchor(...))`.
The independently authenticated private selection supplies the anchor's
principal/key, exact API source/profile, actual public source cut, operation,
selector/grant byte bindings and private file locators. A request cannot supply
that anchor. The Ed25519 custody grant selects exact input bytes and read scope;
it supplies no Artifact admission, owner role or release approval.

The closed selector lists every exact allowed root and file with kind, logical
identity, relative no-follow path, SHA256, size, mode, uid, device and inode.
Root/file/ancestor attachment is rechecked. Selector/grant controls are0600 in
an independently owned0700 root; state revocation/control mutation invalidates
each read. Source/profile `/files` tables are mandatory, with exact complete
ordered coverage. Composite environment tables use the actual original keys
`complete_source_bindings`, `complete_profile_bindings`, and
`schema_execution_bindings`; none can be silently omitted. Verification streams
all selected file bytes afresh. The separate protected JSON parser is bounded
at64MiB; the ordinary1MiB Vault/frame limits are unchanged. Larger files can be
stream-hashed but cannot be parsed by this reader. No input is public-exportable
by virtue of its binding kind.

`verify()` is the fresh full boundary guard; `read(file_id, expected_kind)`
additionally rechecks current controls/state/time and the exact original file.
`boundary()` verifies the full closure on entry and exit, including exceptions.
At actual effects the host must still repeat its original signed source,
Actor/Agent, schema, current policy/revocation and deadline guards before claim,
before publication and after effect. This component neither replaces nor
patches those callbacks. The host must ensure the current controls were selected
independently, including actual root/locator metadata; a self-signed untrusted
selector is not a transport grant.

Checkpoint2: `verify_graph(reader, policy_file_id, declared_edges, root_refs)`.
The semantic policy itself is an independently pinned selected file. It selects
exact original schema and descriptor bytes per carrier, explicit declared
reference-field classifications, nodes, proof references and current context
references. Record validation uses the closed local schema registry and original
descriptor `relation_roles` including pair/kind/direction. Reference-field name
matching only checks classification coverage; it never decides semantic edges.
Schema-selected `semantic-node` fields and actual typed relations generate edges;
all other selected proof inputs are separately byte-verified. No recursive
traversal of arbitrary naked `{path/ref,sha256}` objects occurs. Historical
proof-only cycles/annotations are not declared Artifact graph edges. True semantic
cycles, missing/duplicate edges/nodes, unsupported schemas/identities and kind
spoofing are refused.

The current original-descriptor profile supports full canonical descriptors with
`schema_digest`, `classification.semantic_kind`, `instance_contract.identity_field
= node_id` and `relation_roles`. Native registered-item/fragment descriptors are
not relabeled to that shape. A separately versioned legitimate selector/origin
adapter is needed before that native form can be consumed. The coordinator must
independently ground every per-carrier field disposition and exact eligible
version/identity/source mapping. Schema validity/identity names do not establish
current admission, governing roles or final package readiness. Unsupported or
unresolved field meaning stays a refusal, not a generic wrapper.

The owned qualification creates an ephemeral Ed25519 key in memory, real files
and real clocks in test-owned roots. Its24,497-row table exceeds27MiB and is
explicitly a technical size fixture with opaque cycle annotations, not genuine
source-history evidence. Every owned scratch root is removed. The original
GovernedModel/v1 public schema and descriptor are copied byte-identically into
those owned inputs. No live private policy, key, native host, database or store
is read by the qualifier. Actual source/profile/host closure for API17 is not
qualified by that fixture result.

See `CONTRIBUTION.json` and the T08 run for exact pins, command/OS-exit receipts,
tests, integration hooks and remaining production constraints.
