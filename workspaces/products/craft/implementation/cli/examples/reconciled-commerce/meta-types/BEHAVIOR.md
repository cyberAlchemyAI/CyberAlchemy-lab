# Interface, Event, State Machine, Operation and Workflow

These examples invoke generated TypeScript code from the selected
`domainspec.reconciled-typescript/v1-candidate` profile. Run them through the
all-meta-types consumer harness. `behavior.mjs` exports
`runBehavior({generatedRoot, exampleRoot})`; the caller supplies the compiled
JavaScript directory and this installed example directory.

An **Interface** describes the values and members a consumer can use. The
`api` Interface exposes `find`. Its request and result normalizers check values;
`summary` maps an Order and explicitly supplied Calculation results into its
public response. A second `named-boundary-api` Interface carries a public identity,
Money Value Object shape and Choice Enum in both request and result. It checks
finite alternatives and their payloads while keeping invariant execution explicit.
The consumer supplies an adapter and explicitly checks the
requested version before calling it. An unsupported version or malformed request
makes zero adapter calls. A malformed adapter result is rejected after the call.
The generator does not create a transport or execute Value Object invariants
inside Interface shape normalization.

An **Event** records an occurrence. `eventPosted` takes a supplied occurrence
identity, required clock value and payload; `eventReleased` obtains its clock
from an explicitly supplied callback. The witnesses preserve unsigned numeric
Order identities above JavaScript's safe Number range, exact signed payload
integers, and immutable data. They reject missing identities, bad reference
values, overflow and invalid clock results. Constructing an Event does not
register it or deliver it. A separate delivery envelope may carry a separate
message identity; two deliveries can refer to the same occurrence.

A **State Machine** controls legal transitions. `transitionLifecycle` begins
in `draft`, reaches `posted` only when its Rule accepts the supplied amount, and
then can reach `released`. Failed guards and absent transitions return distinct
rejections; invalid state/input is rejected. The transition returns ordered
`confirmation` and `audit` Event intents. Those intents remain data: no Event
construction, persistence or delivery is performed by the reducer.

An **Operation** prepares a guarded action and settles through explicit
dependencies. `operationPerform` takes an Order and posted Event input, checks
its types, guard and owned value invariants, prepares one state write and one
outbox Event, and awaits one atomic commit receipt. This selection declares no
reads; the supplied provider refuses unexpected reads. Input rejection occurs
before starting a transaction. Guard, invariant and Event failures perform no
commits or writes; an opened transaction is rolled back. A returned commit
rejection remains different from a thrown/lost acknowledgement, which is
indeterminate. The runtime does not automatically retry an uncertain commit.

The supplied example provider commits state and outbox together in memory. The
failpoint between draft preparation and publication leaves both unchanged. This
is a consumer implementation of the declared transaction port; it demonstrates
the generated protocol without claiming disk durability, crash recovery or
remote effects. Separate AlchLang source tests exercise its existing SQLite
state/outbox implementation and rollback failpoint.

A **Workflow** coordinates Operations. `workflowFlow` awaits `first`, `second`,
`third` and `last` in order, passing each normalized result to the next step.
A supplied Mapping normalizes the input Order, and another Mapping projects the
final result. Separate captured results with identities 61 and 62 demonstrate that
the next step reads the preceding result rather than substituting initial input;
missing and misordered result prefixes reject. Numeric Event reference values
survive capture and materialization. A known
rejection stops immediately and returns the selected compensation plan for the
completed prefix. The example consumer then explicitly executes generated
`operationUndo` calls using those supplied arguments and order; the Workflow
itself does not dispatch compensation. Uncertain commits require reconciliation
and return no compensation bindings, even if the provider actually wrote data.
This is bounded orchestration; the separate durable recovery successor remains
separate.

`runLegacyPermission({alchModule})` additionally accepts the namespace of the
exact installed AlchLang core package. It checks a permitted action succeeds
once, while a permission for another action, a failed guard, wrong actor,
mismatched authority boundary, failed permission condition and missing grant
make zero adapter calls and effects. This uses the public package exports only.

## Open Questions

Exact installed-package qualification and its immutable receipts are owned by
the all-meta-types integration harness and the completion plan's execution
status. Other language profiles require their own native witnesses. Public
publication, durable recovery acceptance, local hosting, TDE and EVF are outside
these example claims.
