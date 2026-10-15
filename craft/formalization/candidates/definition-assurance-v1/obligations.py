"""Generate the required set before inspecting submissions; compare it exactly."""
import importlib.util
import json
from pathlib import Path
import contracts as c
import resolver as r

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location('assurance_relation_policy',HERE/'relation-policy.py')
p=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(p)
RULES=HERE/'profiles/obligation-rules.json'
POLICY_RECEIPT=HERE.parents[3]/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/units/A05/receipt.json'


class ObligationFault(ValueError):
    def __init__(self,code,path=''):self.code=code;self.path=path


def reviewed_policy():
    raw=POLICY_RECEIPT.read_bytes();receipt=r.parse(raw,str(POLICY_RECEIPT))
    if receipt.get('review_disposition',{}).get('kind')!='candidate-agent-self-review' or receipt.get('authority_effect')!='none':raise ObligationFault('missing-candidate-policy-review')
    bound={item['path']:item['sha256'] for item in receipt['outputs']};root=HERE.parents[3]
    for file in [HERE/'relation-policy.py',p.PROFILE]:
        if bound.get(file.relative_to(root).as_posix())!=r.digest(file.read_bytes()):raise ObligationFault('stale-candidate-policy-review',str(file))
    return r.digest(raw)


def generate(theory,relation_requests,populations,bindings,alignment_root):
    p.exact(theory,['theory_id','sources','declarations','statements','assumption_set_id','scope','change_class','prior_theory_ref'],'malformed-theory-subject')
    c.bounded_tree(theory);p.ident(theory['theory_id']);p.ident(theory['assumption_set_id'])
    if not theory['sources'] or not theory['declarations'] or not isinstance(theory['statements'],list) or not isinstance(theory['scope'],str) or not theory['scope']:raise ObligationFault('empty-or-malformed-theory-subject')
    sources=sorted(theory['sources'],key=lambda row:row['version_ref'])
    source_payload={'snapshot_id':'selected-theory-sources','registry_path':'authority/definitions/registry.json','registry_sha256':'0'*64,'sources':sources,'historical_sources':[],'capture_status':'incomplete','current_lookup_sha256':'0'*64}
    p.structural('source',source_payload)
    change=theory['change_class']
    if change not in {'initial','additive','meaning-change','constraint-change'}:raise ObligationFault('unsupported-change-class')
    prior=theory['prior_theory_ref']
    if (change=='initial' and prior is not None) or (change!='initial' and (not isinstance(prior,dict) or set(prior)!={'path','sha256'})):raise ObligationFault('missing-or-inapplicable-prior-binding')
    rules_raw=RULES.read_bytes();rules=r.parse(rules_raw,str(RULES));policy_review_sha=reviewed_policy()
    policy_sha=p.sha({'rules':r.digest(rules_raw),'relation_policy':r.digest(p.PROFILE.read_bytes()),'policy_review':policy_review_sha,'generator':r.digest(Path(__file__).read_bytes())})
    theory_sha=p.sha(theory);signature_sha=p.sha(theory['declarations'])
    relation_targets=[]
    for request in relation_requests:
        p.exact(request,['relation','bindings','proper','distinction','forbidden'],'malformed-relation-request')
        relation=request['relation']
        if relation['scope']!=theory['scope'] or any(ref not in sources for ref in [relation['left_definition'],relation['right_definition']]):raise ObligationFault('relation-theory-binding-mismatch')
        if not isinstance(request['bindings'],dict) or set(request['bindings'])!={'left','right'}:raise ObligationFault('relation-endpoint-not-in-population-scope')
        for side in ['left','right']:
            if request['bindings'][side] not in bindings.values():raise ObligationFault('relation-endpoint-not-in-population-scope')
        relation_targets.extend(p.compile_relation(relation,request['bindings'],alignment_root,proper=request['proper'],distinction=request['distinction'],forbidden=request['forbidden']))
    for binding in bindings.values():
        p.endpoint(binding,binding['source'],theory['scope'])
        if binding['source'] not in sources:raise ObligationFault('population-source-not-in-theory')
    unary={(row['argument_sorts'][0],row['symbol_id']) for row in theory['declarations'] if row.get('kind')=='predicate' and len(row.get('argument_sorts',[]))==1}
    supplied={(binding['carrier'],binding['predicate']) for binding in bindings.values()}
    if unary!=supplied:raise ObligationFault('signature-population-denominator-mismatch')
    population_targets=p.compile_populations(populations,bindings,theory['scope'])
    population_ids=[row['key'] for row in population_targets];required_populations=[row for row in population_targets if row['status']!='exemption-review-required']
    gates=[]
    def gate(key,check,subject,strength,requires=()):gates.append({'gate_id':key,'check':check,'subject':subject,'minimum_strength':strength,'prerequisites':list(requires),'status':'required'})
    common={'theory_sha256':theory_sha,'signature_sha256':signature_sha,'policy_sha256':policy_sha}
    for declaration in theory['declarations']:
        if declaration.get('kind') in {'predicate','relation'} and len(declaration.get('argument_sorts',[]))!=1:
            gate('gate:population-signature:'+p.sha(declaration),'nonunary-population-profile-review',declaration,'source-review')
    for check,strength in sorted(rules['base_gates'].items()):gate('gate:'+check,check,common,strength)
    for source in sources:
        for check,strength in rules['per_source_gates'].items():gate('gate:'+check+':'+p.sha(source),check,source,strength,['gate:source-currentness'])
    for row in population_targets:
        if row['status']=='exemption-review-required':gate('gate:exemption:'+row['key'],'population-exemption-review',{'population_id':row['key'],'review_ref':row['review_ref'],'subject_sha256':row['review_subject_sha256']},'source-review')
        elif row['status']=='unresolved-policy':gate('gate:population:'+row['key'],'population-policy-review',{'population_id':row['key'],'statement':row['statement']},'source-review')
    for check,strength in rules['change_gates'].get(change,{}).items():gate('gate:'+check,check,{'prior_theory_ref':prior,'new_theory_sha256':theory_sha},strength)
    logical=[];query_requirements=[]
    def logical_row(key,statement,strength,query_type,population_refs):
        logical.append({'obligation_id':key,'statement':statement,'assumption_set_ref':theory['assumption_set_id'],'source_refs':sources,'dependency_refs':[row['definition_id'] for row in sources],'population_refs':population_refs,'direction':'none','minimum_strength':strength,'status':'required'})
        query_requirements.append({'obligation_id':key,'query_type':query_type,'statement_sha256':p.sha(statement),'prerequisites':[g['gate_id'] for g in gates]+(['query:consistency','query:joint-population'] if key not in {'query:consistency','query:joint-population'} else ['query:consistency'] if key=='query:joint-population' else []),'scope':theory['scope']})
    logical_row('query:consistency',{'op':'and','args':[]},'model-witness','model-witness',[])
    logical_row('query:joint-population',{'op':'and','args':[row['statement'] for row in required_populations]},'model-witness','model-witness',population_ids)
    for row in required_populations:logical_row('population:'+row['key'],row['statement'],'model-witness','model-witness',population_ids)
    for row in relation_targets:logical_row('relation:'+row['key'],row['statement'],row['minimum_strength'],row['query_type'],population_ids)
    for rows,key in [(logical,'obligation_id'),(gates,'gate_id')]:
        if len({row[key] for row in rows})!=len(rows):raise ObligationFault('duplicate-required-identity')
    logical.sort(key=lambda row:row['obligation_id']);query_requirements.sort(key=lambda row:row['obligation_id']);gates.sort(key=lambda row:row['gate_id'])
    logical_manifest={'manifest_id':'logical:'+p.sha(logical),'theory_sha256':theory_sha,'policy_sha256':policy_sha,'obligations':logical,'population_refs':population_ids}
    p.structural('obligation-manifest',logical_manifest)
    return {'schema_version':'definition-assurance-required-set/v1-candidate','authority_effect':'none','logical_manifest':logical_manifest,'administrative_and_semantic_gates':gates,'query_requirements':query_requirements,'signature_sha256':signature_sha,'change_class':change,'candidate_policy_review_sha256':policy_review_sha,'required_set_sha256':p.sha({'logical':logical_manifest,'gates':gates,'queries':query_requirements,'signature':signature_sha,'change':change}),'prerequisite_use':'Assurance-readiness requirements; candidate logical checks may execute while meaning/fidelity remains pending.','claim_ceiling':'Required-set identity only. Logical evidence, administrative checks and semantic-review evidence require separate verification.'}


def compare_required(expected,submitted):
    c.bounded_tree(submitted)
    if not r.same_json(expected,submitted):raise ObligationFault('required-set-omitted-substituted-weakened-or-stale')
    return {'status':'required-set-identical','authority_effect':'none','semantic_ready':False,'evidence_verified':False,'required_logical_obligations':len(expected['logical_manifest']['obligations']),'required_gates':len(expected['administrative_and_semantic_gates']),'claim_ceiling':'Exact submitted required-set metadata only; no submitted result, proof, fidelity or readiness accepted.'}


def verify_submission(theory,relation_requests,populations,bindings,alignment_root,submitted):
    # Regenerate from independently selected inputs, never from result lists.
    return compare_required(generate(theory,relation_requests,populations,bindings,alignment_root),submitted)
