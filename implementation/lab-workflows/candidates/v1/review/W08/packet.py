"""Exact candidate workflow review preparation; no admission or effect dispatch."""
import copy
import hashlib
import json
from pathlib import Path,PurePosixPath
from jsonschema import Draft202012Validator

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
PACKAGE=HERE.parents[1]
RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
W07={'path':'implementation/lab-workflows/candidates/v1/receipts/integration/W07/0004.json','sha256':'3e40e0cb64a479b5546a30c069dc009c950b78a8a6357e0bd58b8e92ea840203'}
CONTEXT_SHA='08c6eb2ff09481570b944deceab067980a9d1d4bf35ea308429035dc9d56f397'
EXCLUSIONS=['canonical admission before R08','local action permission','service activation','external effects','private Session memory',
    'automatic Lesson promotion','general Product benefit','unqualified fixture postimage merge','human pilot inference','blanket completion of every design transition']
INVALIDATION=['target bytes changed','source or evidence cut changed','selected effect or scope changed','owner authority unresolved or changed','independent member omitted']
OWNER_FIELDS={'actual_owner_outcome':None,'actual_answering_principal_ref':None,'current_owner_authority_verified':False,'authority_effect':'none'}


def require(value,message):
    if not value:raise ValueError(message)


def encoded(value):return (json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False)+'\n').encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def parse(raw):
    def closed(pairs):
        d={}
        for k,v in pairs:require(k not in d,'duplicate JSON key');d[k]=v
        return d
    return json.loads(raw,object_pairs_hook=closed)
