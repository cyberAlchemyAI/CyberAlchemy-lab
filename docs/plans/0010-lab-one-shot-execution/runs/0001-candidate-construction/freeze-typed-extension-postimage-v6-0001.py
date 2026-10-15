"""Freeze a candidate successor; preserve all64 predecessor test method ASTs."""
import ast,hashlib,json
from pathlib import Path
RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
PARENT=BASE/'typed-extension-preparation-v5'
TARGET=BASE/'typed-extension-preparation-v6'
ENGINE=BASE/'custody-correction-v4'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes())}
def put(p,v):
 with p.open('x') as f:json.dump(v,f,sort_keys=True,indent=2);f.write('\n')
def methods(p):
 return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes()))
         if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
 raw=(PARENT/'source-manifest.json').read_bytes()
 assert sha(raw)=='e4d4b80dc6b7277f3d1e04abeb6cd8c5065b2b138e7940550a0d6872054bfdfc'
 parent=json.loads(raw); rows={r['path']:r for r in parent['files']}
 for r in rows.values():assert sha((ROOT/r['path']).read_bytes())==r['sha256']
 for p in PARENT.glob('test_*.py'):assert methods(p)==methods(TARGET/p.name)
 assert (PARENT/'adapter.py').read_bytes()==(TARGET/'adapter.py').read_bytes()
 engine=json.loads((ENGINE/'engine-manifest.json').read_bytes())
 for r in engine['files']+[engine['parent_binding'],engine['profile_binding'],engine['mapping_binding'],engine['correction_profile_binding']]:rows[r['path']]=r
 ancestor=json.loads((ROOT/engine['parent_binding']['path']).read_bytes())
 for r in ancestor['files']:rows[r['path']]=r
 kernel_inputs=json.loads((TARGET/'kernel-inputs.json').read_bytes())
 for r in kernel_inputs['files']:rows[r['path']]=r
 for p in [ENGINE/'loader.py',ENGINE/'pins.json',ENGINE/'engine-manifest.json',
           PARENT/'source-manifest.json',PARENT/'receipts/checks-0001.json',RUN/'authorization.json',
           RUN/'typed-extension-postimage-authoring-0001.log',RUN/'typed-extension-postimage-authoring-0002.log',
           RUN/'typed-extension-postimage-authoring-0003.log',Path(__file__).resolve()]:
  r=bind(p);rows[r['path']]=r
 context=RUN/'context-R03-typed-extension-postimage-v6.json'
 put(context,{'schema_version':'lab-bounded-context/v1-candidate','task':'R03 exact typed-extension registered slots and coupled postimage',
  'strict_coverage':'PASS','blockers':[],'source_bindings':[bind(RUN/'authorization.json'),bind(PARENT/'source-manifest.json'),bind(ENGINE/'engine-manifest.json')],
  'write_scope':TARGET.relative_to(ROOT).as_posix(),'decisions':[{'selection':'original current custody engine and its complete original verifier','mode':'existing-authorized-implementation'}],
  'validation_surface':'All29 original C14 cases,18 wire cases,17 catalog cases and14 postimage cases; all64 predecessor methods unchanged.',
  'constraints':['No registered public operation, host/source freshness or Actor authority is added.','No live store, key, canonical descriptor or Relation Kind is changed.',
                 'Registration body stays in original seven-field slot; endpoint roles and schema metadata stay in separate closed contract.',
                 'Hypothetical copied D75 projection and explicit reviewed endpoint mapping only; full original schema/core preparation, zero actual transactions.',
                 'Frozen predecessors, their failed reports and all original callbacks remain immutable.'],
  'remaining_obligations':['Actual host, Actor, source cut and permission integration.','Durable journal and original public cases.','Declared prospective/internal/specialized resolvers.','Complete S02 and genuine R08 owner checkpoint.'],
  'actual_owner_outcome':None,'authority_effect':'none','task_complete':False})
 r=bind(context);rows[r['path']]=r
 for p in TARGET.rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts and 'receipts' not in p.parts:
   r=bind(p);rows[r['path']]=r
 for r in rows.values():assert sha((ROOT/r['path']).read_bytes())==r['sha256']
 manifest={**parent,'files':[rows[k] for k in sorted(rows)],'expected_cases':78,
  'parent_source_binding':bind(PARENT/'source-manifest.json'),'context_binding':bind(context),
  'original_engine_manifest_binding':bind(ENGINE/'engine-manifest.json'),
  'retained_predecessor_case_count':64,'new_exact_postimage_case_count':14,
  'pure_postimage_only':True,'public_handler_qualified':False,'actual_owner_outcome':None,'authority_effect':'none'}
 put(TARGET/'source-manifest.json',manifest)
 print(json.dumps({'result':'FROZEN','source_binding':bind(TARGET/'source-manifest.json'),'source_files':len(rows),'expected_cases':78}),flush=True)
if __name__=='__main__':main()
