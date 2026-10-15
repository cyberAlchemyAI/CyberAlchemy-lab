"""Compose a source-linked conceptual Lab map for the two local article editions."""
from pathlib import Path
from html import escape
import hashlib
import json
import re
import textwrap
from diagram_label_layout import arrange_labels
from lab_visual_language import CONCEPTS, ICONS as MODEL_ICONS, NODE_CONCEPTS, model_styles

ROOT = Path(__file__).resolve().parent
CAT = json.loads((ROOT / 'research/catalog.json').read_text())
READER = json.loads((ROOT / 'research/library-reader-copy.json').read_text())
REF = 'lab-reference-library.html'
NODES = {}

# Presentation families use the copied KEP palette. They classify the illustration only.
FAMILIES = {
    'purpose': dict(label='Purpose & work', color='#b94812', source_token='--orange', icon='compass'),
    'governance': dict(label='Governance', color='#bd1230', source_token='--ds-accent', icon='shield'),
    'records': dict(label='Records & contracts', color='#245eb0', source_token='--ds-focus', icon='file'),
    'knowledge': dict(label='Connected views', color='#087773', source_token='--teal', icon='network'),
    'agents': dict(label='Actors & agents', color='#5c55b8', source_token='--violet', icon='robot'),
    'evidence': dict(label='Evidence & research', color='#82520a', source_token='--ds-warning', icon='flask'),
    'learning': dict(label='Operational learning', color='#246440', source_token='--ds-success', icon='sprout'),
}

# Original line icons share a 24-unit grid, stroke weight and rounded joins.
ICONS = {
    'compass': '<circle cx="12" cy="12" r="9"/><path d="m16 8-2.5 5.5L8 16l2.5-5.5Z"/>',
    'target': '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
    'briefcase': '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V4h8v3M3 12c6 3 12 3 18 0M12 11v4"/>',
    'folder': '<path d="M3 7V5h7l2 3h9v12H3Z"/>',
    'hammer': '<path d="m14 4 6 6-3 3-6-6Zm-3 3-7 7 3 3 7-7M3 21l4-4"/>',
    'wrench': '<path d="M14 4a6 6 0 0 0-6 8L3 17a2.8 2.8 0 0 0 4 4l5-5a6 6 0 0 0 8-6l-4 3-4-4Z"/>',
    'book': '<path d="M12 6C8 3 5 3 2 4v15c4-1 7-1 10 1 3-2 6-2 10-1V4c-3-1-6-1-10 2Zm0 0v14"/>',
    'layers': '<path d="m12 3 10 5-10 5L2 8Zm-10 10 10 5 10-5M2 18l10 5 10-5"/>',
    'file': '<path d="M5 2h9l5 5v15H5ZM14 2v5h5M8 12h8M8 16h6"/>',
    'archive': '<path d="M3 3h18v5H3ZM5 8v13h14V8M9 12h6M10 16h4"/>',
    'shield': '<path d="m12 2 9 4v6c0 5-5 8-9 10-4-2-9-5-9-10V6Zm-4 10 3 3 5-6"/>',
    'fingerprint': '<path d="M4 13V9a8 8 0 0 1 16 0v4M8 17V9a4 4 0 0 1 8 0v8M12 8v13M4 17l-1 4M20 17l1 4"/>',
    'cycle': '<path d="M20 8a8 8 0 0 0-14-3L3 8m0-5v5h5M4 16a8 8 0 0 0 14 3l3-3m0 5v-5h-5"/>',
    'alert': '<path d="m12 3 10 18H2Zm0 6v5m0 3v1"/>',
    'link': '<path d="m10 7 2-2a5 5 0 0 1 7 7l-2 2M14 17l-2 2a5 5 0 0 1-7-7l2-2m1 6 8-8"/>',
    'sliders': '<path d="M3 6h18M3 12h18M3 18h18"/><circle cx="8" cy="6" r="2"/><circle cx="16" cy="12" r="2"/><circle cx="9" cy="18" r="2"/>',
    'check': '<circle cx="12" cy="12" r="9"/><path d="m7 12 3 3 7-7"/>',
    'stamp': '<path d="M8 4a4 4 0 0 1 8 0v2l-2 4v3h4l3 4H3l3-4h4v-3L8 6ZM4 21h16"/>',
    'network': '<circle cx="12" cy="4" r="2.5"/><circle cx="4" cy="19" r="2.5"/><circle cx="20" cy="19" r="2.5"/><path d="m11 7-6 9m8-9 6 9M7 19h10"/>',
    'eye': '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>',
    'filter': '<path d="M3 4h18l-7 8v7l-4 2V12Z"/>',
    'robot': '<rect x="4" y="6" width="16" height="15" rx="3"/><path d="M12 2v4M1 12h3m16 0h3M8 11v2m8-2v2M9 17h6"/>',
    'cpu': '<rect x="6" y="6" width="12" height="12" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 2v4m6-4v4M9 18v4m6-4v4M2 9h4m-4 6h4m12-6h4m-4 6h4"/>',
    'person': '<circle cx="12" cy="7" r="4"/><path d="M4 22v-3a8 8 0 0 1 16 0v3"/>',
    'key': '<circle cx="8" cy="8" r="5"/><path d="m12 12 9 9m-4-4 3-3m-6 0 3-3"/>',
    'clipboard': '<path d="M8 5H4v17h16V5h-4"/><rect x="8" y="2" width="8" height="5" rx="2"/><path d="M8 12h8M8 17h6"/>',
    'memory': '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 9h10M7 13h7M7 17h4"/>',
    'play': '<circle cx="12" cy="12" r="9"/><path d="m10 7 7 5-7 5Z"/>',
    'scan': '<path d="M8 3H3v5m13-5h5v5M3 16v5h5m8 0h5v-5M4 12h16"/>',
    'tags': '<path d="M3 3h8l10 10-8 8L3 11Z"/><circle cx="7" cy="7" r="1"/>',
    'flask': '<path d="M9 2h6M10 2v7L3 21h18L14 9V2M7 15h10"/>',
    'bulb': '<path d="M8 15a7 7 0 1 1 8 0v3H8Zm1 7h6M9 18h6M12 10v8"/>',
    'sprout': '<path d="M12 22V11C5 11 3 7 3 3c7 0 9 4 9 8 0-7 3-9 9-9 0 7-3 10-9 10"/>',
    'flag': '<path d="M5 22V3c5-4 9 4 15 0v12c-6 4-10-4-15 0"/>',
    'chart': '<path d="M3 3v18h18M7 16v-4m5 4V7m5 9v-7"/>',
    'history': '<path d="M3 10a9 9 0 1 1 2 8M3 4v6h6M12 7v6l4 2"/>',
    'cut': '<path d="M3 5h18M3 12h18M3 19h18M8 2v20M16 2v20"/>',
}

ICONS.update(MODEL_ICONS)

VISUAL_GROUPS = {
    'purpose': ['purpose','work-system','intent','resolution','product','capability','project','goal','realization','work','implementation'],
    'governance': ['governance','authority','provenance','lifecycle','challenge','policies','decision','admission','delegation'],
    'records': ['definitions','types','records','project-state','relation-kinds','subject','artifact','typed-relation','semantic-history','governance-history'],
    'knowledge': ['ontology-view','context-view','coordination','bounded-context','manifest','ontology-node','ontology-edge','cut'],
    'agents': ['agent-session','profile','actor','assignment','tool','instance','memory','action'],
    'evidence': ['evidence-system','evidence','work-assessment','observation','occurrence','mode','classification','failure-assessment','hypothesis','experiment-design','experiment-run','evaluation'],
    'learning': ['learning-system','lesson','application','lesson-assessment'],
}

NODE_ICONS = dict(
    purpose='compass', intent='compass', resolution='target', product='briefcase', capability='target', project='folder', goal='target',
    definitions='book', types='layers', records='file', governance='shield', authority='shield', provenance='fingerprint', lifecycle='cycle',
    challenge='alert', policies='sliders', decision='check', admission='stamp', evidence='flask', realization='link', work='hammer',
    implementation='wrench', coordination='filter', profile='sliders', actor='person', delegation='key', assignment='clipboard', tool='wrench',
    instance='cpu', memory='memory', action='play', observation='scan', occurrence='alert', mode='alert', classification='tags',
    hypothesis='bulb', lesson='bulb', application='flag', evaluation='chart', artifact='file', subject='file', manifest='clipboard', cut='cut')
NODE_ICONS.update({'work-system':'hammer','evidence-system':'flask','learning-system':'sprout','project-state':'archive',
    'ontology-view':'network','context-view':'filter','agent-session':'robot','relation-kinds':'link','work-assessment':'check',
    'bounded-context':'network','failure-assessment':'scan','experiment-design':'flask','experiment-run':'play','lesson-assessment':'chart',
    'typed-relation':'link','ontology-node':'network','ontology-edge':'link','semantic-history':'history','governance-history':'history'})


