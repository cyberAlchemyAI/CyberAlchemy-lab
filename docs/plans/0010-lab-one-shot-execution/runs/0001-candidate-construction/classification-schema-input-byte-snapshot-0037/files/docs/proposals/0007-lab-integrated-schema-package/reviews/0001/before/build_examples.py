#!/usr/bin/env python3
"""Create clearly illustrative protocol examples and workflow model candidates."""
import copy,hashlib,json
from pathlib import Path
from resources import HERE,ROOT,build_registry
REG=build_registry()
PREFIX='urn:cyberalchemy-lab:protocol:'
ZERO='0'*64
WORK_BODY=json.loads((ROOT/'authority/admissions/first-governed-agent-work-episode/v1/instances/artifacts/work.json').read_text())
WORK_SHA=hashlib.sha256((ROOT/'authority/admissions/first-governed-agent-work-episode/v1/instances/artifacts/work.json').read_bytes()).hexdigest()

def dump(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def merge(a,b):
    result=copy.deepcopy(a)
    for k,v in b.items():
        if k=='required':result[k]=list(dict.fromkeys(result.get(k,[])+v))
        elif k=='properties':
            result.setdefault(k,{})
            for key,value in v.items():result[k][key]=merge(result[k].get(key,{}),value)
        else:result[k]=copy.deepcopy(v)
    return result

def flatten(s,base):
    s=copy.deepcopy(s)
    base=s.get('$id',base)
    if '$ref' in s:
        resolved=REG.resolver(base_uri=base).lookup(s.pop('$ref'))
        s=merge(flatten(resolved.contents,resolved.resolver._base_uri),s)
    if 'allOf' in s:
        items=s.pop('allOf')
        for item in items:
            # if/then branches constrain values; apply later after discriminator generation.
            if 'if' not in item:s=merge(s,flatten(item,base))
            else:s.setdefault('allOf',[]).append(item)
    return s

def art(kind='work'):
    refs=json.loads((HERE/'domain-bindings.json').read_text())['bindings']
    normalized={'project':'project-identity','product':'product-identity'}.get(kind,kind)
    binding=next(x for x in refs if (x['semantic_kind']==kind or x['carrier_ref'].split('/')[0].split('.')[-1]==normalized) and x['write_posture']=='current')
    return {'scope_ref':'example:scope','identity_ref':WORK_BODY['node_id'] if kind=='work' else 'example:'+kind,'version_ref':(WORK_BODY['node_id'] if kind=='work' else 'example:'+kind)+'@example.1','carrier_ref':binding['carrier_ref'],'byte_sha256':WORK_SHA if kind=='work' else ZERO}

def connection():
    c=json.loads((ROOT/'docs/plans/0009-lab-integrated-roadmap/contract-coverage.json').read_text())
    r=next(x for x in c['relations'] if x['ref']=='relation.member-of')
    return {'relation_kind_ref':r['ref'],'signature_sha256':r['source_sha256'],'axis_ref':r['axis_id'],
      'source':{'artifact':art('work'),'semantic_kind':'work'},'target':{'artifact':art('project'),'semantic_kind':'project'},'qualifiers':{'membership_role':'example:bounded-work'}}

def sample(s,base='',key=''):
    if s.get('$ref')==PREFIX+'domain-artifact:v1-candidate':return {'carrier_ref':'cal.artifact-type.work/v1','body':copy.deepcopy(WORK_BODY)}
    if s.get('$ref')==PREFIX+'typed-connection:v1-candidate':return connection()
    if s.get('$ref')==PREFIX+'artifact-envelope:v1-candidate':
        v=sample(json.loads((HERE/'schemas/artifact-envelope.schema.json').read_text()),PREFIX+'artifact-envelope:v1-candidate')
        v['artifact']=art();v['content']['byte_sha256']=WORK_SHA;v['content']['size_bytes']=(ROOT/'authority/admissions/first-governed-agent-work-episode/v1/instances/artifacts/work.json').stat().st_size;v['content']['media_type']='application/json'
        return v
    s=flatten(s,base);base=s.get('$id',base)
    if s.get('title')=='Dispatch to exact registered artifact contract':return {'carrier_ref':'cal.artifact-type.work/v1','body':copy.deepcopy(WORK_BODY)}
    if s.get('title')=='Declared exact endpoint-pair and qualifier dispatcher':return connection()
    if 'const' in s:return copy.deepcopy(s['const'])
    if 'enum' in s:
        choices=s['enum']
        # Prefer candidate/blocked dispositions, so examples cannot be mistaken for execution evidence.
        preferred=['candidate','blocked','denied','not-evaluable','rejected','pending','building','indeterminate','no-retry']
        return next((x for x in preferred if x in choices),choices[0])
    if 'oneOf' in s or 'anyOf' in s:
        return sample((s.get('oneOf') or s.get('anyOf'))[0],base,key)
    kind=s.get('type')
    if isinstance(kind,list):kind=next((k for k in kind if k!='null'),'null')
    if kind=='object':
        result={k:sample(s.get('properties',{}).get(k,{}),base,k) for k in s.get('required',[])}
        for rule in s.get('allOf',[]):
            if 'if' not in rule:continue
            conditions=rule['if'].get('properties',{})
            if all(result.get(k)==v.get('const') for k,v in conditions.items()):
                for k,v in rule['then'].get('properties',{}).items():result[k]=sample(v,base,k)
        return result
    if kind=='array':return [sample(s['items'],base,key) for _ in range(s.get('minItems',0))]
    if kind=='integer' or kind=='number':return s.get('minimum',0)
    if kind=='boolean':return False
    if kind=='null':return None
    if kind=='string':
        if s.get('format')=='date-time':return '2026-10-07T12:00:00Z' if key in ('expires_at','deadline') else '2026-10-07T10:00:00Z'
        if s.get('pattern')=='^[a-f0-9]{64}$':return ZERO
        if key=='managed_relative_paths':return 'artifacts/example.json'
        return 'Illustrative shape only; not executed or authorized.' if key=='claim_ceiling' else 'example:value'
    return None

catalog=json.loads((HERE/'schema-catalog.json').read_text())
for p in catalog['protocols']:
    if p['name']=='common':continue
    s=json.loads((HERE/p['path']).read_text());value=sample(s,s['$id'])
    if p['name']=='artifact-envelope':
        value['artifact']=art();value['content']['byte_sha256']=WORK_SHA;value['content']['size_bytes']=(ROOT/'authority/admissions/first-governed-agent-work-episode/v1/instances/artifacts/work.json').stat().st_size
    dump(HERE/'examples'/f'{p["name"]}.json',value)

# The runtime profile states below are proposed workflow coordination states,
# independent of each domain artifact's admission and completion vocabularies.
profiles=[
 ('intent-framing',['intent','goal','coordination-context'],['intent-resolution','work'],['framed','resolved','prepared']),
 ('agent-context',['agent-assignment','delegation','context-request'],['context-view','ontology-view','agent-session'],['requested','context-ready','session-ready']),
 ('engineering',['intent-resolution','work','implementation'],['generated-output','evidence-set','work-outcome-assessment'],['prepared','designed','implemented','assessed']),
 ('research',['research-inquiry','hypothesis','experiment-design'],['experiment-run','measurement-result','finding','evaluation'],['prepared','designed','executed','evaluated']),
 ('failure-assessment',['failure-occurrence','evidence-set'],['classification-assignment','failure-assessment','failure-control-binding'],['observed','classified','assessed','response-assessed']),
 ('challenge-handling',['challenge-contract','challenge-event'],['decision','challenge-event'],['submitted','eligible','responded','resolved']),
 ('operational-learning',['operational-observation','work-outcome-assessment'],['operational-lesson','lesson-application','lesson-outcome-assessment','improvement-signal'],['observed','lesson-prepared','application-recorded','outcome-assessed']),
 ('review-admission',['decision-bundle','decision-checkpoint','decision-scope'],['admission-transaction','project-state','project-semantic-event-history','project-governance-event-history'],['prepared','review-ready','owner-resolved','applied']),
 ('ontology-migration',['source','source-admission','typed-relation'],['ontology-node','ontology-edge','ontology-cut','ontology-view','repository-migration-manifest'],['selected','mapped','candidate-validated','selected-scope-assessed']),
 ('product-adoption-release',['product-identity','product-capability','implementation'],['capability-realization-binding','work-outcome-assessment','decision'],['scoped','candidate-assessed','pilot-assessed','release-reviewed']),
]
current={b['semantic_kind']:b['carrier_ref'] for b in json.loads((HERE/'domain-bindings.json').read_text())['bindings'] if b['write_posture']=='current'}
identity_current={b['carrier_ref'].split('/')[0].split('.')[-1]:b['carrier_ref'] for b in json.loads((HERE/'domain-bindings.json').read_text())['bindings'] if b['write_posture']=='current'}
def carrier(k):return identity_current[k]
stage_outputs={
 'intent-framing':[['intent-resolution'],['work']],
 'agent-context':[['context-view','ontology-view'],['agent-session']],
 'engineering':[['generated-output'],['generated-output','evidence-set'],['work-outcome-assessment']],
 'research':[['experiment-design'],['experiment-run','measurement-result'],['finding','evaluation']],
 'failure-assessment':[['classification-assignment'],['failure-assessment'],['failure-control-binding']],
 'challenge-handling':[['challenge-event'],['challenge-event'],['decision','challenge-event']],
 'operational-learning':[['operational-lesson'],['lesson-application'],['lesson-outcome-assessment','improvement-signal']],
 'review-admission':[['decision-bundle','decision-checkpoint'],['decision'],['admission-transaction','project-state','project-semantic-event-history','project-governance-event-history']],
 'ontology-migration':[['ontology-node','ontology-edge'],['ontology-cut','ontology-view'],['repository-migration-manifest']],
 'product-adoption-release':[['capability-realization-binding'],['work-outcome-assessment'],['decision']],
}
models=[]
for name,inputs,outputs,states in profiles:
    outputs=list(dict.fromkeys(outputs+[k for group in stage_outputs[name] for k in group]))
    transitions=[]
    for i,(old,new) in enumerate(zip(states,states[1:])):
        owner_step=(name,new) in [('review-admission','owner-resolved'),('challenge-handling','resolved'),('product-adoption-release','release-reviewed')]
        application_step=name=='review-admission' and new=='applied'
        transitions.append({'transition_ref':'transition:'+name+':'+new,'from_state':old,'to_state':new,
          'actor_role_refs':['role:accountable-owner' if owner_step else ('role:authorized-application-adapter' if application_step else 'role:assigned-worker')],
          'input_carriers':[carrier(k) for k in list(dict.fromkeys(inputs+[k for group in stage_outputs[name][:i] for k in group]))],'output_carriers':[carrier(k) for k in stage_outputs[name][i]],
          'authority_requirement_refs':['obligation:exact-owner-outcome' if owner_step else 'obligation:bounded-current-authority'],
          'precondition_refs':['obligation:exact-source-and-reference-closure'],'satisfaction_check_refs':['obligation:'+name+':'+new],
          'relation_requirement_refs':['obligation:declared-exact-connections'],'failure_state':'blocked','indeterminate_state':'indeterminate'})
    model={'schema_version':'lab-workflow-definition/v1-candidate','workflow_type_ref':'workflow:'+name+':v1-candidate','version':'1-candidate','states':states+['blocked','indeterminate','cancelled'],
      'initial_state':states[0],'terminal_states':[states[-1],'cancelled'],'transitions':transitions,'decision_profile':art('workflow-decision-profile'),
      'single_goal_coordination':True,'domain_mapping_bindings':[],'challenge_route':'route:workflow-owner','authority_effect':'none'}
    path=HERE/'workflows'/f'{name}.json';dump(path,model)
    models.append({'name':name,'path':str(path.relative_to(HERE)),'input_carriers':[carrier(k) for k in list(dict.fromkeys(inputs+[k for group in stage_outputs[name][:i] for k in group]))],'output_carriers':[carrier(k) for k in stage_outputs[name][i]],
      'status':'proposed-model','domain_mapping_posture':'must-bind-explicit-domain-lifecycle-and-actor-routes-before-execution'})
dump(HERE/'workflow-catalog.json',{'schema_version':'lab-workflow-catalog/v1-candidate','authority_effect':'none','workflows':models})
print(json.dumps({'illustrative_examples':len(catalog['protocols'])-1,'workflow_models':len(models)}))
