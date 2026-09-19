"""Map declared compiler outcomes and policies into candidate acceptance conditions."""
import collections,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];SOURCE=ROOT.parent/'cyberAlchemy-v2';PREV=HERE.parent/'0024-definition-nft-gap-review'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool
sys.path.insert(0,str(ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0026-remaining-targets-review-batch'))
import engine
PREFIX='product/knowledge-exchange-protocol/capabilities/durable-storage/successors/sql-three-layer/v1/'
ID='CA2-CAP-PROTECT-AND-RECOVER-ENCRYPTED-KNOWLEDGE-MATERIAL'
def bind(p,root=ROOT):return {'path':str(p.relative_to(root)),'sha256':tool.sha(p)}
def dump(p,obj):
    text=json.dumps(obj,indent=2,sort_keys=True)+'\n'
    if p.exists() and p.read_text()!=text:raise ValueError('Preserve existing artifact')
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def requirements(cap,nodes,rules):
    matches=[n for n in nodes if n['id']==cap['obligation_registry_ref']]
    if len(matches)!=1 or matches[0]['role']!='obligation-registry':raise ValueError('Wrong obligation registry')
    if len(rules)!=12 or len({r['rule_id'] for r in rules})!=12:raise ValueError('Missing or duplicate recovery rule')
    if any(not tool.text(r.get('statement')) or r.get('enforcement_state')!='candidate' for r in rules):raise ValueError('Invalid recovery rule')
    return [{'id':r['rule_id'],'statement':r['statement']} for r in rules]

def prepare():
    for b in tool.read(PREV/'verification.json')['bindings']:
        if tool.sha(ROOT/b['path'])!=b['sha256']:raise ValueError('Previous artifact drift')
    registry=tool.load_registry();plan=tool.read(HERE/'plan.json');docs={};index=collections.defaultdict(list)
    for b in plan['sources']:
        if tool.sha(SOURCE/b['path'])!=b['sha256']:raise ValueError('Source drift')
        docs[b['path']]=tool.read(SOURCE/b['path'])
        for ptr,row in tool.walk(docs[b['path']]):
            for key in ['id','node_id','capability_id','product_id']:
                if tool.text(row.get(key)):index[row[key]].append({'source':{**b,'selector':ptr},'record':row})
    cap=docs[PREFIX+'product-capability.json'];assert cap['capability_id']==ID
    inventory=tool.read(PREV/'inventory.json');row=next(r for r in inventory['results'] if r['id']==ID and r['category']=='declaration')
    if tool.sha(SOURCE/row['source']['path'])!=row['source']['sha256']:raise ValueError('Inventory source drift')
    obligations=requirements(cap,docs[PREFIX+'ontology/nodes.json']['nodes'],docs[PREFIX+'ontology/rules.json']['rules'])
    candidate={'registry_id':cap['obligation_registry_ref'],'kind':'obligation-registry','capability_ref':ID,'obligations':obligations,'status':'candidate-unadmitted','authority_effect':'none','source_bindings':plan['sources'],'mapping_effect':'New local candidate registry under the unresolved source identity, derived from exact linked source meanings; not a recovered source registry or operational admission.'}
    registry_path=HERE/'obligation-registry.json'
    dump(registry_path,candidate)
    index[candidate['registry_id']]=[{'source':{**bind(registry_path),'root':'lab','selector':''},'record':candidate}]
    consumer_id=cap['consumer_refs'][0]
    if cap['consumer_refs']!=['CA2-CAPABILITY-CONSUMER-KEP-ENCRYPTED-MATERIAL']:raise ValueError('Unexpected consumer')
    route=next(r['owner'] for r in cap['owner_routes'] if r['responsibility']=='next-use-suitability')
    consumer={'id':consumer_id,'role':'capability-consumer','meaning':'Consuming Product Capability for the encrypted knowledge-material protection and recovery outcome.','owner_route':route,'status':'candidate-unadmitted','authority_effect':'none','source_binding':row['source'],'mapping_effect':'Explicit local candidate role projection from consumer_refs, outcome and next-use-suitability owner; no concrete consumer implementation asserted.'}
    consumer_path=HERE/'consumer.json';dump(consumer_path,consumer)
    index[consumer_id]=[{'source':{**bind(consumer_path),'root':'lab','selector':''},'record':consumer}]
    mapped=cap
    normalized=tool.normalize({'record':mapped,'source':row['source']},index,engine,registry['scope'])
    entry=next(x for x in registry['entries'] if x['target_id']=='type.product-capability')
    for b in plan['sources']:
        if tool.sha(SOURCE/b['path'])!=b['sha256']:raise ValueError('Source changed')
    return {**normalized,'id':ID,'source':row['source'],'source_record':cap,'status':'imported-candidate','source_bindings':plan['sources'],'acceptance_mapping':obligations,'candidate_dependency_bindings':[bind(registry_path),bind(consumer_path)],'contract':entry['contract'],'semantic_dependencies':entry['semantic_definition_bindings'],'authority_effect':'none','operational_use_authorized':False,'limitations':['Description import only; PostgreSQL, Docker, archive and recovery tests were not run. Semantic contract identities resolve but do not prove operational restoration.','Credit release, inventory reservation and production rollback remain reference examples, not capabilities.']}
if __name__=='__main__':
    result=prepare();prior=tool.read(HERE.parent/'0023-governed-domain-model-import/imports.json');assert not any(r['id']==ID for r in prior)
    combined=prior+[result];nodes={}
    for item in combined:
        for n in [item['product'],item['capability']]:
            if n['node_id'] in nodes and nodes[n['node_id']]!=n:raise ValueError('Identity collision')
            nodes[n['node_id']]=n
    engine.validate_graph({'schema_version':'cal-review-graph/v1','authority_effect':'none','nodes':list(nodes.values()),'relations':[]})
    inventory=tool.read(PREV/'inventory.json');changed=0
    for row in inventory['results']:
        if row['id']==ID and row['category']=='declaration':
            assert row['status']=='blocked';row.update(status='imported-candidate',reason='Twelve source recovery rules bound to declared obligation registry; explicit candidate consumer role added; Product and declared references resolved.');changed+=1
    assert changed==1
    inventory['counts']=dict(collections.Counter(r['status'] for r in inventory['results']))
    for name,obj in [('result.json',result),('imports.json',combined),('inventory.json',inventory)]:dump(HERE/name,obj)
    dump(ROOT/'.local/capability-inventory-import-0025/imports.json',combined)
    print(json.dumps(inventory['counts']))
