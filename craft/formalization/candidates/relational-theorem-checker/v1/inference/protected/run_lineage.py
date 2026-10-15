#!/usr/bin/env python3
"""Exercise direct/indirect leakage and exact four-coordinate root lineage."""
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import tempfile
import lineage_checker as p
s=p.s;f=p.f;c=p.c
BASE=Path(__file__).resolve().parent


def patterns(request,predicate,version=None,effect=None,scope=None,epoch=None):
    target=request['domain'][0];values=[target,*request['domain'][2:5]]
    if version is not None:values[0]={**target,'version':version}
    for index,changed in [(1,effect),(2,scope),(3,epoch)]:
        if changed is not None:values[index]={'kind':values[index]['kind'],'value':changed}
    return {'predicate':predicate,'terms':[{'variable':'subject'} if index==0 and version is None else {'constant':v} for index,v in enumerate(values)]}


def legal_bridge():
    request=s.read(s.BASE/'inference/profile/coexistence-input.json')
    request['facts']=request['facts'][:1]  # Root is independent; admission is derived through the bridge.
    for name in ['AuthorizationStage1','AuthorizationStage2']:
        request['predicates'].append({'id':name,'version':'v1','sorts':f.ROOT_SORTS,'role':'root-carrier'})
    def rule(name,head,body):return {'id':name,'version':'v1','head':patterns(request,head),'body':[patterns(request,body)]}
    request['rules']+=[rule('rule:root-to-stage1','AuthorizationStage1','CheckedRoot'),
                       rule('rule:stage1-to-stage2','AuthorizationStage2','AuthorizationStage1'),
                       rule('rule:stage2-to-admission','Admitted','AuthorizationStage2')]
    return request


