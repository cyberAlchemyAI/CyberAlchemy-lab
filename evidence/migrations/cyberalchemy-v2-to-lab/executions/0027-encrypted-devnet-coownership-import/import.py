"""Map declared compiler outcomes and policies into candidate acceptance conditions."""
import collections,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];SOURCE=ROOT.parent/'cyberAlchemy-v2';PREV=HERE.parent/'0026-hosted-devnet-exchange-import'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool
sys.path.insert(0,str(ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0026-remaining-targets-review-batch'))
import engine
PREFIX='product/knowledge-exchange-protocol/capabilities/solana-coownership/successors/encrypted-durable-devnet/v1/'
ID='CA2-CAP-REALIZE-ENCRYPTED-DURABLE-DEVNET-COOWNERSHIP'
def bind(p,root=ROOT):return {'path':str(p.relative_to(root)),'sha256':tool.sha(p)}
def dump(p,obj):
    text=json.dumps(obj,indent=2,sort_keys=True)+'\n'
    if p.exists() and p.read_text()!=text:raise ValueError('Preserve existing artifact')
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def requirements(cap,nodes,rules):
    if len(rules)!=26 or len({r['rule_id'] for r in rules})!=26:raise ValueError('Missing or duplicate hosted rule')
    if any(not tool.text(r.get('statement')) or not tool.strings(r.get('definition_refs')) for r in rules):raise ValueError('Invalid hosted rule')
    return [{'id':r['rule_id'],'statement':r['statement']} for r in rules]

def prepare():
    for b in tool.read(PREV/'verification.json')['bindings']:
        if tool.sha(ROOT/b['path'])!=b['sha256']:raise ValueError('Previous artifact drift')
    registry=tool.load_registry();plan=tool.read(HERE/'plan.json');docs={};index=collections.defaultdict(list)
    for b in plan['sources']:
        if tool.sha(SOURCE/b['path'])!=b['sha256']:raise ValueError('Source drift')
        docs[b['path']]=tool.read(SOURCE/b['path']) if b['path'].endswith('.json') else (SOURCE/b['path']).read_text()
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
    definitions={n['id']:n['meaning'] for n in docs[PREFIX+'ontology/nodes.json']['nodes'] if tool.text(n.get('meaning'))}
    rules={r['rule_id']:r['statement'] for r in docs[PREFIX+'ontology/rules.json']['rules']}
    projections=[]
    for ident,selectors in plan['reference_mappings'].items():
        statements=[]
        for selector in selectors:
            if selector not in definitions and selector not in rules:raise ValueError('Missing projection meaning')
            statements.append(definitions.get(selector,rules.get(selector)))
        record={'id':ident,'role':'candidate-semantic-reference','meaning':' '.join(statements),'status':'candidate-unadmitted','authority_effect':'none','source_selectors':selectors,'source_bindings':plan['sources'],'mapping_effect':'Explicit local semantic binding under the capability reference ID; exact source definitions/rules reused, no executable schema or operational authorization asserted.'}
        path=HERE/'references'/(ident+'.json');dump(path,record);projections.append(bind(path))
        index[ident]=[{'source':{**bind(path),'root':'lab','selector':''},'record':record}]
    mapped=cap
    normalized=tool.normalize({'record':mapped,'source':row['source']},index,engine,registry['scope'])
    entry=next(x for x in registry['entries'] if x['target_id']=='type.product-capability')
    for b in plan['sources']:
        if tool.sha(SOURCE/b['path'])!=b['sha256']:raise ValueError('Source changed')
    return {**normalized,'id':ID,'source':row['source'],'source_record':cap,'status':'imported-candidate','source_bindings':plan['sources'],'acceptance_mapping':obligations,'candidate_dependency_bindings':[bind(registry_path)]+projections,'contract':entry['contract'],'semantic_dependencies':entry['semantic_definition_bindings'],'authority_effect':'none','operational_use_authorized':False,'limitations':['Description import only. Semantic mappings are not executable API schemas or proof of deployment, finality observation, security or recovery. No service, wallet or chain operation executed.','Credit release, inventory reservation and production rollback remain reference examples, not capabilities.']}
if __name__=='__main__':
    result=prepare();prior=tool.read(PREV/'imports.json');assert not any(r['id']==ID for r in prior)
    combined=prior+[result];nodes={}
    for item in combined:
        for n in [item['product'],item['capability']]:
            if n['node_id'] in nodes and nodes[n['node_id']]!=n:raise ValueError('Identity collision')
            nodes[n['node_id']]=n
    engine.validate_graph({'schema_version':'cal-review-graph/v1','authority_effect':'none','nodes':list(nodes.values()),'relations':[]})
    inventory=tool.read(PREV/'inventory.json');changed=0
    for row in inventory['results']:
        if row['id']==ID and row['category']=='declaration':
            assert row['status']=='blocked';row.update(status='imported-candidate',reason='26 exact source rules bound to candidate obligation registry; ten semantic references mapped to source concepts and rules.');changed+=1
    assert changed==1
    inventory['counts']=dict(collections.Counter(r['status'] for r in inventory['results']))
    for name,obj in [('result.json',result),('imports.json',combined),('inventory.json',inventory)]:dump(HERE/name,obj)
    dump(ROOT/'.local/capability-inventory-import-0027/imports.json',combined)
    print(json.dumps(inventory['counts']))
