"""Evidence strength cannot be replaced by provider names or runtime presence."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[3]
UNIT=ROOT/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/units/P01'
sys.path[:0]=[str(UNIT),str(HERE),str(HERE/'tests')]
import select_profile as s
import test_A01 as fixtures


class SelectionControls(unittest.TestCase):
    def setUp(self):
        self.policy=s.load_policy();self.inventory=json.loads((UNIT.parents[1]/'tooling-assessment.json').read_text());self.core=fixtures.payloads()['interpretation'];self.subject=s.ir.compile_interpretation(self.core)
        self.sorts={row['symbol_id']:2 for row in self.subject['declarations'] if row['kind']=='sort'}
    def request(self,query='model-local-check',scope='finite-exact'):
        return {'obligation_id':'obligation:synthetic-control','query_type':query,'statement':copy.deepcopy(self.subject['clauses'][0]['formal_statement']),'minimum_strength':s.MINIMUMS[query],'domain_scope':{'kind':scope,'cardinalities':self.sorts if scope=='finite-exact' else None}}
    def select(self,query='model-local-check',**options):return s.select(self.core,self.request(query),self.policy,self.inventory,**options)
    def fault(self,code,callback):
        with self.assertRaises(s.SelectionFault) as caught:callback()
        self.assertEqual(code,caught.exception.code)

    def test_model_local_route_is_available_but_grants_no_semantic_readiness(self):
        out=self.select();self.assertEqual('ready-for-candidate-provider-execution',out['status']);self.assertEqual('static-model-evaluator',out['selected_route']);self.assertFalse(out['semantic_ready']);self.assertNotIn('truth',out)
        self.assertIn('first-order',out['derived_logic_features'])

    def test_witness_route_remains_pending_implementation_even_with_python(self):
        out=self.select('consistency');self.assertEqual('pending-provider-implementation',out['status']);self.assertEqual('model-witness',out['required_strength'])

    def test_universal_route_missing_runtime_is_not_finite_fallback(self):
        out=self.select('universal-property');self.assertEqual('missing-runtime',out['status']);self.assertEqual('proof-kernel',out['selected_route'])

    def test_finite_and_solver_evidence_cannot_satisfy_theorem_requirement(self):
        for route in ['generic-finite','smt-projection','static-model-evaluator']:
            out=self.select('universal-property',preferred_route=route);self.assertEqual('weaker-than-required-evidence',out['status']);self.assertIsNone(out['selected_route'])

    def test_required_strength_cannot_be_weakened_in_request(self):
        request=self.request('universal-property');request['minimum_strength']='bounded-exhaustion'
        out=s.select(self.core,request,self.policy,self.inventory);self.assertEqual('required-strength-mismatch',out['status'])

    def test_source_logic_need_is_checked_before_provider_availability(self):
        self.core['logic_features']=['temporal'];out=self.select('universal-property');self.assertEqual('unsupported-logic',out['status']);self.assertIsNone(out['selected_route'])

    def test_a_supported_feature_label_cannot_hide_a_temporal_operator(self):
        request=self.request();request['statement']={'op':'eventually','body':{'op':'and','args':[]}}
        out=s.select(self.core,request,self.policy,self.inventory);self.assertEqual('unsupported-logic',out['status'])

    def test_malformed_actual_symbol_never_routes_from_a_feature_label(self):
        request=self.request();request['statement']={'op':'pred','name':'missing','args':[]}
        out=s.select(self.core,request,self.policy,self.inventory);self.assertEqual('malformed-typed-input',out['status'])

    def test_mutated_inventory_availability_does_not_override_selected_bytes(self):
        self.inventory['routes']['proof-kernel']['runtime_available']=True
        self.fault('inventory-selection-or-byte-binding-mismatch',lambda:self.select('universal-property'))

    def test_available_runtime_or_adapter_requires_exact_binding(self):
        bad=copy.deepcopy(self.inventory);bad['routes']['static-model-evaluator']['runtime_bindings']=[]
        self.fault('unbound-available-runtime',lambda:s.verify_inventory(bad,live=False))
        bad=copy.deepcopy(self.inventory);bad['routes']['static-model-evaluator']['adapter_bindings']=[]
        self.fault('unbound-available-adapter',lambda:s.verify_inventory(bad,live=False))

    def test_stale_runtime_digest_fails_live_revalidation(self):
        bad=copy.deepcopy(self.inventory)
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'runtime';path.write_bytes(b'exact');bad['routes']['static-model-evaluator']['runtime_bindings']=[{'path':str(path),'sha256':'0'*64}]
            self.fault('stale-runtime-or-adapter',lambda:s.verify_inventory(bad))

    def test_exact_finite_scope_cannot_use_boolean_zero_or_missing_sort(self):
        for value in [True,0,4,None]:
            request=self.request();request['domain_scope']['cardinalities']={key:value for key in self.sorts}
            self.fault('invalid-finite-domain-scope',lambda:s.select(self.core,request,self.policy,self.inventory))
        request=self.request();request['domain_scope']['cardinalities']={}
        self.fault('invalid-finite-domain-scope',lambda:s.select(self.core,request,self.policy,self.inventory))

    def test_bounded_absence_requires_explicit_scope_and_is_separate_from_witness(self):
        out=self.select('bounded-property');self.assertEqual('bounded-exhaustion',out['required_strength']);self.assertEqual('pending-provider-implementation',out['status'])
        out=s.select(self.core,self.request('bounded-property','general-static'),self.policy,self.inventory);self.assertEqual('unsupported-domain-scope',out['status'])

    def test_solver_witness_may_be_considered_but_missing_adapter_or_runtime_remains(self):
        out=self.select('consistency',preferred_route='smt-projection');self.assertEqual('missing-runtime',out['status']);self.assertEqual('model-witness',out['required_strength'])

    def test_policy_cannot_weaken_fixed_minimums_or_boolean_budget(self):
        bad=copy.deepcopy(self.policy);bad['minimum_strengths']['universal-property']='model-witness';self.fault('changed-required-strength-or-logic',lambda:s.validate_policy(bad))
        bad=copy.deepcopy(self.policy);bad['budgets']['max_interpretations']=True;self.fault('invalid-positive-budget',lambda:s.validate_policy(bad))


if __name__=='__main__':unittest.main()
