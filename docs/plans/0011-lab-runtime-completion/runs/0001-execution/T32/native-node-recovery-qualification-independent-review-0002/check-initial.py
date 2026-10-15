"""Bounded frozen public-byte/AST review and owned inert FD controls only."""
import ast, hashlib, json, os, runpy, sys
from pathlib import Path

ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
NEW=RUN/'T32/native-node-recovery-qualification-preparation-0002'
OLD=RUN/'T32/native-node-recovery-qualification-preparation-0001'
ADOPT=RUN/'T32/native-lifecycle-recovery-adoption-0003'
OUT=Path(__file__).parent
def need(value,message):
    if not value: raise ValueError(message)
def sha(raw): return hashlib.sha256(raw).hexdigest()
def load(path): return json.loads(path.read_bytes())
def path(row):
    p=Path(row['path']);return p if p.is_absolute() else ROOT/p
def fds():
    result={}
    for name in os.listdir('/proc/self/fd'):
        try:
            s=os.fstat(int(name));result[name]=(s.st_dev,s.st_ino,s.st_mode)
        except OSError: continue
    return result
baseline=fds()
need('ctypes' not in sys.modules,'unexpected ctypes before review')
capture_env=runpy.run_path(str(NEW/'capture.py'),run_name='_review_capture')
capture=capture_env['capture_path']
mf=load(NEW/'source-manifest.json');old=load(OLD/'source-manifest.json');adopt=load(ADOPT/'source-manifest.json')
need(len(mf['files'])==178 and len(old['files'])==153 and len(adopt['files'])==130,'declared counts differ')
def verify_all():
    for row in mf['files']:
        raw=capture(path(row),row['sha256'])
        need(len(raw)==row['size_bytes'],'selected size differs')
verify_all()
for parent in (old,adopt):
    for row in parent['files']:
        need(row in mf['files'],'literal predecessor declaration missing')
for row in load(NEW/'preimages.json')['all_predecessor_files']:
    capture(path(row),row['sha256'])
for row in load(NEW/'input-selection.json')['files']:
    capture(path(row),row['sha256'])
hh=load(NEW/'HANDOFF.json')
for key,value in hh.items():
    if key.endswith('_binding') and isinstance(value,dict) and set(value)=={'path','sha256'}:
        capture(path(value),value['sha256'])
newtree=ast.parse((NEW/'qualify.py').read_bytes());oldtree=ast.parse((OLD/'qualify.py').read_bytes())
nf={n.name:n for n in newtree.body if isinstance(n,ast.FunctionDef)}
of={n.name:n for n in oldtree.body if isinstance(n,ast.FunctionDef)}
def shape(n):return ast.dump(n,include_attributes=False)
def cases(fn):
    return next(n for n in ast.walk(fn) if isinstance(n,ast.With) and any(isinstance(i.context_expr,ast.Call) and isinstance(i.context_expr.func,ast.Attribute) and i.context_expr.func.attr=='signed_catalog' for i in n.items))
need(shape(cases(nf['run']))==shape(cases(of['run'])),'original four cases changed')
for name in ('need','sha','parse','relative','bootstrap_capture','module','diagnostic','main'):
    need(shape(nf[name])==shape(of[name]),'original helper changed: '+name)
for name in ('boundary.py','capture.py'):
    need((NEW/name).read_bytes()==(OLD/name).read_bytes(),'original bounded helper changed')
oldselection=load(RUN/'T07/ontology-installation-root-0001/execution-selection.json')
newselection=load(RUN/'T07/installed-proof-Root-comparison-0001/execution-selection.json')
need(oldselection.keys()==newselection.keys(),'selector shape changed')
need(oldselection['module_bindings']['control']!=newselection['module_bindings']['control'],'control not rebound')
oldselection['module_bindings']['control']=newselection['module_bindings']['control']
need(oldselection==newselection,'selector changed beyond reviewed control')
need(newselection['module_bindings']['control']['sha256']=='a212cf5352ce7994e6a041ccc69f8f5924f01b2be2e9067c066e082ee9a9a5dd','wrong control')
controls=runpy.run_path(str(NEW/'controls.py'),run_name='_review_pure_controls')
controls_result=controls['main']()
need(controls_result['result']=='PASS' and controls_result['check_count']==32,'bounded controls failed')
verify_all()
need('ctypes' not in sys.modules,'review imported ctypes')
need(fds()==baseline,'review leaked descriptors')
result={'result':'PASS-scoped-static-and-inert-review','manifest_rows_fresh_entry_exit':178,'literal_predecessor_rows':153,'literal_original_adoption_rows':130,'original_cases_AST_identical':4,'unchanged_helper_AST':8,'boundary_capture_bytes_identical':True,'selector_only_control_changed':True,'controls':controls_result,'FD_delta':0,'ctypes_imported':False,'actual_native_API_Source_guard_lease_or_installation_executed':False,'four_case_runtime_qualified':False}
with (OUT/'checks-result.json').open('x') as f: json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps(result,sort_keys=True))
