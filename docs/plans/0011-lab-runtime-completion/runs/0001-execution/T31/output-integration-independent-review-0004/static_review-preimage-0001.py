"""Independent static public-byte review only; imports no candidate/runtime modules."""
import ast, hashlib, json, os
from pathlib import Path
R=Path('/home/vlad_/projects/CyberAlchemy-lab'); B=R/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T31'; P=B/'output-integration-preparation-0004'; OUT=B/'output-integration-independent-review-0004'; POST=P/'postimages/product/lab/release-candidates/v1/interface/api-integration-v17'
checks=[]
def need(v,label):
 if not v: raise AssertionError(label)
 checks.append(label)
def raw(p): return Path(p).read_bytes()
def sha(p): return hashlib.sha256(raw(p)).hexdigest()
def obj(p):return json.loads(raw(p))
def binding(b):
 p=R/b['path']; need(sha(p)==b['sha256'],'binding '+b['path']);
 if 'size_bytes' in b:need(p.stat().st_size==b['size_bytes'],'size '+b['path'])
def rows_current(rows):
 for b in rows:binding(b)
def methods(p,c):
 n=next(n for n in ast.parse(raw(p)).body if isinstance(n,ast.ClassDef) and n.name==c)
 return {n.name:ast.dump(n,include_attributes=False) for n in n.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
def qualnames(p):
 names=set()
 def walk(nodes,prefix=''):
  for n in nodes:
   if isinstance(n,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)):
    name=prefix+n.name;names.add(name)
    if isinstance(n,ast.ClassDef):walk(n.body,name+'.')
 walk(ast.parse(raw(p)).body);return names
fd_before=len(os.listdir('/proc/self/fd'))
for name,pin in [('HANDOFF.json','a9e78b1915cf6e25657ab069d9835644b58ea17e382f764b78f24456ceffe911'),('source-manifest.json','4bdd219b89d078f56305b872784c450383c6d5f0b626b630186ecd17a67420fc'),('ADOPTION.json','028ddf2f53f2c7e9c8c904abb2cde347fc84dbf48d2b091e5422b6608c66df6b'),('bootstrap.py','4313a946ce16b9daedc74c22af6b320db4fefab3d6fcfaa019157d628a70cb8b')]:need(sha(P/name)==pin,'independent selected '+name)
mf=obj(P/'source-manifest.json');need(len(mf['files'])==56,'56 own declarations'); rows_current(mf['files'])
parent=obj(P/'parent-preimage-conservation.json');binding(parent['parent_manifest']);binding(parent['parent_handoff']);need(parent['declarations']==obj(R/parent['parent_manifest']['path'])['files'],'all52 parent declarations equal');need(len(parent['declarations'])==52,'52 parent declarations');rows_current(parent['declarations'])
cons=obj(P/'original-input-conservation.json');binding(cons['parent_input_selection']);need(cons['declarations']==obj(R/cons['parent_input_selection']['path'])['files'],'original293 exact declaration conservation');need(len(cons['declarations'])==293,'293 original declarations retained without claiming all current')
for n in ['source-observations.json','external-inputs.json']:rows_current(obj(P/n)['files'])
a=obj(P/'ADOPTION.json');need(len(a['rows'])==26,'26 staged targets');targets={x['target']:x for x in a['rows']};need(sum(bool(x['target_expected_absent']) for x in a['rows'])==24,'24 absent plus two existing targets')
for row in a['rows']:
 binding(row['postimage']);need((R/row['postimage']['path']).stat().st_mode&511==row['postimage_mode'],'postimage mode '+row['target'])
 if row['target_expected_absent']:need(not (R/row['target']).exists(),'shared target still absent '+row['target'])
 else:
  binding(row['preimage']);need(sha(R/row['target'])==row['preimage']['sha256'],'shared preimage unchanged '+row['target']);need((R/row['target']).stat().st_mode&511==row['preimage']['mode'],'shared preimage mode '+row['target'])
