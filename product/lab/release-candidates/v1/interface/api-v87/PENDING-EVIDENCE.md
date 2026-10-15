# Pending validation evidence

Incomplete stable-core validation retains native verification evidence after the
original source scope exits successfully. API57 binds classification preparation
v9 and records those exact committed evidence bindings in a private observation
file associated with the original operation claim hash and authenticated principal.

The observation has no domain result, completion state or authority effect.
`operation.inspect` verifies the pending claim and exact evidence bytes and returns
the original call binding followed by the native verification bindings. It keeps
`posture: indeterminate`, `result_binding: null`, `reconciliation_required: true`
and `retry_allowed: false`. Exact retry continues to return `recovery-required`.

Observation writes require a current owned pending claim, bounded closed bindings,
existing exact objects and no replacement. Inspection verifies private file modes,
claim identity and object hashes. A missing observation remains inspectable as a
pending claim without evidence. A corrupted observation is refused. An interrupted
observation write cannot create an operation result or permission to redispatch.

All 293 inherited test methods and all 34 original operation contracts remain.
The separate qualification retains the 16 prior classification cases and adds
one case for inspection, unchanged pending state, exact retry and tamper refusal.
No predecessor qualification transfers to this successor. Nineteen handlers are
authored; fifteen operations and full plan completion remain outstanding.