def node(key, title, subtitle, terms, role, example, boundary, chapter, kind='durable'):
    definitions = []
    for term in terms:
        matches = [d for d in CAT['definitions'] if d['term'] == term]
        if not matches:
            raise ValueError(f'Missing source definition: {term}')
        for d in matches:
            anchor = re.sub(r'[^a-z0-9]+', '-', d['identity'].lower()).strip('-')
            definitions.append({k: d[k] for k in ['term', 'ref', 'effective_status', 'source', 'sha256']})
            scope = READER['scope_labels_by_identity'].get(d['identity'])
            definitions[-1]['display_term'] = d['term'] + (' · ' + scope if scope else '')
            definitions[-1]['href'] = f'{REF}#def-{anchor}'
    NODES[key] = dict(id=key, title=title, subtitle=subtitle, definitions=definitions,
                      role=role, example=example, boundary=boundary, chapter=chapter, kind=kind)
    NODES[key]['family'] = next(f for f, members in VISUAL_GROUPS.items() if key in members)
    NODES[key]['icon'] = NODE_ICONS[key]
    NODES[key]['visual_role'] = NODE_CONCEPTS.get(key)


node('purpose', 'Purpose', 'Why the work matters', ['Intent', 'Product', 'Project'],
     'Purpose states why the work is needed and what it concerns. A product offers value over time; a project organizes a particular effort toward goals.',
     'Customers need complete exports. A project investigates missing rows in the customer platform.',
     'Product, project and intent are recorded separately.', 'purpose')
node('work-system', 'Work & implementation', 'Tasks and technical results', ['Goal', 'Work', 'Implementation', 'Capability Realization Binding'],
     'Work describes an activity, its expected result and its limits. A separate binding record identifies which implementation version is intended to provide a product capability.',
     'Revise batch retrieval in the export service, then assess the result.',
     'Building software, selecting it for use and showing that it works each need evidence.', 'purpose')
node('evidence-system', 'Evidence & evaluation', 'Observe, measure, compare', ['Evidence', 'Observation', 'Operational Observation', 'Measurement Method', 'Evaluation'],
     'Operational Observations record ordinary work; Observations record Research or Experiment Runs. Measurements use an identified method. Evaluation applies an exact profile to the subject and inputs, retaining every outcome and any blocked checks.',
     'Compare exported rows with the rows the inclusion rule requires.',
     'A success message may show that the program finished; it does not show that all required data arrived.', 'evidence')
node('learning-system', 'Operational learning', 'Advice, later use, results', ['Operational Learning Cycle', 'Operational Lesson', 'Lesson Application', 'Lesson Outcome Assessment'],
     'Experience can produce advice for stated conditions. Later work records whether it used that advice and checks whether the predicted benefit occurred.',
     'Try the proposed batch-boundary check on another export and examine missing or repeated rows.',
     'Saving a lesson preserves it. Demonstrating that it helps requires evidence from later use.', 'learning')
node('definitions', 'Definitions', 'What a term means', ['Definition'],
     'Definitions state what terms mean and what they include or exclude for a particular purpose. Records, rules and decisions refer to these meanings.',
     'Product Capability describes an outcome such as complete export, separately from the software that provides it.',
     'Meaning and required record format are separate questions.', 'records', 'authority')
node('types', 'Artifact types', 'Required record formats', ['Artifact Type', 'Schema'],
     'An Artifact Type sets requirements for records of a particular kind. Its schema specifies fields and constraints that tools can check.',
     'A capability record names its product, identity, owner and selected version.',
     'A record can meet the schema without having been accepted by its authorized owner.', 'records', 'authority')
node('records', 'Governed records', 'Saved, versioned records', ['Artifact', 'Typed Relation'],
     'An artifact is a saved, identifiable and versioned record. A Typed Relation records a permitted connection between specific versions of two things.',
     'Inspect the export-capability record, software revision and declared links between them.',
     'Each record and connection has its own source history and acceptance status.', 'records')
node('project-state', 'Project State', 'Knowledge saved outside agents', ['Project State', 'Project Semantic Event History', 'Project Governance Event History'],
     'Project State is the project’s saved records, definitions, decisions, evidence and connections. Histories preserve what changed and why changes were accepted.',
     'The accepted export revision and its evaluation remain available after the agent session closes.',
     'This state belongs to the project and its record owners. Included records retain their own standing; accepting the state does not automatically promote its sources. The two histories track their positions separately.', 'agent')
node('governance', 'Governance', 'Rules, origins and change', ['Authority', 'Provenance', 'Governance-Axis Independence Invariant'],
     'Governance organizes which meanings and rules apply, where information came from, and which states and changes are permitted.',
     'Inspect the export requirements, the version that produced the output and whether the fix was proposed, accepted or put into use.',
     'Acceptance, confidence in evidence and observed operation are separate facts.', 'governance', 'authority')
node('ontology-view', 'Ontology View', 'A selected connected model', ['Ontology View', 'Ontology Cut'],
     'An ontology organizes concepts, things and their relationships. An Ontology View selects part of that model for a purpose from a consistent recorded state, called an Ontology Cut.',
     'Show the export capability, selected software revision and related evaluations for this investigation.',
     'The view is generated from records and has use and refresh conditions. It does not replace those records.', 'records')
node('context-view', 'Context View', 'Information for this task', ['Context View', 'Context Request'],
     'A Context View contains information selected for a task request. It identifies sources and versions, exclusions, how the selection was made and when it needs refreshing.',
     'Prepare the export requirements, current software and relevant evidence for the investigation.',
     'A task view must be refreshed when its use conditions require it.', 'agent')
node('agent-session', 'Agent Session', 'One temporary working period', ['Agent Session', 'Agent Instance', 'Session Memory'],
     'A session brings one agent instance together with its task, prepared information, rules, permissions and resource limits. Its working memory lasts only for that session.',
     'Investigate the export with current project information and temporary notes.',
     'In the Lab model, ending a machine-agent session ends its instance and clears its working memory.', 'agent', 'ephemeral')

node('authority', 'Authority', 'Applicable meanings and permissions', ['Authority', 'Authority Surface', 'Authority Boundary'],
     'Authority determines which accepted definitions, record formats, connection rules and policies apply, and which effects an actor may authorize within stated limits.',
     'The export definition determines what counts as complete. Delegation states what the agent may do.',
     'Being technically able to act does not supply permission to act.', 'governance', 'authority')
node('provenance', 'Provenance', 'Where information came from', ['Provenance', 'Source', 'Traceability'],
     'Provenance traces a record or claim to its sources, versions, participants and transformations.',
     'Trace a missing-row finding to the input data, counting method, run and saved output.',
     'Knowing a source’s origin does not establish that it supports a particular conclusion.', 'evidence', 'authority')
node('lifecycle', 'Lifecycle tracks', 'States and permitted changes', ['Artifact Lifetime', 'Semantic Epoch', 'Representation Revision', 'Derived Refresh'],
     'Lifecycle rules define the states a thing may occupy and how it may change. A material meaning change needs owner selection of a successor Semantic Epoch. Representation Revisions preserve meaning with evidence; Derived Refreshes validate views from unchanged input under an exact generator binding.',
     'A code revision can be accepted before deployment. A session can end while the project continues.',
     'A change in one status does not automatically change the other statuses.', 'change', 'authority')
node('challenge', 'Challenge Contract', 'How to contest a revision', ['Challenge Contract', 'Challenge Event'],
     'A Challenge Contract states who may contest a particular revision, acceptable reasons and evidence, and who must respond. A Challenge Event records one challenge.',
     'Contest an export-completeness finding with evidence of missing required rows.',
     'A challenge does not automatically withdraw or suspend the record; the stated rules and authorization govern those effects.', 'change', 'authority')
node('relation-kinds', 'Relation kinds', 'Rules for allowed connections', ['Relation Kind', 'Typed Coupling Invariant', 'Typed Connection Extension Rule'],
     'A Relation Kind states one connection meaning and direction, an exact closed set of source–target kind pairs and required additional details. Extending that set requires an accepted successor contract; a different semantic question requires a distinct kind.',
     'The catalog permits an Experiment Run to evaluate a Product Capability.',
     'Arrows in this explanatory map do not create actual Typed Relation records.', 'records', 'authority')
