"""Project explicit package semantic ownership onto its bound extension candidates."""
import collections,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];SOURCE=ROOT.parent/'cyberAlchemy-v2';PREV=HERE.parent/'0017-residual-path-closure-import'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool
sys.path.insert(0,str(ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0026-remaining-targets-review-batch'))
import engine
PREFIX='language/capabilities/alchlang/plans/general-compiler-v1/'
EXTENSIONS=['generatable-operation-patterns-v1','local-runtime-cli-v1']
def bind(p,root=ROOT):return {'path':str(p.relative_to(root)),'sha256':tool.sha(p)}
def dump(p,obj):
    text=json.dumps(obj,indent=2,sort_keys=True)+'\n'
    if p.exists() and p.read_text()!=text:raise ValueError('Preserve existing artifact: '+str(p))
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def prepare():
    for b in tool.read(PREV/'verification.json')['bindings']:
        if tool.sha(ROOT/b['path'])!=b['sha256']:raise ValueError('Previous artifact drift')
    registry=tool.load_registry();inventory=tool.read(PREV/'inventory.json');plan=tool.read(HERE/'plan.json');docs={};index=collections.defaultdict(list)
    for b in plan['sources']:
        if tool.sha(SOURCE/b['path'])!=b['sha256']:raise ValueError('Source drift')
        doc=tool.read(SOURCE/b['path']);docs[b['path']]=doc
        for ptr,row in tool.walk(doc):
            for key in ['id','node_id','capability_id','product_id']:
                if tool.text(row.get(key)):index[row[key]].append({'source':{**b,'selector':ptr},'record':row})
    profile=docs[PREFIX+'profile.json'];parent=docs[PREFIX+'product-capability.json'];owners=profile['semantic_owner_routes']
    if not tool.strings(owners) or owners!=parent['owner_routes']:raise ValueError('Package and parent semantic owners disagree')
    chain=docs[PREFIX+'evidence/construction-binding.candidate.json']['d65_chain']
    bindings=[chain['operation_pattern_extension']['product_capability'],chain['extension_product_capability']]
    results=[]
    for ext,b in zip(EXTENSIONS,bindings,strict=True):
        path=PREFIX+'extensions/'+ext+'/product-capability.json';cap=docs[path]
        if PREFIX+b['ref']!=path or tool.sha(SOURCE/path)!=b['sha256'] or cap['capability_id']!=b['capability_id']:raise ValueError('Extension construction binding mismatch')
        prior=next(r for r in inventory['results'] if r['category']=='declaration' and r['id']==cap['capability_id'])
        if prior['source']['sha256']!=b['sha256']:raise ValueError('Inventory source mismatch')
        if not tool.strings(cap['policies']):raise ValueError('Missing explicit acceptance rules')
        mapped={**cap,'owner_routes':owners,'acceptance_conditions':cap['policies']}
        normalized=tool.normalize({'record':mapped,'source':prior['source']},index,engine,registry['scope'])
        entry=next(x for x in registry['entries'] if x['target_id']=='type.product-capability')
        results.append({**normalized,'id':cap['capability_id'],'source':prior['source'],'source_record':cap,'status':'imported-candidate','source_bindings':plan['sources'],'contract':entry['contract'],'semantic_dependencies':entry['semantic_definition_bindings'],'mapping':{'owner_ref':'Explicit local candidate projection of profile.json /semantic_owner_routes, corroborated by parent /owner_routes; extension membership checked against construction binding.','acceptance_conditions':'/policies verbatim','product_ref':'Explicit extends/parent capability chain to AlchLang Product reference'},'authority_effect':'none','operational_use_authorized':False,'limitations':['Package semantic owners are declared roles, not authenticated people or instantiated teams.','Import preserves capability description only; generator/runtime implementations and conformance evidence were not executed.','Parent capability links are source evidence, not a claim that every parent has already been imported.']})
    for b in plan['sources']:
        if tool.sha(SOURCE/b['path'])!=b['sha256']:raise ValueError('Source changed during preparation')
    return results
if __name__=='__main__':
    results=prepare();prior=tool.read(PREV/'imports.json');ids={r['id'] for r in results}
    if ids & {r['id'] for r in prior}:raise ValueError('Already imported')
    combined=prior+results;nodes={}
    for item in combined:
        for n in [item['product'],item['capability']]:
            if n['node_id'] in nodes and nodes[n['node_id']]!=n:raise ValueError('Identity collision')
            nodes[n['node_id']]=n
    engine.validate_graph({'schema_version':'cal-review-graph/v1','authority_effect':'none','nodes':list(nodes.values()),'relations':[]})
    inventory=tool.read(PREV/'inventory.json');changed=0
    for row in inventory['results']:
        if row['category']=='declaration' and row['id'] in ids:
            if row['status']!='blocked':raise ValueError('Wrong predecessor status')
            row.update(status='imported-candidate',reason='Explicit package semantic owners and capability policies projected; construction membership and Product parent chain validated.');changed+=1
    assert changed==2
    inventory['counts']=dict(collections.Counter(r['status'] for r in inventory['results']))
    for name,obj in [('results.json',results),('imports.json',combined),('inventory.json',inventory)]:dump(HERE/name,obj)
    dump(ROOT/'.local/capability-inventory-import-0018/imports.json',combined)
    print(json.dumps(inventory['counts']))
