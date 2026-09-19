import copy,hashlib,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('bridge_import',HERE/'import.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
b=m.build();r=m.tool.read;p=m.PACKAGE/m.PREFIX
for mode in ['duplicate-node','duplicate-relation','endpoint','relation-kind','authority','missing-child','child-redefinition']:
    nodes=r(p/'nodes.json')['nodes'];relations=r(p/'relations.json')['relations'];profile=r(p/'profile.json');external=copy.deepcopy(b['external_nodes'])
    if mode=='duplicate-node':nodes.append(copy.deepcopy(nodes[0]))
    elif mode=='duplicate-relation':relations.append(copy.deepcopy(relations[0]))
    elif mode=='endpoint':relations[0]['target']='missing'
    elif mode=='relation-kind':relations[0]['type']='unowned-kind'
    elif mode=='missing-child':del external[next(iter(external))]
    elif mode=='child-redefinition':nodes.append({**nodes[0],'id':next(iter(external))})
    else:profile['authority_effect']='admitted'
    try:m.graph_check(nodes,relations,profile,external)
    except ValueError:pass
    else:raise AssertionError(mode)
def resolve(ref):
    file,ptr=ref.split('#');obj=r(m.STORE/file)
    for key in ptr.strip('/').split('/'):obj=obj[int(key)] if isinstance(obj,list) else obj[key]
    return obj
for ref in b['ontology']['concept_refs']+b['ontology']['relation_ids']:assert isinstance(resolve(ref),dict)
for qualified,entry in b['external_nodes'].items():
    node=resolve(entry['source_ref']);assert node.get('id',node.get('node_id'))==qualified.split('::')[1]
    assert m.tool.sha(m.ROOT/entry['context_bundle']['path'])==entry['context_bundle']['sha256']
for folder in [m.BUSINESS,m.SYSTEM]:
    for entry in r(folder/'package-inputs.json'):assert m.tool.sha(m.PACKAGE/entry['path'])==entry['sha256']
old=r(HERE/'original-sources.json');expected=copy.deepcopy(old);row=next(s for s in expected['sources'] if s['id']=='SRC-CAV2-PRODUCT-THESIS');thesis=m.PACKAGE/row['path'];row['sha256']=m.tool.sha(thesis);row['size']=thesis.stat().st_size
assert expected==r(p/'sources.json')
recovery=r(HERE/'source-recovery.json');assert len(recovery['sources'])==30 and sum(s['exact'] for s in recovery['sources'])==29
for source in r(p/'sources.json')['sources']:
    path=m.PACKAGE/source['path'];assert m.tool.sha(path)==source['sha256'] and path.stat().st_size==source['size'];assert all(s in path.read_text() for s in source['selectors'])
validation=r(HERE/'source-validation.json');output=json.loads(validation['stdout']);assert validation['exit_code']==0 and output['overall']=='PASS' and output['summary']['passed']==27
assert output['child_runs']['business']['overall']=='PASS' and output['child_runs']['system']['overall']=='FLAG'
assert output['child_runs']['business']['output_sha256']==r(m.BUSINESS/'source-validation.json')['stdout_sha256']
assert output['child_runs']['system']['output_sha256']==hashlib.sha256(r(m.SYSTEM/'source-validation.json')['stdout'].encode()).hexdigest()
assert r(p/'construction-handoffs.json')['handoffs']==[] and r(p/'construction-handoffs.json')['status']=='candidate-empty-blocked'
assert len([line for line in (p/'residue.jsonl').read_text().splitlines() if line])==11
for entry in r(HERE/'package-inputs.json'):assert m.tool.sha(m.PACKAGE/entry['path'])==entry['sha256']
assert r(m.STORE/'bundle.json')==b
assert (m.ROOT/'.local/capability-inventory-import-0035/imports.json').read_bytes()==(m.CAPS/'imports.json').read_bytes()
m.dump(HERE/'verification.json',{'result':'PASS','authority_effect':'none','checks':['predecessor bindings and existing migration header contracts','27 restored source checks pass with exact child results','duplicate local node rejected','duplicate relation rejected','unknown endpoint rejected','unknown relation kind rejected','authority escalation rejected','missing child binding rejected','child node redefinition rejected','all local and qualified child model pointers resolve','both imported child snapshots remain entirely byte-identical','29 exact recoveries and only explicit thesis fingerprint/size successor','empty blocked handoff and eleven residue entries preserved','capability storage and entire restored snapshot unchanged'],'bindings':[m.bind(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='verification.json']})
print('PASS: fourteen import checks and twenty-seven source checks; both child snapshots unchanged.')
