"""Finite saturation candidates plus kernel-certified least closures."""
from copy import deepcopy
import itertools
import json
from pathlib import Path
import sys
import tempfile
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'derivations'))
import derivation_checker as c
f=c.f;s=c.s;d=c.d
BASE=Path(__file__).resolve().parent


def raw_atom(atom):
    return {'predicate':atom['predicate']['id'],'version':atom['predicate']['version'],'terms':deepcopy(atom['values'])}


def unknown(reason,normal,count=0):
    return {'status':'unknown','reason':reason,'normal_form_identity':normal['normal_form_identity'],
            'ground_instances_examined':count,'closure_complete':False,'non_derivability_proved':False,'authority_effect':'none'}


def enumerate_instances(normal,limit=100000,deadline=None):
    """Typed substitution enumeration; completeness is proved in Lean separately."""
    instances=[]
    for rule in normal['rules']:
        choices=[[v for v in normal['domain'] if v['kind']==variable['sort']] for variable in rule['variables']]
        for combination in itertools.product(*choices):
            if deadline is not None and time.monotonic()>=deadline:return None,'grounding-timeout'
            if limit is not None and len(instances)>=limit:return None,'grounding-resource-limit'
            values=list(combination)
            instances.append({'rule':{k:rule[k] for k in ['id','version','hash']},'substitution':values,
                              'head':c.instantiated(rule['head'],values),
                              'body':[c.instantiated(p,values) for p in rule['body']]})
    return instances,None


def compute(request,max_instances=100000,max_steps=None,time_limit=None):
    normal=f.normalize(request)
    s.require(max_instances is None or type(max_instances) is int and max_instances>=0,'invalid grounding resource limit')
    s.require(max_steps is None or type(max_steps) is int and max_steps>=0,'invalid saturation resource limit')
    s.require(time_limit is None or type(time_limit) in [int,float] and time_limit>=0,'invalid time limit')
    deadline=None if time_limit is None else time.monotonic()+time_limit
    instances,reason=enumerate_instances(normal,max_instances,deadline)
    if reason:return unknown(reason,normal)
    current=deepcopy(normal['facts']);positions={f.identity(a):'fact:'+str(i) for i,a in enumerate(current)}
    steps=[{'id':positions[f.identity(a)],'kind':'base','conclusion':raw_atom(a)} for a in current]
    remaining=[]
    for ground in instances:
        if ground['head'] not in current and ground['head'] not in remaining:remaining.append(ground['head'])
    initial_measure=len(remaining);transitions=[]
    while True:
        if deadline is not None and time.monotonic()>=deadline:return unknown('saturation-timeout',normal,len(instances))
        enabled=next((i for i in instances if i['head'] in remaining and all(a in current for a in i['body'])),None)
        if enabled is None:break
        if max_steps is not None and len(transitions)>=max_steps:return unknown('saturation-resource-limit',normal,len(instances))
        before=len(remaining);remaining.remove(enabled['head']);current.append(enabled['head']);name='derived:'+str(len(transitions))
        rule=next(r for r in normal['rules'] if {k:r[k] for k in ['id','version','hash']}==enabled['rule'])
        steps.append({'id':name,'kind':'apply','conclusion':raw_atom(enabled['head']),'rule':enabled['rule'],
                      'substitution':{v['name']:value for v,value in zip(rule['variables'],enabled['substitution'])},
                      'premises':[positions[f.identity(a)] for a in enabled['body']]})
        positions[f.identity(enabled['head'])]=name
        transitions.append({'before_measure':before,'after_measure':len(remaining),'head':enabled['head']})
        s.require(len(remaining)<before,'finite saturation did not decrease its pending head measure')
    bundle={'schema':'relational.closure-certificate/v1','normal_form_identity':normal['normal_form_identity'],
        'closure':[raw_atom(a) for a in current],
        'certificates':[{'schema':'relational.derivation-certificate/v1','normal_form_identity':normal['normal_form_identity'],
                         'query':raw_atom(a),'steps':deepcopy(steps)} for a in current], 'negative_query':None}
    return {'status':'candidate-complete','closure_complete':False,'non_derivability_proved':False,
            'normal_form_identity':normal['normal_form_identity'],'bundle':bundle,'ground_instance_count':len(instances),
            'termination':{'initial_remaining_heads':initial_measure,'steps':len(transitions),'strict_decreases':transitions},
            'scope':'Computed candidate requires independent closure kernel certification. No absence claim before that replay.',
            'authority_effect':'none'}


def normalize_bundle(normal,bundle):
    f.fields(bundle,['schema','normal_form_identity','closure','certificates','negative_query'],'closure certificate')
    s.require(bundle['schema']=='relational.closure-certificate/v1','unknown closure certificate version')
    s.require(bundle['normal_form_identity']==normal['normal_form_identity'],'closure belongs to another captured theory/fact/root snapshot')
    s.require(isinstance(bundle['closure'],list) and isinstance(bundle['certificates'],list),'closure inventories must be lists')
    atoms=[c.captured_atom(normal,a) for a in bundle['closure']]
    certificates=[c.normalize_certificate(normal,cert) for cert in bundle['certificates']]
    query=None if bundle['negative_query'] is None else c.captured_atom(normal,bundle['negative_query'])
    return {'closure':atoms,'certificates':certificates,'query':query}


