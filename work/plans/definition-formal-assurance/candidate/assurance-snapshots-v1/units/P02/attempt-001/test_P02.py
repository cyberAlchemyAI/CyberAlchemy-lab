"""Hand-derived finite theories and generic-signature search controls."""
import copy
import sys
import tracemalloc
import unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(HERE/'providers'),str(HERE),str(HERE/'tests')]
import finite as f
import test_A01 as fixtures


def subject(extra=()):
    core=fixtures.payloads()['interpretation'];core['declarations']+=copy.deepcopy(list(extra));value=f.ir.compile_interpretation(core)
    names={row['local_symbol_id']:row['canonical_id'] for row in value['origins']}
    return value,names


class FiniteControls(unittest.TestCase):
    def setUp(self):self.subject,self.ids=subject();self.cards={self.ids['Object']:2}
    def var(self,name='x'):return {'op':'var','name':name}
    def pred(self,name='P',*args):return {'op':'pred','name':self.ids[name],'args':list(args)}
    def quant(self,op,body,var='x',sort='Object'):return {'op':op,'var':var,'sort':self.ids[sort],'body':body}
    def search(self,T=(),I=(),Q=None,**kwargs):return f.search(self.subject,list(T),list(I),{'op':'and','args':[]} if Q is None else Q,self.cards,**kwargs)
    def replay(self,out,T=(),I=(),Q=None):return f.replay(self.subject,out,list(T),list(I),{'op':'and','args':[]} if Q is None else Q,self.cards)

    def test_first_witness_streams_a_complete_interpretation(self):
        out=self.search();self.assertEqual('witness-found',out['status']);self.assertEqual(1,out['counts']['visited']);self.assertEqual([],out['witness']['model']['predicates'][self.ids['P']]);self.assertFalse(out['exhaustion_complete']);self.assertFalse(out['semantic_ready']);self.assertEqual('PASS',self.replay(out)['result'])

    def test_hand_theory_one_exactly_one_marked_member_and_unmarked_witness(self):
        p=self.pred('P',self.var());exactly_one=self.quant('exists',{'op':'and','args':[p,self.quant('forall',{'op':'implies','left':self.pred('P',self.var('y')),'right':{'op':'eq','left':self.var('y'),'right':self.var()}},'y')]})
        unmarked=self.quant('exists',{'op':'not','arg':p});out=self.search(T=[exactly_one],I=[self.quant('exists',p)],Q=unmarked)
        self.assertEqual('witness-found',out['status']);extension=out['witness']['model']['predicates'][self.ids['P']];self.assertEqual(1,len(extension));self.assertEqual('PASS',self.replay(out,[exactly_one],[self.quant('exists',p)],unmarked)['result'])
        # Hand argument: one marked member in a two-member domain leaves one unmarked.
        bounded=self.search(T=[exactly_one],I=[self.quant('exists',p)],Q=unmarked,mode='bounded-validity');self.assertEqual('bounded-supported',bounded['status']);self.assertEqual(4,bounded['counts']['visited']);self.assertEqual(2,bounded['counts']['admissible_models'])

    def test_hand_theory_two_total_involution_without_fixed_point(self):
        scope=self.subject['input_core']['scope'];self.subject,self.ids=subject([{'kind':'total-function','symbol_id':'next','scope':scope,'argument_sorts':['Object'],'result_sort':'Object','definedness_policy':None}]);self.cards={self.ids['Object']:2}
        x=self.var();nextx={'op':'fn','name':self.ids['next'],'args':[x]};twice={'op':'fn','name':self.ids['next'],'args':[nextx]}
        involution=self.quant('forall',{'op':'eq','left':twice,'right':x});no_fixed=self.quant('forall',{'op':'not','arg':{'op':'eq','left':nextx,'right':x}})
        out=self.search(T=[involution,no_fixed]);self.assertEqual('witness-found',out['status']);rows=out['witness']['model']['functions'][self.ids['next']];self.assertEqual([{'args':['a0'],'value':'a1'},{'args':['a1'],'value':'a0'}],rows);self.assertEqual('PASS',self.replay(out,[involution,no_fixed])['result'])
        # On one member every total function fixes it, so absence is scoped to n=1.
        self.cards={self.ids['Object']:1};out=self.search(T=[involution,no_fixed]);self.assertEqual('bounded-no-theory-model',out['status']);self.assertTrue(out['exhaustion_complete']);self.assertIsNone(out['unbounded_conclusion'])

    def test_constants_total_functions_and_predicates_exact_space_count(self):
        scope=self.subject['input_core']['scope'];self.subject,self.ids=subject([{'kind':'constant','symbol_id':'c','scope':scope,'result_sort':'Object'},{'kind':'total-function','symbol_id':'f','scope':scope,'argument_sorts':['Object'],'result_sort':'Object','definedness_policy':None}]);self.cards={self.ids['Object']:2}
        out=self.search(Q={'op':'or','args':[]});self.assertEqual('bounded-no-witness',out['status']);self.assertEqual(32,out['space']['small_exact_total']);self.assertEqual(32,out['counts']['visited'])

    def test_countermodel_target_is_not_inserted_into_theory(self):
        population=self.quant('exists',self.pred('P',self.var()));target=self.quant('forall',self.pred('P',self.var()));saved=copy.deepcopy(target)
        out=self.search(I=[population],Q=target,mode='countermodel');self.assertEqual('countermodel-found',out['status']);self.assertFalse(out['witness']['query_truth']);self.assertEqual(saved,target);self.assertEqual('PASS',self.replay(out,[],[population],target)['result'])

    def test_required_populations_must_coexist_under_one_interpretation(self):
        p=self.pred('P',self.var());T=[self.quant('forall',{'op':'not','arg':p})];I=[self.quant('exists',p)]
        out=self.search(T,I,mode='bounded-validity');self.assertEqual('bounded-no-admissible-model',out['status']);self.assertEqual(1,out['counts']['theory_models']);self.assertEqual(0,out['counts']['admissible_models']);self.assertNotEqual('bounded-supported',out['status'])

    def test_bounded_validity_requires_admissible_models_and_exact_exhaustion(self):
        out=self.search(mode='bounded-validity');self.assertEqual('bounded-supported',out['status']);self.assertEqual(4,out['counts']['visited']);self.assertEqual('bounded-exhaustion',out['evidence_strength']);self.assertIsNone(out['unbounded_conclusion'])
        self.assertEqual(4,out['space']['small_exact_total'])

    def test_unary_and_binary_predicates_with_multiple_sorts(self):
        scope=self.subject['input_core']['scope'];extra=[{'kind':'sort','symbol_id':'Color','scope':scope,'domain_policy':'nonempty'},{'kind':'relation','symbol_id':'Paint','scope':scope,'argument_sorts':['Object','Color']}]
        self.subject,self.ids=subject(extra);self.cards={self.ids['Object']:2,self.ids['Color']:1}
        paint=self.pred('Paint',self.var('x'),self.var('y'));target=self.quant('forall',self.quant('exists',paint,'y','Color'))
        out=self.search(Q=target);self.assertEqual('witness-found',out['status']);self.assertEqual([['a0','a0'],['a1','a0']],out['witness']['model']['predicates'][self.ids['Paint']]);self.assertEqual('PASS',self.replay(out,Q=target)['result'])

    def test_zero_arity_predicate_and_total_function_enumeration(self):
        scope=self.subject['input_core']['scope'];extra=[{'kind':'predicate','symbol_id':'Flag','scope':scope,'argument_sorts':[]},{'kind':'total-function','symbol_id':'unit','scope':scope,'argument_sorts':[],'result_sort':'Object','definedness_policy':None}]
        self.subject,self.ids=subject(extra);self.cards={self.ids['Object']:1};out=self.search(Q=self.pred('Flag'))
        self.assertEqual('witness-found',out['status']);self.assertEqual([[]],out['witness']['model']['predicates'][self.ids['Flag']]);self.assertEqual([{'args':[],'value':'a0'}],out['witness']['model']['functions'][self.ids['unit']]);self.assertEqual('PASS',self.replay(out,Q=self.pred('Flag'))['result'])

    def test_unknown_false_missing_and_empty_domains_are_distinct(self):
        for value in [0,True,None,4]:
            self.cards={self.ids['Object']:value};out=self.search();self.assertEqual('malformed',out['status']);self.assertIsNone(out['witness']);self.assertEqual('none',out['evidence_strength'])
        self.cards={};out=self.search();self.assertEqual('malformed',out['status'])

    def test_interpretation_budget_exhaustion_is_unknown_not_absence(self):
        out=self.search(Q={'op':'or','args':[]},budgets={'max_interpretations':2});self.assertEqual('resource-limit',out['status']);self.assertFalse(out['exhaustion_complete']);self.assertEqual(2,out['counts']['visited']);self.assertEqual('none',out['evidence_strength'])
        # Completing at exactly the budget is valid when every interpretation was visited.
        out=self.search(Q={'op':'or','args':[]},budgets={'max_interpretations':4});self.assertEqual('bounded-no-witness',out['status']);self.assertTrue(out['exhaustion_complete'])

    def test_global_evaluation_budget_does_not_reset_per_model(self):
        out=self.search(Q={'op':'or','args':[]},budgets={'max_evaluation_steps':2});self.assertEqual('resource-limit',out['status']);self.assertEqual('evaluation-step-limit',out['diagnostics'][0]['code']);self.assertEqual(2,out['counts']['evaluation_steps'])

    def test_cancellation_before_search_and_during_quantification(self):
        out=self.search(cancelled=lambda:True);self.assertEqual('cancelled',out['status']);self.assertEqual(0,out['counts']['visited']);self.assertIsNone(out['witness'])
        calls=[0]
        def cancel():calls[0]+=1;return calls[0]>12
        out=self.search(Q=self.quant('forall',self.pred('P',self.var())),mode='bounded-validity',cancelled=cancel);self.assertEqual('cancelled',out['status']);self.assertEqual('none',out['evidence_strength'])

    def test_deadline_checked_before_enumeration(self):
        with patch.object(f,'monotonic',side_effect=[0,31,31]):out=self.search()
        self.assertEqual('timeout',out['status']);self.assertEqual('none',out['evidence_strength']);self.assertFalse(out['exhaustion_complete'])

    def test_output_limit_has_no_model_or_absence_evidence(self):
        out=self.search(budgets={'max_output_bytes':2048});self.assertEqual('resource-limit',out['status']);self.assertIsNone(out['witness']);self.assertEqual('none',out['evidence_strength']);self.assertLessEqual(len(f.ir.canonical(out)),2048)

    def test_tuple_space_limit_is_an_execution_outcome(self):
        scope=self.subject['input_core']['scope'];self.subject,self.ids=subject([{'kind':'relation','symbol_id':'R','scope':scope,'argument_sorts':['Object','Object']}]);self.cards={self.ids['Object']:2}
        out=self.search(budgets={'max_function_tuple_space':2});self.assertEqual('resource-limit',out['status']);self.assertEqual('symbol-tuple-space-limit',out['diagnostics'][0]['code'])

    def test_huge_factored_space_can_stream_first_sparse_witness(self):
        scope=self.subject['input_core']['scope'];self.subject,self.ids=subject([{'kind':'relation','symbol_id':'R','scope':scope,'argument_sorts':['Object']*9}]);self.cards={self.ids['Object']:3}
        out=self.search();self.assertEqual('witness-found',out['status']);self.assertIsNone(out['space']['small_exact_total']);factor=next(row for row in out['space']['factors'] if row['symbol_id']==self.ids['R']);self.assertEqual(19683,factor['exponent']);self.assertIsNone(factor['small_exact_choice_count']);self.assertEqual(1,out['counts']['visited'])

    def test_no_powerset_or_visited_model_cache_memory_bound(self):
        scope=self.subject['input_core']['scope'];self.subject,self.ids=subject([{'kind':'relation','symbol_id':'R','scope':scope,'argument_sorts':['Object']*9}]);self.cards={self.ids['Object']:3}
        tracemalloc.start()
        try:
            out=self.search(Q={'op':'or','args':[]},budgets={'max_interpretations':512});_,peak=tracemalloc.get_traced_memory()
        finally:tracemalloc.stop()
        self.assertEqual('resource-limit',out['status']);self.assertEqual(512,out['counts']['visited']);self.assertLess(peak,8_000_000)

    def test_unsupported_and_malformed_ast_are_not_logical_absence(self):
        out=self.search(Q={'op':'eventually','body':{'op':'and','args':[]}});self.assertEqual('unsupported',out['status']);self.assertEqual('none',out['evidence_strength'])
        out=self.search(Q={'op':'pred','name':'missing','args':[]});self.assertEqual('malformed',out['status'])

    def test_budget_cannot_be_boolean_nonfinite_or_looser_than_sealed_caps(self):
        for budgets in [{'max_interpretations':True},{'max_interpretations':10001},{'timeout_seconds':float('nan')},{'timeout_seconds':float('inf')},{'max_output_bytes':1}]:
            out=self.search(budgets=budgets);self.assertEqual('malformed',out['status']);self.assertEqual('none',out['evidence_strength'])

    def test_provider_errors_do_not_receive_a_truth_value(self):
        with patch.object(f.s,'validate_model',side_effect=OSError('synthetic provider failure')):out=self.search()
        self.assertEqual('provider-error',out['status']);self.assertEqual('none',out['evidence_strength']);self.assertIsNone(out['witness'])

    def test_composition_requires_independently_selected_ir_inputs(self):
        joined=f.ir.compose([self.subject]);out=f.search(joined,[],[],{'op':'and','args':[]},self.cards);self.assertEqual('malformed',out['status'])
        out=f.search(joined,[],[],{'op':'and','args':[]},self.cards,selected_inputs=[self.subject]);self.assertEqual('witness-found',out['status'])
        self.assertEqual('PASS',f.replay(joined,out,[],[],{'op':'and','args':[]},self.cards,selected_inputs=[self.subject])['result'])

    def test_replay_rejects_tampering_even_with_rehashed_model(self):
        query=self.quant('exists',self.pred('P',self.var()));out=self.search(Q=query);bad=copy.deepcopy(out);bad['witness']['model']['predicates'][self.ids['P']]=[];bad['witness']['model_sha256']=f.ir.digest(bad['witness']['model'])
        with self.assertRaises(f.ProviderFault) as caught:self.replay(bad,Q=query)
        self.assertEqual('witness-does-not-establish-selected-query',caught.exception.code)

    def test_replay_binds_the_selected_query_and_cardinality_scope(self):
        out=self.search()
        with self.assertRaises(f.ProviderFault) as caught:self.replay(out,Q={'op':'or','args':[]})
        self.assertEqual('witness-replay-input-substitution',caught.exception.code)
        self.cards={self.ids['Object']:1}
        with self.assertRaises(f.ProviderFault):self.replay(out)

    def test_capped_radix_never_marks_a_prefix_as_full_exhaustion(self):
        scope=self.subject['input_core']['scope'];self.subject,self.ids=subject([{'kind':'relation','symbol_id':'R','scope':scope,'argument_sorts':['Object']*3}]);self.cards={self.ids['Object']:3}
        out=self.search(Q={'op':'or','args':[]},budgets={'max_interpretations':10});self.assertEqual('resource-limit',out['status']);self.assertFalse(out['exhaustion_complete']);self.assertEqual(10,out['counts']['visited'])


if __name__=='__main__':unittest.main()
