import copy,hashlib,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];SOURCE=ROOT.parent/'cyberAlchemy-v2'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for b in read(HERE/'source-bindings.json'):
 assert sha(HERE/b['snapshot'])==b['sha256'] and sha(SOURCE/b['path'])==b['sha256']
rows=read(HERE/'compiler-recovery.json');assert len(rows)==9
assert sum(bool(r['match']) for r in rows)==8
for r in rows:
 if r['match']:assert sha(HERE/r['match']['snapshot'])==r['expected']
 else:assert r['path'].endswith('/src/cli.ts')
spec=importlib.util.spec_from_file_location('routing_source',SOURCE/'agent-routing/scripts/validate.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
routes=read(HERE/'source/routes.json');ontology=read(HERE/'source/ontology.json');errors=[]
m.validate_routes(routes,errors);m.validate_ontology(ontology,errors);assert not errors
bad=copy.deepcopy(ontology);bad['relations'][0]['target']='missing';errors=[];m.validate_ontology(bad,errors);assert errors
bad=copy.deepcopy(routes);bad['routes'][0]['fallback_route']='CA2-ROUTE-LOCATE';errors=[];m.validate_routes(bad,errors);assert errors
assert [r['route_id'] for r in routes['routes'] if r['lifecycle_state']=='blocked']==['CA2-ROUTE-SESSION']
for b in read(HERE.parent/'0049-contextual-framings-context-import/verification.json')['bindings']:assert sha(ROOT/b['path'])==b['sha256']
report={'result':'PASS','scope':'preparation and evidence recovery only; full source validation remains BLOCK','authority_effect':'none','checks':['source snapshots unchanged','eight exact compiler versions recovered','business graph and route checks pass','dangling relation rejected','routing fallback rejected','blocked session route and predecessor preserved'],'bindings':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='verification.json']}
(HERE/'verification.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print('PASS: six preparation checks; one compiler version remains unresolved.')
