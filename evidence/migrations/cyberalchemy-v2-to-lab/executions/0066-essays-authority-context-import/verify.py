import copy,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('authority_import',HERE/'import.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
b=m.build();r=m.tool.read;p=m.PACKAGE/m.PREFIX
def views_check(nodes,relations,views):
    ids={n['id'] for n in nodes};edges={e['id']:e for e in relations};view_ids=[v['view_id'] for v in views]
    if len(view_ids)!=len(set(view_ids)):raise ValueError('Duplicate view')
    for v in views:
        if len(v['node_ids'])!=len(set(v['node_ids'])) or len(v['relation_ids'])!=len(set(v['relation_ids'])):raise ValueError('Duplicate view entry')
        if not set(v['node_ids'])<=ids or not set(v['relation_ids'])<=set(edges):raise ValueError('Unknown view reference')
        if any(not {edges[e]['source'],edges[e]['target']}<=set(v['node_ids']) for e in v['relation_ids']):raise ValueError('View edge not closed')
nodes=r(p/'NODES.json')['nodes'];relations=r(p/'RELATIONS.json')['relations'];profile=r(p/'PROFILE.json');views=r(p/'VIEWS.json')['views'];views_check(nodes,relations,views)
for mode in ['duplicate-node','duplicate-relation','endpoint','empty-relation-kind','authority']:
    n=copy.deepcopy(nodes);e=copy.deepcopy(relations);pr=copy.deepcopy(profile)
    if mode=='duplicate-node':n.append(copy.deepcopy(n[0]))
    elif mode=='duplicate-relation':e.append(copy.deepcopy(e[0]))
    elif mode=='endpoint':e[0]['target']='missing'
    elif mode=='empty-relation-kind':e[0]['type']=''
    else:pr['authority_effect']='admitted'
    try:m.graph_check(n,e,pr)
    except ValueError:pass
    else:raise AssertionError(mode)
for mode in ['missing-relation','duplicate-view']:
    v=copy.deepcopy(views)
    if mode=='missing-relation':v[0]['relation_ids'].append('missing')
    else:v.append(copy.deepcopy(v[0]))
    try:views_check(nodes,relations,v)
    except ValueError:pass
    else:raise AssertionError(mode)
for ref in b['ontology']['concept_refs']+b['ontology']['relation_ids']:
    file,ptr=ref.split('#');obj=r(m.STORE/file)
    for key in ptr.strip('/').split('/'):obj=obj[int(key)] if isinstance(obj,list) else obj[key]
    assert isinstance(obj,dict)
sources=r(p/'SOURCES.json')['sources'];assert len(sources)==len({s['source_id'] for s in sources})==5
for src in sources:
    path=m.PACKAGE/src['path'];assert m.tool.sha(path)==src['sha256'] and path.stat().st_size==src['size_bytes'];assert all(s in path.read_text() for s in src['selectors'])
assert set(profile['material_files'])=={str(f.relative_to(p)) for f in p.rglob('*') if f.is_file() and 'receipts' not in f.relative_to(p).parts}
output=json.loads(r(HERE/'source-validation.json')['stdout']);assert output['overall']=='PASS' and not output['errors'] and output['authority_effect']=='none'
receipts=list((p/'receipts').glob('*'));assert len(receipts)==1
receipt=r(receipts[0]);assert receipt.pop('validated_at')=='2026-09-01' and receipt==output
assert receipts[0].name=='validation-'+output['material_digest'][:16]+'.json'
assert profile['status']=='candidate-development-pre-merge-approval-pending'
residue=r(p/'RESIDUE.json')['residue'];assert len(residue)==2 and all(d['authority_effect']=='none' and d['status']=='open' for d in residue)
for entry in r(HERE/'package-inputs.json'):assert m.tool.sha(m.PACKAGE/entry['path'])==entry['sha256']
assert r(m.STORE/'bundle.json')==b
assert (m.ROOT/'.local/capability-inventory-import-0035/imports.json').read_bytes()==(m.CAPS/'imports.json').read_bytes()
m.dump(HERE/'verification.json',{'result':'PASS','authority_effect':'none','checks':['predecessor bindings and existing migration header contracts','restored source validator passes without errors','duplicate node rejected','duplicate relation rejected','dangling endpoint rejected','empty relation kind rejected','authority escalation rejected','unknown view relation rejected','duplicate view rejected','all six views close over declared nodes and relations','all model pointers, five exact sources and closed inventory verified','pending approval and two open residue entries preserved','capability storage and entire restored snapshot unchanged'],'bindings':[m.bind(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='verification.json']})
print('PASS: thirteen import checks; source validation passes; 11 concepts and 11 relationships.')
