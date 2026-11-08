# Private owned workflow profile through the common Service

The public `workflow.transition` request/receipt schemas and dispatch count stay
unchanged. The original `WorkflowTransition` and strict kernel stay unchanged.
A new separately selected handler supports the existing private owned profile.

1. Add `owned_workflow_transition.py` to the new API cut and its code/source
   closure. A trusted bootstrap registers one selection on an actual selected
   Service/ReaderChannel after authentication. API message fields cannot create
   or select a profile. No registration means the existing strict path.
2. Retain actual `workflow_control`, `workflow_source_control`, scope material,
   current grant, Source period and nonce checks. A new private routing row
   selects a private runtime-profile binding. Its kernel binding identifies the
   exact owned or scoped-owned kernel; its journal binding still identifies the
   original immutable output journal. Auth accepts current-Legacy transition
   metadata only through this exact validator, retaining ordinary strict routes.
3. The registered selection binds the actual host/channel/Vault/Source cut,
   policy SHA, store root/config, typed kernel, and four private host adapters:
   exact headers, full original semantic records, existing producer outputs,
   and live guard. Each callable's file hash and entrypoint is independently
   bound in the private profile and checked before every operation. This is a
   trusted local host boundary, not remote attestation or arbitrary wire code.
4. The handler independently validates original record schemas and bytes for
   Intent/Resolution/Work/Coordination/Goal/Decision/Effects and the exact
   Decision→Resolution and Goal→Project relationships. Header-provider success
   alone does not establish these semantics. Private records retain their owned
   posture; none become Source-current.
5. Before outer Vault claim, compute the owned kernel plan from exact selected
   original materials, actual Actor/cut/UTC/grant, complete named obligations
   and trusted producer originals. Required output carriers are attached using
   original schemas and scope contracts. No producer is dispatched by a message.
6. Apply uses the selected durable OutputJournal, preserving original output
   bytes before inner claim and checking them at every guard. Keep the common
   Service's outer allocation/wire/claim/result lifecycle and exact retry. Build
   the original receipt from the actual committed transaction and cold replay.
   Pending work is never redispatched after interruption.

Scoped variants additionally verify exact native container/body/authority scope
correspondence through the new scoped store/header/kernel. Original headers and
bodies remain unchanged. The ordinary owned variant keeps Project-scope equality.

Service delta: its workflow selector first consults the installed typed private
selection, then falls back to the existing selector. Include the new handler in
`code_files` and report the actual selected handler binding in transport evidence.
There is no broadening of `K.CURRENT`, no public profile switch, and no admission.

Required causal tests: no registered selection; wrong host/channel/Actor/cut;
changed private control, callback origin or producer original; mismatched
Work/Goal/Decision/Effect/edge; stale owned revision; unheaded output; expiry or
revocation between preflight and inner HEAD; actual common-Service output-bearing
positive and exact retry; separate cold output read. Pure fixture tests must say
which grant/callbacks are synthetic. Final qualification requires the real selected
API, current Reader and physical source/producer paths.