def binding(p):
    p=Path(p);p=ROOT/p if not p.is_absolute() else p
    return {'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes())}
def bound(b):
    require(type(b) is dict and set(b)=={'path','sha256'},'closed exact original binding required')
    p=PurePosixPath(b['path']);require(not p.is_absolute() and '..' not in p.parts and p.as_posix()==b['path'],'unsafe original path')
    f=ROOT/b['path'];require(f.is_file() and f.resolve().is_relative_to(ROOT) and not f.is_symlink() and not any(x.is_symlink() for x in f.parents),'unsafe original file')
    raw=f.read_bytes();require(sha(raw)==b['sha256'],'original binding changed: '+b['path']);return raw

def original(b):return parse(bound(b))

def put(p,value):
    with Path(p).open('xb') as stream:stream.write(encoded(value))

def prerequisite():
    receipt=original(W07)
    require(receipt['result']=='PASS' and receipt['task_complete'] and receipt['model_integration_result']=='PASS' and receipt['tests']==302
        and receipt['remaining_runtime_kind_gaps']==0 and receipt['actual_owner_outcome'] is None,'complete exact W07 candidate proof required')
    for b in receipt['files']:bound({'path':b['path'],'sha256':b['sha256']})
    return receipt

def member(ref,kind,targets,evidence,roles,effect,scope,selected=None):
    value={**OWNER_FIELDS,'member_ref':ref,'member_class':kind,'admission_posture':'candidate-unadmitted','targets':targets,
        'evidence':evidence,'proposed_owner_roles':roles,'requested_effect':effect,'scope':scope,'exclusions':EXCLUSIONS,
        'invalidation':INVALIDATION,'selected_record':selected,'selected_outcome':None,'application_route':'S02/R08 exact member preparation; A01 only after actual complete owner response'}
    for b in targets+evidence:bound(b)
    return value


def build():
    proof=prerequisite();context=original(binding(RUN/'context-W08.json'))
    for b in context['source_bindings']:bound(b)
    output=HERE/'packages/0001';output.mkdir(parents=True,exist_ok=False);post=output/'postimages';post.mkdir()
    models=original(binding(PACKAGE/'design/transition-contracts.json'));members=[];coverage=[]
    cases_index=original({'path':'implementation/lab-workflows/candidates/v1/tests/signed_integration/selection.json',
        'sha256':'6e5d8e24325e45c6801d64161b23539190c78befb2bf9d8f1a9d0f2819ffb1db'})
    case_bindings={original(b)['domain']:b for b in cases_index['cases']}
    selected_case={'agent-context':['learning'],'engineering':['engineering'],'research':['research'],
        'failure-assessment':['failure'],'challenge-handling':['failure'],'operational-learning':['learning']}
    for index,model in enumerate(models['workflows']):
        name=model['name'];p=post/(name+'.json');put(p,model);evidence=[W07]+[case_bindings[d] for d in selected_case.get(name,[])]
        source_selector={'parent_binding':binding(PACKAGE/'design/transition-contracts.json'),'json_pointer':'/workflows/'+str(index)}
        scope={'model_only':True,'workflow':name,'source_selection':source_selector,'per_run_bindings_required':True,'original_executable_flag':model['executable'],
            'observed_case_domains':selected_case.get(name,[]),'all_transitions_operationally_complete':False}
        members.append(member('protocol:W08:workflow:'+name,'workflow-transition-protocol',[binding(p),model['source_binding']],evidence,
            ['role:repository-owner'],'Select the exact bounded transition contract as a model; each future execution requires independently resolved actors, authority, schemas, relations and satisfaction evidence.',scope,model))
        coverage.append({'workflow':name,'model_prepared':True,'observed_candidate_domains':scope['observed_case_domains'],
            'remaining_per_run_obligations':[g for t in model['transitions'] for g in t['gaps']],
            'execution_coverage':'bounded-original-candidate-example' if scope['observed_case_domains'] else 'design-only-no-selected-runtime-example',
            'all_transitions_operationally_complete':False})
    schema_dir=post/'schemas';schema_dir.mkdir()
    schemas=[]
    for name in ('common.schema.json','workflow-run.schema.json'):
        source=PACKAGE/'schemas'/name;target=schema_dir/name;target.write_bytes(source.read_bytes());schemas.append(binding(target))
    members.append(member('protocol:W08:workflow-run-schemas','workflow-protocol-schema',schemas,[binding(PACKAGE/'receipts/W01-0001.json'),W07],
        ['role:repository-owner'],'Select the exact shared protocol validation contracts; no new Artifact Type or carrier admission is declared.',
        {'protocol_only':True,'Artifact_Type_added':False,'workflow_status_is_not_admission':True}))
    boundary_paths=[PACKAGE/p for p in ('authority/BOUNDARY.md','authority/evaluator.py','authority/action.py','authority/dispatch.py','evidence/service.py')]
    members.append(member('protocol:W08:Agent-Tool-boundary','implementation-action-boundary',[binding(p) for p in boundary_paths],
        [binding(PACKAGE/'receipts/action-boundaries/0004.json'),W07],['role:repository-owner'],
        'Select the exact bounded Agent/Tool evaluator, action and evidence implementations; actual action grants remain independent and current per operation.',
        {'machine_Agent_ephemeral':True,'short_memory_owner':'Session','durable_memory_sources':['Project State','Context View','Ontology View'],'action_permission_included':False}))
    # Exact upstream review targets are scoped separately from generated episodic observations.
    selected=[]
    for domain in ('engineering','research'):
        case=original(case_bindings[domain])
        for r in case['records']:
            if r['kind']=='implementation' and r['role']=='output':selected.append((domain,r['version_ref'],{'path':r['path'],'sha256':r['sha256']},case_bindings[domain]))
    for family,receipt in [('failure',PACKAGE/'failures/receipts/0004.json'),('learning',PACKAGE/'learning/receipts/0002.json')]:
        v=original(binding(receipt))
        for r in v['review_members']:selected.append((family,r['version_ref'],r['target'],binding(receipt)))
    selected_records=[]
    for family,version,b,evidence in selected:
        value=original(b);kind=value['kind'];file=post/(sha(version.encode())[:24]+'.json');file.write_bytes(bound(b))
        scope={'exact_version_ref':version,'source_binding':b,'controlled_candidate_scope':value['scope_ref'],'original_fixture_owner_ref':value['owner_ref'],
            'fixture_owner_is_final_owner':False,'operational_use_authorized':False,'current_use_from_this_member':False}
        effect='Prepare exact controlled implementation record and its source/evidence lineage for final review; no callable runtime binding or activation is conferred by the artifact.'
        if kind=='operational-lesson':
            scope.update(historical_retention_only=True,expires_at=value['payload']['expires_at'],expiry_observation_binding=binding(HERE/'lesson-expiry-observation.json'),
                current_application_permission=False,new_scope_requires_new_revision_and_review=True)
            effect='Retain this exact expired scoped Lesson as historical candidate evidence; current application, broader scope and automatic promotion are excluded.'
        members.append(member('protocol:W08:'+version,'scoped-Lesson-evidence' if kind=='operational-lesson' else 'implementation-carrier',
            [binding(file),b],[evidence,W07],['role:repository-owner'],effect,scope,value));selected_records.append({'version_ref':version,'source_binding':b,'postimage_binding':binding(file),'family':family})
    join=original(proof['warm_join_binding']);conflicts=[]
    cases={original(b)['case_id']:original(b) for b in cases_index['cases']}
    for conflict in join['candidate_postimage_collisions']:
        witnesses=[]
        for cid in (conflict['left_case'],conflict['right_case']):
            r=next(r for r in cases[cid]['records'] if r['version_ref']==conflict['version_ref'])
            witnesses.append({'case_id':cid,'domain':cases[cid]['domain'],'binding':{'path':r['path'],'sha256':r['sha256']}})
        conflicts.append({**conflict,'witnesses':witnesses,'review_disposition':'case-qualified-evidence-only; excluded-from-canonical-targets',
            'new_run_identity_route':'W09/R03 explicit exact run/store namespace adaptation before affected writes; no alias or rewritten historical record'})
    for m in original(binding(PACKAGE/'tests/signed_integration/review-members.json'))['members']:
        members.append(member(m['member_ref'],m['kind'],m['bindings'],[W07],['role:repository-owner'],
            'Select exact integration verification code or witness selection; no canonical admission or operation authority follows from a passing result.',
            {'verification_only':True,'model_evidence_task':'W07'}))
    v={'schema_version':'lab-W08-review-preparation/v1-candidate','task':'W08','status':'prepared-for-final-S02-R08-review',**OWNER_FIELDS,
        'complete_final_package':False,'final_checkpoint':'R08','application_task':'A01','atomicity':'The eventual whole selected S02 bundle is indivisible; independent member scopes and Decision cores remain separate.',
        'upstream_workflow_proof_binding':W07,'source_context_binding':binding(RUN/'context-W08.json'),
        'members':members,'model_coverage':coverage,'selected_carrier_postimages':selected_records,'candidate_collision_dispositions':conflicts,
        'global_merge_performed':False,'canonical_effects_applied':0,'local_transactions_applied':0,'lessons_promoted':0,
        'all_workflow_transitions_executed':False,'runtime_activation':False,'human_pilot':False,'operational_permissions_granted':0,
        'model_execution_gaps_retained':sum(len(r['remaining_per_run_obligations']) for r in coverage),
        'final_assembly_obligations':['Bind actual answering principal and current accountable owner authority at S02/R08.',
            'Join exact schema, semantic mapping, executable/environment/entrypoint, correction/publisher and registry effects independently.',
            'Keep case-qualified fixtures and expired Lesson historical; resolve fresh run identities and current Lesson revisions before affected operation.',
            'Recompute source/target/evidence currentness for the complete final bundle; changed bytes require a new exact review.',
            'Complete remaining APIs, queries, migration, real pilot, S02 and actual R08 before canonical authority application.'],
        'claim_ceiling':'Closed candidate workflow review preparation only. Ten models and independent code/scoped historical Lesson members are exact; design gaps, fixture owners, final authority, operational use and wider Product evidence remain separately unresolved.'}
    put(output/'preparation.json',v);validate(v);print(encoded({'result':'PASS','preparation':binding(output/'preparation.json'),'members':len(members),
        'models':len(coverage),'transitions':sum(len(m['selected_record']['transitions']) for m in members if m['member_class']=='workflow-transition-protocol'),
        'model_execution_gaps_retained':v['model_execution_gaps_retained'],'selected_carrier_postimages':len(selected_records)}).decode(),end='')


def validate(v):
    schema=original(binding(HERE/'preparation.schema.json'));Draft202012Validator.check_schema(schema);Draft202012Validator(schema).validate(v)
    require(v['schema_version']=='lab-W08-review-preparation/v1-candidate' and v['task']=='W08' and v['status']=='prepared-for-final-S02-R08-review','packet identity differs')
    require(all(v[k]==value for k,value in OWNER_FIELDS.items()) and v['complete_final_package'] is False,'invented owner authority or complete final package')
    require(v['final_checkpoint']=='R08' and v['application_task']=='A01','owner/application route changed')
    require(v['upstream_workflow_proof_binding']==W07,'independently pinned workflow proof differs')
    require(v['source_context_binding']=={'path':str((RUN/'context-W08.json').relative_to(ROOT)),'sha256':CONTEXT_SHA},'independent task source context differs')
    for b in original(v['source_context_binding'])['source_bindings']:bound(b)
    require(len(v['members'])==27 and len({m['member_ref'] for m in v['members']})==27,'independent complete member partition differs')
    for k in ('canonical_effects_applied','local_transactions_applied','lessons_promoted','operational_permissions_granted'):require(v[k]==0,'invented preparation effect')
    require(all(v[k] is False for k in ('global_merge_performed','all_workflow_transitions_executed','runtime_activation','human_pilot')),'invented execution or pilot result')
    models=original(binding(PACKAGE/'design/transition-contracts.json'));model_members=[m for m in v['members'] if m['member_class']=='workflow-transition-protocol']
    require(len(model_members)==len(models['workflows'])==10 and v['model_execution_gaps_retained']==56,'model or execution obligations omitted')
    all_refs=set()
    for m in v['members']:
        require(all(m[k]==value for k,value in OWNER_FIELDS.items()) and m['selected_outcome'] is None and m['admission_posture']=='candidate-unadmitted','member supplies owner or admission authority')
        require(m['exclusions']==EXCLUSIONS and m['invalidation']==INVALIDATION and m['proposed_owner_roles']==['role:repository-owner'],'member effect/exclusion/owner boundary changed')
        require(m['requested_effect'] and m['scope'] and m['targets'] and m['evidence'],'member lacks concrete scope/targets/evidence')
        requests={
            'workflow-transition-protocol':'Select the exact bounded transition contract as a model; each future execution requires independently resolved actors, authority, schemas, relations and satisfaction evidence.',
            'workflow-protocol-schema':'Select the exact shared protocol validation contracts; no new Artifact Type or carrier admission is declared.',
            'implementation-action-boundary':'Select the exact bounded Agent/Tool evaluator, action and evidence implementations; actual action grants remain independent and current per operation.',
            'implementation-carrier':'Prepare exact controlled implementation record and its source/evidence lineage for final review; no callable runtime binding or activation is conferred by the artifact.',
            'scoped-Lesson-evidence':'Retain this exact expired scoped Lesson as historical candidate evidence; current application, broader scope and automatic promotion are excluded.',
            'implementation':'Select exact integration verification code or witness selection; no canonical admission or operation authority follows from a passing result.',
            'verification-source-selection':'Select exact integration verification code or witness selection; no canonical admission or operation authority follows from a passing result.'}
        require(m['requested_effect']==requests[m['member_class']],'member request widens the prepared effect')
        for b in m['targets']+m['evidence']:bound(b)
        if m['selected_record'] is not None:require(original(m['targets'][0])==m['selected_record'],'materialized member differs from selected exact postimage')
        if m['member_class']=='workflow-transition-protocol':
            original_model=next(r for r in models['workflows'] if r['name']==m['scope']['workflow'])
            require(m['selected_record']==original_model and m['scope']['model_only'] and not m['scope']['original_executable_flag']
                and m['scope']['per_run_bindings_required'] and not m['scope']['all_transitions_operationally_complete'],'workflow design changed or execution inferred')
            source_selection=m['scope']['source_selection'];index=models['workflows'].index(original_model)
            require(source_selection=={'parent_binding':binding(PACKAGE/'design/transition-contracts.json'),'json_pointer':'/workflows/'+str(index)},
                'exact model source parent/selector differs')
        if m['member_class']=='implementation-action-boundary':
            require(m['scope']=={'machine_Agent_ephemeral':True,'short_memory_owner':'Session','durable_memory_sources':['Project State','Context View','Ontology View'],
                'action_permission_included':False},'Agent memory or action boundary collapsed')
        if m['member_class']=='scoped-Lesson-evidence':
            s=m['scope'];require(s['historical_retention_only'] and not s['current_application_permission'] and not s['current_use_from_this_member']
                and s['new_scope_requires_new_revision_and_review'],'expired scoped Lesson promoted for current use')
            observation=original(s['expiry_observation_binding']);require(observation['posture']=='expired-for-current-application' and
                observation['source_binding']==s['source_binding'] and observation['expires_at']==s['expires_at'],'Lesson expiry witness differs')
        if 'exact_version_ref' in m['scope']:
            require(m['scope']['exact_version_ref'] not in all_refs and not m['scope']['fixture_owner_is_final_owner']
                and not m['scope']['operational_use_authorized'],'selected carrier ambiguity or fixture authority collapse');all_refs.add(m['scope']['exact_version_ref'])
            require(m['scope']['exact_version_ref'].startswith(m['selected_record']['node_id']+'@')
                and original(m['scope']['source_binding'])==m['selected_record'],'exact carrier identity/source differs')
            carrier='operational-lesson' if m['member_class']=='scoped-Lesson-evidence' else 'implementation'
            Draft202012Validator(original(binding(ROOT/('authority/artifact-types/'+carrier+'/v1/schema.json')))).validate(m['selected_record'])
    require(len(v['selected_carrier_postimages'])==13 and {r['version_ref'] for r in v['selected_carrier_postimages']}==all_refs,'selected carrier partition differs')
    for r in v['selected_carrier_postimages']:require(bound(r['source_binding'])==bound(r['postimage_binding']),'original carrier bytes changed')
    expected=original(original(W07)['warm_join_binding'])['candidate_postimage_collisions']
    require(len(v['candidate_collision_dispositions'])==len(expected)==6,'candidate collisions omitted')
    for c,old in zip(v['candidate_collision_dispositions'],expected):
        require(all(c[k]==value for k,value in old.items()) and not c['global_merge_allowed']
            and c['review_disposition']=='case-qualified-evidence-only; excluded-from-canonical-targets','collision was merged or silently rewritten')
        require(len(c['witnesses'])==2 and {w['case_id'] for w in c['witnesses']}=={c['left_case'],c['right_case']}
            and len({w['binding']['sha256'] for w in c['witnesses']})==2,'independent conflicting postimages collapsed')
        for w in c['witnesses']:bound(w['binding'])
        require(c['version_ref'] not in all_refs,'conflicting episodic record included as canonical target')
    require(len(v['model_coverage'])==10 and {r['workflow'] for r in v['model_coverage']}=={m['name'] for m in models['workflows']}
        and all(not r['all_transitions_operationally_complete'] for r in v['model_coverage'])
        and sum(len(r['remaining_per_run_obligations']) for r in v['model_coverage'])==56,'model coverage/gaps concealed')
    for row in v['model_coverage']:
        model=next(m for m in models['workflows'] if m['name']==row['workflow'])
        require(row['remaining_per_run_obligations']==[g for t in model['transitions'] for g in t['gaps']],
            'named model execution obligations changed')
    return {'result':'PASS','members':27,'workflow_models':10,'carrier_postimages':13,'collision_dispositions':6,'authority_effect':'none'}


if __name__=='__main__':build()
