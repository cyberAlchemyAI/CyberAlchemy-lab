from pathlib import Path
import subprocess,json
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
tests=subprocess.run(['python3','-B','-m','unittest','discover','-s','implementation/lab-workspaces/v2'],cwd=R,capture_output=True,text=True)
assert tests.returncode==0,tests.stdout+tests.stderr
assert 'Ran 42 tests' in tests.stderr
migration=subprocess.run(['python3','-B','tooling/verify_workspace_migration.py'],cwd=R,capture_output=True,text=True)
assert migration.returncode==0,migration.stdout+migration.stderr
result=json.loads(migration.stdout);assert result['status']=='pass' and result['runtime_copies']==0 and result['shared_runtime_targets']==1
receipt={'status':'PASS','workspace_checks':42,'migration':result,'unittest_output':tests.stderr}
(P/'WORKSPACE-VERIFICATION.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
