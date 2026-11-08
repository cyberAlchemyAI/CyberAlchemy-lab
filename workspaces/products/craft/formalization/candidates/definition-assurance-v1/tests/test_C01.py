import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
HERE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(HERE));sys.path.insert(0,str(HERE/'tests'))
import ir
import test_A01 as fixtures
import test_A05 as relations


class TypeControls(unittest.TestCase):
    def setUp(self):self.core=fixtures.payloads()['interpretation']
    def compile(self):return ir.compile_interpretation(self.core)
    def fault(self,code,callback=None):
        with self.assertRaises(ir.IRFault) as caught:(callback or self.compile)()
        self.assertEqual(code,caught.exception.code)

    def test_valid_closed_formula_and_preserved_origin_namespace(self):
        result=self.compile();self.assertTrue(ir.verify_ir(result));self.assertFalse(result['semantic_ready']);self.assertEqual('not-assessed',result['noncollapse'])
        identity=ir.qualified(self.core['source'],self.core['scope'],'P');self.assertEqual(identity,result['clauses'][0]['formal_statement']['body']['name'])
        origin=next(row for row in result['origins'] if row['local_symbol_id']=='P');self.assertEqual(self.core['source']['version_ref'],origin['version_ref'])

    def test_equal_labels_different_source_version_scope_have_distinct_symbols(self):
        a=self.compile();b=copy.deepcopy(self.core);b['source']=fixtures.source('cal.definition.other');different=ir.compile_interpretation(b)
        self.assertNotEqual(a['declarations'][0]['symbol_id'],different['declarations'][0]['symbol_id'])
        b=copy.deepcopy(self.core);b['source']=fixtures.source(version='2.0.0');self.assertNotEqual(a['ir_sha256'],ir.compile_interpretation(b)['ir_sha256'])
        b=copy.deepcopy(self.core);b['scope']='other-scope'
        for row in b['declarations']:row['scope']='other-scope'
        self.assertNotEqual(a['declarations'][0]['symbol_id'],ir.compile_interpretation(b)['declarations'][0]['symbol_id'])

    def test_unbound_variable_and_predicate_arity_rejected(self):
        self.core['clauses'][0]['formal_statement']={'op':'pred','name':'P','args':[{'op':'var','name':'x'}]};self.fault('unbound-variable')
        self.core['clauses'][0]['formal_statement']={'op':'pred','name':'P','args':[]};self.fault('predicate-arity')

    def test_unknown_predicate_and_sort_rejected(self):
        self.core['clauses'][0]['formal_statement']['body']['name']='Missing';self.fault('unknown-or-wrong-kind-predicate')
        self.core['clauses'][0]['formal_statement']['body']['name']='P';self.core['clauses'][0]['formal_statement']['sort']='Unknown';self.fault('unbound-quantifier-sort-or-variable')

    def test_ill_sorted_predicate_and_equality_rejected(self):
        scope=self.core['scope'];self.core['declarations'] += [{'kind':'sort','symbol_id':'Other','scope':scope,'domain_policy':'nonempty'},{'kind':'constant','symbol_id':'k','scope':scope,'result_sort':'Other'},{'kind':'constant','symbol_id':'c','scope':scope,'result_sort':'Object'}]
        self.core['clauses'][0]['formal_statement']={'op':'pred','name':'P','args':[{'op':'const','name':'k'}]};self.fault('predicate-argument-sort')
        self.core['clauses'][0]['formal_statement']={'op':'eq','left':{'op':'const','name':'c'},'right':{'op':'const','name':'k'}};self.fault('unaligned-equality-sorts')

    def test_total_functions_repeated_arguments_and_zero_arity_predicates(self):
        scope=self.core['scope'];self.core['declarations'] += [{'kind':'constant','symbol_id':'c','scope':scope,'result_sort':'Object'},{'kind':'total-function','symbol_id':'f','scope':scope,'argument_sorts':['Object','Object'],'result_sort':'Object','definedness_policy':None},{'kind':'predicate','symbol_id':'Flag','scope':scope,'argument_sorts':[]}]
        atom={'op':'const','name':'c'};self.core['clauses'][0]['formal_statement']={'op':'and','args':[{'op':'pred','name':'P','args':[{'op':'fn','name':'f','args':[atom,atom]}]},{'op':'pred','name':'Flag','args':[]}]};self.assertTrue(ir.verify_ir(self.compile()))
        self.core['clauses'][0]['formal_statement']['args'][0]['args'][0]['args'].pop();self.fault('function-arity')

    def test_quantifier_shadowing_keeps_lexical_sort_and_outer_environment(self):
        self.core['declarations'].append({'kind':'sort','symbol_id':'Other','scope':self.core['scope'],'domain_policy':'nonempty'})
        inner={'op':'forall','var':'x','sort':'Other','body':{'op':'eq','left':{'op':'var','name':'x'},'right':{'op':'var','name':'x'}}}
        self.core['clauses'][0]['formal_statement']={'op':'forall','var':'x','sort':'Object','body':{'op':'and','args':[inner,{'op':'pred','name':'P','args':[{'op':'var','name':'x'}]}]}}
        result=self.compile();self.assertTrue(ir.verify_ir(result))

    def test_partial_function_and_extension_features_are_unsupported(self):
        for feature in ['temporal','inductive-fixed-point','normative-deontic','empirical-probabilistic','unresolved']:
            self.core['logic_features']=[feature]
            with self.assertRaises(ir.Unsupported):self.compile()
        self.core['logic_features']=['first-order'];self.core['declarations'].append({'kind':'partial-function','symbol_id':'f','scope':self.core['scope'],'argument_sorts':['Object'],'result_sort':'Object','definedness_policy':'explicit graph needed'})
        with self.assertRaises(ir.Unsupported):self.compile()

    def test_unknown_ast_marker_and_duplicate_symbol_are_malformed(self):
        self.core['clauses'][0]['formal_statement']['ignored']=True;self.fault('malformed-interpretation');self.core['clauses'][0]['formal_statement'].pop('ignored')
        self.core['declarations'].append(copy.deepcopy(self.core['declarations'][0]));self.fault('malformed-interpretation')

    def test_deterministic_declaration_order_and_no_self_rehashed_type_forgery(self):
        result=self.compile();self.core['declarations'].reverse();reordered=self.compile()
        self.assertEqual(result['declarations'],reordered['declarations'])
        # Raw-input provenance binds the order even when the canonical signature agrees.
        self.assertNotEqual(result['input_core_sha256'],reordered['input_core_sha256'])
        forged=copy.deepcopy(result);forged['declarations'][0]['kind']='predicate';forged['ir_sha256']=ir.digest({k:v for k,v in forged.items() if k!='ir_sha256'});self.fault('stale-or-forged-IR',lambda:ir.verify_ir(forged))

    def test_nominal_sort_separation_not_proof_of_semantic_difference(self):
        a=self.compile();b=copy.deepcopy(self.core);b['source']=fixtures.source('cal.definition.other');joined=ir.compose([a,ir.compile_interpretation(b)])
        self.assertEqual(2,sum(row['kind']=='sort' for row in joined['declarations']));self.assertEqual('not-assessed',joined['noncollapse']);self.assertFalse(joined['semantic_ready'])
        self.fault('duplicate-interpretation-namespace',lambda:ir.compose([a,a]))

    def test_explicit_shared_carrier_alignment_enables_cross_predicate_query(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);relation,_,_=relations.setup_relation(root)
            cores=[]
            for side in ['left','right']:
                core=copy.deepcopy(self.core);core['source']=relation[side+'_definition'];core['scope']=relation['scope']
                for row in core['declarations']:row['scope']=relation['scope']
                cores.append(ir.compile_interpretation(core))
            a,b=cores;joined=ir.compose(cores)
            sort=ir.qualified(a['source'],a['scope'],'Object');pa=ir.qualified(a['source'],a['scope'],'P');pb=ir.qualified(b['source'],b['scope'],'P')
            query={'op':'forall','var':'x','sort':sort,'body':{'op':'iff','left':{'op':'pred','name':pa,'args':[{'op':'var','name':'x'}]},'right':{'op':'pred','name':pb,'args':[{'op':'var','name':'x'}]}}}
            self.fault('predicate-argument-sort',lambda:ir.check_composed_formula(joined,query))
            aligned=ir.compose(cores,[relation['alignment']['map_ref']],root);query['sort']=aligned['sort_alignment'][sort]
            self.assertEqual(query,ir.check_composed_formula(aligned,query));self.assertEqual(1,sum(row['kind']=='sort' for row in aligned['declarations']));self.assertFalse(aligned['semantic_ready'])
            ref=relation['alignment']['map_ref'];(root/ref['path']).write_bytes(b'{}');self.fault('stale-carrier-alignment',lambda:ir.compose(cores,[ref],root))

    def test_rehashed_composition_cannot_substitute_independent_inputs(self):
        source=self.compile();joined=ir.compose([source]);self.assertTrue(ir.verify_composed(joined,[source],[]))
        changed=copy.deepcopy(joined);changed['clauses']=[];changed['ir_sha256']=ir.digest({k:v for k,v in changed.items() if k!='ir_sha256'})
        self.fault('composed-IR-input-or-alignment-substitution',lambda:ir.verify_composed(changed,[source],[]))


    def test_empty_connectives_and_malformed_composed_names(self):
        result=ir.compose([self.compile()]);self.assertEqual({'op':'and','args':[]},ir.check_composed_formula(result,{'op':'and','args':[]}))
        self.fault('malformed-symbol-name',lambda:ir.check_composed_formula(result,{'op':'pred','name':True,'args':[]}))
        with self.assertRaises(ir.Unsupported):ir.check_composed_formula(result,{'op':'eventually','body':{'op':'and','args':[]}})


if __name__=='__main__':unittest.main()
