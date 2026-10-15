"""Bounded declared-record inspection; supplied labels never authenticate admission."""
import copy
import json
import build_candidate as b
import verifier as v

class ProfileFault(ValueError):
    def __init__(self,code):self.code=code
def require(ok,code):
    if not ok:raise ProfileFault(code)
def exact(value,keys,code):require(type(value) is dict and set(value)==set(keys),code)
def label(value):require(type(value) is str and 0<len(value)<=256,'invalid-label')
def refkey(value):
    exact(value,['id','version'],'malformed-instance-or-kind-reference')
    for x in value.values():label(x)
    return value['id'],value['version']
def inspect(value):
    exact(value,['instances','kinds','relations'],'closed-profile-fields')
    for field,limit in [('instances',16),('kinds',8),('relations',32)]:require(type(value[field]) is list and len(value[field])<=limit,'profile-size-limit')
    instances={};kinds={};ids=set()
    for row in value['instances']:
        exact(row,['ref','type'],'malformed-instance-record');key=refkey(row['ref']);label(row['type']);require(key not in instances,'duplicate-instance-reference');instances[key]=row['type']
    for row in value['kinds']:
        exact(row,['ref','admission_label','allowed_pairs','qualifier_roles'],'malformed-kind-record');key=refkey(row['ref']);require(key not in kinds,'duplicate-kind-reference')
        require(row['admission_label']=='admitted','kind-label-not-admitted')
        require(type(row['allowed_pairs']) is list and 0<len(row['allowed_pairs'])<=16,'invalid-allowed-pairs')
        pairs=[]
        for pair in row['allowed_pairs']:
            require(type(pair) is list and len(pair)==2,'malformed-allowed-ordered-pair')
            for item in pair:label(item)
            require(tuple(pair) not in pairs,'duplicate-allowed-pair');pairs.append(tuple(pair))
        require(type(row['qualifier_roles']) is list and 0<len(row['qualifier_roles'])<=8,'invalid-qualifier-roles')
        for role in row['qualifier_roles']:label(role)
        require(len(set(row['qualifier_roles']))==len(row['qualifier_roles']),'duplicate-qualifier-role')
        kinds[key]=row
    accepted=[]
    for row in value['relations']:
        exact(row,['id','source','target','kind','qualifiers','owner_ref','evidence_refs','lifecycle_ref','contestability_ref','scope_ref'],'malformed-relation-record')
        label(row['id']);require(row['id'] not in ids,'duplicate-relation-identity');ids.add(row['id'])
        source=refkey(row['source']);target=refkey(row['target']);kind=refkey(row['kind'])
        require(source in instances and target in instances,'unresolved-exact-endpoint-reference');require(kind in kinds,'unresolved-exact-kind-version')
        require([instances[source],instances[target]] in kinds[kind]['allowed_pairs'],'ordered-endpoint-type-pair-not-allowed')
        exact(row['qualifiers'],['role'],'closed-qualifier-payload');label(row['qualifiers']['role'])
        require(row['qualifiers']['role'] in kinds[kind]['qualifier_roles'],'qualifier-not-allowed-for-kind')
        for key in ['owner_ref','lifecycle_ref','contestability_ref','scope_ref']:label(row[key])
        require(type(row['evidence_refs']) is list and 0<len(row['evidence_refs'])<=8,'missing-or-invalid-evidence-list')
        for item in row['evidence_refs']:label(item)
        accepted.append({'id':row['id'],'ordered_pair':[source,target],'kind':kind,'qualifiers':row['qualifiers']})
    return {'relation_count':len(accepted),'accepted_records':accepted,'actual_admission_authenticated':False,
            'owner_authorized':False,'evidence_support_verified':False,'lifecycle_or_contestability_executed':False,
            'constraint_cycle_safety_proved':False,'source_profile_embedding_reviewed':False}
def fixture():
    return {'instances':[{'ref':{'id':'capability:typed-meaning','version':'v1'},'type':'Capability'},
                         {'ref':{'id':'product:ontology','version':'v1'},'type':'Product'},
                         {'ref':{'id':'capability:second','version':'v1'},'type':'Capability'}],
            'kinds':[{'ref':{'id':'relation.member-of','version':'v1'},'admission_label':'admitted','allowed_pairs':[['Capability','Product']],'qualifier_roles':['product-capability']},
                     {'ref':{'id':'relation.peer','version':'v1'},'admission_label':'admitted','allowed_pairs':[['Capability','Capability']],'qualifier_roles':['peer']}],
            'relations':[{'id':'TR-204','source':{'id':'capability:typed-meaning','version':'v1'},'target':{'id':'product:ontology','version':'v1'},
                          'kind':{'id':'relation.member-of','version':'v1'},'qualifiers':{'role':'product-capability'},'owner_ref':'synthetic-owner',
                          'evidence_refs':['synthetic-evidence:1'],'lifecycle_ref':'synthetic-active','contestability_ref':'synthetic-challenge','scope_ref':'synthetic-bounded'}]}