node('policies', 'Policies & scope', 'Rules and limits on actions', ['Policy', 'Constitution', 'Decision Scope', 'Delegation'],
     'Policies supply requirements within their issuer’s scope. A constitution applies only after its exact version and scope are adopted and the subject matches its selectors. Decision scopes and delegations define what an accountable actor may authorize or do.',
     'Permit the agent to read selected records and propose a fix for this investigation.',
     'Identity, role and permission are recorded separately; a role name alone does not grant permission.', 'governance', 'authority')
node('subject', 'Thing being examined', 'A particular thing and version', ['Artifact', 'Authority Claim'],
     'A subject is the thing being examined: a definition, contract, record, connection or another declared kind. Governance identifies the specific thing and version concerned.',
     'Review proposed export-service revision 8, its exact contents and the changes being requested.',
     'Accepting a record format and accepting a particular record using it are separate decisions.', 'records')
node('evidence', 'Evidence', 'Material bearing on a claim', ['Evidence', 'Evidence Set', 'Finding'],
     'Evidence identifies the claim, thing and version examined, provenance, scope and freshness. An Evidence Set retains supporting material, counterevidence and gaps. Findings explain conclusions and limits.',
     'The saved row comparison supports the claim that this export omitted required rows.',
     'An unchanged evidence file, a supported conclusion and a healthy running service are different facts.', 'evidence')
node('decision', 'Decision', 'A recorded choice and its limits', ['Decision', 'Decision Bundle', 'Decision Checkpoint'],
     'A Decision records an accountable choice, its authority, targets and permitted effects. A Decision Bundle can bring distinct decisions into one review.',
     'The owner accepts the reviewed software revision and specified updates to project records.',
     'Sharing a review does not extend one decision’s scope to the others.', 'change', 'authority')
node('admission', 'Admission transaction', 'Save accepted changes together', ['Admission Transaction'],
     'Admission is formal acceptance for a stated purpose. An Admission Transaction applies the authorized record changes and their declared bookkeeping consequences together.',
     'Save the accepted software revision, connection records and updated Project State in one transaction.',
     'Acceptance of an implementation does not by itself authorize deployment or establish observed operation.', 'change')

node('intent', 'Intent', 'What is sought and under what limits', ['Intent'],
     'Intent records a desired outcome and its constraints.', 'Customers should be able to obtain every row the export rule requires.',
     'Later records identify the chosen response and implementation.', 'purpose')
node('resolution', 'Intent Resolution', 'Chosen response and success test', ['Intent Resolution'],
     'Intent Resolution records an authorized owner’s choice of how to address an intent and how success will be assessed.',
     'Choose an export-repair project and require a comparison against the required source rows.', 'Choosing a response does not establish that it has been delivered.', 'purpose')
node('product', 'Product', 'Value offered over time', ['Product', 'Product Thesis'],
     'A product identifies the value offered to participants and the outcomes its capabilities serve. A Product Thesis explains that value and for whom it matters.',
     'A customer platform offers reliable export of customer data.', 'The product retains its identity across particular projects.', 'purpose')
node('capability', 'Product Capability', 'An outcome the product enables', ['Product Capability'],
     'A Product Capability states an outcome the product should enable for identified consumers.',
     'Customers can retrieve their complete required data.', 'The outcome is distinct from the technology used to provide it.', 'purpose')
node('project', 'Project', 'One organized effort', ['Project'],
     'A project coordinates a stated body of work toward its purpose and goals.', 'Investigate and repair incomplete exports.',
     'The product may continue after this project closes.', 'purpose')
node('goal', 'Goal', 'The target for assessment', ['Goal'],
     'A goal records a target that directs work and provides criteria for assessing results.', 'No required rows are omitted under the selected comparison.',
     'The target, the work and the outcome assessment have separate records.', 'purpose')
node('coordination', 'Coordination Context', 'What the work concerns', ['Coordination Context', 'Context'],
     'A Coordination Context is a saved frame anchored to exactly one product, optionally one project and one primary goal. It identifies purpose, users of the information and source-selection rules.',
     'Coordinate the export investigation while preserving distinct billing and customer-data meanings.',
     'Material changes to Product, Project, Goal or purpose require a successor context identity. Refreshing its information does not redefine those anchors.', 'purpose')
node('realization', 'Realization binding', 'Linking capability to software', ['Capability Realization Binding'],
     'A Capability Realization Binding links specific capability and implementation versions, their roles, compatibility and adoption status.',
     'Identify running export-service revision 7 and keep proposed revision 8’s adoption status separate.', 'The link alone does not establish adoption, deployment or customer benefit.', 'purpose')
node('work', 'Work', 'An activity and expected result', ['Work'],
     'Work records an activity, what it concerns, why it is needed, its limits and lifecycle.', 'Investigate Northstar’s reported omission and prepare bounded evidence and a candidate response.',
     'Finishing the activity and meeting the goal require their own assessments.', 'purpose')
node('work-assessment', 'Outcome assessment', 'What the activity achieved', ['Work Outcome Assessment', 'Evaluation'],
     'An outcome assessment compares an observed result with the target and records uncertainty and unresolved work, called residue.',
     'The investigation identified 200 missing required identifiers; a remedy and wider impact remain unestablished.', 'Completion, meeting requirements and demonstrated benefit are separate conclusions.', 'evidence')
node('implementation', 'Implementation', 'The technical realization', ['Implementation', 'Conformance'],
     'An Implementation identifies a software or other technical realization. Conformance checks whether a specific version meets the applicable requirements under stated conditions.',
     'Proposed export-service revision 8 changes batch retrieval; its efficacy still needs assessment.', 'The presence of code does not establish that it is running.', 'purpose')
node('bounded-context', 'Bounded Context', 'Meaning within one domain area', ['Bounded Context', 'Context Map'],
     'A Bounded Context defines the meaning and ownership of a local model. A Context Map records how that model relates to others.',
     'Billing and data export may define eligibility differently; their relationship must be stated.', 'Using the same word in two models does not make its meanings interchangeable.', 'purpose')

node('profile', 'Agent Profile', 'Reusable behavior and stop rules', ['Agent Profile', 'Agent Capability'],
     'An Agent Profile specifies expected inputs, outputs, behavior, tools, evidence, escalation and stopping conditions.',
     'An export-investigator profile requires evidence before proposing a correction.', 'The profile does not create an agent instance or grant permission.', 'agent', 'authority')
node('actor', 'Actor & Principal', 'Who acts and who is accountable', ['Actor', 'Principal', 'Person', 'Role', 'Role Assignment'],
     'An Actor identifies who or what participates. A Principal is an identity recognized for authentication, authorization, ownership or accountability at a particular boundary.',
     'An authorized owner assigns the investigation to an identified machine-agent instance.', 'Identity and role labels do not establish permission beyond explicit grants.', 'agent', 'authority')
node('delegation', 'Delegation', 'Permission within stated limits', ['Delegation', 'Authority Boundary'],
     'Delegation records permission from an authorized owner or principal for specified actions, with limits, rules, revocation and review requirements.',
     'Permit selected reads and a fix proposal for this assignment.', 'Delegation does not transfer identity or ownership.', 'agent', 'authority')
node('assignment', 'Agent Assignment', 'The job and its constraints', ['Agent Assignment'],
     'An assignment identifies the work, inputs, accountability and constraints for a particular agent engagement.',
     'Investigate this incomplete export and prepare a finding supported by saved evidence.', 'The assigned job and the session performing it are separate records.', 'agent')
node('tool', 'Tool', 'Operations and their possible effects', ['Tool', 'Effect'],
     'A Tool exposes operations with stated inputs, outputs and possible effects. Session rules and permissions still apply to its use.',
     'Read an export file or prepare a proposed code change.', 'Having access to a tool does not authorize all of its possible effects.', 'agent')
node('instance', 'Agent Instance', 'One temporary machine worker', ['Agent Instance'],
     'An Agent Instance is one concrete agent, with its profile, implementation, capabilities, accountable principal and lifecycle identified.',
     'Create the machine-agent instance for this export investigation.', 'A machine-agent instance cannot outlive its session or continue across sessions.', 'agent', 'ephemeral')
node('memory', 'Session Memory', 'Temporary working information', ['Session Memory'],
     'Session Memory is working information owned by exactly one session.', 'Keep a tentative explanation for the missing rows and the next comparison to try.',
     'Working memory ends with the session. Information for future sessions must enter project records through the applicable process.', 'agent', 'ephemeral')
node('action', 'Agent Action', 'Who attempted which operation', ['Agent Action', 'Operational Observation'],
     'An Agent Action records an operation attributed to a particular session and its permitted scope. Outcomes can supply observations and evidence.',
     'Record who ran the comparison, which inputs it used and what it returned.', 'A saved action result can persist after the temporary working memory ends.', 'agent')

