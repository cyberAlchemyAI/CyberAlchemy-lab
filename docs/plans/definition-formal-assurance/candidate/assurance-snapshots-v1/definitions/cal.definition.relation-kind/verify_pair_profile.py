"""Closed finite pair/qualifier inspection and read-only selected current Kind bytes."""
import copy,json
import build_candidate as b
import verifier as v

REGISTRY='authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json'
ACTUAL='authority/relation-kinds/candidates/0007-governance-transaction-extension/instances/relation-kinds/member-of.json'
class PairFault(ValueError):
    def __init__(self,code):self.code=code
def require(ok,code):
    if not ok:raise PairFault(code)
def exact(x,keys,code):require(type(x) is dict and set(x)==set(keys),code)
def label(x):require(type(x) is str and 0<len(x)<=256 and x not in ['*','any','all'],'invalid-exact-label')
def endpoint(x):
    exact(x,['id','version'],'malformed-exact-endpoint-kind')
    for value in x.values():label(value)
    require(not any(token in x['id'] for token in ['*','?']),'wildcard-family-endpoint-forbidden')
    return x['id'],x['version']
def schema(value):
    require(type(value) is dict,'invalid-qualifier-schema');b.c.bounded_tree(value)
    stack=[value]
    while stack:
        node=stack.pop()
        if isinstance(node,dict):
            require(not any(key in node for key in ['$ref','$dynamicRef','$recursiveRef']),'external-or-dynamic-schema-reference-forbidden')
            stack.extend(node.values())
        elif isinstance(node,list):stack.extend(node)
    require(value.get('type')=='object' and value.get('additionalProperties') is False,'qualifier-schema-must-be-closed-object')
    b.c.Draft202012Validator.check_schema(value)
    return b.c.Draft202012Validator(value)
def inspect(spec):
    exact(spec,['version_ref','question_ref','question_text','pairs'],'closed-profile-fields')
    for key in ['version_ref','question_ref','question_text']:label(spec[key])
    require(type(spec['pairs']) is list and len(spec['pairs'])<=256,'finite-profile-pair-limit')
    result={}
    for row in spec['pairs']:
        exact(row,['source','target','qualifier_schema'],'malformed-pair-rule-record')
        key=endpoint(row['source']),endpoint(row['target']);require(key not in result,'duplicate-ordered-pair');schema(row['qualifier_schema']);result[key]=row['qualifier_schema']
    return result
def use(spec,source,target,qualifiers):
    pairs=inspect(spec);key=endpoint(source),endpoint(target);require(key in pairs,'undeclared-ordered-pair')
    require(type(qualifiers) is dict,'qualifier-payload-not-object')
    require(not list(schema(pairs[key]).iter_errors(qualifiers)),'pair-qualifier-validation-failed')
    return {'result':'accepted-bounded-pair-and-qualifier','pair_count':len(pairs),'actual_authority_or_admission':False}
def fixture():
    def pair(s,t,value):return {'source':{'id':s,'version':'v1'},'target':{'id':t,'version':'v1'},'qualifier_schema':{'type':'object','properties':{'role':{'type':'string','enum':[value]}},'required':['role'],'additionalProperties':False}}
    return {'version_ref':'synthetic-member-of@v1','question_ref':'synthetic-question:membership','question_text':'Which container is this member part of?',
            'pairs':[pair('capability','product','product-capability'),pair('work','project','project-work')]}
def profile_controls():
    rows=[]
    def add(name,mutate=lambda x:None,source='capability',target='product',payload=None,error=None,inspect_only=False):
        spec=fixture();mutate(spec);rows.append({'case_id':name,'spec':spec,'source':{'id':source,'version':'v1'},'target':{'id':target,'version':'v1'},'qualifiers':{'role':'product-capability'} if payload is None else payload,'expected_error':error,'inspect_only':inspect_only})
    add('exact-forward-pair-and-specific-qualifier')
    add('other-pair-uses-its-own-rule',source='work',target='project',payload={'role':'project-work'})
    add('source-target-marginals-do-not-license-cross-pair',target='project',error='undeclared-ordered-pair')
    add('reversing-pair-does-not-license-reverse',source='product',target='capability',error='undeclared-ordered-pair')
    add('qualifier-from-other-pair-not-accepted',payload={'role':'project-work'},error='pair-qualifier-validation-failed')
    add('missing-qualifier',payload={},error='pair-qualifier-validation-failed')
    add('extra-authority-field',payload={'role':'product-capability','authority':True},error='pair-qualifier-validation-failed')
    add('boolean-role-not-string',payload={'role':True},error='pair-qualifier-validation-failed')
    add('wildcard-endpoint-rejected',lambda x:x['pairs'][0]['source'].update(id='*'),error='invalid-exact-label')
    add('wildcard-family-endpoint-rejected',lambda x:x['pairs'][0]['source'].update(id='capability.*'),error='wildcard-family-endpoint-forbidden')
    add('duplicate-pair-rule-rejected',lambda x:x['pairs'].append(copy.deepcopy(x['pairs'][0])),error='duplicate-ordered-pair')
    add('Cartesian-expansion-control-field-rejected',lambda x:x.update(cartesian=True),error='closed-profile-fields')
    add('schema-reference-cannot-fetch-external-content',lambda x:x['pairs'][0]['qualifier_schema'].update({'$ref':'https://example.invalid/schema'}),error='external-or-dynamic-schema-reference-forbidden')
    add('open-qualifiers-rejected',lambda x:x['pairs'][0]['qualifier_schema'].update(additionalProperties=True),error='qualifier-schema-must-be-closed-object')
    add('empty-finite-pair-set-is-not-an-owner-exemption',lambda x:x.update(pairs=[]),inspect_only=True)
    add('successor-version-can-retain-question',lambda x:x.update(version_ref='synthetic-member-of@v2'))
    return rows
