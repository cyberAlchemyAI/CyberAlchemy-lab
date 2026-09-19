"""Import one blocked Capability using its source-owned Business Rules."""
import collections
import json
from pathlib import Path
import sys
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
SOURCE=ROOT.parent/'cyberAlchemy-v2'
PREVIOUS=HERE.parent/'0008-capability-inventory-import'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool

def acceptance(capability,nodes,relations,rule_ids):
    by_id={n['id']:n for n in nodes}
    if len(by_id)!=len(nodes):raise ValueError('Duplicate node identity')
    reachable=set(capability['inputs']+capability['outputs']+[capability['capability_id']])
    # Include the workflow producing the outputs and concepts used by them.
    changed=True
    while changed:
        before=set(reachable)
        for edge in relations:
            if edge['type']=='produces' and edge['target'] in reachable:reachable.add(edge['source'])
            if edge['type']=='uses' and edge['source'] in reachable:reachable.add(edge['target'])
        changed=before!=reachable
    mapped=[]
    for ident in rule_ids:
        rule=by_id.get(ident)
        if not rule or rule['kind']!='Business Rule' or not tool.text(rule.get('meaning')):raise ValueError('Missing or invalid acceptance rule: '+ident)
        edges=[e for e in relations if e['type']=='constrains' and e['source']==ident and e['target'] in reachable]
        if not edges:raise ValueError('Rule has no applicable constraint relation: '+ident)
        if any(e['authority_effect']!='none' for e in edges) or rule['authority_effect']!='none':raise ValueError('Unexpected rule authority effect')
        mapped.append({'rule_id':ident,'statement':rule['meaning'],'relations':edges})
    if len({m['rule_id'] for m in mapped})!=5:raise ValueError('Expected five distinct source rules')
    return mapped

def prepare():
    receipt=tool.read(PREVIOUS/'verification.json')
    for ref in receipt['bindings']:
        if ref['path'].endswith('capability_inventory_import.py') or ref['path'].endswith('/imports.json'):
            if tool.sha(ROOT/ref['path'])!=ref['sha256']:raise ValueError('Predecessor implementation or import drift')
    registry=tool.load_registry();plan=tool.read(HERE/'plan.json');docs={};index=collections.defaultdict(list)
    for ref in plan['sources']:
        p=SOURCE/ref['path']
        if tool.sha(p)!=ref['sha256']:raise ValueError('Source drift: '+ref['path'])
        docs[ref['path']]=tool.read(p)
        for ptr,row in tool.walk(docs[ref['path']]):
            if tool.text(row.get('id')):index[row['id']].append({'source':{**ref,'selector':ptr},'record':row})
    prefix='agent-reasoning-engine/framings/'
    cap=docs[prefix+'product-capability.json'];nodes=docs[prefix+'nodes.json']['nodes'];edges=docs[prefix+'relations.json']['relations']
    if cap['capability_id']!=plan['capability_id']:raise ValueError('Wrong capability')
    profile=docs[prefix+'profile.json']
    if profile['product_capability_ref']!=cap['capability_id']:raise ValueError('Package binding mismatch')
    schema=docs[prefix+'schemas/framings.schema.json']
    Draft202012Validator({**schema,'$ref':'#/$defs/productCapability'}).validate(cap)
    mappings=acceptance(cap,nodes,edges,plan['rule_ids'])
    enriched={**cap,'acceptance_conditions':[m['statement'] for m in mappings],'input_contract_refs':cap['inputs'],'output_contract_refs':cap['outputs']}
    sys.path.insert(0,str(ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0026-remaining-targets-review-batch'))
    import engine
    source_ref=next(r for r in plan['sources'] if r['path']==prefix+'product-capability.json')
    result=tool.normalize({'record':enriched,'source':{**source_ref,'selector':''}},index,engine,registry['scope'])
    entry=next(e for e in registry['entries'] if e['target_id']=='type.product-capability')
    for ref in plan['sources']:
        if tool.sha(SOURCE/ref['path'])!=ref['sha256']:raise ValueError('Source changed during import')
    return {**result,'id':cap['capability_id'],'status':'imported-candidate','source':{**source_ref,'selector':''},'source_record':cap,'acceptance_mapping':mappings,'source_bindings':plan['sources'],'contract':entry['contract'],'semantic_dependencies':entry['semantic_definition_bindings'],'authority_effect':'none','operational_use_authorized':False}

if __name__=='__main__':
    result=prepare();prior=tool.read(PREVIOUS/'imports.json')
    if any(x['id']==result['id'] for x in prior):raise ValueError('Already imported')
    combined=prior+[result]
    import engine
    nodes={}
    for item in combined:
        for record in [item['product'],item['capability']]:
            if record['node_id'] in nodes and nodes[record['node_id']]!=record:raise ValueError('Graph identity collision')
            nodes[record['node_id']]=record
    engine.validate_graph({'schema_version':'cal-review-graph/v1','authority_effect':'none','nodes':list(nodes.values()),'relations':[]})
    inventory=tool.read(PREVIOUS/'inventory.json');changed=0
    for row in inventory['results']:
        if row['id']==result['id'] and row['source']==result['source'] and row['status']=='blocked':
            row.update(status='imported-candidate',reason='Five source-owned Business Rules mapped to acceptance conditions; input/output references validated.');changed+=1
    if changed!=1:raise ValueError('Expected exactly one blocked transition')
    inventory['counts']=dict(collections.Counter(x['status'] for x in inventory['results']))
    store=ROOT/'.local/capability-inventory-import-0009'
    if store.exists():raise ValueError('Preserve existing store')
    store.mkdir()
    for name,data in [('result.json',result),('imports.json',combined),('inventory.json',inventory)]:
        text=json.dumps(data,indent=2,sort_keys=True)+'\n';(HERE/name).write_text(text)
        if name=='imports.json':(store/name).write_text(text)
    print(json.dumps({'result':'PASS','capability':result['id'],'mapped_rules':5,'counts':inventory['counts']}))
