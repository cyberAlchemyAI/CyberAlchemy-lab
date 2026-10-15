"""Finish the unfrozen draft after its incorrect schema shape assumption."""
import ast, hashlib, json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
API = BASE / 'api-v72'
OLD = BASE / 'api-v71'

def main():
    assert not (API / 'source-manifest.json').exists()
    assert not (API / 'contract-profile.json').exists()
    assert not (API / 'receipts').exists()
    author = RUN / 'author-API72-workflow-composition-0001.py'
    tree = ast.parse(author.read_bytes())
    function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'main')
    start = next(i for i, node in enumerate(function.body)
                 if isinstance(node, ast.Assign)
                 and isinstance(node.value, ast.BinOp)
                 and isinstance(node.value.right, ast.Constant)
                 and node.value.right.value == 'authentication.schema.json')
    namespace = {'__file__': str(author), '__name__': '_API72_recovery'}
    exec(compile(tree, str(author), 'exec'), namespace)
    namespace['kind'] = 'lab-local-challenge-review-policy/v1-candidate'
    namespace['binding'] = {'$ref': 'urn:cyberalchemy-lab:protocol:common:v1-candidate#/$defs/binding'}
    tail = ast.Module(body=function.body[start:], type_ignores=[])
    exec(compile(tail, str(author), 'exec'), namespace)
    tests = list(OLD.glob('test_*.py'))
    assert tests and all(path.read_bytes() == (API / path.name).read_bytes() for path in tests)
    report = {'schema_version': 'lab-unfrozen-draft-recovery/v1-candidate',
              'result': 'AUTHORED', 'successor': 'api-v72',
              'original_test_files_preserved': len(tests),
              'syntax_parsed': True, 'runtime_qualified': False,
              'authority_effect': 'none', 'actual_owner_outcome': None,
              'reason': 'Original authentication branch declares an exact const operation list.',
              'author_sha256': hashlib.sha256(author.read_bytes()).hexdigest()}
    with (RUN / 'API72-draft-recovery-0001.json').open('x') as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps(report))

if __name__ == '__main__':
    main()
