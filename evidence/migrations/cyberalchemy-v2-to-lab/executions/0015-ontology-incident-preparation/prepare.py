"""Prepare exact source fields without fabricating a Product or Capability owner."""
import json
from pathlib import Path
import subprocess
import sys
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
SOURCE=ROOT.parent/'cyberAlchemy-v2'
PREVIOUS=HERE.parent/'0014-continuous-task-loop-import'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool
ID='CA2-CAP-LEARN-ONTOLOGY-INCIDENT'
PATH='essays/implementation/bug-ticket-ontology-game/product-capability-candidate.json'
def bind(p,root=ROOT):return {'path':str(p.relative_to(root)),'sha256':tool.sha(p)}
def prepare():
    registry=tool.load_registry();inventory=tool.read(PREVIOUS/'inventory.json')
    row=next(x for x in inventory['results'] if x['id']==ID and x['category']=='declaration')
    if tool.sha(SOURCE/PATH)!=row['source']['sha256']:raise ValueError('Source capability changed')
    cap=tool.read(SOURCE/PATH)
    if cap['capability_id']!=ID:raise ValueError('Wrong capability')
    mapped={'node_id':'cav2:'+PATH+'#'+ID,'kind':'product-capability','status':'candidate-unadmitted','authority_effect':'none','scope_ref':registry['scope'],'outcome':cap['product_promise'],'acceptance_conditions':cap['bounded_user_journey'],'exclusions':cap['forbidden_outcomes']}
    entry=next(x for x in registry['entries'] if x['target_id']=='type.product-capability')
    schema=tool.read((ROOT/entry['binding']['path']).parent/'schema.json')
    errors=list(Draft202012Validator(schema).iter_errors(mapped))
    missing=sorted(set(schema['required'])-set(mapped))
    if missing!=['owner_ref','product_ref'] or any(e.validator!='required' for e in errors):raise ValueError('Unexpected preparation gap')
    paths=subprocess.check_output(['rg','-l','--hidden','-g','!.git','-g','*.json','-g','*.md','-F','-e',ID,'-e','bug-ticket-ontology-game',str(SOURCE)],text=True).splitlines()
    search=[];ownership=[]
    for file in sorted(paths):
        p=Path(file)
        if not p.resolve().is_relative_to(SOURCE.resolve()):raise ValueError('Reference outside repository')
        search.append(bind(p,SOURCE))
        if p.suffix!='.json':continue
        try:doc=tool.read(p)
        except ValueError:continue
        for ptr,obj in tool.walk(doc):
            if obj.get('capability_id')==ID:
                for key in ['product_ref','parent_capability_ref','extends_capability_ref','owner','owner_ref','owner_route','owner_routes']:
                    if key in obj:ownership.append({'path':str(p.relative_to(SOURCE)),'selector':ptr,'field':key,'value':obj[key]})
    if ownership:raise ValueError('Explicit ownership leads found; inspect before declaring missing')
    for ref in search:
        if tool.sha(SOURCE/ref['path'])!=ref['sha256']:raise ValueError('Source changed during search')
    return {'capability_id':ID,'status':'prepared-not-importable','mapped_fields':mapped,'missing_fields':missing,'source_record':cap,'source_binding':bind(SOURCE/PATH,SOURCE),'contract':entry['contract'],'mappings':{'outcome':'/product_promise','acceptance_conditions':'/bounded_user_journey','exclusions':'/forbidden_outcomes'},'reference_search':search,'ownership_leads':ownership,'decision_needed':'Select the owning Product and Capability owner route; directory placement and simulated game roles do not determine these.','authority_effect':'none','imported':False}
if __name__=='__main__':
    result=prepare();text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    p=HERE/'result.json'
    if p.exists() and p.read_text()!=text:raise ValueError('Preserve existing preparation')
    p.write_text(text)
    inventory=tool.read(PREVIOUS/'inventory.json')
    for row in inventory['results']:
        if row['id']==ID and row['category']=='declaration':row.update(reason='Outcome, acceptance journey and exclusions prepared; explicit Product and Capability owner missing.',resolution_state='reviewed-needs-product-and-owner',preparation=bind(p))
    (HERE/'inventory.json').write_text(json.dumps(inventory,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'result':'PREPARED','missing_fields':result['missing_fields'],'reference_files_checked':len(result['reference_search']),'imported':False}))
