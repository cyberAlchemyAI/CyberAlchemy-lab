import json,sys,tarfile,shutil,importlib.util
from pathlib import Path
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];PREV=HERE.parent/'0060-d65-construction-context-preparation';CAPS=HERE.parent/'0035-definition-card-import';STORE=ROOT/'.local/ontology-context-import-0061';PACKAGE=STORE/'package'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':tool.sha(p)}
def dump(p,d):
    text=json.dumps(d,indent=2,sort_keys=True)+'\n'
    if p.exists() and p.read_text()!=text:raise ValueError('Existing artifact differs: '+str(p))
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def build():
    for folder in [PREV,CAPS]:
        for entry in tool.read(folder/'verification.json')['bindings']:
            if tool.sha(ROOT/entry['path'])!=entry['sha256']:raise ValueError('Predecessor drift')
    PACKAGE.mkdir(parents=True,exist_ok=True)
    with tarfile.open(PREV/'package-snapshot.tar.gz') as archive:archive.extractall(PACKAGE,filter='data')
    for entry in tool.read(PREV/'package-inputs.json'):
        if tool.sha(PACKAGE/entry['path'])!=entry['sha256']:raise ValueError('Snapshot drift')
    r=tool.read;binding=r(HERE/'successor-binding.json');profile=r(HERE/'profile.json');model=r(HERE/'model.json');contracts=r(HERE/'contracts.json')
    if tool.sha(HERE/'adapter.py')!=binding['adapter_sha256']:raise ValueError('Adapter drift')
    if any(d['authority_effect']!='none' for d in [binding,profile,model,contracts]):raise ValueError('Authority escalation')
    if binding['effect_authorized'] is not False or profile['activation_state']!='not-activated':raise ValueError('Activation escalation')
    for name in ['adapter.py','successor-binding.json','profile.json','model.json','contracts.json']:
        target=STORE/name
        if target.exists() and target.read_bytes()!=(HERE/name).read_bytes():raise ValueError('Companion drift')
        shutil.copyfile(HERE/name,target)
    spec=importlib.util.spec_from_file_location('restored_adapter',STORE/'adapter.py');adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
    evidence=adapter.evaluate(PACKAGE,binding['subject_ref'])
    if evidence['status']!='PASS' or evidence['full_construction_conformance']!='not_evaluable' or evidence['authority_granted'] is not False:raise ValueError('Candidate evaluation changed')
    dump(HERE/'candidate-evaluation.json',evidence)
    cap=next(c for c in r(CAPS/'imports.json') if c['id']==binding['capability_ref'])
    if cap['source_record']!=r(PACKAGE/'cyberAlchemy-v2/ontology/governance/first-invariant/product-capability.json'):raise ValueError('Capability changed')
    registry=tool.load_registry();common={'authority_effect':'none','status':'candidate-unadmitted','scope_ref':registry['scope'],'owner_ref':cap['capability']['owner_ref']}
    ontology={**common,'kind':'ontology','node_id':'lab:ontology-contexts/d65-revision2#ontology','name':'D65 Revision 2 Prototype Validation','version':'source-qualified-0061','concept_refs':[n['source_ref'] for n in model['business_concepts']+model['system_contract_concepts']],'relation_ids':[n['evidence_ref'] for n in model['relation_hints']],'boundaries':['Source scaffold hints retain their non-authoritative posture; three external endpoint names are explicitly unresolved.','System concepts come from revision-2 JSON Schema objects; no DomainSpec compilation claimed.','Partial capability realization only: prototype consistency and eligibility, not full construction conformance.']}
    context={**common,'kind':'context','node_id':'lab:ontology-contexts/d65-revision2#context','purpose':profile['purpose'],'identity_boundary':profile['identity_boundary'],'profile_ref':'profile.json','relevance':[cap['capability']['node_id'],ontology['node_id']]}
    headers=[]
    for ident,obj in [('type.context',context),('type.ontology',ontology)]:
        e=next(e for e in registry['entries'] if e['target_id']==ident);schema=(ROOT/e['binding']['path']).parent/'schema.json';Draft202012Validator(r(schema)).validate(obj);headers.append({'target_id':ident,'binding':e['binding'],'schema':bind(schema)})
    bundle={'context':context,'ontology':ontology,'counts':{'scaffold_concepts':len(model['business_concepts']),'relation_hints':len(model['relation_hints']),'schema_object_concepts':len(model['system_contract_concepts']),'external_hint_endpoints':len(model['external_hint_endpoints'])},'contracts':headers,'source_archive':bind(PREV/'package-snapshot.tar.gz'),'source_manifest':bind(PREV/'package-inputs.json'),'capability_binding':bind(CAPS/'imports.json'),'successor_binding':bind(HERE/'successor-binding.json'),'candidate_contracts':bind(HERE/'contracts.json'),'candidate_evaluation':bind(HERE/'candidate-evaluation.json'),'model':bind(HERE/'model.json'),'authority_effect':'none','limitations':['Limited candidate implementation; full construction conformance remains not evaluable.','Eligibility is not approval or authority; human decision authenticity is not established.','Three scaffold hint endpoints remain external names without invented ontology entities.','Legacy contracts and generated models remain historical; no claim that they now implement revision 2.']}
    for name,data in [('context.json',context),('ontology.json',ontology),('bundle.json',bundle)]:dump(HERE/name,data)
    dump(STORE/'bundle.json',bundle);return bundle
if __name__=='__main__':print(json.dumps(build()['counts']))
