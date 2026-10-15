"""Freeze exact kernel, source and context before owned candidate effects."""
import ast,hashlib,importlib.metadata,json,platform
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
    out=HERE/'source-manifest.json';assert not out.exists();parent=HERE.parent/'api-v18/source-manifest.json'
    assert bind(parent)['sha256']=='07a14881e21fe3c0db88ff55e0b3b982de05959cbd68a931efa89a2c3368e445'
    m=json.loads(parent.read_bytes());rows={r['path']:r for r in m['files']};rows[bind(parent)['path']]=bind(parent)
    predecessor=HERE.parent/'review-package-v1'; prior=json.loads((predecessor/'source-manifest.json').read_bytes())
    for row in prior['files']:rows[row['path']]=row
    for p in [predecessor/'source-manifest.json',predecessor/'receipts/checks.json',predecessor/'receipts/examples.json',predecessor/'checks-0001.log',RUN/'review-package-terminal-0001.json',RUN/'context-R03-review-package-0003.json']:rows[bind(p)['path']]=bind(p)
    def methods(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
    assert methods(HERE/'checks.py')==methods(predecessor/'checks.py')
    for p in [RUN/'context-R03-review-package-0001.json',RUN/'context-R03-review-package-0002.json',*HERE.rglob('*')]:
        if p.is_file() and '__pycache__' not in p.parts:
            if p.suffix=='.py':ast.parse(p.read_bytes())
            b=bind(p);assert rows.get(b['path'],b)==b;rows[b['path']]=b
    for row in rows.values():assert bind(ROOT/row['path'])==row
    env={'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')};assert env==m['environment']
    value={'schema_version':'lab-exact-review-kernel-source/v1-candidate','files':sorted(rows.values(),key=lambda r:r['path']),'environment':env,'parent_API_source_binding':bind(parent),'parent_API_qualification_pending':True,'scope':'candidate kernel authoring/owned verification only; public adapter and full API contract qualification separate','expected_tests':20,'frozen_before_owned_effects':True,'actual_owner_outcome':None,'authority_effect':'none','task_complete':False}
    out.open('x').write(json.dumps(value,indent=2,sort_keys=True)+'\n');print(json.dumps({'result':'FROZEN','files':len(rows),'source_binding':bind(out),'expected_tests':20,'public_review_adapter_implemented':False}),flush=True)
if __name__=='__main__':main()
