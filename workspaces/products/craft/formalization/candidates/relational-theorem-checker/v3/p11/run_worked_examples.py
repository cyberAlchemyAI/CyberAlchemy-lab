"""Actual new public commands plus exact recorded mapped/refusal explanations."""
from pathlib import Path
import copy
import json
import subprocess
import sys
import uuid
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sys.path.insert(0,str(BASE.parent))
from v3.p03.context import C,ROOT,binding,check,require
from v3.p09.api import Client
from v3.p04.explain import describe as mapped_describe

run_id=uuid.uuid4().hex;outdir=HERE/'evidence'/run_id;outdir.mkdir(parents=True);controls=[];cases=[]
request_ref=binding(BASE/'p09/rich-combined-request.json');public_ref=binding(BASE/'p09/rich-combined-result.json')
request=C.decode(check(request_ref).read_bytes());public=C.decode(check(public_ref).read_bytes());policy=request['resource_policy']
payload=C.decode(check(public['qualification']['qualified_result']['payload']).read_bytes())
def save(name,value):
    p=outdir/(name+'.json');require(not p.exists(),'worked evidence overwrite refused');p.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n');return binding(p)
def test(name,ok):require(ok,name);controls.append({'name':name,'result':'pass'});print(name,'PASS',flush=True)
def progress():
    (HERE/'worked-progress.json').write_text(json.dumps({'run_id':run_id,'controls':controls,'cases':cases,'authority_effect':'none'},indent=2)+'\n')
policy_ref=save('operator-policy',policy)
def cli(name,operation,input_ref,extra,expected_status,expected_exit=0):
    args=[sys.executable,str(BASE/'p09/cli.py'),operation,str(check(input_ref)),'--policy',str(check(policy_ref)),
          '--run-root',str(BASE/'p07/consumer-runs'/('P11-'+name+'-'+run_id)),*extra]
    invocation=save(name+'-invocation',{'argv':args,'input':input_ref,'policy':policy_ref,'expected_status':expected_status,'expected_exit':expected_exit})
    p=subprocess.run(args,cwd=ROOT,capture_output=True,timeout=policy['run_seconds']+120)
    require(len(p.stdout)<=8388608,'worked command output envelope');value=C.decode(p.stdout)
    observed=value.get('status',value.get('outcome'));output=save(name+'-output',value)
    cases.append({'name':name,'entry_point':'p09/cli.py '+operation,'invocation':invocation,'input':input_ref,'output':output,
        'observed':observed,'exit_code':p.returncode,'evidence_kind':'new-fresh-kernel' if operation=='qualify' else 'new-saved-inspection'})
    progress();test(name+'-actual-command',observed==expected_status and p.returncode==expected_exit)
    return value,output

_,_=cli('positive-inspection','inspect',request_ref,['--result',str(check(public_ref))],'recorded-current')
query=next(a for a in payload['closure'] if a['predicate']['id']=='ContractReady');query_ref=save('positive-query',query)
positive,positive_ref=cli('positive-rich-trace','describe',request_ref,['--result',str(check(public_ref)),'--query',str(check(query_ref))],'present')
test('positive-rich-trace-has-two-source-premises',positive['trace'] is not None and len(positive['supports'])>=2 and not positive['application_authorized'])

wrong=copy.deepcopy(request);wrong['layout']='staged';wrong['proposal']['proposal_id']='P11-wrong-scope-unseeded-cycle'
rule=next(r for r in wrong['proposal']['after']['inference']['rules'] if r['id']=='review-exact-contract-scope')
rule['version']='v3-worked-other-scope';rule['body'][0]['terms'][2]['constant']['value']='other-scope'
test('wrong-scope-keeps-old-frame',wrong['proposal']['before']==request['proposal']['before'] and wrong['proposal']['after']['inference']['domain']==request['proposal']['after']['inference']['domain'])
C.validate('request',wrong);wrong_ref=save('wrong-scope-request',wrong)
wrong_public,wrong_public_ref=cli('wrong-scope-full-qualification','qualify',wrong_ref,[],'qualified-candidate')
test('wrong-scope-full-twenty-obligations',wrong_public['qualification']['qualified_result']['manifest']['obligations']==[o['id'] for o in C.required_inventory('rule-only')])
wrong_explanation,wrong_explanation_ref=cli('wrong-scope-unseeded-cycle','describe',wrong_ref,['--result',str(check(wrong_public_ref)),'--query',str(check(query_ref))],'absent-in-complete-profile')
test('wrong-scope-absence-is-recorded-not-readiness',not wrong_explanation['application_authorized'] and wrong_explanation['trace'] is None)

