"""Produce exact worked-case evidence without editing source definitions."""
import hashlib
import json
from pathlib import Path
from finite_models import *

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
LAB=HERE.parents[6]
PLAN=LAB/'docs/plans/definition-formal-assurance/candidate/foundations-first-v1'


def signature(names=('A','B'),domain=('a','b')):
    return {'domains':{'Object':list(domain)},'constants':{},'functions':{},'predicates':{name:['Object'] for name in names},'fixed_predicates':{}}


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def produce(attempt=None):
    cases=[]
    def add(ident,aspect,sig,formulas,expected,note):
        result=search(sig,formulas)
        if result['outcome']!=expected:raise ValueError('Wrong control outcome: '+ident)
        replay=None
        if 'model' in result:
            model={name:{tuple(row) for row in extension} for name,extension in result['model'].items()}
            replay=all(satisfies(f,sig,model) for f in formulas)
            if not replay:raise ValueError('Unreplayable witness')
        cases.append({'id':ident,'origin':'synthetic finite worked control; not complete source translation','aspect':aspect,
                      'signature':{'domains':sig['domains'],'predicates':sig['predicates'],'fixed_predicates':serialize_model(sig['fixed_predicates'])},
                      'formulas':formulas,'expected_outcome':expected,'actual_result':result,'witness_replayed':replay,'explanation':note})
    sig=signature();x=variable('x')
    alias=forall('x','Object',equivalence(predicate('A',x),predicate('B',x)))
    pop=exists('x','Object',predicate('A',x))
    diff=exists('x','Object',negate(equivalence(predicate('A',x),predicate('B',x))))
    add('WC01','alias',sig,[alias,pop],'finite-sat','Equivalent concepts remain inhabited; a difference is not required for an alias.')
    add('WC02','collapse control',sig,[alias,pop,diff],'bounded-unsat','A forced alias cannot satisfy a selected distinction in this profile.')
    add('WC03','permitted distinction',sig,[diff],'finite-sat','A distinction is possible.')
    universal=bounded_entailment(sig,[],diff)
    assert universal['outcome']=='counterexample'
    cases.append({'id':'WC04','origin':'synthetic','aspect':'universal versus possible distinction','actual_result':universal,
                  'explanation':'The same unconstrained theory also permits equal extensions, so a possible difference is not a universal separation.'})
    sig=signature(('Child','Parent'))
    add('WC05','proper subtype with overlap',sig,[forall('x','Object',implication(predicate('Child',x),predicate('Parent',x))),exists('x','Object',predicate('Child',x)),exists('x','Object',conjunction(predicate('Parent',x),negate(predicate('Child',x))))],'finite-sat','The child is nonempty and properly included; overlap is required rather than rejected.')
    sig=signature(('p','q'));sig['predicates']={'p':[],'q':[]}
    p,q=predicate('p'),predicate('q');theory=[p,q,negate(conjunction(p,q))]
    for n,(a,b) in enumerate([(0,1),(0,2),(1,2)]):
        add('WC06-'+str(n),'pairwise consistency',sig,[theory[a],theory[b]],'finite-sat','This pair alone is consistent.')
    add('WC07','joint contradiction',sig,theory,'bounded-unsat','All three together have no Boolean assignment; three pairwise successes cannot be aggregated.')
    sig=signature(('A',));empty=[forall('x','Object',negate(predicate('A',x)))]
    add('WC08','satisfiable empty predicate',sig,empty,'finite-sat','The core domain is nonempty but A has no inhabitants.')
    add('WC09','required population control',sig,[*empty,exists('x','Object',predicate('A',x))],'bounded-unsat','Required inhabitation fails while the unconstrained population theory remains consistent.')
    sig=signature(('Good',),('s0','s1','s2'));sig['predicates']['Next']=['Object','Object']
    sig['fixed_predicates']={'Good':{('s0',),('s1',)},'Next':{('s0','s1'),('s1','s2')}}
    s,t=variable('s'),variable('t')
    preservation=forall('s','Object',forall('t','Object',implication(conjunction(predicate('Good',s),predicate('Next',s,t)),predicate('Good',t))))
    add('WC10','invariant-preservation counterexample',sig,[negate(preservation)],'finite-sat','The step s1 -> s2 violates the invariant. Preservation is checked, not assumed.')
    sig=signature(('Initial','Reachable'),('a','b'));sig['predicates']['Next']=['Object','Object']
    sig['fixed_predicates']={'Initial':{('a',)},'Next':{('b','b')}}
    p=variable('p')
    equation=forall('x','Object',equivalence(predicate('Reachable',x),disjunction(predicate('Initial',x),exists('p','Object',conjunction(predicate('Reachable',p),predicate('Next',p,x))))))
    fixed_points=[serialize_model(m)['Reachable'] for m in models(sig) if satisfies(equation,sig,m)]
    least=sorted(least_reachable({'a'},{('b','b')}))
    assert fixed_points==[[['a']],[['a'],['b']]] and least==['a']
    cases.append({'id':'WC11','origin':'synthetic','aspect':'inductive versus recursive meaning','fixed_points_of_equivalence':fixed_points,'least_reachable':least,
                  'explanation':'Recursive iff admits an extra self-supported state b; the selected least closure excludes it. This is a finite example, not a generic fixed-point proof.'})
    sig=signature(('Claim','Grant'),('a',))
    add('WC12','independent claim and grant',sig,[exists('x','Object',conjunction(predicate('Claim',x),negate(predicate('Grant',x))))],'finite-sat','An asserted claim can be represented without a grant. This is a representation control, not a complete Authority theory.')
    add('WC13','permitted claim-grant coupling',sig,[exists('x','Object',conjunction(predicate('Claim',x),predicate('Grant',x)))],'finite-sat','The model retains legitimate coupling rather than demanding disjoint predicates.')
    source_queue=json.loads((PLAN/'foundation-source-queue.json').read_text())['sources']
    annotations=json.loads((ROOT/'foundations/definition-kinds.json').read_text())['source_clause_annotations']
    bysource={a['definition_id']:a for a in annotations}
    source_cases=[]
    for row in source_queue:
        assert digest(LAB/row['source_path'])==row['source_sha256']
        source_cases.append({'definition_id':row['definition_id'],'version_ref':row['version_ref'],'source_path':row['source_path'],
                             'source_sha256':row['source_sha256'],'candidate_clause_annotation':bysource[row['definition_id']],
                             'worked_interpretation':bysource[row['definition_id']]['rationale'],
                             'fidelity':'selected clause annotated; whole source translation and owner correspondence not completed',
                             'finding':'Target investigation clause and inherited adopted-premise expression conflict.' if row['definition_id']=='cal.definition.hypothesis' else None})
    bundle={'schema_version':'definition-assurance-foundation-worked-cases/v1-candidate','authority_effect':'none','unit_id':'M08.1','cases':cases,
            'source_cases':source_cases,'module_binding':{'path':str((HERE/'finite_models.py').relative_to(LAB)),'sha256':digest(HERE/'finite_models.py')},
            'strength':'Checked finite model/control results plus source-bound candidate annotations. No full-source fidelity or generic soundness theorem.',
            'limitations':['No production IR/decoder/provider implemented.','No full 183-definition model checked.','No source-owner fidelity acceptance.','No mechanized universal evaluator/obligation-generator theorem.','Temporal/deontic/probabilistic extensions are specified entry contracts, not implemented profiles.']}
    output=ROOT/'foundations/worked-examples.json' if attempt is None else HERE/attempt/'worked-examples.json'
    output.parent.mkdir(parents=True,exist_ok=True)
    if output.exists():raise ValueError('Preserve prior case evidence; choose a new attempt.')
    output.write_text(json.dumps(bundle,indent=2,sort_keys=True)+'\n')
    return {'case_records':len(cases),'current_foundation_source_cases':len(source_cases),'replayed_model_witnesses':sum(c.get('witness_replayed') is True for c in cases)}


if __name__=='__main__':
    import argparse,re
    parser=argparse.ArgumentParser()
    parser.add_argument('--attempt')
    args=parser.parse_args()
    if args.attempt is not None and re.fullmatch(r'attempt-[0-9]{3}',args.attempt) is None:parser.error('Exact attempt-NNN name required')
    print(json.dumps(produce(args.attempt),indent=2))