def projected_result(normal,bundle):
    atoms=bundle['closure']
    if len({f.identity(a) for a in atoms})!=len(atoms):return False
    def valid_atom(a):
        sig=next((p for p in normal['predicates'] if {k:p[k] for k in ['id','version','hash']}==a['predicate']),None)
        return sig is not None and [v['kind'] for v in a['values']]==sig['sorts'] and all(v in normal['domain'] for v in a['values'])
    if not all(valid_atom(a) for a in atoms) or not all(a in atoms for a in normal['facts']):return False
    instances,reason=enumerate_instances(normal,limit=None);s.require(reason is None,'internal complete grounding failed')
    if any(all(a in atoms for a in i['body']) and i['head'] not in atoms for i in instances):return False
    return all(any(c.projected_result(normal,{'query':a,'steps':cert['steps']}) for cert in bundle['certificates']) for a in atoms)


def prepare(normal,build):
    logs=c.prepare(normal,build)
    audit=c.policy();source=(BASE/'ClosureAdequacy.lean').read_text()
    s.require(audit.source_policy(source),'forbidden closure proof bypass')
    import re
    s.require(set(re.findall(r'^import ([A-Za-z0-9_.]+)$',source,re.M))=={'DerivationSoundness'},'unapproved closure dependency')
    logs+=s.compile_lean(build,[('ClosureAdequacy',BASE/'ClosureAdequacy.lean')])
    return logs


def query_source(bundle,accepted,query_absent):
    source='import InferenceFixture\nimport ClosureAdequacy\nset_option maxRecDepth 8192\nset_option maxHeartbeats 4000000\nopen Inference Inference.Captured\n'
    source+='def closure : List Atom := '+d.rows(bundle['closure'],c.atom_lean)+'\n'
    source+='def certificates : List (List Step) := '+d.rows(bundle['certificates'],lambda cert:d.rows(cert['steps'],c.step_lean))+'\n'
    source+='theorem checked_result : checkClosure theory facts closure certificates = '+('true' if accepted else 'false')+' := by decide\n#print axioms checked_result\n'
    if accepted:
        source+='theorem exact_least_closure : ∀ a, a ∈ closure ↔ Derivable theory facts a := checked_closure_exact checked_result\n#print axioms exact_least_closure\n'
        # The actual finite saturation algorithm is replayed independently of
        # the supplied certificate, using its own complete Lean grounding.
        source+='def computed : List Atom := saturate (groundInstances theory) facts ((groundInstances theory).map GroundInstance.head |>.filter (fun a => !(a ∈ facts)))\n'
        source+='theorem saturation_matches : (∀ a ∈ closure, a ∈ computed) ∧ (∀ a ∈ computed, a ∈ closure) := by decide\n#print axioms saturation_matches\n'
        if bundle['query'] is not None:
            source+='def negativeQuery : Atom := '+c.atom_lean(bundle['query'])+'\n'
            if query_absent:
                source+='theorem query_absent : negativeQuery ∉ closure := by decide\n'
                source+='theorem checked_non_derivability : ¬ Derivable theory facts negativeQuery := absent_from_checked_closure_not_derivable checked_result negativeQuery query_absent\n#print axioms checked_non_derivability\n'
            else:source+='theorem requested_query_is_present : negativeQuery ∈ closure := by decide\n#print axioms requested_query_is_present\n'
    return source


def check(request,bundle,build=None):
    normal=f.normalize(request);projected=normalize_bundle(normal,bundle);accepted=projected_result(normal,projected)
    query_absent=projected['query'] is not None and projected['query'] not in projected['closure']
    if build is None:
        with tempfile.TemporaryDirectory(prefix='closure-certificate-') as folder:
            build=Path(folder);prepare(normal,build);return check(request,bundle,build)
    s.require((build/'InferenceFixture.lean').read_text()==c.fixture_source(normal),'private closure build has another snapshot')
    result=c.compile_generated(build,'ClosureQuery',query_source(projected,accepted,query_absent))
    s.require(f.normalize(request)==normal,'closure dependencies changed during replay')
    return {'status':'checked-least-closure' if accepted else 'rejected-closure','accepted':accepted,
        'closure_complete':accepted,'non_derivability_proved':accepted and query_absent,
        'negative_query_status':'not-requested' if projected['query'] is None else ('checked-non-derivable' if accepted and query_absent else 'query-derived' if accepted else 'unknown'),
        'normal_form_identity':normal['normal_form_identity'],'certificate_identity':f.identity(bundle),
        'source_sha256':result['generated_source_sha256'],'olean_sha256':result['olean_sha256'],'axioms':result['axioms'],
        'protected_policy_review':'requires-I04-lineage-review','authority_effect':'none',
        'scope':'Exact finite captured Horn theory and initial facts; no full registry semantics or admission authority.'}


def main(mode):
    import argparse
    import subprocess
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('request',type=Path)
    if mode=='check':parser.add_argument('certificate',type=Path)
    else:
        parser.add_argument('--max-instances',type=int,default=100000);parser.add_argument('--max-steps',type=int)
        parser.add_argument('--time-limit',type=float)
    args=parser.parse_args()
    try:
        request=d.decode(args.request.read_bytes())
        result=check(request,d.decode(args.certificate.read_bytes())) if mode=='check' else compute(request,args.max_instances,args.max_steps,args.time_limit)
    except (ValueError,UnicodeError) as error:result={'status':'invalid-input','diagnostic':str(error),'authority_effect':'none'}
    except (subprocess.TimeoutExpired,OSError) as error:result={'status':'execution-failed','diagnostic':str(error),'non_derivability_proved':False,'authority_effect':'none'}
    print(json.dumps(result,ensure_ascii=False));return 0 if result['status'] in ['checked-least-closure','candidate-complete'] else 1
