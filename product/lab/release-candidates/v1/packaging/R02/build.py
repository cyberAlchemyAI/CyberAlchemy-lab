"""Prepare explicit source/dependency closure, then freeze before candidate effects."""
from common import *
import importlib.util
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5];RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction';PACKAGE=ROOT/'implementation/lab-runtime/candidates/repeatable-operation';OUT=HERE/'packages/0001'
sys.path.insert(0,str(PACKAGE))
from lab_runtime.profiles import select
from lab_runtime.sources import capture

def run():
 need(not (OUT/'selection.json').exists() and not (HERE/'source-manifest.json').exists(),'preserve frozen packages')
 names=set()
 for row in load(PACKAGE/'profiles/selections.json')['selections']:
  args={k:v for k,v in row.items() if k not in ('name','source_bytes','source_materials')};s=select(ROOT,**args);v=capture(s)
  names.update(v['materials']);names.update(b['path'] for b in v['controls'].values());names.update(b['path'] for b in v['executable_materials'])
  names.add(row['review_path']);names.add(s.profile['content_manifest']['path'])
  for paths in v['epoch_inventory'].values():names.update(paths)
 legacy=ROOT/'implementation/lab-runtime/v1';spec=importlib.util.spec_from_file_location('R02_build_legacy',legacy/'lab_runtime/__init__.py',submodule_search_locations=[str(legacy/'lab_runtime')]);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
 from R02_build_legacy.sources import capture as old_capture
 old=old_capture(ROOT,load(legacy/'profile.json'));names.update(old['materials'])
 for paths in old['epoch_inventory'].values():names.update(paths)
 for version in ('v1','v2'):
  base=ROOT/('implementation/lab-runtime/'+version);names.update(p.relative_to(ROOT).as_posix() for p in (base/'lab_runtime').glob('*.py'));names.add((base/'profile.json').relative_to(ROOT).as_posix());names.add((base/'requirements.txt').relative_to(ROOT).as_posix())
 for base in [PACKAGE/'schemas',PACKAGE/'design',PACKAGE/'profiles']:
  names.update(p.relative_to(ROOT).as_posix() for p in base.rglob('*.json'))
 names.add((PACKAGE/'tests/test_transition.py').relative_to(ROOT).as_posix())
 names.update(p.relative_to(ROOT).as_posix() for p in HERE.iterdir() if p.is_file() and p.name!='source-manifest.json')
 source_names=set(names)
 # Source snapshots are separately pinned local state. Public payload contains
 # executable/profile/schema/control material, never historical Session records.
 code_prefix='implementation/lab-runtime/'
 names={n for n in names if n.startswith(code_prefix) or n.startswith(str(HERE.relative_to(ROOT))+'/')}
 sourcefiles={n:read(ROOT/relative(n)) for n in sorted(names)}
 for n,b in sourcefiles.items():
  try:privacy(b,source=True)
  except ValueError as exc:raise ValueError(n+": "+str(exc)) from exc
 raw=encoded(snapshot(sourcefiles));(OUT/'payload.snapshot').write_bytes(raw)
 wheels=[]
 for p in sorted((OUT/'wheels').glob('*.whl')):
  import email
  with zipfile.ZipFile(p) as z:
   metadata=[n for n in z.namelist() if n.endswith('.dist-info/METADATA')];need(len(metadata)==1,'wheel metadata closure');v=email.message_from_bytes(z.read(metadata[0]));name=v['Name'].lower().replace('_','-');version=v['Version']
  need(name in VERSIONS and version==VERSIONS[name],'unselected wheel');wheels.append({'filename':p.name,'sha256':sha(read(p)),'distribution':name,'version':version})
 selection={'schema_version':'lab-R02-installation-package/v1-candidate','authority_effect':'none','actual_owner_outcome':None,'environment':environment(),'snapshot_sha256':sha(raw),'wheels':wheels,'versions':VERSIONS,'limitations':['Foundation runtime packaging; complete product API payload remains R03/S02.','No owner admission, activation, live stores, external publication or Session restoration.']};emit(OUT/'selection.json',selection)
 paths=['docs/plans/0009-lab-integrated-roadmap/work-pack/tasks/R02.md','docs/plans/0010-lab-one-shot-execution/work-pack/tasks/R02.md','docs/plans/0010-lab-one-shot-execution/PLAN.md',str((RUN/'authorization.json').relative_to(ROOT)),str((RUN/'R01-design-evidence.json').relative_to(ROOT)),'product/lab/release-candidates/v1/release-scope.json','product/lab/release-candidates/v1/PRODUCT-ACCEPTANCE.md','implementation/lab-continuity/candidates/v1/receipts/C13/0002.json','implementation/lab-runtime/v2/lab_runtime/store.py','implementation/lab-runtime/v2/requirements.txt','.gitignore',str((PACKAGE/'lab_runtime/transition.py').relative_to(ROOT)),str((PACKAGE/'lab_runtime/replay.py').relative_to(ROOT)),str((PACKAGE/'lab_runtime/promotion.py').relative_to(ROOT)),str((PACKAGE/'profiles/selections.json').relative_to(ROOT)),str((PACKAGE/'design/legacy-runtime-bindings.json').relative_to(ROOT))]
 ctx={'schema_version':'lab-task-execution-context/v1-candidate','task':'R02','mode':'deep','strict_coverage':'PASS','status':'context-prepared-execution-not-started','authority_effect':'none','actual_owner_outcome':None,'allowed_candidate_roots':[str(HERE.relative_to(ROOT))+'/'],'obligations':[{'id':'Q1','text':'Exact complete R01/C13, original and overlay task criteria; retained one final R08 checkpoint.'},{'id':'Q2','text':'Select exact dependency wheels, source closure and Linux environment; install only selected directories without overwrite.'},{'id':'Q3','text':'Rehearse reviewed D74 to D75 carry/exclude branch upgrade; retain original signatures, history and rollback dependencies.'},{'id':'Q4','text':'Export only exact scoped committed bytes; reject keys and Session memory including encoded bytes; cold recovery replays original signatures/cut.'},{'id':'Q5','text':'Actual process interruption/retry preserves incomplete stage and rollback inputs; no canonical effect or incomplete Product claim.'}],'design_decisions':[{'id':'R02-D1','selection':'Use exact selected wheel extraction with isolated -I -S Python launcher, preserving global environment and frozen runtime requirements.'},{'id':'R02-D2','selection':'Foundation packaging independent of eventual 34-operation product API closure; final release payload binds at S02.'},{'id':'R02-D3','selection':'Rollback selects retained old code/branch, never deletes successor or rebases history.'}],'selected_context':[{'path':n,'selectors':('/scope;/excluded_effects' if n.endswith('authorization.json') else 'Original ordered rules, acceptance, actual pinned runtime functions and source/evidence closure'),'obligations':['Q1','Q2','Q3','Q4','Q5']} for n in paths],'source_bindings':[{'path':n,'sha256':sha(read(ROOT/n))} for n in paths]};emit(RUN/'context-R02.json',ctx)
 allfiles=source_names|set(paths)|{str((RUN/'context-R02.json').relative_to(ROOT))}
 allfiles.update(p.relative_to(ROOT).as_posix() for p in OUT.rglob('*') if p.is_file())
 manifest={'schema_version':'lab-R02-source-closure/v1-candidate','task':'R02','authority_effect':'none','actual_owner_outcome':None,'files':[{'path':n,'sha256':sha(read(ROOT/n))} for n in sorted(allfiles)],'package_binding':{'path':str((OUT/'selection.json').relative_to(ROOT)),'sha256':sha(read(OUT/'selection.json'))},'environment':environment(),'context_binding':{'path':str((RUN/'context-R02.json').relative_to(ROOT)),'sha256':sha(read(RUN/'context-R02.json'))}}
 emit(HERE/'source-manifest.json',manifest);print(json.dumps({'result':'PASS','files':len(allfiles),'source_files':len(sourcefiles),'source_bytes':sum(map(len,sourcefiles.values())),'package_sha256':sha(read(OUT/'selection.json')),'manifest_sha256':sha(read(HERE/'source-manifest.json'))}))
if __name__=='__main__':run()
