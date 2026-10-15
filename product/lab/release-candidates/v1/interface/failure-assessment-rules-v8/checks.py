"""Complete isolated original-schema/reference/evidence rule cases."""
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


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()


class Rules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('_cal_failure_rules_actual_checks', HERE / 'engine.py')
        cls.E = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.E
        spec.loader.exec_module(cls.E)
        cls.rules = cls.E.AssessmentRules(PIN)

    def fixture(self, kind, name):
        body = json.loads((ROOT / 'authority/artifact-types' / kind / 'v1/fixtures/valid/record.json').read_bytes())
        body.update(node_id=kind + ':' + name, scope_ref='scope:failure-rule-fixture',
                    lifecycle_state='candidate', authority_effect='none', evidence_refs=[], successor_refs=[])
        return body

    def record(self, body):
        raw = encoded(body)
        return self.E.Record({'scope_ref':body['scope_ref'], 'identity_ref':body['node_id'],
            'version_ref':body['node_id']+'@candidate.1', 'carrier_ref':'cal.artifact-type.'+body['kind']+'/v1',
            'byte_sha256':self.E.sha(raw)}, raw)

    def replace(self, kind, change):
        index = next(i for i, r in enumerate(self.records) if json.loads(r.raw)['kind'] == kind)
        body = json.loads(self.records[index].raw)
        change(body)
        self.records[index] = self.record(body)
        return self.records[index]

    def setUp(self):
        self.materials = {'evidence:failure-original': b'Explicit synthetic original-byte evidence fixture; no execution occurred.\n'}
        self.binding = {'ref':'evidence:failure-original', 'sha256':self.E.sha(self.materials['evidence:failure-original'])}
        subject = self.fixture('implementation', 'subject')
        occurrence = self.fixture('failure-occurrence', 'occurrence')
        occurrence['payload'].update(subject_ref=subject['node_id']+'@candidate.1',
            expected_boundary_ref='contract:valid-candidate-preparation', observed_manifestations=['Preparation refused'],
            detection_evidence_refs=[self.binding['ref']], cause_posture='unresolved', recovery_posture='not-attempted')
        mode = self.fixture('failure-mode', 'mode')
        mode['payload'].update(subject_kind_ref='implementation', expected_boundary_ref=occurrence['payload']['expected_boundary_ref'])
        scheme = self.fixture('classification-scheme', 'scheme')
        scheme['payload'].update(axis_refs=['axis:failure-manifestation'], value_refs=['classification-value:value@candidate.1'],
            cardinality_rules=['one-active-value-per-subject-axis'], compatibility_rules=['annotation-never-grants-authority'])
        value = self.fixture('classification-value', 'value')
        value['payload'].update(scheme_ref=scheme['node_id']+'@candidate.1', axis_ref='axis:failure-manifestation',
            definition_ref=mode['node_id']+'@candidate.1')
        assignment = self.fixture('classification-assignment', 'assignment')
        assignment['payload'].update(subject_ref=occurrence['node_id'], subject_version_ref=occurrence['node_id']+'@candidate.1',
            scheme_version_ref=scheme['node_id']+'@candidate.1', value_ref=value['node_id']+'@candidate.1',
            axis_ref='axis:failure-manifestation', status='candidate-annotation', evidence_refs=[self.binding['ref']])
        cause = self.fixture('hypothesis', 'cause')
        cause['payload'].update(disposition='open')
        assessment = self.fixture('failure-assessment', 'assessment')
        assessment['payload'].update(occurrence_ref=occurrence['node_id']+'@candidate.1',
            mode_assignment_ref=assignment['node_id']+'@candidate.1', cause_hypothesis_refs=[cause['node_id']+'@candidate.1'],
            occurrence_posture='supported-controlled', mode_posture='proposed-manifestation', impact_posture='bounded-authored',
            containment_posture='stopped-before-publication', recovery_posture='not-attempted',
            uncertainty_refs=['uncertainty:cause-unconfirmed'])
        assessment['evidence_refs']=[self.binding['ref']]
        assessment['relation_refs']=[{'relation_kind_ref':'relation.evaluates','direction':'source',
            'counterpart_kind':'failure-occurrence','counterpart_ref':occurrence['node_id']+'@candidate.1'}]
        self.records = [self.record(b) for b in (subject, occurrence, mode, scheme, value, assignment, cause)]
        self.candidate = self.record(assessment)
        self.request = json.loads((ROOT/'docs/proposals/0007-lab-integrated-schema-package/examples/failure-assessment-request.json').read_bytes())
        self.request.update(occurrence=copy.deepcopy(self.records[1].header), mode_assignment=copy.deepcopy(self.records[5].header),
            cause_hypothesis_refs=[copy.deepcopy(self.records[6].header)], evidence_bindings=[copy.deepcopy(self.binding)],
            assessment_candidate_binding={'ref':'candidate:failure-assessment','sha256':self.E.sha(self.candidate.raw)},
            incident_threshold_binding=None)
        self.basis={'schema_version':'lab-failure-assessment-basis/v1-candidate', 'scope_ref':assessment['scope_ref'],
            'source_cut':copy.deepcopy(self.request['source_cut']), 'assessment_binding':copy.deepcopy(self.request['assessment_candidate_binding']),
            'axis_basis':{a:[copy.deepcopy(self.binding)] for a in self.E.AXES}, 'authority_effect':'none','actual_owner_outcome':None}
        self.threshold = None

    def check(self):
        raw=encoded(self.basis)
        return self.rules.evaluate(self.records,self.request,self.candidate,
            basis_binding={'ref':'candidate:failure-basis','sha256':self.E.sha(raw)}, basis_raw=raw,
            material_bytes=self.materials, selected_threshold_binding=self.threshold)

    def candidate_change(self, change):
        body=json.loads(self.candidate.raw);change(body);self.candidate=self.record(body)
        self.request['assessment_candidate_binding']['sha256']=self.E.sha(self.candidate.raw)
        self.basis['assessment_binding']=copy.deepcopy(self.request['assessment_candidate_binding'])

    def policy(self, minimum=1, rule='minimum-evidenced-occurrences'):
        value={'schema_version':'lab-failure-incident-threshold/v1-candidate', 'scope_ref':self.basis['scope_ref'],
            'source_cut':copy.deepcopy(self.request['source_cut']), 'rule':rule,
            'occurrences':[copy.deepcopy(self.request['occurrence'])], 'minimum_count':minimum,
            'authority_effect':'none','actual_owner_outcome':None}
        self.select_policy(value)
        return value

    def select_policy(self, value):
        raw=encoded(value);self.materials['policy:threshold']=raw
        self.threshold={'ref':'policy:threshold','sha256':self.E.sha(raw)}
        self.request['incident_threshold_binding']=copy.deepcopy(self.threshold)

    def test_01_original_request_and_carrier_positive(self):
        result=self.check();self.assertEqual(result['result'],'pass')
        self.assertEqual(result['axis_claims']['recovery'],'not-attempted')
        self.assertFalse(result['confirmed_cause_inferred']);self.assertFalse(result['whole_API_qualified'])

    def test_02_recovery_coexists_with_unresolved_cause(self):
        self.candidate_change(lambda b:b['payload'].update(recovery_posture='recovered-with-residue'))
        result=self.check();self.assertEqual(result['result'],'pass')
        self.assertEqual(result['axis_claims']['cause'],['hypothesis:cause@candidate.1'])
        self.assertFalse(result['confirmed_cause_inferred']);self.assertFalse(result['recovery_or_control_effectiveness_inferred'])

    def test_03_mode_does_not_supply_impact(self):
        self.candidate_change(lambda b:b['payload'].update(impact_posture='not-assessed'))
        self.assertEqual(self.check()['axis_claims']['impact'],'not-assessed')

    def test_04_unknown_classification_rule_not_evaluable(self):
        self.replace('classification-scheme',lambda b:b['payload']['compatibility_rules'].append('unselected-rule'))
        self.assertEqual(self.check()['result'],'not-evaluable')

    def test_05_threshold_pass_creates_no_Incident(self):
        self.policy();r=self.check();self.assertEqual(r['result'],'pass')
        self.assertFalse(r['incident_threshold']['Incident_created']);self.assertFalse(r['incident_threshold']['production_applicability_inferred'])

    def test_06_threshold_miss_preserves_assessment_axes(self):
        self.policy(2);r=self.check();self.assertEqual(r['result'],'pass')
        self.assertEqual(r['incident_threshold']['result'],'fail')
        self.assertFalse(r['incident_threshold']['eligible_under_declared_rule'])
        self.assertEqual(r['axis_claims']['occurrence'],'supported-controlled')

    def test_07_unknown_threshold_not_evaluable(self):
        self.policy(rule='impact-implies-production-Incident');self.assertEqual(self.check()['result'],'not-evaluable')

    def test_08_threshold_not_host_selected_refused(self):
        self.policy();self.threshold=None
        with self.assertRaises(self.E.Refusal):self.check()

    def test_09_wrong_occurrence_digest_refused(self):
        self.request['occurrence']['byte_sha256']='0'*64
        with self.assertRaises(self.E.Refusal):self.check()

    def test_10_other_occurrence_annotation_refused(self):
        self.request['mode_assignment']=copy.deepcopy(self.replace('classification-assignment',lambda b:b['payload'].update(subject_version_ref='failure-occurrence:other@1')).header)
        with self.assertRaises(self.E.Refusal):self.check()

    def test_11_inactive_annotation_refused(self):
        self.request['mode_assignment']=copy.deepcopy(self.replace('classification-assignment',lambda b:b['payload'].update(status='expired')).header)
        with self.assertRaises(self.E.Refusal):self.check()

    def test_12_other_mode_boundary_refused(self):
        self.replace('failure-mode',lambda b:b['payload'].update(expected_boundary_ref='contract:another'))
        with self.assertRaises(self.E.Refusal):self.check()

    def test_13_wrong_subject_kind_refused(self):
        self.replace('failure-mode',lambda b:b['payload'].update(subject_kind_ref='product'))
        with self.assertRaises(self.E.Refusal):self.check()

    def test_14_wrong_cause_kind_refused(self):
        self.request['cause_hypothesis_refs']=[copy.deepcopy(self.records[2].header)]
        with self.assertRaises(self.E.Refusal):self.check()

    def test_15_missing_cause_refused(self):
        self.request['cause_hypothesis_refs'][0]['version_ref']='hypothesis:missing@1'
        with self.assertRaises(self.E.Refusal):self.check()

    def test_16_duplicate_cause_refused(self):
        self.request['cause_hypothesis_refs']*=2
        with self.assertRaises(self.E.Refusal):self.check()

    def test_17_other_assessment_occurrence_refused(self):
        self.candidate_change(lambda b:b['payload'].update(occurrence_ref='failure-occurrence:other@1'))
        with self.assertRaises(self.E.Refusal):self.check()

    def test_18_changed_evidence_bytes_refused(self):
        self.materials[self.binding['ref']]+=b'changed'
        with self.assertRaises(self.E.Refusal):self.check()

    def test_19_missing_detection_evidence_refused(self):
        self.request['occurrence']=copy.deepcopy(self.replace('failure-occurrence',lambda b:b['payload'].update(detection_evidence_refs=[])).header)
        with self.assertRaises(self.E.Refusal):self.check()

    def test_20_missing_manifestation_refused(self):
        self.request['occurrence']=copy.deepcopy(self.replace('failure-occurrence',lambda b:b['payload'].update(observed_manifestations=[])).header)
        with self.assertRaises(self.E.Refusal):self.check()

    def test_21_unbound_axis_evidence_refused(self):
        self.basis['axis_basis']['recovery']=[{'ref':'evidence:missing','sha256':'0'*64}]
        with self.assertRaises(self.E.Refusal):self.check()

    def test_22_missing_independent_axis_refused(self):
        del self.basis['axis_basis']['containment']
        with self.assertRaises(self.E.Refusal):self.check()

    def test_23_other_basis_cut_refused(self):
        self.basis['source_cut']['commit_sequence']+=1
        with self.assertRaises(self.E.Refusal):self.check()

    def test_24_other_basis_assessment_refused(self):
        self.basis['assessment_binding']['sha256']='0'*64
        with self.assertRaises(self.E.Refusal):self.check()

    def test_25_duplicate_exact_record_refused(self):
        self.records.append(self.records[0])
        with self.assertRaises(self.E.Refusal):self.check()

    def test_26_another_scope_refused(self):
        self.replace('hypothesis',lambda b:b.update(scope_ref='scope:foreign'))
        with self.assertRaises(self.E.Refusal):self.check()

    def test_27_original_candidate_schema_extra_field_refused(self):
        self.candidate_change(lambda b:b['payload'].update(confirmed_cause=True))
        with self.assertRaises(self.E.Refusal):self.check()

    def test_28_claimed_authority_refused(self):
        self.candidate_change(lambda b:b.update(authority_effect='admitted'))
        with self.assertRaises(self.E.Refusal):self.check()

    def test_29_active_candidate_refused(self):
        self.candidate_change(lambda b:b.update(lifecycle_state='active'))
        with self.assertRaises(self.E.Refusal):self.check()

    def test_30_sixth_public_header_axis_refused(self):
        self.request['occurrence']['candidate_contract_binding']={'ref':'schema','sha256':'0'*64}
        with self.assertRaises(self.E.Refusal):self.check()

    def test_31_source_selection_wrong_pin_refused(self):
        with self.assertRaises(self.E.Refusal):self.E.AssessmentRules('0'*64)

    def test_32_duplicate_JSON_member_refused(self):
        with self.assertRaises(self.E.Refusal):self.E.parse(b'{"axis":1,"axis":2}')

    def test_33_nonfinite_JSON_refused(self):
        for raw in (b'{"x":NaN}',b'{"x":Infinity}',b'{"x":1e999}'):
            with self.subTest(raw=raw),self.assertRaises(self.E.Refusal):self.E.parse(raw)

    def test_34_threshold_duplicate_cohort_refused(self):
        p=self.policy();p['occurrences']*=2;self.select_policy(p)
        with self.assertRaises(self.E.Refusal):self.check()

    def test_35_threshold_foreign_cut_refused(self):
        p=self.policy();p['source_cut']['commit_sequence']+=1;self.select_policy(p)
        with self.assertRaises(self.E.Refusal):self.check()

    def test_36_threshold_unknown_field_refused(self):
        p=self.policy();p['activate_incident_response']=True;self.select_policy(p)
        with self.assertRaises(self.E.Refusal):self.check()

    def test_37_original_public_request_extra_authority_refused(self):
        self.request['owner_outcome']='admitted'
        with self.assertRaises(self.E.Refusal):self.check()

    def test_38_candidate_original_byte_binding_refused(self):
        self.request['assessment_candidate_binding']['sha256']='0'*64
        with self.assertRaises(self.E.Refusal):self.check()

    def test_39_missing_subject_refused(self):
        del self.records[0]
        with self.assertRaises(self.E.Refusal):self.check()

    def test_40_cause_set_cannot_disappear_from_candidate(self):
        self.candidate_change(lambda b:b['payload'].update(cause_hypothesis_refs=[]))
        with self.assertRaises(self.E.Refusal):self.check()

    def test_41_distinct_axis_evidence_remains_distinct(self):
        raw=b'Separate synthetic recovery observation; not a confirmed cause.\n'
        self.materials['evidence:recovery-original']=raw
        binding={'ref':'evidence:recovery-original','sha256':self.E.sha(raw)}
        self.request['evidence_bindings'].append(binding)
        self.basis['axis_basis']['recovery']=[binding]
        result=self.check();self.assertEqual(result['result'],'pass')
        self.assertNotEqual(result['axis_basis']['cause'],result['axis_basis']['recovery'])

    def test_42_result_does_not_mutate_selected_inputs(self):
        before=copy.deepcopy((self.request,self.basis,self.candidate.header,self.materials))
        self.check();self.assertEqual(before,(self.request,self.basis,self.candidate.header,self.materials))

    def test_43_duplicate_active_assignment_fails_declared_cardinality(self):
        body=json.loads(self.records[5].raw);body['node_id']='classification-assignment:other'
        self.records.append(self.record(body));self.assertEqual(self.check()['result'],'fail')

    def test_44_evidence_graph_reaches_exact_original_material(self):
        body=self.fixture('evidence-set','observation-closure')
        body['payload'].update(source_refs=[self.binding['ref']],item_refs=[self.binding['ref']])
        item=self.record(body);self.records.append(item)
        self.request['occurrence']=copy.deepcopy(self.replace('failure-occurrence',lambda b:b['payload'].update(detection_evidence_refs=[item.header['version_ref']])).header)
        self.assertEqual(self.check()['result'],'pass')

    def test_45_evidence_cycle_without_original_source_refused(self):
        body=self.fixture('evidence-set','cycle');body['payload'].update(source_refs=['evidence-set:cycle@candidate.1'],item_refs=['evidence-set:cycle@candidate.1'])
        item=self.record(body);self.records.append(item)
        self.request['occurrence']=copy.deepcopy(self.replace('failure-occurrence',lambda b:b['payload'].update(detection_evidence_refs=[item.header['version_ref']])).header)
        with self.assertRaisesRegex(self.E.Refusal,'cyclic evidence'):self.check()

    def test_46_threshold_boolean_count_refused(self):
        policy=self.policy();policy['minimum_count']=True;self.select_policy(policy)
        with self.assertRaises(self.E.Refusal):self.check()


    def test_47_missed_threshold_does_not_change_cause_or_recovery(self):
        before=self.check()['axis_claims'];self.policy(3)
        result=self.check();self.assertEqual(result['result'],'pass')
        self.assertEqual(result['axis_claims'],before)
        self.assertFalse(result['incident_threshold']['Incident_created'])

    def test_48_unknown_threshold_has_no_fabricated_eligibility(self):
        self.policy(rule='unselected-threshold-evaluator');result=self.check()
        self.assertEqual(result['result'],'not-evaluable')
        self.assertIsNone(result['incident_threshold']['eligible_under_declared_rule'])

    def test_49_classification_failure_is_still_a_failure_when_threshold_met(self):
        self.policy();body=json.loads(self.records[5].raw)
        body['node_id']='classification-assignment:conflicting';self.records.append(self.record(body))
        result=self.check();self.assertEqual(result['result'],'fail')
        self.assertTrue(result['incident_threshold']['eligible_under_declared_rule'])

    def test_50_met_threshold_does_not_confirm_cause(self):
        self.policy();result=self.check()
        self.assertTrue(result['incident_threshold']['eligible_under_declared_rule'])
        self.assertFalse(result['confirmed_cause_inferred'])
        self.assertEqual(result['axis_claims']['uncertainty'],['uncertainty:cause-unconfirmed'])

    def test_51_null_threshold_does_not_supply_incident_eligibility(self):
        result=self.check();self.assertEqual(result['incident_threshold']['result'],'not-requested')
        self.assertNotIn('eligible_under_declared_rule',result['incident_threshold'])
        self.assertFalse(result['incident_threshold']['Incident_created'])


    def product_subject(self):
        mapping = json.loads((HERE.parent / 'current-mapped-context-v3/packages/0001/mapping.json').read_bytes())
        header = copy.deepcopy(next(row['artifact'] for row in mapping['rows'] if row['artifact']['identity_ref'] == 'product:cyberalchemy-lab'))
        raw = (HERE.parent / 'current-participation-v4/packages/0001/setup-artifacts/product.json').read_bytes()
        assert set(header) == set(self.E.FIELDS) and self.E.sha(raw) == header['byte_sha256']
        scope = header['scope_ref']
        revised = []
        for record in self.records:
            body = json.loads(record.raw)
            body['scope_ref'] = scope
            if body['kind'] == 'failure-occurrence':
                body['payload']['subject_ref'] = header['version_ref']
            if body['kind'] == 'failure-mode':
                body['payload']['subject_kind_ref'] = header['carrier_ref']
            revised.append(self.record(body))
        revised[0] = self.E.Record(header, raw)
        self.records = revised
        assessment = json.loads(self.candidate.raw)
        assessment['scope_ref'] = scope
        self.candidate = self.record(assessment)
        self.request.update(occurrence=copy.deepcopy(self.records[1].header), mode_assignment=copy.deepcopy(self.records[5].header), cause_hypothesis_refs=[copy.deepcopy(self.records[6].header)])
        self.request['assessment_candidate_binding']['sha256'] = self.E.sha(self.candidate.raw)
        self.basis.update(scope_ref=scope, assessment_binding=copy.deepcopy(self.request['assessment_candidate_binding']))
        return self.records[0]

    def test_52_original_Product_failure_subject(self):
        product = self.product_subject()
        self.assertEqual(self.check()['result'], 'pass')
        self.assertNotIn('node_id', json.loads(product.raw))

    def test_53_original_Product_bytes_unchanged(self):
        product = self.product_subject()
        before = product.raw, copy.deepcopy(product.header)
        self.check()
        self.assertEqual((product.raw, product.header), before)

    def test_54_Product_domain_scope_remains_separate(self):
        product = self.product_subject()
        body = self.rules.record(product, product.header['scope_ref'])
        self.assertIsInstance(body['scope'], dict)
        self.assertNotIn('scope_ref', body)
        self.assertEqual(self.check()['result'], 'pass')

    def test_55_Product_inline_version_is_not_header_revision(self):
        product = self.product_subject()
        self.assertEqual(json.loads(product.raw)['version'], '2.0.0-foundation.1')
        self.assertNotEqual(json.loads(product.raw)['version'], product.header['version_ref'])
        self.assertEqual(self.check()['result'], 'pass')

    def test_56_Product_identity_mismatch_refused(self):
        product = self.product_subject()
        header = copy.deepcopy(product.header); header['identity_ref'] = 'product:foreign'
        self.records[0] = self.E.Record(header, product.raw)
        with self.assertRaises(ValueError): self.check()

    def test_57_Product_raw_digest_mismatch_refused(self):
        product = self.product_subject()
        header = copy.deepcopy(product.header); header['byte_sha256'] = '0' * 64
        self.records[0] = self.E.Record(header, product.raw)
        with self.assertRaises(ValueError): self.check()

    def test_58_Product_unselected_carrier_refused(self):
        product = self.product_subject()
        header = copy.deepcopy(product.header); header['carrier_ref'] = 'cal.artifact-type.undeclared/v1'
        self.records[0] = self.E.Record(header, product.raw)
        with self.assertRaises(ValueError): self.check()

    def test_59_Product_synthetic_node_forbidden(self):
        product = self.product_subject()
        body = json.loads(product.raw); body['node_id'] = product.header['identity_ref']
        raw = encoded(body); header = copy.deepcopy(product.header); header['byte_sha256'] = self.E.sha(raw)
        self.records[0] = self.E.Record(header, raw)
        with self.assertRaises(ValueError): self.check()


    def governed_node(self, kind, revision):
        base = ROOT / 'authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors' / kind / revision
        body = json.loads((base / 'fixtures/valid/record.json').read_bytes())
        raw = encoded(body)
        header = {'scope_ref':body['scope_ref'], 'identity_ref':body['node_id'], 'version_ref':body['node_id'] + '@rule-fixture.1', 'carrier_ref':'cal.artifact-type.' + kind + '/' + revision, 'byte_sha256':self.E.sha(raw)}
        return self.E.Record(header, raw)

    def test_60_exact_governance_Typed_Relation_v3_schema(self):
        record = self.governed_node('typed-relation', 'v3')
        self.assertEqual(self.rules.record(record, record.header['scope_ref'])['kind'], 'typed-relation')

    def test_61_exact_governance_Project_State_v2_schema(self):
        record = self.governed_node('project-state', 'v2')
        self.assertEqual(self.rules.record(record, record.header['scope_ref'])['kind'], 'project-state')

    def test_62_Typed_Relation_v3_extra_fields_refused(self):
        record = self.governed_node('typed-relation', 'v3')
        body = json.loads(record.raw); body['undeclared'] = True
        raw = encoded(body); header = copy.deepcopy(record.header); header['byte_sha256'] = self.E.sha(raw)
        with self.assertRaises(ValueError): self.rules.record(self.E.Record(header, raw), header['scope_ref'])

    def test_63_Project_State_v2_identity_mismatch_refused(self):
        record = self.governed_node('project-state', 'v2')
        header = copy.deepcopy(record.header); header['identity_ref'] = 'project-state:foreign'
        with self.assertRaises(ValueError): self.rules.record(self.E.Record(header, record.raw), header['scope_ref'])


