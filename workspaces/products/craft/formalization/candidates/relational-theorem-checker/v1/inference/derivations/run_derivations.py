#!/usr/bin/env python3
"""Audit the generic theorem, replay certificates and challenge every step axis."""
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import tempfile
import derivation_checker as c
s=c.s;f=c.f
BASE=Path(__file__).resolve().parent


def raw_atom(predicate,values):return {'predicate':predicate,'version':'v1','terms':deepcopy(values)}


def certificate(request):
    normal=f.normalize(request);target=request['domain'][0]
    key={k:normal['rules'][0][k] for k in ['id','version','hash']}
    base=raw_atom('Conforms',[target]);query=raw_atom('ReviewSignal',[target])
    return {'schema':'relational.derivation-certificate/v1','normal_form_identity':normal['normal_form_identity'],
        'query':query,'steps':[{'id':'base:conforms','kind':'base','conclusion':base},
        {'id':'rule:signal','kind':'apply','conclusion':query,'rule':key,'substitution':{'subject':target},'premises':['base:conforms']}]}


def main():
    request=s.read(s.BASE/'inference/profile/example-input.json');cert=certificate(request);normal=f.normalize(request)
    s.context('I02',[(s.PLAN,'I02 exact premise/rule identity and generic soundness'),
        (s.BASE/'inference/profile/rule-profile.json','finite typed language and captured identity'),
        (s.BASE/'inference/profile/protected-root-policy.json','independent protected leaves; I04 producer policy separate'),
        (s.BASE/'inference/profile/inference-semantics.md','inductive semantics distinct from closure')],
        [{'classification':'non-blocking','choice':'Pure Lean topological certificate checks and independent inductive semantics',
          'basis':'No unbound fact lookup or root production; exact statement assignment and transitive axiom audit. Saturation completeness remains I03.'}])
    positives=[];controls=[];audit=c.policy()
    with tempfile.TemporaryDirectory(prefix='derivation-controls-') as folder:
        build=Path(folder);logs=c.prepare(normal,build)
        logs+=s.compile_lean(build,[('StatementAudit',BASE/'StatementAudit.lean')])
        axioms=audit.axiom_report(logs[-1]['output'])
        expected={'Inference.Audit.required_statement','Inference.derivation_checker_iff','Inference.derivation_certificate_sound',
                  'Inference.chain_sound','Inference.step_sound','Inference.resolved_premises_are_previous','Inference.derivable_in_every_closed_model'}
        s.require(set(axioms)==expected and audit.policy_accepts(logs[-1]['output']),'generic statement/axiom audit incomplete')
        result=c.check(request,cert,build);s.require(result['accepted'],'valid rule certificate rejected');positives.append({'case':'review signal from conformance','result':result})
        (BASE/'ExampleCertificate.lean').write_bytes((build/'DerivationQuery.lean').read_bytes())
        (BASE/'InferenceFixture.lean').write_bytes((build/'InferenceFixture.lean').read_bytes())
        base=deepcopy(cert);base['query']=base['steps'][0]['conclusion'];base['steps']=base['steps'][:1]
        result=c.check(request,base,build);s.require(result['accepted'],'base fact certificate rejected');positives.append({'case':'captured base fact','result':result})
        def reject(name,mutate):
            bad=deepcopy(cert);mutate(bad)
            try:outcome=c.check(request,bad,build)
            except (ValueError,UnicodeError) as error:
                s.require('kernel replay failed' not in str(error),'control exposed host/kernel projection disagreement: '+str(error))
                controls.append({'name':name,'result':'rejected','mechanism':'closed certificate input or captured identity','diagnostic':str(error)})
            else:
                s.require(not outcome['accepted'],'hostile derivation accepted: '+name)
                controls.append({'name':name,'result':'rejected','mechanism':'fresh kernel checked false result','outcome':outcome})
        reject('missing body premise',lambda x:x['steps'][1].update(premises=[]))
        reject('extra body premise',lambda x:x['steps'][1].update(premises=['base:conforms','base:conforms']))
        reject('altered exact rule hash',lambda x:x['steps'][1]['rule'].update(hash='0'*64))
        reject('wrong rule version',lambda x:x['steps'][1]['rule'].update(version='v2'))
        reject('unknown rule identity',lambda x:x['steps'][1]['rule'].update(id='rule:external'))
        reject('missing variable binding',lambda x:x['steps'][1].update(substitution={}))
        reject('extra variable binding',lambda x:x['steps'][1]['substitution'].update(unbound=request['domain'][0]))
        reject('wrong substitution sort',lambda x:x['steps'][1]['substitution'].update(subject=request['domain'][2]))
        reject('fresh substitution identity',lambda x:x['steps'][1]['substitution'].update(subject={'kind':'reference','id':'fresh','version':'v1'}))
        reject('wrong substitution target version',lambda x:x['steps'][1]['substitution'].update(subject={'kind':'reference','id':'capability:reviewer','version':'v2'}))
        reject('substitution disagrees with captured premises',lambda x:x['steps'][1]['substitution'].update(subject=request['domain'][1]))
        reject('external premise reference',lambda x:x['steps'][1].update(premises=['fact:external']))
        reject('self cyclic premise',lambda x:x['steps'][1].update(premises=['rule:signal']))
        reject('forward cyclic premise',lambda x:x['steps'][0].update(kind='apply',rule=x['steps'][1]['rule'],substitution={'subject':request['domain'][0]},premises=['rule:signal']))
        reject('duplicate step identity',lambda x:x['steps'][1].update(id='base:conforms'))
        reject('uncaptured base fact',lambda x:x['steps'][0].update(conclusion=raw_atom('Conforms',[request['domain'][1]])))
        reject('wrong head target',lambda x:x['steps'][1].update(conclusion=raw_atom('ReviewSignal',[request['domain'][1]])))
        reject('wrong head predicate',lambda x:x['steps'][1].update(conclusion=raw_atom('Conforms',[request['domain'][0]])))
        reject('wrong head sort',lambda x:x['steps'][1].update(conclusion=raw_atom('ReviewSignal',[request['domain'][2]])))
        reject('query has no certificate conclusion',lambda x:x.update(query=raw_atom('ReviewSignal',[request['domain'][1]])))
        reject('empty certificate',lambda x:x.update(steps=[]))
        reject('stale theory/fact binding',lambda x:x.update(normal_form_identity='0'*64))
        reject('unbound provider field',lambda x:x.update(fact_provider='remote:any'))
        reject('unbound step external fact',lambda x:x['steps'][1].update(external_facts=['remote:any']))
        reject('unsupported certificate version',lambda x:x.update(schema='relational.derivation-certificate/v2'))
        reject('unknown query predicate',lambda x:x['query'].update(predicate='Unknown'))
        reject('wrong query predicate version',lambda x:x['query'].update(version='v2'))
        protected=raw_atom('Admitted',request['domain'][0:1]+request['domain'][2:5])
        forged=raw_atom('CheckedRoot',request['domain'][0:1]+request['domain'][2:5])
        reject('fabricated admission base claim',lambda x:x.update(query=protected,steps=[{'id':'forged','kind':'base','conclusion':protected}]))
        reject('fabricated checked-root claim',lambda x:x.update(query=forged,steps=[{'id':'forged','kind':'base','conclusion':forged}]))
        for name,source,kernel_expected in [
            ('weakened required statement','theorem weak : True := True.intro\nexample : RequiredDerivationSoundness := weak\n',False),
            ('conclusion supplied as assumption','theorem circular (T : Theory) (F : List Atom) (a : Atom) : Derivable T F a → Derivable T F a := id\nexample : RequiredDerivationSoundness := circular\n',False),
            ('unfinished proof','theorem supplied : RequiredDerivationSoundness := by sorry\n#print axioms supplied\n',True),
            ('invented axiom','axiom invented : RequiredDerivationSoundness\ntheorem supplied : RequiredDerivationSoundness := invented\n#print axioms supplied\n',True)]:
            path=build/'HostileProof.lean';path.write_text('import DerivationSoundness\nopen Inference\n'+source)
            run=subprocess.run([str(s.lean_path()),str(path)],cwd=build,env={**os.environ,'LEAN_PATH':str(build)},capture_output=True,text=True,timeout=60)
            output=run.stdout+run.stderr
            if kernel_expected:s.require(run.returncode==0 and not audit.policy_accepts(output),'unapproved assumption escaped audit')
            else:s.require(run.returncode!=0,'wrong statement escaped exact type assignment')
            controls.append({'name':name,'result':'rejected','mechanism':'transitive axiom audit' if kernel_expected else 'exact kernel type assignment'})
        for name,source in [('native evaluation','example : 1 = 1 := by native_decide'),('skip kernel checking','set_option debug.skipKernelTC true')]:
            s.require(not audit.source_policy(source),'proof bypass permitted');controls.append({'name':name,'result':'rejected','mechanism':'source policy'})
    rooted=s.read(s.BASE/'inference/profile/coexistence-input.json');root_normal=f.normalize(rooted)
    with tempfile.TemporaryDirectory(prefix='independent-admission-derivation-') as folder:
        build=Path(folder);root_logs=c.prepare(root_normal,build)
        for name in ['Admitted','CheckedRoot']:
            atom=raw_atom(name,rooted['facts'][1]['terms'])
            existing={'schema':cert['schema'],'normal_form_identity':root_normal['normal_form_identity'],
                      'query':atom,'steps':[{'id':'existing:'+name,'kind':'base','conclusion':atom}]}
            outcome=c.check(rooted,existing,build);s.require(outcome['accepted'],'independent legitimate root/admission rejected')
            positives.append({'case':'independently justified '+name+' coexists with Conforms','result':outcome})
    s.write(BASE/'example-certificate.json',cert)
    report={'task':'I02','result':'pass','required_statement':'Inference.RequiredDerivationSoundness',
            'formal_theorems':sorted(axioms),'transitive_axioms':axioms,'modules':logs,'rooted_modules':root_logs,
            'positive_cases':positives,'negative_controls':controls,'derivation_soundness':True,'closure_complete':False,
            'protected_producer_policy_proved':False,'future_obligations':['I03 closure adequacy','I04 protected lineage'],
            'trust_boundary':'Parser, canonical hashing, host projection and independently supplied evidence truth remain assumptions; all projected outcomes replayed with pinned Lean and audited axioms.',
            'authority_effect':'none'}
    s.write(BASE/'derivation-controls.json',report)
    artifacts={name:BASE/name for name in ['derivation-checker','DerivationSoundness.lean','derivation-controls.json',
        'InferenceCore.lean','StatementAudit.lean','derivation_checker.py','run_derivations.py','InferenceFixture.lean',
        'ExampleCertificate.lean','example-certificate.json']}
    s.accept('I02',artifacts,
        ['Each typed step binds exact captured rule ID/version/hash, total domain-sorted substitution, actual earlier premise conclusions and exact head. Missing, altered, extra, cyclic and external references fail; legitimate independent existing admission passes.',
         'The exact universally quantified RequiredDerivationSoundness statement is assigned to the proved theorem and all seven declarations have audited allowed axioms. Fresh certificate outcomes use that checker; positive soundness is explicitly separate from I03 completeness and I04 protected producer policy.'],
        ['Missing premises, changed hashes/version, wrong/fresh substitutions and forged root/admission leaves are rejected, including kernel checked false results; weak statements and custom/unfinished assumptions fail type or axiom audit.',
         'Closed certificate envelopes and prior-step indices reject external provider fields, missing references and unbound external facts. The pure Lean checker reads only its supplied typed theory, facts and certificate.'],
        [s.BASE/'input/decoder.py',s.BASE/'execution/support.py',s.FORMAL/'validate_f0.py',s.FORMAL/'toolchain-lock.json'])
    print(json.dumps({'task':'I02','result':'accepted','generic_audited_declarations':len(axioms),
                     'positive_cases':len(positives),'negative_controls':len(controls),'closure_complete':False}))


if __name__=='__main__':main()
