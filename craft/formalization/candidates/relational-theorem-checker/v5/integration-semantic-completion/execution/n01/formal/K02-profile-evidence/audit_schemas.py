"""Candidate decoded-value shape checks, not raw representation equivalence."""
from pathlib import Path
import copy
import hashlib
import importlib.metadata
import json
import jsonschema

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[9]


def binding(path): return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def run():
    path = HERE / 'authority-snapshot.schema.json'; schema = json.loads(path.read_text())
    jsonschema.Draft202012Validator.check_schema(schema); validator = jsonschema.Draft202012Validator(schema)
    fixture = HERE / 'fixtures/authority-positive.json'; original = json.loads(fixture.read_text())
    assert validator.is_valid(original)
    checks = [{'case': 'batched-review-multiple-action-positive', 'valid': True, 'source': binding(fixture)}]
    variants = []
    missing = copy.deepcopy(original); missing['body']['target'].pop('trust_root'); variants.append(('missing-root', missing))
    extra = copy.deepcopy(original); extra['body']['target']['extra'] = 1; variants.append(('extra-payload-field', extra))
    invalid = copy.deepcopy(original); invalid['body']['target']['issuances'][0]['source_bytes'][0] = 300; variants.append(('byte-outside-domain', invalid))
    action = copy.deepcopy(original); action['body']['target']['entitlements'][0]['actions'] = ['admin']; variants.append(('unsupported-action', action))
    for label, value in variants:
        assert not validator.is_valid(value); checks.append({'case': label, 'valid': False})
    for name in ['authority-missing-review', 'authority-altered-issued-bytes', 'authority-unused-review-conflict']:
        value = json.loads((HERE / 'fixtures' / (name + '.json')).read_text())
        assert validator.is_valid(value)
        checks.append({'case': name + ':shape-valid-but-semantic-refusal', 'valid': True,
                       'source': binding(HERE / 'fixtures' / (name + '.json'))})
    numeric_path = HERE / 'fixtures/authority-rounded-noninteger-byte.json'
    numeric = json.loads(numeric_path.read_text())
    assert numeric['body']['target']['issuances'][0]['source_bytes'][0] == 123.0
    assert validator.is_valid(numeric); checks.append({'case': 'rounded-noninteger-byte-representation-gap', 'valid': True,
                                                      'source': binding(numeric_path), 'does_not_establish_raw_decoder_acceptance': True})
    report = {'task': 'N01', 'unit': 'K02-profile-evidence', 'result': 'candidate-schema-shape-audit-pass',
              'driver': binding(Path(__file__)), 'schema': binding(path), 'api_contract': binding(HERE / 'candidate-api-contract.json'),
              'validator_version': importlib.metadata.version('jsonschema'), 'checks': checks,
              'byte_decoder_equivalence_proved': False, 'JSON_schema_semantics_interpreter_proved': False,
              'inherited_discharges': 0, 'authority_effect': 'none'}
    (HERE / 'schema-shape-audit.json').write_text(json.dumps(report, indent=2) + '\n')
    print({'result': report['result'], 'checks': len(checks)})


if __name__ == '__main__': run()
