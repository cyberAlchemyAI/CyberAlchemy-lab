"""Complete the Verified Patch Capability through exact source contract bindings."""
import collections
import json
from pathlib import Path
import sys
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
SOURCE=ROOT.parent/'cyberAlchemy-v2'
PREVIOUS=HERE.parent/'0012-governed-access-contracts'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool
PREFIX='development/agent-reasoning-engine/codex-integration/coding-agent-runtime/'
ACTION_SCHEMA='implementation/agent-reasoning-engine/packages/coding-agent-runtime/schemas/next-action-candidate.schema.json'
def dump(path,value):
    text=json.dumps(value,indent=2,sort_keys=True)+'\n'
    if path.exists() and path.read_text()!=text:raise ValueError('Preserve existing artifact')
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
def bind(path,root=ROOT):return {'root':'lab' if root==ROOT else 'cav2','path':str(path.relative_to(root)),'sha256':tool.sha(path)}
def requirements(cap,ontology,interface,plan):
    if ontology['product_capability_ref']!=cap['capability_id'] or ontology['ontology_id']!=cap['business_ontology_ref']:raise ValueError('Capability ontology mismatch')
    if interface['contract_id'] not in cap['output_contract_refs']:raise ValueError('Output contract mismatch')
    rules={x['id']:x for x in ontology['invariants']}
    if len(rules)!=len(ontology['invariants']) or set(rules)!=set(plan['invariant_ids']):raise ValueError('Missing or duplicate invariant')
    conditions=[rules[i]['expression'] for i in plan['invariant_ids']]
    preconditions=interface['patch_candidate_preconditions']
    if len(preconditions)!=9 or not tool.strings(preconditions):raise ValueError('Interface preconditions incomplete')
    if ontology['authority_effect']!='none' or interface['authority_effect']!='none':raise ValueError('Unexpected authority effect')
    return conditions+preconditions

def prepare():
    for ref in tool.read(PREVIOUS/'verification.json')['bindings']:
        if tool.sha(ROOT/ref['path'])!=ref['sha256']:raise ValueError('Previous artifact drift')
    registry=tool.load_registry();plan=tool.read(HERE/'plan.json');docs={};index=collections.defaultdict(list)
    for ref in plan['sources']:
        p=SOURCE/ref['path']
        if tool.sha(p)!=ref['sha256']:raise ValueError('Source drift: '+ref['path'])
        docs[ref['path']]=tool.read(p)
        for ptr,row in tool.walk(docs[ref['path']]):
            for key in ['id','node_id','contract_id']:
                if tool.text(row.get(key)):index[row[key]].append({'source':{**ref,'root':'cav2','selector':ptr},'record':row})
    cap=docs[PREFIX+'product-capability.json'];ontology=docs[PREFIX+'business-ontology.json'];interface=docs[PREFIX+'interface-contract.json']
    if cap['capability_id']!=plan['capability_id']:raise ValueError('Wrong capability')
    conditions=requirements(cap,ontology,interface,plan)
    model=docs[PREFIX+'domainspec/nodes/coding-request.json']
    if model['body']['semantic_refs']!=['ARE-CAR-CODING-REQUEST']:raise ValueError('Request model semantic mismatch')
    props={}
    for f in model['body']['fields']:
        if f['name'] in props or f['type'] not in ['string','sha256']:raise ValueError('Unsupported or duplicate request field')
        props[f['name']]={'type':'string','minLength':1} if f['type']=='string' else {'type':'string','pattern':'^[a-f0-9]{64}$'}
    props['authority_effect']={'const':'none'}
    req_schema={'$schema':'https://json-schema.org/draft/2020-12/schema','type':'object','additionalProperties':False,'required':sorted(props),'properties':props}
    bindings=[]
    for ident,schema,source_path,meaning in [
        ('CA2-CONTRACT-CODING-REQUEST',req_schema,PREFIX+'domainspec/nodes/coding-request.json',model['intent']),
        ('CA2-CONTRACT-NEXT-ACTION-CANDIDATE',docs[ACTION_SCHEMA],ACTION_SCHEMA,'Untrusted closed replace-file proposal; exact source schema reused, not authority to execute it.')]:
        folder=HERE/'contracts'/ident;dump(folder/'schema.json',schema)
        contract={'contract_id':ident,'status':'candidate-unadmitted','authority_effect':'none','meaning':meaning,'schema':bind(folder/'schema.json'),'source_binding':bind(SOURCE/source_path,SOURCE),'mapping_effect':'explicit local candidate binding; source identity and posture unchanged','limitations':['Schema validity does not prove approval, path authorization or verifier success.']}
        dump(folder/'contract.json',contract);ref=bind(folder/'contract.json');bindings.append(ref)
        index[ident].append({'source':{**ref,'selector':''},'record':contract})
    sys.path.insert(0,str(ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0026-remaining-targets-review-batch'))
    import engine
    source_ref=bind(SOURCE/PREFIX/'product-capability.json',SOURCE)
    normalized=tool.normalize({'record':{**cap,'acceptance_conditions':conditions},'source':{**source_ref,'selector':''}},index,engine,registry['scope'])
    entry=next(x for x in registry['entries'] if x['target_id']=='type.product-capability')
    for ref in plan['sources']:
        if tool.sha(SOURCE/ref['path'])!=ref['sha256']:raise ValueError('Source changed')
    return {**normalized,'id':cap['capability_id'],'source':{**source_ref,'selector':''},'source_record':cap,'status':'imported-candidate','contract':entry['contract'],'semantic_dependencies':entry['semantic_definition_bindings'],'candidate_input_bindings':bindings,'source_bindings':plan['sources'],'acceptance_mapping':{'invariants':ontology['invariants'],'interface_preconditions':interface['patch_candidate_preconditions']},'authority_effect':'none','operational_use_authorized':False,'runtime_tests_rerun':False}
if __name__=='__main__':
    result=prepare();prior=tool.read(PREVIOUS/'imports.json')
    if any(x['id']==result['id'] for x in prior):raise ValueError('Already imported')
    combined=prior+[result];nodes={}
    import engine
    for item in combined:
        for n in [item['product'],item['capability']]:
            if n['node_id'] in nodes and nodes[n['node_id']]!=n:raise ValueError('Identity collision')
            nodes[n['node_id']]=n
    engine.validate_graph({'schema_version':'cal-review-graph/v1','authority_effect':'none','nodes':list(nodes.values()),'relations':[]})
    inventory=tool.read(PREVIOUS/'inventory.json');changed=0
    for row in inventory['results']:
        if row['id']==result['id'] and row['status']=='blocked' and row['source']['path']==result['source']['path']:
            row.update(status='imported-candidate',reason='Fourteen source acceptance requirements and two explicit model/schema input bindings validated.');changed+=1
    if changed!=1:raise ValueError('Expected one transition')
    inventory['counts']=dict(collections.Counter(x['status'] for x in inventory['results']))
    store=ROOT/'.local/capability-inventory-import-0013'
    if store.exists():raise ValueError('Preserve existing store')
    for name,data in [('result.json',result),('imports.json',combined),('inventory.json',inventory)]:dump(HERE/name,data)
    dump(store/'imports.json',combined)
    print(json.dumps({'result':'PASS','acceptance_requirements':14,'input_bindings':2,'counts':inventory['counts']}))