for cls,old,new,expected in [
 ('Service',P/'preimages/product/lab/release-candidates/v1/interface/api-integration-v17/service.py',POST/'service.py',{'__init__','select_workflow_transition'}),
 ('WorkflowTransition',P/'preimages/product/lab/release-candidates/v1/interface/api-integration-v17/workflow_transition.py',POST/'workflow_transition.py',{'__init__','original','preflight','apply'}),
 ('Journal',R/'product/lab/release-candidates/v1/interface/workflow-transition-v1/journal.py',POST/'workflow_output_journal.py',{'initialize','__init__','replay','apply','recover'})]:
 x,y=methods(old,cls),methods(new,cls);need(set(x)==set(y),cls+' preserves complete method membership');need({k for k in x if x[k]!=y[k]}==expected,cls+' exact declared method delta')
inv=obj(B/'output-transitions-0001/workflow-output-inventory.json');proposal=obj(P/'ROOT-selection-proposal.json');routes=proposal['routes'];need(len(inv['workflows'])==10 and len(routes)==28,'10 workflows and28 routes')
originals={t['transition_ref']:(w,t) for w in inv['workflows'] for t in w['transitions']};need(set(originals)==set(routes),'complete28 transition identity conservation')
for ref,route in routes.items():
 w,t=originals[ref]
 for new,old in [('original_required_output_carriers','original_required_output_carriers'),('original_input_carriers','original_input_carriers'),('original_from_state','from_state'),('original_to_state','to_state'),('original_authority_precondition_satisfaction_relation_obligations','original_authority_precondition_satisfaction_relation_obligations')]:need(route[new]==t[old],ref+' '+new)
 need(route['original_definition_binding']==w['original_definition_binding'],ref+' exact definition');binding(w['original_definition_binding'])
 for method in route['implementation_methods']+[{ 'binding':route['producer_binding'],'entrypoint':route['producer_entrypoint']},{'binding':route['resolver_binding'],'entrypoint':route['resolver_entrypoint']}]:
  b=method['binding']; path=R/b['path']
  if b['path'] in targets:path=R/targets[b['path']]['postimage']['path']
  need(sha(path)==b['sha256'],ref+' exact method bytes '+method['entrypoint']);need(method['entrypoint'] in qualnames(path),ref+' actual method '+method['entrypoint'])
cat=obj(B/'output-transitions-0001/carrier-catalog.json');need(len(cat['rows'])==33,'33 original catalog rows');required={v for _,t in originals.values() for v in t['original_required_output_carriers']};need(required=={r['artifact_type_ref'] for r in cat['rows']},'all33 required carrier identities exactly retained')
for row in cat['rows']:
 binding({'path':row['artifact_path'],'sha256':row['artifact_sha256']});binding({'path':row['schema_path'],'sha256':row['schema_sha256']})
svc_inv=obj(P/'service-code-inventory.json');need(len(svc_inv['original_names'])==71 and len(svc_inv['T31_additional_names'])==24 and len(svc_inv['separate_required_T15_names'])==8,'Service original71 plus24T31 plus8T15');need(len(svc_inv['final_names'])==103 and len(set(svc_inv['final_names']))==103,'103 unique Service names')
s=ast.parse(raw(POST/'service.py'));init=next(n for n in next(n for n in s.body if isinstance(n,ast.ClassDef) and n.name=='Service').body if isinstance(n,ast.FunctionDef) and n.name=='__init__');assign=next(n for n in ast.walk(init) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='code_files' for t in n.targets));need(list(ast.literal_eval(assign.value))==svc_inv['final_names'],'actual Service code_files equals declared103 union')
need(raw(P/'private-output-plan.schema.json')==raw(POST/'workflow-output-plan.schema.json'),'private plan schema exact postimage')
# Syntax only: no validator construction or candidate import.
for q in P.rglob('*.py'):ast.parse(raw(q),filename=str(q))
for q in P.rglob('*.json'):obj(q)
rows_current(mf['files']);need(len(os.listdir('/proc/self/fd'))==fd_before,'FD delta zero')
result={'schema_version':'lab-T31-independent-static-review/v1','result':'PASS-static-conservation-only','checks':checks,'check_count':len(checks),'own_manifest_rows':56,'parent_rows':52,'historical_original_declarations':293,'historical_original_rows_claimed_current':False,'workflows':10,'transitions':28,'catalog_carriers':33,'postimages':26,'service_names':103,'FD_delta':0,'candidate_imported':False,'authored_full_control_suite_run':False,'actual_API_Source_native_lease_or_producer_called':False,'authority_effect':'none'}
(OUT/'static-result-0001.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='checks'},sort_keys=True))
