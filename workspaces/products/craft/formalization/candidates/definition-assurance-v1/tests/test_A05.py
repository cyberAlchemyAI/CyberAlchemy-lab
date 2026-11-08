import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(HERE))
spec=importlib.util.spec_from_file_location('relation_policy',HERE/'relation-policy.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
import test_A01 as fixtures


def setup_relation(root,kind='alias',direction='both'):
    relation=fixtures.payloads()['relation'];relation.update(relation_class=kind,direction=direction,minimum_strength='mechanized-theorem')
    bindings={side:{'source':relation[side+'_definition'],'scope':relation['scope'],'predicate':name,'carrier':'Object'} for side,name in [('left','P'),('right','Q')]}
    doc={'schema_version':'definition-assurance-carrier-alignment/v1-candidate','authority_effect':'none','mapping_kind':'identity-shared-carrier','carrier':'Object','scope':relation['scope'],'left_source':relation['left_definition'],'right_source':relation['right_definition'],'reviewer_ref':'agent:fixture','review_basis':'Explicit synthetic shared carrier; no real source correspondence claim.','equivalence_claim':'none'}
    raw=json.dumps(doc).encode();(root/'alignment.json').write_bytes(raw);relation['alignment']={'status':'reviewed','map_ref':{'path':'alignment.json','sha256':p.r.digest(raw)}}
    populations=[{'population_id':'POP-'+name,'carrier':'Object','predicate_ref':name,'requirement':'required','statement':p.quant('exists','Object',p.pred(name)),'scope':relation['scope'],'rationale':'Required hypothetical inhabitant for this synthetic relation.','review_ref':None} for name in ['P','Q']]
    return relation,bindings,populations


class RelationControls(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name);self.relation,self.bindings,self.populations=setup_relation(self.root)

    def compile(self,**options):return p.compile_relation(self.relation,self.bindings,self.root,**options)
    def model(self,left,right,**options):return p.assess_model(self.compile(**options),p.compile_populations(self.populations,self.bindings,self.relation['scope']),['a','b','c'],{'P':left,'Q':right})
    def fault(self,code,callback):
        with self.assertRaises(p.PolicyFault) as caught:callback()
        self.assertEqual(code,caught.exception.code)

    def test_alias_no_forced_distinction_and_false_alias_countermodel(self):
        self.assertEqual('model-local-supported',self.model(['a'],['a'])['status']);self.assertEqual('model-local-counterexample',self.model(['a'],['b'])['status'])
        target=self.compile()[0];self.assertEqual('universal-property',target['query_type']);self.assertEqual('mechanized-theorem',target['minimum_strength']);self.assertFalse(self.model(['a'],['a'])['semantic_ready'])

    def test_subtype_direction_and_selected_properness(self):
        self.relation.update(relation_class='subtype',direction='forward')
        self.assertEqual('model-local-supported',self.model(['a'],['a','b'],proper=True)['status']);self.assertEqual('model-local-counterexample',self.model(['a'],['a'],proper=True)['status'])
        self.assertEqual('model-local-supported',self.model(['a'],['a'],proper=False)['status'])
        self.relation['direction']='reverse';self.assertEqual('model-local-supported',self.model(['a','b'],['a'],proper=True)['status'])

    def test_overlap_and_both_directed_differences(self):
        self.relation.update(relation_class='overlap-distinct',direction='both')
        self.assertEqual('model-local-supported',self.model(['a','b'],['b','c'])['status']);self.assertEqual('model-local-counterexample',self.model(['a'],['a'])['status'])
        self.assertEqual(3,len(self.compile()))

    def test_distinction_witness_not_all_model_proof(self):
        self.relation.update(relation_class='overlap-distinct',direction='forward')
        witness=self.compile(distinction='permitted')[-1];universal=self.compile(distinction='all-models')[-1]
        self.assertEqual(witness['statement'],universal['statement']);self.assertEqual('model-witness',witness['query_type']);self.assertEqual('universal-property',universal['query_type'])
        self.assertFalse(self.model(['a','b'],['b'],distinction='all-models')['semantic_ready'])

    def test_disjoint_positive_and_overlap_counterexample(self):
        self.relation.update(relation_class='disjoint',direction='both');self.assertEqual('model-local-supported',self.model(['a'],['b'])['status']);self.assertEqual('model-local-counterexample',self.model(['a'],['a'])['status'])

    def test_empty_required_population_precedes_vacuous_alias_success(self):
        self.assertEqual('vacuous-required-population',self.model([],[])['status'])
        self.populations.pop();self.fault('missing-population-policy',lambda:p.compile_populations(self.populations,self.bindings,self.relation['scope']))

    def test_population_target_not_weakened_or_replaced(self):
        self.populations[0]['statement']={'op':'forall','var':'x','sort':'Object','body':p.pred('P')}
        self.fault('population-statement-substitution',lambda:p.compile_populations(self.populations,self.bindings,self.relation['scope']))

    def test_exemption_requires_review_and_stays_pending(self):
        self.populations[0].update(requirement='exempt',statement=None)
        self.fault('unreviewable-population-exemption',lambda:p.compile_populations(self.populations,self.bindings,self.relation['scope']))
        self.populations[0]['review_ref']={'path':'review.json','sha256':'0'*64}
        targets=p.compile_populations(self.populations,self.bindings,self.relation['scope']);self.assertEqual('exemption-review-required',targets[0]['status'])
        self.assertEqual('unresolved-population-policy',p.assess_model(self.compile(),targets,['a'],{'P':[],'Q':['a']})['status'])

    def test_unresolved_population_keeps_existential_requirement(self):
        self.populations[0].update(requirement='unresolved',statement=None)
        targets=p.compile_populations(self.populations,self.bindings,self.relation['scope']);self.assertEqual('exists',targets[0]['statement']['op']);self.assertEqual('unresolved-policy',targets[0]['status'])

    def test_unaligned_label_and_stale_alignment_rejected(self):
        self.bindings['right']['carrier']='Other';self.fault('unaligned-carriers',self.compile);self.bindings['right']['carrier']='Object'
        self.relation['alignment']['status']='unresolved';self.fault('unresolved-carrier-alignment',self.compile)
        self.relation['alignment']['status']='reviewed';(self.root/'alignment.json').write_bytes(b'{}');self.fault('stale-alignment-binding',self.compile)

    def test_no_automatic_merge_from_identical_predicate_label(self):
        self.bindings['right']['predicate']='P';self.fault('collapsed-predicate-identity',self.compile)

    def test_endpoint_source_scope_and_unknown_marker_rejected(self):
        self.bindings['left']['source']=fixtures.source('cal.definition.wrong');self.fault('endpoint-source-scope-mismatch',self.compile)
        self.bindings['left']['source']=self.relation['left_definition'];self.bindings['left']['ignored']=True;self.fault('malformed-endpoint-binding',self.compile)

    def test_forbidden_inference_targets_are_named_and_directional(self):
        self.relation.update(relation_class='independent-axis',direction='none');self.fault('explicit-forbidden-inferences-required',self.compile)
        self.assertEqual('model-local-supported',self.model(['a'],['b'],forbidden=['left-implies-right','right-implies-left'])['status'])
        self.assertEqual('model-local-counterexample',self.model(['a'],['a','b'],forbidden=['left-implies-right'])['status'])

    def test_explicit_coupling_preserved_and_bool_integer_change_visible(self):
        before={'authority':False,'maturity':0};after={'authority':True,'maturity':1}
        self.assertFalse(p.check_axis_move(before,after,['maturity'],[])['frame_holds'])
        self.assertTrue(p.check_axis_move(before,after,['maturity'],['authority'])['frame_holds'])
        self.assertFalse(p.check_axis_move({'axis':True},{'axis':1},[],[])['frame_holds'])
        self.assertEqual(['axis'],p.check_axis_move({'axis':True},{'axis':1},['axis'],[])['changed_axes'])

    def test_statement_list_cannot_substitute_target_or_erase_generation(self):
        targets=self.compile();self.assertTrue(targets);self.relation['required_statements']=[p.quant('exists','Object',p.pred('P'))];self.fault('submitted-target-substitution',self.compile)

    def test_empty_target_list_never_reports_model_support(self):
        self.fault('empty-control-denominator',lambda:p.assess_model([],[],['a'],{}))


    def test_invalid_model_carrier_and_extension_rejected(self):
        targets=self.compile();pop=p.compile_populations(self.populations,self.bindings,self.relation['scope'])
        self.fault('invalid-model-carrier',lambda:p.assess_model(targets,pop,[],{'P':[],'Q':[]}))
        self.fault('invalid-model-extension',lambda:p.assess_model(targets,pop,['a'],{'P':['outside'],'Q':['a']}))


if __name__=='__main__':unittest.main()