node('observation', 'Operational observation', 'A record of what happened', ['Operational Observation'],
     'An operational observation preserves what occurred during work, the thing examined, conditions and supporting evidence.', 'An export returned fewer required rows than the comparison expected.',
     'An observation records the event; an assessment interprets it.', 'learning')
node('occurrence', 'Failure Occurrence', 'One actual or suspected failure', ['Failure Occurrence'],
     'A Failure Occurrence records a particular actual or suspected deviation from a stated requirement.', 'This illustrative export omitted 200 required rows under the selected comparison.',
     'Recording a failure does not establish its cause or a reusable failure pattern.', 'learning')
node('mode', 'Failure Mode', 'A possible failure pattern', ['Failure Mode', 'Failure Control Binding'],
     'A Failure Mode describes a distinct way something can fail under stated conditions. A Failure Control Binding identifies measures intended to address it.',
     'Changing row order between requests can cause a batch-retrieval method to skip rows.', 'A possible failure pattern can be described before any occurrence is observed.', 'learning')
node('classification', 'Classification', 'Organize by declared categories', ['Classification', 'Classification Scheme', 'Classification Assignment'],
     'Classification assigns a particular version of a thing to values in a stated scheme. Separate categories can describe different facts, such as affected component and observed impact.',
     'Classify where the failure was observed and its impact while leaving the cause unresolved.', 'Classification does not establish cause or acceptance.', 'learning')
node('failure-assessment', 'Failure Assessment', 'Investigate cause and consequences', ['Failure Assessment', 'Incident'],
     'A Failure Assessment examines the occurrence, possible pattern, cause, impact, containment, recovery and uncertainty. An Incident coordinates a response when needed.',
     'The service has recovered, but the cause of the missing rows still needs evidence.', 'Recovery can coexist with unresolved causes and unfinished work.', 'learning')
node('hypothesis', 'Research & hypothesis', 'A question and testable explanation', ['Research Inquiry', 'Hypothesis'],
     'A Research Inquiry records an uncertainty. A Hypothesis states an explanation or prediction that evidence can support, revise or reject under stated conditions.',
     'Keeping row order stable will remove omissions caused by changes between batches.', 'A proposed explanation needs applicable evidence and review; stating it does not establish it.', 'learning')
node('experiment-design', 'Experiment Design', 'The planned comparison', ['Experiment Design'],
     'An Experiment Design states what will change, what will be measured and compared, the criteria and the limits of the test.',
     'Compare retrieving batches by row number and by a stable position marker while new rows are inserted.', 'The plan and each execution have separate records.', 'learning')
node('experiment-run', 'Experiment Run', 'One execution and its results', ['Experiment Run', 'Measurement Result'],
     'An Experiment Run records the selected plan, inputs, execution and measured outcomes.', 'Run the comparison on a recorded dataset and save both outputs.',
     'A run supports conclusions only within its recorded conditions.', 'learning')
node('lesson', 'Operational Lesson', 'Advice with conditions and a test', ['Operational Lesson'],
     'An Operational Lesson is versioned advice for later work. It records supporting evidence, when it applies, exclusions, predicted benefit and what would contradict the prediction.',
     'Check adjacent batches when row order can change between requests.', 'Saving advice preserves it. Changing a policy or permission requires its own authorized decision.', 'learning')
node('application', 'Lesson Application', 'What was used in later work', ['Lesson Application'],
     'A Lesson Application records use or deliberate non-use of a specific lesson version in later work.',
     'A later export investigation records which version of the batch-boundary lesson it used.', 'Showing advice, judging it relevant, using it and showing benefit are different facts.', 'learning')
node('lesson-assessment', 'Lesson outcome', 'Did the predicted benefit occur?', ['Lesson Outcome Assessment'],
     'A Lesson Outcome Assessment compares the predicted benefit and contradicting conditions with evidence from a particular application.', 'Did the later check detect missing rows before delivery? Record the comparison and its limits.',
     'Repetition and the agent’s own success claim do not alone establish improvement.', 'learning')
node('evaluation', 'Evaluation', 'Results compared with criteria', ['Evaluation', 'Evidence', 'Finding'],
     'Evaluation applies an exact profile to a specific subject and input state, records all outcomes and preserves checks that could not be evaluated.', 'The revised batch-retrieval method passed this comparison; other conditions remain untested.',
     'The result cannot exceed the profile’s coverage or create authority. Evidence may support or oppose a lesson within the conditions examined.', 'evidence')

node('artifact', 'Artifact instance', 'One identifiable, versioned record', ['Artifact'],
     'An artifact is a saved record with an identity, type and version. Its purpose, owner, origins, lifecycle and ways to validate it are explicit.',
     'The export-capability record at revision 1 is represented by a graph node.', 'The record keeps its identity outside the graph.', 'records')
node('typed-relation', 'Typed Relation', 'One permitted record connection', ['Typed Relation', 'Relation Kind'],
     'A Typed Relation is one connection between specific source and target versions under an accepted connection rule.', 'A particular experiment run evaluates a particular version of the export capability.',
     'The source connection and the graph edge representing it are separate records.', 'records')
node('manifest', 'Ontology Manifest', 'Which ontology and configuration', ['Ontology Manifest', 'Ontology'],
     'An Ontology Manifest records which ontology and configuration to use, including identity and profile choices.', 'Select the ontology and profile for representing export-related records.',
     'Configuration, the model’s meaning and an exported package have distinct roles.', 'records', 'authority')
node('ontology-node', 'Ontology Node', 'A graph point for one version', ['Ontology Node'],
     'An Ontology Node represents a particular thing and revision, with its meaning, sources and required details identified.', 'Represent the selected export-capability revision in a business graph.',
     'Showing a record in a graph does not grant its authority or prove its claims.', 'records')
node('ontology-edge', 'Ontology Edge', 'A graph connection with a rule', ['Ontology Edge'],
     'An Ontology Edge represents a specific Typed Relation or a connection declared within that particular ontology.', 'Show the experiment’s evaluates connection with the same versions and direction.',
     'Representing an existing connection and declaring an ontology-local connection follow their own rules.', 'records')
node('semantic-history', 'Semantic event history', 'Recorded changes to meaning', ['Semantic Event History'],
     'A semantic event history preserves resulting meaning-bearing states in order. Earlier entries are retained so state can be reconstructed under the selected rules.',
     'A change to an ontology node’s meaning creates a new recorded change event.', 'Snapshots and views are calculated from the history; they do not replace it as the reconstruction source.', 'change')
node('governance-history', 'Governance event history', 'Acceptance and challenge records', ['Governance Event History'],
     'Governance event history separately records acceptance, challenges and other governance observations, linked to the specific meaning-changing events they concern.',
     'Record the response to a challenge against the particular revision that was challenged.', 'The history records governance evidence; the applicable decisions retain their own authority.', 'change')
node('cut', 'Ontology Cut', 'One consistent recorded state', ['Ontology Cut'],
     'An Ontology Cut reconstructs an ontology at specific positions in its change and governance histories, with a digital fingerprint of the included events.', 'Select a consistent recorded ontology state for the export investigation.',
     'The cut is rebuilt from event histories. This explanatory map is not an executed cut.', 'records')


def at(key, col, row):
    return dict(node=key, x=30 + col * 280, y=65 + row * 185, width=220, height=104)


def edge(a, b, label, explanation, route=None):
    return dict(source=a, target=b, label=label, explanation=explanation, route=route,
                interpretation='explanatory role connection')


def view(key, title, question, summary, rows, edges, chapter, boundaries=None):
    return dict(id=key, title=title, question=question, summary=summary, chapter=chapter,
                placements=[at(n, c, r) for r, row in enumerate(rows) for c, n in enumerate(row)],
                edges=edges, boundaries=boundaries or [])


