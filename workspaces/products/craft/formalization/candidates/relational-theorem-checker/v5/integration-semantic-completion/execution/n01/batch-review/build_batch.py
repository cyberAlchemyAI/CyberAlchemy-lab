"""Build a successor definition proposal; never edit assessed source definitions.

This is specification generation, not proof generation or source interpretation.
The mathematical predicates below describe independently supplied semantic data.
Raw-field adapters, authenticity, satisfiability and refinement remain proof work.
"""
from pathlib import Path
import hashlib
import importlib.util
import json

HERE = Path(__file__).resolve().parent
N01 = HERE.parent
SUCCESSOR = N01.parents[1]
ROOT = SUCCESSOR.parents[5]
REVISION = 'v5-batch-definitions-2026-10-11-1'


def read(path):
    return json.loads(path.read_text())


def binding(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


# Each row supplies a relation-specific formula, its witness fields, intuition,
# a concrete correction, and the source adapter work that the formula needs.
# Field notation is defined in the generated individual definition, not inferred
# from an arbitrary raw string or the result of the relation checker.
SPECS = {
 'K00': (
  'Bounded representation permits a particular agent to represent a principal for this use. It does not make them the same identity.',
  'w.agent = s ∧ w.principal = t ∧ w.delegation = resolve(q.delegation_ref) ∧ w.scope = resolve(q.scope_ref) ∧ w.window = resolve(q.effective_period) ∧ w.revocation = resolve(q.revocation_state) ∧ PermitUse(W,w,f)',
  {'agent':'Agent Instance exact revision', 'principal':'Principal exact revision', 'delegation':'Delegation exact revision', 'scope':'owned scope revision', 'window':'epoch interval or exact session window', 'revocation':'as-of revocation observation', 'use':'exact action, subject and scope being represented', 'ancestors':'complete applicable delegation chain'},
  'Select the delegation for this agent and principal; narrow the use to the intersection of all ancestor envelopes and supply matching window/gate/revocation evidence.',
  'Original and redelegated grant authenticity, complete ancestry, scope inclusion, owned gates and observed revocation require adapters and refinement.'),
 'K01': (
  'An inquiry may aim at an improvement target while the target stays open. The link is optional: inquiries need not have an improvement target.',
  'w.inquiry = s ∧ w.target = t ∧ t = resolve(q.target_version_ref) ∧ w.role = code(q.addressing_role)',
  {'inquiry':'Research Inquiry exact revision', 'target':'Improvement Target exact revision', 'role':'owned intended-addressing role for this inquiry/target pair'},
  'Use the target revision actually named by the addressing declaration, or create a new declaration for the other revision.',
  'An owner-maintained optional addressing declaration and exact target/role resolution must be mapped; do not add a required target to every inquiry.'),
 'K02': (
  'An owner has selected this subject to address an intent. Selection supplies a reason for work, while satisfaction and completion need their own evidence.',
  'w.subject = s ∧ w.intent = t ∧ w.resolution = resolve(q.intent_resolution_ref) ∧ w.resolution.intent = t ∧ s ∈ w.resolution.selected ∧ s ∉ w.resolution.excluded ∧ w.role = code(q.addressing_role) ∧ w.role = roleFor(w.resolution,s) ∧ SelectedByOwner(W,w.resolution,f)',
  {'subject':'selected Assignment, Goal, Product, Capability, Project or Inquiry revision', 'intent':'Intent exact revision', 'resolution':'owned Intent Resolution with selected/excluded subjects, decision, roles and satisfaction tests', 'role':'selection addressing role'},
  'Supply the exact owner-selected resolution that includes this subject and agrees with its addressing role; revise the resolution if it excludes the subject.',
  'Existing parser/body fragments do not realize all selection-policy premises; satisfaction-test ownership, selection/exclusion and catalog authenticity remain.'),
 'K03': (
  'Evidence supports a specific observed impact on a subject. Impact can be established while cause, severity and responsibility remain unsettled.',
  'w.source = s ∧ w.affected = t ∧ w.scope = resolve(q.impact_scope) ∧ w.posture = code(q.evidence_posture) ∧ ObservedImpact(W,w,f)',
  {'source':'Failure Occurrence or Incident revision', 'affected':'exact affected subject revision', 'scope':'scope of the observed impact', 'posture':'observed-impact evidence posture', 'observations':'exact admissible impact observations with source and affected participant joins'},
  'Attach an admissible observation of this subject and impact scope; retain a prediction as a separate unestablished impact claim.',
  'Observation admissibility and external provenance must be supplied; occurrence and incident impact constructors need separate adapters.'),
 'K04': (
  'A recorded application says a lesson was used or deliberately not used, with a reason in this session. Merely selecting or displaying it is insufficient.',
  'w.application = s ∧ w.lesson = t ∧ t = resolve(q.lesson_revision_ref) ∧ w.posture = code(q.application_posture) ∧ w.posture ∈ {used, deliberatelyNotUsed} ∧ w.assessment = resolve(q.applicability_assessment_ref) ∧ w.precedence = resolve(q.instruction_precedence) ∧ QualifiedLessonUse(W,w,f)',
  {'application':'Lesson Application exact revision', 'lesson':'Operational Lesson exact revision', 'posture':'used or deliberatelyNotUsed constructor', 'assessment':'exact lesson/application/frame applicability assessment', 'precedence':'owned instruction precedence policy', 'sessionOrAction':'exact attributable use envelope', 'conflicts':'all relevant instruction conflict origins', 'overrides':'exact justified override records'},
  'Record actual use or the deliberate non-use decision and its assessment; resolve applicable conflicts with an owned precedence basis.',
  'Synthetic draft uses inclusive intervals, unlike proposed D02 half-open intervals. Lesson identifiers in original fixtures disagree and need an owned mapping. Applicability, expiry, retention and influence fields are not fully refined.'),
 'K05': (
  'An identity assertion records a correspondence claim in a specified scope. Recording the claim neither merges identities nor reveals private attributes.',
  'w.assertor = s ∧ w.correspondent = t ∧ w.assertionKind = code(q.assertion_kind) ∧ w.scope = resolve(q.claim_scope) ∧ w.claim.correspondence = (s,t,w.assertionKind,w.scope)',
  {'assertor':'Identity Claim, Person Reference or Principal Reference revision', 'correspondent':'Person, Person Reference or Principal revision', 'assertionKind':'owned correspondence claim constructor', 'scope':'bounded correspondence claim scope', 'claim':'recorded assertion with exact participants and provenance'},
  'Supply the assertion for these participants and scope; request a separate identity operation if merging is actually intended.',
  'Each of the four permitted pairs needs its own assertion constructor and privacy boundary; no asserted identifier is an authenticated equivalence.'),
 'K06': (
  'An exact assignment connects an assignee with a role or responsibility and its recorded lifecycle. This connection alone does not add team membership or permissions.',
  'w.assignment = resolve(q.relation_record_ref) ∧ w.assignee = s ∧ w.assignedRoleOrResponsibility = t ∧ w.assignmentKind = code(q.assignment_kind) ∧ AssignmentRecorded(W,w,f)',
  {'assignment':'exact lifecycle assignment record', 'assignee':'Agent Instance, Person Reference or Team revision', 'assignedRoleOrResponsibility':'Role or Responsibility revision', 'assignmentKind':'owned role/responsibility assignment constructor', 'period':'assignment interval or session window', 'lifecycle':'recorded assignment state at the frame'},
  'Use the assignment naming this assignee and role/responsibility; show an active-at-frame record for a live assignment claim.',
  'Role-assignment and responsibility records have different fields. Historical assignment and live assignment require explicit temporal/lifecycle profiles.'),
 'K07': (
  'An implementation declares a binding to an ontology or schema. Binding identifies what it implements, while conformance and performance are assessed separately.',
  'w.implementation = s ∧ w.model = t ∧ w.role = code(q.binding_role) ∧ ((kind(t)=schema ∧ w.constructor=schemaBinding) ∨ (kind(t)=ontology ∧ w.constructor=ontologyBinding))',
  {'implementation':'Implementation exact revision', 'model':'Schema or Ontology exact revision', 'role':'owned binding role', 'constructor':'schemaBinding or ontologyBinding with exact model reference'},
  'Use a schema-binding witness for a schema target and an ontology-binding witness for an ontology target.',
  'Source-to-model binding fields and owned role catalogs require refinement; a binding must not reuse conformance evidence as its definition.'),
 'K08': (
  'An artifact type carries one exact definition and its content commitment. The type and definition retain distinct identities and ownership.',
  'w.artifactType = s ∧ w.definition = t ∧ t = resolve(q.definition_version_ref) ∧ w.bytes = bytes(W,t) ∧ hash(w.bytes)=q.definition_sha256 ∧ w.digestPolicy = f.digestPolicy',
  {'artifactType':'Artifact Type exact revision', 'definition':'Definition exact revision', 'bytes':'resolved immutable definition content bytes', 'digestPolicy':'exact named byte representation and hash algorithm'},
  'Resolve the specified definition bytes and recompute the commitment under the named digest policy; do not substitute a same-named revision.',
  'Content authenticity and raw definition capture remain assumptions to discharge; hash equality alone does not establish semantic correctness or ownership.'),
 'K09': (
  'A challenge event targets a revision under an exact contract and permitted mode. The target continues to need separate suspension or reversal decisions.',
  'w.challenge = s ∧ w.target = t ∧ t = resolve(q.challenged_version_ref) ∧ w.contract = resolve(q.challenge_contract_ref) ∧ w.mode = code(q.challenge_mode) ∧ ChallengePermitted(W,w,f)',
  {'challenge':'Challenge Event exact revision', 'target':'challenged exact revision', 'contract':'Challenge Contract exact revision', 'mode':'contract-permitted challenge constructor', 'posture':'recorded challenge request or assessment posture'},
  'Retarget the challenge to the correct revision under a contract permitting that target kind and mode; obtain separate suspension/reversal evidence if needed.',
  'All 100 target-kind branches must refine their contract target interpretation. Challenge-of-challenge is allowed only as an explicit record, not an inference loop.'),
 'K10': (
  'Conformance establishes the owned criteria for a particular subject, target and scope in a supplied snapshot. A later runtime state requires a new assessment.',
  'w.subject = s ∧ w.target = t ∧ t = resolve(q.exact_version_ref) ∧ w.scope = scopeValue(q.conformance_scope) ∧ w.evidence = evidenceValue(q.conformance_evidence_refs) ∧ ScopedCriteriaSatisfied(W,w,f)',
  {'subject':'Capability Instance or Context exact revision', 'target':'Contract, Governed Model or Context Profile exact revision', 'scope':'literal F0 scope or explicitly mapped successor scope', 'evidence':'literal F0 support reference or successor evidence-reference collection', 'criteria':'complete owned target criteria for the selected pair/profile'},
  'Provide admissible support for every owned applicable criterion of this target and scope; preserve the legacy F0 profile when using its literal tokens.',
  'Three different target semantics need separate bridges. Existing F0 evidence strings remain literal; successor lists and negative evidence must use a new explicit profile.'),
 'K11': (
  'A session consumed an immutable view to an exact position or extent. Consumption is historical and does not establish that its sources are still current.',
  'w.session = s ∧ w.view = t ∧ hash(bytes(W,t)) = q.view_digest ∧ w.cursor = cursorValue(q.cursor,t,q.view_digest) ∧ w.purpose = code(q.consumption_purpose) ∧ ConsumptionObserved(W,w,f)',
  {'session':'Agent Session exact revision', 'view':'Context View or Ontology View exact revision', 'cursor':'view-specific bounded position or extent', 'purpose':'owned consumption-purpose code', 'receipt':'attributable observation of consumption'},
  'Use a cursor from the same view revision and digest, and attach an attributable consumption receipt.',
  'Context and ontology views use different extent models; digest framing, cursor bounds, provenance and session attribution require adapters.'),
 'K12': (
  'A contribution declaration says how an activity intends to advance a product or goal. It does not establish delivered value or membership.',
  'w.activity = s ∧ w.objective = t ∧ w.role = code(q.contribution_role) ∧ w.scope = resolve(q.contribution_scope) ∧ w.declaration.activity = s ∧ w.declaration.objective = t ∧ w.declaration.role = w.role ∧ w.declaration.scope = w.scope ∧ w.declaration.intent = intendedContribution',
  {'activity':'exact activity/project/inquiry revision', 'objective':'Product or Goal exact revision', 'role':'owned intended contribution role', 'scope':'bounded contribution scope', 'declaration':'record of intended advancement'},
  'Match the declaration scope and role to this activity and objective; use separate outcome evidence for realized contribution.',
  'Each of eight permitted pairs needs an intended-contribution adapter; product value and goal achievement cannot be collapsed into this declaration.'),
 'K13': (
  'A binding names a control intended for a failure mode and states its role. The binding can exist before installation or execution.',
  'w.binding = s ∧ w.failureMode = t ∧ w.control = resolve(q.control_version_ref) ∧ w.binding.controlSubject = w.control ∧ w.binding.failureMode = t ∧ w.role = code(q.control_role) ∧ w.role ∈ {prevent,detect,contain,recover,compensate} ∧ w.installationPosture = code(q.installation_posture)',
  {'binding':'Failure Control Binding exact revision', 'failureMode':'Failure Mode exact revision', 'control':'the separate controlSubject revision', 'role':'one primary intended control role', 'installationPosture':'recorded binding installation posture'},
  'Reference the controlSubject revision, retain its actual installation posture, and select one owned primary control role.',
  'A typed control subject and installation-posture catalog must be mapped. The failure-mode target is not the control-version reference.'),
 'K14': (
  'A decision declares one governance effect on a target. Admission, adoption and authorization are distinct values, and a declaration does not execute them.',
  'w.decision = s ∧ w.target = t ∧ t = resolve(q.exact_target_version_ref) ∧ w.effect = effectValue(q.effect_kind) ∧ w.effect ∈ {admission,adoption,authorization} ∧ w.declaration = selectedDeclaration(W,s,t,w.effect,f)',
  {'decision':'Decision exact revision', 'target':'governance target exact revision', 'effect':'one distinct governance effect constructor', 'declaration':'exact selected decision declaration'},
  'Use the selected declaration for this effect and target; provide a separately authorized application receipt to claim execution.',
  'Retain F0 literal effect meaning while introducing any typed successor mapping. All 21 target branches need exact target/effect admissibility.'),
 'K15': (
  'A recorded transformation, compilation or projection produced one revision from another. Lineage does not transfer source authority or equate identities.',
  'w.derived = s ∧ w.input = t ∧ w.role = code(q.derivation_role) ∧ w.transform.role = w.role ∧ w.transform.output = s ∧ t ∈ w.transform.inputs ∧ w.transform.kind ∈ {transformation,compilation,projection}',
  {'derived':'derived exact revision', 'input':'source exact revision', 'role':'owned derivation role', 'transform':'exact transformation record with inputs and output'},
  'Provide the actual transformation record joining this input to this output; keep an origin assertion separate.',
  'Forty heterogeneous branches need input/output projections and transformation provenance. Repeated graph edges do not prove transformation correctness.'),
 'K16': (
  'An activity addresses an inquiry, or a finding proposes an answer. These are distinct engagement constructors; neither accepts the answer or completes the inquiry.',
  'w.carrier = s ∧ w.inquiry = t ∧ w.role = code(q.inquiry_role) ∧ ((kind(s)=finding ∧ w.constructor=proposedAnswer) ∨ (kind(s)∈{experimentDesign,experimentRun,researchRun} ∧ w.constructor=activityAddressing))',
  {'carrier':'Finding or research activity exact revision', 'inquiry':'Research Inquiry exact revision', 'role':'owned answer/activity engagement role', 'constructor':'proposedAnswer or activityAddressing'},
  'Select the finding-answer constructor for a finding and the activity-addressing constructor for a research activity.',
  'Raw carrier bodies and role codes must refine the two constructors; answer content and experimental execution remain separate evidence.'),
 'K17': (
  'An evaluation or experiment names its subject and purpose. Naming the target leaves the eventual result and evidential polarity open.',
  'w.assessor = s ∧ w.subject = t ∧ w.role = code(q.evaluation_role) ∧ w.purpose = code(q.evaluation_purpose) ∧ w.assessmentScope.subject = t ∧ w.assessmentScope.role = w.role ∧ w.assessmentScope.purpose = w.purpose',
  {'assessor':'Evaluation, experiment or specialized assessment exact revision', 'subject':'exact evaluated subject revision', 'role':'owned assessment role', 'purpose':'owned evaluation purpose', 'assessmentScope':'recorded target and scope; no result field is required to define targeting'},
  'Use the assessment scope naming this subject and purpose; attach a result assessment separately when claiming support or contradiction.',
  'Sixteen branches include specialized failure, lesson, preference and work assessments; their target fields need separate source projections.'),
 'K18': (
  'Evidence bears on a proposition with an explicit supporting or contradicting polarity. Support can be recorded without a truth or acceptance decision.',
  'w.evidence = s ∧ w.claimCarrier = t ∧ w.polarity = polarityValue(q.polarity) ∧ w.polarity ∈ {supports,contradicts} ∧ EvidentialCorrespondence(W,w,f)',
  {'evidence':'exact evidence carrier revision', 'claimCarrier':'exact target containing the proposition', 'proposition':'owned proposition selector within that target revision', 'polarity':'supports or contradicts constructor', 'correspondence':'admissible evidential correspondence record'},
  'Supply the correspondence for the selected target proposition and declared polarity; changing polarity needs a new witness.',
  'Seventy-two pairs need explicit proposition selectors and admissibility policies. A target artifact can contain multiple claims; the endpoint alone does not choose one.'),
 'K19': (
  'A context supplies a declared interpretation boundary for a subject. Framing makes it relevant for a purpose without validating its claims.',
  'w.context = s ∧ w.subject = t ∧ w.role = code(q.framing_role) ∧ (t,w.role) ∈ w.context.subjectBoundary ∧ RelevanceWithin(W,w,f)',
  {'context':'Context exact revision', 'subject':'framed Product, Goal, Project, Review or Bounded Context revision', 'role':'owned framing role', 'relevance':'exact context subject/relevance boundary'},
  'Add or select the exact context revision whose relevance boundary includes this subject and role.',
  'Context framing and DDD Bounded Context identity need separate projections; relevance does not authenticate a source or make it current.'),
 'K20': (
  'A view fulfills a particular request when every mandatory owned request constraint is met at resolution time. Later source changes require rechecking.',
  'w.view = s ∧ w.request = t ∧ w.view.request = t ∧ w.view.contextRevision = w.request.contextRevision ∧ w.role = code(q.fulfillment_role) ∧ w.criteria = deriveCriteria(W,t,f) ∧ RequestSatisfied(W,w,f)',
  {'view':'Context View exact revision', 'request':'Context Request exact revision', 'role':'owned request/view fulfillment role', 'criteria':'complete independently derived selector, exclusion, freshness, budget and output criterion set', 'resolutionEpoch':'view generation/source-resolution epoch in one domain', 'evidence':'exact admissible criterion support'},
  'Derive the full criterion set from the owned request, restore omitted selectors, and supply exact support at the resolution epoch.',
  'Owned selector derivation, exclusions, source freshness, budgets and output constraints require a full E03 bridge; a caller-supplied reduced set is insufficient.'),
 'K21': (
  'A policy, constitution, challenge contract or classification scheme applies to a subject in this frame. Applicability does not establish compliance or permission.',
  'w.subject = s ∧ w.governor = t ∧ w.role = code(q.governance_role) ∧ GovernanceApplies(W,w,f)',
  {'subject':'exact governed subject revision', 'governor':'Policy, Constitution, Challenge Contract or Classification Scheme revision', 'role':'owned governance applicability role', 'conditions':'owned applicability conditions', 'origins':'complete applicable norm origins'},
  'Select the governance record applicable to this subject, scope and time; leave unresolved conditions unknown.',
  'Twenty-nine branches require distinct governor semantics. Inherited norms and opposing obligations need the E00/E04 conflict bridge.'),
 'K22': (
  'A profile or instance declares a particular capability under an owned basis. Capability declaration does not confer authority or prove successful performance.',
  'w.agent = s ∧ w.capability = t ∧ t = resolve(q.capability_version_ref) ∧ w.basis = resolve(q.declaration_basis) ∧ w.basis.agent = s ∧ w.basis.capability = t ∧ w.basis.constructor = ownedCapabilityDeclaration',
  {'agent':'Agent Profile or Agent Instance exact revision', 'capability':'Agent Capability exact revision', 'basis':'owned capability declaration with exact agent/capability joins'},
  'Use the declaration for this profile or instance and capability revision; do not substitute a successful action trace for a declaration.',
  'Instance derivation from a profile needs an explicit reviewed bridge. Profile declarations do not automatically authorize or equip every instance.'),
 'K23': (
  'An instance inherits identified contract obligations, retaining where they came from. Inheritance does not establish that the obligations are satisfied.',
  'w.instance = s ∧ w.contract = t ∧ t = resolve(q.contract_version_ref) ∧ w.binding = resolve(q.binding_ref) ∧ w.binding.instance = s ∧ w.binding.contract = t ∧ InheritedOrigins(W,w,f)',
  {'instance':'Capability Instance exact revision', 'contract':'Contract exact revision', 'binding':'owned instance/contract inheritance binding', 'origins':'norm records keyed by subject, contract, norm and binding revision', 'conditions':'owned condition expressions determining active or potential status'},
  'Use the exact inheritance binding and retain every applicable norm origin; report unknown activation as potential rather than satisfied.',
  'Complete contract norm extraction, conditional activation, overrides and conflict handling need E00/E04 adapters; an AST result is not an authority grant.'),
 'K24': (
  'An exact binding classifies a subject under a model, product, capability, failure mode or classification value. Classification does not show realization or conformance.',
  'w.subject = s ∧ w.parent = t ∧ t = resolve(q.parent_version_ref) ∧ w.binding = resolve(q.binding_ref) ∧ w.binding.subject = s ∧ w.binding.parent = t ∧ w.binding.constructor = classificationFor(kind(s),kind(t))',
  {'subject':'classified exact revision', 'parent':'exact classification/model/product/failure parent revision', 'binding':'owned classification assignment or model-instance binding', 'constructor':'pair-specific classification constructor'},
  'Choose the binding whose subject, parent revision and classification constructor match this pair.',
  'Twelve branches require classification-specific bodies; classification under a failure mode is not the separate confirmation assessment.'),
 'K25': (
  'A verified local transaction already applied an authorized deterministic consequence atomically. The relation records that application and cannot add new authorization.',
  'w.transaction = s ∧ w.output = t ∧ w.receipt = receiptValue(q.application_receipt_ref) ∧ w.role = roleValue(q.consequence_role) ∧ hash(bytes(W,t)) = q.output_digest ∧ AppliedAuthorizedBundle(W,w,f)',
  {'transaction':'Admission Transaction exact revision', 'output':'exact generated output, project state or event history revision', 'receipt':'completed local atomic application receipt', 'role':'selected consequence role in the approved bundle', 'bundle':'exact previously authorized complete bundle', 'before':'prior local state', 'after':'actual final local state', 'generator':'pinned deterministic generator'},
  'Provide the complete applied bundle, prior/final state and output digest from a verified local execution; a planned receipt is insufficient.',
  'Four consequence constructors need execution provenance and atomicity proofs. Existing F0 literal receipt/role/digest meanings must retain their own profile.'),
 'K26': (
  'A member-to-container record establishes an owned membership or composition link. It does not imply assignments, contributions or inherited permissions.',
  'w.member = s ∧ w.container = t ∧ w.role = code(q.membership_role) ∧ (s,w.role) ∈ w.container.members ∧ w.constructor = membershipFor(kind(s),kind(t))',
  {'member':'exact member revision', 'container':'exact container revision', 'role':'owned membership/composition role', 'constructor':'team membership, role composition, bundle membership, ontology membership or other exact pair constructor'},
  'Use the owner-maintained member-to-container record in the declared direction; do not invert it or add transitive membership without a rule.',
  'Twenty-four branches have distinct composition/membership meanings. Live membership requires lifecycle evidence separate from historical inclusion.'),
 'K27': (
  'An occurrence was observed within a particular execution envelope and time domain. Temporal inclusion does not establish cause or recovery.',
  'w.occurrence = s ∧ w.envelope = t ∧ t = resolve(q.envelope_version_ref) ∧ w.scope = resolve(q.temporal_scope) ∧ OccurrenceWithin(W,w,f)',
  {'occurrence':'Failure Occurrence exact revision', 'envelope':'Action, Session, experiment, research or Work execution envelope', 'scope':'owned temporal attribution scope', 'event':'observed occurrence time or interval in the envelope time domain'},
  'Resolve the exact envelope and compare the observed event under its owned time-domain/window policy.',
  'All five envelope kinds need observed execution windows; equal numeric epochs in different domains cannot establish inclusion.'),
 'K28': (
  'An origin declaration identifies where an identity or content came from. It does not establish a transformation or replacement.',
  'w.derived = s ∧ w.origin = t ∧ w.role = code(q.origin_role) ∧ w.assertion.derived = s ∧ w.assertion.source = t ∧ w.assertion.role = w.role ∧ w.assertion.constructor = originDeclaration',
  {'derived':'exact identity/content artifact revision', 'origin':'Source exact revision', 'role':'owned origin role', 'assertion':'exact origin declaration'},
  'Use an origin declaration joining these revisions; use a separate transformation or succession record for those stronger claims.',
  'Seven source-origin projections require owned provenance interpretation. Origin and derivation records are not interchangeable.'),
 'K29': (
  'An agent is attributable to an operation in its exact active session and recorded posture. An attempted or failed action remains an attempted or failed action.',
  'w.agent = s ∧ w.operation = t ∧ w.session = resolve(q.session_ref) ∧ w.session.agent = s ∧ w.role = code(q.participation_role) ∧ w.posture = code(q.action_posture) ∧ AttributedOperation(W,w,f)',
  {'agent':'Agent Instance exact revision', 'operation':'Action, experiment/research run, Review or Work exact revision', 'session':'exact attributable Agent Session revision', 'role':'owned operation participation role', 'posture':'proposed, attempted, completed, rejected or failed constructor', 'operationEpoch':'recorded operation epoch in the session domain'},
  'Join this operation to this agent and its session at the recorded epoch; retain the observed posture without upgrading it.',
  'Non-Agent-Action operations have different actor/session fields; all five branches need attribution projections and posture provenance.'),
 'K30': (
  'An action produced an exact recorded output. Producing a candidate does not accept it, prove its correctness or admit it.',
  'w.action = s ∧ w.output = t ∧ w.receipt = resolve(q.action_receipt_ref) ∧ w.role = code(q.production_role) ∧ w.posture = code(q.output_posture) ∧ t ∈ w.action.actualOutputs ∧ OutputProduced(W,w,f)',
  {'action':'Agent Action exact revision', 'output':'exact produced artifact revision', 'receipt':'attributable action/output/frame production receipt', 'role':'owned production role', 'posture':'recorded output posture, separate from output acceptance', 'actualOutputs':'outputs established by the production observation'},
  'Supply a receipt for this actual output and action; keep a planned output in the plan until production is observed.',
  'Nineteen output-kind branches need exact receipt roles and body capture. Planned references and candidate acceptance labels are insufficient.'),
 'K31': (
  'An instance is configured by an exact profile through a specific binding. Configuration alone does not create capability, conformance or identity continuity.',
  'w.instance = s ∧ w.profile = t ∧ t = resolve(q.profile_version_ref) ∧ w.binding = resolve(q.binding_ref) ∧ w.binding.instance = s ∧ w.binding.profile = t ∧ w.binding.constructor = profileConfiguration',
  {'instance':'Agent Instance exact revision', 'profile':'Agent Profile exact revision', 'binding':'owned profile configuration record'},
  'Supply the exact profile-configuration binding; a generic classification assignment cannot substitute for it.',
  'Profile binding source fields and ownership need refinement; capability inheritance and identity continuity require separate explicit contracts.'),
 'K32': (
  'An implementation instantiates a product capability, or an experiment run executes its design. Each realization constructor needs evidence appropriate to that pair.',
  'w.subject = s ∧ w.target = t ∧ t = resolve(q.exact_target_version_ref) ∧ w.role = code(q.realization_role) ∧ ((kind(s)=implementation ∧ w.constructor=implementedCapability) ∨ (kind(s)=experimentRun ∧ w.constructor=executedDesign)) ∧ RealizationObserved(W,w,f)',
  {'subject':'Implementation or Experiment Run exact revision', 'target':'Product Capability or Experiment Design exact revision', 'role':'owned realization role', 'constructor':'implementedCapability or executedDesign', 'evidence':'exact implementation/instantiation or execution observation'},
  'Attach implementation evidence for the capability branch or attributable execution evidence for the design branch.',
  'The two branches need different source and evidence bridges; a binds-implementation edge or experimental design declaration is insufficient.'),
 'K33': (
  'A context request asks for resolution of a particular context revision and constraints. The request can exist before any view is created.',
  'w.request = s ∧ w.context = t ∧ t = resolve(q.context_version_ref) ∧ w.request.contextRevision = t ∧ RequestWellFormed(W,w,f)',
  {'request':'Context Request exact revision', 'context':'Context exact revision', 'consumers':'exact intended consumers', 'selectors':'owned request selectors', 'constraints':'exclusions, freshness, budget and output constraints'},
  'Bind the request to the intended exact context revision and its complete constraints; produce and assess a view separately.',
  'The source has context_ref and context_version_ref fields; their exact revision join and all request constraints need refinement.'),
 'K34': (
  'An action is intended as a response to an occurrence or incident. Its intended outcome remains separate from successful containment, recovery or closure.',
  'w.action = s ∧ w.incidentOrOccurrence = t ∧ w.role = code(q.response_role) ∧ w.objective = resolve(q.intended_outcome) ∧ w.declaration.action = s ∧ w.declaration.responseTarget = t ∧ w.declaration.role = w.role ∧ w.declaration.intendedOutcome = w.objective',
  {'action':'Agent Action exact revision', 'incidentOrOccurrence':'Incident or Failure Occurrence exact revision', 'role':'owned intended response role', 'objective':'declared versioned response outcome', 'declaration':'owned intended response declaration'},
  'Supply the declaration naming this incident/occurrence and intended outcome; assess actual recovery or closure separately.',
  'Both response constructors and intended-outcome ownership need mapping; response labels cannot discharge recovery criteria.'),
 'K35': (
  'An authority claim or boundary declares its scope over a decision scope or role assignment. Recording a boundary does not authenticate a claim or issue a grant.',
  'w.declarer = s ∧ w.subject = t ∧ w.role = code(q.authority_role) ∧ w.scope = resolve(q.scope_ref) ∧ ScopeDeclared(W,w,f)',
  {'declarer':'Authority Claim or Authority Boundary exact revision', 'subject':'Decision Scope or Role Assignment exact revision', 'role':'owned declared boundary role', 'scope':'explicit owned declared authority scope', 'declaration':'boundary declaration; not an authenticated grant'},
  'Resolve the declared boundary for this subject and scope; establish authentication and permission through separate records.',
  'Three branches need scope interpretation. Scope declaration must not reuse effective authority as its antecedent and become a grant-producing definition.'),
 'K36': (
  'Succession records that a revision continues or supersedes its predecessor. Actual replacement requires a separately qualified lifecycle transition.',
  'w.successor = s ∧ w.predecessor = t ∧ kind(s)=kind(t) ∧ w.effect = successionValue(q.succession_effect) ∧ w.effect ∈ {continues,supersedes} ∧ w.record.participants = (s,t,w.effect)',
  {'successor':'exact successor revision', 'predecessor':'exact predecessor revision of the same declared kind', 'effect':'continues or supersedes declaration', 'record':'owned directional succession declaration', 'replacement':'optional separate qualified lifecycle transition, not required to record a declaration'},
  'Keep continues and supersedes distinct; obtain a qualified replacement transition before changing active-state selection.',
  'All 100 same-kind branches need lineage/lifecycle adapters. Whether to reject self-links or cycles is proposed validation policy, not silently added to inherited meaning.'),
 'K37': (
  'An experiment design targets an exact hypothesis for testing. Designing the test does not run it or establish the hypothesis truth.',
  'w.design = s ∧ w.hypothesis = t ∧ t = resolve(q.hypothesis_version_ref) ∧ w.role = code(q.test_role) ∧ w.protocol.hypothesis = t ∧ w.protocol.testRole = w.role',
  {'design':'Experiment Design exact revision', 'hypothesis':'Hypothesis exact revision', 'role':'owned test role', 'protocol':'owned revision-bound experiment protocol'},
  'Use the protocol targeting this hypothesis revision; supply separate run observations and evidence for a test result.',
  'Protocol targeting and test-role resolution require source refinement; executed experiments and supporting/contradicting evidence are separate predicates.'),
 'K38': (
  'A subject records a dependency on or employment of a method specification. That dependency need not mean an implementation has run successfully.',
  'w.subject = s ∧ w.method = t ∧ w.role = code(q.usage_role) ∧ w.constructor ∈ {methodDependency,methodEmployment} ∧ w.record.method = t ∧ w.record.subject = s',
  {'subject':'exact method-dependent activity/product/project/measurement revision', 'method':'Method specification exact revision', 'role':'owned dependency/employment role', 'constructor':'methodDependency or methodEmployment', 'record':'attributable dependency/use declaration'},
  'Resolve the method specification revision and the declared dependency/employment role; do not substitute an implementation identifier.',
  'Seven source branches and the migrated Method carrier need exact adapters. Actual execution postures must be witnessed separately from declared dependency.'),
 'K39': (
  'A session or action records a dependency on, proposed use of or invocation of a tool under an exact contract. Only an invocation constructor requires an invocation trace.',
  'w.subject = s ∧ w.tool = t ∧ t = resolve(q.tool_version_ref) ∧ w.contract = resolve(q.invocation_contract_ref) ∧ w.role = code(q.use_role) ∧ ToolContractApplies(W,w,f) ∧ (w.constructor=invocation → InvocationObserved(W,w,f))',
  {'subject':'Agent Session or Agent Action exact revision', 'tool':'Tool or Implementation exact revision', 'contract':'owned invocation contract exact revision', 'role':'owned tool dependency/proposal/invocation role', 'constructor':'dependency, proposedUse or invocation', 'trace':'exact attempted/completed/failed invocation trace when invocation is claimed'},
  'Use the contract for this subject and tool revision; supply an attributable invocation trace only when claiming invocation.',
  'Four branches need tool/implementation contract adapters and explicit posture mappings; failed invocation is still distinct from successful external effect.'),
 'K40': (
  'Admissible evidence establishes that an exact boundary condition was not satisfied. This finding alone does not confirm a failure mode or its cause.',
  'w.occurrence = s ∧ w.boundary = t ∧ t = resolve(q.boundary_version_ref) ∧ w.posture = code(q.evidence_posture) ∧ BoundaryNotSatisfied(W,w,f)',
  {'occurrence':'Failure Occurrence exact revision', 'boundary':'Contract, Policy, Schema or Challenge Contract exact revision', 'posture':'owned admissible non-satisfaction evidence posture', 'test':'owned boundary condition test', 'evidence':'exact negative assessment supporting non-satisfaction'},
  'Use admissible evidence against this boundary revision and its owned test; leave missing evidence unknown and confirm the failure mode separately.',
  'Four boundary constructors require distinct test semantics. Source violation evidence, criterion refutation and failure-mode confirmation must remain separate.'),
}

# Exact mathematical interpretation of every special atom used above.
ATOMS = {
 'resolve':'The unique entry for the raw token in the selected immutable typed reference catalog for this relation, pair, field and frame. Missing, ambiguous or wrong-kind entries are undefined and cannot establish Meaning.',
 'code':'The unique entry in the owner-reviewed code catalog indexed by relation kind, exact ordered pair, field and catalog revision. Its semantic constructor and record role must agree; identical spellings in another catalog are distinct.',
 'kind':'The independently captured governed artifact kind of an exact reference. Camel-case constructor names in formulas denote the corresponding hyphenated source kinds listed in the signature matrix.',
 'bytes':'The exact immutable resolved content bytes under the frame byte representation; source authenticity is a separately stated assumption.',
 'hash':'The pinned content-commitment algorithm applied to those exact bytes. Equality is checked under the named byte/hash assumptions and is not an authenticity or semantic-correctness theorem.',
 'PermitUse':'The exact delegation names agent and principal; the proposed use lies in every independently established ancestor action/subject/scope envelope; all owned gates evaluate yes; the use epoch lies in the D02 window in its domain; admissible as-of observations show every relevant delegation unrevoked. The ancestry input must be complete under its owned derivation policy.',
 'SelectedByOwner':'An actual decision in the independently supplied owner decision catalog selects this resolution revision, selected/excluded participants, role map and exact satisfaction-test definitions within the frame. The tests need not have passed.',
 'roleFor':'The uniquely selected addressing role for this subject in the exact owned Intent Resolution role map. Missing or ambiguous entries cannot establish the selection meaning.',
 'ObservedImpact':'At least one admissible exact observation identifies the source occurrence/incident, affected subject, scope and observed impact in the frame under the selected observation policy. A forecast or declared possibility is not an observation.',
 'QualifiedLessonUse':'The application, lesson, session/action, disposition evidence and applicability assessment join exactly; assessment covers applicable/excluded/expiry conditions at this use. All relevant conflicts and override origins are retained. The owned precedence relation is irreflexive and transitive on the applicable instruction set, and each required resolution has a justified winner. Used and deliberate non-use have distinct attributable records.',
 'AssignmentRecorded':'The owner-maintained assignment joins assignee, role/responsibility, assignment kind, scope, period and lifecycle. Historical mode records the witnessed state at its recorded epoch; live mode additionally requires active lifecycle and a containing D02 window at the frame epoch. The selected mode is explicit.',
 'ChallengePermitted':'The exact contract admits the challenge target kind, mode and challenger in this scope; the challenge body names the target revision and recorded posture. This predicate contains no suspension, reversal or contradiction proof.',
 'scopeValue':'Legacy F0 selects its original exact literal-token denotation; the successor selects an explicit owned scope-catalog mapping. Profile selection is part of the meaning revision and cannot silently widen the legacy interpretation.',
 'evidenceValue':'Legacy F0 uses its original literal evidence-reference meaning; the successor resolves an exact bounded reference collection with declared multiplicity/duplicate policy. A string is not implicitly split into a list.',
 'ScopedCriteriaSatisfied':'In successor mode the complete owned criterion derivation for this exact pair/target/scope has a yes verdict for every active mandatory criterion and no unresolved potential/conflicting required criterion. D05 determines verdicts from admissible exact evidence. Legacy F0 retains its pinned original any-accepted-positive-support predicate, separately indexed by profile.',
 'cursorValue':'The unique owner-resolved cursor interpretation in this exact view revision and digest. Its positions or extent lie within the view-specific bounds; it is neither a source epoch nor a cursor from another view.',
 'ConsumptionObserved':'An admissible attributable consumption record joins this session, view bytes, extent and purpose at the recorded epoch. Availability, a request, or a generated view alone do not establish consumption.',
 'effectValue':'The explicit profile-indexed interpretation of the raw effect token as admission, adoption or authorization. Legacy literal meaning is retained; no cross-effect conversion exists.',
 'selectedDeclaration':'The unique owned selected decision declaration for this decision/target/effect in the frame. Other declarations or later transactions remain separate records.',
 'EvidentialCorrespondence':'An owned correspondence record selects an exact proposition within the target carrier and connects this evidence revision and polarity under the selected admissibility policy. The proposition selector must be unique; acceptance decisions and independent truth valuation are not premises.',
 'polarityValue':'The unique owned interpretation of this raw token as supports or contradicts for the selected evidence/target proposition. It is not a truth valuation or an acceptance decision.',
 'RelevanceWithin':'The exact context boundary includes this subject and framing role under its owned relevance interpretation; a Bounded Context target retains its separate domain identity.',
 'deriveCriteria':'The deterministic owned derivation from the exact request body, selector catalogs, exclusions, freshness requirement, budget and output constraints in the frame. The complete output is bound by revision/digest; callers cannot provide a smaller substitute.',
 'RequestSatisfied':'The view/request/context revision joins are exact; source epoch and generation epoch use the same domain; deriveCriteria produces the complete mandatory set; D05 supplies yes for every mandatory criterion; no unresolved potential or conflict is ignored. Included/excluded material, freshness at resolution, budget and output format satisfy the request. An empty set is allowed only when the owned request derivation itself yields it.',
 'GovernanceApplies':'An exact applicability record names this subject, governor and role; its owned scope/window and applicability conditions evaluate yes. All applicable norm origins are retained. Conflicting norms are represented separately and cannot produce a compliance or permission verdict.',
 'InheritedOrigins':'Every contract obligation selected by the complete owned inheritance derivation appears with its subject/contract/norm/binding origin. E00 yes activates, no makes inactive, unknown makes potential; conflicts are retained rather than resolved by dropping an origin.',
 'classificationFor':'The owned constructor indexed by this exact allowed pair: model instance, product/capability classification, failure classification or classification-value assignment. Each constructor joins the proper parent revision without making a conformance or failure confirmation claim.',
 'receiptValue':'Profile-indexed exact application-receipt interpretation. The legacy F0 literal predicate remains separate from a successor resolved applied-receipt record.',
 'roleValue':'Profile-indexed exact consequence-role interpretation. The selected consequence must belong to the approved bundle, not an arbitrary role label.',
 'AppliedAuthorizedBundle':'A verified local execution record binds transaction, complete already-authorized bundle, prior state, pinned deterministic generator and final state. All and only declared consequences apply atomically; the named output bytes/digest occur in the final state. No authority root, external action or runtime activation outside the approved envelope is introduced. A self-reported applied flag is insufficient.',
 'membershipFor':'The owner-maintained membership/composition constructor for the exact ordered pair. It reads the corresponding container record; inverse or transitive membership is not supplied by this function.',
 'OccurrenceWithin':'An admissible observation supplies the occurrence event time/interval; the exact envelope independently supplies its execution window in the same time domain. The owned temporal-scope policy establishes inclusion under D02. Planned windows do not show observed occurrence.',
 'AttributedOperation':'The operation and session records identify this agent, role and posture; admissible operation evidence supplies the operation epoch, and the exact session is active at that epoch in the same time domain. This predicate does not require successful effect or owner approval.',
 'OutputProduced':'An admissible production observation and receipt join this action, output bytes/revision, role, posture and frame. The output belongs to the observed actual output set, not merely a planned set. It may remain a candidate or later be rejected.',
 'RealizationObserved':'For implementedCapability, exact implementation/instantiation evidence connects subject and capability. For executedDesign, an attributable experiment execution connects run and design. The owned realization policy admits the evidence; neither branch requires conformance, benefit or hypothesis truth.',
 'RequestWellFormed':'The exact context request resolves its consumers, context reference/revision, selectors, exclusions and bounded freshness/budget/output constraints under the owned request schema/profile. Resolution has not necessarily been executed.',
 'ScopeDeclared':'The exact boundary declaration joins declarer and subject; its owned scope includes the named subject in the declared role. Authentication, effective permission and execution are independent catalogs, never synthesized from this declaration.',
 'successionValue':'The exact owned interpretation as continues or supersedes. A supersedes declaration and a qualified replacement transition are different records; continues never becomes replacement.',
 'ToolContractApplies':'The exact contract admits the subject/tool revision, scope, role and dependency/proposal/invocation constructor. Each code resolves to exactly one constructor; undeclared postures are unsupported.',
 'InvocationObserved':'An admissible attributable trace joins the invocation to this subject, tool revision and contract. Attempted, completed and failed postures remain distinct; external effects need separate observations.',
 'BoundaryNotSatisfied':'The owned boundary test and admissible exact negative assessment establish non-satisfaction for this occurrence/boundary/frame under D05. A conflicting positive assessment yields conflict and cannot silently count as established non-satisfaction. Unknown is not false.',
}

# These definitions specialize every qualifier, including identically spelled
# role fields whose meanings differ between relations.
QUALIFIERS = {
 'K00': {'delegation_ref':('w.delegation','exact Agent-to-Principal delegation; every ancestor restriction remains applicable'), 'scope_ref':('w.scope','owned scope containing the proposed use and contained in every ancestor envelope'), 'effective_period':('w.window','half-open epoch interval or exact observed session window, with one time domain'), 'revocation_state':('w.revocation','admissible as-of observations covering this use and every relevant ancestor')},
 'K01': {'target_version_ref':('w.target','exact Improvement Target revision; optional inquiry linkage'), 'addressing_role':('w.role','intended investigation/addressing role; no resolution or measured improvement')},
 'K02': {'intent_resolution_ref':('w.resolution','owned selected resolution including this subject and excluding no selected subject'), 'addressing_role':('w.role','role chosen for this subject by that exact resolution')},
 'K03': {'impact_scope':('w.scope','owned scope of the observed affected-subject impact'), 'evidence_posture':('w.posture','observed-impact evidence posture under the exact observation policy; prediction does not qualify')},
 'K04': {'lesson_revision_ref':('w.lesson','exact Operational Lesson revision'), 'application_posture':('w.posture','used or deliberately-not-used; selected and presented remain insufficient'), 'applicability_assessment_ref':('w.assessment','assessment for this lesson/application/envelope, including exclusions and expiry'), 'instruction_precedence':('w.precedence','owned strict partial order and justified conflict/override resolution; no implicit numeric tie-break')},
 'K05': {'assertion_kind':('w.assertionKind','bounded correspondence claim constructor for this exact pair'), 'claim_scope':('w.scope','bounded domain of this asserted correspondence, with privacy restrictions')},
 'K06': {'assignment_kind':('w.assignmentKind','owned role-assignment or responsibility-assignment constructor for this pair'), 'relation_record_ref':('w.assignment','exact assignee/role-or-responsibility assignment and lifecycle record')},
 'K07': {'binding_role':('w.role','schema-binding or ontology-binding role as determined by target kind')},
 'K08': {'definition_version_ref':('w.definition','exact carried Definition revision'), 'definition_sha256':('hash(w.bytes)','commitment to the exact definition bytes under the pinned representation/hash assumption')},
 'K09': {'challenge_contract_ref':('w.contract','exact contract permitting this target kind, challenger and challenge mode'), 'challenge_mode':('w.mode','contract-permitted request/assessment challenge mode; no suspension constructor'), 'challenged_version_ref':('w.target','exact challenged artifact revision')},
 'K10': {'conformance_scope':('w.scope','legacy literal F0 scope or separately versioned typed scope mapping'), 'exact_version_ref':('w.target','legacy exact target token or explicit successor exact-revision mapping'), 'conformance_evidence_refs':('w.evidence','legacy literal reference or successor bounded reference collection; no implicit string splitting')},
 'K11': {'view_digest':('hash(bytes(W,w.view))','exact consumed view content commitment'), 'cursor':('w.cursor','bounded position/extent within that exact view revision and digest'), 'consumption_purpose':('w.purpose','owned session consumption purpose, separate from request fulfillment')},
 'K12': {'contribution_role':('w.role','intended activity-to-product/goal contribution constructor'), 'contribution_scope':('w.scope','bounded scope of intended contribution, not a product-value assessment')},
 'K13': {'control_role':('w.role','one primary prevent/detect/contain/recover/compensate role'), 'control_version_ref':('w.control','exact binding.controlSubject revision; never the failure-mode endpoint'), 'installation_posture':('w.installationPosture','owner-recorded intended/installed or other declared binding posture; no installation inference')},
 'K14': {'effect_kind':('w.effect','distinct admission/adoption/authorization declaration value in the selected profile'), 'exact_target_version_ref':('w.target','exact selected governance target, preserving F0 literal meaning')},
 'K15': {'derivation_role':('w.role','transformation/compilation/projection role joining actual input and output revisions')},
 'K16': {'inquiry_role':('w.role','finding proposed-answer role or activity-addressing role; constructor follows source kind')},
 'K17': {'evaluation_role':('w.role','pair-specific target assessment role, including specialized failure/lesson/preference/work assessment'), 'evaluation_purpose':('w.purpose','owned reason/scope for assessment; no evidence polarity or result')},
 'K18': {'polarity':('w.polarity','exact supports or contradicts correspondence for the selected proposition within the target')},
 'K19': {'framing_role':('w.role','owned context-to-subject relevance role, keeping Bounded Context identity distinct')},
 'K20': {'fulfillment_role':('w.role','owned complete request/view fulfillment constructor, distinct from generic conformance')},
 'K21': {'governance_role':('w.role','pair-specific policy/constitution/contract/scheme applicability role')},
 'K22': {'capability_version_ref':('w.capability','exact Agent Capability revision'), 'declaration_basis':('w.basis','owned exact profile/instance capability declaration; no implicit profile propagation')},
 'K23': {'binding_ref':('w.binding','exact instance/contract inheritance binding with complete obligation origins'), 'contract_version_ref':('w.contract','exact inherited Contract revision')},
 'K24': {'parent_version_ref':('w.parent','exact classification/model/product/failure parent revision'), 'binding_ref':('w.binding','pair-specific classification or model-instance record')},
 'K25': {'application_receipt_ref':('w.receipt','F0 literal or separately resolved verified applied atomic receipt'), 'consequence_role':('w.role','selected deterministic consequence role in the exact approved bundle'), 'output_digest':('hash(bytes(W,w.output))','exact final consequence bytes commitment under the selected profile')},
 'K26': {'membership_role':('w.role','owned directional membership/composition constructor for this member/container pair')},
 'K27': {'envelope_version_ref':('w.envelope','exact observed execution envelope revision'), 'temporal_scope':('w.scope','owned temporal attribution scope and time-domain inclusion policy')},
 'K28': {'origin_role':('w.role','owned identity/content origin declaration; separate from transformation or succession')},
 'K29': {'session_ref':('w.session','exact session belonging to this agent and active at the recorded operation epoch'), 'participation_role':('w.role','owned actor/operation participation role for this pair'), 'action_posture':('w.posture','distinct proposed/attempted/completed/rejected/failed operation posture')},
 'K30': {'action_receipt_ref':('w.receipt','exact attributable action/output/frame production receipt'), 'production_role':('w.role','owned action-output production role'), 'output_posture':('w.posture','actual recorded output posture; planned output does not qualify as produced')},
 'K31': {'profile_version_ref':('w.profile','exact configuring Agent Profile revision'), 'binding_ref':('w.binding','owned profile configuration record; separate from generic classification')},
 'K32': {'realization_role':('w.role','implemented-capability or executed-design evidence constructor for the exact pair'), 'exact_target_version_ref':('w.target','exact realized capability/design revision')},
 'K33': {'context_version_ref':('w.context','exact requested Context revision, consistent with the source context reference')},
 'K34': {'response_role':('w.role','owned intended response-to-occurrence/incident role'), 'intended_outcome':('w.objective','versioned declared response objective; no observed recovery result')},
 'K35': {'authority_role':('w.role','declared claim/boundary role over this decision scope or role assignment'), 'scope_ref':('w.scope','explicit owned declared authority scope; inclusion is not permission')},
 'K36': {'succession_effect':('w.effect','continues or supersedes declaration; replacement additionally needs a qualified transition')},
 'K37': {'hypothesis_version_ref':('w.hypothesis','exact Hypothesis revision targeted by the owned protocol'), 'test_role':('w.role','owned experimental design test role; no execution or polarity')},
 'K38': {'usage_role':('w.role','owned method dependency/employment constructor, preserving specification/implementation distinction')},
 'K39': {'tool_version_ref':('w.tool','exact Tool or Implementation revision'), 'invocation_contract_ref':('w.contract','exact subject/tool/frame invocation contract'), 'use_role':('w.role','owned dependency/proposed-use/invocation constructor with witnessed posture when invoked')},
 'K40': {'boundary_version_ref':('w.boundary','exact Contract/Policy/Schema/Challenge Contract boundary revision'), 'evidence_posture':('w.posture','admissible exact non-satisfaction evidence posture; unknown/conflict cannot establish violation')},
}

EXTENSIONS = [
 ('E00','Condition expressions','Conditions use yes/no/unknown with strong Kleene conjunction, disjunction and negation. Yes activates a norm, no deactivates it, unknown retains a potential obligation. Conflict is a separate diagnostic state. No activation result supplies an authorization root.', ['K00','K21','K23'], 'Define exact AST grammar, typed environment lookup, truth tables, total evaluation and norm-origin preservation; prove source/environment refinement.'),
 ('E01','Multiple evidence references','Resolve exact bounded evidence references under the chosen profile. Duplicate normalized references count once under the proposed successor set policy. For a criterion, admissible positive only gives yes, negative only no, neither unknown, and both conflict. Unaccepted action/output evidence is inadmissible. Legacy any-positive F0 remains separately versioned.', ['K03','K10','K18','K20','K40'], 'Freeze reference normalization, limits and policy selection; prove criterion verdicts, duplicate invariance, exact joins and legacy compatibility.'),
 ('E02','Redelegation','A child use is permitted only within the intersection of all complete independently established ancestor envelopes, gates, windows and unrevoked observations in one domain. Cyclic ancestry is invalid. Missing ancestry is unknown. Child declarations cannot enlarge the root grant.', ['K00','K35'], 'Specify chain derivation and completeness, lawful scope inclusion, time intersections, cycle diagnostics and authentic grant/revocation providers; prove no privilege amplification.'),
 ('E03','Fulfillment','The owned exact requirement derivation, rather than a caller-supplied criterion list, determines the complete set. All active mandatory criteria must be yes; potential or conflicting mandatory criteria prevent completion. An empty set is allowed only if the owned derivation yields it. Request fulfillment checks selectors, exclusions, freshness at resolution, budget and output constraints.', ['K10','K20','K23','K33'], 'Build pair-specific criterion derivations and an explicit request/E03 bridge; prove completeness, selection and evidence admissibility under the pinned policy.'),
 ('E04','Lifecycle','Every historical relation keeps its original exact witness and frame. Ending, replacement and expiration affect live eligibility through exact qualified transitions; they never rewrite prior history. Continues does not replace. Norm origins and conflicts survive projection. Recursive positive rules use least-fixed-point closure, so an unseeded cycle derives no starting fact.', ['K06','K21','K23','K26','K36'], 'Define historical/live projections, ending targets and revision applicability; prove monotonic positive closure and preservation, then specify any nonmonotone live-state selection separately.'),
 ('E05','Checked IR','A typed intermediate representation binds the exact selected definition/policy revision, all references, source digests, normalized qualifier values, frame, criterion derivations and evidence. It contains no executable effect authority. Bounded verification rejects unsupported variants and stale commitments; a well-typed IR is not proof of raw source authenticity.', ['K08','K10','K14','K20','K25'], 'Specify closed IR grammar and resource limits; prove decode/type/source interpretation bridges and replay correspondence for all implemented constructors.'),
 ('E06','Independent checker','An independently implemented checker validates the supported proof/certificate language against the exact theory, sources and resource profile. Same-toolchain replay is reproduction, not independent verification. Capability coverage is explicit; unsupported proof constructs remain unsupported, never implicitly accepted.', ['K00','K04','K10','K20','K25','K40'], 'Finish N11A substantial core/semantic sample and N11B required coverage; document separate implementation trust assumptions and replay disagreements.'),
]


def branch_interpretation(unit, pair):
    s, t = pair['source_kind'], pair['target_kind']
    special = {
      'K03': f'{s} impact observation on {t}: affected-subject role; source occurrence and incident provenance remain distinct',
      'K07': f'{t}-binding constructor; implementation.model must resolve this {t} revision',
      'K09': f'Challenge Contract admits a challenge against {t} in this mode; only that exact revision is targeted',
      'K10': {'contract':'inherited contract norm criteria for the Capability Instance', 'governed-model':'governed-model conformance criteria for the Capability Instance', 'context-profile':'exact Context projection and Context Profile criterion interpretation'}.get(t),
      'K11': f'{t} content commitment and its own cursor/extent interpretation; session consumption receipt',
      'K16': 'proposedAnswer constructor' if s == 'finding' else f'activityAddressing constructor for {s}',
      'K17': f'{s} assessment target projection for {t}; explicit subject, scope, role and purpose without outcome',
      'K18': f'{s} evidential correspondence to the uniquely selected proposition in {t}; polarity is independent of truth',
      'K21': f'{t} applicability constructor and complete norm origins for {s}',
      'K24': f'classificationFor({s},{t}); bind this exact subject to this exact parent using the pair-specific assignment',
      'K25': f'approved deterministic {t} consequence in a verified applied Admission Transaction; final-state commitment',
      'K26': f'membershipFor({s},{t}); owner-maintained {t} container includes {s} in its exact role',
      'K27': f'observed Failure Occurrence inside the exact {t} execution window and time domain',
      'K29': f'{s} attribution to {t} through its exact active session; preserve operation-specific recorded posture',
      'K30': f'actual {t} output bytes/revision joined to Agent Action and exact attributable production receipt',
      'K32': 'implementedCapability constructor with implementation evidence' if s=='implementation' else 'executedDesign constructor with experiment execution evidence',
      'K35': f'{s} declared authority boundary over {t}; explicit scope inclusion is separate from a grant',
      'K36': f'directional same-kind {s} succession declaration; preserve identities, continues/supersedes and history',
      'K38': f'{s} method specification dependency/employment record; method identity is separate from implementation',
      'K39': f'{s} dependency/proposal/invocation of {t} under the exact invocation contract',
      'K40': f'owned {t} boundary test with exact admissible non-satisfaction evidence',
    }
    return special.get(unit) or f'{s} to {t}: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog'


def endpoint_schema(kind):
    path = ROOT/'authority/artifact-types'/kind/'v1/schema.json'
    if kind == 'method':
        path = ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0011-method-carrier/artifact-types/method/v1/schema.json'
    return path


def schema_inventory(path):
    if not path.exists():
        return {'status':'source-schema-not-found', 'expected_path':str(path.relative_to(ROOT))}
    schema = read(path)
    fields = []
    def visit(value, pointer):
        if not isinstance(value,dict): return
        for name, shape in value.get('properties',{}).items():
            p = pointer+'/properties/'+name
            fields.append({'pointer':p, 'name':name, 'type':shape.get('type'), 'required':name in value.get('required',[]), 'constraints':{k:v for k,v in shape.items() if k in ['const','enum','minLength','pattern','minItems','maxItems','uniqueItems']}})
        # Include fields in anyOf/oneOf and if/then/else branches as well as
        # ordinary properties, items and $defs. Requiredness above is local to
        # this object branch, not an evaluation of the whole conditional schema.
        for name,child in value.items():
            escaped=name.replace('~','~0').replace('/','~1')
            child_pointer=pointer+'/'+escaped
            if isinstance(child,dict): visit(child,child_pointer)
            elif isinstance(child,list):
                for i,item in enumerate(child):
                    if isinstance(item,dict): visit(item,child_pointer+f'/{i}')
    visit(schema,'')
    return {'status':'inventoried-not-refined', 'source':binding(path), 'fields':fields, 'schema_interpretation_proved':False}


def build():
    # Generating a new proposal must not erase a later human assessment or edits
    # to the response worksheet. Accepted/revised review evidence needs a new
    # versioned package, rather than rerunning this historical generator.
    if (HERE/'review-manifest.json').exists():
        assert read(HERE/'review-manifest.json')['actual_batch_response'] is None, 'Create a new revision; this batch has an actual response.'
    if (HERE/'review-response-template.json').exists():
        worksheet=read(HERE/'review-response-template.json')
        assert worksheet['actual_user_response'] is None and all(v is None for key in ['kind_assessments','policy_assessments','extension_bridge_assessments'] for v in worksheet[key].values()), 'Preserve reviewed worksheet; create a new revision.'
    loader = importlib.util.spec_from_file_location('original_definition_specs',SUCCESSOR/'definition_specs.py')
    module = importlib.util.module_from_spec(loader); loader.loader.exec_module(module)
    definitions = [read(p) for p in sorted((SUCCESSOR/'definitions').glob('*.json'))]
    assert [d['unit'] for d in definitions] == [f'K{i:02}' for i in range(41)] == sorted(SPECS)
    plan = read(SUCCESSOR/'execution/plan.json')
    inventory = read(ROOT/plan['source_obligation_inventory']['path'])
    source_kinds = sorted({p[side] for d in definitions for p in d['ordered_pairs'] for side in ['source_kind','target_kind']})
    assert len(source_kinds)==109
    schema_rows = {kind:schema_inventory(endpoint_schema(kind)) for kind in source_kinds}
    write(HERE/'source-field-inventory.json',{'revision':REVISION,'node_kinds':109,'schemas':schema_rows,'purpose':'Exact available endpoint-schema property-occurrence inventory, including conditional branches and definitions. Requiredness is local to each object schema branch, not a complete conditional interpretation or field-to-meaning refinement theorem.'})
    source_inventory_binding = binding(HERE/'source-field-inventory.json')
    rows, obligations, branches = [], [], []
    for old in definitions:
        unit = old['unit']; kind = old['kind'].removeprefix('relation.')
        intuition, formula, fields, correction, gap = SPECS[unit]
        assert set(QUALIFIERS[unit]) == {q['field'] for q in old['qualifiers']}
        qualifiers = []
        for q in old['qualifiers']:
            role, interpretation = QUALIFIERS[unit][q['field']]
            qualifiers.append({**q,'exact_role':role,'interpretation':interpretation,
                'catalog_key':['relation_kind','source_kind','target_kind','field','catalog_revision'],
                'success_condition':'Unique typed resolution under the exact frame; the resolved value equals its role in the independent witness and every meaning condition holds.',
                'unresolved_result':'unknown; ambiguous, wrong-kind or unsupported catalog entries cannot establish this meaning',
                'raw_mapping_status':'specified; full original-source refinement unproved'})
        if unit in {'K10','K14','K25'}:
            typed_types={'conformance_scope':'OwnedScopeRevisionRef','exact_version_ref':'ExactRevisionRef','conformance_evidence_refs':'BoundedEvidenceReferenceCollection','effect_kind':'DeclaredGovernanceEffectCode','exact_target_version_ref':'ExactRevisionRef','application_receipt_ref':'VerifiedAppliedReceiptRevisionRef','consequence_role':'ApprovedBundleConsequenceRole','output_digest':'FinalOutputContentCommitment'}
            for q in qualifiers:
                q['prior_interpretation_type']=q['type']
                q['type']=typed_types[q['field']]
        branch_rows = []
        for j,pair in enumerate(old['ordered_pairs']):
            branch_rows.append({'id':f'{unit}:branch:{j:03}', 'unit':unit, **pair,
              'interpretation':branch_interpretation(unit,pair),
              'meaning_revision':REVISION,'qualifier_catalog_key':[old['kind'],pair['source_kind'],pair['target_kind']],
              'source_schema':schema_rows[pair['source_kind']].get('source'),
              'target_schema':schema_rows[pair['target_kind']].get('source'),
              'proof_target':f'WF(W) ∧ OwnedSourceMapping_{unit}_{j}(raw,W,f) → (DecodedMeaning_{unit}_{j}(raw,W,f) ↔ Meaning_{unit}(W,e,f))',
              'source_mapping_implemented':False,'refinement_proved':False})
        branches.extend(branch_rows)
        conclusions = []
        for c in old['forbidden_conclusions']:
            conclusions.append({**c,
              'theorem_target':f'∃ W,e,f. WF(W) ∧ Meaning_{unit}(W,e,f) ∧ ¬ {c["predicate"]}(W,anchors_{unit}(e,f))',
              'proof_status':'unproved for the complete pinned original source/composed theory',
              'positive_coexistence_allowed':True,
              'interpretation_note':'Non-entailment means the relation alone is insufficient; independent evidence may establish this conclusion in another valid world. Extra witnesses range over the independently supplied owned catalogs, never over asserted truth flags.'})
        ass = N01/'assessments'/f'{unit}.json'
        assessment = binding(ass) if ass.exists() else None
        proposed = {**old,'schema':'relational.batch-proposed-meaning/v1','revision':REVISION,
          'status':'proposed-for-consolidated-review','prior_definition':binding(SUCCESSOR/'definitions'/f'{unit}-{kind}.json'),
          'prior_actual_meaning_assessment':assessment,'actual_owner_review':None,
          'approval_scope_note':'The prior receipt, if present, retains its exact earlier scope. It does not accept this expanded batch revision, global policies or proofs.',
          'formal_expression':f'Meaning_{unit}(W,e,f) := ∃ w ∈ W.{old["independent_meaning"]["primary_record_type"]}. Base_{unit}(W,e,f,w) ∧ ({formula})',
          'notation':{'W':'independently supplied typed semantic world, exact captured bodies and owner catalogs; not checker output','e':'candidate edge with kind, exact source s, exact target t and closed raw qualifiers q','f':'complete exact evaluation frame and selected meaning/evidence/digest/catalog profiles','s':'e.source exact revision','t':'e.target exact revision','q':'e.qualifiers; precisely the required fields listed below','w':'independent normalized primary witness record, with the following typed roles','witness_fields':fields,'special_atoms':{name:meaning for name,meaning in ATOMS.items() if name+'(' in formula}},
          'base_definition':'Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.',
          'plain_language_intuition':{'normative':False,'text':intuition},
          'qualifiers':qualifiers,'forbidden_conclusions':conclusions,
          'operational_interpretation':{**old['operational_effect'],'precondition':f'Meaning_{unit}(W,e,f)','record_postcondition':'R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.', 'meaning_world_preserved':'W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.', 'composed_closure_status':'Full-rule/composed-state preservation remains a separate theorem target; append-only local behavior does not prove it.'},
          'worked_cases':{'positive':old['satisfiability_blueprint']['instance'],'insufficient':old['worked_failure'],'correction':correction,'examples_are_synthetic':True,'full_source_model_checked':False},
          'source_refinement_gap':gap,'branch_matrix':branch_rows,
          'theorem_targets':{'satisfiable':f'∃ W,e,f. WF(W) ∧ Meaning_{unit}(W,e,f)',
            'checker_soundness':f'WF(W) ∧ CompleteOwnedInputs(W,e,f) ∧ check_{unit}(W,e,f)=qualified → Meaning_{unit}(W,e,f)',
            'checker_completeness':f'WF(W) ∧ CompleteOwnedInputs(W,e,f) ∧ Meaning_{unit}(W,e,f) → check_{unit}(W,e,f)=qualified',
            'qualifier_refinements':[q['id'] for q in qualifiers],
            'effect':old['operational_effect']['id'],
            'non_entailments':[c['id'] for c in conclusions],
            'assumption_note':'CompleteOwnedInputs and WF must be independently justified. These are proposed targets, not new theorem declarations or inherited discharges.'},
          'source_field_inventory':source_inventory_binding,'inherited_discharges':0}
        if unit in {'K10','K14','K25'}:
            original_semantics = ROOT/'craft/formalization/candidates/relational-theorem-checker/v1/formal/core/RelationalSemantics.lean'
            proposed['formal_expression'] = proposed['formal_expression'].replace(':= ', ':= f.profile = typedSuccessor ∧ ', 1)
            proposed['profile_contract'] = {
              'typed_successor':'The stronger independent Meaning here is available only in an explicitly selected typedSuccessor profile.',
              'legacy_predicate':'LegacyQualified_k(g,e) := e.kind = k ∧ Relational.InstanceValid(g,e)',
              'legacy_definition':binding(original_semantics),
              'legacy_claim_ceiling':'Exact original literal-token/accepted-assessment predicate. An accepted flag or nonempty literal remains supplied graph data; it is not authenticated source truth or actual application.',
              'bridge_obligation':'Preserve legacy acceptance in its separately named/profile-indexed API. Do not rename LegacyQualified as the stronger Meaning, or infer typed-successor evidence, enum restrictions, execution or criteria completion from legacy acceptance.',
              'equivalence_to_stronger_successor_claimed':False}
        path = HERE/'definitions'/f'{unit}-{kind}.json'; write(path,proposed)
        doc = HERE/'definitions'/f'{unit}-{kind}.md'
        lines = [f'# {unit} — {kind}', '', f'**Proposed revision:** `{REVISION}`. Claim tier: **{old["independent_meaning"]["claim_tier"]}**.', '',
          f'**Meaning in plain language.** {intuition}', '',
          f'**Question answered.** {old["source_question"]}', '',
          '**Formal definition.**', '', '```text', proposed['formal_expression'], '```', '',
          proposed['base_definition'], '',
          '**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a '+old['independent_meaning']['primary_record_type']+' record in W. None is inferred from a successful checker result.', '',
          '| Witness field | Meaning |','|---|---|']
        lines += [f'| `{field}` | {meaning} |' for field,meaning in fields.items()]
        for name,meaning in proposed['notation']['special_atoms'].items(): lines += ['',f'`{name}`: {meaning}']
        lines += ['', '**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.', '', '| Field | Independent role | Interpretation |','|---|---|---|']
        lines += [f'| `{q["field"]}` | `{q["exact_role"]}` | {q["interpretation"]} |' for q in qualifiers]
        lines += ['', '**Operational behavior.** '+old['operational_effect']['meaning'], '', proposed['operational_interpretation']['record_postcondition'], '', proposed['operational_interpretation']['meaning_world_preserved'], '',
          '**Worked example.** '+old['satisfiability_blueprint']['instance'], '', '**Insufficient case.** '+old['worked_failure'], '', '**Useful correction.** '+correction, '',
          '**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.', '', '| Conclusion | Independent definition | Original obligation |','|---|---|---|']
        lines += [f'| {c["label"]} | {c["definition"]} | `{c["id"]}` |' for c in conclusions]
        lines += ['', '**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.', '',
          '**Source and implementation gap.** '+gap, '',
          '**Review status.** '+('An earlier scoped meaning receipt exists. It remains bound to its original definition; this expansion is presented for batch review.' if assessment else 'This meaning has no actual owner assessment yet. It is ready for the final consolidated review.'), '',
          f'[Original source]({(ROOT/old["source"]["path"]).as_posix()}) · [Machine-readable definition]({path.as_posix()})', '',
          f'**Exact ordered pairs ({len(branch_rows)}).** These branches are specified, not proved.', '', '| Source kind | Target kind | Interpretation |','|---|---|---|']
        lines += [f'| {b["source_kind"]} | {b["target_kind"]} | {b["interpretation"]} |' for b in branch_rows]
        if proposed.get('profile_contract'):
            pc=proposed['profile_contract']
            lines += ['', '**Legacy profile boundary.** '+pc['legacy_claim_ceiling'], '', '`'+pc['legacy_predicate']+'`', '', pc['bridge_obligation'], '']
        doc.write_text('\n'.join(lines)+'\n')
        rows.append({'unit':unit,'kind':old['kind'],'definition':binding(path),'explanation':binding(doc),'signature_branch_count':len(branch_rows),'pending_ids':old['pending_ids'],'prior_actual_meaning_assessment':assessment,'batch_actual_assessment':None})
        for q in qualifiers:
            if q['id'] not in old['pending_ids']:
                continue  # Eight legacy qualifier meanings were already discharged.
            obligations.append({'id':q['id'],'unit':unit,'category':'qualifier','definition':binding(path),'target':f'For complete owned mapping, raw {q["field"]} resolves exactly to {q["exact_role"]}; prove soundness/completeness and all field/frame joins.', 'original_status':'pending','discharged':False})
        obligations.append({'id':old['operational_effect']['id'],'unit':unit,'category':'effect','definition':binding(path),'target':proposed['operational_interpretation'],'original_status':'pending','discharged':False})
        obligations += [{'id':c['id'],'unit':unit,'category':'forbidden','definition':binding(path),'target':c['theorem_target'],'independent_conclusion':{key:c[key] for key in ['predicate','parameter_types','definition','anchor','context_rule']},'original_status':'pending','discharged':False} for c in conclusions]
    assert len(obligations)==263 and {o['id'] for o in obligations}=={o['id'] for o in inventory['obligations']}
    assert len(branches)==550
    write(HERE/'obligation-targets.json',{'revision':REVISION,'source_inventory':plan['source_obligation_inventory'],'counts':{'qualifier':74,'effect':41,'forbidden':148},'rows':obligations,'discharged':0,'retained_original_discharged':90})
    write(HERE/'ordered-pair-matrix.json',{'revision':REVISION,'branch_count':550,'rows':branches,'complete_refinement_proofs':0})
    policies = [{**p,'proposed_choice':p['recommended'],'actual_assessment':None,'status':'proposed-for-consolidated-review'} for p in module.POLICIES]
    write(HERE/'shared-policies.json',{'revision':REVISION,'policies':policies,'new_global_acceptances':0})
    write(HERE/'extension-bridges.json',{'revision':REVISION,'extensions':[{'id':i,'name':name,'proposed_meaning':meaning,'affected_units':units,'completion_work':work,'actual_assessment':None} for i,name,meaning,units,work in EXTENSIONS],'implemented_by_this_package':False})
    write(HERE/'remediation-plan.json',{'revision':REVISION,'starts_with':'Independent typed formalization and source meaning before runtime adapters or inherited discharge.',
      'relation_work':[{'unit':d['unit'],'proposed_definition':rows[i]['definition'],'source_definition':d['source'],
        'remaining_work':SPECS[d['unit']][4],'candidate_formalization_task':'N01','full_refinement_and_discharge_task':'N02',
        'formalization_exit':'Independently satisfiable typed model; precise typed conclusion anchors; exact source denotation for every declared pair, with all assumptions explicit.',
        'proof_exit':'Exact qualifier/effect/non-entailment evidence under the agreed definition, complete pinned theory and required independent checking.',
        'runtime_adapter_task':'N12','actual_owner_assignment':None,'discharged':False} for i,d in enumerate(definitions)],
      'cross_cutting':[{'id':'legacy-profile-bridge','units':['K10','K14','K25'],'target_file':str((HERE/'FOUNDATIONS.md').relative_to(ROOT)),'work':'Preserve exact original F0 acceptance separately; prove explicit typed-successor profile selection and prevent stronger claim relabeling.'},
        {'id':'lesson-interval-and-source-join','units':['K04'],'target_file':str((N01/'formal/K04-draft/LessonUseCandidate.lean').relative_to(ROOT)),'work':'Prepare a new model revision reconciling inclusive synthetic intervals with D02 half-open policy, and an owned exact lesson-identifier mapping; retain earlier proof bytes.'},
        {'id':'shared-choices','units':[d['unit'] for d in definitions],'target_file':str((HERE/'shared-policies.json').relative_to(ROOT)),'work':'Collect actual consolidated choice assessments after all definitions are prepared; no assumed default acceptance.'}],
      'full_plan_tasks_unchanged':20,'inherited_pending_ids':263,'inherited_discharges':0})
    write(HERE/'index.json',{'schema':'relational.batch-definition-index/v1','revision':REVISION,'status':'ready-for-consolidated-review','units':rows,
      'counts':{'definitions':41,'qualifiers':82,'pending_qualifiers':74,'retained_legacy_qualifiers':8,'effects':41,'conclusions':148,'inherited_obligations':263,'ordered_pairs':550,'node_kinds':109,'policies':8,'extension_bridges':7},
      'source_review_manifest':binding(N01/'review-manifest.json'), 'definition_specs':binding(SUCCESSOR/'definition_specs.py'), 'generator':binding(Path(__file__)),
      'foundations':binding(HERE/'FOUNDATIONS.md'),'definition_schema':binding(HERE/'definition.schema.json'),'audit_driver':binding(HERE/'verify_batch.py'),
      'obligation_targets':binding(HERE/'obligation-targets.json'),'ordered_pair_matrix':binding(HERE/'ordered-pair-matrix.json'),'source_field_inventory':source_inventory_binding,
      'shared_policies':binding(HERE/'shared-policies.json'),'extension_bridges':binding(HERE/'extension-bridges.json'),
      'remediation_plan':binding(HERE/'remediation-plan.json'),
      'new_theorem_declarations':0,'inherited_discharges':0,'N01_accepted':False,'authority_effect':'none'})
    make_review(rows, policies, schema_rows)
    print(json.dumps({'definitions':len(rows),'obligations':len(obligations),'branches':len(branches),'new_proofs':0}))


def make_review(rows,policies,schemas):
    header = [
      '# All 41 relation definitions — consolidated review', '',
      'All definitions are now presented together. This proposal expands the earlier briefs with explicit independent formulas, typed witness roles, qualifier interpretations, record effects, examples, corrections, theorem targets and every exact ordered pair. Review changes or approval after considering the complete set.', '',
      'Your earlier K00–K03 meanings assessments remain preserved in their original scope. The expanded batch revision and shared policies have no new approval recorded. This package adds specifications, not proof discharges: all 263 inherited obligations remain pending and the 90 original discharges remain untouched.', '',
      '**Coverage:** 41 relations, all 82 qualifier fields (74 pending plus eight retained legacy meanings), 41 record effects, 148 independent conclusion definitions, 550 ordered pairs, eight shared policies and seven extension bridges.', '',
      f'[Common foundations, truth tables and legacy profile boundaries]({HERE/"FOUNDATIONS.md"})', '',
      '**How to review.** Start with the plain-language sentence in each row. Open a relation to inspect its exact conditions and examples. Mark a relation for revision if it requires too much evidence, permits too weak a claim, points in the wrong direction, or wrongly connects two concepts. Then review the shared choices and seven extension bridges. Mathematical validity and operational readiness have separate verification work.', '',
      '**Notation.** `W` is an independently supplied semantic world, `e` an exact candidate edge, `s`/`t` its endpoint revisions, `q` its raw qualifiers, `f` the pinned frame and `w` an independent witness record. An exact reference contains kind, identity, revision and a content commitment. Equality never follows from spelling similarity. `∃` means there is a witness; `∧` means all conditions must hold; `∨` means one stated constructor; `→` states a conditional requirement; `∈` means membership in an independently supplied set.', '',
      '**Common meaning.** Each relation requires one declared ordered pair, exact endpoint and witness joins, a closed qualifier object with unique typed interpretation, matching frame and provenance appropriate to its claim tier. Recording, as-of checking, actual local execution and observed external effects remain distinct claim tiers. A raw nonempty string or supplied Boolean cannot establish those stronger facts.', '',
      '**Unknown and conflict.** Missing/ambiguous inputs yield unknown. Conflicting admissible evidence is reported as conflict. A failed decoder is a refusal to establish the meaning, not a proof that an external fact is false. The checker cannot quietly strengthen a historical observation into live currentness.', '',
      '**Optional links and graph inference.** Defining a relation does not require every eligible endpoint to have that relation. In particular an inquiry needs no Improvement Target. Inverse, transitive or authority-propagating edges require explicit reviewed rules. Recursive positive rules have least-fixed-point semantics: `Review → Ready → Review` preserves an existing seed but produces nothing from an empty seed.', '',
      '| Unit | Relation | Meaning to assess | Pairs | Earlier meaning assessment |','|---|---|---|---:|---|']
    for row in rows:
        kind=row['kind'].removeprefix('relation.'); doc=ROOT/row['explanation']['path']
        header.append(f'| {row["unit"]} | [{kind}]({doc}) | {SPECS[row["unit"]][0]} | {row["signature_branch_count"]} | '+('Accepted earlier revision; batch expansion pending' if row['prior_actual_meaning_assessment'] else 'Pending batch review')+' |')
    header += ['', '## Shared policy choices', '', 'These are concrete proposals for review, rather than defaults that have been accepted on your behalf.', '']
    for policy in policies:
        header += [f'### {policy["id"]} — {policy["topic"]}', '', policy['proposed_choice'], '', '**Consequence:** '+policy['consequence'], '', '**Alternative:** '+policy['alternative'], '']
    header += ['## Seven extension definitions and their bridges', '']
    for i,name,meaning,units,work in EXTENSIONS:
        header += [f'### {i} — {name}', '',meaning,'','**Relation bridges:** '+', '.join(units)+'.', '', '**Implementation/proof work still required:** '+work,'']
    missing=[k for k,v in schemas.items() if v['status']=='source-schema-not-found']
    header += ['## Findings and limits to consider', '',
      '1. **Raw strings are not the proposed semantic values.** Original qualifier contracts often require only nonempty strings. These definitions require versioned owned reference/code maps. The exact token-to-role implementation and authenticity boundary remain unfinished.',
      '2. **The endpoint matrix is complete, its proof is not.** All 550 declared pairs are listed, including 100 challenge targets and 100 same-kind succession pairs. Pair-specific source mappings and source-refinement proofs still need implementation.',
      '3. **No full source countermodel is claimed.** The 148 forbidden conclusions have independent definitions and exact inherited IDs. Their full-theory non-entailment targets are specified; existing local synthetic models do not prove every composed source boundary.',
      '4. **Lesson-use draft and proposed time policy differ.** K04 synthetic code uses an inclusive end; D02 proposes a half-open end. Existing application/lesson fixture identifiers also disagree. Resolve these through a new versioned adapter and model; retain the old proof scope.',
      '5. **A proposition inside an artifact needs a selector.** K18 may target a finding, hypothesis or assessment containing multiple claims. An owned unique proposition selector is required; selecting a target artifact alone is insufficient.',
      '6. **Historical and live state differ.** Assignment, membership, scope and succession records need explicit as-of/live profiles. Recording a supersedes declaration cannot automatically update current state.',
      '7. **Origin, derivation and succession remain independent.** No inferred transformation, identity equality or replacement follows just from lineage. Cycles in positive inference cannot create facts; policy for self/cyclic succession declarations should be decided explicitly during review.',
      '8. **Profile compatibility matters.** K10, K14 and K25 retain their legacy F0 predicate separately as LegacyQualified. Their stronger new Meaning explicitly requires typedSuccessor. Typed scopes, evidence collections, receipts and consequences need explicit profile selection and compatibility proofs; the two claim strengths are not equated.',
      '9. **Local recording is a narrow effect.** Append/idempotence/conflict-refusal postconditions preserve the independent meaning world. Full inference closure, local atomic materialization and external observations still require separate proofs and providers.',
      '10. **Approval of meanings does not complete the full plan.** Owner assessment, satisfiability, exact source refinement, all inherited discharges, implementation, independent checking and composed measurements remain distinct exit criteria.', '',
      '**Endpoint source schema inventory:** '+(f'{len(missing)} of 109 kinds have no schema at the expected configured location: '+', '.join(missing)+'. Those mappings remain explicit gaps.' if missing else 'All 109 expected schema locations were found and inventoried; inventorying fields is not proof of their interpretation.'), '',
      '## Completion order after revisions or approval', '',
      '1. Incorporate requested changes into a new exact revision; record actual assessments against its manifest, retaining prior receipts.',
      '2. Formalize independently satisfiable typed worlds and all pair-specific source meanings. Repair K04 interval and source joins; justify all owned catalog/provenance assumptions.',
      '3. Implement and prove each of the 74 qualifier mappings, 41 operational effects and 148 full-theory non-entailments. Only exact evidence can discharge an inherited ID.',
      '4. Freeze the agreed schemas/APIs, then implement the seven extension bridges and all 41 adapters in the existing N02–N13 dependency order.',
      '5. Complete independent checking, composed limits/pilot and discharge audit, followed by the final N17 assessment and N18 readout.', '',
      '## Review response', '',
      'Use `Kxx: change …` for individual revisions and `Dxx: change …` for shared policies. You can approve the meanings as a batch, approve a selected subset, or request changes. An approval will assess the exact proposed meanings and expressly selected policy/bridge choices; it will not approve unproved theorems or operational release.', '',
      f'[All definitions and exact manifest]({HERE/"index.json"}) · [263 obligation targets]({HERE/"obligation-targets.json"}) · [550 ordered pairs]({HERE/"ordered-pair-matrix.json"}) · [109-kind source field inventory]({HERE/"source-field-inventory.json"})', '']
    (HERE/'REVIEW.md').write_text('\n'.join(header))
    write(HERE/'review-response-template.json',{'revision':REVISION,'kind_assessments':{r['unit']:None for r in rows},'policy_assessments':{p['id']:None for p in policies},'extension_bridge_assessments':{e[0]:None for e in EXTENSIONS},'actual_user_response':None,'instructions':'A blank field is unassessed. Record only an actual human response bound to this exact review manifest. No default acceptance.'})


if __name__=='__main__':
    build()
