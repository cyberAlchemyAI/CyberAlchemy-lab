"""Exact-denominator evidence contracts using isolated admitted-byte fixtures."""
import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[3]
UNIT=ROOT/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/units/E01'
sys.path[:0]=[str(UNIT),str(HERE),str(HERE/'tests')]
import evidence_contract as e
import test_A01 as basic
import test_A02 as capture
import test_A05 as relation


def create_fixture():
    fixture=capture.CaptureTests();fixture.setUp();root=fixture.root;snapshot=e.r.capture(root)
    selected={row['definition_id']:{key:row[key] for key in ['definition_id','version_ref','path','sha256']} for row in snapshot['current_entries']}
    rel,bindings,populations=relation.setup_relation(root)
    for side,key in [('left','DEF-A'),('right','DEF-B')]:rel[side+'_definition'].clear();rel[side+'_definition'].update(selected[key])
    alignment=json.loads((root/'alignment.json').read_text());alignment.update(left_source=rel['left_definition'],right_source=rel['right_definition'])
    raw=json.dumps(alignment).encode();(root/'alignment.json').write_bytes(raw);rel['alignment']['map_ref']['sha256']=e.r.digest(raw)
    scope=rel['scope'];theory={'theory_id':'T1','sources':[rel['left_definition'],rel['right_definition']],'declarations':[{'kind':'sort','symbol_id':'Object','scope':scope,'domain_policy':'nonempty'}]+[{'kind':'predicate','symbol_id':name,'scope':scope,'argument_sorts':['Object']} for name in ['P','Q']],'statements':[],'assumption_set_id':'CTX1','scope':scope,'change_class':'initial','prior_theory_ref':None}
    requests=[{'relation':rel,'bindings':bindings,'proper':False,'distinction':'permitted','forbidden':[]}]
    required=e.o.generate(theory,requests,populations,bindings,root)
    def put(path,value):
        raw=json.dumps(value,indent=2,sort_keys=True).encode();file=root/path;file.parent.mkdir(parents=True,exist_ok=True);file.write_bytes(raw)
        return {'path':path,'sha256':e.r.digest(raw)}
    logical=[]
    for obligation in required['logical_manifest']['obligations']:
        result=basic.payloads()['result'];result.update(obligation_id=obligation['obligation_id'],statement_sha256=e.digest(obligation['statement']),theory_sha256=required['logical_manifest']['theory_sha256'],verdict='missing')
        logical.append({'obligation':copy.deepcopy(obligation),'result':result,'provider_kind':'unresolved','native_input_ref':None,'native_result':None,'profile_ref':None,'toolchain_ref':None})
    gates=[{'gate':copy.deepcopy(gate),'execution':'not-run','currentness':'unknown','reported_status':'pending','evidence_refs':[],'native_result':None,'readiness':'not-assessed'} for gate in required['administrative_and_semantic_gates']]
    bundle={'schema_version':'definition-assurance-evidence-bundle/v1-candidate','authority_effect':'none','upstream_schema_sha256':e.r.digest((HERE/'schemas/input-envelope.json').read_bytes()),'snapshot_ref':put('candidate/snapshot.json',snapshot),'sources':copy.deepcopy(theory['sources']),'interpretations':[{'source':copy.deepcopy(source),'scope':scope,'status':'missing','correspondence_ref':None,'typed_ir_ref':None} for source in theory['sources']],'dependency_graph_ref':put('candidate/dependencies.json',{'status':'missing-semantic-dependency-declarations','authority_effect':'none'}),'theory_ref':put('candidate/theory.json',theory),'assumption_set_ref':put('candidate/assumptions.json',{'assumption_set_id':'CTX1','assumptions':[],'authority_effect':'none'}),'coupling_refs':[rel['alignment']['map_ref']],'required_set_ref':put('candidate/required.json',required),'required_set':required,'logical_results':logical,'gate_results':gates,'readiness':'not-assessed','semantic_ready':False,'verification':'pending-independent-verification','claim_ceiling':'Synthetic complete-denominator evidence accounting with missing translations/results; no source meaning or theorem accepted.'}
    return fixture,bundle,required,put


