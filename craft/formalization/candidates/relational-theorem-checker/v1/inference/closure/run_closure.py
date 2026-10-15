#!/usr/bin/env python3
"""Replay generic adequacy, late consequences, unexplained atoms and limits."""
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import tempfile
import closure_checker as c
s=c.s;f=c.f
BASE=Path(__file__).resolve().parent


def chain_input():
    request=s.read(s.BASE/'inference/profile/example-input.json')
    for name in ['MiddleSignal','FinalSignal']:
        request['predicates'].append({'id':name,'version':'v1','sorts':['reference'],'role':'ordinary'})
    def rule(name,head,body):return {'id':name,'version':'v1',
        'head':{'predicate':head,'terms':[{'variable':'subject'}]},
        'body':[{'predicate':body,'terms':[{'variable':'subject'}]}]}
    request['rules'] += [rule('rule:middle','MiddleSignal','ReviewSignal'),
                         rule('rule:final','FinalSignal','MiddleSignal'),
                         rule('rule:cycle','ReviewSignal','FinalSignal'),
                         rule('rule:duplicate-head','MiddleSignal','ReviewSignal')]
    return request


def main():
    s.context('I03',[(s.PLAN,'I03 finite termination and exact closure including late consequences'),
        (s.BASE/'inference/derivations/InferenceCore.lean','independent substitution semantics, Derivable and Closed'),
        (s.BASE/'inference/derivations/DerivationSoundness.lean','no-extra facts from sound certificates'),
        (s.BASE/'inference/profile/inference-semantics.md','model/least-fixed-point definitions and unknown boundary')],
        [{'classification':'non-blocking','choice':'Complete finite grounding plus closure certification and a strictly decreasing pending-head saturation algorithm',
          'basis':'Enumeration completeness is proved against independent ValidInstance; checked closure equals all derivable atoms. Resource interruption returns unknown.'}])
    request=chain_input();normal=f.normalize(request);computed=c.compute(request)
    s.require(computed['status']=='candidate-complete' and not computed['non_derivability_proved'],'candidate computation claims a theorem')
    bundle=computed['bundle'];target=request['domain'][0]
    bundle['negative_query']={'predicate':'Admitted','version':'v1','terms':[target,*request['domain'][2:5]]}
    controls=[];positives=[];audit=c.c.policy()
    with tempfile.TemporaryDirectory(prefix='closure-controls-') as folder:
        build=Path(folder);logs=c.prepare(normal,build)
        logs+=s.compile_lean(build,[('ClosureStatementAudit',BASE/'StatementAudit.lean')])
        axioms=audit.axiom_report(logs[-1]['output'])
        names={'Inference.ClosureAudit.required_statement','Inference.choices_complete','Inference.ground_rule_captures_instance',
               'Inference.ground_instances_complete','Inference.closure_checker_iff','Inference.checked_closure_is_closed',
               'Inference.checked_closure_has_no_extra','Inference.checked_closure_exact','Inference.checked_closure_is_least',
               'Inference.absent_from_checked_closure_not_derivable','Inference.saturation_measure_decreases',
               'Inference.saturation_sufficient_fuel','Inference.saturation_never_exhausts','Inference.saturate'}
        s.require(set(axioms)==names and audit.policy_accepts(logs[-1]['output']),'closure statement/axiom audit incomplete')
        outcome=c.check(request,bundle,build);s.require(outcome['accepted'] and outcome['non_derivability_proved'],'complete closure negative proof failed')
        positives.append({'case':'multi-rule closure with cycle and duplicate producer; no unrooted admission','result':outcome})
        (BASE/'ClosureFixture.lean').write_bytes((build/'InferenceFixture.lean').read_bytes())
        (BASE/'CompleteClosure.lean').write_bytes((build/'ClosureQuery.lean').read_bytes())
        reordered=deepcopy(bundle);reordered['closure'].reverse()
        outcome=c.check(request,reordered,build);s.require(outcome['accepted'],'least closure depends on tuple order')
        positives.append({'case':'reordered exact closure remains valid','result':outcome})
        present=deepcopy(bundle);present['negative_query']=present['closure'][-1]
        outcome=c.check(request,present,build)
        s.require(outcome['accepted'] and not outcome['non_derivability_proved'] and outcome['negative_query_status']=='query-derived','present query called absent')
        positives.append({'case':'derived query refuses negative claim','result':outcome})
        def reject(name,mutate):
            bad=deepcopy(bundle);mutate(bad)
            try:outcome=c.check(request,bad,build)
            except (ValueError,UnicodeError) as error:
                s.require('kernel replay failed' not in str(error),'closure projection disagrees with kernel: '+str(error))
                controls.append({'name':name,'result':'rejected','mechanism':'closed captured input','diagnostic':str(error)})
            else:
                s.require(not outcome['accepted'] and not outcome['non_derivability_proved'],'invalid closure accepted: '+name)
                controls.append({'name':name,'result':'rejected','mechanism':'fresh kernel checked false','outcome':outcome})
        reject('missing late rule consequence',lambda x:x.update(closure=[a for a in x['closure'] if a['predicate']!='FinalSignal']))
        reject('missing intermediate consequence',lambda x:x.update(closure=[a for a in x['closure'] if a['predicate']!='MiddleSignal']))
        reject('missing captured base fact',lambda x:x.update(closure=[a for a in x['closure'] if a['predicate']!='Conforms']))
        reject('invented closure member',lambda x:x['closure'].append({'predicate':'FinalSignal','version':'v1','terms':[request['domain'][1]]}))
        reject('fabricated protected member',lambda x:x['closure'].append(deepcopy(x['negative_query'])))
        reject('duplicate closure member',lambda x:x['closure'].append(x['closure'][0]))
        reject('empty closure hides initial facts',lambda x:x.update(closure=[]))
        reject('no derivation explanations',lambda x:x.update(certificates=[]))
        def delete_premises(x):
            for cert in x['certificates']:cert['steps'][-1]['premises']=[]
        reject('invalid explanations for supplied closure',delete_premises)
        reject('stale closure theory binding',lambda x:x.update(normal_form_identity='0'*64))
        reject('stale derivation binding',lambda x:x['certificates'][0].update(normal_form_identity='0'*64))
        reject('unknown complete flag cannot bypass checks',lambda x:x.update(complete=True))
        reject('unbound rule source',lambda x:x.update(rule_provider='remote:rules'))
        for name,source in [('weak adequacy statement','theorem weak : True := True.intro\nexample : RequiredClosureAdequacy := weak\n'),
                            ('assumed closure completeness','theorem assumed (T : Theory) (F C : List Atom) : (∀ a, a ∈ C ↔ Derivable T F a) → (∀ a, a ∈ C ↔ Derivable T F a) := id\nexample : RequiredClosureAdequacy := assumed\n')]:
            path=build/'HostileClosure.lean';path.write_text('import ClosureAdequacy\nopen Inference\n'+source)
            run=subprocess.run([str(s.lean_path()),str(path)],cwd=build,env={**os.environ,'LEAN_PATH':str(build)},capture_output=True,text=True,timeout=60)
            s.require(run.returncode!=0,'weakened closure statement accepted');controls.append({'name':name,'result':'rejected','mechanism':'exact kernel type assignment'})
    for name,options in [('grounding resource limit',{'max_instances':0}),('saturation resource limit',{'max_steps':0}),
                         ('timeout before closure',{'time_limit':0})]:
        outcome=c.compute(request,**options)
        s.require(outcome['status']=='unknown' and not outcome['closure_complete'] and not outcome['non_derivability_proved'] and 'bundle' not in outcome,'resource failure became absence evidence')
        controls.append({'name':name,'result':'unknown','outcome':outcome})
    # Constant-only facts, empty initial facts and the least empty closure are
    # distinct cases; they expose enumeration and zero-premise rule boundaries.
    empty=s.read(s.BASE/'inference/profile/example-input.json');empty['facts']=[];empty['rules']=[]
    constant=deepcopy(empty);constant['rules']=[{'id':'rule:constant','version':'v1',
        'head':{'predicate':'ReviewSignal','terms':[{'constant':constant['domain'][0]}]},'body':[]}]
    for name,example in [('empty least closure',empty),('zero-premise captured constant rule',constant)]:
        produced=c.compute(example);outcome=c.check(example,produced['bundle'])
        s.require(outcome['accepted'],'grounding boundary case failed: '+name);positives.append({'case':name,'result':outcome})
    for name,obj in [('example-input.json',request),('example-closure-certificate.json',bundle),('candidate-computation.json',computed)]:s.write(BASE/name,obj)
    s.write(BASE/'closure-controls.json',{'task':'I03','result':'pass','formal_theorems':sorted(axioms),'transitive_axioms':axioms,
        'required_statement':'Inference.RequiredClosureAdequacy','modules':logs,'positive_cases':positives,'controls':controls,
        'ground_instance_count':computed['ground_instance_count'],'closure_size':len(bundle['closure']),
        'termination':computed['termination'],'finite_termination':'Kernel-accepted structurally terminating saturation with a proved sufficient fuel bound and strictly decreasing pending-head length.',
        'scope':'Complete grounding is proved against independent ValidInstance. Accepted closures contain exactly the inductively derivable atoms and are least among all closed models.',
        'trust_boundary':'Source interpretation, parser/hashing/host projection and supplied evidence truth remain assumptions. Computation alone claims no theorem; all decisive results freshly kernel certified.',
        'authority_effect':'none','protected_producer_policy_proved':False})
    artifacts={name:BASE/name for name in ['closure-engine','closure-certificate-checker','ClosureAdequacy.lean',
        'closure_checker.py','run_closure.py','StatementAudit.lean','closure-controls.json','ClosureFixture.lean','CompleteClosure.lean',
        'example-input.json','example-closure-certificate.json','candidate-computation.json']}
    s.accept('I03',artifacts,
        ['Closure certification checks every initial fact, all independently complete ground rule instances, and sound derivation explanations for every member. Generic exact/least closure proofs and fresh multi-rule/cyclic examples pass; missing late consequences and invented/protected members fail.',
         'Structurally terminating Lean saturation consumes a pending head with strictly decreasing finite length; generic sufficient-fuel and never-exhausts proofs establish that this bound reaches saturation. Fourteen audited declarations include independent finite enumeration completeness, exact least-fixed-point adequacy and absence-implies-nonderivability. Resource/timeout outcomes remain unknown; accepted complete closure gives only scoped finite-profile negatives.'],
        ['Zero grounding budget, zero saturation budget and zero time limit yield unknown without a certificate or non-derivability claim. A query present in a checked closure explicitly refuses a negative claim.',
         'Missing late/intermediate/base consequences, invented or duplicated members and absent/invalid explanations are freshly kernel rejected. Reordering a complete closure is accepted, and empty/constant-only boundary examples pass.'],
        [s.BASE/'input/decoder.py',s.BASE/'execution/support.py',s.FORMAL/'validate_f0.py',s.FORMAL/'toolchain-lock.json'])
    print(json.dumps({'task':'I03','result':'accepted','generic_audited_declarations':len(axioms),'positive_cases':len(positives),
                     'controls':len(controls),'checked_closure_size':len(bundle['closure'])}))


if __name__=='__main__':main()
