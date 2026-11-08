"""Review every grounded protected/carrier producer and replay generic lineage."""
import json
from pathlib import Path
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'closure'))
import closure_checker as c
f=c.f;s=c.s;d=c.d
BASE=Path(__file__).resolve().parent


def analyze(normal,max_instances=100000):
    instances,reason=c.enumerate_instances(normal,max_instances)
    if reason:return {'status':'unknown','reason':reason,'root_lineage_proved':False,'authority_effect':'none'}
    roles={f.identity({k:p[k] for k in ['id','version','hash']}):p['role'] for p in normal['predicates']}
    violations=[];producers=0
    for i in instances:
        if roles[f.identity(i['head']['predicate'])]=='ordinary':continue
        producers+=1
        matches=[a for a in i['body'] if roles[f.identity(a['predicate'])] in ['checked-root','root-carrier'] and a['values']==i['head']['values']]
        if not matches:violations.append({'rule':i['rule'],'substitution':i['substitution'],'conclusion':i['head'],
                                         'premises':i['body'],'cause':'No same-tuple checked-root or justified root-carrier premise.'})
    return {'status':'candidate-safe' if not violations else 'candidate-violation','ground_instances':len(instances),
            'protected_or_carrier_producers':producers,'violations':violations,'root_lineage_proved':False,'authority_effect':'none'}


def prepare(normal,build):
    logs=c.prepare(normal,build);audit=c.c.policy();source=(BASE/'ProtectedLineage.lean').read_text()
    s.require(audit.source_policy(source),'forbidden lineage proof bypass')
    import re
    s.require(set(re.findall(r'^import ([A-Za-z0-9_.]+)$',source,re.M))=={'ClosureAdequacy'},'unexpected lineage proof import')
    logs+=s.compile_lean(build,[('ProtectedLineage',BASE/'ProtectedLineage.lean')])
    return logs


def query_source(normal,accepted,query):
    source='import InferenceFixture\nimport ProtectedLineage\nset_option maxRecDepth 8192\nset_option maxHeartbeats 4000000\nopen Inference Inference.Captured\n'
    source+='theorem checked_result : checkLineage theory facts = '+('true' if accepted else 'false')+' := by decide\n#print axioms checked_result\n'
    if accepted:
        source+='theorem exact_root_lineage : ∀ a, Derivable theory facts a → Rooted theory a → a.values ∈ theory.roots := checked_protected_lineage theory facts\n'
        # The parameter ordering of the general theorem retains the actual
        # successful check, rather than assuming it in the captured statement.
        source=source.replace(':= checked_protected_lineage theory facts\n',':= fun a derived rooted => checked_protected_lineage theory facts a checked_result derived rooted\n')
        source+='#print axioms exact_root_lineage\n'
        if query is not None and query['values'] not in [r['values'] for r in normal['roots']]:
            source+='def protectedQuery : Atom := '+c.c.atom_lean(query)+'\n'
            source+='theorem query_rooted : Rooted theory protectedQuery := by decide\n'
            source+='theorem query_has_no_matching_root : protectedQuery.values ∉ theory.roots := by decide\n'
            source+='theorem checked_no_unrooted_derivation : ¬ Derivable theory facts protectedQuery := no_unrooted_protected_derivation checked_result query_rooted query_has_no_matching_root\n#print axioms checked_no_unrooted_derivation\n'
    return source


def check(request,query=None,build=None,max_instances=100000):
    normal=f.normalize(request);analysis=analyze(normal,max_instances)
    if analysis['status']=='unknown':return analysis
    atom=None if query is None else c.c.captured_atom(normal,query)
    if atom is not None:
        sig=next(p for p in normal['predicates'] if {k:p[k] for k in ['id','version','hash']}==atom['predicate'])
        s.require(sig['role']!='ordinary' and [v['kind'] for v in atom['values']]==sig['sorts'] and all(v in normal['domain'] for v in atom['values']),'lineage negative query must be a typed captured protected/carrier/root atom')
    accepted=not analysis['violations']
    if build is None:
        with tempfile.TemporaryDirectory(prefix='lineage-check-') as folder:
            build=Path(folder);prepare(normal,build);return check(request,query,build,max_instances)
    s.require((build/'InferenceFixture.lean').read_text()==c.c.fixture_source(normal),'lineage build contains another snapshot')
    result=c.c.compile_generated(build,'LineageQuery',query_source(normal,accepted,atom))
    s.require(f.normalize(request)==normal,'lineage dependencies changed during replay')
    absent=atom is not None and atom['values'] not in [r['values'] for r in normal['roots']]
    return {**analysis,'status':'checked-root-lineage' if accepted else 'protected-policy-violation',
        'accepted':accepted,'root_lineage_proved':accepted,'no_unrooted_derivation_proved':accepted and absent,
        'normal_form_identity':normal['normal_form_identity'],'source_sha256':result['generated_source_sha256'],
        'olean_sha256':result['olean_sha256'],'axioms':result['axioms'],'authority_effect':'none',
        'scope':'All valid grounded protected/carrier producers in the exact finite captured theory; generic induction retains exact independent tuple lineage.',
        'truth_boundary':'Independent existing-admission assessment truth remains supplied; this review performs no authority transition or issuer authentication.',
        'readiness':'Requires I05/I06/G3 complete extension evidence.'}


def main():
    import argparse
    import subprocess
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('request',type=Path)
    parser.add_argument('--query',type=Path);args=parser.parse_args()
    try:result=check(d.decode(args.request.read_bytes()),None if args.query is None else d.decode(args.query.read_bytes()))
    except (ValueError,UnicodeError) as error:result={'status':'invalid-input','diagnostic':str(error),'accepted':False,'authority_effect':'none'}
    except (subprocess.TimeoutExpired,OSError) as error:result={'status':'execution-failed','diagnostic':str(error),'root_lineage_proved':False,'accepted':False,'authority_effect':'none'}
    print(json.dumps(result,ensure_ascii=False));return 0 if result.get('accepted') else 1


if __name__=='__main__':raise SystemExit(main())
