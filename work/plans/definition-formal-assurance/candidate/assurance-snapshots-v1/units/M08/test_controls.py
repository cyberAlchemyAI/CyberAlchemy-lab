import unittest
from itertools import product
from finite_models import *


def signature(names=('A','B'),domain=('a','b')):
    return {'domains':{'Object':list(domain)},'constants':{},'functions':{},'predicates':{name:['Object'] for name in names},'fixed_predicates':{}}


class FoundationControls(unittest.TestCase):
    def test_boolean_denotation_against_complete_independent_truth_table(self):
        sig=signature(('p','q'));sig['predicates']={'p':[],'q':[]}
        p,q=predicate('p'),predicate('q')
        for left,right in product((False,True),repeat=2):
            model={'p':{()} if left else set(),'q':{()} if right else set()}
            for formula,expected in [(conjunction(p,q),left and right),(disjunction(p,q),left or right),(implication(p,q),(not left) or right),(equivalence(p,q),left==right),(negate(p),not left)]:
                validate_formula(formula,sig)
                self.assertEqual(satisfies(formula,sig,model),expected)

    def test_quantified_denotation_against_all_64_direct_relational_cases(self):
        sig=signature(('P',));sig['predicates']['R']=['Object','Object']
        x,y=variable('x'),variable('y')
        query=forall('x','Object',exists('y','Object',conjunction(predicate('R',x,y),predicate('P',y))))
        validate_formula(query,sig)
        count=0
        for model in models(sig):
            direct=all(any((a,b) in model['R'] and (b,) in model['P'] for b in sig['domains']['Object']) for a in sig['domains']['Object'])
            self.assertEqual(satisfies(query,sig,model),direct);count+=1
        self.assertEqual(count,64)

    def test_typed_total_function_and_equality(self):
        sig=signature(())
        sig['constants']['a']=('Object','a')
        sig['functions']['flip']=(['Object'],'Object',{('a',):'b',('b',):'a'})
        query=forall('x','Object',equality(function('flip',function('flip',variable('x'))),variable('x')))
        self.assertEqual(search(sig,[query])['outcome'],'finite-sat')
        sig['functions']['flip'][2].pop(('a',))
        with self.assertRaises(Malformed):search(sig,[query])

    def test_unaligned_carriers_free_variables_and_extra_ast_fields(self):
        sig=signature()
        sig['domains']['Other']=['a']
        sig['constants']={'a':('Object','a'),'other':('Other','a')}
        for query in [equality(constant('a'),constant('other')),predicate('A',variable('free')),{'op':'exists','var':'x','sort':'Object','body':predicate('A',variable('x')),'ignored':True}]:
            with self.assertRaises(Malformed):search(sig,[query])

    def test_alias_has_no_forced_difference(self):
        sig=signature();x=variable('x')
        theory=[forall('x','Object',equivalence(predicate('A',x),predicate('B',x)))]
        pop=exists('x','Object',predicate('A',x))
        difference=exists('x','Object',negate(equivalence(predicate('A',x),predicate('B',x))))
        self.assertEqual(search(sig,[*theory,pop])['outcome'],'finite-sat')
        self.assertEqual(search(sig,[*theory,pop,difference])['outcome'],'bounded-unsat')

    def test_proper_subtype_retains_overlap(self):
        sig=signature(('Child','Parent'));x=variable('x')
        theory=[forall('x','Object',implication(predicate('Child',x),predicate('Parent',x))),exists('x','Object',predicate('Child',x)),exists('x','Object',conjunction(predicate('Parent',x),negate(predicate('Child',x))))]
        result=search(sig,theory)
        self.assertEqual(result['outcome'],'finite-sat')
        child={tuple(t) for t in result['model']['Child']};parent={tuple(t) for t in result['model']['Parent']}
        self.assertTrue(child and child<parent)

    def test_pairwise_satisfiable_triple_is_jointly_inconsistent(self):
        sig=signature(('p','q'));sig['predicates']={'p':[],'q':[]}
        p,q=predicate('p'),predicate('q');theory=[p,q,negate(conjunction(p,q))]
        for pair in [(theory[0],theory[1]),(theory[0],theory[2]),(theory[1],theory[2])]:
            self.assertEqual(search(sig,pair)['outcome'],'finite-sat')
        result=search(sig,theory)
        self.assertEqual((result['outcome'],result['examined']),('bounded-unsat',4))
        self.assertEqual(bounded_entailment(sig,theory,p)['outcome'],'inconsistent-or-unresolved-premises')

    def test_required_population_not_empty_sort_distinguishes_vacuity(self):
        sig=signature(('A',));x=variable('x')
        theory=[forall('x','Object',negate(predicate('A',x)))]
        inhabit=exists('x','Object',predicate('A',x))
        self.assertEqual(search(sig,theory)['outcome'],'finite-sat')
        self.assertEqual(search(sig,[*theory,inhabit])['outcome'],'bounded-unsat')
        self.assertEqual(bounded_entailment(sig,theory,inhabit,[inhabit])['outcome'],'vacuous-or-unresolved-populations')
        sig['domains']['Object']=[]
        with self.assertRaises(Malformed):search(sig,theory)

    def test_witness_distinction_is_weaker_than_all_model_separation(self):
        sig=signature();x=variable('x')
        difference=exists('x','Object',negate(equivalence(predicate('A',x),predicate('B',x))))
        self.assertEqual(search(sig,[difference])['outcome'],'finite-sat')
        self.assertEqual(bounded_entailment(sig,[],difference)['outcome'],'counterexample')

    def test_claim_without_grant_and_allowed_coupling_both_expressible(self):
        sig=signature(('Claim','Grant'),('a',));x=variable('x')
        ungranted=exists('x','Object',conjunction(predicate('Claim',x),negate(predicate('Grant',x))))
        coupled=exists('x','Object',conjunction(predicate('Claim',x),predicate('Grant',x)))
        self.assertEqual(search(sig,[ungranted])['outcome'],'finite-sat')
        self.assertEqual(search(sig,[coupled])['outcome'],'finite-sat')

    def test_invariant_preservation_counterexample_not_assumed(self):
        sig=signature(('Good',),('s0','s1','s2'));sig['predicates']['Next']=['Object','Object']
        sig['fixed_predicates']={'Good':{('s0',),('s1',)},'Next':{('s0','s1'),('s1','s2')}}
        s,t=variable('s'),variable('t')
        target=forall('s','Object',forall('t','Object',implication(conjunction(predicate('Good',s),predicate('Next',s,t)),predicate('Good',t))))
        result=bounded_entailment(sig,[],target)
        self.assertEqual(result['outcome'],'counterexample')
        direct_bad=[(a,b) for a,b in sig['fixed_predicates']['Next'] if (a,) in sig['fixed_predicates']['Good'] and (b,) not in sig['fixed_predicates']['Good']]
        self.assertEqual(direct_bad,[('s1','s2')])

    def test_recursive_equivalence_allows_non_least_reachability(self):
        sig=signature(('Initial','Reachable'),('a','b'));sig['predicates']['Next']=['Object','Object']
        sig['fixed_predicates']={'Initial':{('a',)},'Next':{('b','b')}}
        x,p=variable('x'),variable('p')
        equation=forall('x','Object',equivalence(predicate('Reachable',x),disjunction(predicate('Initial',x),exists('p','Object',conjunction(predicate('Reachable',p),predicate('Next',p,x))))))
        accepted=[model['Reachable'] for model in models(sig) if satisfies(equation,sig,model)]
        self.assertEqual(accepted,[{('a',)},{('a',),('b',)}])
        self.assertEqual(least_reachable({'a'},{('b','b')}),{'a'})

    def test_hypothesis_and_target_are_not_silently_assumed(self):
        sig=signature(('p',));sig['predicates']={'p':[]};p=predicate('p')
        self.assertEqual(assemble([{'id':'h','role':'hypothesis','selected':False,'formula':p}]),[])
        for role in ['hypothesis','proof-obligation','explanation-example']:
            with self.assertRaises(Malformed):assemble([{'id':'h','role':role,'selected':True,'formula':p}])
        with self.assertRaises(Malformed):assemble([{'id':'target','role':'selected-premise','selected':True,'formula':p}],target_id='target')
        self.assertEqual(assemble([{'id':'premise','role':'selected-premise','selected':True,'formula':p}]),[p])

    def test_unknown_resource_result_never_becomes_exhaustive_absence(self):
        sig=signature(('A',));x=variable('x');target=exists('x','Object',predicate('A',x))
        result=search(sig,[target],model_limit=1)
        self.assertEqual((result['outcome'],result['exhausted']),('resource-limit',False))
        result=search(sig,[target],cancelled=lambda:True)
        self.assertEqual((result['outcome'],result['examined'],result['exhausted']),('cancelled',0,False))

    def test_unsupported_logic_is_distinct_from_malformed_input(self):
        sig=signature()
        with self.assertRaises(Unsupported):search(sig,[{'op':'eventually','body':predicate('A',constant('a'))}])
        with self.assertRaises(Malformed):search(sig,[{'body':predicate('A',constant('a'))}])

    def test_statement_identity_substitution_and_unsupported_evidence_roles(self):
        p=predicate('p')
        for clauses in [
            [{'id':'t','role':'proof-obligation','selected':False,'formula':p},{'id':'different','role':'selected-premise','selected':True,'formula':p}],
            [{'id':'x','role':'definition','selected':True,'formula':p},{'id':'x','role':'definition','selected':True,'formula':p}],
            [{'id':'x','role':'unknown-role','selected':False,'formula':p}]]:
            with self.assertRaises(Malformed):assemble(clauses,target_id='t')
        for role in ['derived-claim','observation-measurement','unresolved']:
            with self.assertRaises(Unsupported):assemble([{'id':'x','role':role,'selected':True,'formula':p}])


if __name__=='__main__':unittest.main()
