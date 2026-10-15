"""Select qualified fresh components while preserving Context8 and all guards."""
import ast
import hashlib
import json
import shutil
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
PARENT = BASE / 'current-context-delivery-v8'
SELECTED = BASE / 'current-context-delivery-v9'
OLD_READER = 'current-source-adapter-v3/reader.py#SelectedReader.open_signed'
NEW_READER = 'current-source-adapter-v4/reader.py#SelectedReader.open_signed'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def emit(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    parents = [PARENT / 'receipts/qualification-0001.json',
               BASE / 'current-source-adapter-v4/qualification-0002.json',
               BASE / 'current-mapped-context-v4/qualification-0001.json']
    for path in parents:
        document = json.loads(path.read_bytes())
        assert document['result'] == 'PASS'
        for row in document['files']:
            target = ROOT / row['path']
            assert hashlib.sha256(target.read_bytes()).hexdigest() == row['sha256'], row['path']
    assert not SELECTED.exists()
    SELECTED.mkdir()
    replacements = {
        'current-context-delivery-v8': 'current-context-delivery-v9',
        '_delivery_v8': '_delivery_v9', '_v25_v8': '_v25_v9',
        'current-mapped-context-v3': 'current-mapped-context-v4',
        '_mapper_v3_': '_mapper_v4_', OLD_READER: NEW_READER,
        '665d5ac2287b95dfc5857780d57ee60b9f2e4aff351019eb669d6b5dad03b54e':
            bind(BASE / 'current-mapped-context-v4/source-manifest.json')['sha256'],
        'de880a25a53a4c1410c983489d81ef4a9a551316f36f79d5abde73112015a07b':
            bind(BASE / 'current-mapped-context-v4/packages/0001/manifest.json')['sha256'],
        'b5130870913b980398dab64a1c33067231a042fe9d06f6d35f5afedaaffa96f2':
            bind(BASE / 'current-participation-v5/source-manifest.json')['sha256'],
        'b4381aa92a3519f1536bb4a64a74b4af0d0d3556bfc35a9254b8489bab301092':
            bind(BASE / 'current-participation-v5/packages/0001/manifest.json')['sha256'],
    }
    for path in PARENT.iterdir():
        if path.is_file() and path.name != 'freeze.py' and (path.suffix == '.py' or path.name in ['lifetime-policy.json', 'implementation-binding.json']):
            text = path.read_text()
            for old, new in replacements.items():
                text = text.replace(old, new)
            if path.suffix == '.py':
                ast.parse(text)
            (SELECTED / path.name).write_text(text)
    shutil.copytree(PARENT / 'protocols', SELECTED / 'protocols')
    for path in (SELECTED / 'protocols').glob('*.json'):
        path.write_text(path.read_text().replace('protocol:R03-current-episode-0003-policy/v1',
                                               'protocol:R03-current-episode-0004-policy/v1'))
    binding_path = SELECTED / 'implementation-binding.json'
    binding = json.loads(binding_path.read_bytes())
    binding['code_binding'] = {'ref': bind(SELECTED / 'build.py')['path'], 'sha256': bind(SELECTED / 'build.py')['sha256']}
    binding_path.write_text(json.dumps(binding, indent=2, sort_keys=True) + '\n')
    text = (PARENT / 'freeze.py').read_text()
    replacements = {
        "PARENT = HERE.parent / 'current-context-delivery-v6'": "PARENT = HERE.parent / 'current-context-delivery-v8'",
        'current-mapped-context-v3': 'current-mapped-context-v4',
        'current-source-adapter-v3/qualification-0001.json': 'current-source-adapter-v4/qualification-0002.json',
        'context-delivery-0008.json': 'context-delivery-0009.json',
        'construct-R03-current-context-0008.py': 'construct-R03-current-context-0009.py',
        'current-context-binding-revision-0008.json': 'current-context-binding-revision-0009.json',
        'd3ecda8d3c796e402e87efa25036ca4867534966ad4e50acb83741dc4fa9b010': bind(PARENT / 'source-manifest.json')['sha256'],
        "'current-source-adapter-v2/reader.py#SelectedReader.open_signed', 'current-source-adapter-v3/reader.py#SelectedReader.open_signed'":
            repr(OLD_READER) + ', ' + repr(NEW_READER),
        'qualified Reader3': 'qualified Reader4',
    }
    for old, new in replacements.items():
        assert old in text, old
        text = text.replace(old, new)
    ast.parse(text)
    (SELECTED / 'freeze.py').write_text(text)
    emit(RUN / 'current-context-binding-revision-0009.json', {
        'schema_version': 'lab-context-binding-revision/v1-candidate',
        'parent_bindings': [bind(path) for path in parents],
        'test_name': 'test_42_current_API_profile_and_source_implementation_are_exact',
        'only_test_revision': {'old_reader_entrypoint': OLD_READER, 'new_reader_entrypoint': NEW_READER},
        'unchanged_test_methods': 49, 'total_test_methods': 50,
        'reason': 'Select fresh signed Source5, qualified Reader4 and Mapper4 with exact original code/body/schema guards.',
        'clock_replaced': False, 'permission_cached': False, 'maximum_Session_seconds': 900,
        'context_qualified': False, 'authority_effect': 'none', 'actual_owner_outcome': None})
    (SELECTED / 'DESIGN.md').write_text(
        '# Context9 fresh source integration\n\n'
        'Select signed Source5, Reader4 and Mapper4. Retain the entire Context8 qualification, '
        'original real clock, source/schema/native guards, current host permission checks and '
        '900 second Session ceiling. Source5 has its own fixed period and identities; no preceding period changes.\n\n'
        'Preserve all 50 test methods, changing only the exact declared reader path in test42. '
        'Retain the observed historical import evidence as selection input, then separately qualify '
        'actual successor code execution, full50 checks and independent native/carrier replay. '
        'Component success does not qualify the API or create an owner outcome.\n')
    print(json.dumps({'result': 'CONSTRUCTED', 'selected': str(SELECTED.relative_to(ROOT)),
                      'unchanged_methods': 49, 'reader_path_assertion_rebound': 1}), flush=True)


if __name__ == '__main__':
    main()
