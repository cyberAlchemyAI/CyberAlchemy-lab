import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(HERE));sys.path.insert(0,str(HERE/'tests'))
import semantics as s
import test_A01 as fixtures


def fixture():
    core=fixtures.payloads()['interpretation'];scope=core['scope']
    core['declarations'] += [{'kind':'predicate','symbol_id':'Q','scope':scope,'argument_sorts':['Object']},{'kind':'relation','symbol_id':'R','scope':scope,'argument_sorts':['Object','Object']},{'kind':'predicate','symbol_id':'Flag','scope':scope,'argument_sorts':[]},{'kind':'constant','symbol_id':'c','scope':scope,'result_sort':'Object'},{'kind':'total-function','symbol_id':'flip','scope':scope,'argument_sorts':['Object'],'result_sort':'Object','definedness_policy':None}]
    subject=s.ir.compile_interpretation(core);ids={row['local_symbol_id']:row['canonical_id'] for row in subject['origins']}
    model={'domains':{ids['Object']:['a','b']},'constants':{ids['c']:'a'},'functions':{ids['flip']:[{'args':['a'],'value':'b'},{'args':['b'],'value':'a'}]},'predicates':{ids['P']:[['a']],ids['Q']:[['a']],ids['R']:[],ids['Flag']:[]}}
    return subject,ids,model


