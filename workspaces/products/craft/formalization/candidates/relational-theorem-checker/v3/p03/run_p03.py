"""Fresh public API/CLI/shadow-path checks and invocation isolation controls."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import copy
import json
import subprocess
import sys
import uuid
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]))
from v3.p03 import QualificationContext,qualify_fresh,inspect_saved,qualify_for_shadow
from v3.p03.context import C,BASE,read,write,binding,require
sys.path.insert(0,str(BASE/'execution'))
import support as s

request=read(BASE/'p01/request-fixture.json');request['build_mode']='warm'
controls=[]
journal_path=HERE/'validation-attempts'/uuid.uuid4().hex/'controls.json'
tested_sources=[binding(HERE/name) for name in ['context.py','qualification.py','cli.py','run_p03.py']]
def checkpoint():
    s.write(journal_path,{'schema':'relational.integration-observation/v1','tested_sources':tested_sources,'request_identity':C.identity(request),'controls':controls,'complete':False,'application_authorized':False,'authority_effect':'none'})
def check(name,condition):
    require(condition,'control failed '+name);controls.append({'name':name,'result':'pass'});checkpoint()
def negative(name,fn):
    try:fn()
    except Exception as e:controls.append({'name':name,'result':'pass','expected':'rejected','reason':str(e).splitlines()[0]});checkpoint();return
    raise AssertionError('unexpected acceptance '+name)

observed=read(HERE/'observed-timeout.json')
previous_timeout=read(s.check(observed['result']))
C.validate('result',previous_timeout)
check('observed-cli-replay-timeout-has-no-qualified-claims',previous_timeout['status']=='unknown-resource' and not previous_timeout['claims'] and not previous_timeout['complete_closure'] and not previous_timeout['application_authorized'])

broken=QualificationContext(HERE/'runs/fault-context',request['resource_policy'])
normal=QualificationContext(HERE/'runs/shadow-context',request['resource_policy'])
default=broken.compile_default
remaining=[1]
def fail_once(build,modules):
    if remaining[0]:remaining[0]-=1;raise ValueError('injected stage compiler failure in this invocation only')
    return default(build,modules)
broken.stage_compiler=fail_once
with ThreadPoolExecutor(max_workers=2) as executor:
    failed_future=executor.submit(qualify_fresh,request,broken)
    normal_future=executor.submit(qualify_for_shadow,request,normal)
    failed=failed_future.result();normal_result=normal_future.result()
check('isolated-stage-failure-refuses',failed['status']=='invalid' and failed['stage']=='projection-instance')
check('parallel-shadow-context-qualified',normal_result['status']=='qualified-candidate')
check('only-successful-invocation-has-live-event',normal.live_event(normal_result) and not broken.live_event(normal_result))
print('Independent shadow context freshly qualified while injected-failure context refused',flush=True)

recovered=qualify_fresh(request,broken)
check('same-context-subsequent-call-recovers',recovered['status']=='qualified-candidate' and broken.live_event(recovered))
check('private-build-roots-never-collide',normal_result['run_id']!=recovered['run_id'])
print('Python API freshly qualified after stage failure',flush=True)
unsafe_source=HERE/'unsafe-driver-control.lean'
unsafe_source.write_text('unsafe def fake : Nat := 0\n')
negative('untrusted-source-cannot-impersonate-verifier-driver',lambda:broken.compile_default(unsafe_source.parent,[('RuntimeVerifier',unsafe_source)]))

cli_request=HERE/'cli-request.json'
if cli_request.exists():require(read(cli_request)==request,'previous CLI fixture differs')
else:write(cli_request,request)
process=subprocess.run([sys.executable,str(HERE/'cli.py'),'qualify',str(cli_request),'--run-root',str(HERE/'runs/cli-context')],capture_output=True,text=True,timeout=request['resource_policy']['run_seconds'])
cli=C.decode(process.stdout.encode());check('public-cli-fresh-qualified',process.returncode==0 and cli['status']=='qualified-candidate')
print('CLI freshly qualified through identical public pipeline',flush=True)

cold_request=copy.deepcopy(request);cold_request['build_mode']='cold'
cold=qualify_fresh(cold_request,broken)
check('cold-build-with-pinned-operational-driver-qualified',cold['status']=='qualified-candidate' and broken.live_event(cold))
print('Cold API freshly qualified with the exact pinned operational driver',flush=True)

def semantic(result):
    payload=C.decode((s.ROOT/result['payload']['path']).read_bytes())
    return {k:payload[k] for k in ['closure','certificates','observations','supports','before_normal_form','normal_form']}
check('CLI-Python-shadow-semantic-output-agreement',semantic(cli)==semantic(recovered)==semantic(normal_result))
check('warm-cold-semantic-output-agreement',semantic(cold)==semantic(recovered))
check('CLI-Python-shadow-exact-request-agreement',cli['request_identity']==recovered['request_identity']==normal_result['request_identity']==C.identity(request))
check('full-twenty-hard-obligations-identical',cli['manifest']['obligations']==normal_result['manifest']['obligations']==[o['id'] for o in C.required_inventory('rule-only')])
inspection=inspect_saved(request,normal_result,broken)
check('saved-inspection-current-not-application-authority',inspection['status']=='recorded-current' and not inspection['application_authorized'])
check('saved-inspection-does-not-create-live-event',not broken.live_event(normal_result))
bad=copy.deepcopy(normal_result);bad['manifest']['obligations'].pop()
negative('caller-shrunken-catalog-refused',lambda:inspect_saved(request,bad,normal))
bad=copy.deepcopy(request);bad['resource_policy']['stage_seconds']=30
negative('cross-context-resource-policy-refused',lambda:inspect_saved(bad,normal_result,normal))
strict=copy.deepcopy(request);strict['resource_policy']['memory_mode']='required'
strict_ctx=QualificationContext(HERE/'runs/required-policy',strict['resource_policy'])
refused=qualify_fresh(strict,strict_ctx)
check('required-memory-policy-never-silently-advisory',refused['status']=='unsupported-policy' and refused['resource_report']['enforcement']=='unavailable')
check('no-global-compiler-patching',all('s.compile_modules=' not in (HERE/name).read_text() and 'r.qualify=' not in (HERE/name).read_text() for name in ['qualification.py','context.py']))
check('private-pure-module-ownership',C.__name__=='_relational_v3_contracts_context')

outputs=[]
for name,result in [('shadow',normal_result),('api',recovered),('cli',cli),('cold-api',cold),('injected-failure',failed),('required-policy-refusal',refused)]:
    outputs.append({'name':name,'build_mode':'cold' if name=='cold-api' else request['build_mode'],**write(HERE/(name+'-result.json'),result)})
s.write(HERE/'integration-controls.json',{'result':'pass','controls':controls,'qualified_outputs':outputs,'source_catalog':binding(BASE/'p01/catalog.json'),'method':'Three actual fresh source/witness/general kernel qualifications through public Python, shadow consumer and CLI with the identical request, plus full cold qualification; concurrent context isolation, failure/recovery and saved-inspection controls.','aggregate_resource_enforcement':'Advisory at this layer; P06 implements required supervision.','authority_effect':'none'})
s.accept('P03',[
    'Actual CLI, Python and shadow consumers freshly qualify the identical request and agree on normalized theories, closures, certificates, observations, supports and all 20 hard obligations; a separate actual cold build gives the same semantic output.',
    'Each context owns its compiler/policy/run roots/live replay events; pure successor modules use private names and legacy normalization/inspection runs in a dedicated process, with no process-global function replacement.',
    'A concurrently injected compiler failure refuses only its own run; the independent invocation succeeds, a subsequent call recovers, saved inspection creates no replay event, and policy/catalog substitution controls reject.'
],controls,extra=[HERE/'__init__.py',HERE/'inspect_worker.py',HERE/'run_p03.py',HERE/'API.md',HERE/'observed-timeout.json',s.check(observed['result']),unsafe_source,cli_request,journal_path]+[s.ROOT/x['path'] for x in outputs])
print('P03 accepted')
