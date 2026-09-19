"""Apply the user's standalone Product direction to the prepared dataset capability."""
import collections,copy,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];SOURCE=ROOT.parent/'cyberAlchemy-v2';PREV=HERE.parent/'0031-trusted-dataset-gap-review'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool
sys.path.insert(0,str(ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0026-remaining-targets-review-batch'))
import engine
ID='CA2-CAP-MATERIALIZE-TRUSTED-DATASET'
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':tool.sha(p)}
def dump(p,obj):
    text=json.dumps(obj,indent=2,sort_keys=True)+'\n'
    if p.exists() and p.read_text()!=text:raise ValueError('Preserve existing artifact')
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def prepare():
    receipt=tool.read(PREV/'verification.json')
    for b in receipt['bindings']+[receipt['store']]:
        if tool.sha(ROOT/b['path'])!=b['sha256']:raise ValueError('Predecessor drift')
    registry=tool.load_registry();prepared=tool.read(PREV/'result.json')
    for b in prepared['source_bindings']:
        if tool.sha(SOURCE/b['path'])!=b['sha256']:raise ValueError('Source drift')
    selection={'instruction':'its own product,','subject':ID,'decision':'Trusted Dataset Materialization is a standalone Product.','product_id':'CAL-PRODUCT-TRUSTED-DATASET-MATERIALIZATION','authority_effect':'candidate Product identity and capability assignment only','owner_route_posture':'Product owner is a declared candidate role, not an appointed person or team. Capability owner remains the existing source declaration.'}
    dump(HERE/'product-selection.json',selection)
    cap=copy.deepcopy(prepared['prepared_fields']);pid='lab:trusted-dataset-materialization#'+selection['product_id']
    product={'node_id':pid,'kind':'product','name':'Trusted Dataset Materialization','purpose':cap['outcome'],'identity_boundary':'A standalone Product for bounded dataset materialization, validation, lineage and recoverable execution. Current candidate exclusions: '+ '; '.join(cap['exclusions'])+'.','owner_ref':'Trusted Dataset Materialization product owner','owner_route':'Trusted Dataset Materialization product owner','scope_ref':registry['scope'],'status':'candidate-unadmitted','authority_effect':'none'}
    cap['product_ref']=pid
    engine.validate_graph({'schema_version':'cal-review-graph/v1','authority_effect':'none','nodes':[product,cap],'relations':[]})
    entry=next(e for e in registry['entries'] if e['target_id']=='type.product-capability')
    return {'id':ID,'status':'imported-candidate','product':product,'capability':cap,'source_record':prepared['source_record'],'source':{**prepared['source_bindings'][0],'selector':''},'source_bindings':prepared['source_bindings'],'product_selection':bind(HERE/'product-selection.json'),'contract':entry['contract'],'semantic_dependencies':entry['semantic_definition_bindings'],'authority_effect':'none','operational_use_authorized':False,'notes':['Standalone Product identity explicitly selected by user; created locally rather than asserted as a recovered source identity.','Product owner route is a candidate responsibility role; no person or team appointment asserted.','Six source requirements preserved. No dataset publication, runtime execution or deployment performed.']}
if __name__=='__main__':
    result=prepare();prior=tool.read(HERE.parent/'0030-no-price-solana-import/imports.json');assert not any(r['id']==ID for r in prior);combined=prior+[result];nodes={}
    for item in combined:
        for n in [item['product'],item['capability']]:
            if n['node_id'] in nodes and nodes[n['node_id']]!=n:raise ValueError('Identity collision')
            nodes[n['node_id']]=n
    engine.validate_graph({'schema_version':'cal-review-graph/v1','authority_effect':'none','nodes':list(nodes.values()),'relations':[]})
    inventory=tool.read(PREV/'inventory.json');changed=0
    for row in inventory['results']:
        if row['id']==ID and row['category']=='declaration':
            assert row['status']=='blocked';row.update(status='imported-candidate',resolution_state='resolved-user-selected-standalone-product',reason='User selected a standalone Trusted Dataset Materialization Product; six prepared requirements and Product assignment validated.',product_selection=bind(HERE/'product-selection.json'));changed+=1
    assert changed==1
    inventory['counts']=dict(collections.Counter(r['status'] for r in inventory['results']))
    for name,obj in [('result.json',result),('imports.json',combined),('inventory.json',inventory)]:dump(HERE/name,obj)
    dump(ROOT/'.local/capability-inventory-import-0032/imports.json',combined)
    print(json.dumps(inventory['counts']))
