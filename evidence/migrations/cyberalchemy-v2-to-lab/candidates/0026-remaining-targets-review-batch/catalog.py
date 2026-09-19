"""Explicit per-target contracts; no target is inferred from a name alone."""
# Field notation: text, list, id:<kind union>, ids:<kind union>, number, nonnegative, period.
TYPES = {
'intent': {'attributed_to':'id:person-reference|team','direction':'text','motivation':'text','constraints':'list','review_route':'text'},
'product': {'name':'text','purpose':'text','identity_boundary':'text','owner_route':'text'},
'product-thesis': {'product_ref':'id:product','audience':'text','problem':'text','value_proposition':'text','assumptions':'list','revision_criteria':'list'},
'product-capability': {'product_ref':'id:product','outcome':'text','acceptance_conditions':'list','exclusions':'list'},
'capability-realization-binding': {'capability_ref':'id:product-capability','realization_refs':'ids:implementation','contract':'list','limitations':'list'},
'project': {'name':'text','purpose':'text','identity_boundary':'text','owner_route':'text'},
'research-inquiry': {'project_ref':'id:project','question':'text','method_ref':'id:method','inclusions':'list','exclusions':'list','stop_conditions':'list'},
'research-run': {'inquiry_ref':'id:research-inquiry','method_ref':'id:method','period':'period','input_refs':'ids:evidence-set','output_refs':'ids:observation','receipt_ref':'id:receipt','limitations':'list'},
'finding': {'question_ref':'id:research-inquiry','evidence_ref':'id:evidence-set','statement':'text','counterevidence_refs':'ids0:evidence-set','limitations':'list'},
'experiment-design': {'project_ref':'id:project','question':'text','subject_ref':'id:product-capability','protocol_ref':'id:method','conditions':'list','variables':'list','measures':'ids:measurement-method','stop_conditions':'list'},
'experiment-run': {'design_ref':'id:experiment-design','period':'period','input_refs':'ids:evidence-set','observation_refs':'ids:observation','receipt_ref':'id:receipt','deviations':'list0'},
'observation': {'subject_ref':'id:product-capability','observed_at':'time','readout':'text','conditions':'list','observer_ref':'id:person-reference','evidence_ref':'id:evidence-set'},
'measurement-method': {'property':'text','unit':'text','procedure':'text','conditions':'list','uncertainty_rule':'text'},
'measurement-result': {'method_ref':'id:measurement-method','subject_ref':'id:product-capability','observed_at':'time','value':'number','uncertainty':'nonnegative','unit':'text','receipt_ref':'id:receipt'},
'ontology': {'name':'text','version':'text','concept_refs':'ids:definition','relation_ids':'list0','boundaries':'list'},
'context': {'purpose':'text','relevance':'list','profile_ref':'id:context-profile','identity_boundary':'text'},
'context-profile': {'allowed_anchor_kinds':'list','minimum_anchors':'nonnegative-int','maximum_anchors':'positive-int','identity_fields':'list','successor_rule':'text'},
'context-request': {'context_ref':'id:context','policy_ref':'id:policy','anchor_refs':'ids:product|project|product-capability','question':'text','budget':'positive-int'},
'context-view': {'request_ref':'id:context-request','selected_refs':'ids0:evidence-set|definition','residue_refs':'ids0:residue','selection_basis':'text'},
'model-instance-binding': {'parent_ref':'id:product-capability','instance_ref':'id:implementation','parent_authority_scope':'text','instance_authority_scope':'text','inherited_contract':'list','extension_scope':'list'},
'person-reference': {'local_label':'text','identity_scope':'text','minimization_basis':'text'},
'identity-claim': {'person_ref':'id:person-reference','asserted_identifier':'text','evidence_ref':'id:evidence-set','challenge_route':'text'},
'TEAM_PLACEHOLDER': {},
 'team': {'name':'text','purpose':'text','identity_boundary':'text','owner_route':'text'},
 'team-membership': {'person_ref':'id:person-reference','team_ref':'id:team','period':'period','membership_posture':'membership'},
 'role': {'name':'text','functions':'list','exclusions':'list','authority_boundary':'text'},
 'role-assignment': {'assignee_ref':'id:person-reference|team','role_ref':'id:role','period':'period','assignment_basis':'text'},
}
del TYPES['TEAM_PLACEHOLDER']
# Source kinds, target kinds; * permits any explicitly cataloged node, not a dangling reference.
RELATIONS = {
'belongs-to-product':('product-capability|product-thesis','product'), 'belongs-to-project':('research-inquiry|experiment-design|goal|work|evidence-set|capability-realization-binding','project'),
'originates-from':('*','source'), 'successor-of':('*','*'), 'supersedes':('*','*'), 'uses-method':('research-run|experiment-run','method'),
'derives-from':('*','*'), 'supports':('evidence-set|observation|measurement-result','finding|identity-claim|authority-claim|hypothesis'),
'contradicts':('evidence-set|observation|measurement-result','finding|identity-claim|authority-claim|hypothesis'),
'evaluates':('evaluation','*'), 'governed-by':('*','policy|constitution'), 'authorizes':('decision','effect'), 'adopts':('decision','*'),
'realizes':('implementation','product-capability'), 'instance-of':('implementation|product-capability','product-capability|product'),
'compiles-to':('*','generated-output'), 'binds-implementation':('implementation','ontology|schema'),
'frames':('context','*'), 'references-bounded-context':('context','bounded-context'), 'member-of':('person-reference','team'),
'assigned-role':('person-reference|team','role'), 'assigned-responsibility':('person-reference|team','responsibility'),
'represents-person':('person-reference','person'), 'identity-link':('person-reference','person-reference'), 'claims-authority-over':('authority-claim','*')}
# Explicit states and transitions. These are proposed profiles, not live lifecycle changes.
LIFECYCLES={
'architecture-pattern-promotion':(['candidate','reviewed','adopted'], [('candidate','reviewed'),('reviewed','adopted')]),
'ux-authority-promotion':(['candidate','evaluated','adopted'], [('candidate','evaluated'),('evaluated','adopted')]),
'authority-lifecycle':(['candidate','reviewed','admitted','withdrawn'], [('candidate','reviewed'),('reviewed','admitted'),('admitted','withdrawn')]),
'goal-lifecycle':(['proposed','active','satisfied','abandoned'], [('proposed','active'),('active','satisfied'),('active','abandoned')]),
'project-lifecycle':(['proposed','active','closed'], [('proposed','active'),('active','closed')]),
'product-thesis-lifecycle':(['draft','tested','adopted','superseded'], [('draft','tested'),('tested','adopted'),('adopted','superseded')]),
'context-lifecycle':(['candidate','active','superseded','retired'], [('candidate','active'),('active','superseded'),('active','retired')]),
'capability-lifecycle':(['proposed','specified','realized','retired'], [('proposed','specified'),('specified','realized'),('realized','retired')]),
'team-lifecycle':(['proposed','active','dissolved'], [('proposed','active'),('active','dissolved')])}
EVALUATIONS={
'ux-evidence-compatibility':['same_audience','same_task','same_environment','limitations_recorded'],
'gate-evaluation':['scope_matches','evidence_bound','criteria_pass','owner_route_present'],
'goal-evaluation':['same_goal_version','condition_met','evidence_bound','residue_recorded'],
'project-evaluation':['identity_preserved','goals_accounted','work_accounted','residue_recorded'],
'product-thesis-evaluation':['audience_matches','value_tested','counterevidence_recorded','revision_criteria_checked'],
'model-instance-binding-evaluation':['parent_exact','instance_exact','inherited_contract_preserved','authority_scopes_separate']}
POLICIES=['repository-layout-policy','source-selection-policy','authority-aware-navigation','challenge','retention','semantic-consistency','publication','cross-context-generalization','context-resolution','recursion']
DERIVED={
'definition-graph':(['definition'],['derives-from','successor-of','originates-from']),
'promotion-queue':(['gate','evaluation','decision'],['evaluates','adopts','authorizes']),
'source-index':(['source','source-admission'],['originates-from']),
'artifact-graph':(['*'],['*']),
'project-index':(['project'],['belongs-to-project']),
'capability-ontology':(['product','product-capability','capability-realization-binding','model-instance-binding','implementation','decision','evaluation'],['belongs-to-product','realizes','instance-of','adopts','evaluates']),
'team-roster':(['team','person-reference','team-membership','role','role-assignment'],['member-of','assigned-role'])}
LIMITS={
'artifact-type':'Candidate record and graph consistency only; references bind exact input files, but identity, ownership, observations and execution assertions are not authenticated. No record is admitted or executed.',
'profile':'Bounded pure evaluation of supplied inputs. Results are proposed review outcomes, not gate verdicts or permission. Authentication and actual effects remain outside this profile.',
'relation-kind':'Directed endpoint typing and graph closure only. Relation existence does not prove owner-local semantics, authority, identity equivalence or effect execution.',
'derived-surface':'Deterministic read-only projection of the exact supplied graph. Missing source data stays missing; generated rows grant no authority or completeness proof.'}
