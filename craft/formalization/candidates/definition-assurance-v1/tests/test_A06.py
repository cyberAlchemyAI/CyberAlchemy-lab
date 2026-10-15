import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
HERE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(HERE));sys.path.insert(0,str(HERE/'tests'))
import obligations as o
import test_A05 as fixtures


class ObligationControls(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        relation,bindings,self.populations=fixtures.setup_relation(self.root)
        self.bindings=bindings;self.requests=[{'relation':relation,'bindings':bindings,'proper':False,'distinction':'permitted','forbidden':[]}]
        scope=relation['scope']
        declarations=[{'kind':'sort','symbol_id':'Object','scope':scope,'domain_policy':'nonempty'}]+[{'kind':'predicate','symbol_id':name,'scope':scope,'argument_sorts':['Object']} for name in ['P','Q']]
        self.theory={'theory_id':'T1','sources':[relation['left_definition'],relation['right_definition']],'declarations':declarations,'statements':[],'assumption_set_id':'CTX1','scope':scope,'change_class':'initial','prior_theory_ref':None}

    def generate(self):return o.generate(self.theory,self.requests,self.populations,self.bindings,self.root)
    def fault(self,callback,code='required-set-omitted-substituted-weakened-or-stale'):
        with self.assertRaises(o.ObligationFault) as caught:callback()
        self.assertEqual(code,caught.exception.code)

    def test_required_set_contains_independent_alias_population_and_fidelity_requirements(self):
        required=self.generate();logical=required['logical_manifest']['obligations'];keys={row['obligation_id'] for row in logical}
        self.assertEqual({'query:consistency','query:joint-population','population:POP-P','population:POP-Q','relation:R1:equivalence'},keys)
        alias=next(row for row in logical if row['obligation_id']=='relation:R1:equivalence');self.assertEqual('forall',alias['statement']['op']);self.assertEqual('iff',alias['statement']['body']['op']);self.assertEqual('mechanized-theorem',alias['minimum_strength'])
        self.assertEqual(2,sum(row['check']=='source-fidelity' for row in required['administrative_and_semantic_gates']))
        result=o.verify_submission(self.theory,self.requests,self.populations,self.bindings,self.root,required);self.assertEqual('required-set-identical',result['status']);self.assertFalse(result['semantic_ready']);self.assertFalse(result['evidence_verified'])

    def test_remove_each_obligation_gate_and_query_requirement_rejected(self):
        expected=self.generate()
        for container,key in [('logical_manifest','obligations'),(None,'administrative_and_semantic_gates'),(None,'query_requirements')]:
            rows=expected[container][key] if container else expected[key]
            for index in range(len(rows)):
                with self.subTest(key=key,index=index):
                    submitted=copy.deepcopy(expected);(submitted[container][key] if container else submitted[key]).pop(index);self.fault(lambda:o.compare_required(expected,submitted))

    def test_weaken_formula_strength_context_or_prerequisites_rejected(self):
        expected=self.generate()
        mutations=[lambda x:x['logical_manifest']['obligations'][0].update(statement={'op':'and','args':[]}),lambda x:x['logical_manifest']['obligations'][0].update(minimum_strength='structural'),lambda x:x['logical_manifest']['obligations'][0].update(assumption_set_ref='Other'),lambda x:x['query_requirements'][0].update(prerequisites=[]),lambda x:x['logical_manifest'].update(theory_sha256='0'*64),lambda x:x.update(signature_sha256='0'*64),lambda x:x['administrative_and_semantic_gates'][0].update(status='exempt')]
        for mutation in mutations:
            changed=copy.deepcopy(expected);mutation(changed);self.fault(lambda:o.compare_required(expected,changed))

    def test_joint_populations_in_one_conjunction_not_independent_models(self):
        required=self.generate();joint=next(row for row in required['logical_manifest']['obligations'] if row['obligation_id']=='query:joint-population')
        self.assertEqual('and',joint['statement']['op']);self.assertEqual(2,len(joint['statement']['args']));self.assertTrue(all(row['op']=='exists' for row in joint['statement']['args']))
        selected=next(row for row in required['query_requirements'] if row['obligation_id']=='relation:R1:equivalence');self.assertIn('query:joint-population',selected['prerequisites'])

    def test_drop_endpoint_binding_or_population_cannot_shrink_denominator(self):
        self.bindings.pop('right');self.fault(self.generate,'relation-endpoint-not-in-population-scope')
        self.requests=[];self.fault(self.generate,'signature-population-denominator-mismatch')

    def test_exemption_keeps_required_semantic_review_gate(self):
        self.populations[0].update(requirement='exempt',statement=None,review_ref={'path':'review.json','sha256':'0'*64})
        required=self.generate();gates=required['administrative_and_semantic_gates'];self.assertTrue(any(row['check']=='population-exemption-review' for row in gates))
        changed=copy.deepcopy(required);changed['administrative_and_semantic_gates']=[row for row in gates if row['check']!='population-exemption-review'];self.fault(lambda:o.compare_required(required,changed))

    def test_unresolved_population_keeps_formula_and_policy_review(self):
        self.populations[0].update(requirement='unresolved',statement=None)
        required=self.generate();self.assertTrue(any(row['obligation_id']=='population:POP-P' for row in required['logical_manifest']['obligations']));self.assertTrue(any(row['check']=='population-policy-review' for row in required['administrative_and_semantic_gates']))

    def test_additive_change_requires_exact_prior_and_conservativity(self):
        self.theory['change_class']='additive';self.fault(self.generate,'missing-or-inapplicable-prior-binding')
        self.theory['prior_theory_ref']={'path':'prior-theory.json','sha256':'0'*64};required=self.generate();gate=next(row for row in required['administrative_and_semantic_gates'] if row['check']=='conservativity');self.assertEqual('mechanized-theorem',gate['minimum_strength'])

    def test_signature_or_theory_change_invalidates_old_required_set(self):
        old=self.generate();self.theory['statements']=[{'op':'forall','var':'x','sort':'Object','body':o.p.pred('P')}];new=self.generate();self.assertNotEqual(old['logical_manifest']['theory_sha256'],new['logical_manifest']['theory_sha256']);self.fault(lambda:o.verify_submission(self.theory,self.requests,self.populations,self.bindings,self.root,old))
        self.theory['declarations'].append({'kind':'predicate','symbol_id':'Nary','scope':self.theory['scope'],'argument_sorts':['Object','Object']});third=self.generate();self.assertNotEqual(new['signature_sha256'],third['signature_sha256']);self.assertTrue(any(row['check']=='nonunary-population-profile-review' for row in third['administrative_and_semantic_gates']))

    def test_unknown_marker_authority_or_duplicate_obligation_rejected(self):
        expected=self.generate()
        for mutation in [lambda x:x.update(authority_effect='admitted'),lambda x:x.update(extra=True),lambda x:x['logical_manifest']['obligations'].append(copy.deepcopy(x['logical_manifest']['obligations'][0]))]:
            changed=copy.deepcopy(expected);mutation(changed);self.fault(lambda:o.compare_required(expected,changed))

    def test_deterministic_repeated_generation(self):self.assertEqual(self.generate(),self.generate())


if __name__=='__main__':unittest.main()
