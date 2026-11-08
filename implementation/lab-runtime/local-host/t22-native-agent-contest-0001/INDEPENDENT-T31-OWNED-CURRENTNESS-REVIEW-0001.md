# Independent owned-currentness component review

Read `t31-owned-produced-0001/currentness.py`, `host_headers.py` and
`owned_kernel.py`; independently reran the then-current 14 tests on the selected
durable ABI. All 14 passed in 53.246 seconds. The later fifteenth test and actual
native workflow integration are separate observations, not claimed here.

No blocking defect was found for the documented trusted-host component boundary.
Selection freezes Actor, Source cut, Work, Run and producer receipt bindings.
Resolution reopens the actual committed OutputJournal, checks the independently
selected transaction digest, exact originals and all lineage dimensions, rejects
unheaded/orphan material and later same-carrier revisions, rereads actual private
producer receipt bytes, and repeats guards and committed closure before returning
`owned-produced-current`. It does not label the result admitted or reactivate a
Session. The coordinating Run Actor is checked independently of the original
producer Actor; the latter remains a required producer-lineage guard obligation.

The selected owned kernel preserves original states, carrier sets, roles,
obligations, actual time checks and no-admission/no-Work-completion flags. Its
currentness branch accepts only the exact host-selected HostHeaders class.
Wire-supplied headers cannot choose that profile or provide their own posture.

The remaining boundary is explicit and material: Source/coordination resolver
callbacks must actually validate original schemas, exact Source originals,
Intent/Work/Goal/Coordination relationships and scoped private coordination
semantics. Producer guards must bind actual invocation, request/reply, original
output bytes, producer source/Actor and live permission. The component's receipt
hash equality alone does not establish that a producer ran. Unit fixtures do not
qualify native WorkflowRun transitions.

Revision retirement currently compares identity **and carrier**. That is adequate
for the exercised fixed-carrier transitions. A future profile allowing the same
identity to change carrier/version must specify and test retirement across that
change before claiming general identity-wide latestness. No such migration was
exercised or relied on by this review.