VIEWS = [
    view('overview', 'Whole Lab', 'How does the system fit together?',
         'A need directs work. Saved records preserve the result. Selected information prepares a temporary agent session, and evidence supports assessment and later learning.',
         [['purpose', 'work-system', 'evidence-system', 'learning-system'],
          ['definitions', 'types', 'records', 'project-state'],
          ['governance', 'ontology-view', 'context-view', 'agent-session']],
         [edge('purpose', 'work-system', 'directs', 'The chosen response to a need identifies goals and work with stated limits.'),
          edge('work-system', 'evidence-system', 'produces observations', 'Work results provide observations and measurements for assessment.'),
          edge('evidence-system', 'learning-system', 'supports', 'Assessed evidence can support advice for later work under stated conditions.'),
          edge('definitions', 'types', 'supplies meaning', 'Record-format requirements refer to defined meanings.'),
          edge('types', 'records', 'sets record format', 'Records use their selected type’s required format and constraints.'),
          edge('records', 'project-state', 'preserved in', 'Governed project records contribute to durable Project State.'),
          edge('governance', 'definitions', 'rules for acceptance', 'The applicable authority rules determine which definition versions are accepted for a purpose.'),
          edge('records', 'ontology-view', 'represented in a graph', 'Specific record versions and their connections can be represented as graph points and lines in a selected consistent view.', [[700,338],[700,385],[420,385],[420,435]]),
          edge('ontology-view', 'context-view', 'can inform', 'A selected graph view can contribute to the information prepared for a task. Each view has its own requirements.'),
          edge('context-view', 'agent-session', 'prepares', 'The session uses selected task information and its relevant connected model, with source versions identified.'),
          edge('project-state', 'context-view', 'supplies selected records', 'Saved Project State supplies records and source versions for the task’s selected information.', [[980,338],[980,395],[700,395],[700,435]]),
          edge('evidence-system', 'records', 'recorded as', 'Evidence and assessments are saved records with their conditions and sources identified.'),
          edge('agent-session', 'work-system', 'performs the task', 'The agent performs the assigned work within its permissions and rules.', [[1090,479],[1130,479],[1130,25],[420,25],[420,65]])], 'purpose'),
    view('governance', 'Governance', 'What governs meaning, evidence and change?',
         'Examine which rules apply, where information came from and how it may change. Definitions, formats, policies and decisions have distinct roles.',
         [['authority','provenance','lifecycle','challenge'], ['definitions','types','relation-kinds','policies'], ['subject','evidence','decision','admission']],
         [edge('authority','definitions','meaning','The applicable accepted definitions determine what the terms mean for this purpose.'),
          edge('authority','types','record format','The selected Artifact Type sets the required record format.', [[140,153],[140,195],[420,195],[420,250]]),
          edge('authority','relation-kinds','connection rules','Connection rules state meaning, direction, allowed record kinds and required additional details.', [[140,153],[140,182],[700,182],[700,250]]),
          edge('authority','policies','applicable rules','Policies, constitutions and permissions limit actions and their effects.', [[140,153],[140,169],[980,169],[980,250]]),
          edge('provenance','evidence','traces support','Evidence can be followed to its selected sources and transformations.', [[420,153],[420,210],[285,210],[285,395],[420,395],[420,435]]),
          edge('lifecycle','decision','limits changes','Lifecycle rules state which changes are permitted. Authorized decisions select the specific changes requested.', [[700,153],[700,195],[845,195],[845,395],[700,395],[700,435]]),
          edge('lifecycle','subject','separate states','The thing examined has separate domain, acceptance, format and operation states.', [[700,65],[700,38],[10,38],[10,479],[30,479]]),
          edge('challenge','policies','response rules','Challenge rules state acceptable reasons, required evidence and who must respond.'),
          edge('definitions','subject','defines meaning','The thing examined refers to the selected definition for its meaning.'),
          edge('types','subject','checks the format','The record-format requirements specify fields and constraints for the thing being examined.', [[310,294],[275,294],[275,410],[140,410],[140,435]]),
          edge('relation-kinds','subject','governs connections','The rule states which kinds of records may connect, in which direction, and with which details.', [[700,338],[700,365],[15,365],[15,479],[30,479]]),
          edge('policies','admission','limits changes','Applicable rules and authority limits constrain the changes the transaction may apply.'),
          edge('evidence','subject','supports a claim','Evidence supports a claim about the particular thing and version, within stated conditions.'),
          edge('evidence','decision','supports review','Evidence can inform a decision. It does not grant permission to decide.'),
          edge('decision','admission','authorizes changes','The transaction applies only the specific record changes and bookkeeping effects authorized by the decisions.')], 'governance'),
    view('purpose', 'Purpose & work', 'How does intent become something useful?',
         'Choose a response to a need and a success test. Record the product outcome, selected software and particular project effort separately.',
         [['intent','resolution','product','capability'], ['project','goal','coordination','realization'], ['work','work-assessment','implementation','bounded-context']],
         [edge('intent','resolution','owner resolves','An attributable selection names what will address the intent.'),
          edge('resolution','product','selects scope','The chosen response may address a product or one of the outcomes it offers.'),
          edge('product','capability','enables outcome','Each capability belongs to one product and states a consumer outcome.'),
          edge('resolution','project','coordinates work','The chosen project organizes the particular work required for the response.', [[420,153],[420,195],[140,195],[140,250]]),
          edge('project','goal','targets','Project work is directed toward declared goals.'),
          edge('project','work','organizes','Work belongs to the selected project coordination.'),
          edge('goal','work-assessment','assessed against','Work results are assessed against declared targets.'),
          edge('work','work-assessment','produces result','Assessment records what the work achieved and what remains unresolved.'),
          edge('capability','realization','selects an implementation','A separate binding record identifies the selected capability and implementation versions.'),
          edge('realization','implementation','names the version','The binding record identifies the specific implementation version and its adoption status.', [[980,338],[980,385],[700,385],[700,435]]),
          edge('work','implementation','builds or changes','The activity and the software or other technical result have separate records.', [[140,523],[140,570],[700,570],[700,523]]),
          edge('bounded-context','coordination','supplies domain meaning','The work’s coordination frame refers to domain models with their own meaning and owners.', [[980,435],[980,405],[700,405],[700,338]])], 'purpose'),
    view('agent', 'Agent session', 'How does an agent act and leave useful records?',
         'Saved Project State supplies selected task information and a connected model. A profile, assignment and permissions prepare one session. The machine instance and its working memory end with it.',
         [['project-state','ontology-view','context-view','profile'], ['actor','delegation','assignment','tool'], ['instance','agent-session','memory','action']],
         [edge('project-state','ontology-view','represented for a purpose','Selected project records and relationships can be represented in a graph for a stated purpose.'),
          edge('ontology-view','context-view','can inform','A selected graph view can contribute to the information prepared for a task. Each view has its own requirements.'),
          edge('context-view','assignment','task information','The assignment and its preparation identify which selected information the task needs.'),
          edge('actor','delegation','grants permission','An authorized owner or principal delegates permission within specified limits.'),
          edge('delegation','agent-session','limits actions','The session acts within its explicit permission and applicable rules.'),
          edge('assignment','agent-session','names the job','The session binds one assignment with inputs, budgets and stop conditions.', [[700,338],[700,385],[420,385],[420,435]]),
          edge('profile','instance','sets behavior rules','The concrete agent uses a selected behavior profile. The profile does not grant permission.', [[980,65],[980,25],[15,25],[15,479],[30,479]]),
          edge('instance','agent-session','one machine lifetime','The machine Instance cannot outlive or span Sessions.'),
          edge('agent-session','memory','owns','Temporary working state belongs to exactly this session.'),
          edge('agent-session','action','performs','Each action identifies the responsible session and the limits under which it acted.', [[420,523],[420,580],[980,580],[980,523]]),
          edge('action','tool','uses an operation','The action uses a tool whose possible effects and applicable permissions are stated.'),
          edge('action','project-state','saves evidence','Observations and results are saved as project records through the required process.', [[1090,479],[1130,479],[1130,10],[140,10],[140,65]])], 'agent',
         [dict(x=18,y=422,width=802,height=125,label='TEMPORARY · machine instance, session and working memory')]),
    view('learning', 'Learning', 'How can experience improve later work?',
         'Record what happened, examine possible failure patterns and test uncertain explanations. Advice for later work needs recorded use and an assessment of its benefit.',
         [['observation','occurrence','mode','classification'], ['failure-assessment','hypothesis','experiment-design','experiment-run'], ['lesson','application','lesson-assessment','evaluation']],
         [edge('observation','occurrence','may reveal a failure','An observation may support a record of a particular failure against a stated requirement.'),
          edge('occurrence','failure-assessment','assess','Assessment preserves cause, impact, recovery and uncertainty separately.', [[420,153],[420,195],[140,195],[140,250]]),
          edge('mode','failure-assessment','candidate pattern','The assessment checks whether evidence supports the reusable mode.', [[700,153],[700,210],[285,210],[285,294],[250,294]]),
          edge('classification','mode','organizes distinctions','A declared scheme organizes values and assignments; it establishes no cause.'),
          edge('failure-assessment','hypothesis','can open a question','Uncertain mechanisms can motivate a research inquiry and testable hypothesis.'),
          edge('hypothesis','experiment-design','testable claim','The design specifies conditions, comparison, measurement and acceptance criteria.'),
          edge('experiment-design','experiment-run','executed as','The run records one actual execution of the selected design.'),
          edge('experiment-run','evaluation','assess results','Evaluation states what the selected run supports under the declared criteria.'),
          edge('failure-assessment','lesson','can support advice','A lesson records evidence, use conditions, exclusions, expected benefit and what would contradict the prediction.'),
          edge('lesson','application','used later','The exact lesson revision’s use or deliberate non-use is recorded.'),
          edge('application','lesson-assessment','checks benefit','Compare the predicted benefit with evidence from this use, including results that would contradict it.'),
          edge('evaluation','lesson','can inform','Research evidence can support, revise or reject advice under the examined conditions.', [[980,523],[980,570],[140,570],[140,523]]),
          edge('lesson-assessment','lesson','revise or withdraw','Outcome evidence can motivate an explicitly governed lesson successor or withdrawal.', [[700,523],[700,610],[140,610],[140,523]])], 'learning'),
    view('ontology', 'Records & graph', 'How do records become a connected view?',
         'Graph points represent particular record versions. Connections represent existing relationships or declared local meanings. Separate histories supply a consistent recorded state for a selected graph view.',
         [['artifact','typed-relation','definitions','manifest'], ['ontology-node','ontology-edge','semantic-history','governance-history'], ['cut','ontology-view','context-view','project-state']],
         [edge('artifact','ontology-node','represented as','The source record and the graph point representing it remain separate.'),
          edge('typed-relation','ontology-edge','represented as','The graph connection preserves the specific relationship version, endpoints, required details and direction.'),
          edge('definitions','ontology-node','meaning binding','A represented subject binds to its applicable definition.', [[700,153],[700,195],[140,195],[140,250]]),
          edge('manifest','governance-history','selects the model','The selected ontology identity and configuration determine which representation and histories are used.'),
          edge('ontology-node','ontology-edge','exact endpoints','Each edge resolves its represented endpoint revisions.'),
          edge('ontology-edge','semantic-history','records meaning changes','The resulting meaning-bearing states of graph nodes and edges are preserved in recorded change events.'),
          edge('governance-history','semantic-history','links the same event','Governance records identify the exact meaning-changing event, its content fingerprint and its position in history.'),
          edge('semantic-history','cut','reconstructs state','Selected positions in the event history reconstruct one consistent meaning-bearing state.', [[700,338],[700,385],[140,385],[140,435]]),
          edge('governance-history','cut','adds matching governance','The cut combines compatible recorded positions from the change and governance histories.', [[980,338],[980,400],[275,400],[275,479],[250,479]]),
          edge('cut','ontology-view','selects for a purpose','The view selects relevant information from the consistent recorded state for an identified user or task.'),
          edge('ontology-view','context-view','can inform','A selected graph view can contribute to the information prepared for a task. Each view has its own requirements.'),
          edge('project-state','context-view','supplies selected records','Saved Project State supplies records and source versions for the task’s selected information.')], 'records'),
]

