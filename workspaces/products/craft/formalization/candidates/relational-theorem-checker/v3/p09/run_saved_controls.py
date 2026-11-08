"""New interface and hostile saved-evidence controls; no fresh event is fabricated."""
from pathlib import Path
import copy
import json
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sys.path.insert(0,str(BASE.parent))
from v3.p03.context import C,binding,check,require
from v3.p09.api import describe,validate,validate_application,resource_status
from v3.p04.explain import classify_query
from v3.p03 import QualificationContext,inspect_saved
request=C.decode((BASE/'p03/cli-request.json').read_bytes());result=C.decode((BASE/'p03/api-result.json').read_bytes())
context=QualificationContext(HERE/'saved-control-context',request['resource_policy'])
payload=C.decode(check(result['payload']).read_bytes());controls=[];cases=[]
input_ref=binding(BASE/'p03/api-result.json')
def test(name,ok,kind='contract',observed='expected refusal',challenge=None):
    require(ok,name);controls.append({'name':name,'result':'pass'})
    p=HERE/'saved-challenges'/(name+('.raw' if isinstance(challenge,bytes) else '.json'));p.parent.mkdir(exist_ok=True)
    p.write_bytes(challenge if isinstance(challenge,bytes) else (json.dumps(challenge if challenge is not None else {'case':name,'harness':binding(Path(__file__))},indent=2)+'\n').encode())
    cases.append({'name':name,'evidence_kind':kind,'input':binding(p),'observed':observed})
def negative(name,fn,kind='saved-inspection',challenge=None):
    try:fn()
    except Exception as e:test(name,True,kind,str(e).splitlines()[0][:350],challenge);return
    raise AssertionError('Hostile accepted: '+name)
for name,modify in [
    ('missing-obligation',lambda q:q['manifest']['obligations'].pop()),
    ('catalog-substitution',lambda q:q['manifest']['identity'].update(catalog='0'*64)),
    ('profile-substitution',lambda q:q['manifest']['identity'].update(profile='0'*64)),
    ('toolchain-substitution',lambda q:q['manifest']['identity'].update(toolchain='0'*64)),
    ('missing-module',lambda q:q['manifest']['witness']['modules'].pop()),
    ('caller-absence-claim',lambda q:q['claims'][0].update(kind='absence')),
    ('sampled-model-claim',lambda q:q['claims'][0].update(model_class='sampled-least-closure')),
    ('omitted-root-truth-assumption',lambda q:q['claims'][0]['truth_assumptions'].pop()),
    ('application-authority-flag',lambda q:q.update(application_authorized=True))]:
    bad=copy.deepcopy(result);modify(bad);negative(name,lambda bad=bad:inspect_saved(request,bad,context),challenge={'request':binding(BASE/'p03/cli-request.json'),'result':bad})
atom=copy.deepcopy(next(a for a in payload['closure'] if a['predicate']['id']=='ContractReady'))
for name,modify,expected in [
    ('predicate-digest',lambda a:a['predicate'].update(hash='0'*64),'outside-profile'),
    ('predicate-version',lambda a:a['predicate'].update(version='unknown'),'outside-profile'),
    ('reference-revision',lambda a:a['values'][0].update(version='unknown'),'outside-profile'),
    ('arity',lambda a:a['values'].append(a['values'][0]),'invalid-query'),
    ('sort',lambda a:a['values'].__setitem__(0,{'kind':'scope','value':'static'}),'invalid-query')]:
    q=copy.deepcopy(atom);modify(q);out=describe(request,result,q,context)
    test('unified-query-'+name,out['outcome']==expected and out['trace'] is None,'saved-inspection',out['outcome'],q)
null_success={'schema':'relational.shadow-application/v3','status':'applied-candidate-shadow','reason':'','before':None,'after':None,'transaction':None,'seconds':0,'authority_effect':'none','application_authorized':False}
negative('forged-null-applied-success',lambda:validate_application(null_success),'contract',null_success)
applied=C.decode((BASE/'p08/publication-controls.json').read_bytes())['applications'][0]
bad=copy.deepcopy(applied);bad['after']['generation']+=1
negative('unrelated-head-generation-success',lambda:validate_application(bad),'contract',bad)
bad=copy.deepcopy(applied);bad['transaction']['phase']='prepared'
negative('uncommitted-transaction-success',lambda:validate_application(bad),'contract',bad)
test('composed-deadline-is-resource',resource_status('cancelled','Explicit cancellation.',True)=='unknown-resource','contract','unknown-resource')
test('explicit-user-cancel-retained',resource_status('cancelled','Explicit cancellation.',False)=='cancelled','contract','cancelled')
test('postcommit-success-never-downgraded',resource_status('applied-candidate-shadow','',True)=='applied-candidate-shadow','contract','applied-candidate-shadow')
test('atomic-tool-refusal-cause',resource_status('invalid','Atomic tool deadline exceeded.')=='unknown-resource','contract','unknown-resource')
test('ordinary-invalid-not-resource',resource_status('invalid','Malformed request.')=='invalid','contract','invalid')
# This decoder exercise is deliberately separate from public supervised runs.
for name,raw in [('duplicate-key',b'{"a":0,"a":1}'),('nan',b'{"a":NaN}'),('infinite',b'{"a":1e999}'),('excess-depth',('['*65+'0'+']'*65).encode())]:
    negative('strict-decoder-'+name,lambda raw=raw:C.decode(raw),'decoder',raw)
report={'result':'pass','controls':controls,'cases':cases,'source_request':binding(BASE/'p03/cli-request.json'),'source_result':input_ref,
        'actual_fresh_kernel_qualifications':0,'scope':'New saved inspection/interface/decoder controls; inherited fresh qualifications are not reissued by reading their files.','authority_effect':'none'}
(HERE/'saved-controls.json').write_text(json.dumps(report,indent=2)+'\n')
print('New saved/interface controls passed:',len(controls),flush=True)