bad=copy.deepcopy(public);bad['qualification']['qualified_result']['manifest']['obligations'].pop();bad_ref=save('missing-obligation-result',bad)
missing,missing_ref=cli('missing-obligation-refusal','inspect',request_ref,['--result',str(check(bad_ref))],'invalid',2)
test('missing-proof-does-not-authorize',not missing['application_authorized'])

mapped_report=C.decode((BASE/'p08/mapped-controls.json').read_bytes())
unknown=next(c['answer'] for c in mapped_report['cases'] if c['name']=='unknown-potential')
active=C.decode((BASE/'p09/active-conflict-result.json').read_bytes())
for name,value in [('unknown-potential-norm',unknown),('active-conflicting-norms',active)]:
    mapped_request=C.decode(check(value['value']['request']).read_bytes());mapped_result=C.decode(check(value['value']['result']).read_bytes())
    explanation=mapped_describe(mapped_request,mapped_result);ref=save(name+'-explanation',explanation)
    cases.append({'name':name,'entry_point':'p04.explain.describe exact mapped API','input':value['value']['request'],'source_result':value['value']['result'],
        'source_completion':value['completion'],'output':ref,'observed':explanation['condition_status'],'evidence_kind':'new-saved-inspection-of-prior-fresh-mapping'})
    test(name+'-exact-meaning',explanation['inspection']=='recorded-current' and not explanation['application_authorized'] and explanation['fulfilled']=='not-established' and explanation['admission']=='not-derived')
    if name=='unknown-potential-norm':test('unknown-keeps-potential-not-active',explanation['condition_status']=='unknown' and explanation['potential_norms'] and not explanation['active_norms'])
    else:test('active-conflict-preserves-both-origins',explanation['condition_status']=='yes' and len(explanation['active_conflicts'])==1 and len(explanation['active_conflicts'][0])==2)
    progress()

hostile=C.decode((BASE/'p09/public-hostile-controls.json').read_bytes())
for name,source_name,expected in [('resource-exhaustion','atomic-stage-budget','unknown-resource'),('operator-cancellation','actual-user-cancellation','cancelled')]:
    source=next(c for c in hostile['cases'] if c['name']==source_name);r=C.decode(check(source['input']).read_bytes());answer=C.decode(check(source['answer']).read_bytes())
    explanation=Client(r['resource_policy']).describe(r,answer);ref=save(name+'-explanation',explanation)
    cases.append({'name':name,'entry_point':'p09.Client.describe','input':source['input'],'source_result':source['answer'],'output':ref,
        'observed':answer['status'],'evidence_kind':'new-explanation-of-actual-public-refusal'})
    test(name+'-no-false-absence',answer['status']==expected and explanation['outcome']=='incomplete' and not explanation['application_authorized']);progress()

layout=C.decode((BASE/'p09/layout-suite.json').read_bytes())
numeric=[e for e in layout['events'] if e['name'] in ['combined-numeric-query','combined-boolean-query']]
for e in numeric:check(e['value'])
report={'result':'pass','run_id':run_id,'controls':controls,'cases':cases,'numeric_examples':numeric,
    'approved_v2_packet':binding(BASE.parent/'v2/s13/review-packet.md'),'actual_v2_feedback':binding(BASE.parent/'v2/s14/human-feedback.json'),
    'new_fresh_horn_qualifications':1,'new_mapped_qualifications':0,'pending_human_assessment':True,
    'scope':'One actual new full wrong-scope qualification; new public recorded explanations/refusals. Prior fresh evidence stays source-bound and is not reissued by reading it.','authority_effect':'none'}
(HERE/'worked-examples.json').write_text(json.dumps(report,indent=2)+'\n');print('Worked examples complete:',len(controls),'controls',flush=True)
