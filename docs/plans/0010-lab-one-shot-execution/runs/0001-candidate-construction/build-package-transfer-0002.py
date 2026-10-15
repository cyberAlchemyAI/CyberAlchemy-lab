"""Explicit raw dependency encodings and whole-plan bounds; preserve original50 tests."""
import ast
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD, NEW = BASE / 'package-transfer-v1', BASE / 'package-transfer-v2'


def load(path):
    return json.loads(path.read_bytes())


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def emit(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def change(path, old, new):
    text = path.read_text()
    assert text.count(old) == 1, (path, old)
    path.write_text(text.replace(old, new))


def methods(path):
    return {node.name: ast.dump(node, include_attributes=False) for node in ast.walk(ast.parse(path.read_bytes()))
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')}


def main():
    proof = OLD / 'receipts/checks-0001.json'
    assert load(proof)['result'] == 'PASS' and load(proof)['pure_cases'] == 50
    parent = load(OLD / 'source-manifest.json')
    for row in parent['files'] + parent['input_bindings']:
        assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
    NEW.mkdir(exist_ok=False)
    for row in parent['files']:
        path = ROOT / row['path']
        with (NEW / path.name).open('xb') as stream:
            stream.write(path.read_bytes())
    module = NEW / 'transfer.py'
    change(module, '    artifact_json: bytes | None = None', '    artifact_json: bytes | None = None\n    encoding: str = "json-utf8"')
    change(module, "        self.valid('urn:cyberalchemy-lab:internal:package-' + name + ':v1-candidate', value)",
        "        version = 'v2-candidate' if name in ('archive', 'privacy-review') else 'v1-candidate'\n"
        "        self.valid('urn:cyberalchemy-lab:internal:package-' + name + ':' + version, value)")
    change(module, '            value = parse(material.original)\n            privacy(value)',
        "            require(material.encoding in ('json-utf8', 'text-utf8', 'binary'), 'unknown dependency encoding')\n"
        "            require(type(material.original) is bytes and len(material.original) <= MAX_BYTES, 'bounded original material')\n"
        "            require(b'PRIVATE KEY-----' not in material.original, 'private key')\n"
        "            if material.encoding == 'json-utf8':\n                privacy(parse(material.original))\n"
        "            elif material.encoding == 'text-utf8':\n                text = material.original.decode('utf-8', errors='strict')\n"
        "                privacy(text)\n"
        "            else:\n                # A binary label cannot hide JSON credentials or Session memory.\n"
        "                try:\n                    structured = parse(material.original)\n"
        "                except (ValueError, UnicodeError, RecursionError):\n                    structured = None\n"
        "                if structured is not None:\n                    privacy(structured)")
    change(module, '            if header is not None:\n                self.valid',
        "            if header is not None:\n                require(material.encoding == 'json-utf8', 'artifact carrier requires original JSON body')\n                self.valid")
    change(module, "                'original_bytes_b64': base64.b64encode(material.original).decode('ascii')}",
        "                'original_bytes_b64': base64.b64encode(material.original).decode('ascii'), 'encoding': material.encoding}")
    change(module, "        frontier = []\n        for header in roots:",
        "        require(len({encoded(row) for row in admission}) == len(admission), 'duplicate source admission basis')\n"
        "        frontier = []\n        for header in roots:")
    change(module, "                and review['materials'] == [graph[ref]['binding'] for ref in sorted(graph)], 'privacy review misses package material')",
        "                and review['materials'] == [graph[ref]['binding'] for ref in sorted(graph)]\n"
        "                and review['material_encodings'] == [{'binding': graph[ref]['binding'], 'encoding': graph[ref]['encoding']} for ref in sorted(graph)],\n"
        "                'privacy review misses package material or encoding')")
    change(module, "package = {'schema_version': 'lab-source-package/v1-candidate'", "package = {'schema_version': 'lab-source-package/v2-candidate'")
    change(module, "self.valid('urn:cyberalchemy-lab:internal:package-archive:v1-candidate', package)",
        "self.valid('urn:cyberalchemy-lab:internal:package-archive:v2-candidate', package)")
    change(module, "None if row['artifact'] is None else encoded(row['artifact'])))",
        "None if row['artifact'] is None else encoded(row['artifact']), row['encoding']))")
    change(module, "            return {'source_package_binding': request['source_package_binding'], 'source_cut': package['source_cut'],",
        "            plan = {'source_package_binding': request['source_package_binding'], 'source_cut': package['source_cut'],")
    change(module, "                'automatic_admission': False, 'target_model_validation_pending': True, 'authority_effect': 'none'}",
        "                'automatic_admission': False, 'target_model_validation_pending': True, 'authority_effect': 'none'}\n"
        "            require(len(encoded(plan)) <= MAX_BYTES, 'complete import plan byte budget')\n            return plan")
    for name in ('archive', 'privacy-review'):
        path = NEW / (name + '.schema.json')
        schema = load(path)
        schema['$id'] = schema['$id'].replace(':v1-candidate', ':v2-candidate')
        schema['properties']['schema_version']['const'] = schema['properties']['schema_version']['const'].replace('/v1-candidate', '/v2-candidate')
        enum = {'enum': ['json-utf8', 'text-utf8', 'binary']}
        if name == 'archive':
            item = schema['properties']['materials']['items']
            item['properties']['encoding'] = enum
            item['required'].append('encoding')
        else:
            schema['properties']['material_encodings'] = {'type': 'array', 'minItems': 1, 'maxItems': 1000,
                'items': {'type': 'object', 'additionalProperties': False,
                    'properties': {'binding': {'$ref': 'urn:cyberalchemy-lab:protocol:common:v1-candidate#/$defs/binding'}, 'encoding': enum},
                    'required': ['binding', 'encoding']}}
            schema['required'].append('material_encodings')
        path.write_text(json.dumps(schema, indent=2, sort_keys=True) + '\n')
    test = NEW / 'test_transfer.py'
    change(test, "'lab-package-privacy-review/v1-candidate'", "'lab-package-privacy-review/v2-candidate'")
    change(test, "'export_contract_binding': self.contract_binding, 'materials': bindings,",
        "'export_contract_binding': self.contract_binding, 'materials': bindings,\n"
        "            'material_encodings': [{'binding': T.parse(m.binding_json), 'encoding': m.encoding} for m in sorted(self.materials, key=lambda m: T.parse(m.binding_json)['ref'])],")
    change(test, "'actor': self.actor, 'source_cut': self.cut, 'artifact_refs': [self.header],",
        "'actor': self.actor, 'source_cut': self.cut, 'artifact_refs': self.contract['artifact_refs'],")
    extra = RUN / 'package-transfer-extra-cases-0002.txt'
    assert extra.exists(), 'extra tests must be authored before freeze'
    tests = test.read_text() + '\n' + extra.read_text()
    test.write_text(tests)
    original_methods = methods(OLD / 'test_transfer.py')
    new_methods = methods(test)
    assert len(original_methods) == 50 and all(new_methods[key] == value for key, value in original_methods.items())
    for path in NEW.glob('*.py'):
        ast.parse(path.read_bytes())
    readme = NEW / 'README.md'
    readme.write_text(readme.read_text() + '''

## v2 successor

Raw text and binary dependencies have explicit encoding declarations covered by
the complete privacy review. Artifact bodies remain original JSON for later
carrier validation. Exact raw dependency bytes survive archive verification;
neither parsing nor rendering rewrites them. Binary labeling cannot bypass the
JSON credential/Session checks, and PEM key markers are refused in every encoding.
The actual host remains responsible for a genuine privacy review of every raw
dependency; a byte scan is not proof that an arbitrary binary contains no secret.
Source basis duplicates are refused. Complete import output is bounded at 1 MiB.
Archive and privacy-review internal schemas are explicit v2 successors; original
public request schemas and all 50 original test assertions remain unchanged.
''')
    own = [bind(path) for path in sorted(NEW.iterdir()) if path.is_file() and path.name != 'source-manifest.json']
    inputs = {row['path']: row for row in parent['files'] + parent['input_bindings']}
    for path in [OLD / 'source-manifest.json', proof, extra, Path(__file__).resolve()]:
        row = bind(path)
        inputs[row['path']] = row
    external = [inputs[key] for key in sorted(inputs)]
    digest = hashlib.sha256(json.dumps(own + external, sort_keys=True, separators=(',', ':'),
        ensure_ascii=False, allow_nan=False).encode()).hexdigest()
    emit(NEW / 'source-manifest.json', {**parent, 'source_sha256': digest, 'files': own,
        'input_bindings': external, 'selected_pure_cases': len(new_methods),
        'parent_source_binding': bind(OLD / 'source-manifest.json'), 'retained_original_cases': 50})
    print(json.dumps({'result': 'FROZEN', 'source_sha256': digest, 'selected_pure_cases': len(new_methods),
        'retained_original_cases': 50, 'source_binding': bind(NEW / 'source-manifest.json')}), flush=True)


if __name__ == '__main__':
    main()