def cases():
    rows=[]
    def add(name,change,error=None):
        x=fixture();change(x);rows.append({'case_id':name,'input':x,'expected_error':error})
    add('hypothetical-TR-204-member-of-ordered-type-pair',lambda x:None)
    def same_pair(x):
        row=copy.deepcopy(x['relations'][0]);row['id']='TR-205';row['evidence_refs']=['synthetic-evidence:2'];x['relations'].append(row)
    add('two-identities-on-same-endpoints-kind-and-qualifiers',same_pair)
    def loop(x):
        x['relations'][0].update(target=copy.deepcopy(x['relations'][0]['source']),kind={'id':'relation.peer','version':'v1'},qualifiers={'role':'peer'})
    add('explicitly-allowed-self-loop',loop)
    def cycle(x):
        loop(x);first=x['relations'][0];first['target']={'id':'capability:second','version':'v1'}
        second=copy.deepcopy(first);second.update(id='TR-205',source=copy.deepcopy(first['target']),target=copy.deepcopy(first['source']));x['relations'].append(second)
    add('ordinary-directed-cycle-no-global-cycle-ban-or-safety-proof',cycle)
    add('empty-record-set-inspection-vacuous-not-primary-inhabitation',lambda x:x.update(relations=[]))
    add('duplicate-connection-identity-rejected',lambda x:x['relations'].append(copy.deepcopy(x['relations'][0])),'duplicate-relation-identity')
    def swap(x):r=x['relations'][0];r['source'],r['target']=r['target'],r['source']
    add('reverse-ordered-pair-is-not-allowed-by-forward-pair',swap,'ordered-endpoint-type-pair-not-allowed')
    add('wrong-source-instance-version',lambda x:x['relations'][0]['source'].update(version='v2'),'unresolved-exact-endpoint-reference')
    add('unresolved-target-instance',lambda x:x['relations'][0]['target'].update(id='missing'),'unresolved-exact-endpoint-reference')
    add('wrong-kind-version',lambda x:x['relations'][0]['kind'].update(version='v2'),'unresolved-exact-kind-version')
    add('kind-label-not-admitted',lambda x:x['kinds'][0].update(admission_label='candidate'),'kind-label-not-admitted')
    add('qualifier-from-other-kind',lambda x:x['relations'][0]['qualifiers'].update(role='peer'),'qualifier-not-allowed-for-kind')
    add('unknown-qualifier-key',lambda x:x['relations'][0]['qualifiers'].update(authority=True),'closed-qualifier-payload')
    add('boolean-qualifier-is-not-string',lambda x:x['relations'][0]['qualifiers'].update(role=True),'invalid-label')
    for key in ['owner_ref','lifecycle_ref','contestability_ref','scope_ref']:
        add('missing-'+key,lambda x,key=key:x['relations'][0].pop(key),'malformed-relation-record')
        add('empty-'+key,lambda x,key=key:x['relations'][0].update({key:''}),'invalid-label')
    add('empty-evidence-list',lambda x:x['relations'][0].update(evidence_refs=[]),'missing-or-invalid-evidence-list')
    add('duplicate-instance-reference',lambda x:x['instances'].append(copy.deepcopy(x['instances'][0])),'duplicate-instance-reference')
    add('duplicate-kind-version',lambda x:x['kinds'].append(copy.deepcopy(x['kinds'][0])),'duplicate-kind-reference')
    add('schema-fields-do-not-supply-missing-kind',lambda x:x['relations'][0].pop('kind'),'malformed-relation-record')
    return rows
def verify(write=False):
    context=json.loads((b.UNIT/'context.json').read_bytes());b.unchanged(context['sources']);b.r.verify(b.snapshot(),b.ROOT)
    runtime=v.f.current_bindings();bindings=[b.ref(x) for x in [b.UNIT/'verify_record_profile.py',b.UNIT/'build_candidate.py',b.IMPL/'resolver.py']]
    results=[]
    for case in cases():
        before=copy.deepcopy(case['input'])
        try:
            out=inspect(case['input']);require(case['expected_error'] is None,'expected-rejection-missing')
            result={'case_id':case['case_id'],'status':'accepted-bounded-record-profile','inspection':out}
        except ProfileFault as error:
            if error.code!=case['expected_error']:raise
            result={'case_id':case['case_id'],'status':'rejected-record-profile','code':error.code}
        if case['input']!=before:raise ValueError('Inspector mutated records')
        results.append({**result,'input':case['input'],'input_sha256':b.ir.digest(case['input'])})
    prior=json.loads((b.BASE/'units/I04/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(b.snapshot(),b.ROOT)
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-typed-relation-record-profile/v1-candidate','status':'PASS-for-exact-bounded-record-profile-controls',
            'authority_effect':'none','source':b.source_ref(b.snapshot(),'cal.definition.typed-relation'),'checker_bindings':bindings,'runtime_bindings':runtime,
            'controls':len(results),'rejected_controls':sum(x['status']=='rejected-record-profile' for x in results),'results':results,
            'source_profile_embedding_reviewed':False,'actual_kind_admission_authenticated':False,'owner_authorized':False,'actual_relations_created':0,
            'subject_runtime_executed':False,'semantic_ready':False,'mechanized_proof':False,'source_fidelity':'pending',
            'claim_ceiling':'Exact closed bounded synthetic catalogs/records, ordered type pairs and qualifier checks only. Kind labels and references do not authenticate actual admission, owner/evidence, lifecycle/contestability, constraint-cycle safety, authority or source embedding.'}
    if write:b.put('record-profile-checks.json',report)
    elif not b.r.same_json(report,json.loads((b.UNIT/'record-profile-checks.json').read_bytes())):raise ValueError('Fresh profile differs')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({k:x[k] for k in ['status','controls','rejected_controls','actual_relations_created','actual_kind_admission_authenticated','source_profile_embedding_reviewed','semantic_ready']},indent=2,sort_keys=True))
if __name__=='__main__':main()
