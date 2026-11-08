#!/usr/bin/env python3
"""Check both ground implications in one captured context plus coexistence."""
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import tempfile
import witness_checker as w
s=w.s;f=w.f;c=w.c
BASE=Path(__file__).resolve().parent


def fixtures():
    request=s.read(s.BASE/'inference/profile/coexistence-input.json');request['facts']=[]
    normal=f.normalize(request);root=c.raw_atom(normal['facts'][0]);target=request['domain'][0]
    conforms={'predicate':'Conforms','version':'v1','terms':[target]}
    signal={'predicate':'ReviewSignal','version':'v1','terms':[target]}
    admitted={'predicate':'Admitted','version':'v1','terms':[target,*request['domain'][2:5]]}
    def witness(model,claim):return {'schema':'relational.inference-model/v1','normal_form_identity':normal['normal_form_identity'],
                                    'model':deepcopy(model),'claim':claim}
    forward=witness([root,conforms,signal],{'kind':'non-entailment','premise':conforms,'conclusion':admitted})
    reverse=witness([root,admitted],{'kind':'non-entailment','premise':admitted,'conclusion':conforms})
    coexist=witness([root,conforms,signal,admitted],{'kind':'model-existence'})
    return request,normal,forward,reverse,coexist


def main():
    request,normal,forward,reverse,coexist=fixtures()
    s.context('I05',[(s.PLAN,'I05 complete model counterexamples and coexistence'),
        (s.BASE/'inference/profile/inference-semantics.md','closed Horn models and distinct negative claims'),
        (s.BASE/'evolution/models/model-audit.json','E04 exact model witness discipline'),
        (s.BASE/'inference/derivations/InferenceCore.lean','reused current independent model/derivation semantics'),
        (s.BASE/'inference/closure/ClosureAdequacy.lean','reused complete ground enumeration')],
        [{'classification':'non-blocking','choice':'Two exact ground implication countermodels and a coexistence model under one fixed context',
          'basis':'Stable I02/I03 exports are supplementary bound proof dependencies; do not alter DAG prerequisites or claim universal noninterference.'}])
    outcomes=[];controls=[];audit=c.c.policy()
    with tempfile.TemporaryDirectory(prefix='independence-witnesses-') as folder:
        build=Path(folder);logs=w.prepare(normal,build)
        logs+=s.compile_lean(build,[('ModelStatementAudit',BASE/'StatementAudit.lean')])
        axioms=audit.axiom_report(logs[-1]['output'])
        expected={'Inference.ModelAudit.required_statement','Inference.model_checker_iff','Inference.checked_model_is_closed',
                  'Inference.countermodel_checker_iff','Inference.checked_countermodel_non_entailment'}
        s.require(set(axioms)==expected and audit.policy_accepts(logs[-1]['output']),'model generic statement/axiom audit incomplete')
        for index,(name,witness) in enumerate([('conformance does not entail admission',forward),('admission does not entail conformance',reverse),
                                             ('conformance and independent admission coexist',coexist)]):
            outcome=w.check(request,witness,build);s.require(outcome['accepted'],'valid model witness rejected: '+name)
            outcomes.append({'name':name,'result':outcome});(BASE/('Witness'+str(index)+'.lean')).write_bytes((build/'ModelQuery.lean').read_bytes())
        (BASE/'ModelFixture.lean').write_bytes((build/'InferenceFixture.lean').read_bytes())
        def reject(name,mutate):
            bad=deepcopy(forward);mutate(bad)
            try:result=w.check(request,bad,build)
            except (ValueError,UnicodeError) as error:
                s.require('kernel replay failed' not in str(error),'model host/kernel disagreement: '+str(error))
                controls.append({'name':name,'result':'rejected','mechanism':'closed input or exact context','diagnostic':str(error)})
            else:
                s.require(not result['accepted'] and not result['non_entailment_proved'],'false model evidence accepted: '+name)
                controls.append({'name':name,'result':'rejected','mechanism':'fresh kernel checked false countermodel','outcome':result})
        reject('missing applicable rule consequence',lambda x:x.update(model=[a for a in x['model'] if a['predicate']!='ReviewSignal']))
        reject('false implication premise',lambda x:x.update(model=[a for a in x['model'] if a['predicate']!='Conforms']))
        reject('conclusion true in purported countermodel',lambda x:x['model'].append(x['claim']['conclusion']))
        reject('missing captured independent root fact',lambda x:x.update(model=[a for a in x['model'] if a['predicate']!='CheckedRoot']))
        reject('duplicate model member',lambda x:x['model'].append(x['model'][0]))
        reject('wrong model atom sort',lambda x:x['model'][-1].update(terms=[request['domain'][2]]))
        reject('fresh model reference',lambda x:x['model'][-1].update(terms=[{'kind':'reference','id':'fresh','version':'v1'}]))
        reject('wrong predicate version',lambda x:x['model'][-1].update(version='v2'))
        reject('stale theory or root identity',lambda x:x.update(normal_form_identity='0'*64))
        reject('weakened formula replaces exact implication',lambda x:x.update(claim={'kind':'non-entailment','premise_axis':'Conforms','conclusion_axis':'Admitted'}))
        reject('axis labels without actual model',lambda x:x.update(model=[]))
        reject('external solver verdict cannot replace witness',lambda x:x.update(solver_result='no-counterexample'))
        def fake_root(x):
            x['model'].append({'predicate':'CheckedRoot','version':'v1','terms':[request['domain'][1],*request['domain'][2:5]]})
        reject('additional fabricated root in model',fake_root)
        def different_conclusion(x):
            x['claim']['conclusion']=deepcopy(x['claim']['premise'])
        reject('distinct labels do not establish a self-implication countermodel',different_conclusion)
        path=build/'HostileModel.lean';path.write_text('import ModelSemantics\nopen Inference\ntheorem weak : True := True.intro\nexample : RequiredCountermodelSoundness := weak\n')
        run=subprocess.run([str(s.lean_path()),str(path)],cwd=build,env={**os.environ,'LEAN_PATH':str(build)},text=True,capture_output=True,timeout=60)
        s.require(run.returncode!=0,'weak model statement accepted');controls.append({'name':'wrong required theorem type','result':'rejected','mechanism':'exact type assignment'})
        closure=c.compute(request);closure['bundle']['negative_query']=forward['claim']['conclusion']
        least=c.check(request,closure['bundle'],build)
        s.require(least['accepted'] and least['non_derivability_proved'],'profile closure absence not proved')
        (BASE/'ProfileAbsence.lean').write_bytes((build/'ClosureQuery.lean').read_bytes())
    unknown=w.unsuccessful_search();s.require(not unknown['non_entailment_proved'] and not unknown['non_derivability_proved'],'unsuccessful search proves absence')
    controls.append({'name':'bounded search without verified witness','result':'unknown','outcome':unknown})
    s.write(BASE/'example-input.json',request)
    for name,obj in [('conformance-countermodel.json',forward),('admission-countermodel.json',reverse),('coexistence-model.json',coexist),
                     ('profile-closure-certificate.json',closure['bundle'])]:s.write(BASE/name,obj)
    report={'task':'I05','result':'pass','normal_form_identity':normal['normal_form_identity'],
        'required_statement':'Inference.RequiredCountermodelSoundness','formal_theorems':sorted(axioms),'transitive_axioms':axioms,'modules':logs,
        'semantic_non_entailment':outcomes[:2],'positive_coexistence':outcomes[2],
        'profile_non_derivability':least,'failed_bounded_search':unknown,'controls':controls,
        'claim_ceiling':'Both exact ground implications are non-entailed in one captured context. No universal axis perturbation/noninterference theorem is asserted.',
        'model_scope':'All Horn consequences and base facts checked; supplied models also obey typed exact-root interpretations. Non-entailment theorem ranges over all closed Horn models.',
        'distinction':'A closed model may assign independently rooted admission true even when it is absent from the least derivable closure. Conformance does not imply a negative admission axiom.',
        'extra_reused_dependencies':[s.binding(s.BASE/'inference/derivations/InferenceCore.lean'),s.binding(s.BASE/'inference/closure/ClosureAdequacy.lean')],
        'trust_boundary':'Source meaning, strict parser, canonical hashing, host projection and independent root truth remain explicit assumptions.',
        'authority_effect':'none'}
    s.write(BASE/'non-entailment-report.json',report)
    artifacts={name:BASE/name for name in ['independence-witnesses','non-entailment-report.json','ModelSemantics.lean',
        'StatementAudit.lean','witness_checker.py','run_independence.py','ModelFixture.lean','Witness0.lean','Witness1.lean','Witness2.lean',
        'ProfileAbsence.lean','example-input.json','conformance-countermodel.json','admission-countermodel.json','coexistence-model.json','profile-closure-certificate.json']}
    s.accept('I05',artifacts,
        ['Two supplied models satisfy every rule, captured base fact, typed domain and independent-root interpretation under the same context. Their exact premise/negated conclusion is checked and a generic theorem yields non-entailment even over all closed Horn models; coexistence is separately checked.',
         'Semantic non-entailment, complete finite-profile non-derivability and unsuccessful bounded search are separately reported. Model-positive independently rooted admission can coexist with least-closure absence; no universal noninterference claim or negative admission axiom is introduced.'],
        ['Axis labels without a model, missing rule consequences, a false premise, true conclusion, a self-implication and a weak theorem statement all fail independent checks.',
         'The fully checked coexistence model contains Conforms, ReviewSignal, CheckedRoot and independently justified Admitted together. It does not require conformance to entail admission or its negation.'],
        [s.BASE/'inference/derivations/InferenceCore.lean',s.BASE/'inference/derivations/DerivationSoundness.lean',
         s.BASE/'inference/derivations/derivation_checker.py',s.BASE/'inference/closure/ClosureAdequacy.lean',
         s.BASE/'inference/closure/closure_checker.py',s.FORMAL/'validate_f0.py',s.FORMAL/'toolchain-lock.json'])
    print(json.dumps({'task':'I05','result':'accepted','generic_audited_declarations':len(axioms),'checked_models':3,'controls':len(controls)}))


if __name__=='__main__':main()
