# Session opening scope successor

The original 70-second expiry tests failed in API50. A retained API53 profile
confirms that repeated original file checks dominate execution; profiling adds
overhead and does not qualify normal latency. All 293 inherited method ASTs and
34 public contracts remain unchanged in this successor.

Pre-claim eligibility retains its full original scope. After the durable claim,
eligibility, exact original delivery verification, classification, Agent/Session
descriptors and connection metadata share one synchronous pure source read scope.
The exact delivery consumed by eligibility is reused within that calculation.
Profile resolution uses its sealed copy. Original source/eligibility/channel
callbacks and the scope registry are unchanged. Every policy call rereads the
actual private policy, revocation and real clock. Full original source/package
exit checks precede live resource creation and journal writes outside the scope.

Short memory still belongs only to the live Session and is erased on disposal.
The original timer and absolute Assignment/deadline limits are retained. A final
real-clock check follows reply verification so an expired operation returns an
indeterminate outcome available through operation.inspect. Recorded exact retries
continue to return operation evidence without recreating a live resource.

Qualification requires this successor's own original expiry tests, affected
Session journeys, package import and full API regression. Authoring and static
AST retention alone do not qualify runtime latency, admit this implementation,
complete the plan or authorize activation. Nineteen handlers are authored and
fifteen original operations remain unimplemented.
