"""Freeze explicit public predecessor adapter with inherited methods intact."""
import ast,hashlib,json
from pathlib import Path
RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
PARENT=BASE/'typed-extension-preparation-v8'
TARGET=BASE/'typed-extension-preparation-v9'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes())}
def put(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def methods(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
 assert sha((PARENT/'source-manifest.json').read_bytes())=='21183a4e9e81049ba53f80242ad1f077465dfee0aac5326a34a98b382a595e73'
 assert sha((PARENT/'receipts/proof-0001.json').read_bytes())=='09fd864a72254e3f27805b2ea2cf7ecbd2a0b854917f26af443d9a40f56f513d'
 parent=json.loads((PARENT/'source-manifest.json').read_bytes());rows={r['path']:r for r in parent['files']}
 for p in PARENT.glob('test_*.py'):assert methods(p)==methods(TARGET/p.name)
 assert len(methods(TARGET/'test_predecessor_binding.py'))==12
 for name in ['adapter.py','source_selection.py','prospective.py','catalog_binding.py','kernel-inputs.json']:
  assert (PARENT/name).read_bytes()==(TARGET/name).read_bytes()
 extras=[PARENT/'source-manifest.json',PARENT/'receipts/proof-0001.json',PARENT/'receipts/checks-0001.json',BASE/'api-v45/catalog-representations.json',RUN/'context-R03-public-predecessor-v9.json',RUN/'typed-actual-source-comparison-0007.json',RUN/'typed-actual-source-comparison-terminal-0007.json',RUN/'authorization.json',Path(__file__).resolve()]
 for p in extras:
  r=bind(p);rows[r['path']]=r
 for p in TARGET.rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts and 'receipts' not in p.parts:
   r=bind(p);rows[r['path']]=r
 for r in rows.values():assert sha((ROOT/r['path']).read_bytes())==r['sha256']
 value={**parent,'files':[rows[k] for k in sorted(rows)],'expected_cases':126,'parent_source_binding':bind(PARENT/'source-manifest.json'),'context_binding':bind(RUN/'context-R03-public-predecessor-v9.json'),'retained_predecessor_case_count':114,'new_public_predecessor_case_count':12,'pure_postimage_only':True,'scope_grant_supplied':False,'public_handler_qualified':False,'authority_effect':'none','actual_owner_outcome':None}
 put(TARGET/'source-manifest.json',value)
 print(json.dumps({'result':'FROZEN','source_binding':bind(TARGET/'source-manifest.json'),'source_files':len(rows),'expected_cases':126}),flush=True)
if __name__=='__main__':main()
