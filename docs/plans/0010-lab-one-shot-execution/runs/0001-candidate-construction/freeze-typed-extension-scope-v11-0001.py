"""Freeze exact coupled scope hypothesis after positive authoring checks."""
import ast,hashlib,json
from pathlib import Path
RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
PARENT=BASE/'typed-extension-preparation-v10'
TARGET=BASE/'typed-extension-preparation-v11'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes())}
def put(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def methods(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
 assert sha((PARENT/'source-manifest.json').read_bytes())=='586f890e93f4472012e55e2eac267d4df0a14445fdd65c6377fff0d3bcf6fb83'
 assert sha((PARENT/'receipts/proof-0001.json').read_bytes())=='d86ee45ecec19e5783c67abd151d4dc0b0143c43b47c286e09413335517ca01a'
 parent=json.loads((PARENT/'source-manifest.json').read_bytes());rows={r['path']:r for r in parent['files']}
 checks=json.loads((PARENT/'receipts/checks-0001.json').read_bytes());assert checks['result']=='PASS' and checks['actual_tests']==128
 authoring=json.loads((RUN/'typed-scope-authoring-positive-terminal-0001.json').read_bytes());assert authoring['actual_exit_code']==0 and authoring['actual_tests']==3
 for p in PARENT.glob('test_*.py'):assert methods(p)==methods(TARGET/p.name)
 assert len(methods(TARGET/'test_scope_preparation.py'))==16
 for name in ['adapter.py','source_selection.py','prospective.py','catalog_binding.py','predecessor_binding.py','kernel-inputs.json']:
  assert (PARENT/name).read_bytes()==(TARGET/name).read_bytes()
 extras=[PARENT/'source-manifest.json',PARENT/'receipts/proof-0001.json',PARENT/'receipts/checks-0001.json',RUN/'context-R03-typed-scope-preparation-v11.json',RUN/'typed-scope-authoring-positive-0001.log',RUN/'typed-scope-authoring-positive-terminal-0001.json',RUN/'authorization.json',Path(__file__).resolve()]
 for p in extras:
  r=bind(p);rows[r['path']]=r
 for p in TARGET.rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts and 'receipts' not in p.parts:
   r=bind(p);rows[r['path']]=r
 for r in rows.values():assert sha((ROOT/r['path']).read_bytes())==r['sha256']
 value={**parent,'files':[rows[k] for k in sorted(rows)],'expected_cases':144,'parent_source_binding':bind(PARENT/'source-manifest.json'),'context_binding':bind(RUN/'context-R03-typed-scope-preparation-v11.json'),'retained_predecessor_case_count':128,'predecessor_full_suite_result':'PASS','new_exact_scope_preparation_case_count':16,'pure_postimage_only':True,'scope_grant_supplied':False,'operational_preparation_ready':False,'public_handler_qualified':False,'authority_effect':'none','actual_owner_outcome':None}
 put(TARGET/'source-manifest.json',value)
 print(json.dumps({'result':'FROZEN','source_binding':bind(TARGET/'source-manifest.json'),'source_files':len(rows),'expected_cases':144}),flush=True)
if __name__=='__main__':main()