JOURNEY = [
    dict(node='purpose', title='1 · Open the incident response', text='Northstar reports missing records in a delivered export. The service owner opens an Incident to coordinate the response; investigation work belongs to the repair Project.'),
    dict(node='context-view', title='2 · Recover the governing scope', text='Prepare accepted definition 1.0.0, snapshot S1, account Northstar, filter status = active and output E12. View 3 records these sources and its use conditions.'),
    dict(node='agent-session', title='3 · Start the bounded investigation', text='Session 12 receives a Work Assignment and a separate 30-minute Delegation to inspect saved material, compare identifiers and prepare review material. It pauses if its permission or task view becomes unusable.'),
    dict(node='work-system', title='4 · Compare the actual identifiers', text='Method 2 compares the 10,000 required identifiers with output E12 and identifies 200 omissions. Export run 12 and investigation session 12 are distinct records. The cause remains unresolved.'),
    dict(node='evidence-system', title='5 · Preserve the assessment basis', text='Save exact sources and comparison in an Evidence Set for the Failure Assessment. Keep proposed code revision 8 candidate; its efficacy and the extent of impact need further assessment.'),
    dict(node='governance', title='6 · Review each requested effect', text='The authorized owner reviews exact records, versions and evidence. Accepting assessment material does not automatically activate code, establish recovery or close the incident.'),
    dict(node='project-state', title='7 · Save the authorized record changes', text='An authorized Admission Transaction saves the specified records and Project State. The incident record may remain active with an open response and candidate code. Ending the session clears its working memory.'),
    dict(node='learning-system', title='8 · Examine later lesson use', text='A proposed lesson may guide future work under its stated conditions. Advice about changing datasets does not establish a remedy for this fixed-snapshot incident. Record actual use and assess the predicted benefit.'),
]

# Governance uses short, separately laid out explanations instead of one crowded mesh.
GOVERNANCE = next(v for v in VIEWS if v['id'] == 'governance')
GOVERNANCE['edges'] += [
    edge('authority','subject','applicable rules','Examine the meanings, record formats, connection rules and permitted effects applicable to this particular thing.'),
    edge('provenance','subject','traces origins','Trace the particular record to its source files, versions and transformations.'),
    edge('subject','decision','review a proposed change','When a change is proposed, the accountable owner reviews the exact subject revision and requested effects.'),
    edge('challenge','subject','contests a revision','The challenge identifies the exact revision, reasons, evidence and required response process.'),
]


def gov_edge(source, target, route=None):
    original = next(e for e in GOVERNANCE['edges'] if e['source'] == source and e['target'] == target)
    return {**original, 'route': route}


def gov_focus(key, title, question, summary, positions, connections, headings):
    return dict(id='governance-'+key, focus_key=key, title=title, question=question, summary=summary,
                chapter='governance', placements=[dict(node=n,x=x,y=y,width=220,height=104) for n,x,y in positions],
                edges=connections, boundaries=[], display_labels=False, heading_labels=headings)


GOVERNANCE['focus_views'] = [
    gov_focus('overview','Governance overview','Three questions about the same thing',
              'Inspect applicable rules, information origins and current state. Choose a question to see its detail. Proposed changes require their own review and acceptance.',
              [('authority',110,80),('provenance',470,80),('lifecycle',830,80),('subject',470,330),('decision',300,535),('admission',650,535)],
              [gov_edge('authority','subject',[[220,168],[220,250],[530,250],[530,330]]),
               gov_edge('provenance','subject',[[580,168],[580,330]]),
               gov_edge('lifecycle','subject',[[940,168],[940,250],[630,250],[630,330]]),
               gov_edge('subject','decision',[[580,418],[580,470],[410,470],[410,535]]),
               gov_edge('decision','admission')],
              [(30,35,'INSPECT THE SAME SUBJECT'),(30,500,'WHEN A CHANGE IS PROPOSED')]),
    gov_focus('authority','Authority','Which definitions, formats and rules apply?',
              'Definitions specify meaning, Artifact Types specify record formats, Relation Kinds specify permitted connections, and policies limit actions and effects.',
              [('authority',470,75),('definitions',30,280),('types',310,280),('relation-kinds',590,280),('policies',870,280),('subject',310,520),('admission',870,520)],
              [gov_edge('authority','definitions',[[490,163],[490,210],[140,210],[140,280]]),
               gov_edge('authority','types',[[550,163],[550,240],[420,240],[420,280]]),
               gov_edge('authority','relation-kinds',[[610,163],[610,240],[700,240],[700,280]]),
               gov_edge('authority','policies',[[670,163],[670,210],[980,210],[980,280]]),
               gov_edge('definitions','subject',[[140,368],[140,470],[370,470],[370,520]]),
               gov_edge('types','subject',[[420,368],[420,520]]),
               gov_edge('relation-kinds','subject',[[700,368],[700,470],[470,470],[470,520]]),
               gov_edge('policies','admission')],
              [(30,35,'APPLICABLE MEANING, CONTRACTS AND RULES')]),
    gov_focus('provenance','Provenance','Where did this record or claim come from?',
              'Trace evidence to its source files and versions. Explain the conditions under which it supports a claim. Supporting evidence and permission to decide are separate facts.',
              [('provenance',470,75),('evidence',470,285),('subject',250,510),('decision',700,510)],
              [gov_edge('provenance','evidence',[[580,163],[580,285]]),
               gov_edge('evidence','subject',[[530,373],[530,440],[360,440],[360,510]]),
               gov_edge('evidence','decision',[[630,373],[630,440],[810,440],[810,510]])],
              [(30,35,'SOURCE LINEAGE AND CLAIM SUPPORT')]),
    gov_focus('lifecycle','Lifecycle','What state is this in, and how may it change?',
              'Acceptance status, domain state and operation have separate rules. Authorized decisions select changes; an Admission Transaction saves the accepted record changes together.',
              [('lifecycle',470,75),('subject',250,300),('decision',700,300),('admission',700,520)],
              [gov_edge('lifecycle','subject',[[530,163],[530,235],[360,235],[360,300]]),
               gov_edge('lifecycle','decision',[[630,163],[630,235],[810,235],[810,300]]),
               gov_edge('decision','admission',[[810,388],[810,520]])],
              [(30,35,'STATE TRACKS AND EXACT TRANSITIONS')]),
    gov_focus('challenges','Challenges','How can someone contest a particular revision?',
              'A Challenge Contract names what may be contested, acceptable reasons and who responds. Evidence supports the response. Changing acceptance status requires the applicable authorization.',
              [('challenge',250,75),('subject',700,75),('policies',250,300),('evidence',700,300),('admission',250,520),('decision',700,520)],
              [gov_edge('challenge','subject'),gov_edge('challenge','policies',[[360,163],[360,300]]),
               gov_edge('evidence','subject',[[810,300],[810,163]]),
               gov_edge('policies','admission',[[360,388],[360,520]]),
               gov_edge('evidence','decision',[[810,388],[810,520]]),gov_edge('decision','admission')],
              [(30,35,'CONTEST, ASSESS AND RESPOND')]),
]
GOVERNANCE['node_focus'] = {
    'authority':'authority','definitions':'authority','types':'authority','relation-kinds':'authority','policies':'authority',
    'provenance':'provenance','evidence':'provenance','lifecycle':'lifecycle','decision':'lifecycle','admission':'lifecycle',
    'challenge':'challenges','subject':'overview',
}
GOVERNANCE['presentation'] = 'Five focused diagrams. The overview shows six concepts and five role connections; labels move to the inspector. Selecting a concept reveals only its local connections.'

