"""Check candidate schema shapes; explicitly avoid claiming byte-level equivalence."""
from pathlib import Path
import copy
import hashlib
import json
import jsonschema

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[9]


def binding(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def run():
    checks = []
    for name in ['declaration', 'selection']:
        path = HERE / 'schemas' / (name + '.schema.json')
        schema = json.loads(path.read_text())
        jsonschema.Draft202012Validator.check_schema(schema)
        validator = jsonschema.Draft202012Validator(schema)
        fixture_path = HERE / 'fixtures' / (name + '.json')
        original = json.loads(fixture_path.read_text())
        assert validator.is_valid(original)
        checks.append({'source': binding(fixture_path), 'schema': binding(path), 'case': name + ':positive', 'valid': True})
        variants = []
        absent = copy.deepcopy(original); absent['body']['target'].pop('issuer'); variants.append(('missing-issuer', absent))
        extra = copy.deepcopy(original); extra['body']['target']['extra'] = 1; variants.append(('extra-target-field', extra))
        posture = copy.deepcopy(original); posture['body']['target']['review_posture'] = 'approved'; variants.append(('unsupported-review-token', posture))
        ref = copy.deepcopy(original); ref['owner_review_ref']['key']['extra'] = True; variants.append(('extra-reference-field', ref))
        epoch = copy.deepcopy(original); epoch['body']['frame']['epoch'] = -1; variants.append(('negative-epoch', epoch))
        for label, value in variants:
            assert not validator.is_valid(value), (name, label)
            checks.append({'case': name + ':' + label, 'valid': False})
        # Demonstrate the remaining representation gap: a decoded integral float
        # is shape-valid while its JSON lexeme is refused by the exact Nat decoder.
        integral_float = copy.deepcopy(original); integral_float['body']['frame']['epoch'] = 42.0
        assert validator.is_valid(integral_float)
        checks.append({'case': name + ':integral-float-decoded-value-gap', 'valid': True,
                       'does_not_establish_byte_decoder_acceptance': True})
    report = {'task': 'N01', 'unit': 'K02-profile-selection', 'result': 'candidate-schema-shape-audit-pass',
              'driver': binding(Path(__file__)), 'api_contract': binding(HERE / 'candidate-api-contract.json'),
              'validator_version': __import__('importlib.metadata', fromlist=['version']).version('jsonschema'),
              'checks': checks, 'byte_decoder_equivalence_proved': False,
              'JSON_schema_semantics_interpreter_proved': False, 'inherited_discharges': 0, 'authority_effect': 'none'}
    (HERE / 'schema-shape-audit.json').write_text(json.dumps(report, indent=2) + '\n')
    print({'result': report['result'], 'checks': len(checks), 'byte_decoder_equivalence_proved': False})


if __name__ == '__main__':
    run()
