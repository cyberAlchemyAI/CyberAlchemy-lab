#!/usr/bin/env python3
"""Validate I01's contract and exact-root projection before task acceptance."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import frontend as f
s=f.s
BASE=Path(__file__).resolve().parent


def example(receipt_path):
    target={'kind':'reference','id':'capability:reviewer','version':'v1'}
    contract={'kind':'reference','id':'contract:review','version':'v1'}
    effect={'kind':'effect','value':'admission'};scope={'kind':'scope','value':'review'};epoch={'kind':'epoch','value':7}
    doc={'schema':'relational.existing-admission-receipt/v1-candidate','receipt_id':'receipt:independent-admission',
         'receipt_version':'v1','mode':'existing-admission','accepted':True,
         'target_version':{k:target[k] for k in ['id','version']},'effect':effect['value'],'scope':scope['value'],'epoch':7,
         'authority_effect':'none','claim_ceiling':'Synthetic fixture: independently supplied existing-admission truth is assumed; no issuer authentication or real admission.'}
    s.write(receipt_path,doc);binding=s.binding(receipt_path)
    root={'id':'root:existing','target_version':doc['target_version'],'effect':doc['effect'],'scope':doc['scope'],
          'epoch':7,'assessment_ref':{'id':doc['receipt_id'],'version':'v1','sha256':binding['sha256']}}
    source_rule=s.read(s.BASE/'evolution/proposals/rule-change-proposal.json')['after']['rules'][0]
    request={'schema':'relational.inference-input/v1','snapshot_epoch':7,
             'domain':[target,contract,effect,scope,epoch,{'kind':'scope','value':'other'},{'kind':'epoch','value':8}],
             'predicates':deepcopy(f.CORE)+[{'id':'ReviewSignal','version':'v1','sorts':['reference'],'role':'ordinary'}],
             'rules':[source_rule],'facts':[{'predicate':'Conforms','terms':[target]}],
             'roots':[],'root_assessments':[]}
    rooted=deepcopy(request);rooted['roots']=[root]
    rooted['root_assessments']=[{'id':doc['receipt_id'],'version':'v1','source':binding}]
    rooted['facts'].append({'predicate':'Admitted','version':'v1','terms':[target,effect,scope,epoch]})
    return request,rooted,doc


def main():
    s.context('I01',[(s.PLAN,'I01 finite typed profile and exact roots'),
          (s.BASE/'gates/l2/l2-review.json','G2 named-profile limits and pending L3 obligations'),
          (s.BASE/'evolution/obligations/required-rule-obligations.json','complete independently required rule obligations'),
          (s.FORMAL/'specification/l0/semantic-contract.md','independent admission roots and conformance')],
          [{'classification':'non-blocking','choice':'Finite typed positive Horn profile with protected policy reviewed separately in I04',
            'basis':'Preserve logical derivability analysis and require exact independent root lineage; allow conformance and existing admission to coexist.'}])
    request,rooted,document=example(BASE/'fixtures/existing-admission.json')
    normal=f.normalize(request);coexist=f.normalize(rooted)
    s.require(not normal['roots'] and all(a['predicate']['id']!='Admitted' for a in normal['facts']),'conformance became admission')
    s.require({'Conforms','Admitted','CheckedRoot'}<={a['predicate']['id'] for a in coexist['facts']},'independent coexistence rejected')
    only_root=deepcopy(rooted);only_root['facts']=request['facts']
    root_normal=f.normalize(only_root)
    s.require('Admitted' not in {a['predicate']['id'] for a in root_normal['facts']},'root automatically claims admission')
    s.require(normal==f.normalize(deepcopy(request)),'normalization is nondeterministic')
    explicit=deepcopy(request)
    for pattern in [explicit['rules'][0]['head'],*explicit['rules'][0]['body']]:pattern['version']='v1'
    s.require(f.normalize(explicit)['rules'][0]['head']==normal['rules'][0]['head'],'captured unique version resolution differs')
    constants=deepcopy(request);constants['rules'][0]['body']=[]
    constants['rules'][0]['head']['terms']=[{'constant':request['domain'][0]}]
    s.require(not f.normalize(constants)['rules'][0]['variables'],'captured constant ground rule refused')
    # These rules are logical inputs to I04, not evidence that root policy holds.
    leak=deepcopy(request);leak['rules'][0]['head']={'predicate':'Admitted','terms':[
        {'variable':'subject'},*({'constant':v} for v in request['domain'][2:5])]}
    s.require(f.normalize(leak)['protected_policy_status']=='requires-I04-lineage-review','typed rule confused with protected policy approval')
    controls=[]
    def reject(name,mutate,source=request):
        bad=deepcopy(source);mutate(bad)
        try:f.normalize(bad)
        except (ValueError,UnicodeError) as error:controls.append({'name':name,'result':'rejected','diagnostic':str(error)})
        else:raise ValueError('control accepted: '+name)
    reject('empty active domain',lambda x:x.update(domain=[]))
    reject('duplicate domain value',lambda x:x['domain'].append(x['domain'][0]))
    reject('negative epoch',lambda x:x.update(snapshot_epoch=-1))
    reject('boolean epoch',lambda x:x.update(snapshot_epoch=True))
    reject('unknown request field',lambda x:x.update(external_fact_provider='unbound'))
    reject('duplicate predicate ID',lambda x:x['predicates'].append(x['predicates'][0]))
    reject('unknown sort',lambda x:x['predicates'][-1].update(sorts=['unbounded']))
    reject('renamed root producer',lambda x:x['predicates'].append({'id':'ForgedRoot','version':'v1','sorts':f.ROOT_SORTS,'role':'checked-root'}))
    reject('changed protected signature',lambda x:x['predicates'][1].update(sorts=['reference']))
    reject('changed protected version',lambda x:x['predicates'][1].update(version='v2'))
    reject('changed protected role',lambda x:x['predicates'][1].update(role='ordinary'))
    reject('wrong predicate version',lambda x:x['facts'][0].update(version='v2'))
    reject('undeclared predicate',lambda x:x['facts'][0].update(predicate='Unknown'))
    reject('malformed atom',lambda x:x['facts'].append(None))
    reject('wrong atom sort',lambda x:x['facts'][0].update(terms=[x['domain'][2]]))
    reject('wrong atom arity',lambda x:x['facts'][0].update(terms=[]))
    reject('fresh fact identity',lambda x:x['facts'][0].update(terms=[{'kind':'reference','id':'fresh','version':'v1'}]))
    reject('duplicate base fact',lambda x:x['facts'].append(x['facts'][0]))
    reject('duplicate rule identity',lambda x:x['rules'].append(x['rules'][0]))
    reject('unsafe head variable',lambda x:x['rules'][0]['head']['terms'][0].update(variable='fresh'))
    reject('generated function term',lambda x:x['rules'][0]['head'].update(terms=[{'function':'fresh','args':[]}]))
    reject('negative premise',lambda x:x['rules'][0]['body'][0].update(negated=True))
    reject('arithmetic condition',lambda x:x['rules'][0].update(constraint='epoch+1'))
    reject('fresh rule constant',lambda x:x['rules'][0]['head'].update(terms=[{'constant':{'kind':'reference','id':'fresh','version':'v1'}}]))
    reject('wrong rule predicate version',lambda x:x['rules'][0]['head'].update(version='v2'))
    reject('rule cannot manufacture roots',lambda x:x['rules'][0].update(head={'predicate':'CheckedRoot','terms':[
        {'variable':'subject'},*({'constant':v} for v in x['domain'][2:5])]}))
    def incompatible(x):
        x['predicates'].append({'id':'ScopeValue','version':'v1','sorts':['scope'],'role':'ordinary'})
        x['rules'][0]['body'].append({'predicate':'ScopeValue','terms':[{'variable':'subject'}]})
    reject('variable inconsistent sorts',incompatible)
    reject('conformance cannot justify admission leaf',lambda x:x['facts'].append(rooted['facts'][1]))
    reject('unbound checked-root leaf',lambda x:x['facts'].append({'predicate':'CheckedRoot','terms':rooted['facts'][1]['terms']}))
    reject('missing independent assessment',lambda x:x.update(root_assessments=[]),rooted)
    reject('nonempty receipt string is not root',lambda x:x.update(roots=['receipt:anything']),rooted)
    reject('wrong assessment digest',lambda x:x['roots'][0]['assessment_ref'].update(sha256='0'*64),rooted)
    reject('wrong assessment ID',lambda x:x['roots'][0]['assessment_ref'].update(id='receipt:other'),rooted)
    reject('wrong assessment version',lambda x:x['roots'][0]['assessment_ref'].update(version='v2'),rooted)
    reject('stale source binding',lambda x:x['root_assessments'][0]['source'].update(sha256='0'*64),rooted)
    for coordinate,other in [('target_version',{'id':'capability:reviewer','version':'v2'}),('effect','execution'),('scope','other'),('epoch',8)]:
        reject('root mismatched '+coordinate,lambda x,k=coordinate,v=other:x['roots'][0].update({k:v}),rooted)
    reject('root belongs to another snapshot epoch',lambda x:x.update(snapshot_epoch=8),rooted)
    reject('duplicate independent root',lambda x:x['roots'].append(x['roots'][0]),rooted)
    # Rehash altered evidence so controls test semantics, not just stale bytes.
    with tempfile.TemporaryDirectory(prefix='.receipt-controls-',dir=BASE) as temp:
        path=Path(temp)/'receipt.json'
        for name,changes in [('wrong evidence role',{'mode':'conformance'}),('unaccepted evidence',{'accepted':False}),
                             ('authority effect claimed',{'authority_effect':'admitted'}),('boolean receipt epoch',{'epoch':True})]:
            changed={**deepcopy(document),**changes};s.write(path,changed);bad=deepcopy(rooted)
            bad['root_assessments'][0]['source']=s.binding(path);bad['roots'][0]['assessment_ref']['sha256']=s.digest(path)
            reject(name,lambda x:None,bad)
        path.write_text('{"schema":"first","schema":"second"}')
        bad=deepcopy(rooted);bad['root_assessments'][0]['source']=s.binding(path);bad['roots'][0]['assessment_ref']['sha256']=s.digest(path)
        reject('duplicate receipt JSON key',lambda x:None,bad)
    for name,raw in [('duplicate input JSON key',b'{"schema":"a","schema":"b"}'),('nonfinite JSON number',b'{"x":NaN}'),
                     ('invalid UTF8',b'\xff'),('unpaired surrogate',b'{"x":"\\ud800"}')]:
        try:f.d.decode(raw)
        except (ValueError,UnicodeError):controls.append({'name':name,'result':'rejected'})
        else:raise ValueError('parser control accepted: '+name)
    profile={'schema':'relational.rule-profile/v1-candidate','id':'finite-positive-typed-horn/v1',
        'value_sorts':sorted(f.SORTS),'core_predicates':f.CORE,
        'domain':'Nonempty finite unique inventory; every fact, constant and substitution value belongs to it.',
        'rules':'Positive conjunction bodies, one head, no functions; all variables occur in body premises; zero-variable ground rules permitted.',
        'identity':'Predicate ID/version/content SHA; rule ID/version/source and resolved signature SHA; exact captured input SHA.',
        'version_resolution':'Only explicitly captured unique declaration; omitted input version resolves to its exact version/hash.',
        'normal_form':'Sorted variable names map to canonical typed slots; pattern and fact identities retain exact signature hashes.',
        'root_production':'CheckedRoot forbidden as rule head. Protected/carrier rule heads require separate I04 lineage review.',
        'unsupported':['negation','function terms','arithmetic constraints','generated identity','external fact lookup','unbounded time'],
        'formal_obligations':{'I02':'Generic certificate soundness for independent inductive derivability.',
                              'I03':'Finite grounding completeness, terminating closure and exact least-fixed-point certification.',
                              'I04':'Exact independent-root lineage for all protected/carrier producer chains.',
                              'I05':'Checked model non-entailment and positive conformance/admission coexistence.'},
        'projection':s.binding(BASE/'frontend.py'),'semantics':s.binding(BASE/'inference-semantics.md'),
        'authority_effect':'none','trust_boundary':'Strict parser, host projection, canonical hashing and supplied base/evidence truth; no Lean theorem claimed by I01.'}
    policy={'schema':'relational.protected-root-policy/v1-candidate','protected_predicate':'Admitted',
        'root_predicate':'CheckedRoot','coordinates':['targetVersion(id,version)','effect','scope','capturedAuthorityEpoch'],
        'matching':'Exact literal tuple equality, no wildcards, inherited scopes or version/epoch conversion.',
        'initial_facts':'Admitted, CheckedRoot and root-carrier leaves require a matching independent existing-admission receipt.',
        'evidence':'Bound receipt ID/version/SHA; existing-admission mode; accepted true; exact tuple and captured epoch; no authority effect.',
        'producer_policy':'Each protected/carrier producer has an exact same-tuple CheckedRoot or justified root-carrier premise; check all producers before generic lineage induction.',
        'conformance_is_root':False,'conformance_implies_not_admitted':False,
        'existing_admission_may_coexist_with_conformance':True,'root_observation_automatically_adds_admission':False,
        'untrusted_truth':'Receipt truth remains an assumption; syntactic evidence checks do not authenticate or authorize real-world admission.',
        'future_gate':'I04 proves lineage; I06/G3 discharge complete rule-change obligations; I01 is not readiness.',
        'authority_effect':'none'}
    for name,obj in [('example-input.json',request),('example-normal-form.json',normal),('coexistence-input.json',rooted),
                     ('coexistence-normal-form.json',coexist),('unsafe-coupling-input.json',leak),
                     ('rule-profile.json',profile),('protected-root-policy.json',policy)]:s.write(BASE/name,obj)
    s.write(BASE/'profile-controls.json',{'result':'pass','positive_cases':[
        'conformance-only roots absent','conformance with independently justified admission','root without automatic admission',
        'deterministic normalization','explicit and omitted captured version resolution','zero-variable captured constant rule',
        'well-typed authority leak remains pending I04 policy review'],
        'negative_controls':controls,'source_bindings':[s.binding(BASE/'frontend.py'),s.binding(Path(__file__)),s.binding(BASE/'fixtures/existing-admission.json')],
        'generic_theorems_claimed':False,'authority_effect':'none'})
    artifacts={name:BASE/name for name in ['rule-profile.json','protected-root-policy.json','inference-semantics.md',
        'frontend.py','run_profile.py','profile-controls.json','example-input.json','example-normal-form.json',
        'coexistence-input.json','coexistence-normal-form.json','unsafe-coupling-input.json']}
    artifacts['existing-admission-fixture']=BASE/'fixtures/existing-admission.json'
    s.accept('I01',artifacts,
        ['Exact target ID/version, effect, scope and captured epoch are fixed in predicate signatures, root receipts, leaves and the future producer policy; coordinate and evidence-role/digest controls reject mismatches.',
         'Finite typed range-restricted rule projection rejects generated identities, functions, external fields and unsafe variables. Independent conformance/admission coexistence passes; rule policy remains separately pending I04.'],
        ['Conformance-only input contains no roots/admission; fabricated protected leaves and nonempty receipt strings fail. Typed leaking rules are retained as unsafe analysis inputs and cannot yield policy readiness.',
         'No negative admission axiom is introduced; independently rooted Admitted and Conforms base facts coexist, and CheckedRoot observations do not automatically produce admission.'],
        [s.BASE/'input/decoder.py',s.BASE/'execution/support.py',s.BASE/'evolution/proposals/rule-change-proposal.json'])
    print(json.dumps({'task':'I01','result':'accepted','positive_cases':7,'negative_controls':len(controls),'authority_effect':'none'}))


if __name__=='__main__':main()
