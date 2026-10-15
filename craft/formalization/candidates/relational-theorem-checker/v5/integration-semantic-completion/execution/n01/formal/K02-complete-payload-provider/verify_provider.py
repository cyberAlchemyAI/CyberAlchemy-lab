"""Exercise complete source formats without claiming formal correspondence."""
from copy import deepcopy
from dataclasses import replace
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import re
import shutil
import subprocess

import jsonschema
from provider import (CandidateBodyProvider, LocalLimits, Refused, ROOT, HERE, read_bound,
                      pattern_matches, TIMESTAMP_PATTERN, ECMA_WHITESPACE)


def binding(path):
    return {'path': str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def encoded(body):
    return json.dumps(body, ensure_ascii=True, separators=(',', ':')).encode()


def at(value, path):
    for part in path:
        value = value[part]
    return value


def run():
    captured = [binding(HERE / name) for name in
                ['FORMALIZATION.md', 'PATTERN-FORMALIZATION.md', 'profile-manifest.json',
                 'provider.py', 'verify_provider.py', 'regex_reference.mjs']]
    provider, cases, positives = CandidateBodyProvider(), [], {}
    manifest = json.loads((HERE / 'profile-manifest.json').read_text())
    assert len(manifest['profiles']) == len(provider.profiles) == 7
    assert not manifest['owned_profile_admission'] and not manifest['authenticity_proved']

    def exercise(case_id, kind, raw, refusal=None, keyword=None,
                 expected_digest=None, limits=LocalLimits()):
        digest = hashlib.sha256(raw).hexdigest()
        try:
            value = provider.decode(kind, raw, digest if expected_digest is None else expected_digest, limits)
            assert refusal is None, (case_id, 'accepted', refusal)
            assert value.original_bytes == raw and value.body_digest == digest
            row = provider.profiles[kind]
            assert value.schema_digest == row['schema']['sha256'] and value.schema_ref == row['schema_ref']
            assert value.identity_token == value.body[row['identity_field']]
            observed, detail = 'candidate-body-decoded', None
        except Refused as error:
            assert error.code == refusal, (case_id, error.code, refusal, error.detail)
            if keyword:
                assert keyword in {item['keyword'] for item in error.detail}, (case_id, error.detail)
            observed, detail = error.code, error.detail
        cases.append({'id': case_id, 'kind': kind, 'input_sha256': digest,
                      'input_bytes': len(raw), 'expected': refusal or 'candidate-body-decoded',
                      'observed': observed, 'required_schema_keyword': keyword, 'detail': detail})

    def changed(kind, case_id, path, value=None, remove=False, keyword=None):
        body = deepcopy(positives[kind])
        parent = at(body, path[:-1])
        if remove:
            del parent[path[-1]]
        else:
            parent[path[-1]] = value
        exercise(case_id, kind, encoded(body), 'schema', keyword)

    required_paths = []
    nested_paths, array_paths = [], []
    for kind, row in provider.profiles.items():
        artifact, schema = read_bound(row['artifact']), read_bound(row['schema'])
        assert artifact['schema_digest'] == row['schema']['sha256']
        assert artifact['status'] == row['source_status'] == 'candidate-unadmitted'
        assert set(schema['required']) == set(row['required_fields'])
        assert sorted(schema['properties']) == row['all_top_level_fields']
        raw = (ROOT / row['positive_fixture']['path']).read_bytes()
        assert binding(ROOT / row['positive_fixture']['path']) == row['positive_fixture']
        positives[kind] = json.loads(raw)
        exercise(kind + ':original-positive', kind, raw)
        decoded = provider.decode(kind, raw, hashlib.sha256(raw).hexdigest())
        assert decoded.body == positives[kind]
        changed_copy = decoded.body
        changed_copy.clear()
        assert decoded.body == positives[kind]
        for field in row['required_fields']:
            changed(kind, kind + ':required:' + field, [field], remove=True, keyword='required')
            required_paths.append((kind, field))
        changed(kind, kind + ':extra-top-level', ['unreviewed_field'], True, keyword='additionalProperties')
        changed(kind, kind + ':authority-claim', ['authority_effect'], 'granted', keyword='const')

        def walk(rule, value, path):
            if '$ref' in rule:
                resolved = schema
                for part in rule['$ref'][2:].split('/'):
                    resolved = resolved[part.replace('~1', '/').replace('~0', '~')]
                walk(resolved, value, path)
                return
            if isinstance(value, dict):
                if path:
                    for field in rule.get('required', []):
                        changed(kind, kind + ':nested-required:' + '/'.join(map(str, path + [field])),
                                path + [field], remove=True, keyword='required')
                        nested_paths.append((kind, path + [field]))
                    if rule.get('additionalProperties') is False:
                        changed(kind, kind + ':nested-extra:' + '/'.join(map(str, path)),
                                path + ['unreviewed_field'], True, keyword='additionalProperties')
                for field, subrule in rule.get('properties', {}).items():
                    if field in value:
                        walk(subrule, value[field], path + [field])
            elif isinstance(value, list):
                if rule.get('uniqueItems') and rule.get('items', {}).get('type') == 'string':
                    duplicate = value + [value[0]] if value else ['fixture:duplicate'] * 2
                    changed(kind, kind + ':unique:' + '/'.join(map(str, path)), path, duplicate, keyword='uniqueItems')
                    array_paths.append((kind, path, 'uniqueItems'))
                if rule.get('minItems', 0) > 0:
                    changed(kind, kind + ':minItems:' + '/'.join(map(str, path)), path, [], keyword='minItems')
                    array_paths.append((kind, path, 'minItems'))
                if 'maxItems' in rule and rule.get('items', {}).get('type') == 'string':
                    excess = ['fixture:entry:' + str(i) for i in range(rule['maxItems'] + 1)]
                    changed(kind, kind + ':maxItems:' + '/'.join(map(str, path)), path, excess, keyword='maxItems')
                    array_paths.append((kind, path, 'maxItems'))
                for index, child in enumerate(value):
                    walk(rule.get('items', {}), child, path + [index])

        walk(schema, positives[kind], [])
        for source in row['negative_fixtures']:
            fixture_path = ROOT / source['path']
            assert binding(fixture_path) == source
            data = json.loads(fixture_path.read_text())
            if data.get('fixture_kind') == 'mutation-v1':
                data_source = data
                data = json.loads((fixture_path.parents[2] / data_source['base_path']).read_text())
                for mutation in data_source['mutations']:
                    parts = [part for part in mutation['path'].split('/') if part]
                    parent = data
                    for part in parts[:-1]:
                        parent = parent[int(part)] if isinstance(parent, list) else parent[part]
                    leaf = int(parts[-1]) if isinstance(parent, list) else parts[-1]
                    if mutation['op'] == 'remove':
                        del parent[leaf]
                    elif mutation['op'] in {'add', 'replace'}:
                        parent[leaf] = mutation['value']
                    else:
                        raise AssertionError(mutation['op'])
            exercise(kind + ':original-negative:' + fixture_path.name, kind, encoded(data), 'schema')

    for state, field in [('satisfied', 'satisfaction_refs'), ('superseded', 'successor_refs')]:
        data = deepcopy(positives['intent'])
        data['intent_state'], data[field] = state, []
        exercise('intent:conditional:' + state, 'intent', encoded(data), 'schema', 'minItems')
        data[field] = ['fixture:separately-unresolved-support']
        exercise('intent:shape-only-state:' + state, 'intent', encoded(data))
    changed('goal', 'goal:wrong-schema-version', ['schema_version'], 'unreviewed/v9', keyword='const')
    changed('goal', 'goal:common-header-invented', ['node_id'], 'invented', keyword='additionalProperties')
    changed('project', 'project:common-version-invented', ['schema_version'], 'unreviewed/v1', keyword='additionalProperties')
    changed('research-inquiry', 'inquiry:timestamp', ['created_at'], 'yesterday', keyword='pattern')
    changed('research-inquiry', 'inquiry:non-ascii-timestamp-digits', ['created_at'],
            '٢٠٢٦-١٠-١١T٠٠:٠٠:٠٠Z', keyword='pattern')
    changed('research-inquiry', 'inquiry:timestamp-final-newline', ['created_at'],
            '2026-10-11T00:00:00Z\n', keyword='pattern')
    changed('project', 'project:ecma-whitespace-only', ['purpose'], '\ufeff', keyword='pattern')
    nel = deepcopy(positives['project'])
    nel['purpose'] = '\u0085'
    exercise('project:ecma-non-whitespace-nel', 'project', encoded(nel))
    changed('agent-assignment', 'assignment:lifecycle-enum', ['lifecycle_state'], 'completed', keyword='enum')

    raw = encoded(positives['project'])
    exercise('bytes:wrong-profile', 'goal', raw, 'schema')
    exercise('bytes:wrong-digest', 'project', raw, 'digest-mismatch', expected_digest='0' * 64)
    exercise('bytes:invalid-digest', 'project', raw, 'digest-format', expected_digest='owner-approved')
    exercise('bytes:limit', 'project', raw, 'byte-budget', limits=replace(LocalLimits(), max_bytes=len(raw)-1))
    exercise('bytes:depth', 'project', raw, 'depth-budget', limits=replace(LocalLimits(), max_depth=0))
    exercise('bytes:negative-limit', 'project', raw, 'invalid-limits', limits=replace(LocalLimits(), max_depth=-1))
    exercise('bytes:boolean-limit', 'project', raw, 'invalid-limits', limits=replace(LocalLimits(), max_depth=True))
    exercise('bytes:utf8', 'project', b'\xff', 'utf8')
    exercise('bytes:json', 'project', b'{', 'json')
    exercise('bytes:array', 'project', b'[]', 'object-required')
    exercise('bytes:duplicate', 'project', raw[:-1] + b',"kind":"project"}', 'duplicate-member')
    inquiry = encoded(positives['research-inquiry'])
    duplicate = inquiry.replace(b'"source_policy":{', b'"source_policy":{"freshness_rule":"duplicate",', 1)
    assert duplicate != inquiry
    exercise('bytes:nested-duplicate', 'research-inquiry', duplicate, 'duplicate-member')
    exercise('bytes:surrogate', 'project', b'{"unused":"\\ud800"}', 'unsupported-surrogate')
    exercise('bytes:key-surrogate', 'project', b'{"\\ud800":"unused"}', 'unsupported-surrogate')
    exercise('bytes:nan', 'project', b'{"unused":NaN}', 'non-json-constant')
    exercise('bytes:huge-exponent', 'project', b'{"unused":1e1000000000}', 'numeric-budget')
    exercise('bytes:huge-mantissa', 'project', b'{"unused":' + b'1' * 129 + b'}', 'numeric-budget')
    exercise('bytes:unknown-kind', 'unreviewed-kind', raw, 'unsupported-kind')
    bracket_body = deepcopy(positives['project'])
    bracket_body['purpose'] = '[' * 1000 + '1e1000000000' + ']' * 1000
    exercise('bytes:string-is-not-structure-or-number', 'project', encoded(bracket_body))
    escaped = deepcopy(positives['project'])
    escaped['purpose'] = 'Scalar emoji \U0001f600'
    exercise('bytes:supported-paired-surrogate', 'project', encoded(escaped))
    try:
        read_bound(dict(provider.profiles['project']['schema'], sha256='0' * 64))
        raise AssertionError('changed schema accepted')
    except Refused as error:
        assert error.code == 'changed-profile-source'
    exposed = provider.profiles
    exposed['project']['identity_field'] = 'purpose'
    assert provider.profiles['project']['identity_field'] == 'node_id'
    regex_cases = [{'pattern': r'\S', 'value': chr(code)} for code in
                   [*sorted(ECMA_WHITESPACE), 0x85, 0x1c, 0x180e, 0x200b, 0x1f600]]
    regex_cases += [{'pattern': r'\S', 'value': value}
                    for value in ['', ' ', ' x ', '\ufeffx\ufeff']]
    timestamps = ['2026-10-11T00:00:00Z', '9999-99-99T99:99:99Z',
                  '٢٠٢٦-١٠-١١T٠٠:٠٠:٠٠Z', '', '2026-10-11T00:00:00Z\n',
                  '2026-10-11T00:00:00Z\r', '2026-10-11T00:00:00Z\u2028']
    base = '2026-10-11T00:00:00Z'
    for index in range(20):
        for char in ['0', '9', 'a', '٠', '\n', 'Z', 'T', '-', ':']:
            timestamps.append(base[:index] + char + base[index+1:])
    regex_cases += [{'pattern': TIMESTAMP_PATTERN, 'value': value} for value in timestamps]
    node = Path(shutil.which('node')).resolve()
    node_binding = binding(node)
    reference = subprocess.run([str(node), str(HERE / 'regex_reference.mjs')],
                               input=json.dumps({'cases': regex_cases}), capture_output=True,
                               text=True, timeout=30, check=True)
    oracle = json.loads(reference.stdout)
    assert oracle['scalarCount'] == 1112064
    assert set(oracle['whitespace']) == ECMA_WHITESPACE
    assert oracle['results'] == [pattern_matches(case['pattern'], case['value']) for case in regex_cases]
    assert binding(node) == node_binding
    differences = [{'pattern': case['pattern'], 'value': case['value'],
                    'python_result': bool(re.search(case['pattern'], case['value'])),
                    'ecmascript_result': result}
                   for case, result in zip(regex_cases, oracle['results'], strict=True)
                   if bool(re.search(case['pattern'], case['value'])) != result]
    assert any(case['value'] == '\ufeff' for case in differences)
    assert any(case['value'] == '\u0085' for case in differences)
    assert any(case['value'] == '٢٠٢٦-١٠-١١T٠٠:٠٠:٠٠Z' for case in differences)
    assert any(case['value'] == '2026-10-11T00:00:00Z\n' for case in differences)
    assert len({case['id'] for case in cases}) == len(cases)
    assert [binding(HERE / Path(item['path']).name) for item in captured] == captured
    report = {'task': 'N01', 'unit': HERE.name, 'result': 'candidate-complete-body-controls-pass',
              'method': 'Complete pinned source schemas exercised by the installed validator; not a formal schema refinement proof.',
              'sources': captured, 'profile_manifest': binding(HERE / 'profile-manifest.json'),
              'runtime': {'python': platform.python_version(), 'jsonschema': importlib.metadata.version('jsonschema'),
                          'referencing': importlib.metadata.version('referencing'), 'node': oracle['nodeVersion']},
              'ecmascript_reference_binary': node_binding,
              'scalar_regex_whitespace_exhaustion_count': oracle['scalarCount'],
              'regex_runtime_comparison_count': len(regex_cases),
              'observed_python_ecmascript_differences': differences,
              'exact_two_pinned_pattern_forms_implemented': True,
              'profiles': list(provider.profiles.values()), 'profile_count': 7,
              'positive_body_count': 7, 'required_top_level_field_counterexamples': len(required_paths),
              'required_top_level_field_paths': required_paths,
              'nested_required_counterexamples': len(nested_paths), 'nested_required_paths': nested_paths,
              'array_constraint_counterexamples': len(array_paths), 'array_constraint_paths': array_paths,
              'runtime_case_count': len(cases), 'runtime_cases': cases,
              'all_original_body_fields_retained_in_positive_cases': True,
              'exact_source_schema_references_retained': True,
              'changed_schema_binding_refused': True, 'returned_body_and_profile_mutation_isolated': True,
              'general_lean_decoder_correspondence_proved': False,
              'general_json_schema_semantics_proved': False, 'regex_dialect_correspondence_proved': False,
              'owned_profile_admission_proved': False, 'approved_kind_specific_payload_decoders_realized': False,
              'real_authoritative_source_provider': False, 'integrated_into_lean_full_entrypoint': False,
              'all_eighteen_remaining_source_policies_realized': False,
              'new_general_theorems': 0, 'inherited_discharges': 0, 'independent_checker_run': False,
              'supported_resource_envelope_measured': False, 'N01_accepted': False, 'authority_effect': 'none'}
    (HERE / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: report[key] for key in ['result', 'profile_count', 'positive_body_count',
          'required_top_level_field_counterexamples', 'nested_required_counterexamples',
          'array_constraint_counterexamples', 'runtime_case_count', 'inherited_discharges']}, indent=2))


if __name__ == '__main__':
    run()
