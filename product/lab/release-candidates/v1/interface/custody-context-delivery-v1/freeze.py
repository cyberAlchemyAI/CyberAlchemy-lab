"""Bind all producer/mapper/source/API/schema/protocol bytes before host effects."""
import ast,hashlib,importlib.metadata,json,platform
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
MAPPED=HERE.parent/'custody-mapped-context-v2'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def methods(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
    assert not (HERE/'source-manifest.json').exists() and not (HERE/'packages').exists() and not (HERE/'receipts').exists();rows={}
    def add(row):
        assert rows.get(row['path'],row)==row,row['path'];p=ROOT/row['path'];assert p.is_file() and not p.is_symlink() and bind(p)==row,row['path'];rows[row['path']]=row
    for n in ['custody-mapped-context-v2','context-delivery-v3','api-v16']:
        path=HERE.parent/n/'source-manifest.json';m=json.loads(path.read_bytes());add(bind(path))
        for row in m['files']:add(row)
    for p in (MAPPED/'packages/0001').rglob('*'):
        if p.is_file():add(bind(p))
    context=RUN/'context-R03-custody-context-delivery-0001.json';c=json.loads(context.read_bytes());assert c['strict_coverage']=='PASS'
    for row in c['source_bindings']:add({'path':row['path'],'sha256':row['sha256']})
    for p in [context,RUN/'CONTEXT-R03-custody-context-delivery-0001.md']:add(bind(p))
    assert methods(HERE.parent/'context-delivery-v3/run_checks.py')==methods(HERE/'test_original_delivery.py') and len(methods(HERE/'test_original_delivery.py'))==38
    assert len(methods(HERE/'test_raw_delivery.py'))==8
    for p in HERE.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts:
            if p.suffix=='.py':ast.parse(p.read_bytes(),filename=str(p))
            add(bind(p))
    environment={'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')}
    assert environment=={'python':'3.14.4','jsonschema':'4.23.0','cryptography':'46.0.5'}
    m={'schema_version':'lab-original-source-context-delivery-source/v1-candidate','files':sorted(rows.values(),key=lambda r:r['path']),
        'qualified_mapper_source_binding':bind(MAPPED/'source-manifest.json'),'qualified_mapper_package_binding':bind(MAPPED/'packages/0001/manifest.json'),
        'old_delivery_source_binding':bind(HERE.parent/'context-delivery-v3/source-manifest.json'),'current_API_source_binding':bind(HERE.parent/'api-v16/source-manifest.json'),
        'current_API_profile_binding':bind(HERE.parent/'api-v16/contract-profile.json'),'context_binding':bind(context),'environment':environment,
        'original38assertion_ASTs_preserved':True,'new_original_source_methods':8,'frozen_before_owned_hostpermission_key_or_view_effects':True,
        'authority_effect':'none','actual_owner_outcome':None,'claim_ceiling':'Actual owned controlled Context generation during independent current host permission, exact source/native/query interval. No activeAgent/Session/publicAPI/canonicalowner outcome; all original fullplan criteria remain.'}
    (HERE/'source-manifest.json').open('x').write(json.dumps(m,indent=2,sort_keys=True)+'\n');print(json.dumps({'result':'FROZEN','files':len(rows),'methods':46,'source_binding':bind(HERE/'source-manifest.json')}))
if __name__=='__main__':main()