def actual_contract(document):
    payload=document['payload'];q=payload['qualifier_contract']
    require(q['closed'] is True,'actual-qualifier-contract-not-closed')
    result={'type':'object','properties':q['properties'],'required':q['required_axes'],'additionalProperties':False}
    schema(result);return result
def verify(write=False):
    context=json.loads((b.UNIT/'context.json').read_bytes());b.unchanged(context['sources']);snap=b.snapshot();b.r.verify(snap,b.ROOT)
    runtime=v.f.current_bindings();bindings=[b.ref(p) for p in [b.UNIT/'verify_pair_profile.py',b.UNIT/'build_candidate.py',b.IMPL/'contracts.py',b.IMPL/'resolver.py']]
    results=[]
    for case in profile_controls():
        original=copy.deepcopy(case['spec'])
        try:
            out={'pair_count':len(inspect(case['spec']))} if case['inspect_only'] else use(case['spec'],case['source'],case['target'],case['qualifiers'])
            require(case['expected_error'] is None,'expected-profile-rejection-missing');row={'case_id':case['case_id'],'status':'accepted-bounded-profile','outcome':out}
        except PairFault as error:
            if error.code!=case['expected_error']:raise
            row={'case_id':case['case_id'],'status':'rejected-bounded-profile','code':error.code}
        if case['spec']!=original:raise ValueError('Profile inspector mutated input')
        results.append({**row,'input':case,'input_sha256':b.ir.digest(case)})
    selected={name:b.ref(b.ROOT/path) for name,path in [('registry',REGISTRY),('actual_member_of',ACTUAL),('carrier_schema','authority/artifact-types/relation-kind/v2/schema.json'),('decision','docs/decisions/0074-governance-transaction-surface-admission/decision.json')]}
    registry=b.r.parse(b.r.read_bytes(b.ROOT,REGISTRY),REGISTRY);actual=b.r.parse(b.r.read_bytes(b.ROOT,ACTUAL),ACTUAL)
    carrier=b.r.parse(b.r.read_bytes(b.ROOT,selected['carrier_schema']['path']),'carrier-schema');b.c.Draft202012Validator.check_schema(carrier)
    require(registry['count']==len(registry['entries'])==41 and registry['status']=='owner-admitted-postimage','selected-registry-posture-or-count')
    catalog=[];ids=set();axis_ids=set();questions=[];all_inputs=[]
    for entry in registry['entries']:
        require(entry['relation_kind_id'] not in ids,'duplicate-current-kind-id');ids.add(entry['relation_kind_id'])
        ref={'path':entry['instance_path'],'sha256':entry['instance_sha256']};raw=b.r.read_bytes(b.ROOT,ref['path']);require(b.r.digest(raw)==ref['sha256'],'changed-selected-kind-bytes');all_inputs.append(ref)
        doc=b.r.parse(raw,ref['path']);errors=list(b.c.Draft202012Validator(carrier).iter_errors(doc));require(not errors,'selected-kind-carrier-shape-failed')
        payload=doc['payload'];require(payload['relation_kind_id']==entry['relation_kind_id'] and payload['axis_id']==entry['axis_id'],'kind-axis-binding-substitution')
        require(entry['axis_id'] not in axis_ids,'duplicate-current-axis-id');axis_ids.add(entry['axis_id']);label(payload['unique_question']);questions.append(payload['unique_question'])
        pairs=[]
        for pair in payload['allowed_endpoint_pairs']:
            exact(pair,['source_kind','target_kind'],'actual-pair-shape')
            for value in pair.values():label(value)
            require(not any(token in value for value in pair.values() for token in ['*','?']),'actual-wildcard-family-endpoint-forbidden')
            key=pair['source_kind'],pair['target_kind'];require(key not in pairs,'duplicate-actual-ordered-pair');pairs.append(key)
        require(len(pairs)==entry['exact_endpoint_pair_count'],'actual-pair-denominator-substitution')
        require(sorted({x[0] for x in pairs})==sorted(payload['source_kinds']) and sorted({x[1] for x in pairs})==sorted(payload['target_kinds']),'summary-kind-lists-disagree-with-declaration')
        actual_contract(doc)
        catalog.append({'relation_kind_id':entry['relation_kind_id'],'source_ref':ref,'node_id':doc['node_id'],'axis_id':entry['axis_id'],'question_text':payload['unique_question'],'exact_pair_count':len(pairs),
                        'descriptor_lifecycle':doc['lifecycle_state'],'selected_registry_lifecycle':entry['lifecycle_state'],'admission_decision_ref':entry['admission_decision_ref'],'schema_valid':True,
                        'qualifier_rule_association':'same selected closed Kind-level contract applied to each declared pair; source embedding/overrides require review'})
    row=next(x for x in registry['entries'] if x['relation_kind_id']=='relation.member-of');require(row['instance_path']==ACTUAL and row['instance_sha256']==selected['actual_member_of']['sha256'],'actual-member-of-selection-substitution')
    pairs={(x['source_kind'],x['target_kind']) for x in actual['payload']['allowed_endpoint_pairs']};qvalidator=schema(actual_contract(actual))
    actual_results=[]
    for name,s,t,q,expected in [('actual-product-capability-member-of-product','product-capability','product',{'membership_role':'product-capability'},True),
            ('actual-reverse-not-inferred','product','product-capability',{'membership_role':'product-capability'},False),
            ('actual-marginal-Cartesian-cross-pair-not-inferred','responsibility','team',{'membership_role':'member'},False),
            ('actual-missing-qualifier','product-capability','product',{},False),('actual-extra-authority','product-capability','product',{'membership_role':'member','authority':True},False),
            ('actual-boolean-qualifier','product-capability','product',{'membership_role':True},False),('actual-empty-qualifier','product-capability','product',{'membership_role':''},False)]:
        outcome=(s,t) in pairs and not list(qvalidator.iter_errors(q))
        require(outcome is expected,'actual-selected-pair-control-failed');actual_results.append({'case_id':name,'source_kind':s,'target_kind':t,'qualifiers':q,'pair_declared':(s,t) in pairs,'pair_and_qualifier_accepted':outcome})
    # Explicitly compare 24 selected pairs with the summaries' larger product.
    cartesian={(s,t) for s in actual['payload']['source_kinds'] for t in actual['payload']['target_kinds']}
    require(pairs<cartesian and ('responsibility','team') in cartesian-pairs,'Cartesian-control-not-a-real-gap')
    decision=b.r.parse(b.r.read_bytes(b.ROOT,selected['decision']['path']),'decision')
    require(decision['status']=='owner-admitted' and 'CAL-DECISION-0074C-GOVERNANCE-RELATION-SURFACE-ADMISSION' in decision['decision_refs'],'selected-decision-posture')
    prior=json.loads((b.BASE/'definitions/cal.definition.typed-relation/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings+list(selected.values())+all_inputs);b.r.verify(snap,b.ROOT)
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-relation-kind-pair-profile/v1-candidate','status':'PASS-for-bounded-pair-profile-and-selected-actual-kind-bytes','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'selected_inputs':selected,'selected_kind_refs':all_inputs,'profile_controls':len(results),'rejected_profile_controls':sum(x['status']=='rejected-bounded-profile' for x in results),'profile_results':results,
            'selected_registry_kind_count':len(catalog),'selected_registry_axis_count':len(axis_ids),'distinct_question_strings':len(set(questions)),'selected_actual_catalog':catalog,
            'actual_member_of_controls':actual_results,'actual_member_of_pair_count':len(pairs),'actual_member_of_cartesian_pair_count':len(cartesian),
            'actual_member_of_cartesian_extra_pairs':sorted(cartesian-pairs),'source_profile_embedding_reviewed':False,'semantic_question_orthogonality_proved':False,'natural_language_question_equivalence_decided':False,
            'unbounded_finiteness_proved':False,'new_kind_or_relation_instances_created':0,'actual_owner_principal_authenticated':False,'semantic_ready':False,'mechanized_proof':False,'source_fidelity':'pending',
            'claim_ceiling':'Closed bounded synthetic pair/rule controls and selected41 Kind carrier/registry bytes plus seven actual member-of pair/qualifier controls. No source embedding, semantic question orthogonality, unbounded finiteness, actual principal authentication, connection admission or runtime effect.'}
    if write:b.put('pair-profile-checks.json',report)
    elif not b.r.same_json(report,json.loads((b.UNIT/'pair-profile-checks.json').read_bytes())):raise ValueError('Fresh pair/actual-kind report differs')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({k:x[k] for k in ['status','profile_controls','rejected_profile_controls','selected_registry_kind_count','actual_member_of_pair_count','actual_member_of_cartesian_pair_count','source_profile_embedding_reviewed','semantic_ready']},indent=2,sort_keys=True))
if __name__=='__main__':main()
