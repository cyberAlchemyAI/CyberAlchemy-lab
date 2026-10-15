# Selected environment context and read consumer custody

Status: candidate foundation for R03. No API operation is added by this package.

## Actual continuity

The successor generator uses the exact R02 Python dependency environment and the
same immutable C12 signed branch. Its generated Implementation revision is
`implementation:lab-committed-context-generator@candidate.2`. Original generator
code, environment contracts, records, signatures and receipts remain evidence.
ContextSession fully replays signed Project State, binds original transaction
bytes separately from reconstructed records, and calls the actual Rust native
ontology reader with an independently pinned semantic and governance event cut.
The native fixture has two nodes and one edge; it establishes integration, not
the complete Lab domain ontology.

## Ephemeral read consumers

ReadCustodian wraps actual ContextSession objects. Each new consumer gets a new
Machine instance and Session identity, fresh context, and empty bounded RAM.
These consumers are unassigned, have no action permission, and cannot be treated
as active operational Agent Sessions. The old assignment is never selected as
permission for a new instance. Operational assignment, capability, authority
envelope and transport integration remain R03 obligations.

The trusted development caller selects the principal, Project, source cut,
consumer control and factory before constructing the custodian. Public JSON or
context contents cannot grant permission. A hash is an exact input binding,
not authority. The development authorization permits these owned read fixtures.

## Metadata and disposal

The process owns one exclusive flock on its private `/tmp` custody root.
Allocations precede creation; immutable metadata revisions chain original file
hashes. Metadata includes identifiers, exact source bindings, context digest,
observed times, posture and disposal observation. It contains no context pack,
private credentials, notes, hashes of notes, or restored Session memory.
Notes belong only to the current consumer's RAM and never enter inspection or
durable metadata. Project State and Context/Ontology Views supply continuity.

Closing validates the caller and exact metadata binding, then disposes memory
without requiring source freshness. Expired or invalidated sources also dispose
owned RAM. Cleanup attempts actual disposal even if metadata is corrupt; failure
to retain a receipt remains an evidence gap. A source invalidation is reported
as indeterminate rather than a successful work/action result. No action is
executed and no unresolved action can be resolved by closing this reader.

## Interruption and claim limits

An allocated consumer without completion metadata cannot be redispatched. A cold
process may inspect retained metadata but never recreate a consumer or assert
disposal based on absence. Former active metadata is indeterminate until external
reconciliation; this package does not supply that reconciliation. A verified
close receipt remains inspectable. A fresh key creates a fresh identity.

This custody journal is a development metadata protocol, distinct from API JCS
idempotency, canonical artifact transactions, ontology event authority, and
session.close's final integrated contract. Whole-root loss, hostile concurrent
writers and power loss need external custody/reconciliation and final release
validation. Fsync and cooperative locking alone do not prove those cases.

## Final review members

1. Successor generator source and environment contract.
2. Candidate generator Implementation and realization relation.
3. Read consumer custody protocol and source.
4. Exact validation evidence and native fixture limitations.

Each remains independently reviewable in S02/R08. No owner outcome is recorded.
