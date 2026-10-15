"""Prepare exact fresh component selection; retain original API methods and guards."""
import ast
import hashlib
import json
import shutil
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-v75'
API = BASE / 'api-v76'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def methods(text):
    return {n.name: ast.dump(n, include_attributes=False) for n in ast.walk(ast.parse(text))
            if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}


def main():
    assert not API.exists() and not (BASE / 'lesson-host-composition-v26').exists()
    assert bind(OLD / 'source-manifest.json')['sha256'] == '35c97975fe0be4541d6a87f0881b60c11991746b8b3e661ccbbd81c34aaa4b20'
    ignore = shutil.ignore_patterns('receipts', '__pycache__', 'source-manifest.json', 'contract-profile.json')
    shutil.copytree(OLD, API, ignore=ignore)
    shutil.copytree(BASE / 'lesson-host-composition-v25', BASE / 'lesson-host-composition-v26', ignore=ignore)
    host = BASE / 'lesson-host-composition-v26/host.py'
    text = host.read_text()
    assert text.count('api-v75/service.py') == 1
    host.write_text(text.replace('api-v75/service.py', 'api-v76/service.py'))
    replacements = {
        'current-context-delivery-v8': 'current-context-delivery-v9',
        '_custody_context_v8': '_custody_context_v9',
        'current-participation-v4': 'current-participation-v5',
        'current-source-adapter-v3': 'current-source-adapter-v4',
        'R03-current-episode-0003': 'R03-current-episode-0004',
        'de6957eb09db5bd052ae494f808f6d02aaeba0641316d62753c13a7d9a0d0bf6':
            bind(BASE / 'current-context-delivery-v9/source-manifest.json')['sha256'],
        'lesson-host-composition-v25': 'lesson-host-composition-v26',
    }
    changed, retained = [], []
    for path in API.rglob('*.py'):
        original = (OLD / path.relative_to(API)).read_text()
        text = original
        for old, new in replacements.items():
            text = text.replace(old, new)
        ast.parse(text)
        path.write_text(text)
        before, after = methods(original), methods(text)
        assert before.keys() == after.keys()
        for name in before:
            reference = path.relative_to(API).as_posix() + ':' + name
            if before[name] == after[name]:
                retained.append(reference)
            else:
                changed.append(reference)
    assert len(retained) + len(changed) == 323
    value = {'schema_version': 'lab-current-API-binding-revision/v1-candidate',
             'parent_source_binding': bind(OLD / 'source-manifest.json'),
             'fresh_Context_source_binding': bind(BASE / 'current-context-delivery-v9/source-manifest.json'),
             'replacements': replacements, 'total_inherited_methods': 323,
             'unchanged_method_count': len(retained), 'unchanged_methods': retained,
             'binding_only_revised_methods': changed,
             'clock_replaced': False, 'permission_cached': False, 'source_callbacks_replaced': False,
             'all_original_public_contracts_retained': 34, 'authored_handlers': 21,
             'missing_operations': 13, 'whole_API_qualified': False,
             'current_Agent_qualified': False, 'authority_effect': 'none',
             'actual_owner_outcome': None, 'task_complete': False, 'goal_complete': False}
    path = RUN / 'API76-fresh-binding-revision-0001.json'
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': 'AUTHORED', 'revision': bind(path), 'unchanged_methods': len(retained),
                      'binding_revised_methods': len(changed), 'runtime_qualified': False}), flush=True)


if __name__ == '__main__':
    main()