def main():
    s.context('I04',[(s.PLAN,'I04 every producer, indirect laundering and exact coordinates'),
        (s.BASE/'inference/profile/protected-root-policy.json','root/carrier roles and independent existing admission'),
        (s.BASE/'inference/derivations/InferenceCore.lean','typed root leaves and inductive derivability'),
        (s.BASE/'inference/closure/ClosureAdequacy.lean','complete enumeration and closure witnesses')],
        [{'classification':'non-blocking','choice':'Generic derivation induction after complete producer checks',
          'basis':'All carrier and protected rule heads require same-tuple independent-root/carrier premises; ordinary intermediate predicates cannot launder evidence.'}])
    legal=legal_bridge();normal=f.normalize(legal);positives=[];controls=[];audit=c.c.policy()
    with tempfile.TemporaryDirectory(prefix='lineage-audit-') as folder:
        build=Path(folder);logs=p.prepare(normal,build)
        logs+=s.compile_lean(build,[('LineageStatementAudit',BASE/'StatementAudit.lean')])
        axioms=audit.axiom_report(logs[-1]['output'])
        expected={'Inference.LineageAudit.required_statement','Inference.lineage_checker_iff','Inference.justification_is_rooted',
            'Inference.initial_root_lineage','Inference.protected_lineage','Inference.checked_protected_lineage','Inference.no_unrooted_protected_derivation'}
        s.require(set(axioms)==expected and audit.policy_accepts(logs[-1]['output']),'lineage statement/axiom audit incomplete')
        checked=p.check(legal,build=build);s.require(checked['accepted'],'legitimate bridge rejected')
        positives.append({'case':'independent checked root through two carriers to admission','result':checked})
        (BASE/'LineageFixture.lean').write_bytes((build/'InferenceFixture.lean').read_bytes())
        (BASE/'LegalLineage.lean').write_bytes((build/'LineageQuery.lean').read_bytes())
        closure=c.compute(legal);closure_result=c.check(legal,closure['bundle'],build)
        s.require(closure_result['accepted'],'legitimate bridge closure failed')
        s.require(any(a['predicate']=='Admitted' for a in closure['bundle']['closure']),'legitimate bridge never derives admission')
        s.require(any(a['predicate']=='Conforms' for a in closure['bundle']['closure']),'conformance cannot coexist with admitted bridge')
        positives.append({'case':'checked closure derives admission and retains independent conformance','result':closure_result})
        (BASE/'LegalBridgeClosure.lean').write_bytes((build/'ClosureQuery.lean').read_bytes())
        for name,source in [('weak lineage statement','theorem weak : True := True.intro\nexample : RequiredProtectedLineage := weak\n'),
                            ('assumed independent root','theorem circular (T : Theory) (a : Atom) : a.values ∈ T.roots → a.values ∈ T.roots := id\nexample : RequiredProtectedLineage := circular\n')]:
            path=build/'HostileLineage.lean';path.write_text('import ProtectedLineage\nopen Inference\n'+source)
            run=subprocess.run([str(s.lean_path()),str(path)],cwd=build,env={**os.environ,'LEAN_PATH':str(build)},capture_output=True,text=True,timeout=60)
            s.require(run.returncode!=0,'weakened lineage type accepted');controls.append({'name':name,'result':'rejected','mechanism':'exact kernel statement assignment'})
    def violation(name,request,show_actual_leak=False):
        result=p.check(request);s.require(result['status']=='protected-policy-violation' and result['violations'] and not result['root_lineage_proved'],'illegal producer policy accepted: '+name)
        entry={'name':name,'result':'rejected','mechanism':'fresh kernel false lineage result','outcome':result}
        if show_actual_leak:
            computed=c.compute(request);checked=c.check(request,computed['bundle'])
            s.require(checked['accepted'] and any(a['predicate']=='Admitted' for a in computed['bundle']['closure']),'coupling control has no actual leaking derivation')
            entry.update(logical_closure=checked,explanation='Horn consequence is derivable, but protected justification policy fails; no authority permission follows.')
        controls.append(entry)
    direct=s.read(s.BASE/'inference/profile/unsafe-coupling-input.json')
    violation('direct conformance to admission',direct,True)
    indirect=deepcopy(direct)
    indirect['predicates'].append({'id':'IntermediateAssessment','version':'v1','sorts':['reference'],'role':'ordinary'})
    indirect['rules'][0]['head']={'predicate':'IntermediateAssessment','terms':[{'variable':'subject'}]}
    indirect['rules'].append({'id':'rule:laundered','version':'v1','head':patterns(indirect,'Admitted'),
                             'body':[{'predicate':'IntermediateAssessment','terms':[{'variable':'subject'}]}]})
    violation('multi-rule ordinary assessment launders conformance',indirect,True)
    renamed=deepcopy(legal);renamed['predicates'][-2]['role']='ordinary'
    violation('carrier loses checked justification role',renamed)
    laundered=deepcopy(legal);laundered['rules'][-2]['body']=[{'predicate':'Conforms','terms':[{'variable':'subject'}]}]
    violation('intermediate carrier producer loses root',laundered)
    for coordinate,changed in [('version','v2'),('effect','execution'),('scope','other'),('epoch',8)]:
        bad=deepcopy(legal);bad['rules'][-1]['head']=patterns(bad,'Admitted',**{coordinate:changed})
        if coordinate=='version':
            new={**bad['domain'][0],'version':'v2'};bad['domain'].append(new)
            # Keep subject range restricted in the carrier premise even when
            # the head uses a different constant target version.
        elif coordinate=='effect':bad['domain'].append({'kind':'effect','value':changed})
        violation('protected conclusion changes '+coordinate,bad)
    same_named=deepcopy(direct)
    same_named['predicates'].append({'id':'application_receipt_ref','version':'v1','sorts':['text'],'role':'ordinary'})
    same_named['domain'].append({'kind':'text','value':'CheckedRoot'})
    same_named['facts'].append({'predicate':'application_receipt_ref','terms':[same_named['domain'][-1]]})
    same_named['rules'][0]['body'].append({'predicate':'application_receipt_ref','terms':[{'constant':same_named['domain'][-1]}]})
    violation('same-named nonempty receipt qualifier string',same_named)
    alternate=deepcopy(legal)
    alternate['rules'].append({'id':'rule:unchecked-alternate-producer','version':'v1','head':patterns(alternate,'Admitted'),
                               'body':[{'predicate':'Conforms','terms':[{'variable':'subject'}]}]})
    violation('safe path cannot hide an unsafe alternate producer',alternate)
    roots_only=s.read(s.BASE/'inference/profile/example-input.json')
    query={'predicate':'Admitted','version':'v1','terms':[roots_only['domain'][0],*roots_only['domain'][2:5]]}
    result=p.check(roots_only,query=query)
    s.require(result['accepted'] and result['no_unrooted_derivation_proved'],'generic conformance-only boundary not proved')
    positives.append({'case':'conformance-only exact tuple has no protected derivation under safe rules','result':result})
    existing=s.read(s.BASE/'inference/profile/coexistence-input.json');result=p.check(existing)
    s.require(result['accepted'],'independently rooted existing admission prohibited')
    positives.append({'case':'existing independent admission and conformance coexist','result':result})
    # Exercise a genuinely general substitution carrying all four coordinates.
    generalized=deepcopy(legal)
    generalized['domain']=[generalized['domain'][0],*generalized['domain'][2:5]]
    terms=[{'variable':name} for name in ['subject','effect','scope','epoch']]
    for rule in generalized['rules'][1:]:
        rule['head']['terms']=deepcopy(terms)
        for premise in rule['body']:premise['terms']=deepcopy(terms)
    result=p.check(generalized);s.require(result['accepted'],'fully variable exact-tuple bridge rejected')
    positives.append({'case':'four-variable exact coordinate propagation','result':result})
    unknown=p.check(legal,max_instances=0)
    s.require(unknown['status']=='unknown' and not unknown['root_lineage_proved'],'partial producer enumeration called safe')
    controls.append({'name':'incomplete producer enumeration','result':'unknown','outcome':unknown})
    for name,obj in [('legal-bridge-input.json',legal),('direct-leak-input.json',direct),('indirect-leak-input.json',indirect),
                     ('four-variable-bridge-input.json',generalized),('legal-bridge-closure.json',closure['bundle'])]:s.write(BASE/name,obj)
    s.write(BASE/'coupling-controls.json',{'result':'pass','positive_cases':positives,'controls':controls,'authority_effect':'none'})
    s.write(BASE/'lineage-audit.json',{'task':'I04','result':'pass','required_statement':'Inference.RequiredProtectedLineage',
        'formal_theorems':sorted(axioms),'transitive_axioms':axioms,'modules':logs,
        'coordinates':['exact target ID/version','effect','scope','captured authority epoch'],
        'policy':'All grounded protected/carrier producers have a same-tuple CheckedRoot or justified root-carrier premise; every carrier producer is reviewed.',
        'generic_scope':'Every inductively derivable protected/carrier/root atom under InitialValid and checked SafeRules has its exact tuple in independently supplied roots.',
        'conformance_implies_not_admitted':False,'positive_existing_admission_coexistence_checked':True,
        'truth_boundary':'Independent root/evidence truth is externally supplied, not authenticated by this theorem. No real authority transition.',
        'authority_effect':'none','producer_controls':s.binding(BASE/'coupling-controls.json')})
    artifacts={name:BASE/name for name in ['ProtectedLineage.lean','coupling-controls.json','lineage-audit.json',
        'lineage_checker.py','run_lineage.py','StatementAudit.lean','LineageFixture.lean','LegalLineage.lean','LegalBridgeClosure.lean',
        'legal-bridge-input.json','direct-leak-input.json','indirect-leak-input.json','four-variable-bridge-input.json','legal-bridge-closure.json']}
    s.accept('I04',artifacts,
        ['Exact target ID/version, effect, scope and epoch are compared as complete typed tuples for every grounded protected/carrier producer. Wrong coordinate changes, role changes and unchecked alternate producers fail; a four-variable matching bridge passes.',
         'Seven audited declarations prove generic independent-root lineage by induction over arbitrary derivations and complete producer enumeration. Conformance-only absence follows from that theorem, while legitimate rooted chains and existing admission coexistence pass. Actual direct/indirect Horn leakage is separately kernel demonstrated and rejected by the policy.'],
        ['Multiple-rule ordinary laundering, an unrooted carrier producer, unsafe alternate producers and wrong version/effect/scope/epoch fail fresh kernel policy checks. Legitimate root-to-two-carrier-to-admission closure derives admission without rejecting independent conformance.',
         'An ordinary nonempty text fact named application_receipt_ref and containing CheckedRoot supplies no justification role or exact independent tuple; producer policy rejects it. Incomplete enumeration remains unknown.'],
        [s.BASE/'input/decoder.py',s.BASE/'execution/support.py',s.FORMAL/'validate_f0.py',s.FORMAL/'toolchain-lock.json'])
    print(json.dumps({'task':'I04','result':'accepted','generic_audited_declarations':len(axioms),'positive_cases':len(positives),'controls':len(controls)}))


if __name__=='__main__':main()
