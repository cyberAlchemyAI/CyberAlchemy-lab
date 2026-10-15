"""Primitive checks over retained original bytes and in-memory counterexamples."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
NAME = '_cal_exact_classification_rules_v3'
spec = importlib.util.spec_from_file_location(NAME, HERE / '__init__.py', submodule_search_locations=[str(HERE)])
module = importlib.util.module_from_spec(spec)
sys.modules[NAME] = module
spec.loader.exec_module(module)
E = __import__(NAME + '.engine', fromlist=['*'])


def owned(body, version=None):
    raw = (json.dumps(body, indent=2, sort_keys=True) + '\n').encode()
    return E.ExactRecord(version or body['node_id'] + '@candidate.1', raw, E.sha(raw))


class Rules(unittest.TestCase):
    def setUp(self):
        self.captured = {}
        self.rows = []
        directory = ROOT / 'implementation/lab-workflows/candidates/v1/failures/receipts/0004/observed'
        for kind in ('classification-scheme', 'classification-value', 'failure-occurrence',
                     'operational-observation', 'evidence-set', 'classification-assignment'):
            path, = directory.glob(kind + '-*.json')
            raw = path.read_bytes()
            body = json.loads(raw)
            self.captured[kind] = body
            if kind != 'classification-assignment':
                self.rows.append(E.ExactRecord(body['node_id'] + '@candidate.1', raw, E.sha(raw)))
        self.candidate = copy.deepcopy(self.captured['classification-assignment'])
        self.existing = []
        self.materials = {row.version_ref: row.raw for row in self.rows
                          if row.body()['kind'] in ('operational-observation', 'evidence-set')}
        self.basis = [{'ref': reference, 'sha256': E.sha(raw)} for reference, raw in self.materials.items()]

    def run_evaluation(self):
        payload = self.candidate['payload']
        return E.evaluate(E.ExactRecords(self.rows, self.candidate['scope_ref']),
                          subject_ref=payload['subject_version_ref'], scheme_ref=payload['scheme_version_ref'],
                          value_ref=payload['value_ref'], axis_ref=payload['axis_ref'],
                          candidate=self.candidate, basis_bindings=self.basis,
                          material_bytes=self.materials, existing_assignment_refs=self.existing)

    def change_record(self, kind, mutate):
        row, = [row for row in self.rows if row.body()['kind'] == kind]
        body = row.body()
        mutate(body)
        self.rows[self.rows.index(row)] = owned(body, row.version_ref)

    def agent(self):
        directory = ROOT / 'authority/admissions/first-governed-agent-work-episode/v1/instances/artifacts'
        self.rows = []
        for name in ('agent-instance', 'agent-session', 'classification-scheme', 'classification-value'):
            raw = (directory / (name + '.json')).read_bytes()
            body = json.loads(raw)
            self.rows.append(E.ExactRecord(body['node_id'] + '@candidate.1', raw, E.sha(raw)))
        self.candidate = json.loads((directory / 'classification-assignment.json').read_bytes())
        reference, = self.candidate['payload']['evidence_refs']
        raw = (ROOT / reference).read_bytes()
        self.materials = {reference: raw}
        self.basis = [{'ref': reference, 'sha256': E.sha(raw)}]

    def test_01_actual_W05_original_annotation_rules(self):
        result = self.run_evaluation()
        self.assertEqual(result['result'], 'pass')
        self.assertEqual(len(result['checks']), 2)
        self.assertFalse(result['causality_proven'])
        self.assertFalse(result['runtime_conformance_proven'])
        self.assertEqual(result['authority_effect'], 'none')

    def test_02_wrong_candidate_subject_revision_refused(self):
        self.candidate['payload']['subject_version_ref'] += '.foreign'
        with self.assertRaises(E.Refusal):
            self.run_evaluation()

    def test_03_Value_wrong_Scheme_refused(self):
        self.change_record('classification-value', lambda body: body['payload'].update(scheme_ref='classification-scheme:missing'))
        with self.assertRaises(E.Refusal):
            self.run_evaluation()

    def test_04_cross_axis_Value_refused(self):
        self.change_record('classification-value', lambda body: body['payload'].update(axis_ref='axis:other'))
        with self.assertRaises(E.Refusal):
            self.run_evaluation()

    def test_05_exact_basis_corruption_refused(self):
        reference = self.basis[0]['ref']
        self.materials[reference] += b' '
        with self.assertRaises(E.Refusal):
            self.run_evaluation()

    def test_06_candidate_evidence_outside_basis_refused(self):
        self.basis.pop()
        with self.assertRaises(E.Refusal):
            self.run_evaluation()

    def test_07_existing_active_slot_conflicts(self):
        existing = copy.deepcopy(self.candidate)
        existing['node_id'] += ':existing'
        row = owned(existing)
        self.rows.append(row)
        self.existing.append(row.version_ref)
        self.assertEqual(self.run_evaluation()['result'], 'fail')

    def test_08_independent_axis_does_not_collapse_into_same_slot(self):
        second = copy.deepcopy(self.captured['classification-value'])
        second['node_id'] += ':independent'
        second['payload']['axis_ref'] = 'axis:independent'
        value = owned(second)
        self.rows.append(value)
        def extend(body):
            body['payload']['axis_refs'].append('axis:independent')
            body['payload']['value_refs'].append(value.version_ref)
        self.change_record('classification-scheme', extend)
        existing = copy.deepcopy(self.candidate)
        existing['node_id'] += ':other-axis'
        existing['payload'].update(axis_ref='axis:independent', value_ref=value.version_ref)
        row = owned(existing)
        self.rows.append(row)
        self.existing.append(row.version_ref)
        self.assertEqual(self.run_evaluation()['result'], 'pass')

    def test_09_unknown_rule_is_not_evaluable(self):
        self.change_record('classification-scheme', lambda body: body['payload']['compatibility_rules'].append('unknown-rule'))
        result = self.run_evaluation()
        self.assertEqual(result['result'], 'not-evaluable')
        self.assertEqual(result['checks'][-1]['rule'], 'unknown-rule')

    def test_10_unknown_existing_status_is_not_evaluable(self):
        existing = copy.deepcopy(self.candidate)
        existing['node_id'] += ':unknown-status'
        existing['payload']['status'] = 'undefined-status'
        row = owned(existing)
        self.rows.append(row)
        self.existing.append(row.version_ref)
        self.assertEqual(self.run_evaluation()['result'], 'not-evaluable')

    def test_11_ambiguous_identity_refused(self):
        value, = [row for row in self.rows if row.body()['kind'] == 'classification-value']
        self.rows.append(owned(value.body(), value.version_ref + '.second'))
        self.candidate['payload']['value_ref'] = value.body()['node_id']
        with self.assertRaises(E.Refusal):
            self.run_evaluation()

    def test_12_foreign_scope_refused(self):
        self.change_record('classification-value', lambda body: body.update(scope_ref='scope:foreign'))
        with self.assertRaises(E.Refusal):
            self.run_evaluation()

    def test_13_candidate_authority_refused(self):
        self.candidate['authority_effect'] = 'grant'
        with self.assertRaises(E.Refusal):
            self.run_evaluation()

    def test_14_actual_Agent_declaration_has_no_runtime_proof(self):
        self.agent()
        result = self.run_evaluation()
        self.assertEqual(result['result'], 'pass')
        self.assertEqual(len(result['checks']), 3)
        self.assertFalse(result['runtime_conformance_proven'])
        self.assertIsNone(result['actual_owner_outcome'])

    def test_15_Agent_identity_reuse_conflicts(self):
        self.agent()
        session, = [row for row in self.rows if row.body()['kind'] == 'agent-session']
        body = session.body()
        body['node_id'] += ':another'
        self.rows.append(owned(body))
        self.assertEqual(self.run_evaluation()['result'], 'fail')

    def test_16_Session_memory_boundary_conflicts(self):
        self.agent()
        self.change_record('agent-session', lambda body: body['payload']['session_memory'].update(expires_with_session=False))
        self.assertEqual(self.run_evaluation()['result'], 'fail')

    def test_17_retained_records_and_candidate_are_not_mutated(self):
        before = tuple(self.rows), copy.deepcopy(self.candidate), copy.deepcopy(self.basis), self.materials.copy()
        self.run_evaluation()
        self.assertEqual(before, (tuple(self.rows), self.candidate, self.basis, self.materials))

    def test_18_record_hash_corruption_refused(self):
        row = self.rows[0]
        self.rows[0] = E.ExactRecord(row.version_ref, row.raw + b' ', row.byte_sha256)
        with self.assertRaises(E.Refusal):
            self.run_evaluation()


    def test_19_duplicate_top_level_member_refused(self):
        row = self.rows[0]
        raw = b'{"scope_ref":"scope:foreign",' + row.raw.lstrip()[1:]
        self.rows[0] = E.ExactRecord(row.version_ref, raw, E.sha(raw))
        with self.assertRaisesRegex(E.Refusal, 'duplicate JSON member'):
            self.run_evaluation()

    def test_20_duplicate_nested_rule_member_refused(self):
        row, = [row for row in self.rows if row.body()['kind'] == 'classification-scheme']
        needle = b'"payload": {'
        replacement = b'"payload": {"compatibility_rules":["unknown-rule"],'
        self.assertEqual(row.raw.count(needle), 1)
        raw = row.raw.replace(needle, replacement)
        self.rows[self.rows.index(row)] = E.ExactRecord(row.version_ref, raw, E.sha(raw))
        with self.assertRaisesRegex(E.Refusal, 'duplicate JSON member'):
            self.run_evaluation()

    def test_21_nonfinite_JSON_token_refused(self):
        row = self.rows[0]
        raw = b'{"owned_probe":NaN,' + row.raw.lstrip()[1:]
        self.rows[0] = E.ExactRecord(row.version_ref, raw, E.sha(raw))
        with self.assertRaisesRegex(E.Refusal, 'nonfinite JSON token'):
            self.run_evaluation()


    def original_product(self):
        mapping=json.loads((HERE.parent/'current-mapped-context-v3/packages/0001/mapping.json').read_bytes())
        header=copy.deepcopy(next(r['artifact'] for r in mapping['rows'] if r['artifact']['identity_ref']=='product:cyberalchemy-lab'))
        raw=(HERE.parent/'current-participation-v4/packages/0001/setup-artifacts/product.json').read_bytes()
        self.assertEqual(E.sha(raw),header['byte_sha256'])
        return E.TypedRecord(header['version_ref'],raw,E.sha(raw),header)

    def annotate_product(self):
        row=self.original_product();self.rows.append(row)
        self.candidate['payload'].update(subject_ref=row.header['identity_ref'],subject_version_ref=row.version_ref)
        return row

    def test_22_original_Product_carrier_annotation(self):
        row=self.annotate_product();result=self.run_evaluation()
        self.assertEqual(result['result'],'pass')
        self.assertEqual(row.identity(),'product:cyberalchemy-lab')
        self.assertEqual(row.semantic_kind(),'product-identity')
        self.assertNotIn('node_id',row.body())

    def test_23_Product_domain_scope_is_not_authority_scope(self):
        row=self.annotate_product();body=row.body()
        self.assertIsInstance(body['scope'],dict);self.assertNotIn('scope_ref',body)
        self.assertEqual(row.selection_scope(),self.candidate['scope_ref'])
        self.assertEqual(self.run_evaluation()['result'],'pass')

    def test_24_inline_model_version_is_not_header_revision(self):
        row=self.annotate_product();self.assertEqual(row.body()['version'],'2.0.0-foundation.1')
        self.assertNotEqual(row.version_ref,row.identity()+'@'+row.body()['version'])
        self.assertEqual(self.run_evaluation()['result'],'pass')

    def test_25_declared_Product_identity_mismatch_refused(self):
        row=self.original_product();header=copy.deepcopy(row.header);header['identity_ref']='product:foreign'
        with self.assertRaises(ValueError):E.TypedRecord(row.version_ref,row.raw,row.byte_sha256,header).body()

    def test_26_exact_Product_header_digest_mismatch_refused(self):
        row=self.original_product();header=copy.deepcopy(row.header);header['byte_sha256']='0'*64
        with self.assertRaises(ValueError):E.TypedRecord(row.version_ref,row.raw,row.byte_sha256,header).body()

    def test_27_sixth_header_axis_refused(self):
        row=self.original_product();header=copy.deepcopy(row.header);header['candidate_contract_binding']={'ref':'schema','sha256':'0'*64}
        with self.assertRaises(ValueError):E.TypedRecord(row.version_ref,row.raw,row.byte_sha256,header).body()

    def test_28_unselected_carrier_refused(self):
        row=self.original_product();header=copy.deepcopy(row.header);header['carrier_ref']='cal.artifact-type.unselected/v1'
        with self.assertRaisesRegex(ValueError,'no explicitly selected identity contract'):E.TypedRecord(row.version_ref,row.raw,row.byte_sha256,header).body()

    def test_29_duplicate_original_Product_member_refused(self):
        row=self.original_product();raw=b'{"product_id":"product:foreign",'+row.raw.lstrip()[1:]
        header=copy.deepcopy(row.header);header['byte_sha256']=E.sha(raw)
        with self.assertRaisesRegex(ValueError,'duplicate JSON member'):E.TypedRecord(row.version_ref,raw,E.sha(raw),header).body()

    def test_30_original_Product_schema_forbids_synthetic_node(self):
        row=self.original_product();body=row.body();body['node_id']=row.identity()
        raw=json.dumps(body).encode();header=copy.deepcopy(row.header);header['byte_sha256']=E.sha(raw)
        with self.assertRaisesRegex(ValueError,'original carrier schema refused'):E.TypedRecord(row.version_ref,raw,E.sha(raw),header).body()

    def test_31_node_carrier_uses_its_declared_identity(self):
        row,=[r for r in self.rows if r.body()['kind']=='classification-scheme']
        header={'scope_ref':self.candidate['scope_ref'],'identity_ref':row.body()['node_id'],
                'version_ref':row.version_ref,'carrier_ref':'cal.artifact-type.classification-scheme/v1','byte_sha256':row.byte_sha256}
        typed=E.TypedRecord(row.version_ref,row.raw,row.byte_sha256,header)
        self.assertEqual(typed.body(),row.body());self.assertEqual(typed.identity(),row.body()['node_id'])

    def test_32_node_carrier_authority_scope_mismatch_refused(self):
        row,=[r for r in self.rows if r.body()['kind']=='classification-scheme']
        header={'scope_ref':'scope:foreign','identity_ref':row.body()['node_id'],'version_ref':row.version_ref,
                'carrier_ref':'cal.artifact-type.classification-scheme/v1','byte_sha256':row.byte_sha256}
        with self.assertRaisesRegex(ValueError,'authority scope differs'):E.TypedRecord(row.version_ref,row.raw,row.byte_sha256,header).body()

    def test_33_Product_header_cannot_enter_another_selected_scope(self):
        row=self.original_product();header=copy.deepcopy(row.header);header['scope_ref']='scope:foreign'
        typed=E.TypedRecord(row.version_ref,row.raw,row.byte_sha256,header)
        with self.assertRaisesRegex(E.Refusal,'selected record scope differs'):E.ExactRecords([typed],self.candidate['scope_ref'])

    def test_34_carrier_revision_must_qualify_declared_identity(self):
        row=self.original_product();header=copy.deepcopy(row.header);header['version_ref']='product:another@candidate.1'
        with self.assertRaisesRegex(ValueError,'revision does not qualify'):E.TypedRecord(header['version_ref'],row.raw,row.byte_sha256,header).body()

    def test_35_original_carrier_and_scope_are_not_mutated(self):
        row=self.annotate_product();before=row.raw,copy.deepcopy(row.header),row.body()
        self.run_evaluation();self.assertEqual(before,(row.raw,row.header,row.body()))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-sha256', required=True)
    args = parser.parse_args()
    source = HERE / 'source-manifest.json'
    assert E.sha(source.read_bytes()) == args.source_sha256
    manifest = json.loads(source.read_bytes())
    def guard():
        for row in manifest['files']:
            path = ROOT / row['path']
            assert path.is_file() and not path.is_symlink() and E.sha(path.read_bytes()) == row['sha256'], row['path']
    guard()
    cases = []
    class Result(unittest.TextTestResult):
        def addSuccess(self, test):
            super().addSuccess(test)
            cases.append({'test': test.id(), 'result': 'PASS'})
        def addFailure(self, test, error):
            super().addFailure(test, error)
            cases.append({'test': test.id(), 'result': 'FAIL', 'detail': self._exc_info_to_string(error, test)})
        def addError(self, test, error):
            super().addError(test, error)
            cases.append({'test': test.id(), 'result': 'ERROR', 'detail': self._exc_info_to_string(error, test)})
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Rules)
    assert suite.countTestCases() == 35
    result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(suite)
    guard()
    report = {'schema_version': 'lab-classification-rule-tests/v1-candidate',
              'result': 'PASS' if result.wasSuccessful() and result.testsRun == 35 else 'FAIL',
              'tests_run': result.testsRun, 'expected_tests': 35, 'cases': cases,
              'source_sha256': args.source_sha256, 'public_API_qualified': False,
              'runtime_conformance_proven': False, 'actual_owner_outcome': None,
              'authority_effect': 'none', 'task_complete': False}
    output = HERE / 'receipts'
    output.mkdir(mode=0o700, exist_ok=True)
    with (output / 'checks-0001.json').open('x') as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': report['result'], 'tests_run': result.testsRun}), flush=True)
    raise SystemExit(0 if report['result'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
