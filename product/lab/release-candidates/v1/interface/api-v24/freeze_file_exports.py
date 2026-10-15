"""Freeze unchanged predecessors, exact export adapter and complete case surface."""
import ast
import hashlib
import importlib.metadata
import json
import platform
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
RUN = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
def bind(path):
    return {'path':path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def put(path,value):
    with path.open('x') as stream:
        json.dump(value,stream,indent=2,sort_keys=True)
        stream.write('\n')
def methods(path):
    return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(path.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
    old = HERE.parent / 'api-v23'
    context = RUN / 'context-R03-file-export-api-0001.json'
    ctx = json.loads(context.read_bytes())
    assert ctx['strict_coverage'] == 'PASS' and not ctx['blockers']
    profile = json.loads((old / 'contract-profile.json').read_bytes())
    profile['implemented_operations'].append('files.materialize')
    profile['files'] = [bind(HERE / (ROOT / row['path']).relative_to(old) if (ROOT / row['path']).is_relative_to(old) else ROOT / row['path']) for row in profile['files']]
    for name in ['file_exports.py','export_kernel.py','export_fixture.py']:
        row = bind(HERE / name)
        if row['path'] not in {r['path'] for r in profile['files']}:
            profile['files'].append(row)
    profile['claim_ceiling'] = 'Thirteen implemented candidate handlers with separate nine-operation export, eight-operation metadata and unchanged twelve-operation v4 grants. Full134verification pending; currentAgent qualification and remaining21APIs/full46criteria/S02/R08 not established.'
    put(HERE / 'contract-profile.json',profile)
    rows = {}
    def add(row):
        assert rows.get(row['path'],row) == row
        rows[row['path']] = row
    for parent in [old / 'receipts/R03-0023.json', HERE.parent / 'file-materialization-v1/receipts/proof-0001.json']:
        proof = json.loads(parent.read_bytes())
        assert proof['result'] == 'PASS' and proof['task_complete'] is False
        for row in proof['files']:
            add(row)
        add(bind(parent))
    for row in ctx['source_bindings']:
        add(row)
    add(bind(context))
    for path in HERE.rglob('*'):
        if path.is_file() and '__pycache__' not in path.parts:
            add(bind(path))
    for name in ['test_preparation.py','test_preparation_corrected.py','run_session_checks.py','test_custody_sessions.py','test_custody_api.py','test_guarded_reads.py','test_metadata_scope.py']:
        assert methods(HERE / name) == methods(old / name), name
    assert methods(HERE / 'test_export_kernel.py') == methods(HERE.parent / 'file-materialization-v1/test_exports.py')
    assert len(methods(HERE / 'test_file_exports.py')) == 24
    for path in HERE.glob('*.py'):
        ast.parse(path.read_bytes())
    for name in ['api-call','api-reply']:
        schema = json.loads((HERE / 'schemas' / (name + '.schema.json')).read_bytes())
        signatures = [(b['properties']['operation']['const'],b['properties'].get('kind',{}).get('const')) for b in schema['oneOf']]
        assert len(signatures) == len(set(signatures)) == (34 if name == 'api-call' else 68)
    for row in rows.values():
        assert bind(ROOT / row['path']) == row, row['path']
    env = {'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')}
    assert env == {'python':'3.14.4','jsonschema':'4.23.0','cryptography':'46.0.5'}
    source = {'schema_version':'lab-public-file-export-source/v1-candidate','files':sorted(rows.values(),key=lambda r:r['path']),
              'environment':env,'frozen_before_owned_effects':True,'original146methodASTs_retained':True,
              'original86metadata_methods_retained':True,'original24kernel_methods_retained':True,'new_public_methods':24,
              'current_suite_cases':134,'original_Assignment_renewed':False,'authority_effect':'none','actual_owner_outcome':None,'task_complete':False}
    put(HERE / 'source-manifest.json',source)
    print(json.dumps({'result':'FROZEN','files':len(rows),'source_binding':bind(HERE/'source-manifest.json'),'profile_binding':bind(HERE/'contract-profile.json')}))
if __name__ == '__main__':
    main()
