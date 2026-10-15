"""Separate large source-package bounds from unchanged public control budgets."""
import ast
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD, NEW = BASE / 'package-transfer-v2', BASE / 'package-transfer-v3'


def load(path):
    return json.loads(path.read_bytes())


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def change(path, old, new):
    text = path.read_text()
    assert text.count(old) == 1, (path, old)
    path.write_text(text.replace(old, new))


def methods(path):
    return {node.name: ast.dump(node, include_attributes=False) for node in ast.walk(ast.parse(path.read_bytes()))
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')}


def main():
    proof = OLD / 'receipts/checks-0001.json'
    assert load(proof)['result'] == 'PASS' and load(proof)['pure_cases'] == 61
    parent = load(OLD / 'source-manifest.json')
    for row in parent['files'] + parent['input_bindings']:
        assert bind(ROOT / row['path']) == row
    NEW.mkdir(exist_ok=False)
    for row in parent['files']:
        original = ROOT / row['path']
        with (NEW / original.name).open('xb') as stream:
            stream.write(original.read_bytes())
    module = NEW / 'transfer.py'
    change(module, 'MAX_BYTES = 1024 * 1024', '''MAX_BYTES = 1024 * 1024  # Public requests, controls, metadata and target proposals.
MAX_MATERIAL_BYTES = 32 * 1024 * 1024
MAX_SOURCE_BYTES = 40 * 1024 * 1024
MAX_PACKAGE_BYTES = 64 * 1024 * 1024''')
    change(module, 'def parse(raw):\n    require(type(raw) is bytes and len(raw) <= MAX_BYTES,',
        'def parse(raw, maximum=MAX_BYTES):\n    require(type(maximum) is int and 0 < maximum <= MAX_PACKAGE_BYTES, "invalid independent parser bound")\n    require(type(raw) is bytes and len(raw) <= maximum,')
    change(module, "        value = parse(raw)\n        version = 'v2-candidate' if name in ('archive', 'privacy-review') else 'v1-candidate'",
        "        value = parse(raw, MAX_PACKAGE_BYTES if name == 'archive' else MAX_BYTES)\n"
        "        version = {'archive': 'v3-candidate', 'privacy-review': 'v2-candidate', 'export-contract': 'v2-candidate'}.get(name, 'v1-candidate')")
    change(module, "len(material.original) <= MAX_BYTES, 'bounded original material'",
        "len(material.original) <= MAX_MATERIAL_BYTES, 'bounded original material'")
    start = "            if material.encoding == 'json-utf8':"
    end = "            dependencies = parse(material.dependencies_json)"
    source = module.read_text()
    begin, finish = source.index(start), source.index(end)
    source = source[:begin] + '''            # Structured bytes stay structured across labels. Malformed JSON-looking
            # text/binary is refused rather than treated as a privacy-safe blob.
            structured = material.original.lstrip().startswith((b'{', b'[', b'"'))
            if material.encoding == 'json-utf8' or structured:
                privacy(parse(material.original, MAX_MATERIAL_BYTES))
            elif material.encoding == 'text-utf8':
                privacy(material.original.decode('utf-8', errors='strict'))
            # Arbitrary nonstructured binary still needs independent human/source
            # privacy evidence. This scan is not a proof of absence of secrets.
''' + source[finish:]
    module.write_text(source)
    change(module, "total <= MAX_BYTES, 'complete original material byte budget'", "total <= MAX_SOURCE_BYTES, 'complete original material byte budget'")
    change(module, "'lab-source-package/v2-candidate'", "'lab-source-package/v3-candidate'")
    change(module, "'urn:cyberalchemy-lab:internal:package-archive:v2-candidate'", "'urn:cyberalchemy-lab:internal:package-archive:v3-candidate'")
    change(module, "min(MAX_BYTES, contract['maximum_package_bytes'])", "min(MAX_PACKAGE_BYTES, contract['maximum_package_bytes'])")
    change(module, 'rebuilt = parse(self.export(encoded(request), facts, contract, review))',
        'rebuilt = parse(self.export(encoded(request), facts, contract, review), MAX_PACKAGE_BYTES)')
    # Archive verification must independently guard its source on both exits too.
    source = module.read_text()
    begin, finish = source.index('    def verify_archive('), source.index('    def account_import(')
    old = source[begin:finish]
    lines = old.rstrip().splitlines()
    wrapper = [lines[0], '        self.guard()', '        try:']
    wrapper.extend('    ' + line for line in lines[1:])
    wrapper.extend(['        finally:', '            self.guard()', '', ''])
    module.write_text(source[:begin] + '\n'.join(wrapper) + source[finish:])
    for name, version in [('archive', 'v3-candidate'), ('export-contract', 'v2-candidate')]:
        path = NEW / (name + '.schema.json')
        schema = load(path)
        schema['$id'] = schema['$id'].rsplit(':', 1)[0] + ':' + version
        schema['properties']['schema_version']['const'] = schema['properties']['schema_version']['const'].rsplit('/', 1)[0] + '/' + version
        if name == 'archive':
            schema['properties']['materials']['items']['properties']['original_bytes_b64']['maxLength'] = 4 * ((32 * 1024 * 1024 + 2) // 3)
        else:
            schema['properties']['maximum_package_bytes']['maximum'] = 64 * 1024 * 1024
        path.write_text(json.dumps(schema, indent=2, sort_keys=True) + '\n')
    test = NEW / 'test_transfer.py'
    change(test, "'lab-package-export-contract/v1-candidate'", "'lab-package-export-contract/v2-candidate'")
    extra = RUN / 'package-transfer-extra-cases-0003.txt'
    test.write_text(test.read_text() + '\n' + extra.read_text())
    previous, current = methods(OLD / 'test_transfer.py'), methods(test)
    assert len(previous) == 61 and all(current[k] == v for k, v in previous.items())
    readme = NEW / 'README.md'
    readme.write_text(readme.read_text() + '''

## v3 successor

Controls, API requests, import mapping/disposition, target bodies and resulting
plans retain their original 1 MiB budget. Individual source materials are capped
at 32 MiB, aggregate originals at 40 MiB and encoded archives at 64 MiB, further
limited by the independently selected export contract. These limits allow a
complete selected 23.5 MB replay snapshot without dropping its dependencies.
Archive/v3 and export-contract/v2 are explicit internal schema successors.

Text/binary labels cannot hide JSON objects, arrays or strings: structured-looking
bytes must pass the bounded strict decoder and recursive privacy checks.
Duplicate keys, malformed or invalid UTF-8 structured bytes are refused. Ordinary
text and binary bytes remain exact. Independent source/privacy review is still
required for arbitrary nonstructured data; this calculation supplies no authority.
Archive verification now checks its frozen source both before and after work.
All 61 predecessor assertions are retained; no public handler is added here.
''')
    for path in NEW.glob('*.py'):
        ast.parse(path.read_bytes())
    own = [bind(p) for p in sorted(NEW.iterdir()) if p.is_file() and p.name != 'source-manifest.json']
    inputs = {row['path']: row for row in parent['files'] + parent['input_bindings']}
    for path in [OLD / 'source-manifest.json', proof, extra, Path(__file__).resolve()]:
        row = bind(path)
        inputs[row['path']] = row
    external = [inputs[k] for k in sorted(inputs)]
    raw = json.dumps(own + external, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()
    digest = hashlib.sha256(raw).hexdigest()
    manifest = {**parent, 'source_sha256': digest, 'files': own, 'input_bindings': external,
        'parent_source_binding': bind(OLD / 'source-manifest.json'), 'selected_pure_cases': len(current),
        'retained_original_cases': 50, 'retained_predecessor_cases': 61,
        'budgets': {'control_bytes': 1048576, 'material_bytes': 33554432, 'source_bytes': 41943040, 'archive_bytes': 67108864}}
    with (NEW / 'source-manifest.json').open('x') as stream:
        json.dump(manifest, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': 'FROZEN', 'source_sha256': digest, 'pure_cases': len(current),
        'retained_predecessor_cases': 61, 'source_binding': bind(NEW / 'source-manifest.json')}), flush=True)


if __name__ == '__main__':
    main()
