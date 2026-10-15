"""Construct a successor without modifying any qualified parent bytes."""
import ast
import hashlib
import json
import shutil
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
INTERFACE = ROOT / 'product/lab/release-candidates/v1/interface'
PARENT = INTERFACE / 'current-context-delivery-v6'
SELECTED = INTERFACE / 'current-context-delivery-v7'
OLD_READER = 'current-source-adapter-v2/reader.py#SelectedReader.open_signed'
NEW_READER = 'current-source-adapter-v3/reader.py#SelectedReader.open_signed'


def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    assert not SELECTED.exists()
    parents = [
        (PARENT / 'receipts/qualification-0001.json', '56a20dc3851234ddefeab003626614651d2bb929380cce0538eb53cbfb7400da'),
        (INTERFACE / 'current-source-adapter-v3/qualification-0001.json', '83f1070f9843f28d101da08e59b95c30fd8a310e47b9538a6d197a47e085a936'),
        (INTERFACE / 'current-mapped-context-v3/qualification-0001.json', 'a51822c6422f28af51cf3d64374a088f438bd80e6ebf06c99a0278a3d544cbcf'),
    ]
    for path, expected in parents:
        assert bind(path)['sha256'] == expected
        assert json.loads(path.read_bytes())['result'] == 'PASS'
    SELECTED.mkdir()
    for path in PARENT.iterdir():
        if path.is_file() and (path.suffix == '.py' or path.name in ['lifetime-policy.json', 'implementation-binding.json']):
            shutil.copyfile(path, SELECTED / path.name)
    shutil.copytree(PARENT / 'protocols', SELECTED / 'protocols')
    replacements = {
        'current-context-delivery-v6': 'current-context-delivery-v7',
        '_delivery_v6': '_delivery_v7',
        '_v25_v6': '_v25_v7',
        '_cal_current_context_delivery_v6': '_cal_current_context_delivery_v7',
        'current-mapped-context-v2': 'current-mapped-context-v3',
        '_mapper_v2_': '_mapper_v3_',
        'cdb291afc961952edaee4f1327d89a0decc7ea6ec330bd162c6f571d50657685': '665d5ac2287b95dfc5857780d57ee60b9f2e4aff351019eb669d6b5dad03b54e',
        '911d5f13514737d8f529b0199a0f37340e1a974ac63b53f3f9c2d5fe0e47b9f1': 'de880a25a53a4c1410c983489d81ef4a9a551316f36f79d5abde73112015a07b',
        '991c3068570a3584bfdfdb423d6f80fbea974f6ac3a739e126386ef974a34b35': 'b5130870913b980398dab64a1c33067231a042fe9d06f6d35f5afedaaffa96f2',
        'f4dda6b5b0c0b009a07f422bf482f0e885fd385421cd133703d0133bb40eb76c': 'b4381aa92a3519f1536bb4a64a74b4af0d0d3556bfc35a9254b8489bab301092',
        OLD_READER: NEW_READER,
    }
    for path in SELECTED.glob('*.py'):
        if path.name == 'freeze.py':
            continue
        text = path.read_text()
        for old, new in replacements.items():
            text = text.replace(old, new)
        ast.parse(text)
        path.write_text(text)
    binding = json.loads((PARENT / 'implementation-binding.json').read_bytes())
    binding['entrypoint_ref'] = binding['entrypoint_ref'].replace(OLD_READER, NEW_READER)
    binding['code_binding'] = {'ref': bind(SELECTED / 'build.py')['path'], 'sha256': bind(SELECTED / 'build.py')['sha256']}
    (SELECTED / 'implementation-binding.json').write_text(json.dumps(binding, indent=2, sort_keys=True) + '\n')
    text = (PARENT / 'freeze.py').read_text()
    text = text.replace("PARENT = HERE.parent / 'current-context-delivery-v5'", "PARENT = HERE.parent / 'current-context-delivery-v6'")
    text = text.replace('current-mapped-context-v2', 'current-mapped-context-v3').replace('context-delivery-0006.json', 'context-delivery-0007.json')
    text = text.replace('2908afb3d739d92d403c3f4035fe5742d626899a23b401103065b21e9314b5f3', 'd3ecda8d3c796e402e87efa25036ca4867534966ad4e50acb83741dc4fa9b010')
    text = text.replace("assert methods(HERE / name) == methods(PARENT / name), name", "assert methods(HERE / name) == methods_normalized(PARENT / name), name")
    text = text.replace('def main():', "def methods_normalized(path):\n    text = path.read_text().replace('current-source-adapter-v2/reader.py#SelectedReader.open_signed', 'current-source-adapter-v3/reader.py#SelectedReader.open_signed')\n    return {node.name: ast.dump(node, include_attributes=False) for node in ast.walk(ast.parse(text)) if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')}\n\n\ndef main():")
    text = text.replace("for document in [proof, load(observed_proof)]:", "for document in [proof, load(observed_proof), load(MAPPED / 'qualification-0001.json'), load(HERE.parent / 'current-source-adapter-v3/qualification-0001.json')]:")
    text = text.replace("RUN / 'EXECUTION-DEPENDENCY-REVIEW-0001.md', RUN / 'authorization.json']", "RUN / 'EXECUTION-DEPENDENCY-REVIEW-0001.md', RUN / 'authorization.json',\n              RUN / 'construct-R03-current-context-0007.py', RUN / 'current-context-binding-revision-0007.json',\n              MAPPED / 'qualification-0001.json', HERE.parent / 'current-source-adapter-v3/qualification-0001.json']")
    # The original observed import was Context5. Translate that exact source,
    # while retaining every original component declaration and parent receipt.
    text = text.replace("if path.is_relative_to(PARENT):\n            path = HERE / path.relative_to(PARENT)", "observed_context = HERE.parent / 'current-context-delivery-v5'\n        if path.is_relative_to(observed_context):\n            path = HERE / path.relative_to(observed_context)")
    text = text.replace('original50assertion_ASTs_preserved=True,', "original48assertion_ASTs_preserved=False, original50assertion_ASTs_preserved=False,\n                    original49assertion_ASTs_preserved=True, original50assertions_preserved_except_declared_reader_path=True,\n                    reader_path_revision_binding=bind(RUN / 'current-context-binding-revision-0007.json'),\n                    qualified_mapper_source_binding=bind(MAPPED / 'source-manifest.json'),\n                    qualified_mapper_package_binding=bind(MAPPED / 'packages/0001/manifest.json'),")
    text = text.replace('all50 original test method ASTs unchanged.', '49 original test method ASTs unchanged; sole reader path assertion explicitly rebound to qualified Reader3.')
    text = text.replace("'original_methods_preserved': 50", "'original_methods_preserved': 49, 'reader_path_assertion_rebound': 1")
    ast.parse(text)
    (SELECTED / 'freeze.py').write_text(text)
    put(RUN / 'current-context-binding-revision-0007.json', {
        'schema_version': 'lab-context-binding-revision/v1-candidate',
        'parent_bindings': [bind(path) for path, _ in parents],
        'test_name': 'test_42_current_API_profile_and_source_implementation_are_exact',
        'only_test_revision': {'old_reader_entrypoint': OLD_READER, 'new_reader_entrypoint': NEW_READER},
        'unchanged_test_methods': 49, 'total_test_methods': 50,
        'reason': 'Exact selected reader changed from Reader2 to qualified Reader3; original path assertion remains exact.',
        'clock_replaced': False, 'permission_cached': False, 'maximum_Session_seconds': 900,
        'context_qualified': False, 'authority_effect': 'none', 'actual_owner_outcome': None,
    })
    with (SELECTED / 'DESIGN.md').open('x') as stream:
        stream.write('# Context7 exact source successor\n\nSelect qualified Source4, Reader3 and Mapper3. Preserve the complete Context6 qualification and original runtime guards. The fixed Source4 period and 900 second Session ceiling remain.\n\nAll 50 tests remain: 49 methods have identical ASTs; test42 changes only its expected reader path from Reader2 to Reader3. The revision receipt binds both expectations and parent qualifications. No test is removed or weakened.\n\nThe complete qualification manifest retains history. The separate execution manifest selects all actual mapper declarations, original API schema/profile, observed imports, current production/configuration/templates and native executable. Every selected input remains guarded and belongs to the complete qualification.\n\nRequire actual build, full50 checks and independent source/native/carrier/code audit before qualification. API selection and full integration remain subsequent work. Authority effect: none; sole owner checkpoint R08 remains after complete S02.\n')
    print(json.dumps({'result': 'CONSTRUCTED', 'selected': str(SELECTED.relative_to(ROOT)), 'unchanged_methods': 49, 'reader_path_assertion_rebound': 1}), flush=True)


if __name__ == '__main__':
    main()
