K04 — applies-lesson

K03 affects has been accepted by the semantic owner. This packet asks about
K04 only. Its single endpoint pair is Lesson Application → Operational Lesson.

The relation answers: which exact lesson revision was used, or deliberately
not used, by this application? Despite the name, deliberate non-use is an
explicit supported posture. Selection and presentation remain distinct and
cannot by themselves establish this relation.

Four qualifiers determine the meaning:

- lesson_revision_ref selects the exact lesson revision and must match the target.
- application_posture distinguishes actual use from deliberate non-use; a label
  must be supported by the application record and its evidence policy.
- applicability_assessment_ref identifies the assessment for this exact lesson,
  application and session/frame.
- instruction_precedence identifies an owned versioned policy that resolves
  relevant instruction ordering. Conflicts and overrides must remain recorded.

Example: lesson L@2 suggests a procedure. In session S, application A records
a deliberate decision not to use L@2 because a higher-priority instruction
governs. It retains its applicability assessment and conflict/override basis.
A applies-lesson L@2 records that exact disposition; it does not claim that
the session complied with every instruction or produced a measured benefit.
Merely displaying L@2 in the session is insufficient.

Recording the qualified relation appends an exact witnessed record, retains an
identical retry, and refuses conflicting content at the same revision. It does
not grant authority, execute a method, or establish compliance or benefit.
Those conclusions may coexist when separately evidenced.

The formal target is:

    AppliesLesson(A, L, frame) implies
      ExactLessonAndSession(A, L, frame) AND
      SupportedUseOrDeliberateNonUse(A, L, frame) AND
      ExactApplicabilityAssessment(A, L, frame) AND
      OwnedPrecedenceWithRetainedConflictBasis(A, frame).

This is a target to prove, not a completed theorem. Four separate non-entailment
proofs must show that the relation alone does not establish compliance, benefit,
authority or method use under the complete pinned theory. Nine inherited IDs
remain pending: four qualifier meanings, one record effect and four excluded
inferences.

The existing Lesson Application schema stores lesson revision, session, posture,
assessment, intended influence, conflict references and override references.
Posture and assessment are nonempty strings, and conflict/override arrays may
be empty. Operational Lesson stores applicability, exclusions, predicted benefit,
evidence, counterevidence, expiry and status. Shape validity cannot prove actual
use, a completed assessment, a resolved instruction conflict or measured benefit.
Instruction precedence is a relation qualifier; the application payload does not
itself contain an instruction_precedence field. The adapter must join and check
that policy against the exact application and its retained conflict/override basis.

Implementation begins with an independent LessonUse meaning, posture domain and
precedence interpretation. Then prove a positive actual-use model and a deliberate
non-use model, refusal of selection/presentation alone, exact source/qualifier
refinement and record preservation. Whole-theory countermodels, public diagnostics
and independent checking follow the existing plan dependencies. No K04 proof or
source refinement is complete here. D03 and D04 globally remain separate reviews.

This assessment accepts only whether K04's intended meaning fits. It does not
accept the other relations, global policies, mathematical proofs or plan completion.