MODEL = dict(schema_version='lab-concept-explanation-map/v1', authority_effect='none',
             source_snapshot=CAT['captured_at'], catalog_sha256=hashlib.sha256((ROOT/'research/catalog.json').read_bytes()).hexdigest(),
             interpretation='Explanatory concept groups and role connections. Examples are hypothetical; no instance or relation is admitted.',
             nodes=NODES, views=VIEWS, journey=JOURNEY,
             visual_language=dict(families=FAMILIES, model_roles=CONCEPTS, icon_system='Original 24-unit line icons; consistent stroke and rounded joins.',
                                  color_meaning='Editorial concept families; admission and lifecycle remain separate.',
                                  lifetime_meaning='Dashed card outlines identify ephemeral Session state.'),
             evidence_boundary='Node definitions link to the captured Lab catalog. Grouping, layout and connection explanations are editorial synthesis; they report no graph execution or current liveness.',
             open_questions=['User review of the visual grouping and explanation density.', 'Additional specialist views can expand the same captured model without changing canonical definitions.'])
(ROOT/'research/system-map-model.json').write_text(json.dumps(MODEL, ensure_ascii=False, indent=2)+'\n')


def h(s):
    return escape(str(s), quote=True)


def svg(v):
    uid = 'smap-'+v['id']
    p = {n['node']: n for n in v['placements']}
    foundation = re.search(r':root\s*\{([^}]+)\}', (ROOT/'assets/kep/design-system.css').read_text()).group(1)
    css=(ROOT/'assets/system-map.css').read_text()
    visual_css=css.split('/* Graph visual language: begin. */',1)[1].split('/* Graph visual language: end. */',1)[0]
    standalone_style = 'svg{'+foundation+'background:var(--ds-surface)}'+visual_css+model_styles('svg')
    markers=''.join(f'<marker id="{uid}-{family}-arrow" class="smap-family-{family}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z"/></marker>' for family in FAMILIES)
    markers+=''.join(f'<marker id="{uid}-{key}-arrow" data-model-concept="{key}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z"/></marker>' for key in CONCEPTS)
    content = [f'<svg xmlns="http://www.w3.org/2000/svg" class="smap-diagram" viewBox="0 0 1160 650" role="group" aria-labelledby="{uid}-title {uid}-desc">',
               f'<title id="{uid}-title">{h(v["title"])} · CyberAlchemy Lab concept map</title>',
               f'<desc id="{uid}-desc">{h(v["summary"])} Select a node for its role, example and connections. Arrows are explanatory role connections.</desc>',
               f'<defs>{markers}</defs>']
    for x,y,label in v.get('heading_labels',[]):
        content.append(f'<text class="smap-section-label" x="{x}" y="{y}">{h(label)}</text>')
    for b in v['boundaries']:
        content += [f'<rect class="smap-boundary" x="{b["x"]}" y="{b["y"]}" width="{b["width"]}" height="{b["height"]}" rx="4"/>',
                    f'<text class="smap-boundary-label" x="{b["x"]+10}" y="{b["y"]+b["height"]+19}">{h(b["label"])}</text>']
    for i, e in enumerate(v['edges']):
        a, b = p[e['source']], p[e['target']]
        route = e['route']
        if not route:
            if a['y'] == b['y']:
                route = [[a['x']+(a['width'] if a['x']<b['x'] else 0), a['y']+44],
                         [b['x']+(0 if a['x']<b['x'] else b['width']), b['y']+44]]
            else:
                route = [[a['x']+110, a['y']+(a['height'] if a['y']<b['y'] else 0)],
                         [b['x']+110, b['y']+(0 if a['y']<b['y'] else b['height'])]]
        d = 'M'+' L'.join(f'{x},{y}' for x,y in route)
        # Keep the existing caption density. Shared layout places the chosen
        # captions using all nodes, paths and previously placed labels.
        segments = list(zip(route,route[1:]))
        horizontal = [(a,b) for a,b in segments if a[1]==b[1]]
        longest=max((abs(a[0]-b[0]) for a,b in horizontal),default=0)
        label = e['label'] if v.get('display_labels',True) and (longest>180 or not horizontal) else ''
        family=NODES[e['source']]['family']
        concept=NODES[e['source']]['visual_role']
        visual_attr=f' data-model-concept="{concept}"' if concept else ''
        marker_key=concept or family
        content.append(f'<g class="smap-edge smap-family-{family}"{visual_attr} data-edge-index="{i}" data-source="{e["source"]}" data-target="{e["target"]}"><title>{h(e["explanation"])}</title><path class="smap-edge-path" d="{d}" marker-end="url(#{uid}-{marker_key}-arrow)"/>')
        if label:
            content.append(f'<text class="smap-edge-label" data-connection-label="true">{h(label)}</text>')
        content.append('</g>')
    for n in v['placements']:
        d=NODES[n['node']]
        lines=textwrap.wrap(d['title'],width=15 if d['id']=='governance-history' else 16,break_long_words=False,break_on_hyphens=False)
        title_y=n['y']+(34 if len(lines)==1 else 27)
        title=''.join(f'<tspan x="{n["x"]+56}" y="{title_y+j*20}">{h(line)} </tspan>' for j,line in enumerate(lines))
        sublines=textwrap.wrap(d['subtitle'],width=26,break_long_words=False,break_on_hyphens=False)
        subtitle=''.join(f'<tspan x="{n["x"]+14}" y="{n["y"]+75+j*16}">{h(line)}{(" " if j<len(sublines)-1 else "")}</tspan>' for j,line in enumerate(sublines))
        node_id=uid+'-'+d['id']
        icon=ICONS[d['icon']]
        concept=d['visual_role']
        visual_attr=f' data-model-concept="{concept}"' if concept else ''
        visual_label=CONCEPTS[concept]['label'] if concept else FAMILIES[d['family']]['label']
        content.append(f'<g class="smap-node smap-{d["kind"]} smap-family-{d["family"]}"{visual_attr} data-map-node="{d["id"]}" data-map-family="{d["family"]}" role="button" tabindex="0" aria-pressed="false" aria-labelledby="{node_id}-title {node_id}-subtitle" aria-describedby="{node_id}-description"><desc id="{node_id}-description">{h(visual_label)}. Show explanation.</desc><rect x="{n["x"]}" y="{n["y"]}" width="220" height="104" rx="5"/><path class="smap-node-rail" d="M{n["x"]+2},{n["y"]+8}V{n["y"]+96}"/><circle class="smap-node-icon-disc" cx="{n["x"]+29}" cy="{n["y"]+33}" r="17"/><g class="smap-glyph smap-node-glyph" transform="translate({n["x"]+17},{n["y"]+21})" aria-hidden="true">{icon}</g><text class="smap-node-title" id="{node_id}-title">{title}</text><text class="smap-node-subtitle" id="{node_id}-subtitle">{subtitle}</text></g>')
    content.append('</svg>')
    result=''.join(content[:3])+arrange_labels(''.join(content[3:-1]),1160,650,font_size=16,monospaced=True)+content[-1]
    (ROOT/'assets'/f'system-map-{v["id"]}.svg').write_text(result.replace('<defs>', '<style>'+standalone_style+'</style><defs>', 1))
    return result


