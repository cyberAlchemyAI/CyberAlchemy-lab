"""Map declared compiler outcomes and policies into candidate acceptance conditions."""
import collections,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];SOURCE=ROOT.parent/'cyberAlchemy-v2';PREV=HERE.parent/'0018-alchlang-extension-import'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool
sys.path.insert(0,str(ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0026-remaining-targets-review-batch'))
import engine
PREFIX='language/capabilities/alchlang/plans/general-compiler-v1/'
ID='CA2-CAP-ALCHLANG-COMPILE-GOVERNED-DOMAIN-MODELS'
def bind(p,root=ROOT):return {'path':str(p.relative_to(root)),'sha256':tool.sha(p)}
def dump(p,obj):
    text=json.dumps(obj,indent=2,sort_keys=True)+'\n'
    if p.exists() and p.read_text()!=text:raise ValueError('Preserve existing artifact')
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def requirements(cap,nodes):
    mapped={};conditions=[]
    for field,role in [('policy_refs','policy'),('outcome_refs','outcome')]:
        ids=cap[field]
        if not tool.strings(ids) or len(ids)!=len(set(ids)):raise ValueError('Invalid acceptance references')
        for ident in ids:
            matches=[n for n in nodes if n.get('id')==ident]
            if len(matches)!=1:raise ValueError('Missing or ambiguous acceptance reference')
            node=matches[0]
            if node.get('role')!=role or not tool.text(node.get('meaning')) or node.get('authority_effect')!='none':raise ValueError('Invalid acceptance meaning')
            conditions.append(node['meaning']);mapped[ident]=node['meaning']
    return conditions,mapped

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
    conditions,mapping=requirements(cap,docs[PREFIX+'nodes.json']['nodes'])
    mapped={**cap,'acceptance_conditions':conditions,'participant_refs':cap['participants'],'context_policy_refs':cap['policy_refs']}
    normalized=tool.normalize({'record':mapped,'source':row['source']},index,engine,registry['scope'])
    entry=next(x for x in registry['entries'] if x['target_id']=='type.product-capability')
    for b in plan['sources']:
        if tool.sha(SOURCE/b['path'])!=b['sha256']:raise ValueError('Source changed')
    return {**normalized,'id':ID,'source':row['source'],'source_record':cap,'status':'imported-candidate','source_bindings':plan['sources'],'acceptance_mapping':mapping,'reference_mapping':{'participant_refs':'/participants','context_policy_refs':'/policy_refs'},'contract':entry['contract'],'semantic_dependencies':entry['semantic_definition_bindings'],'authority_effect':'none','operational_use_authorized':False,'limitations':['Candidate requirements and semantic input/output contracts validated; compiler implementation and runtime conformance not executed.','Parent links remain source evidence; parent import is not asserted.']}
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
            assert row['status']=='blocked';row.update(status='imported-candidate',reason='Four declared policies and three outcomes mapped to acceptance conditions; participants and input/output contracts resolved.');changed+=1
    assert changed==1
    inventory['counts']=dict(collections.Counter(r['status'] for r in inventory['results']))
    for name,obj in [('result.json',result),('imports.json',combined),('inventory.json',inventory)]:dump(HERE/name,obj)
    dump(ROOT/'.local/capability-inventory-import-0019/imports.json',combined)
    print(json.dumps(inventory['counts']))
