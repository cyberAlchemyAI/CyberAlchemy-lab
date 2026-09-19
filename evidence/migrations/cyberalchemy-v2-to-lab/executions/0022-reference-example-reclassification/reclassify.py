"""Apply the user's distinction between product capabilities and reference examples."""
import collections,copy,hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];PREV=HERE.parent/'0021-customer-credit-release-import'
IDS={'CA2-REF-CAP-CUSTOMER-CREDIT-RELEASE','CA2-REF-CAP-INVENTORY-RESERVATION','CA2-REF-CAP-PRODUCTION-ROLLBACK'}
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
def dump(p,obj):
    text=json.dumps(obj,indent=2,sort_keys=True)+'\n'
    if p.exists() and p.read_text()!=text:raise ValueError('Existing artifact differs')
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def run():
    receipt=read(PREV/'verification.json')
    for b in receipt['bindings']:
        if sha(ROOT/b['path'])!=b['sha256']:raise ValueError('Historical artifact drift')
    old=read(PREV/'inventory.json');inventory=copy.deepcopy(old);examples=[]
    for row in inventory['results']:
        if row['category']=='declaration' and row['id'] in IDS:
            examples.append({'id':row['id'],'source':row['source'],'previous_status':row['status'],'classification':'reference-example','supports':'CA2-CAP-ALCHLANG-MODEL-GOVERNED-DOMAINS','basis':'User correction: these are examples, not separate product capabilities.','authority_effect':'none'})
            row.update(category='reference-example',status='retained-reference-example',resolution_state='reclassified-by-user',reason='AlchLang reference example; not a separate product capability. Historical source label preserved in provenance.')
    assert {e['id'] for e in examples}==IDS and len(examples)==3
    prior=read(PREV/'imports.json');removed=[i for i in prior if i['id'] in IDS];imports=[i for i in prior if i['id'] not in IDS]
    assert len(removed)==1 and removed[0]['id']=='CA2-REF-CAP-CUSTOMER-CREDIT-RELEASE'
    inventory['counts']=dict(collections.Counter(r['status'] for r in inventory['results']))
    assert inventory['counts']['imported-candidate']==32 and inventory['counts']['blocked']==9 and inventory['counts']['retained-reference-example']==3 and inventory['counts']['excluded-from-migration']==1
    assert imports==read(HERE.parent/'0020-typed-backend-import/imports.json')
    sys.path.insert(0,str(ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0026-remaining-targets-review-batch'))
    import engine
    nodes={}
    for item in imports:
        for n in [item['product'],item['capability']]:
            if n['node_id'] in nodes and nodes[n['node_id']]!=n:raise ValueError('Identity collision')
            nodes[n['node_id']]=n
    engine.validate_graph({'schema_version':'cal-review-graph/v1','authority_effect':'none','nodes':list(nodes.values()),'relations':[]})
    assert sum(a!=b for a,b in zip(old['results'],inventory['results'],strict=True))==3
    for name,obj in [('inventory.json',inventory),('imports.json',imports),('reference-examples.json',examples)]:dump(HERE/name,obj)
    store=ROOT/'.local/capability-inventory-import-0022/imports.json';dump(store,imports)
    assert read(store)==imports
    for b in receipt['bindings']:assert sha(ROOT/b['path'])==b['sha256']
    dump(HERE/'verification.json',{'result':'PASS','checks':['exactly three user-selected examples reclassified','only credit reference removed from active imports','remaining imports exactly match run 0020','counts recomputed; prior exclusion preserved','combined capability graph validates','new store matches report; historical artifacts unchanged'],'previous_receipt':bind(PREV/'verification.json'),'bindings':[bind(p) for p in sorted(HERE.glob('*')) if p.is_file() and p.name!='verification.json'],'store':bind(store),'authority_effect':'none'})
    print(json.dumps(inventory['counts']))
if __name__=='__main__':run()
