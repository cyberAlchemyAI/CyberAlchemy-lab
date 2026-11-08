# Evidence eligibility and original acceptance

This unit implements C08. It provides integrity and eligibility checks over
independently selected inputs, not authenticity of human or runtime observations.
It changes no original task status, source, role, private input or live store.

## Selected inputs and retained occurrences

`original-inventory-selection.json` selects all36 completion contracts, the46
phase contracts, the40 underlying original contracts, the36/73 completion DAG,
36 completion SWUs,63 inherited SWUs (including the57 underlying SWUs), and all13
AC sections. `inventory.build(reader, expected_selection_binding)` verifies the
crosswalk joins, complete body membership and every original edge. Each body
remains available as exact original bytes, including whitespace and legacy JSON
numbers. No old document is rewritten through the new codec.

Every Markdown paragraph and individual list row has an original byte-span selector. Known nested SWU Parent/Dependencies/Source rows are context; write/ordered/done/negative/review/handoff rows remain criteria. Acceptance/done,
ordered rules, validation, scope, authority gates, failure and synchronization
sections are separate criterion occurrences. Unrecognized sections remain gated
occurrences. JSON acceptance/done/ordered-rule arrays remain separately identified
in completion, inherited, phase and original manifests. Repeated text is not
deduplicated. The110 DAG acceptance-evidence labels are not the entire criterion
set. Source digest plus exact selector defines occurrence identity.

## Trust and review boundaries

Callers must use `AnchoredReader` with independently retained root identities and
literal expected selection/policy/context hashes. A case author must not supply
all of these as its own authority. The coordinator verifies exact interpreter,
module/dependency closure, regular-file cache-prefix sentinel and sanitized
`python3.14 -B -S` launch before candidate imports. There is no hostile-same-UID
or privileged-host authenticity claim.

`eligibility.evaluate(reader, inventory_binding, policy_binding, context_binding)`
loads the original inventory itself. A closed policy must account for every
occurrence and each mapped owner, in original order. Every criterion has a required owner, independently source-bound task contribution,
explicit unresolved interpretation, or permitted source-bound downstream deferral.
A contribution points to exact original task-body criteria; it never substitutes
for the complete candidate condition or later operational obligation. It cannot
be relabeled context. Unknown interpretations stay gated. Test policies explicitly
describe synthetic inert proofs; they do not qualify any original native task.

The selected context enrolls exact original review bytes, reviewer identity,
author identity and evidence-core digest. Merely using unequal identity strings
does not establish independence. Enrolled reviewers/providers must actually
verify the original command, terminal, state, timing and underlying observations
within permitted custody; a wrapper or hash alone never qualifies a native gate.
Native receipt authenticity and actual permissions remain external prerequisites.

The acyclic order is command/terminal/original observations → EvidenceCore →
review → EvidenceRecord → independently selected context. EvidenceCore excludes
only the later `review_binding`. PolicyCore similarly excludes only its later
interpretation-review binding. The external context selects the actual expected
review identities and original review bytes, so neither record can self-enroll.

The index validates exact selection, task, criterion/AC scope, subject/input role,
attempt, case, stage, command, terminal, timing and review joins. Original native
observations are exact bound originals retained alongside the reviewed closed
receipts. Process PASS requires observed exit0, known cleanup/effect state and accepted
independent review. Human/native observations use closed non-process terminals
with null argv/OS exit; no fabricated process success is required. Selected
required stage/terminal pairs are conjunctive. A genuine signed reject/defer/stop
may prove a received disposition while leaving later effects ineligible. Static/inert evidence cannot claim observed external effects. Negative,
malformed, unknown and incomplete originals remain visible; they do not become
positive support. A scoped negative and a PASS for the same selected criterion
remain conflicted. Known FAIL/ERROR, rejected review or observed nonzero process
exit produces FAIL; NOT_RUN/BLOCKED/UNKNOWN, incomplete review, missing process
terminal/timing, or unknown cleanup/effects remains INCOMPLETE and PENDING. A
same-scope incomplete observation still blocks a later PASS; known failure takes
precedence. There is no implicit latest-wins reconciliation.

## Historical and current views

