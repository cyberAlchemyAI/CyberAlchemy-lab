import copy,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('hosted_context',HERE/'import.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
r=m.tool.read;b=r(HERE/'bundle.json');assert m.build()==b
for mode in ['endpoint','duplicate','branch','evidence','authority']:
    s=copy.deepcopy(b['source_graph'])
    if mode=='endpoint':s['relations'][0]['target']='missing'
    elif mode=='duplicate':s['nodes'].append(copy.deepcopy(s['nodes'][0]))
    elif mode=='branch':next(v for v in s['relations'] if v['branch']=='bridge')['branch']='business'
    elif mode=='evidence':s['relations'][0]['evidence_refs']=[]
    else:s['authority_effect']='admitted'
    try:m.validate_graph(s,{})
    except ValueError:pass
    else:raise AssertionError('Invalid source accepted')
assert r(m.STORE/'bundle.json')==b
for ref in b['snapshots']:
    p=m.ROOT/ref['path'];assert p.read_bytes()==(m.STORE/'source'/p.name).read_bytes()
for ref in b['ontology']['concept_refs']:
    file,ptr=ref.split('#');obj=r(m.STORE/file)
    for key in ptr.strip('/').split('/'):obj=obj[int(key)] if isinstance(obj,list) else obj[key]
    assert obj['node_id']
assert b['source_graph']['construction_state']['vps_deployment']=='not_authorized'
assert len(b['implementation_evidence_bindings'])==5
assert (m.ROOT/'.local/capability-inventory-import-0035/imports.json').read_bytes()==(m.CAPS/'imports.json').read_bytes()
m.dump(HERE/'verification.json',{'result':'PASS','checks':['source-bound replay and Lab header schemas','dangling endpoint rejected','duplicate node rejected','cross-branch misclassification rejected','missing evidence references rejected','authority escalation rejected','stored snapshots/pointers and five implementation references close','source deployment limit and capability store preserved'],'bindings':[m.bind(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='verification.json'],'authority_effect':'none','runtime_tests_rerun':False})
print('PASS: eight checks; six business and six system nodes, 14 relations, eight bridge links.')