def main():
    global PIN
    parser=argparse.ArgumentParser();parser.add_argument('--source-sha256',required=True)
    PIN=parser.parse_args().source_sha256
    cases=[]
    class Result(unittest.TextTestResult):
        def addSuccess(self,t):super().addSuccess(t);cases.append({'test':t.id(),'result':'PASS'})
        def addFailure(self,t,e):super().addFailure(t,e);cases.append({'test':t.id(),'result':'FAIL','detail':self._exc_info_to_string(e,t)})
        def addError(self,t,e):super().addError(t,e);cases.append({'test':t.id(),'result':'ERROR','detail':self._exc_info_to_string(e,t)})
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Rules);assert suite.countTestCases()==63
    result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite)
    success=result.wasSuccessful() and result.testsRun==63
    output=HERE/'receipts';output.mkdir(mode=0o700,exist_ok=True)
    value={'schema_version':'lab-failure-assessment-primitive-checks/v1-candidate',
        'result':'PASS' if success else 'FAIL','tests_run':result.testsRun,'expected_tests':63,'cases':cases,
        'source_sha256':PIN,'actual_public_API_calls':0,'candidate_proposals_created':0,
        'Incidents_created':0,'whole_API_qualified':False,'current_Agent_qualified':False,
        'authority_effect':'none','actual_owner_outcome':None,'task_complete':False}
    with (output/'checks-0001.json').open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'result':value['result'],'tests_run':result.testsRun}),flush=True)
    raise SystemExit(0 if success else 1)


if __name__=='__main__':main()