`history.historical` is a separate explicitly selected adapter. T00 retains its
baseline-only acceptance and no runtime test. T01 retains causal diagnosis and
the unavailable OS exit handle; it supplies no seven-read successor qualification.
T04 retains its31 focused checks/exit0, with zero live API calls and pending final
API qualification. Historical acceptance never enters the current evaluator as
an automatic PASS.

Current task eligibility requires every applicable criterion and all73 original
predecessor edges. T24's source-authorized final AC05/13 and admitted-operation
deferrals satisfy only its local disposition requirement. Their AC clauses stay
pending globally. Only exact downstream same-occurrence support and that task's
complete eligibility discharge a global deferral. Arbitrary original done
criteria cannot be sent to another task. Candidate T24 acceptance never by itself
means all13 conditions are globally complete. The selected acceptance-phase
policy exhaustively partitions every AC owner: candidate closure is T24, with
final package AC05/AC13 at T25; T26–T30 are separately tracked later contributors.
T31–T35 remain candidate support despite their numeric IDs. Each AC exposes
candidate_status, later_operational_status and combined status. Missing evidence
is PENDING, an applicable selected negative propagates FAIL through contributions
and upstream tasks, and an absent later obligation is NOT_APPLICABLE.
A rejected owner route cannot close T27–T30 effect tasks. No status grants effect
authority.

For T27–T30, exact-final-bundle identifies initial T25 ancestry only.
current-effect-scope identifies the selected current target. The independently
enrolled current-authority-review must verify current permission/target scope
and its reviewed relationship to that initial bundle; if original records
separate these facts, retain their exact bindings within the reviewed evidence.
A later T30 semantic target can differ from the initial bundle. A closed task_subject_bindings map may select distinct current scope/review
pairs for T27–T30; it cannot override global source/family/profile or initial
ancestry. Adding a later reviewed pair may preserve earlier records byte-for-byte
under the unchanged source/cut selection; cross-task target or review substitution
refuses. The index never
creates permission, treats lineage as permission, or assumes byte equality.

## Invalidation and retention

`invalidation.invalidate` compares exact subject selections, follows selected and
dynamic consumers, includes all73 task edges and complete task→AC dependencies,
and requires all13 identified AC nodes. Missing consumer coverage is refused;
explicit unknown mappings invalidate all affected aggregate/evidence/task/AC
claims conservatively. An unaffected candidate is not automatically reusable:
an independently selected unchanged-input proof is still required. History is
never mutated.

Readability does not authorize public retention. Current contexts and historical
selections explicitly select exact `public_retention_bindings`. The enclosing
closed public selector is retained through its externally supplied binding; it
does not contain its own digest. No arbitrary malformed read gets this exception.
`persist(evaluation, owned_root, reader=..., expected_disclosure=...)` independently
rechecks this closed selection and recomputes the projection from independently
supplied inventory/policy/disclosure inputs (or the historical selector). It
compares the entire projection and original set, then exports only recomputed
bytes. Constructed or nested-mutated Evaluation objects cannot export unselected
projection payloads. These input pins must come from the host selection, never
from an untrusted Evaluation. It retains exact originals using exclusive no-follow file creation and fsync in an
initially empty, identity-bound owned root. Partial retention remains visible;
nothing is overwritten or rollback-deleted. Per-document reads are bounded to
16MiB, with a policy-only32MiB bound for the measured complete native policy;
capture/retention to8192 records and64MiB, projection to16MiB. Oversized declared
policy inputs refuse before body reads. Protected-input
bindings are refused; only explicitly reviewed public receipt bytes may export.

## Execution and remaining scope

Run the selected tests through the accepted `tools/run_case.py` with a coordinator
endorsement and exact source closure. The runner's `predecessor_acceptance_binding`
remains its accepted U01-01 baseline-origin anchor. The current unit dependency
(accepted U01-02) is separately bound in the source closure and coordinator start
record; the coordinator verifies manifest dependency acceptance before dispatch.

This unit supplies the mechanism, all7,301 original occurrences and a complete
source-bound native policy with25,133 owner dispositions. The policy core receives
a separate actual independent technical interpretation review before its wrapper
and context are selected. That review does not accept original tasks. Genuine
runtime/human/owner evidence and final clause-by-clause original acceptance remain
external selected review obligations. No unresolved native interpretation
is satisfied by the synthetic evaluator tests or by historical status.
