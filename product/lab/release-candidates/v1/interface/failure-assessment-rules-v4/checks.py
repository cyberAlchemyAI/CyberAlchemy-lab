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
        self.policy(2);r=self.check();self.assertEqual(r['result'],'fail')
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


def main():
    global PIN
    parser=argparse.ArgumentParser();parser.add_argument('--source-sha256',required=True)
    PIN=parser.parse_args().source_sha256
    cases=[]
    class Result(unittest.TextTestResult):
        def addSuccess(self,t):super().addSuccess(t);cases.append({'test':t.id(),'result':'PASS'})
        def addFailure(self,t,e):super().addFailure(t,e);cases.append({'test':t.id(),'result':'FAIL','detail':self._exc_info_to_string(e,t)})
        def addError(self,t,e):super().addError(t,e);cases.append({'test':t.id(),'result':'ERROR','detail':self._exc_info_to_string(e,t)})
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Rules);assert suite.countTestCases()==46
    result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite)
    success=result.wasSuccessful() and result.testsRun==46
    output=HERE/'receipts';output.mkdir(mode=0o700,exist_ok=True)
    value={'schema_version':'lab-failure-assessment-primitive-checks/v1-candidate',
        'result':'PASS' if success else 'FAIL','tests_run':result.testsRun,'expected_tests':46,'cases':cases,
        'source_sha256':PIN,'actual_public_API_calls':0,'candidate_proposals_created':0,
        'Incidents_created':0,'whole_API_qualified':False,'current_Agent_qualified':False,
        'authority_effect':'none','actual_owner_outcome':None,'task_complete':False}
    with (output/'checks-0001.json').open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'result':value['result'],'tests_run':result.testsRun}),flush=True)
    raise SystemExit(0 if success else 1)


if __name__=='__main__':main()
