"""Check closure and preservation; reject invalid coverage mutations. Open questions: README.md."""
import copy,importlib.util
from pathlib import Path
H=Path(__file__).resolve().parent;s=importlib.util.spec_from_file_location('bridge_import',H/'import.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
b=m.build();doc=m.r(m.PACKAGE/m.PREFIX/'COVERAGE.json');ob=m.r(m.PACKAGE/m.OBL)['obligations']
cases=['duplicate-obligation','missing-obligation','unknown-obligation','missing-file','missing-test','escaping-path','promoted-proof','authority','duplicate-reference']
for case in cases:
 d=copy.deepcopy(doc);row=d['coverage'][0]
 if case=='duplicate-obligation':d['coverage'].append(copy.deepcopy(row))
 elif case=='missing-obligation':d['coverage'].pop()
 elif case=='unknown-obligation':row['obligation']='missing'
 elif case=='missing-file':row['implementation']=['src/missing.rs']
 elif case=='missing-test':row['evidence']=['tests/runtime.rs#missing_test']
 elif case=='escaping-path':row['implementation']=['../../../../../../etc/passwd']
 elif case=='promoted-proof':row['result']='pass'
 elif case=='authority':d['authority_effect']='admitted'
 else:row['implementation'].append(row['implementation'][0])
 try:m.model_check(d,ob)
 except ValueError:pass
 else:raise AssertionError(case)
for ref in b['ontology']['concept_refs']:
 file,ptr=ref.split('#');obj=m.r(m.STORE/file)
 for key in ptr.strip('/').split('/'):obj=obj[int(key)] if isinstance(obj,list) else obj[key]
 assert obj in doc['coverage']
assert b['ontology']['relation_ids']==[]
gaps=m.r(H/'evidence-gaps.json');assert gaps['empty_evidence_obligations']==['CAP-OBL-ESSAYS-AR-006-CLIENT-PARITY'];assert len(gaps['authored_tests'])==10 and not gaps['runtime_tests_executed'];assert len(gaps['source_residue']['residue'])==6
manifest=m.r(H/'package-inputs.json')
assert {str(p.relative_to(m.PACKAGE)) for p in m.PACKAGE.rglob('*') if p.is_file()}=={x['path'] for x in manifest}
for x in manifest:assert m.tool.sha(m.PACKAGE/x['path'])==x['sha256']
assert (m.ROOT/'.local/capability-inventory-import-0035/imports.json').read_bytes()==(m.CAPS/'imports.json').read_bytes()
assert m.r(m.STORE/'bundle.json')==b
m.dump(H/'verification.json',{'result':'PASS','authority_effect':'none','negative_cases':cases,'checks':['frozen system and capability predecessors verified','existing migration header contracts validate','all twenty obligations covered exactly once','every implementation and evidence path resolves within runtime scope','ten distinct authored test anchors resolve','historical receipt and obligations match execution 0068 exactly','source validator reproduces FLAG with twenty partial rows and zero errors','client parity gap and all six residue statements preserved','all source pointers resolve without invented graph relations','nine invalid coverage mutations rejected','restored snapshot and capability store unchanged'],'bindings':[m.bind(p) for p in sorted(H.rglob('*')) if p.is_file() and p.name!='verification.json']})
print('PASS: eleven import checks and nine rejection cases; source remains FLAG, twenty partial, zero proven.')
