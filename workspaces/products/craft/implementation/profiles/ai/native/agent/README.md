# Optional bounded business agent

`index.mjs` exports `createBusinessAgentRuntime` and `agent-run-port/v1`. The
existing ARE coding loop now delegates iteration to `runBoundedAgentLoop`;
`runBusinessAgentTask` consumes that same helper with a business event adapter.
Coding repository snapshots, patch candidates and tools remain in the original
coding adapter. The business path does not wrap the unchanged patch loop and
does not own another adaptive loop, provider client, queue or session journal.

**Reuse:** original ARE bounded iteration/event parser/session lock+ledger+
checkpoint owner, existing Core generated read-only Query codecs/Auth, M00
inference and R04 child exposure, R02 source-owned single-use releases.
**Extend:** closed local custody and one original-session mapping between tenant,
start key, immutable intent, realization, workflow, local run and checkpoint.
**Configure:** trusted generated tool/context owners and authored egress policies.
**Unverified:** live provider/model/harness/account qualification and external
managed-harness continuations. This realization is the local ARE business loop.

The host injects `{session,inference,exposure,sourceRelease,contextOwner,
toolBroker,tools,resultCodec,assertCurrent,resource,observer?,now?}`. The session
is the existing original durable ARE session or existing workflow-owned adapter
with `record` and ordered `snapshot`. `openPersistentBusinessSession` reuses the
same ARE ledger/lock/checkpoint implementation as `openPersistentCodingSession`.
No new agent SQLite ledger exists. The native module imports the public ARE
`business-agent-task` subpath; the host supplies the original session so private
context-engine dependencies need not leak into native execution.

`tools` is a finite trusted list `{name,readonly:true,argumentSchema,
decodeArguments,resultSchema,decodeResult}` from original generated Query
bindings. `toolBroker.assertCurrent(name,binding)` and `invoke(name,argsWire,
{signal,runId,fence})` retain actual Entry/Auth/delegation/tenant checks. No shell,
SQL, arbitrary HTTP, mutation or caller-selected credential/tenant arguments are
admitted. A tool's content is data, never instructions or new authority.

`contextOwner.capture(startContext)` returns an original opaque full manifest;
`extend({runId,manifestId,toolName,result})` appends authoritative Query dependencies
while retaining prior inputs, including uncited material. `assertCurrent(binding)`
checks current original source/grant custody. Model citations cannot prune the
manifest. Source policy must allow action `agent.release` for exact selected
`agent-session`, `agent-result`, `agent-export` sinks and recipients. Every
tool-result checkpoint, next model input, final result and payload export checks
original release. Revoke after a tool result blocks the next disclosure/resume.
Already released bytes cannot be recalled.

Resource identity is `{id,tenant,application,billingAccount,realization,workflowId,
mode,maxInputBytes?,maxOutputBytes?,maxCheckpointBytes?,modelDeadlineMs?}`. Mode
is constructor-selected fixture/provider identity. `inspect()` provides stable
redacted runtime identity; `capabilityManifest()` explicitly declares local
inspect, read-only tools, local cancel and resume from safe local checkpoints.
Remote inspect/cancel/resume are false.

`start({startKey,goal,input,context,limits})` binds complete immutable intent and
stores it before dispatch. Matching duplicate starts return the same run; changed
intent conflicts. Limits cover lifetime model/tool attempts, tokens, optional
maximum money and absolute deadline. One R04 run envelope aggregates unique
M00 child reservations without another debit. `run({runId,signal?,
maxStepsThisCall?})` persists fenced start intent before any I/O. Ordered snapshots
include lifetime counts; limits survive restart and cannot be reset by resume.

`resume` admits only `waiting` with a complete safe checkpoint and no pending
model/tool call. Recovered running/start/model/tool intent is `unknown`, retains
paid exposure, and requires original inspection/review; no blind relaunch exists.
`cancel({runId,tenant})` durably stops future local dispatch even while awaiting a
model or tool. Late results append redacted evidence and cannot revive terminal
local states. Harness observation and local custody state are separate.
`LOCAL_TRANSITIONS` is the exact closed transition table; unlisted transitions
reject. A failed pre-dispatch source check from waiting enters review.

`inspectRun({runId,tenant})` returns redacted recorded facts and accounting
references. `exportPayload({runId,tenant,recipient})` separately checks source
policy for its exact bytes/recipient. Session raw history must never be exposed
through an application endpoint; run access alone does not authorize payloads.
Completion means a checked typed proposal, not business approval/posting.

The reusable `createCapabilityResource({controller,bindInvocation,capabilities?})`
binds the original generated native-resource ABI. It uses `exportProposal` to
release only the completed typed proposal under `agent-result`; it requires no
raw-history `agent-export` grant. The optional async `contextOwner.checkRelease`
is awaited for original Query grant reauthorization before model/tool/final
disclosures, resume and exports. Callers should await export methods when this
actual generated Auth hook is configured.

Setup, source retention and credentials remain original-owner responsibilities.
Backups/migrations preserve original session and M00/source/R04 databases together.
Schema/tool/profile changes require compatible checkpoint selection; incompatible
authority/version drift stops continuation without resetting limits. No remote
start, stored provider conversation, synchronizer, credential mirror or provider
fallback is introduced. Retiring this realization preserves old journal/source
and account inspection needed for unknown effects. No automatic deletion exists.

## Open Questions

Actual provider quality and remote managed-harness guarantees are unrun. The
isolated G02 example and final root packaging own clean-consumer generated Query,
Rule, API/graph/bridge and exact built-byte integration. Native tests exercise the
actual original persistent session and real SQLite/codec/accounting mechanisms;
their Query broker is labelled fixture code until that generated example join.
