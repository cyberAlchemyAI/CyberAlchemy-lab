K04 source adapter: implementation and remaining obligations

This package extends the earlier K04 candidate model with complete fixed source
body shapes and qualifier joins. K04 still awaits its existing owner assessment.
The proposed meaning, request, earlier verified model, plan and inherited inventory
remain unchanged. This package is not registered in the main preparation index.

LessonBodyProfiles.lean retains every field of the exact Lesson Application and
Operational Lesson schemas: 55 fields across six record types, with 70 active
schema assertion nodes. Root metadata, all payload fields and relation references
are decoded as closed required objects. String bounds, constants, enums, array
item constraints, minimum lengths and declared uniqueness are retained. Arrays
without uniqueItems may repeat. Whitespace remains valid for plain minLength:1
fields. The two fixed decoder/meaning equivalences are checked Lean theorems.
The generator uses the previously bound compiler without changing it; this is
not a proof that the Python compiler implements arbitrary JSON Schema correctly.

LessonSourceAdapter.lean adds a closed four-field qualifier decoder and a closed
source bundle containing the complete application, lesson and qualifier records.
The bundle is a candidate adapter input contract, not a frozen public API. It
checks against the independently defined K04 candidate meaning and independently
defined typed source joins. Seven additional general theorems establish the exact
adapter interpretation, successful qualification requirements, token consistency,
complete body meaning, missing-policy refusal and Boolean-check equivalence.

An explicit resolution catalog maps raw strings to exact typed revision references
or posture values. Duplicate token keys are refused. No prefix parser, spelling
convention or default interpretation supplies these mappings. Successful joins
require exact application and lesson identities; application owner/scope/session;
payload lesson, posture, assessment, conflicts and overrides; all four qualifiers;
and an outgoing applies-lesson counterpart of the correct kind and direction.
The earlier candidate model additionally requires captured records, exact frame
agreement, disposition evidence, owned precedence and retained conflict/override
basis. Selection and presentation remain unqualified even when shapes are valid.

The maps used in positive controls are explicitly synthetic. Two original schema
fixtures do not themselves establish one qualified relation. The application has:

- node_id: lesson-application:example-001
- payload lesson: operational-lesson:definition-carrier-coverage@1
- relation counterpart: operational-lesson:example-001

The provided lesson fixture has node_id operational-lesson:example-001. An owned
catalog would have to establish whether the two lesson tokens designate one exact
revision. No such alias or revision mapping is supplied here. The application also
uses the raw posture applied and an assessment token without an authenticated
assessment/provider. Shape validity therefore does not close these semantic joins.
The adapter does not silently rewrite the fixture or manufacture that evidence.

Controls cover all 55 field omissions, both original positive fixtures and ten
original negatives, closed object extras, scalar type/length constraints and array
constraints. The 250 complete-shape expectations use Draft202012Validator. The
29 semantic controls include synthetic use/non-use success, mismatched reference
joins, wrong counterpart direction, unknown policy, absent/conflicting token maps,
missing evidence/assessment, selection/presentation, and missing/extra qualifiers.
These 279 runtime observations per phase are tests, not 279 additional theorems.
The nine general declarations are inspected separately for axioms.

What remains for full K04 source refinement:

1. Actual owned and versioned token providers, posture meanings, assessment policy,
   precedence domain and evidence admission. The current finite rank profile and
   the applicability of D03/D04 still require their scoped assessments.
2. Authentication and completeness of captured catalogs, source snapshot/frame
   binding, raw bytes and digest integration, lifecycle and schema admission.
3. Semantic interpretation of Operational Lesson applicability, exclusions,
   evidence/counterevidence, expiry, status and retention; application intended
   influence; and remaining root owner, evidence, challenge and claim-ceiling
   policies. Full shape retention does not supply these policy interpretations.
4. A complete pinned-theory account of compliance, measured benefit, effective
   authority and method employment, with satisfiable non-entailment countermodels.
   Local candidate recording preservation does not discharge whole-rule closure.
5. Public API/diagnostic integration, required independent checking and the later
   composed extension/resource tasks in the full plan.

Boolean refusal here means that this source bundle does not qualify the resolved
candidate claim. It does not establish falsity of an unknown external fact. The
public unknown/unsupported classification remains a separate integration contract.

verify_candidate.py checks all source and dependency bindings, regenerates the
fixed profiles and controls for exact comparison, checks imported module locations,
and compiles the model, its controls, profiles, adapter and source controls in two
fresh phases. It reuses exact prior dependency outputs by matching phase. Replay
with the same Lean toolchain is not independent checking. No inherited ID is
discharged; all nine K04 IDs and all 263 successor IDs remain open.

Formalization still precedes contract freezing and integration: complete the
existing one-at-a-time owner review, specify the missing independent policies and
providers, prove full source and theory obligations, then attach exact discharge
evidence under the plan dependencies.
