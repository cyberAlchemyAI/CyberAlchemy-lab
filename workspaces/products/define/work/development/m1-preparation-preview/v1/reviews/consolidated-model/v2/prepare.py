#!/usr/bin/env python3
"""Prepare the Definition application revision and review fixtures, without effects."""
import copy
import hashlib
import importlib.util
import json
import os
import re
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[7]
OUT = Path(__file__).resolve().parent
BASE = ROOT / 'define/development/m1-preparation-preview/v1'
OLD = OUT.parent / 'v1'
PREFIX = str(OUT.relative_to(ROOT))
checks = []
inputs = {}


def canonical_bytes(value):
    """Local preview subtree encoding; not a new admitted authority hash protocol."""
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False) + '\n').encode()


def digest(value):
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_ref(path):
    absolute = path if isinstance(path, Path) and path.is_absolute() else ROOT / path
    data = absolute.read_bytes()
    return {'path': str(absolute.relative_to(ROOT)), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


def read(path):
    absolute = path if isinstance(path, Path) and path.is_absolute() else ROOT / path
    inputs[str(absolute.relative_to(ROOT))] = file_ref(absolute)
    return json.loads(absolute.read_text())


def write(path, value):
    target = OUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
    with target.open('x') as f:
        f.write(text)


def check(name, condition, detail=''):
    checks.append({'check_id': name, 'outcome': 'PASS' if condition else 'FAIL', 'detail': detail})
    if not condition:
        raise ValueError(name + ': ' + detail)


def link(path, label):
    return f'[{label}]({os.path.relpath(ROOT / path, OUT)})'


def renderer(path):
    spec = importlib.util.spec_from_file_location('definition_projection', ROOT / path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def cell(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')


def table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---'] * len(headers)) + ' |'] + ['| ' + ' | '.join(cell(x) for x in row) + ' |' for row in rows])


old_manifest = read(OLD / 'package-manifest.json')
for entry in old_manifest['files']:
    check('prior-package:' + entry['path'], file_ref(entry['path']) == entry)
old_model = read(OLD / 'model.json')
registry = read('authority/definitions/registry.json')
protected = old_model['baseline']['protected']
for entry in protected:
    check('baseline:' + entry['path'], file_ref(entry['path']) == entry)
check('no-existing-application-identity', all(x['definition_id'] != 'cal.definition.definition-application' for x in registry['entries']))
schema_path = 'authority/artifact-types/definition/v2/schema.json'
generator_path = 'authority/artifact-types/definition/v2/generator.py'
schema = read(schema_path)
inputs[generator_path] = file_ref(generator_path)
projector = renderer(generator_path)
prior_subjects = {x['model_role']: x for x in old_model['selected_meanings']}
pack = copy.deepcopy(read(prior_subjects['Pack']['path']))
define = copy.deepcopy(read(prior_subjects['Define']['path']))
specimen_path = str((BASE / 'steps/03-foundational-definition/example-definition.json').relative_to(ROOT))
specimen = read(specimen_path)
work_path = 'define/proposals/0005-amended-integration-plan/work-items.json'
work = read(work_path)
applicable_sources = {}
for e in registry['entries']:
    if e['term'] in ['Definition', 'Evaluation', 'Measurement Result', 'Model Instance Binding', 'Capability Realization Binding', 'Source', 'Decision Scope', 'Typed Connection Extension Rule']:
        applicable_sources[e['term']] = e
        d = read(e['path'])
        check('admitted-source:' + e['term'], file_ref(e['path'])['sha256'] == e['sha256'])
        inputs[e['admission_decision_ref']] = None  # Remove symbolic key below; file/record standing comes from the registry.
inputs = {k: v for k, v in inputs.items() if v is not None}

new_bounds = [
    'A Definition application binds values under the selected meaning; it cannot override, weaken or extend that meaning.',
    'Meaning identity/version, binding values, captured standing, intended authority scope, materialization and assessment outcome are independent selections.',
    'Task-local proposals remain explicitly unadmitted. An application of one supports bounded proposal examination, not substitution for an applicable admitted meaning or Policy.',
    'Applications and task assessments are embedded, separately addressable entries in a Pack. They are not new independently admitted Artifact Types in this release.',
    'A changed binding or input/evidence epoch creates a new application or assessment revision with lineage; historical Pack bytes remain preserved.',
    'An application is not an Evaluation execution, Measurement Result, Finding, owner Decision, Model Instance Binding or proof of an applied effect.',
    'No recorded assessment is inferred from a binding. Counts or an outcome without exact evidence and producer/execution posture are not a completed governed Evaluation.',
    'Promotion/materialization requires an explicit purpose, authority scope and applicable owner route; repeated use alone selects no admission.',
]
app = copy.deepcopy(pack)
app.update(definition_id='cal.definition.definition-application', version='1.0.0-candidate.1', term='Definition application', aliases=['Definition application binding'])
app['classification']['lifecycle_posture_ref'] = 'candidate:define-application-model:authored-unadmitted'
app['scope']['applicability'] = 'Proposed shared meaning of an embedded task binding to an exact Definition version or explicitly identified task-local meaning proposal. Scope and standing of the selected meaning remain independent.'
app['scope']['exclusions'] = ['Semantic overrides or model inheritance/adoption.', 'Canonical admission by binding or packaging.', 'Agent execution authority, completed evaluation or incident closure.']
app['voices']['scientific_formal'] = {
    'normative_statement': 'A Definition application is an identifiable, revision-exact task record that selects one exact admitted or candidate Definition version, or one explicitly identified task-local meaning proposal, and binds its declared parameters to explicit values for a named context, consumer and intended use without changing the selected meaning. It preserves the meaning selection and captured standing, parameter contract, value provenance, applicability and unresolved binding obligations. Applications and their separately recorded assessments can be retained inside a Definition Pack. Binding values does not create a new normative meaning, produce an assessment, admit a Definition, appoint an owner, transfer authority or authorize an effect.',
    'formal_expression': 'a=(id,r,m,theta,k,u,e,q);\nWellFormedApplication(a) iff ExactSelection(m) and ExactContextUse(k,u) and DeclaredParameters(m) and dom(theta) subseteq Parameters(m) and ValuesTyped(theta,m) and MissingRequiredRecorded(theta,m,q) and ValueProvenanceRecorded(e) and MeaningUnchanged(m).\nFullyBound(a) iff WellFormedApplication(a) and RequiredParameters(m) subseteq dom(theta) and RequiredReferencesResolved(a) and ApplicabilityEstablished(a).\nFullyBound(a) does not entail ExecutedAssessment(a), Admitted(m), MayExecute(u), or AuthorityTransferred(a).',
    'notation': [
        {'symbol': 'a; id,r', 'meaning': 'One embedded application identity and exact revision within its owning Pack; local selectors identify the record without a separate file.'},
        {'symbol': 'm', 'meaning': 'One exact selected Definition version or task-local proposed meaning with its own identity/revision, digest, parameter declaration and captured standing. Proposal standing is never admitted reuse.'},
        {'symbol': 'theta; Parameters(m); RequiredParameters(m)', 'meaning': 'Partial parameter-to-value map, declared permitted names/types, and required subset. Missing required values remain explicit gaps; undeclared values and semantic overrides are rejected.'},
        {'symbol': 'k,u; e,q', 'meaning': 'Declared task context and consumer/use; exact value provenance and unresolved binding obligations.'},
        {'symbol': 'FullyBound; ExecutedAssessment', 'meaning': 'Established binding/applicability and a separately attributable evidence-producing assessment. One is not evidence of the other.'},
    ],
    'boundary_conditions': new_bounds,
    'testable_conditions': [
        'The incident binds S, A, F and E without changing the inclusion predicate.',
        'Changing E creates another binding revision and invalidates the old assessment for that changed binding.',
        'Adding an undeclared tolerance parameter is rejected; changing the required coverage threshold requires a meaning proposal.',
        'A binding can exist without any assessment; one application may have several separately versioned assessments.',
        'A task-local candidate criterion can yield an illustrative PASS while shared admission and incident closure remain unselected.',
        'Exact local selectors and subtree digests resolve applications and their evidence inside one Pack without self-hashing the Pack.',
    ],
}
app['voices']['plain_language']['explanation'] = 'Use one exact meaning for this task by supplying its declared values. Keep that binding and any later evidence-backed result inside the task Pack. Different values create another application; a different meaning needs a proposal. The binding itself approves and executes nothing.'
app['voices']['domain_context']['explanation'] = 'INC-1042 supplies snapshot S-1042, account Northstar, status=active and saved output E-1042 to the proposed identifier-completeness meaning. The fixture records its 200 missing IDs in a separate embedded assessment. The criterion is still a proposal; no customer record, Finding or incident state is changed.'
app['voices']['domain_context']['examples'] = ['A saved retry E-1042-retry supplies a new value for E under the same exact meaning.', 'A criterion allowing 1% missing IDs changes the meaning and is not a permitted parameter substitution.', 'The application record has no parent/instance override or lifecycle-adoption contract; those belong to Model Instance Binding.']
app['boundaries'] = new_bounds
app['source_refs'] = [{'source_ref': e['definition_id'] + '@' + e['version'], 'selector': '/voices/scientific_formal/normative_statement', 'content_sha256': e['sha256'], 'admission_posture': 'admitted', 'source_admission_ref': e['admission_decision_ref']} for e in applicable_sources.values()]

pack['version'] = '1.0.0-candidate.4'
pack['classification']['lifecycle_posture_ref'] = 'candidate:define-application-model:definition-pack:authored-unadmitted'
formal = pack['voices']['scientific_formal']
formal['normative_statement'] += ' The Pack may embed exact Definition applications, task values, task-local proposed meanings and separately attributable assessments as individually addressable records. Task-local proposals remain explicitly unadmitted. Existing meaning applications preserve their selected meaning; new or changed meaning intended for admission requires complete Definition preparation under an explicit materialization selection. Disposition, scope, standing, materialization and assessment outcome remain independent. Assessments are optional; Pack preparation does not manufacture an Evaluation execution or accepted fact.'
formal['formal_expression'] = formal['formal_expression'].replace('Q,V,A);', 'Q,V,A,M,B,Y);').replace(' and NoNewAuthorityFromPack(A).', ' and EmbeddedMeaningBindingsValid(M,B) and SeparateAssessmentBindingsValid(Y,B,E) and MaterializationSelectionExplicit(H) and NoNewAuthorityFromPack(A).')
formal['notation'] += [
    {'symbol': 'M; B; Y', 'meaning': 'Embedded task-local meaning proposals, Definition application records and separate assessments. Any collection may be empty; nonempty assessment entries bind exact application/input evidence and preserve execution/claim posture.'},
    {'symbol': 'MaterializationSelectionExplicit', 'meaning': 'Task-local proposed meaning is embedded by default. Creating a separately reviewable complete Definition candidate requires an explicit intent/purpose, scope and owner route. Neither placement nor selection admits it.'},
]
old_boundary = 'Specialization within the parent meaning produces an application binding. A new or changed normative meaning produces a complete proposed Definition through the explicit identity/successor route.'
new_boundary = 'Specialization within the parent meaning produces a Definition application under its declared parameter contract. A new or changed meaning is an explicitly unadmitted task-local proposal by default; selecting it for admission requires complete Definition preparation through the explicit identity/successor route.'
for field in [formal['boundary_conditions'], pack['boundaries']]:
    field[field.index(old_boundary)] = new_boundary
    field += new_bounds
formal['testable_conditions'] += app['voices']['scientific_formal']['testable_conditions']
pack['voices']['plain_language']['explanation'] += ' Task values and results stay inside the Pack. A new working meaning can stay there as an unadmitted proposal; a separate Definition is prepared when its purpose and intended authority scope are explicitly selected.'
pack['voices']['domain_context']['explanation'] = 'The incident Pack embeds one task-local proposed completeness meaning, its S/A/F/E application, saved synthetic input evidence and a separate coverage assessment. Incident is reused, Work is applied without semantic change, completeness remains proposed and account exclusivity remains open. No per-incident Definition or assessment file is emitted.'
pack['voices']['domain_context']['examples'] = ['INC-1042 keeps its account, filters, snapshot and saved output in the application record.', 'The embedded assessment reports 200 missing required IDs under the proposed criterion; the criterion itself remains unadmitted.', 'A later retry has a new application/assessment epoch under the same meaning.', 'Account exclusivity remains open even when identifier coverage passes.']

define['version'] = '1.0.0-candidate.4'
define['classification']['lifecycle_posture_ref'] = 'candidate:define-application-model:define:authored-unadmitted'
define['voices']['scientific_formal']['normative_statement'] += ' Define prepares task-specific Definition applications and preserves available assessments inside the Pack with their independent evidence and producer posture. Task-local proposed meaning remains embedded by default; separately materializing a complete Definition candidate requires an explicit purpose, scope and owner route. Define preparation neither executes a domain assessment nor turns a task-local proposal into shared authority.'
define['voices']['scientific_formal']['formal_expression'] = define['voices']['scientific_formal']['formal_expression'].replace('and ReviewableFor(P,u)', 'and PreservesMeaningAndBindingSeparation(P) and PreservesAssessmentProvenance(P)\n  and ReviewableFor(P,u)')
for item in define['voices']['scientific_formal']['notation']:
    if item['symbol'] == 'WellFormedPack(P)':
        item['meaning'] = 'Exact revised Definition Pack candidate.4 in this package, including embedded applications, optional assessments and explicit materialization. This candidate coupling is not an admitted governing source.'
define['voices']['scientific_formal']['notation'] += [{'symbol': 'PreservesMeaningAndBindingSeparation; PreservesAssessmentProvenance', 'meaning': 'Parameter substitutions preserve selected meaning; separately recorded assessments retain their exact application, input, producer and claim limits. Define does not invent an assessment merely by preparing a binding.'}]
define['voices']['scientific_formal']['boundary_conditions'] += new_bounds
define['boundaries'] += new_bounds
define['voices']['scientific_formal']['testable_conditions'] += app['voices']['scientific_formal']['testable_conditions']
define['voices']['plain_language']['explanation'] += ' The Pack keeps task values and any separately produced results together. It prepares a separate Definition only when that materialization is explicitly selected.'
define['voices']['domain_context']['examples'] += ['The incident criterion, S/A/F/E binding and synthetic assessment remain embedded in one task Pack; no new per-task shared Definition is selected.']

new_subjects = []
for role, slug, d in [('DefinitionApplication', 'definition-application', app), ('Pack', 'definition-pack', pack), ('Define', 'cyberalchemy-define', define)]:
    path = PREFIX + '/definitions/' + slug + '/definition.json'
    d['primary_consumer_refs'] = [PREFIX + '/MODEL.md', PREFIX + '/pack-embedding.schema.json', PREFIX + '/incident-pack.json']
    d['index_entry'] = {'entry_id': d['definition_id'], 'index_ref': PREFIX + '/DEFINITIONS-INDEX.md'}
    d['drift_route']['audit_ref'] = PREFIX + '/review-report.json'
    d['evidence_refs'] = [PREFIX + '/source-bindings.json', PREFIX + '/incident-pack.json', PREFIX + '/non-collapse-review.json', PREFIX + '/review-report.json']
    d['residue_refs'] = ['revised-meaning-fidelity-owner-review-pending', 'bounded-controls-not-global-proof', 'revised-registry-and-consumer-postimages-pending-qualified-review', 'applicable-v2-profile-standing-pending', 'production-pack-adapter-and-runtime-qualification-pending', 'exact-admission-and-application-unselected']
    d['claim_ceiling'] = 'Revised authored semantic candidate and local preview evidence only. Prior candidate.3 fidelity/assurance acceptance is not transferred to changed bytes. No independent owner fidelity acceptance, global semantic proof, production Evaluation, profile/type adoption, admission or application.'
    jsonschema.Draft202012Validator(schema).validate(d)
    write('definitions/' + slug + '/definition.json', d)
    markdown = projector.render(d)
    check('deterministic-projection:' + slug, markdown == projector.render(d))
    write('definitions/' + slug + '/DEFINITION.md', markdown)
    new_subjects.append({'model_role': role, 'definition_ref': d['definition_id'] + '@' + d['version'], 'admission_posture': 'candidate-unadmitted', 'carrier_ref': 'cal.artifact-type.definition/v2', **file_ref(path), 'human_projection': file_ref(PREFIX + '/definitions/' + slug + '/DEFINITION.md'), 'schema': file_ref(schema_path), 'generator': file_ref(generator_path)})
    check('candidate-schema:' + slug, True)
selected = new_subjects + [copy.deepcopy(x) for x in old_model['selected_meanings'] if x['model_role'] not in ['Pack', 'Define']]
check('six-selected-meanings', len(selected) == 6)

# The local proposed meaning is an embedded working record, not a new complete
# Lab Definition artifact or independently admitted Artifact Type.
meaning = {
    'meaning_id': 'working:export-identifier-completeness', 'revision': 1,
    'scope_ref': 'task:INC-1042', 'standing': 'working-proposal', 'shared_admission_selected': False,
    'normative_statement': specimen['voices']['scientific_formal']['normative_statement'],
    'formal_expression': specimen['voices']['scientific_formal']['formal_expression'],
    'parameters': {'S': {'type': 'string', 'required': True}, 'A': {'type': 'string', 'required': True}, 'F': {'type': 'object', 'required': True}, 'E': {'type': 'string', 'required': True}},
    'boundaries': specimen['scope']['exclusions'] + specimen['voices']['scientific_formal']['boundary_conditions'],
    'lineage': {'source': file_ref(specimen_path), 'selectors': ['/voices/scientific_formal/normative_statement', '/voices/scientific_formal/formal_expression'], 'posture': 'candidate specimen only; no source or meaning admission'},
}
meaning_ref = {'kind': 'task-local-proposal', 'meaning_id': meaning['meaning_id'], 'revision': 1, 'sha256': digest(meaning), 'selector': '/working_meanings/0', 'standing': 'working-proposal', 'admission_decision_ref': None}
application = {
    'application_id': 'application:INC-1042-coverage', 'revision': 1, 'task_ref': 'task:INC-1042',
    'meaning_ref': meaning_ref,
    'bindings': {'S': 'S-1042', 'A': 'Northstar', 'F': {'status': 'active'}, 'E': 'E-1042'},
    'binding_gaps': [], 'consumer': 'incident-investigating agent and human reviewer',
    'intended_use': 'examine a proposed criterion against saved synthetic evidence',
    'value_provenance': [{'parameters': ['S','A','F'], 'evidence_id': 'S-1042'}, {'parameters': ['E'], 'evidence_id': 'E-1042'}],
    'lineage': {'predecessor': None, 'reason': 'Initial synthetic task application'}, 'authority_effect': 'none',
}
evidence = [
    {'evidence_id': 'S-1042', 'revision': 1, 'kind': 'synthetic-source-snapshot', 'account': 'Northstar', 'filters': {'status': 'active'}, 'population_established': True, 'identifier_encoding': 'inclusive-integer-ranges', 'identifier_ranges': [[1,12000]], 'identity_assumption': 'globally unique integer identifiers within the fixture'},
    {'evidence_id': 'E-1042', 'revision': 1, 'kind': 'synthetic-saved-output', 'account': 'Northstar', 'filters': {'status': 'active'}, 'population_established': True, 'identifier_encoding': 'inclusive-integer-ranges', 'identifier_ranges': [[1,11800]], 'identity_assumption': 'globally unique integer identifiers within the fixture'},
]


def exact_definition(term):
    e = next(x for x in registry['entries'] if x['term'] == term)
    read(e['path'])
    return {'kind': 'definition', 'definition_id': e['definition_id'], 'version': e['version'], 'path': e['path'], 'sha256': e['sha256'], 'standing': 'admitted-current', 'admission_decision_ref': e['admission_decision_ref']}


task_pack = {
    'schema_version': 'cal.define-pack-application-preview/v1', 'pack_id': 'pack:INC-1042-investigation', 'revision': 1,
    'status': 'candidate-unadmitted', 'authority_effect': 'none', 'posture': 'executed-local-synthetic-fixture; not a production Define run',
    'scope': {'task_ref': 'task:INC-1042', 'goal': 'Clarify meanings needed to investigate missing export identifiers', 'intent': 'Investigate the reported omission using saved evidence', 'consumer': 'incident-investigating agent and human reviewer', 'intended_use': 'bounded criterion review'},
    'required_concepts': ['incident', 'investigation-work', 'identifier-completeness', 'account-exclusivity'],
    'concepts': [
        {'concept_id': 'incident', 'disposition': 'reuse', 'payload': {'meaning_ref': exact_definition('Incident'), 'applicability': 'Response/accountability envelope only; no closure effect'}},
        {'concept_id': 'investigation-work', 'disposition': 'specialize', 'payload': {'parent': exact_definition('Work'), 'semantic_change': False, 'application_parameters': {'task_ref': 'task:INC-1042'}, 'boundary': 'Task application context only; not an undeclared override of Work'}},
        {'concept_id': 'identifier-completeness', 'disposition': 'propose', 'payload': {'meaning_ref': meaning_ref, 'materialization': 'embedded-working-proposal', 'shared_admission_selected': False}},
        {'concept_id': 'account-exclusivity', 'disposition': 'open', 'payload': {'question': 'Must the output contain only matching Northstar records?', 'reason': 'No accepted exclusivity criterion selected', 'affected_use': 'complete export conformance or incident closure', 'owner_gap': 'Applicable export-domain owner not established by this fixture', 'continuation': 'Resolve the governing policy/meaning through its own route'}},
    ],
    'working_meanings': [meaning], 'applications': [application], 'assessments': [], 'evidence': evidence,
    'readiness': {'proposal_review': 'bounded illustration available', 'shared_admission': False, 'incident_closure': False, 'production_effects_authorized': False},
    'lineage': {'predecessor': None, 'source_example': file_ref(specimen_path), 'reason': 'Move task values and synthetic assessment into an embedded application Pack'},
}


def ids(record):
    return {i for first,last in record['identifier_ranges'] for i in range(first,last+1)}


def coverage(pack_value):
    a = pack_value['applications'][0]
    m = pack_value['working_meanings'][0]
    b = a['bindings']
    outcome, counts, missing, blockers = 'NOT_EVALUABLE', {'required': None, 'present': None, 'missing': None}, [], []
    if a['meaning_ref']['sha256'] != digest(m):
        blockers.append('meaning digest mismatch')
    elif set(b) - set(m['parameters']):
        blockers.append('undeclared parameter; change is not an application')
    elif set(m['parameters']) - set(b):
        blockers.append('required parameter missing')
    else:
        records = {x['evidence_id']: x for x in pack_value['evidence']}
        s, e = records.get(b['S']), records.get(b['E'])
        if s is None or e is None:
            blockers.append('selected input evidence missing')
        elif s['account'] != b['A'] or s['filters'] != b['F'] or e['account'] != b['A'] or e['filters'] != b['F']:
            blockers.append('selected account/filter evidence is incompatible with binding')
        elif not s['population_established'] or not e['population_established']:
            blockers.append('required or exported population not established')
        else:
            required, exported = ids(s), ids(e)
            missing = sorted(required - exported)
            counts = {'required': len(required), 'present': len(required & exported), 'missing': len(missing)}
            outcome = 'FAIL' if missing else 'PASS'
    return {'assessment_id': 'assessment:INC-1042-coverage', 'revision': 1, 'kind': 'illustrative-criterion-assessment',
            'application_id': a['application_id'], 'application_revision': a['revision'], 'application_sha256': digest(a),
            'meaning_sha256': a['meaning_ref']['sha256'], 'evidence_bindings': [{'evidence_id': x['evidence_id'], 'sha256': digest(x)} for x in pack_value['evidence']],
            'method': {'id': 'fixture:integer-set-inclusion/v1', 'implementation': file_ref(Path(__file__).resolve()), 'scope': 'Saved synthetic integer ranges only; not an adopted Evaluation Profile or Measurement Method'},
            'producer': 'authoring assistant local fixture review', 'execution_posture': 'executed-local-synthetic',
            'outcome': outcome, 'counts': counts, 'missing_identifiers': missing, 'unit': 'unique-identifiers', 'blockers': blockers,
            'authority_effect': 'none', 'claim_ceiling': 'Evidence for this synthetic proposed criterion/application only. Not a complete Lab Evaluation, Measurement Result, accepted Finding, shared admission, permission or closure.'}


task_pack['assessments'] = [coverage(task_pack)]

# Proposed closed embedding representation. Cross-reference/currentness and
# semantic applicability require the separate scoped review below.
def obj(properties, required=None):
    return {'type': 'object', 'additionalProperties': False, 'properties': properties, 'required': list(properties) if required is None else required}


string = {'type': 'string', 'minLength': 1}
integer = {'type': 'integer', 'minimum': 1}
sha = {'type': 'string', 'pattern': '^[a-f0-9]{64}$'}
none = {'const': 'none'}
file_schema = obj({'path': string, 'sha256': sha, 'bytes': {'type':'integer','minimum':0}})
definition_ref = obj({'kind': {'const':'definition'}, 'definition_id': string, 'version': string, 'path': string, 'sha256': sha, 'standing': {'enum':['admitted-current','candidate-unadmitted']}, 'admission_decision_ref': {'type':['string','null']}})
local_ref = obj({'kind': {'const':'task-local-proposal'}, 'meaning_id': string, 'revision': integer, 'sha256': sha, 'selector': string, 'standing': {'const':'working-proposal'}, 'admission_decision_ref': {'type':'null'}})
meaning_ref_schema = {'oneOf':[definition_ref,local_ref]}
meaning_schema = obj({'meaning_id':string,'revision':integer,'scope_ref':string,'standing':{'const':'working-proposal'},'shared_admission_selected':{'const':False},'normative_statement':string,'formal_expression':string,'parameters':{'type':'object','minProperties':1,'additionalProperties':obj({'type':{'enum':['string','object']},'required':{'type':'boolean'}})},'boundaries':{'type':'array','items':string},'lineage':obj({'source':file_schema,'selectors':{'type':'array','items':string},'posture':string})})
application_schema = obj({'application_id':string,'revision':integer,'task_ref':string,'meaning_ref':meaning_ref_schema,'bindings':{'type':'object','additionalProperties':{'type':['string','object']}},'binding_gaps':{'type':'array','items':string},'consumer':string,'intended_use':string,'value_provenance':{'type':'array','items':obj({'parameters':{'type':'array','items':string},'evidence_id':string})},'lineage':obj({'predecessor':{'type':['string','null']},'reason':string}),'authority_effect':none})
assessment_schema = obj({'assessment_id':string,'revision':integer,'kind':{'const':'illustrative-criterion-assessment'},'application_id':string,'application_revision':integer,'application_sha256':sha,'meaning_sha256':sha,'evidence_bindings':{'type':'array','items':obj({'evidence_id':string,'sha256':sha})},'method':obj({'id':string,'implementation':file_schema,'scope':string}),'producer':string,'execution_posture':{'const':'executed-local-synthetic'},'outcome':{'enum':['PASS','FAIL','NOT_EVALUABLE']},'counts':obj({x:{'type':['integer','null'],'minimum':0} for x in ['required','present','missing']}),'missing_identifiers':{'type':'array','uniqueItems':True,'items':{'type':'integer','minimum':1}},'unit':{'const':'unique-identifiers'},'blockers':{'type':'array','items':string},'authority_effect':none,'claim_ceiling':string})
evidence_schema = obj({'evidence_id':string,'revision':integer,'kind':{'enum':['synthetic-source-snapshot','synthetic-saved-output']},'account':string,'filters':obj({'status':string}),'population_established':{'type':'boolean'},'identifier_encoding':{'const':'inclusive-integer-ranges'},'identifier_ranges':{'type':'array','items':{'type':'array','prefixItems':[integer,integer],'items':False,'minItems':2,'maxItems':2}},'identity_assumption':string})
payloads = {
    'reuse':obj({'meaning_ref':definition_ref,'applicability':string}),
    'specialize':obj({'parent':definition_ref,'semantic_change':{'const':False},'application_parameters':obj({'task_ref':string}),'boundary':string}),
    'propose':obj({'meaning_ref':meaning_ref_schema,'materialization':{'enum':['embedded-working-proposal','selected-definition-preparation']},'shared_admission_selected':{'const':False}}),
    'open':obj({x:string for x in ['question','reason','affected_use','owner_gap','continuation']}),
}
concept_schema = {'oneOf':[obj({'concept_id':string,'disposition':{'const':tag},'payload':payload}) for tag,payload in payloads.items()]}
pack_schema = dict(obj({'schema_version':{'const':'cal.define-pack-application-preview/v1'},'pack_id':string,'revision':integer,'status':{'const':'candidate-unadmitted'},'authority_effect':none,'posture':string,'scope':obj({x:string for x in ['task_ref','goal','intent','consumer','intended_use']}),'required_concepts':{'type':'array','minItems':1,'uniqueItems':True,'items':string},'concepts':{'type':'array','minItems':1,'items':concept_schema},'working_meanings':{'type':'array','items':meaning_schema},'applications':{'type':'array','items':application_schema},'assessments':{'type':'array','items':assessment_schema},'evidence':{'type':'array','items':evidence_schema},'readiness':obj({'proposal_review':string,'shared_admission':{'const':False},'incident_closure':{'const':False},'production_effects_authorized':{'const':False}}),'lineage':obj({'predecessor':{'type':['string','null']},'source_example':file_schema,'reason':string})}), **{'$schema':'https://json-schema.org/draft/2020-12/schema', '$id':'https://cyberalchemy.local/preview/define-pack-application/v1', 'title':'Proposed embedding preview; not the complete production Pack adapter', '$comment':'No new independently admitted Artifact Type. Generic full carriers and lifecycle/effect protocols remain pending.'})
jsonschema.Draft202012Validator.check_schema(pack_schema)
jsonschema.Draft202012Validator(pack_schema).validate(task_pack)
check('incident-preview-schema', True)
write('pack-embedding.schema.json', pack_schema)
write('incident-pack.json', task_pack)
check('incident-inclusion-result', task_pack['assessments'][0]['outcome']=='FAIL' and task_pack['assessments'][0]['counts']=={'required':12000,'present':11800,'missing':200})
check('parameters-preserve-meaning', meaning['formal_expression']==specimen['voices']['scientific_formal']['formal_expression'])


def integrity_errors(p):
    errors=[]
    concepts=[x['concept_id'] for x in p['concepts']]
    if len(set(concepts))!=len(concepts) or set(concepts)!=set(p['required_concepts']):errors.append('concept handling not total/unique')
    apps={x['application_id']:x for x in p['applications']}
    if len(apps)!=len(p['applications']):errors.append('duplicate application identity')
    for a in p['applications']:
        m=p['working_meanings'][0]
        if a['meaning_ref']['sha256']!=digest(m):errors.append('meaning hash mismatch')
        if set(a['bindings'])-set(m['parameters']):errors.append('undeclared parameter')
        required={k for k,v in m['parameters'].items() if v['required']}
        if required-set(a['bindings'])!=set(a['binding_gaps']):errors.append('unrecorded required parameter gap')
        for k,v in a['bindings'].items():
            if k in m['parameters'] and not isinstance(v,{'string':str,'object':dict}[m['parameters'][k]['type']]):errors.append('parameter type mismatch')
        if a['task_ref']!=p['scope']['task_ref']:errors.append('application outside task')
    for y in p['assessments']:
        a=apps.get(y['application_id'])
        if a is None:errors.append('orphan assessment');continue
        if y['application_sha256']!=digest(a) or y['application_revision']!=a['revision']:errors.append('stale assessment application')
        if y['meaning_sha256']!=a['meaning_ref']['sha256']:errors.append('stale assessment meaning')
        for e in y['evidence_bindings']:
            observed=next((x for x in p['evidence'] if x['evidence_id']==e['evidence_id']),None)
            if observed is None or digest(observed)!=e['sha256']:errors.append('stale assessment evidence')
    for c in p['concepts']:
        if c['disposition']=='reuse' and c['payload']['meaning_ref']['standing']!='admitted-current':errors.append('candidate relabeled reuse')
    return errors


check('incident-cross-reference-integrity', not integrity_errors(task_pack))
cases=[]


def case(name, transform, expected):
    p=copy.deepcopy(task_pack);p['assessments']=[]
    transform(p)
    result=coverage(p)
    check('criterion-control:'+name, result['outcome']==expected)
    cases.append({'case':name,'expected':expected,'observed':result['outcome'],'counts':result['counts'],'blockers':result['blockers'],'scope':'synthetic inclusion comparison only; no production Evaluation'})


case('missing-200',lambda p:None,'FAIL')
case('all-required-present',lambda p:p['evidence'][1].update(identifier_ranges=[[1,12000]]),'PASS')
case('extras-do-not-change-inclusion',lambda p:p['evidence'][1].update(identifier_ranges=[[1,12100]]),'PASS')
case('duplicates-do-not-replace-missing-identifiers',lambda p:p['evidence'][1].update(identifier_ranges=[[1,11800],[1,200]]),'FAIL')
case('unknown-required-population',lambda p:p['evidence'][0].update(population_established=False),'NOT_EVALUABLE')
case('established-empty-required-population',lambda p:p['evidence'][0].update(identifier_ranges=[]),'PASS')
case('missing-input-evidence',lambda p:p['evidence'].pop(0),'NOT_EVALUABLE')
case('missing-required-binding',lambda p:p['applications'][0]['bindings'].pop('F'),'NOT_EVALUABLE')
case('wrong-account',lambda p:p['applications'][0]['bindings'].update(A='Another account'),'NOT_EVALUABLE')
case('different-filter',lambda p:p['applications'][0]['bindings'].update(F={'status':'inactive'}),'NOT_EVALUABLE')
case('undeclared-tolerance',lambda p:p['applications'][0]['bindings'].update(tolerance=0.01),'NOT_EVALUABLE')
case('meaning-digest-tamper',lambda p:p['applications'][0]['meaning_ref'].update(sha256='0'*64),'NOT_EVALUABLE')
for name, mutate, expected_fragment in [
    ('stale-assessment-after-value-change',lambda p:p['applications'][0]['bindings'].update(E='E-1042-retry'),'stale assessment application'),
    ('orphan-assessment',lambda p:p['assessments'][0].update(application_id='missing-app'),'orphan assessment'),
    ('stale-input-evidence',lambda p:p['evidence'][1].update(identifier_ranges=[[1,12000]]),'stale assessment evidence'),
    ('candidate-cannot-be-reused-as-admitted',lambda p:p['concepts'][0]['payload']['meaning_ref'].update(standing='candidate-unadmitted'),'candidate relabeled reuse'),
]:
    p=copy.deepcopy(task_pack);mutate(p);errors=integrity_errors(p)
    check('integrity-control:'+name, expected_fragment in errors)
    cases.append({'case':name,'expected':'rejected or explicitly invalidated','observed_errors':errors,'scope':'local embedding/cross-reference contract only'})
without=copy.deepcopy(task_pack);without['assessments']=[]
jsonschema.Draft202012Validator(pack_schema).validate(without)
check('application-without-assessment-valid', not integrity_errors(without))
retry=copy.deepcopy(task_pack);retry['revision']=2;retry['lineage']['predecessor']=digest(task_pack)
retry['applications'][0]['revision']=2;retry['applications'][0]['bindings']['E']='E-1042-retry'
retry['evidence'][1].update(evidence_id='E-1042-retry',identifier_ranges=[[1,12000]])
retry['applications'][0]['value_provenance'][1]['evidence_id']='E-1042-retry'
retry['applications'][0]['lineage']={'predecessor':digest(application),'reason':'Saved synthetic retry output; meaning unchanged'}
retry['assessments']=[coverage(retry)];retry['assessments'][0]['revision']=2
check('new-retry-epoch-valid', not integrity_errors(retry) and retry['assessments'][0]['outcome']=='PASS')
check('retry-meaning-unchanged', retry['applications'][0]['meaning_ref']==application['meaning_ref'])
check('retry-no-shared-admission', retry['readiness']['shared_admission'] is False)
cases.append({'case':'saved-retry-new-epoch','expected':'PASS under same proposed meaning; no shared admission','observed':retry['assessments'][0]['outcome'],'counts':retry['assessments'][0]['counts'],'original_pack_preserved':True})
write('incident-controls.json', {'authority_effect':'none','cases':cases,'application_without_assessment_valid':True,'retry_application':retry['applications'][0],'retry_assessment':retry['assessments'][0],'scope':'Executed local synthetic controls; not strict Define CLI or production evaluator qualification'})

distinctions=[
    ('Definition','Defines normative meaning','Binds declared values to that exact meaning','The same criterion is used in the initial application and retry with a different E.'),
    ('Definition Pack','Contains the bounded concept-handling package','Is an embedded record inside that package','A Pack may have zero, one or many applications; the fixture has one.'),
    ('Evaluation','Executes a version-exact profile and yields complete outcomes','Declares a binding without producing outcomes','The application-without-assessment control remains structurally valid.'),
    ('Measurement Result','Records an exact Measurement Method execution with units, uncertainty and receipt','Binds context/values before any measurement/result','The fixture assessment is explicitly not a complete Measurement Result.'),
    ('Model Instance Binding','Canonical lifecycle contract for inherited model/instance authority and overrides','Preserves one meaning under declared parameter substitution','The incident application declares no override, adoption or parent/instance authority transfer.'),
    ('Capability Realization Binding','Associates capability revisions with implementation revisions and adoption','Associates meaning selection with task parameter values','The application names S/A/F/E, not a Product Capability-to-Implementation adoption.'),
]
write('non-collapse-review.json', {'authority_effect':'none','reviewer':'authoring assistant; owner semantic fidelity review pending','scope':'Explicit boundary arguments and executed fixture witnesses; no whole-language equivalence or unrestricted formal proof','pairs':[{'other':a,'other_question':b,'application_question':c,'witness':d} for a,b,c,d in distinctions],'global_consistency_established':False,'new_formal_correspondence_accepted':False})

# Candidate lookup projection, never a live or claimed admitted postimage.
entries=copy.deepcopy(registry['entries'])
for s in selected:
    d=read(s['path'])
    entries.append({'definition_id':d['definition_id'],'version':d['version'],'term':d['term'],'path':s['path'],'sha256':s['sha256'],'lifecycle_state':'candidate-authored','admission_decision_ref':None})
proposed_current=copy.deepcopy(registry['current_lookup'])
for s in selected:
    d=read(s['path']);proposed_current[d['definition_id']]=d['version']
check('new-cohort-counts',len(entries)==195 and len(proposed_current)==188)
write('registry-postimage.json', {'schema_version':'cal.define-application-cohort-registry-preview/v1','status':'candidate-unadmitted','authority_effect':'none','representation_status':'descriptive mixed candidate preview, not the original v1 authoring/admitted-output contract','baseline':file_ref('authority/definitions/registry.json'),'entries':entries,'proposed_current_lookup':proposed_current,'actual_current_lookup_changed':False,'actual_decision_ref':None,'claim_ceiling':'Six selected candidate meanings; no admitted rows fabricated. Original two-meaning v1 mapping remains independently pending. Full revised postimage compatibility and owner review remain required.'})
index=['# Revised candidate Definition index','','Six meanings selected for this model review. Admission is unselected; the live registry is unchanged.','',table(['Meaning','Exact candidate','Record'],[[read(x['path'])['term'],x['definition_ref'],link(x['human_projection']['path'],'Full Definition')] for x in selected]),'','Prospective complete cohort: 195 versions / 188 identities. Current live: 189 versions / 183 identities. Old candidate.3 Pack/Define reviews remain historical; their acceptance is not transferred to candidate.4.','']
write('DEFINITIONS-INDEX.md','\n'.join(index))
activation=copy.deepcopy(old_model['activation'])
app_subject=next(s for s in selected if s['model_role']=='DefinitionApplication')
activation['nodes'].insert(-2,{'id':'DEFINITION-APPLICATION','depends_on':['PROFILE-ADOPTION','FOUNDATIONAL-SUCCESSOR','DEFINITION-BINDING'],'route':'Exact v2 Definition application meaning review, source/impact/assurance and owner selection; all pending','subjects':[app_subject]})
for node in activation['nodes']:
    if node['id']=='PACK-AND-DEFINE':
        node['depends_on'].append('DEFINITION-APPLICATION');node['subjects']=[s for s in selected if s['model_role'] in ['Pack','Define']]
    if node['id']=='COHERENT-VISIBILITY':node['depends_on'].append('DEFINITION-APPLICATION')
activation['status']='revised prospective ordering; no effect selected or applied'
model=copy.deepcopy(old_model)
model.update(schema_version='cal.define-consolidated-review-model/v2',status='revised-candidate-model-with-embedded-definition-applications',definition_subject_count=6,selected_meanings=selected,activation=activation)
model['predecessor']=file_ref(OLD/'package-manifest.json')
model['incident']={'posture':'executed-local-synthetic comparison; no production run','pack':file_ref(PREFIX+'/incident-pack.json'),'application_selector':'/applications/0','assessment_selector':'/assessments/0','working_meananing_selector':'/working_meanings/0','criterion_outcome':'FAIL, 200 missing required IDs','shared_admission':False,'incident_closure':False}
model['postimage_options']['full_five_meaning_cohort']={'status':'historical superseded review selection; not new admission material','versions':194,'conditional_current_identities':187}
model['postimage_options']['full_six_meaning_cohort']={'versions':195,'conditional_current_identities':188,'preview':file_ref(PREFIX+'/registry-postimage.json')}
model['review_outcome']['scope']='One revised model review. Prior unchanged scopes retain their evidence; changed Pack/Define and new Definition application need fresh fidelity/assurance, impact and owner outcomes.'
model['completion']['review_package_prepared']=True
write('model.json',model)

amendments={
    'authority_effect':'none','status':'candidate integration amendments; runtime enforcement not implemented',
    'predecessor_work_map':file_ref(work_path),'original_work_item_count':79,
    'changes':[
        {'area':'G01/G03','change':'Add Definition application candidate.1; revise Pack and Define to candidate.4; retain the other three meanings exactly. Reopen affected formal/fidelity and admission cohort evidence.'},
        {'area':'G04','change':'Embed applications, values, working proposals and optional assessments. Preserve four dispositions. Keep scope, standing, materialization and outcomes independent.'},
        {'area':'G05','change':'Emit one task Pack by default. Emit complete standalone Definition candidates only for explicit selected-definition-preparation intent/scope. Existing full Definition carrier obligations still apply to those selected records.'},
        {'area':'G06','change':'Distinguish parameter substitution, new task-local proposal and meaning change. Missing/undeclared/type-invalid values and incompatible reference standing remain visible blockers.'},
        {'area':'G07/G08','change':'Task-local use/admission cannot override admitted meaning or Policy; shared admission requires fresh exact scope/owner review. No implicit local authority from Pack acceptance.'},
        {'area':'G09','change':'Resolve inline record by exact Pack revision/selector and subtree digest. Preserve original full Pack and evidence when cited; changed values require new epochs and stale-assessment handling.'},
        {'area':'G10','change':'Qualify production adapter/provider/exporter against these cases and preserved legacy API behavior. Local synthetic controls do not establish full implementation or governed Evaluation conformance.'},
    ],
    'affected_consumers':[
        {'path':'implementation/define-cli/v1/CONTRACT.md','disposition':'preserve legacy current contract; new embedding requires explicit successor adapter, not silent compatibility'},
        {'path':'define/proposals/0005-amended-integration-plan/DESIGN.md','disposition':'preserve immutable plan history; this amendment replaces default materialize-every-new-meaning assumption for revised preparation'},
        {'path':prior_subjects['Pack']['path'],'disposition':'preserve candidate.3; select new candidate.4 for this review only'},
        {'path':prior_subjects['Define']['path'],'disposition':'preserve candidate.3; select new candidate.4 for this review only'},
        {'path':specimen_path,'disposition':'preserve full specimen; take exact selected meaning clauses as candidate lineage for the embedded task-local proposal'},
    ],
    'required_remaining_evidence':['new semantic fidelity and scoped formal correspondence','applicable v2 profile standing','full revised registry/index/drift and consumer closure','production embedding adapter and runtime qualification','exact owner decision and confirmed application'],
}
write('integration-amendments.json',amendments)

# Revise the complete explanatory model while leaving the sealed predecessor.
main=(OLD/'MODEL.md').read_text()
replacements=[
 ('# Define in CyberAlchemy Lab — one complete model to review','# Define in CyberAlchemy Lab — revised model with Definition applications'),
 ('Its five Definition subjects retain their exact reviewed bytes; their admission and the new profile adoption remain pending.','The proposal selects six meanings: new Definition application candidate.1, revised Pack/Define candidate.4 and the three unchanged candidate.3 meanings. Changed wording needs fresh review; admission and profile adoption remain pending.'),
 ('| Definition Lifecycle Profile | Which states and directed changes are allowed, with what evidence and authority? | The proposed completeness meaning starts authored; later validation, review and admission are separately evidenced. |','| Definition Lifecycle Profile | Which states and directed changes are allowed, with what evidence and authority? | The proposed completeness meaning starts authored; later validation, review and admission are separately evidenced. |\n| Definition application | Which exact meaning is being applied to which task values? | Bind S-1042, Northstar, status=active and E-1042; keep the assessment separate. |'),
 ('All five selected meanings are `1.0.0-candidate.3`.','Definition application is `1.0.0-candidate.1`; Pack and Define are `1.0.0-candidate.4`; the other three remain `1.0.0-candidate.3`.'),
 ('These are the five semantic subjects; the incident specimen is outside their admission cohort.','These are six semantic subjects. The incident working proposal, application and assessment are embedded task records outside their admission cohort.'),
 ('| propose | A proposed meaning exported as a complete Lab Definition, with lineage and visible unresolved obligations. | Export identifier completeness. |','| propose | An explicitly unadmitted working meaning embedded in the Pack by default. Complete Definition export is required when selected for admission preparation. | Export identifier completeness, retained inside this investigation Pack. |'),
 ('2. Complete Definition JSON for each proposed semantic identity/version, plus deterministic generated Markdown.','2. Embedded Definition applications, task values, task-local working proposals and optional separate assessments. Complete standalone Definition JSON/Markdown is emitted only for explicitly selected admission preparation.'),
 ('The strict preparation wire contracts and exporter remain implementation work; this model does not invent an already adopted protocol schema.','The proposed closed embedding preview and the incident fixture are in [pack schema](pack-embedding.schema.json) and [one incident Pack](incident-pack.json). The complete strict production wire contracts and exporter remain implementation work; this preview is not a new admitted Artifact Type.'),
 ('This is a synthetic realistic illustration.','This is a synthetic fixture whose inclusion comparison was executed locally during self-review. It is not a production incident observation or Define CLI run.'),
 ('Requires the 14 checks below; this illustration supplies no completed evaluation or admission.','Requires the 14 checks below; the embedded synthetic coverage assessment is not that Definition evaluation and selects no admission.'),
 ('| Full five-meaning cohort | 194 | 187, conditional | Four new semantic identities and one foundational successor version. |','| Revised six-meaning cohort | 195 | 188, conditional | Five new semantic identities and one foundational successor version; selected Pack/Define candidate.4 replaces candidate.3 in this review. |'),
 ('The full five-meaning mixed-registry/Project State visibility recipe','The revised six-meaning mixed-registry/Project State visibility recipe'),
 ('The incident criterion needs its own domain/assurance/review closure if selected for actual admission; it is not silently included in the five-meaning cohort.','The incident criterion needs its own domain/assurance/review closure if selected for actual admission; its task-local proposal remains embedded and is not included in the six-meaning cohort.'),
 ('- All 17 registered assurance follow-ups, with their bounded claim ceilings retained.','- Fresh fidelity/non-collapse correspondence and impact closure for the new application meaning and changed Pack/Define bytes; earlier acceptance is not transferred.\n- Production qualification of embedded selectors, parameter contracts, optional assessments, explicit materialization and epoch invalidation.\n- All 17 registered assurance follow-ups, with their bounded claim ceilings retained.'),
]
for old,new in replacements:
    check('model-replacement:'+old[:65],old in main)
    main=main.replace(old,new)
application_section='''### Meaning, application and assessment

The reusable meaning is selected exactly once. A Definition application supplies the task values under its declared parameter contract. A separately attributable assessment records what was established for those values and evidence.

```text
Meaning: every required ID appears in the saved output
    ↓ declared parameter substitution
Application: S-1042 / Northstar / status=active / E-1042
    ↓ separately executed synthetic inclusion comparison
Assessment: 12,000 required / 11,800 present / 200 missing → FAIL
```

All three records, plus the selected input evidence, live in [one incident Pack](incident-pack.json). The application is `/applications/0`; its assessment is `/assessments/0`; the unadmitted working proposal is `/working_meanings/0`. Local subtree digests bind those exact values without requiring a self-hash of the containing Pack. The complete Pack file is sealed separately for subsequent retrieval.

Changing E to a saved retry creates a new application and assessment revision under the same meaning. Allowing 1% missing changes the criterion: an undeclared tolerance is rejected as a parameter substitution. Missing required parameters remain explicit gaps; unknown required population yields NOT_EVALUABLE. Established empty population is different and satisfies inclusion.

An application can have no assessment, or several separately bound assessments. Define preparation records supplied assessment provenance; it does not automatically run one. Assessments in this fixture are illustrative criterion results, not new globally admitted artifacts or complete Evaluation/Measurement Result carriers. Requiring those governed claims still requires their existing contracts.

### Storage, authority and materialization

Applications, task values and assessments stay inside the task Pack by default. A new task-local proposed meaning also stays embedded and unadmitted. `propose` remains its handling disposition; this is not a fifth disposition or an extra lifecycle state.

Selecting a separately materialized Definition requires an explicit purpose, intended authority scope and applicable owner route. A one-use consequential criterion may warrant this; frequency alone does not select admission. Embedding is a storage decision, not an authority exemption, and cannot override an applicable admitted meaning or Policy.

When a result/decision cites the Pack, preserve the exact full Pack and selected evidence. Retention/archive follows applicable rules; no deletion or expiry is selected here. Routine context can be a bounded view rather than loading all completed-task details. Durable task state still uses the applicable Project State route; the agent remains Session-bound.

'''
main=main.replace('### How the agent uses the result',application_section+'### How the agent uses the result')
main=main.replace('The registration proposal has two new profile/v2 type registrations','Definition application is one new reusable semantic Definition carried by existing Definition/v2. Its embedded task records create no new Artifact Type registration. The registration proposal has two new profile/v2 type registrations')
main=main.replace('The following selected final activation recipe remains prospective.','The revised activation recipe adds Definition application after the applicable profiles and foundation, before revised Pack/Define. The table below retains the prior foundation/profile stages; the new meaning and revised meanings require fresh evidence. The exact revised ordering is in [model.json](model.json).')
main=main.replace('| PACK-AND-DEFINE |','| DEFINITION-APPLICATION | PROFILE-ADOPTION, FOUNDATIONAL-SUCCESSOR, DEFINITION-BINDING | New exact v2 meaning review and owner effects; pending |\n| PACK-AND-DEFINE |')
main=main.replace('| PACK-AND-DEFINE | PROFILE-ADOPTION, FOUNDATIONAL-SUCCESSOR, DEFINITION-BINDING |','| PACK-AND-DEFINE | PROFILE-ADOPTION, FOUNDATIONAL-SUCCESSOR, DEFINITION-BINDING, DEFINITION-APPLICATION |')
main=main.replace('The existing amended work map has 79 items.','The existing amended work map has 79 items. [Integration amendments](integration-amendments.json) map this change into its meaning, contract, exporter, handling, review, state and verification areas; those amendments are proposed and runtime enforcement remains pending.')
write('MODEL.md',main)
appendix=['# Revised definitions and complete supporting contracts','','This collection replaces the selected Pack/Define meanings for this review and adds Definition application. Previous frozen candidate material remains history; changed bytes have no inherited fidelity acceptance.','']
for s in selected:
    d=read(s['path'])
    appendix+=['## '+d['term'],'',link(s['path'],'Canonical candidate JSON')+' · SHA256 `'+s['sha256']+'`','',(ROOT/s['human_projection']['path']).read_text(),'']
appendix+=['## Embedded Pack contract','',link(PREFIX+'/pack-embedding.schema.json','Full proposed closed preview schema'),'',link(PREFIX+'/incident-pack.json','Incident values, working proposal, application, assessment and evidence in one file'),'',link(PREFIX+'/incident-controls.json','Executed synthetic controls'),'',link(PREFIX+'/integration-amendments.json','Full integration amendments'),'',
           '## Preserved evaluation/lifecycle contracts, limits and all 79 planning items','',link(str((OLD/'CONTRACTS.md').relative_to(ROOT)),'Prior complete supporting contracts'),'',
           'The prior appendix includes historic Pack/Define candidate.3. Use the revised candidates above for this review. The unchanged evaluation/lifecycle concrete profiles, three unchanged meanings, registered limits and original planning declarations retain their exact bytes.','']
write('CONTRACTS.md','\n'.join(appendix))

# Scope-qualified review observations. Fresh binding/structure controls do not
# substitute for owner fidelity review or the full pending formal package.
for s in selected:
    check('selected-digest:'+s['definition_ref'],file_ref(s['path'])['sha256']==s['sha256'])
check('historical-registry-preserved',entries[:189]==registry['entries'])
for entry in protected:check('live-preserved:'+entry['path'],file_ref(entry['path'])==entry)
for name in ['MODEL.md','CONTRACTS.md','DEFINITIONS-INDEX.md']:
    for target in re.findall(r'\]\(([^)]+)\)',(OUT/name).read_text()):
        if target.startswith(('http:','https:','#')) or target in ['REVIEW.md','review-report.json']:continue
        check('link:'+name+':'+target,(OUT/target.split('#')[0]).exists())
review={
    'schema_version':'cal.define-application-model-self-review/v1','authority_effect':'none','reviewer':'authoring assistant self-review; not an independent owner determination',
    'checks':checks,'passed_checks':len(checks),'failed_checks':0,
    'synthetic_controls':len(cases),'review_findings':[
        {'finding':'Definition application could collapse with a Definition or model inheritance binding','resolution':'Declared parameter substitution and captured standing only; six explicit distinction arguments and application-without-assessment witness retained.'},
        {'finding':'New task-local meaning could bypass shared admission or governing Policy','resolution':'Explicit working-proposal posture; no admitted reuse/permission and no shared selection; governed use remains independently qualified.'},
        {'finding':'Assessment could be fabricated by preparing a binding or by storing counts','resolution':'Separate producer/execution posture, exact application/evidence digests and actual locally computed inclusion; not labeled complete governed Evaluation or Measurement Result.'},
        {'finding':'All four dispositions might force independent file creation','resolution':'Embedded materialization default for new working proposals; explicit selected-definition-preparation for shared/persistent normative admission targets.'},
        {'finding':'Changed Pack/Define bytes could inherit old acceptance and exact postimages','resolution':'New candidate.4 sources, fresh six-meaning registry preview and reopened fidelity/assurance/consumer/postimage requirements; old seals preserved.'},
        {'finding':'Saved retry could silently reuse old assessment','resolution':'New Pack/application/assessment epoch binds new E; stale application and evidence controls reject reuse of old assessment.'},
    ],
    'formal_assurance_status':'new scoped fixture witnesses and boundary review only; complete fresh formal correspondence pending',
    'prior_assurance_acceptance_transferred':False,'production_runtime_tests_executed':False,'independent_owner_fidelity_accepted':False,
    'source_contract_limits':'Preview schema enforces local shape, not a complete production generic Pack, Evaluation or Measurement Result contract. Production adapter/evaluator/currentness and owner effects remain pending.',
    'admission_ready':False,'actual_admissions':0,'application':False,'protected_live_material':protected,
}
write('review-report.json',review)
write('REVIEW.md',f'''# Revised model review

The authoring assistant reviewed this revision before presentation. **{len(checks)} scoped checks passed; zero failures.** There are **{len(cases)} executed local synthetic criterion/integrity controls**, plus the application-without-assessment and retry-epoch checks.

The incident Pack keeps the working meaning, S/A/F/E values, application, assessment and saved synthetic evidence together. The initial output fails inclusion by 200 identifiers; a separately bound retry passes. Extras can still pass inclusion; exclusivity remains open. Unknown required population and incompatible/missing inputs remain NOT_EVALUABLE. Undeclared tolerance, stale hashes and relabeling a candidate as admitted are rejected or visibly blocked.

New reusable meaning: Definition application candidate.1. Revised meanings: Definition Pack and CyberAlchemy Define candidate.4. Foundational Definition and the two profile meanings remain candidate.3. All six are unadmitted.

## Review limits and outstanding work

- This is self-review, not independent semantic-owner acceptance. The six distinction arguments are scoped witnesses, not unrestricted natural-language equivalence or whole-repository consistency proof.
- Old candidate.3 meaning acceptance and formal assurance are not transferred to new/changed bytes. Fresh formal correspondence, fidelity, applicable profile standing, impact and exact postimage review remain required.
- The closed embedding schema is a proposed preview contract; the generic production adapter/exporter and complete Evaluation/Measurement Result conformance remain pending.
- All previous owner mapping gates and registered assurance limits remain visible. No admission, type registration, agent authority, incident closure, current lookup change or application occurred.

Read [the complete revised model](MODEL.md), [Definition application](definitions/definition-application/DEFINITION.md), [the incident Pack](incident-pack.json), [the full review observations](review-report.json) and [integration amendments](integration-amendments.json).
''')
write('source-bindings.json',{'authority_effect':'none','source_epoch':'captured for this revised candidate package','inputs':sorted(inputs.values(),key=lambda x:x['path']),'candidate_couplings':[{'from':'Pack candidate.4 / Define candidate.4','to':app_subject,'posture':'candidate dependency, not admitted source'}]})
files=[file_ref(x) for x in sorted(OUT.rglob('*')) if x.is_file() and x.name not in ['package-manifest.json','verification.json','routing-boundaries.json'] and '__pycache__' not in x.parts]
write('package-manifest.json',{'schema_version':'cal.define-application-model-manifest/v1','status':'frozen revised candidate review; admission unselected','authority_effect':'none','predecessor':file_ref(OLD/'package-manifest.json'),'files':files,'selected_meanings':selected,'exclusions':['manifest itself','later verification/routing receipts','mutable navigation/progress','private/live operator state'],'actual_owner_decision_ref':None,'admission_ready':False,'application':False})
print(json.dumps({'model':str(OUT/'MODEL.md'),'checks_passed':len(checks),'synthetic_controls':len(cases),'selected_meanings':len(selected),'files_sealed':len(files),'manifest':file_ref(OUT/'package-manifest.json')},indent=2))
