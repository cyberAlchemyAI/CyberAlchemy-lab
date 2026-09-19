import copy,hashlib,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('define_import',HERE/'import.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
b=m.build();r=m.tool.read;p=m.PACKAGE/m.PREFIX
for mode in ['duplicate-node','duplicate-relation','endpoint','relation-kind','authority']:
    nodes=r(p/'NODES.json')['nodes'];relations=r(p/'RELATIONS.json')['relations'];profile=r(p/'PROFILE.json')
    if mode=='duplicate-node':nodes.append(copy.deepcopy(nodes[0]))
    elif mode=='duplicate-relation':relations.append(copy.deepcopy(relations[0]))
    elif mode=='endpoint':relations[0]['target']='missing'
    elif mode=='relation-kind':relations[0]['type']='unowned-kind'
    else:profile['authority_effect']='admitted'
    try:m.graph_check(nodes,relations,profile)
    except ValueError:pass
    else:raise AssertionError(mode)
for ref in b['ontology']['concept_refs']+b['ontology']['relation_ids']:
    file,ptr=ref.split('#');obj=r(m.STORE/file)
    for key in ptr.strip('/').split('/'):obj=obj[int(key)] if isinstance(obj,list) else obj[key]
    assert isinstance(obj,dict)
old=r(HERE/'original-sources.json');current=r(p/'SOURCES.json');expected=copy.deepcopy(old)
source=next(s for s in expected['sources'] if s['source_id']=='SRC-CAV2-PRODUCT-THESIS');path=m.PACKAGE/source['path'];source['sha256']=m.tool.sha(path);source['size_bytes']=path.stat().st_size
assert current==expected
assert sum(s['exact_recovery'] for s in r(HERE/'source-recovery.json'))==12
for src in current['sources']:
    path=m.PACKAGE/src['path'];assert m.tool.sha(path)==src['sha256'] and path.stat().st_size==src['size_bytes'];assert all(s in path.read_text() for s in src['selectors'])
receipt=r(m.PACKAGE/r(HERE/'successor-changes.json')['receipt_path']);validation=r(HERE/'source-validation.json')
assert receipt['validation_output_sha256']==validation['stdout_sha256']==hashlib.sha256((json.dumps(validation['output'],indent=2,sort_keys=True)+'\n').encode()).hexdigest()
assert receipt['material_digest']==validation['output']['material_digest']
residue=[json.loads(line) for line in (p/'RESIDUE.jsonl').read_text().splitlines() if line];assert len(residue)==5 and all(d['authority_effect']=='none' for d in residue)
for entry in r(HERE/'package-inputs.json'):assert m.tool.sha(m.PACKAGE/entry['path'])==entry['sha256']
assert r(m.STORE/'bundle.json')==b
assert (m.ROOT/'.local/capability-inventory-import-0035/imports.json').read_bytes()==(m.CAPS/'imports.json').read_bytes()
m.dump(HERE/'verification.json',{'result':'PASS','authority_effect':'none','checks':['predecessor bindings and existing migration header contracts','restored source validator passes all 16 checks','duplicate node rejected','duplicate relation rejected','dangling endpoint rejected','unknown relation kind rejected','authority escalation rejected','all source-qualified model pointers resolve','twelve exact recoveries and only explicit thesis fingerprint/size successor','all thirteen source fingerprints and selectors verified','append-only receipt exactly binds observed validation bytes','five residue entries preserved and capability storage and snapshot unchanged'],'bindings':[m.bind(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='verification.json']})
print('PASS: twelve import checks and sixteen source checks; 13 concepts, 12 relations, five preserved residue items.')
