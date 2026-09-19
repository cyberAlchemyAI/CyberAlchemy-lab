import copy,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('essays_import',HERE/'import.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
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
sources=r(p/'SOURCES.json')['sources'];assert len(sources)==12
for src in sources:
    path=m.PACKAGE/src['path'];assert m.tool.sha(path)==src['sha256'] and path.stat().st_size==src['size_bytes'];assert all(s in path.read_text() for s in src['selectors'])
result=r(HERE/'source-validation.json');output=json.loads(result['stdout'])
assert result['exit_code']==0 and output['overall']=='FLAG' and output['summary']['blocked']==0 and output['summary']['passed']==14
assert [(c['check_id'],c['outcome']) for c in output['checks'] if c['outcome']!='PASS']==[('d65-successors','FLAG')]
assert r(HERE/'successor-observation.json')['source_validator_unchanged'] is True
cap=r(m.PACKAGE/'cyberAlchemy-v2/essays/capabilities/essays-agent-runtime.product-capability.json')
refs=cap['input_contract_refs']+cap['output_contract_refs']+cap['context_policy_refs']+cap['realization_binding_refs']+[cap['obligation_registry_ref']]
decision=r(m.PACKAGE/'cyberAlchemy-v2/goals/projects/essays/decisions/agent-runtime-capability-records/selection.json')
assert len(refs)==len(set(refs))==8 and set(refs)==set(decision['subject']['record_ids'])
residue=[json.loads(line) for line in (p/'RESIDUE.jsonl').read_text().splitlines() if line];assert len(residue)==5 and all(d['authority_effect']=='none' for d in residue)
for entry in r(HERE/'package-inputs.json'):assert m.tool.sha(m.PACKAGE/entry['path'])==entry['sha256']
assert r(m.STORE/'bundle.json')==b
assert (m.ROOT/'.local/capability-inventory-import-0035/imports.json').read_bytes()==(m.CAPS/'imports.json').read_bytes()
m.dump(HERE/'verification.json',{'result':'PASS','authority_effect':'none','checks':['predecessor bindings and existing migration header contracts','restored source result exactly reproduces 14 PASS and one historical FLAG','duplicate node rejected','duplicate relation rejected','dangling endpoint rejected','unknown relation kind rejected','authority escalation rejected','all source-qualified model pointers resolve','all twelve source fingerprints sizes and selectors exact','eight dependent capability record identities resolve to pinned selection','five source residue entries and historical warning annotation preserved','capability storage and entire restored snapshot unchanged'],'bindings':[m.bind(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='verification.json']})
print('PASS: twelve import checks; 14 source checks pass with one annotated historical successor flag.')
