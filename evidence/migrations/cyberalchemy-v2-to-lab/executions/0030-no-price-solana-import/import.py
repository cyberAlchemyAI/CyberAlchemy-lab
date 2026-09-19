"""Map declared compiler outcomes and policies into candidate acceptance conditions."""
import collections,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];SOURCE=ROOT.parent/'cyberAlchemy-v2';PREV=HERE.parent/'0029-persist-encrypted-material-import'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool
sys.path.insert(0,str(ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0026-remaining-targets-review-batch'))
import engine
PREFIX='product/knowledge-exchange-protocol/capabilities/solana-coownership/'
ID='CA2-CAP-REALIZE-NO-PRICE-SOLANA-COOWNERSHIP'
def bind(p,root=ROOT):return {'path':str(p.relative_to(root)),'sha256':tool.sha(p)}
def dump(p,obj):
    text=json.dumps(obj,indent=2,sort_keys=True)+'\n'
    if p.exists() and p.read_text()!=text:raise ValueError('Preserve existing artifact')
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def requirements(cap,nodes,rules):
    matches=[n for n in nodes if n['id']==cap['obligation_registry_ref']]
    if len(matches)!=1 or matches[0]['role']!='obligation_registry':raise ValueError('Wrong obligation registry')
    if len(rules)!=12 or len({r['rule_id'] for r in rules})!=12:raise ValueError('Missing or duplicate recovery rule')
    if any(not tool.text(r.get('statement')) or not tool.text(r.get('failure_behavior')) for r in rules):raise ValueError('Invalid recovery rule')
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
    cap=docs['product/knowledge-exchange-protocol/realize-no-price-solana-coownership.product-capability.json'];assert cap['capability_id']==ID
    inventory=tool.read(PREV/'inventory.json');row=next(r for r in inventory['results'] if r['id']==ID and r['category']=='declaration')
    if tool.sha(SOURCE/row['source']['path'])!=row['source']['sha256']:raise ValueError('Inventory source drift')
    obligations=requirements(cap,docs[PREFIX+'ontology/nodes.json']['nodes'],docs[PREFIX+'ontology/rules.json']['rules'])
    candidate={'registry_id':cap['obligation_registry_ref'],'kind':'obligation-registry','capability_ref':ID,'obligations':obligations,'status':'candidate-unadmitted','authority_effect':'none','source_bindings':plan['sources'],'mapping_effect':'New local candidate registry under the unresolved source identity, derived from exact linked source meanings; not a recovered source registry or operational admission.'}
    registry_path=HERE/'obligation-registry.json'
    dump(registry_path,candidate)
    index[candidate['registry_id']]=[{'source':{**bind(registry_path),'root':'lab','selector':''},'record':candidate}]
    ident='CA2-ACTOR-SOLANA-PROGRAM-REALIZATION'
    matches=[n for n in docs[PREFIX+'ontology/nodes.json']['nodes'] if n['id']=='CA2-SOLANA-PROGRAM-REALIZATION-IDENTITY']
    if len(matches)!=1 or not tool.text(matches[0].get('meaning')):raise ValueError('Missing program realization meaning')
    projection={'id':ident,'role':'actor','meaning':matches[0]['meaning'],'status':'candidate-unadmitted','authority_effect':'none','source_node':matches[0],'source_bindings':plan['sources'],'mapping_effect':'Explicit local semantic participant binding to source program-realization identity; no deployed program asserted.'}
    consumer_path=HERE/'program-participant.json';dump(consumer_path,projection)
    index[ident]=[{'source':{**bind(consumer_path),'root':'lab','selector':''},'record':projection}]
    # The capability-specific identity description is explicit; root KEP remains the Product source.
    identity='CA2-IDENTITY-KNOWLEDGE-PARTICIPANT'
    selected=[v for v in index[identity] if v['source']['path']==PREFIX+'ontology/nodes.json']
    if len(selected)!=1:raise ValueError('Ambiguous selected participant identity')
    index[identity]=selected
    mapped=cap
    normalized=tool.normalize({'record':mapped,'source':row['source']},index,engine,registry['scope'])
    entry=next(x for x in registry['entries'] if x['target_id']=='type.product-capability')
    for b in plan['sources']:
        if tool.sha(SOURCE/b['path'])!=b['sha256']:raise ValueError('Source changed')
    return {**normalized,'id':ID,'source':row['source'],'source_record':cap,'status':'imported-candidate','source_bindings':plan['sources'],'acceptance_mapping':obligations,'candidate_dependency_bindings':[bind(registry_path),bind(consumer_path)],'contract':entry['contract'],'semantic_dependencies':entry['semantic_definition_bindings'],'authority_effect':'none','operational_use_authorized':False,'limitations':['Description import only; PostgreSQL, Docker, archive and recovery tests were not run. Semantic contract identities resolve but do not prove operational restoration.','Credit release, inventory reservation and production rollback remain reference examples, not capabilities.']}
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
            assert row['status']=='blocked';row.update(status='imported-candidate',reason='Twelve exact source rules bound to registry; program participant mapped to source realization identity; other declared references resolved.');changed+=1
    assert changed==1
    inventory['counts']=dict(collections.Counter(r['status'] for r in inventory['results']))
    for name,obj in [('result.json',result),('imports.json',combined),('inventory.json',inventory)]:dump(HERE/name,obj)
    dump(ROOT/'.local/capability-inventory-import-0030/imports.json',combined)
    print(json.dumps(inventory['counts']))