class EvidenceControls(unittest.TestCase):
    def setUp(self):
        self.fixture,self.bundle,self.required,self.put=create_fixture();self.addCleanup(self.fixture.doCleanups);self.root=self.fixture.root
    def check(self,**options):return e.check(self.bundle,self.required,**options)
    def invalid(self):
        result=self.check();self.assertNotEqual('candidate-accounted',result['status']);self.assertFalse(result['semantic_ready']);return result
    def finite(self,status='witness-found'):
        row=next(row for row in self.bundle['logical_results'] if row['obligation']['obligation_id']=='query:consistency')
        native={'schema_version':'definition-assurance-finite-result/v1-candidate','authority_effect':'none','semantic_ready':False,'unbounded_conclusion':None,'status':status,'exhaustion_complete':status.startswith('bounded'),'evidence_strength':'bounded-exhaustion' if status.startswith('bounded') else 'model-witness' if status in {'witness-found','countermodel-found'} else 'none','witness':{'model':{'domains':{},'constants':{},'functions':{},'predicates':{}},'query_truth':status=='witness-found'} if status in {'witness-found','countermodel-found'} else None,'space':{'scope':'synthetic-status-control'}}
        dimensions=e.finite_dimensions(native);ref=self.put('candidate/native-result.json',native);row.update(provider_kind='finite-static',native_input_ref=self.put('candidate/native-input.json',{'query':row['obligation']['statement']}),native_result={'binding':ref,'data':native},profile_ref=self.put('candidate/profile.json',{'kind':'finite-static'}),toolchain_ref=self.put('candidate/toolchain.json',{'kind':'synthetic-unverified-runtime'}))
        row['result'].update(execution=dimensions[0],verdict=dimensions[1],strength=dimensions[2],evidence_refs=[ref],profile_ref='profile:finite-static')
        return row,native

    def test_complete_missing_evidence_rows_are_accounted_without_readiness(self):
        out=self.check(root=self.root);self.assertEqual('candidate-accounted',out['status']);self.assertEqual('bound',out['native_bytes']);self.assertEqual(5,out['required_logical_obligations']);self.assertEqual(6,out['required_gates']);self.assertFalse(out['semantic_ready']);self.assertFalse(out['evidence_verified']);self.assertEqual(5,len(out['pending_logical_reports']))

    def test_structure_without_resolved_bytes_is_not_evidence_verification(self):
        out=self.check();self.assertEqual('candidate-accounted',out['status']);self.assertEqual('not-resolved',out['native_bytes']);self.assertFalse(out['evidence_verified'])

    def test_omit_each_required_result_or_gate_rejects_submission_denominator(self):
        original=copy.deepcopy(self.bundle)
        for key in ['logical_results','gate_results']:
            for index in range(len(original[key])):
                self.bundle=copy.deepcopy(original);self.bundle[key].pop(index);out=self.invalid();self.assertIn('denominator-mismatch',out['diagnostics'][0]['code'])

    def test_duplicate_result_does_not_fill_missing_identity(self):
        self.bundle['logical_results'][1]=copy.deepcopy(self.bundle['logical_results'][0]);self.bundle['logical_results'][1]['result']['currentness']='stale';out=self.invalid();self.assertEqual('logical-result-denominator-mismatch',out['diagnostics'][0]['code'])

    def test_required_set_cannot_weaken_statement_strength_or_assumption_context(self):
        self.bundle=copy.deepcopy(self.bundle);self.bundle['required_set']['logical_manifest']['obligations'][0]['minimum_strength']='structural';out=self.invalid();self.assertEqual('required-set-omitted-substituted-weakened-or-stale',out['diagnostics'][0]['code'])
        self.bundle['required_set']=self.required;self.bundle['logical_results'][0]['obligation']['assumption_set_ref']='Other';out=self.invalid();self.assertEqual('required-obligation-substituted',out['diagnostics'][0]['code'])

    def test_statement_theory_or_identity_substitution_rejected(self):
        original=copy.deepcopy(self.bundle)
        for key,value in [('statement_sha256','0'*64),('theory_sha256','0'*64),('obligation_id','Other')]:
            self.bundle=copy.deepcopy(original);self.bundle['logical_results'][0]['result'][key]=value;out=self.invalid();self.assertEqual('result-statement-or-theory-binding-mismatch',out['diagnostics'][0]['code'])

    def test_missing_or_stale_source_and_interpretation_row_rejected(self):
        self.bundle['interpretations'].pop();out=self.invalid();self.assertEqual('interpretation-denominator-mismatch',out['diagnostics'][0]['code'])
        self.bundle['interpretations']=[{'source':copy.deepcopy(source),'scope':'candidate-scope','status':'missing','correspondence_ref':None,'typed_ir_ref':None} for source in self.bundle['sources']];self.bundle['interpretations'][0]['source']['sha256']='0'*64;out=self.invalid();self.assertEqual('interpretation-source-binding-mismatch',out['diagnostics'][0]['code'])

    def test_selected_source_denominator_cannot_drop_a_required_identity(self):
        self.bundle['sources'].pop();out=self.invalid();self.assertEqual('selected-source-denominator-mismatch',out['diagnostics'][0]['code'])

    def test_native_data_must_match_actual_selected_file_even_if_rehashed(self):
        row,native=self.finite();row['native_result']['data']['witness']['query_truth']=False
        out=self.check(root=self.root);self.assertEqual('native-data-byte-binding-mismatch',out['diagnostics'][0]['code']);self.assertFalse(out['semantic_ready'])

    def test_finite_status_bridge_does_not_promote_bounded_strength_to_theorem(self):
        row,native=self.finite('bounded-supported');out=self.check(root=self.root);self.assertEqual('candidate-accounted',out['status']);self.assertEqual('finite-exhaustion',row['result']['strength']);self.assertFalse(out['semantic_ready'])
        row['result']['strength']='mechanized-theorem';out=self.invalid();self.assertEqual('finite-native-dimension-substitution',out['diagnostics'][0]['code'])

    def test_execution_outcomes_are_retained_without_logical_support(self):
        for status in ['resource-limit','timeout','cancelled','provider-error','unsupported','malformed','unresolved-input-or-binding']:
            row,native=self.finite(status);out=self.check(root=self.root);self.assertEqual('candidate-accounted',out['status']);self.assertEqual('none',row['result']['strength']);self.assertFalse(out['semantic_ready'])

    def test_bounded_absence_is_not_unbounded_inconsistency(self):
        row,native=self.finite('bounded-no-theory-model');out=self.check(root=self.root);self.assertEqual('candidate-accounted',out['status']);self.assertEqual('unknown',row['result']['verdict']);self.assertIsNone(native['unbounded_conclusion'])

    def test_forged_finite_exhaustion_or_witness_shape_rejected(self):
        row,native=self.finite('bounded-supported');native['exhaustion_complete']=False;out=self.invalid();self.assertEqual('finite-native-exhaustion-shape',out['diagnostics'][0]['code'])

    def test_supported_row_requires_native_input_data_profile_and_runtime_refs(self):
        row,native=self.finite();row['native_input_ref']=None;self.assertEqual('malformed',self.invalid()['status'])

    def test_reviewed_fidelity_needs_a_review_reference_and_remains_unverified(self):
        row,native=self.finite();row['result']['source_fidelity']['status']='reviewed';self.assertEqual('malformed',self.invalid()['status'])
        row['result']['source_fidelity']['review_ref']=self.put('candidate/review.json',{'reviewer':'synthetic-control','status':'reported-review'});out=self.check(root=self.root);self.assertEqual('candidate-accounted',out['status']);self.assertFalse(out['semantic_ready'])

    def test_reported_gate_support_requires_actual_data_and_evidence_ref(self):
        row=self.bundle['gate_results'][0];row.update(reported_status='reported-supported',execution='completed',currentness='current');self.assertEqual('malformed',self.invalid()['status'])
        native={'status':'reported-supported','authority_effect':'none'};ref=self.put('candidate/gate-result.json',native);row.update(native_result={'binding':ref,'data':native},evidence_refs=[ref]);out=self.check(root=self.root);self.assertEqual('candidate-accounted',out['status']);self.assertFalse(out['semantic_ready'])

    def test_gate_prerequisites_and_check_cannot_be_substituted(self):
        self.bundle['gate_results'][0]['gate']['prerequisites']=['Other'];out=self.invalid();self.assertEqual('required-gate-substituted',out['diagnostics'][0]['code'])

    def test_source_stale_after_bundle_assembly_rejects_byte_binding(self):
        file=self.root/self.bundle['sources'][0]['path'];file.write_bytes(file.read_bytes()+b' ');out=self.check(root=self.root);self.assertEqual('stale-or-substituted-artifact',out['diagnostics'][0]['code'])

    def test_capture_is_closed_and_cannot_drop_or_add_artifacts(self):
        captured={row['path']:e.r.read_bytes(self.root,row['path']) for row in e.artifact_refs(self.bundle)};out=self.check(captured=captured);self.assertEqual('candidate-accounted',out['status'])
        captured['unselected']=b'bytes';out=self.check(captured=captured);self.assertEqual('captured-artifact-denominator-mismatch',out['diagnostics'][0]['code'])

    def test_same_artifact_path_cannot_have_conflicting_hashes(self):
        self.bundle['coupling_refs'].append({'path':self.bundle['snapshot_ref']['path'],'sha256':'0'*64});out=self.invalid();self.assertEqual('conflicting-artifact-byte-binding',out['diagnostics'][0]['code'])

    def test_native_result_must_be_in_its_explicit_evidence_list(self):
        row,native=self.finite('resource-limit');row['result']['evidence_refs']=[];out=self.invalid();self.assertEqual('native-result-not-in-evidence-refs',out['diagnostics'][0]['code'])

    def test_unsupported_unknown_stale_and_missing_reports_never_aggregate_ready(self):
        for verdict in ['unsupported','unknown','stale','missing']:
            self.bundle['logical_results'][0]['result']['verdict']=verdict;out=self.check();self.assertEqual('candidate-accounted',out['status']);self.assertFalse(out['semantic_ready']);self.assertIn(self.bundle['logical_results'][0]['obligation']['obligation_id'],out['pending_logical_reports'])

    def test_self_declared_readiness_or_authority_and_unknown_fields_rejected(self):
        original=copy.deepcopy(self.bundle)
        for key,value in [('semantic_ready',True),('authority_effect','admitted'),('readiness','ready'),('unknown',True)]:
            self.bundle=copy.deepcopy(original);self.bundle[key]=value;self.assertEqual('malformed',self.invalid()['status'])

    def test_remote_schema_reference_is_never_resolved(self):
        # Exercise the local schema loader itself; no network lookup occurs.
        raw=e.SCHEMA_PATH.read_bytes();value=json.loads(raw);value['properties']['snapshot_ref']={'$ref':'https://invalid.example/schema'}
        with patch.object(Path,'read_bytes',return_value=json.dumps(value).encode()):
            out=self.check();self.assertEqual('nonlocal-evidence-schema-reference',out['diagnostics'][0]['code'])


if __name__=='__main__':unittest.main()