def decorative_icon(key):
    return f'<svg class="smap-glyph" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true" focusable="false">{ICONS[key]}</svg>'


VIEW_VISUALS={'overview':('records','network'),'governance':('governance','shield'),'purpose':('purpose','compass'),
              'agent':('agents','robot'),'learning':('learning','sprout'),'ontology':('knowledge','network')}
buttons=''.join(f'<button type="button" class="smap-family-{VIEW_VISUALS[v["id"]][0]} smap-view-{v["id"]}" data-map-view="{v["id"]}" aria-pressed="{str(i==0).lower()}" aria-controls="map-panel-{v["id"]}">{decorative_icon(VIEW_VISUALS[v["id"]][1])}<span>{h(v["title"])}</span></button>' for i,v in enumerate(VIEWS))
legend=''.join(f'<span class="smap-legend-item" data-map-concept="{key}" data-model-concept="{key}">{decorative_icon(f["icon"])}<span>{h(f["label"])}</span></span>' for key,f in CONCEPTS.items())
legend+=''.join(f'<span class="smap-legend-item smap-family-{key}" data-map-family="{key}">{decorative_icon(f["icon"])}<span>{h(f["label"])}</span></span>' for key,f in FAMILIES.items())
SVG_ELEMENT_COUNT=len(VIEWS)*2+len(FAMILIES)+len(CONCEPTS)+1+len(GOVERNANCE['focus_views'])-1


def panel(v,index):
    if 'focus_views' in v:
        body=''.join(f'<div class="smap-focus-panel" data-map-focus="{f["focus_key"]}"{(" hidden" if j else "")}>{svg(f)}</div>' for j,f in enumerate(v['focus_views']))
        # Preserve the existing standalone asset path as the new overview.
        (ROOT/'assets/system-map-governance.svg').write_text((ROOT/'assets/system-map-governance-overview.svg').read_text())
    else:
        body=svg(v)
    return f'<div id="map-panel-{v["id"]}" class="smap-panel" data-map-panel="{v["id"]}"{(" hidden" if index else "")}>{body}</div>'


panels=''.join(panel(v,i) for i,v in enumerate(VIEWS))
focus_buttons=''.join(f'<button type="button" data-governance-focus="{f["focus_key"]}" aria-pressed="{str(i==0).lower()}">{h(f["title"].replace("Governance overview","Overview"))}</button>' for i,f in enumerate(GOVERNANCE['focus_views']))
fallback=''.join(f'<details><summary>{h(v["title"])}</summary><p>{h(v["summary"])}</p><dl>'+''.join(f'<dt>{h(NODES[p["node"]]["title"])}</dt><dd>{h(NODES[p["node"]]["role"])}</dd>' for p in v['placements'])+'</dl></details>' for v in VIEWS)
data=json.dumps(MODEL,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
fragment=f'''<section id="system-map" class="system-map" aria-labelledby="system-map-title">
<div class="smap-heading"><div><p class="eyebrow">Explore the model</p><h2 id="system-map-title">The Lab, connected</h2><p>Start with the whole system. Choose a view, then select a concept to read its explanation and connections. The map illustrates the model; it is not a live view of project operation.</p></div><a class="smap-reading-link" href="#governance">Read the article ↓</a></div>
<div class="smap-view-controls" role="group" aria-label="Choose a system map view">{buttons}</div>
<div class="smap-view-intro"><h3 id="map-question">{h(VIEWS[0]['question'])}</h3><p id="map-summary">{h(VIEWS[0]['summary'])}</p></div>
<div id="governance-focus-controls" class="smap-focus-controls" role="group" aria-label="Choose one governance question" hidden>{focus_buttons}</div>
<div class="smap-toolbar"><label for="map-node-picker">Inspect a concept <select id="map-node-picker"><option value="">Choose a concept…</option>{''.join(f'<option value="{p["node"]}">{h(NODES[p["node"]]["title"])}</option>' for p in VIEWS[0]['placements'])}</select></label><button type="button" id="map-reset">Show all connections</button><button type="button" id="map-start-example">Follow an incident investigation →</button></div>
<div class="smap-legend" role="group" aria-label="Concept colors and icons">{legend}</div>
<div id="map-journey" class="smap-journey" hidden><div><strong id="map-step-title"></strong><p id="map-step-copy"></p></div><div class="smap-journey-controls"><button type="button" id="map-step-prev">← Previous</button><span id="map-step-count"></span><button type="button" id="map-step-next">Next →</button><button type="button" id="map-step-stop">End example</button></div></div>
<div class="smap-display-controls" role="group" aria-label="Map presentation"><button type="button" id="map-diagram-mode" aria-pressed="true">Diagram</button><button type="button" id="map-list-mode" aria-pressed="false">Relationship list</button><button type="button" id="map-zoom-out">− Zoom out</button><button type="button" id="map-zoom-in">+ Zoom in</button><button type="button" id="map-fit">Fit diagram</button><span id="map-zoom-status" class="small" role="status"></span></div>
<div class="smap-workbench"><div class="smap-visual"><div class="smap-stage" tabindex="0" role="region" aria-label="System diagram. Use arrow keys to pan, or choose the relationship list.">{panels}</div><p class="smap-pan-hint">Pan with the arrow keys or scroll sideways. Select a concept to read its explanation.</p><ul id="map-relationship-list" class="smap-relationship-list" aria-label="Concepts and their connections" hidden></ul></div>
<aside id="map-inspector" class="smap-inspector" aria-label="Selected concept explanation"><div class="smap-inspector-copy"><div id="map-selection-feedback" aria-live="polite" aria-atomic="true"><p class="smap-kicker">Selected concept <span id="map-node-family"></span></p><div class="smap-inspector-heading"><span id="map-node-icon-badge" class="smap-inspector-icon" hidden><svg id="map-node-icon" class="smap-glyph" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true" focusable="false"></svg></span><h3 id="map-node-title">Choose where to begin</h3></div><p id="map-node-role">Select a concept to read its role and follow its connections.</p></div><p id="map-node-example" class="smap-example">Follow Northstar’s incident through scoped agent work, a bounded assessment, separate change decisions and later lesson use.</p><p id="map-node-boundary" class="smap-boundary-note"></p><a id="map-read-section" href="#purpose">Read the related article section ↓</a></div><details id="map-connected-roles" open><summary>Related concepts</summary><ul id="map-connections"><li>Choose a concept to inspect its connections.</li></ul></details><details id="map-source-details" class="smap-source-details" hidden><summary>Definitions behind this concept</summary><ul id="map-node-definitions"></ul></details></aside></div>
<div class="smap-caption"><span>Solid outlines: saved records or concepts</span><span class="smap-ephemeral-key">Dashed outlines: temporary session information</span><span>Arrows explain how concepts relate</span></div>
<p class="smap-footnote">Definitions link to the 8 October 2026 source snapshot. The catalog provides the exact requirements and permitted source–target record kinds behind the explanation.</p>
<noscript><p>The overview is available without scripts. Browse the descriptions of each view below.</p>{fallback}</noscript>
<script id="system-map-data" type="application/json">{data}</script>
</section>'''
(ROOT/'system-map.fragment.html').write_text(fragment)
(ROOT/'research/system-map-xray-result.json').write_text(json.dumps(dict(
    schema_version='xray-explanation-result/v1', status='constructed; browser interactions not verified',
    mode='mixed: architecture and process', authority_effect='none', target_boundary='Integrated Lab conceptual model at the captured source snapshot',
    user_intent='Visual graph explanation of the Lab system with a compact Governance overview and separately laid out lens details', renderer='L0: local HTML/CSS/SVG',
    visual_library='Installed YAML component library unavailable; explicit local nodes, role arrows, session boundary and guided walkthrough.',
    lanes=dict(surface='six map views',properties='node role, example and boundary',components='source-linked concept groups',
               internal_dependencies='view-specific role connections',external_dependencies='accountable owner, Principal and tool boundaries; no external product integration',
               flow='illustrative export-repair walkthrough',lifecycle='durable records versus ephemeral Session',risk_questions=MODEL['open_questions'],visual_composition='fixed local SVG layouts with selectable neighborhoods'),
    layer_interaction=['isolate a view','choose one Governance question','trace a neighborhood','follow an example'],evidence_boundary=MODEL['evidence_boundary'],
    validation='Construction only; no browser checks or implementation tests requested.'),indent=2)+'\n')
print(json.dumps(dict(fragment='system-map.fragment.html',views=len(VIEWS),concept_groups=len(NODES),role_connections=sum(len(v['edges']) for v in VIEWS),source_snapshot=CAT['captured_at'])))
