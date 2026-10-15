"""Original-schema checks for the explicit public/candidate reference boundary."""
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
INTERFACE = ROOT / 'product/lab/release-candidates/v1/interface'
API = INTERFACE / 'api-v37'
PARENT = INTERFACE / 'api-v36'
COMPOSITION = INTERFACE / 'classification-preparation-v2'
SCHEMAS = ROOT / 'docs/proposals/0007-lab-integrated-schema-package'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def methods(path):
    return {node.name: ast.dump(node, include_attributes=False)
            for node in ast.walk(ast.parse(path.read_bytes()))
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')}


def main():
    assert not (API / 'source-manifest.json').exists()
    resources = module('_cal_API37_original_reference_resources', SCHEMAS / 'resources.py')
    registry = resources.build_registry()
    common = json.loads((SCHEMAS / 'schemas/common.schema.json').read_bytes())
    public = Draft202012Validator(common['$defs']['artifact_ref'], registry=registry)
    candidate = Draft202012Validator(common['$defs']['candidate_artifact_ref'], registry=registry)
    preparation = module('_cal_API37_public_reference_unit_composition', COMPOSITION / 'preparation.py')
    files = [Path(__file__).resolve(), COMPOSITION / 'preparation.py', API / 'auth.py',
             API / 'classification_fixture.py', API / 'source_bridge.py', SCHEMAS / 'resources.py',
             SCHEMAS / 'schemas/common.schema.json']
    method_count = 0
    for path in PARENT.rglob('*.py'):
        if 'receipts' in path.parts or '__pycache__' in path.parts or path.name == 'freeze_classification.py':
            continue
        if methods(path):
            current = API / path.relative_to(PARENT)
            assert methods(current) == methods(path)
            method_count += len(methods(path))
            files.extend([path, current])
    assert method_count == 275
    rows = {bind(path)['path']: bind(path) for path in files}
    inputs = RUN / 'API37-public-reference-inputs-0001.json'
    with inputs.open('x') as stream:
        json.dump({'files': [rows[key] for key in sorted(rows)], 'authority_effect': 'none'}, stream, indent=2, sort_keys=True)
        stream.write('\n')
    cases = []

    class Checks(unittest.TestCase):
        def setUp(self):
            # Synthetic schema-only values, never a runtime source or grant.
            self.header = {'scope_ref': 'scope:unit', 'identity_ref': 'scheme:unit',
                           'version_ref': 'scheme:unit@1',
                           'carrier_ref': 'cal.artifact-type.classification-scheme/v1',
                           'byte_sha256': '0' * 64,
                           'candidate_contract_binding': {'ref': 'schema:unit', 'sha256': '1' * 64}}

        def test_01_original_public_schema_refuses_candidate_metadata(self):
            self.assertFalse(public.is_valid(self.header))
            self.assertEqual([error.validator for error in public.iter_errors(self.header)], ['additionalProperties'])

        def test_02_exact_public_projection_passes_original_schema(self):
            projected = preparation.public_artifact_ref(self.header)
            self.assertTrue(public.is_valid(projected))
            self.assertEqual(len(projected), 5)

        def test_03_original_candidate_header_stays_valid(self):
            self.assertTrue(candidate.is_valid(self.header))
            saved = copy.deepcopy(self.header)
            preparation.public_artifact_ref(self.header)
            self.assertEqual(self.header, saved)
            self.assertTrue(candidate.is_valid(self.header))

        def test_04_unknown_reference_authority_field_refused(self):
            self.header['owner_authority'] = True
            with self.assertRaisesRegex(ValueError, 'undeclared artifact reference'):
                preparation.public_artifact_ref(self.header)

        def test_05_every_original_reference_field_required(self):
            for key in preparation.PUBLIC_REF_FIELDS:
                header = copy.deepcopy(self.header)
                del header[key]
                with self.subTest(key=key), self.assertRaises(ValueError):
                    preparation.public_artifact_ref(header)

        def test_06_unknown_candidate_binding_field_refused(self):
            self.header['candidate_contract_binding']['authority'] = 'owner'
            with self.assertRaisesRegex(ValueError, 'binding shape'):
                preparation.public_artifact_ref(self.header)

        def test_07_public_header_identity_preserved(self):
            del self.header['candidate_contract_binding']
            self.assertEqual(preparation.public_artifact_ref(self.header), self.header)

        def test_08_original_schema_rejects_bad_digest_after_projection(self):
            self.header['byte_sha256'] = 'not-a-digest'
            self.assertFalse(public.is_valid(preparation.public_artifact_ref(self.header)))

        def test_09_exact_identity_and_revision_are_not_normalized(self):
            projected = preparation.public_artifact_ref(self.header)
            for key in preparation.PUBLIC_REF_FIELDS:
                self.assertEqual(projected[key], self.header[key])

        def test_10_current_qualified_period_selected(self):
            text = (API / 'auth.py').read_text()
            self.assertEqual(text.count('current-participation-v4/packages/0001/period.json'), 1)
            self.assertNotIn('current-participation-v3/packages/0001/period.json', text)

        def test_11_successor_context_namespace_distinct(self):
            text = (API / 'source_bridge.py').read_text()
            self.assertIn('_cal_api_v37_custody_context_v8', text)
            self.assertNotIn('_cal_api_v36_custody_context_v8', text)

        def test_12_all275_original_method_ASTs_preserved(self):
            self.assertEqual(method_count, 275)

    class Result(unittest.TextTestResult):
        def addSuccess(self, test):
            super().addSuccess(test)
            cases.append({'test': test.id(), 'result': 'PASS'})
        def addFailure(self, test, error):
            super().addFailure(test, error)
            cases.append({'test': test.id(), 'result': 'FAIL'})
        def addError(self, test, error):
            super().addError(test, error)
            cases.append({'test': test.id(), 'result': 'ERROR'})

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Checks)
    assert suite.countTestCases() == 12
    result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(suite)
    report = {'schema_version': 'lab-original-public-reference-checks/v1-candidate',
              'result': 'PASS' if result.wasSuccessful() else 'FAIL',
              'tests_run': result.testsRun, 'expected_tests': 12, 'cases': cases,
              'input_binding': bind(inputs), 'original_method_ASTs_preserved': 275,
              'original_public_schema_widened': False, 'host_imports': 0,
              'public_calls': 0, 'source_frozen': False, 'runtime_qualified': False,
              'authority_effect': 'none', 'actual_owner_outcome': None}
    with (RUN / 'API37-public-reference-checks-0001.json').open('x') as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': report['result'], 'tests_run': result.testsRun,
                      'original_method_ASTs_preserved': 275}), flush=True)
    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__ == '__main__':
    main()
