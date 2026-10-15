"""Freeze internal pure transfer contracts and exact original schema resources."""
import ast
import hashlib
import json
from pathlib import Path
from jsonschema import Draft202012Validator

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
PACKAGE = ROOT / 'product/lab/release-candidates/v1/interface/package-transfer-v1'
ORIGINAL = ROOT / 'docs/proposals/0007-lab-integrated-schema-package'
COMMON = 'urn:cyberalchemy-lab:protocol:common:v1-candidate#/$defs/'


def binding(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def emit(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def ref(name):
    return {'$ref': COMMON + name}


def array(value, minimum=0):
    return {'type': 'array', 'items': value, 'minItems': minimum, 'maxItems': 1000}


def closed(properties):
    return {'type': 'object', 'additionalProperties': False, 'properties': properties, 'required': list(properties)}


def schema(name, version, properties):
    return {'$schema': 'https://json-schema.org/draft/2020-12/schema',
            '$id': 'urn:cyberalchemy-lab:internal:package-' + name + ':v1-candidate',
            **closed({'schema_version': {'const': version}, **properties})}


def main():
    authority = {'authority_effect': {'const': 'none'}, 'actual_owner_outcome': {'type': 'null'}}
    nullable = lambda value: {'anyOf': [value, {'type': 'null'}]}
    b64 = {'type': 'string', 'maxLength': 1400000}
    definitions = {
        'export-contract': schema('export-contract', 'lab-package-export-contract/v1-candidate', {
            'source_cut': ref('source_cut'), 'artifact_refs': array(ref('artifact_ref'), 1),
            'dependency_bindings': array(ref('binding')), 'source_admission_basis': array(ref('binding')),
            'source_posture': {'enum': ['controlled-candidate', 'admitted-source']},
            'maximum_package_bytes': {'type': 'integer', 'minimum': 1, 'maximum': 1048576}, **authority}),
        'privacy-review': schema('privacy-review', 'lab-package-privacy-review/v1-candidate', {
            'source_cut': ref('source_cut'), 'export_contract_binding': ref('binding'), 'materials': array(ref('binding'), 1),
            'include_session_memory': {'const': False}, 'include_private_credentials': {'const': False}, **authority}),
        'archive': schema('archive', 'lab-source-package/v1-candidate', {
            'source_cut': ref('source_cut'), 'artifact_refs': array(ref('artifact_ref'), 1),
            'source_admission_basis': array(ref('binding')), 'source_posture': {'enum': ['controlled-candidate', 'admitted-source']},
            'materials': array(closed({'binding': ref('binding'), 'artifact': nullable(ref('artifact_ref')),
                'dependencies': array(ref('binding')), 'original_bytes_b64': b64}), 1),
            'export_contract_binding': ref('binding'), 'privacy_review_binding': ref('binding'),
            'export_contract_bytes_b64': b64, 'privacy_review_bytes_b64': b64, 'authority_effect': {'const': 'none'},
            'target_admission_granted': {'const': False}, 'contains_session_memory': {'const': False},
            'contains_private_credentials': {'const': False}, 'source_admission_verified_by_this_calculation': {'const': False}}),
        'mapping': schema('mapping', 'lab-package-import-mapping/v1-candidate', {
            'source_package_binding': ref('binding'), 'target_base_cut': ref('source_cut'),
            'items': array(closed({'source': ref('artifact_ref'), 'target': nullable(ref('candidate_artifact_ref')),
                'target_bytes_b64': nullable(b64)}), 1), **authority}),
        'disposition': schema('disposition', 'lab-package-import-disposition/v1-candidate', {
            'source_package_binding': ref('binding'), 'target_base_cut': ref('source_cut'),
            'items': array(closed({'source': ref('artifact_ref'),
                'disposition': {'enum': ['import-exact', 'adapt', 'retain-source', 'exclude']},
                'reason': {'type': 'string', 'minLength': 1}}), 1), **authority})}
    for name, value in definitions.items():
        Draft202012Validator.check_schema(value)
        emit(PACKAGE / (name + '.schema.json'), value)
    readme = PACKAGE / 'README.md'
    with readme.open('x') as stream:
        stream.write('''# Package transfer v1 candidate calculation

Pure groundwork for package.export and package.import. Original public request
schemas remain unchanged. The five new schemas are closed internal controls and
archive structure; they are not canonical Definitions, Artifact Types or APIs.

Export retains each original JSON byte sequence, including whitespace, as base64.
It verifies hashes and complete reachable dependencies, allows bounded cycles,
and rejects dangling bindings, duplicate identities/references, unreachable extras,
incomplete ordered request closure, incomplete privacy review and private content.
Independent selected Actor/cut/control values must match; dataclasses do not
authenticate them. Source admission basis bytes survive as provenance, but this
calculation cannot verify signatures or transfer authority into the target.

Archive verification rechecks original controls and rebuilds the exact complete
metadata/content structure. Import accounts for every source artifact and retains
all nonartifact dependency bindings. Exact copy versus explicit adaptation must
match actual bytes; retain/exclude cannot conceal a candidate target. Every target
has a separate bound body, current selected scope and identity without collision.

The import plan explicitly leaves target model validation pending. Its host must
validate every original carrier/schema, full prospective model, typed relations,
mapping semantics, current preimages and complete generated Decision core before
exposing a Change Proposal. It must also verify source admission by actual replay.
No generalized validity is inferred from target hashing or source admission.

Integration still required: independently authenticated export/import policies,
actual current source and source replay, exact owned output scope, strict clocks
and budgets, durable operation claims, managed generation/recovery, target model
validation and complete real public tests. No public handlers are added yet.
Fixtures are synthetic pure values; no real user usefulness or admission is claimed.
''')
    files = sorted(path for path in PACKAGE.iterdir() if path.is_file() and path.name != 'source-manifest.json')
    for path in files:
        if path.suffix == '.py':
            ast.parse(path.read_bytes())
    pure = ast.parse((PACKAGE / 'test_transfer.py').read_bytes())
    count = sum(isinstance(node, ast.FunctionDef) and node.name.startswith('test_') for node in ast.walk(pure))
    inputs = {ORIGINAL / 'resources.py', ORIGINAL / 'schema-catalog.json',
              ORIGINAL / 'domain-bindings.json', ORIGINAL / 'schema-dependencies.json', Path(__file__).resolve()}
    inputs.update((ORIGINAL / 'schemas').glob('*.schema.json'))
    domains = json.loads((ORIGINAL / 'domain-bindings.json').read_bytes())
    for row in domains['bindings']:
        path = ROOT / row['schema_path']
        assert binding(path)['sha256'] == row['schema_sha256'], path
        inputs.add(path)
    dependencies = json.loads((ORIGINAL / 'schema-dependencies.json').read_bytes())
    for row in dependencies['bindings']:
        inputs.add(ROOT / row['source_path'])
        inputs.add(ROOT / row['target_path'])
    catalog = json.loads((ORIGINAL / 'schema-catalog.json').read_bytes())
    for row in catalog['reused_storage_schemas'] + [catalog['ephemeral_memory_binding']]:
        path = ROOT / row['path']
        assert binding(path)['sha256'] == row['sha256'], path
        inputs.add(path)
    own = [binding(path) for path in files]
    external = [binding(path) for path in sorted(inputs)]
    digest = hashlib.sha256(json.dumps(own + external, sort_keys=True, separators=(',', ':'),
        ensure_ascii=False, allow_nan=False).encode()).hexdigest()
    emit(PACKAGE / 'source-manifest.json', {'schema_version': 'lab-package-transfer-source/v1-candidate',
        'source_sha256': digest, 'files': own, 'input_bindings': external, 'selected_pure_cases': count,
        'public_handlers_added': 0, 'runtime_qualified': False, 'authority_effect': 'none', 'actual_owner_outcome': None})
    print(json.dumps({'result': 'FROZEN', 'source_sha256': digest, 'selected_pure_cases': count,
        'own_files': len(own), 'input_files': len(external), 'source_binding': binding(PACKAGE / 'source-manifest.json')}), flush=True)


if __name__ == '__main__':
    main()