class SemanticControls(unittest.TestCase):
    def setUp(self):self.subject,self.ids,self.model=fixture()
    def v(self,name='x'):return {'op':'var','name':name}
    def pred(self,name,*args):return {'op':'pred','name':self.ids[name],'args':list(args)}
    def quant(self,op,body,name='x'):return {'op':op,'var':name,'sort':self.ids['Object'],'body':body}
    def evaluate(self,node,**kwargs):return s.evaluate(self.subject,self.model,node,**kwargs)
    def fault(self,code,callback):
        with self.assertRaises(s.ModelFault) as caught:callback()
        self.assertEqual(code,caught.exception.code)

    def test_complete_model_has_exact_total_interpretations(self):
        structure=s.validate_model(self.subject['declarations'],self.model);self.assertEqual('b',structure['functions'][self.ids['flip']][('a',)])
        truth=self.evaluate(self.quant('exists',self.pred('P',self.v())));self.assertTrue(truth['truth']);self.assertFalse(truth['semantic_ready'])

    def test_hand_derived_boolean_truth_table_twenty_comparisons(self):
        expected={(False,False):[True,False,False,True,True],(False,True):[True,False,True,True,False],(True,False):[False,False,True,False,False],(True,True):[False,True,True,True,True]}
        c={'op':'const','name':self.ids['c']};p=self.pred('P',c);q=self.pred('Q',c)
        forms=[{'op':'not','arg':p},{'op':'and','args':[p,q]},{'op':'or','args':[p,q]},{'op':'implies','left':p,'right':q},{'op':'iff','left':p,'right':q}]
        for (left,right),truths in expected.items():
            self.model['predicates'][self.ids['P']]=[['a']] if left else [];self.model['predicates'][self.ids['Q']]=[['a']] if right else []
            self.assertEqual(truths,[self.evaluate(form)['truth'] for form in forms])

    def test_hand_derived_row_neighbor_and_common_column_quantifiers(self):
        body=self.pred('R',self.v('x'),self.v('y'))
        row=self.quant('forall',self.quant('exists',body,'y'),'x');column=self.quant('exists',self.quant('forall',body,'x'),'y')
        cases=[([],False,False),([['a','a'],['b','b']],True,False),([['a','a'],['b','a']],True,True),([['a','a']],False,False)]
        for extension,rows,common in cases:
            self.model['predicates'][self.ids['R']]=extension;self.assertEqual(rows,self.evaluate(row)['truth']);self.assertEqual(common,self.evaluate(column)['truth'])

    def test_constant_function_application_and_equality(self):
        c={'op':'const','name':self.ids['c']};flip={'op':'fn','name':self.ids['flip'],'args':[c]};twice={'op':'fn','name':self.ids['flip'],'args':[flip]}
        self.assertTrue(self.evaluate({'op':'eq','left':c,'right':twice})['truth']);self.assertFalse(self.evaluate(self.pred('P',flip))['truth'])

    def test_empty_domains_rejected_and_empty_predicates_valid_false(self):
        self.model['predicates'][self.ids['P']]=[];self.assertFalse(self.evaluate(self.quant('exists',self.pred('P',self.v())))['truth'])
        self.model['domains'][self.ids['Object']]=[];out=s.try_evaluate(self.subject,self.model,{'op':'and','args':[]});self.assertEqual('malformed',out['status']);self.assertNotIn('truth',out)

    def test_missing_interpretation_never_closed_world_false(self):
        self.model['predicates'].pop(self.ids['Q']);out=s.try_evaluate(self.subject,self.model,self.pred('Flag'));self.assertEqual('malformed',out['status']);self.assertNotIn('truth',out)

    def test_extra_unknown_interpretation_and_boolean_atom_rejected(self):
        self.model['predicates']['unknown']=[];self.fault('incomplete-or-extra-model-interpretation',lambda:s.validate_model(self.subject['declarations'],self.model))
        self.model['predicates'].pop('unknown');self.model['constants'][self.ids['c']]=True;self.fault('ill-sorted-constant',lambda:s.validate_model(self.subject['declarations'],self.model))

    def test_function_totality_duplicates_and_result_sort(self):
        original=copy.deepcopy(self.model)
        self.model['functions'][self.ids['flip']].pop();self.fault('nontotal-function-interpretation',lambda:s.validate_model(self.subject['declarations'],self.model))
        self.model=copy.deepcopy(original);self.model['functions'][self.ids['flip']].append(copy.deepcopy(self.model['functions'][self.ids['flip']][0]));self.fault('duplicate-function-tuple',lambda:s.validate_model(self.subject['declarations'],self.model))
        self.model=original;self.model['functions'][self.ids['flip']][0]['value']='outside';self.fault('ill-sorted-function-result',lambda:s.validate_model(self.subject['declarations'],self.model))

    def test_predicate_tuple_arity_sort_and_duplicate(self):
        for extension,code in [([['a']],'ill-sorted-model-tuple'),([['a','outside']],'ill-sorted-model-tuple'),([['a','b'],['a','b']],'duplicate-predicate-tuple')]:
            self.model['predicates'][self.ids['R']]=extension;self.fault(code,lambda:s.validate_model(self.subject['declarations'],self.model))

    def test_zero_arity_predicate_and_empty_connectives(self):
        self.assertFalse(self.evaluate(self.pred('Flag'))['truth']);self.model['predicates'][self.ids['Flag']]=[[]];self.assertTrue(self.evaluate(self.pred('Flag'))['truth'])
        self.assertTrue(self.evaluate({'op':'and','args':[]})['truth']);self.assertFalse(self.evaluate({'op':'or','args':[]})['truth'])

    def test_theory_population_target_separation_no_target_insertion(self):
        self.model['predicates'][self.ids['P']]=[['a'],['b']];self.model['predicates'][self.ids['Q']]=[]
        theory=[self.quant('forall',self.pred('P',self.v()))];population=[self.quant('exists',self.pred('P',self.v()))];target=[self.quant('forall',self.pred('Q',self.v()))];saved=copy.deepcopy(theory)
        out=s.assess(self.subject,self.model,theory,population,target);self.assertEqual('model-local-counterexample',out['status']);self.assertTrue(out['theory_satisfied']);self.assertEqual([False],out['targets']);self.assertEqual(saved,theory)

    def test_joint_population_guard_and_invalid_premise_model(self):
        self.model['predicates'][self.ids['Q']]=[];pop=[self.quant('exists',self.pred(name,self.v())) for name in ['P','Q']]
        out=s.assess(self.subject,self.model,[],pop,[{'op':'and','args':[]}]);self.assertEqual('vacuous-required-population',out['status']);self.assertEqual([],out['targets'])
        out=s.assess(self.subject,self.model,[self.quant('forall',self.pred('Q',self.v()))],[],[{'op':'and','args':[]}]);self.assertEqual('model-theory-counterexample',out['status']);self.assertEqual([],out['targets'])

    def test_cancellation_and_limits_have_no_truth_value(self):
        node=self.quant('forall',self.pred('P',self.v()))
        for options,status in [({'max_steps':1},'resource-limit'),({'cancelled':lambda:True},'cancelled')]:
            out=s.try_evaluate(self.subject,self.model,node,**options);self.assertEqual(status,out['status']);self.assertNotIn('truth',out)
        with patch.object(s,'MAX_TUPLE_SPACE',0):
            out=s.try_evaluate(self.subject,self.model,node);self.assertEqual('resource-limit',out['status']);self.assertNotIn('truth',out)

    def test_unsupported_operator_and_malformed_formula_have_no_truth(self):
        out=s.try_evaluate(self.subject,self.model,{'op':'eventually','body':{'op':'and','args':[]}});self.assertEqual('unsupported',out['status']);self.assertNotIn('truth',out)
        out=s.try_evaluate(self.subject,self.model,{'op':'pred','name':True,'args':[]});self.assertEqual('malformed',out['status']);self.assertNotIn('truth',out)

    def test_alias_subtype_properness_and_overlap_hand_models(self):
        x=self.v();P=self.pred('P',x);Q=self.pred('Q',x)
        alias=self.quant('forall',{'op':'iff','left':P,'right':Q});inclusion=self.quant('forall',{'op':'implies','left':P,'right':Q});proper=self.quant('exists',{'op':'and','args':[Q,{'op':'not','arg':P}]});intersection=self.quant('exists',{'op':'and','args':[P,Q]})
        self.assertTrue(self.evaluate(alias)['truth']);self.assertFalse(self.evaluate(proper)['truth'])
        self.model['predicates'][self.ids['Q']]=[['a'],['b']]
        self.assertFalse(self.evaluate(alias)['truth']);self.assertTrue(self.evaluate(inclusion)['truth']);self.assertTrue(self.evaluate(proper)['truth']);self.assertTrue(self.evaluate(intersection)['truth'])
        self.model['predicates'][self.ids['Q']]=[['b']];self.assertFalse(self.evaluate(inclusion)['truth']);self.assertFalse(self.evaluate(intersection)['truth'])

    def test_zero_arity_total_function_requires_the_empty_argument_tuple(self):
        core=copy.deepcopy(self.subject['input_core']);core['declarations'].append({'kind':'total-function','symbol_id':'unit','scope':core['scope'],'argument_sorts':[],'result_sort':'Object','definedness_policy':None})
        subject=s.ir.compile_interpretation(core);identity=s.ir.qualified(core['source'],core['scope'],'unit');model=copy.deepcopy(self.model);model['functions'][identity]=[{'args':[],'value':'a'}]
        self.assertTrue(s.evaluate(subject,model,{'op':'eq','left':{'op':'fn','name':identity,'args':[]},'right':{'op':'const','name':self.ids['c']}})['truth'])
        model['functions'][identity]=[];self.fault('nontotal-function-interpretation',lambda:s.validate_model(subject['declarations'],model))

    def test_decoder_to_typed_parser_to_satisfaction_correspondence(self):
        raw=json.dumps({'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':self.subject['input_core']}).encode()
        decoded=s.c.decode(raw,'interpretation');self.assertEqual('structurally-valid',decoded['status'])
        subject=s.ir.compile_interpretation(decoded['data']['payload']);node=subject['clauses'][0]['formal_statement']
        self.assertFalse(s.evaluate(subject,self.model,node)['truth']);self.model['predicates'][self.ids['P']]=[['a'],['b']];self.assertTrue(s.evaluate(subject,self.model,node)['truth'])


    def test_composed_subject_requires_independent_inputs(self):
        joined=s.ir.compose([self.subject]);node=self.quant('exists',self.pred('P',self.v()))
        out=s.try_evaluate(joined,self.model,node);self.assertEqual('malformed',out['status']);self.assertNotIn('truth',out)
        self.assertTrue(s.evaluate(joined,self.model,node,selected_inputs=[self.subject])['truth'])


if __name__=='__main__':unittest.main()
