"""Decoded JSON shape controls; no raw byte/schema equivalence is claimed."""
from pathlib import Path
import copy, hashlib, json
from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[9]
def binding(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
def run():
    schema_path = HERE / 'catalog-snapshot.schema.json'
    schema = json.loads(schema_path.read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    fixtures, checks = {}, []
    def check(label, value, expected):
        actual = validator.is_valid(value)
        assert actual == expected, label
        checks.append({'label': label, 'expected_valid': expected, 'observed_valid': actual})
    for name in ['metadata', 'payload', 'owned']:
        path = HERE / 'fixtures' / (name + '.json')
        value = json.loads(path.read_text())
        fixtures[name] = value
        check(name + ': complete original context', value, True)
        for key in value['context']:
            changed = copy.deepcopy(value)
            del changed['context'][key]
            check(name + ': missing context field ' + key, changed, False)
        for key in ['schema_version', 'kind', 'context']:
            changed = copy.deepcopy(value)
            del changed[key]
            check(name + ': missing snapshot field ' + key, changed, False)
        changed = copy.deepcopy(value)
        changed['extra'] = True
        check(name + ': extra snapshot field', changed, False)
    metadata = fixtures['metadata']
    for value in [-1, 256, 1.5, '1']:
        changed = copy.deepcopy(metadata)
        changed['context']['records'][0]['artifact']['content'] = [value]
        check('invalid embedded byte ' + repr(value), changed, False)
    changed = copy.deepcopy(metadata)
    changed['context']['records'] *= 2
    check('identical ordered record duplicates allowed', changed, True)
    original_path = ROOT / 'authority/artifact-types/intent-resolution/v1/fixtures/valid/record.json'
    original_bytes = original_path.read_bytes()
    original_record = json.loads(original_bytes)
    for receipt in metadata['context']['records'] + metadata['context']['roots']:
        assert receipt['artifact']['content'] == list(original_bytes)
        assert receipt['artifact']['body'] == original_record
        assert receipt['artifact']['ref']['digest'] == hashlib.sha256(original_bytes).hexdigest()
    report = {'task': 'N01', 'unit': 'K02-catalog-snapshots', 'result': 'decoded-shape-controls-pass',
              'driver': binding(Path(__file__)), 'schema': binding(schema_path),
              'fixtures': [binding(HERE / 'fixtures' / (name + '.json')) for name in fixtures],
              'fixture_generator': binding(HERE / 'EmitCatalogFixtures.lean'),
              'fixture_encoder': binding(HERE / 'CatalogRuntimeEncoding.lean'),
              'original_source_fixture': binding(original_path), 'original_source_bytes': len(original_bytes),
              'original_full_record_and_bytes_retained': True, 'checks': checks,
              'check_count': len(checks), 'raw_schema_equivalence_proved': False,
              'fixture_serializer_proved': False, 'authentic_snapshot_proved': False,
              'inherited_discharges': 0, 'authority_effect': 'none'}
    (HERE / 'schema-validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS:', len(checks), 'decoded shape controls; original complete record/bytes retained.')
if __name__ == '__main__':
    run()
