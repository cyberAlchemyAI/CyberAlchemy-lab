"""Prepare declared dataset requirements without inferring Product ownership from dependencies."""
import copy,json,subprocess,sys
from pathlib import Path
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];SOURCE=ROOT.parent/'cyberAlchemy-v2';PREV=HERE.parent/'0030-no-price-solana-import'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool
ID='CA2-CAP-MATERIALIZE-TRUSTED-DATASET'
def bind(p,root=ROOT):return {'path':str(p.relative_to(root)),'sha256':tool.sha(p)}
def dump(p,obj):
    text=json.dumps(obj,indent=2,sort_keys=True)+'\n'
    if p.exists() and p.read_text()!=text:raise ValueError('Preserve existing artifact')
    p.write_text(text)
def review():
    for b in tool.read(PREV/'verification.json')['bindings']:
        if tool.sha(ROOT/b['path'])!=b['sha256']:raise ValueError('Historical drift')
    registry=tool.load_registry();old=tool.read(PREV/'inventory.json');row=next(r for r in old['results'] if r['id']==ID and r['category']=='declaration');path=SOURCE/row['source']['path']
    if tool.sha(path)!=row['source']['sha256']:raise ValueError('Source drift')
    cap=tool.read(path);owner_path=path.parent/'implementation-layering.md';owner_doc=owner_path.read_text();owner='CyberAlchemy v2 trusted-dataset capability owner'
    if '\nowner: '+owner+'\n' not in owner_doc or '\nscope: capability\n' not in owner_doc:raise ValueError('Owner selector changed')
    files=subprocess.check_output(['rg','-l','--hidden','-g','!.git','-g','*.json','-g','*.md','-F','-e',ID,'-e','trusted-dataset-materialization',str(SOURCE)],text=True).splitlines()
    bindings=[];leads=[];parse_errors=[]
    for f in sorted(files):
        p=Path(f);bindings.append(bind(p,SOURCE))
        if p.suffix!='.json':continue
        try:doc=tool.read(p)
        except ValueError as exc:parse_errors.append({'path':str(p.relative_to(SOURCE)),'error':str(exc)});continue
        for ptr,obj in tool.walk(doc):
            if obj.get('capability_id')==ID or obj.get('product_capability_id')==ID:
                for key in ['product_ref','parent_capability_ref','extends_capability_ref']:
                    if key in obj:leads.append({'path':str(p.relative_to(SOURCE)),'selector':ptr,'field':key,'value':obj[key]})
    if leads:raise ValueError('Product leads require review')
    prepared={'node_id':'cav2:'+row['source']['path']+'#'+ID,'kind':'product-capability','status':'candidate-unadmitted','scope_ref':registry['scope'],'authority_effect':'none','owner_ref':owner,'outcome':cap['purpose'],'acceptance_conditions':cap['invariants'],'exclusions':cap['non_goals']}
    entry=next(e for e in registry['entries'] if e['target_id']=='type.product-capability');schema=tool.read((ROOT/entry['binding']['path']).parent/'schema.json');errors=list(Draft202012Validator(schema).iter_errors(prepared))
    if len(errors)!=1 or errors[0].validator!='required' or set(schema['required'])-set(prepared)!={'product_ref'}:raise ValueError('Unexpected preparation gap')
    for b in bindings:
        if tool.sha(SOURCE/b['path'])!=b['sha256']:raise ValueError('Search source changed')
    return {'id':ID,'status':'prepared-not-importable','imported':False,'authority_effect':'none','source_record':cap,'prepared_fields':prepared,'source_bindings':[bind(path,SOURCE),bind(owner_path,SOURCE)],'mapping':{'owner_ref':'implementation-layering.md front matter, scope capability; candidate owner-role projection','outcome':'/purpose','acceptance_conditions':'/invariants','exclusions':'/non_goals'},'missing_required_fields':['product_ref'],'product_leads':leads,'search_bindings':bindings,'parse_errors':parse_errors,'search_scope':'Nonignored JSON/Markdown matching capability ID or package name; exact capability declarations checked for Product/parent fields; prose absence is not proven.','decision_needed':'Identify the Product this dataset capability belongs to. A dependency on work orchestration does not establish ownership.'}
if __name__=='__main__':
    result=review();dump(HERE/'result.json',result);old=tool.read(PREV/'inventory.json');new=copy.deepcopy(old)
    for row in new['results']:
        if row['id']==ID and row['category']=='declaration':row.update(resolution_state='reviewed-needs-product',reason='Six requirements and declared capability owner prepared; owning Product not declared in reviewed source bindings.',review=bind(HERE/'result.json'))
    dump(HERE/'inventory.json',new)
    print(json.dumps({'status':result['status'],'source_files_checked':len(result['search_bindings']),'missing':['product_ref'],'parse_errors':len(result['parse_errors'])}))
