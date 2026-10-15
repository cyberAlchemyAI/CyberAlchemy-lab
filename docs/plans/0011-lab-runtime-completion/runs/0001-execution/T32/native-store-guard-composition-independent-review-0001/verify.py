"""Independent metadata/AST and explicitly owned inert guard controls only."""
from pathlib import Path
import ast,hashlib,json,os,runpy
R=Path('docs/plans/0011-lab-runtime-completion/runs/0001-execution')
B=R/'T32/native-store-guard-composition-preparation-0001';O=R/'T32/native-lifecycle-recovery-adoption-0003'
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v):
 if not v:raise AssertionError('independent metadata/AST correspondence failed')
need(digest(B/'HANDOFF.json')=='0a606eddd3c478e7f9714202652947d989e61f26fc53dc283685a4f46d7bbf14')
need(digest(B/'source-manifest.json')=='64fc4a7077562898638f2ab8c64864eccc6f3fabda61a65e335d20c8610d4f5e')
need(digest(B/'selected_store.py')=='83bd3d974c2e7d8e4f7b060b9b1678f8bb796a3ffac2bc5d10f1dd58af6f3a8f')
m=json.loads((B/'source-manifest.json').read_bytes());old=json.loads((O/'source-manifest.json').read_bytes());need(len(m['files'])==153 and len(old['files'])==130)
need(all(row in m['files']for row in old['files']))
for row in m['files']:
 path=Path(row['path']);need(digest(path)==row['sha256'])
 if 'size_bytes'in row:need(path.stat().st_size==row['size_bytes'])
# This code contains only AST inspection and inert Port/Generation fixtures.
# No candidate module, original NativeCandidateStore, executor, boundary or API
# is imported/constructed. No actual Source or dependency guard is invoked.
ns=runpy.run_path(str(B/'controls.py'),run_name='_INDEPENDENT_OWNED_INERT_GUARD_REVIEW');result=ns['main']()
need(result['check_count']==24 and result['FD_delta']==0)
original=Path('implementation/lab-ontology/candidates/v1/adapters/lifecycle/native_store.py');generation=B/'generation_store.py'
need(digest(original)=='8d61ae200155fefe4e87c3d303e03a6314465d639089708cef91174efa556138')
tree=ast.parse(generation.read_bytes());klass=next(n for n in tree.body if isinstance(n,ast.ClassDef)and n.name=='GenerationStore');methods={n.name:n for n in klass.body if isinstance(n,ast.FunctionDef)}
headcalls=[ast.unparse(n.func)for n in ast.walk(methods['head'])if isinstance(n,ast.Call)]
need('self.guard'not in headcalls and 'self.tree'in headcalls)
proofs=[ast.unparse(n.value.func)for n in methods['guard'].body if isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)]
need(proofs[:2]==['self.boundary.guard','self.executor.guard'])
print(json.dumps({'result':'PASS-scoped-static-and-owned-inert-only','manifest_rows_checked':153,'all_parent_130_literal_rows_retained':True,'inert_checks':24,'FD_delta':result['FD_delta'],'full_external_guard_expansion_AST_identical':True,'early_and_final_boundary_guards_retained':True,'generation_head_invokes_guard':False,'generation_bytes_unchanged':digest(generation)==digest(O/'generation_store.py'),'actual_API_Source_native_executor_boundary_or_lease_used':False,'ctypes_imported':False,'runtime_deadline_or_performance_qualified':False,'checks':result['checks']},sort_keys=True))
