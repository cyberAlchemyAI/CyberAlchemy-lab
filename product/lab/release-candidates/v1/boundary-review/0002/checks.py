"""Negative privacy/path guards for the selected R06 inspector."""
import base64
import argparse
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('_cal_R06_inspector', HERE / 'review.py')
R = importlib.util.module_from_spec(spec);spec.loader.exec_module(R)


class Checks(unittest.TestCase):
    def raw(self, value):return json.dumps(value).encode()

    def test_01_plain_code_is_not_session_state(self):
        self.assertEqual(R.scan(b"session_memory = 'field name'", 'code'), [])

    def test_02_schema_property_is_a_declaration(self):
        self.assertEqual(R.scan(self.raw({'$schema':'https://json-schema.org/draft/2020-12/schema',
             'properties':{'session_memory':{'type':'string'}}}), 'schema'), [])

    def test_03_actual_session_memory_is_private(self):
        result=R.scan(self.raw({'payload':{'session_memory':'owned-negative-example'}}), 'body')
        self.assertEqual(len(result),1);self.assertEqual(result[0]['selector'],'#/payload/session_memory')
        self.assertNotIn('owned-negative-example',json.dumps(result))

    def test_04_actual_short_memory_is_private(self):
        self.assertEqual(len(R.scan(self.raw({'short_memory':[]}), 'body')),1)

    def test_05_private_key_field_is_private(self):
        self.assertEqual(len(R.scan(self.raw({'private_key_bytes':'example'}), 'body')),1)

    def test_06_literal_private_key_marker_is_refused(self):
        self.assertEqual(len(R.scan(b'-----BEGIN PRIVATE KEY-----\nnegative-example', 'body')),1)

    def test_07_nested_original_envelope_is_inspected(self):
        raw=self.raw({'payload':{'session_memory':None}})
        envelope={'base64_original_bytes':base64.b64encode(raw).decode(),'sha256':R.sha(raw)}
        self.assertTrue(R.scan(self.raw(envelope),'archive'))

    def test_08_nested_original_digest_mismatch_is_refused(self):
        raw=self.raw({'value':1})
        envelope={'base64_original_bytes':base64.b64encode(raw).decode(),'sha256':'0'*64}
        with self.assertRaisesRegex(ValueError,'digest differs'):R.scan(self.raw(envelope),'archive')

    def test_09_embedded_public_snapshot_cannot_hide_memory(self):
        raw=self.raw({'short_memory':None});name='code/body.json'
        value={'schema_version':'lab-exact-public-byte-snapshot/v1-candidate','authority_effect':'none',
               'files':{name:base64.b64encode(raw).decode()},'sha256s':{name:R.sha(raw)}}
        self.assertTrue(R.scan(self.raw(value),'public'))

    def test_10_embedded_byte_dictionary_is_inspected(self):
        raw=self.raw({'session_memory':None})
        self.assertTrue(R.scan(self.raw({'byte_contents':{'body.json':base64.b64encode(raw).decode()}}),'archive'))

    def test_11_traversal_is_refused(self):
        with self.assertRaises(ValueError):R.relative('../key.json')

    def test_12_absolute_path_is_refused(self):
        with self.assertRaises(ValueError):R.relative('/key.json')

    def test_13_environment_and_runtime_paths_are_refused(self):
        for name in ['.env','config/.env.local','.local/session.json','x/__pycache__/cache.pyc','store.sqlite3','secret.pem']:
            with self.subTest(name=name),self.assertRaises(ValueError):R.relative(name)

    def test_14_duplicate_keys_are_refused(self):
        with self.assertRaisesRegex(ValueError,'duplicate'):R.parse(b'{"a":1,"a":2}')

    def test_15_nonfinite_values_are_refused(self):
        with self.assertRaises(ValueError):R.parse(b'{"a":NaN}')

    def test_16_exact_safe_code_path_is_retained(self):
        self.assertEqual(R.relative('implementation/lab-runtime/store.py'),'implementation/lab-runtime/store.py')


    def test_17_actual_migration_visibility_is_preserved(self):
        items=R.parse(R.read(R.MIGRATION))['items']
        self.assertEqual(len(items),140)
        self.assertTrue(all(row['public_body_export_allowed'] is False for row in items))
        self.assertEqual(sum(row['privacy']=='private' for row in items),138)
        self.assertEqual({row['item_id'] for row in items if row['privacy']=='public-scoped-source'},
                         {'dependency:SRC-ARCANUM-INVOKE-DEFINE','dependency:SRC-ARCANUM-CYBERALCHEMY-METHOD'})


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source-sha256',required=True)
    args=parser.parse_args();source=HERE/'source-manifest.json'
    R.need(R.sha(R.read(source))==args.source_sha256,'independent source pin differs')
    manifest=R.parse(R.read(source))
    def guard():
        for row in manifest['files']:R.need(R.bind(R.ROOT/row['path'])==row,'frozen inspection input changed')
    guard();cases=[]
    class Result(unittest.TextTestResult):
        def addSuccess(self,t):super().addSuccess(t);cases.append({'test':t.id(),'result':'PASS'})
        def addFailure(self,t,e):super().addFailure(t,e);cases.append({'test':t.id(),'result':'FAIL'})
        def addError(self,t,e):super().addError(t,e);cases.append({'test':t.id(),'result':'ERROR'})
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Checks)
    R.need(suite.countTestCases()==17,'complete17case suite required')
    result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite);guard()
    report={'result':'PASS' if result.wasSuccessful() and result.testsRun==17 else 'FAIL',
            'tests_run':result.testsRun,'expected_tests':17,'cases':cases,'source_binding':R.bind(source),
            'authority_effect':'none','actual_owner_outcome':None,'task_complete':False}
    R.put(HERE/'receipts/checks-0001.json',report)
    print(json.dumps({'result':report['result'],'tests_run':result.testsRun}),flush=True)
    raise SystemExit(0 if report['result']=='PASS' else 1)


if __name__ == '__main__':main()
