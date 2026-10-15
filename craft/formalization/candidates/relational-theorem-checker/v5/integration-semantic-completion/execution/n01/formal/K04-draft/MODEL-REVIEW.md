K04 applies-lesson: candidate model and implementation review

This package implements the currently proposed K04 meaning for review. The owner
assessment is still pending. It changes neither that proposal nor its assessment
request, the plan, the 263-obligation inventory, or any accepted earlier assessment.
Its nine K04 inherited IDs remain open. This package is separately verified and is
not registered in the existing main preparation index or its declaration count.

LessonUseCandidate.lean defines a finite typed world independently of its checker.
Exact revision references carry an identifier and revision. Applications, assessments,
disposition records and relevant conflicts/overrides must agree on the exact session,
owner, scope, snapshot and epoch. The lesson, posture, assessment and precedence
qualifiers must join the selected records exactly. Captured world membership supplies
record evidence; a posture label alone cannot supply the missing disposition record.

Four postures are distinct: selected, presented, used and declined. Only the final
two qualify. Both require a captured matching disposition with a nonempty basis and
an exact applicability assessment with a nonempty basis. These are synthetic typed
records. The model does not authenticate the recorder, establish the external truth
of actual use, or treat a nonempty string as a completed real-world assessment.

Precedence is an explicit finite candidate profile: an owner/scope policy has a
validity interval and unique instruction-to-rank assignments. Every relevant conflict
must name the disposition's governing instruction as winner, have captured owned
instructions on both sides, and satisfy strictly greater winner rank. Arbitrary list
order does not establish priority. Ranks are already interpreted values; mapping an
original policy token to this interpretation remains missing and requires owned
evidence. A general precedence partial order and multiple governing instructions are
outside this profile. D03/D04 have not been accepted globally.

Every conflict and override in the captured world for this exact application/frame
must be retained in the application. Every retained reference must resolve back to
such a record. An override additionally needs a nonempty basis and an exact retained
conflict supporting its governing instruction. Empty lists qualify only when the
captured world has no relevant records. Completeness and authentication of that
world are external requirements: this model cannot discover omitted real conflicts.

The executable checker and six grouped diagnostics are proved equivalent to the
independent meaning. A successful qualified recording therefore requires that meaning.
Recording appends an exact claim, leaves identical retries unchanged, and refuses
different content at the same revision. Its general preservation theorem keeps
authority roots, ownership, identity classes, admissions and runtime state unchanged.
This is a local ledger result; it does not prove whole-system rule closure or actual
runtime integration. An existing ledger still needs an owned consistency contract.

LessonUseControls.lean supplies kernel-checked actual-use and deliberate-non-use
witnesses with a conflict and override. Refusal controls cover selection, presentation,
missing disposition or assessment, stale revision/snapshot, mismatched qualifier joins,
expired/future policy, wrong owner, absent or duplicate ranks, lower-priority winner,
lost or invented conflict/override records, missing override basis and absent governing
instruction. Recording controls cover exact append, retry and conflicting revision.
These are synthetic models and targeted controls, not all raw schema branches.

The source shapes still require a separate adapter. Lesson Application stores seven
payload fields: lesson revision, session, posture, assessment, intended influence,
conflicts and overrides. It does not store instruction_precedence; that relation
qualifier must resolve an independently owned policy. Operational Lesson's remaining
applicability, exclusion, evidence, expiry and status fields are not decoded here.
Complete closed-object decoding, original tokens, body bytes/digests, evidence policy,
lifecycle and schema admission remain separate obligations. Neither of the two source
schemas makes a nonempty posture or assessment token sufficient semantic evidence.

Formalization-first completion sequence for this relation:

1. Obtain the existing K04 meaning assessment, preserving the user's one-at-a-time
   review. Resolve its proposed use/non-use scope and the applicable D03/D04 policies.
2. Specify owned posture, assessment and precedence providers, frame/catalog
   consistency and completeness, evidence admission, temporal interpretation and
   the general precedence domain. Revise this candidate if those meanings differ.
3. Prove complete original-source refinement for the sole declared endpoint pair,
   including both full body schemas, exact four qualifier interpretations and
   all policy joins. Missing mappings must return unknown/unsupported.
4. Prove the exact record effect and complete-theory countermodels for compliance,
   measured benefit, authority and method employment. The local preservation
   theorem above does not discharge those four non-entailment claims.
5. Integrate owned catalogs, public APIs and diagnostics under N02/N03 dependencies;
   perform the required independent checking and composed extension validation.
6. Attach exact evidence to each of the nine inherited IDs only after the full
   obligation is established. N01 and the complete plan retain their other gates.

verify_candidate.py binds the current source proposal and schemas, pending assessment,
protected review/plan state, original closure, toolchain, model and controls. It
compiles both modules in two fresh directories, verifies import locations and inspects
every theorem's axioms. Same-toolchain replay is not independent checking. The
machine-readable result is verification.json; the two axiom logs retain exact output.
