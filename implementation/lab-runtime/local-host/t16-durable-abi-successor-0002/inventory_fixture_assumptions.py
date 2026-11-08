"""Statically expose literal fixture assumptions without changing test methods."""
import ast,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v68-t16-live-source-freshness-0001'
ORIGINAL=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v53-t16-challenge-source-0001'
HERE=Path(__file__).resolve().parent
sha=lambda raw:hashlib.sha256(raw).hexdigest()
def scan(folder):
 methods={};outside=[]
 for path in sorted([*folder.glob('test_*.py'),*folder.glob('run_*checks.py')]):
  text=path.read_text();tree=ast.parse(text)
  for cls in tree.body:
   if not isinstance(cls,ast.ClassDef):continue
   for method in cls.body:
    if not isinstance(method,ast.FunctionDef) or not method.name.startswith('test_'):continue
    key=path.name+':'+cls.name+'.'+method.name
    body=ast.get_source_segment(text,method)
    methods[key]={'ast_sha256':sha(ast.dump(method,include_attributes=False).encode()),'line':method.lineno,'contains_lesson_literal':any(isinstance(n,ast.Constant) and type(n.value)is str and 'lesson' in n.value.lower() for n in ast.walk(method)),'contains_current_family_literal':bool(re.search(r'legacy-local-[a-f0-9]{16}',body)),'inventory_count_literals':sorted({n.value for n in ast.walk(method) if isinstance(n,ast.Constant) and type(n.value)is int and n.value in (15,17,30,34,604,608,616)})}
  for node in ast.walk(tree):
   if isinstance(node,ast.Constant) and isinstance(node.value,str) and re.search(r'legacy-local-[a-f0-9]{16}',node.value):
    outside.append({'file':path.name,'line':node.lineno,'value':node.value})
 return methods,outside
methods,ids=scan(API);old,_=scan(ORIGINAL)
if len(methods)!=345 or set(methods)!=set(old):raise ValueError('exact inherited inventory differs')
changed=[k for k in methods if methods[k]['ast_sha256']!=old[k]['ast_sha256']]
if changed:raise ValueError('inherited test AST changed')
runtime=[]
for name in ('current_legacy_context_sessions.py','legacy_context_sessions.py','context_sessions.py','native_dispositions.py','freeze_machine_transport.py'):
 path=API/name
 for i,line in enumerate(path.read_text().splitlines(),1):
  if re.search(r'==\s*(?:15|30|604|616)\b',line):runtime.append({'file':name,'line':i,'text':line.strip()})
family_assumptions=[]
family=HERE/'instances/legacy-local-83f9427adb0c1e65'
for relative in ('mapped/build.py','context/generation.py','context/build.py'):
 path=family/relative
 for line_no,line in enumerate(path.read_text().splitlines(),1):
  if re.search(r'require\(.*(?:==\s*(?:15|10|30)\b|not lessons)|actual_generated_artifact_carriers.*30|node_count.*15',line):
   family_assumptions.append({'path':path.relative_to(ROOT).as_posix(),'line':line_no,'text':line.strip()})
value={'schema_version':'lab-T16-inherited-fixture-assumptions/v1','authority_effect':'none','selected_api':API.relative_to(ROOT).as_posix(),'api_source_sha256':sha((API/'source-manifest.json').read_bytes()),'original_api':ORIGINAL.relative_to(ROOT).as_posix(),'inherited_methods':345,'changed_method_asts':changed,'method_rows':methods,'explicit_family_ids_outside_test_methods':ids,'runtime_and_freeze_assumptions':runtime,'selected_generic_family_constructor_assumptions':family_assumptions,'findings':[
'No inherited test_* body has a Lesson literal or fixed current-family identity literal. No inherited test body directly asserts 15 mapped nodes, 30 generated Context carriers, or 604 source subjects.',
'CurrentChallenge.setUpClass and _current_protected_session contain three explicit source-family literals; they are fixture setup/helper selections requiring a disclosed exact rebind.',
'The selected generic family constructor explicitly rejects any current Operational Lesson and fixes15nodes/10edges/30carriers. This producer cannot stand in for an integrated Lesson family; use the actual one-Lesson successor and its exact applicability selection.',
'Current legacy delivery closure is fixed to 30 in the runtime, and native dispositions to 604; a combined family must recut these exact guards to its signed actual inventory.',
'Historical context runtimes/freeze script contain their own bounded 30-carrier/25-join fixture assertions. Preserve historical scope or provide an explicitly selected successor rather than claiming a partial fixture is a complete family.',
'Seven candidate Session connections and 34 operation catalog entries in inherited methods name separate protocol contracts, not total Source graph size. Additional Lesson/contest lineage needs separate integrated runtime tests.'
],'claim_ceiling':'Static source audit and AST preservation only; no runtime qualification, complete-family inventory claim, Lesson effectiveness, or contest outcome.'}
out=HERE/'INHERITED-FIXTURE-ASSUMPTIONS-0001.json';out.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n');print(json.dumps({'result':'PASS-static-inventory','methods':len(methods),'changed_asts':len(changed),'runtime_assumptions':len(runtime),'outside_family_literals':len(ids),'output':out.relative_to(ROOT).as_posix()}))
