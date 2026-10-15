"""Synthetic arithmetic/schema fixtures only; no actual timing calibration."""
import copy,hashlib,importlib.util,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_T03_own_margin_arithmetic',HERE/'margin.py')
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
IDENTITY={name:'1'*64 for name in M.IDENTITY_FIELDS}
POLICY={'schema_version':'lab-observed-lifetime-margin/v1-candidate','authority_effect':'none',
        'status':'empirically-qualified','execution_identity':IDENTITY,
        'evidence_bindings':[{'path':'synthetic/inert-fixture.json','sha256':'2'*64}],
        'uncertainty_method':'observed-maximum-plus-reviewed-uncertainty','sample_count':1,
        'phase_upper_bounds_us':{name:1000000 for name in M.REMAINING['application-preclaim']},
        'uncertainty_reserve_us':2000000,'gate_overhead_upper_bound_us':1000000,
        'valid_until':'2030-01-01T12:00:00Z'}
CURRENT='2030-01-01T00:00:00Z'
DEADLINES={name:'2030-01-01T00:02:00Z' for name in M.DEADLINE_FIELDS}
DEADLINES['Session']='2030-01-01T00:01:00Z'
cases=[]
def call(policy=POLICY,identity=IDENTITY,deadlines=DEADLINES,current=CURRENT,checkpoint='application-preclaim',load_current=True):
    return M.decide(policy,identity,deadlines,current,checkpoint,load_current=load_current)
def refused(name,callback,reason):
    try:callback()
    except M.MarginRefusal as error:assert error.reason==reason
    else:raise AssertionError(name+' accepted')
    cases.append({'case':name,'result':'PASS-refused','reason':reason})
assert call()['remaining_real_lease_us']==60000000
assert call()['required_observed_tail_us']==12000000
assert call()['remaining_margin_us']==48000000
cases.append({'case':'synthetic full tail, strictest direct bound and margin arithmetic','result':'PASS'})
assert call(checkpoint='assessment-preclaim')['required_observed_tail_us']==8000000
cases.append({'case':'synthetic assessment excludes already elapsed application/preparation tail','result':'PASS'})
template=json.loads((HERE/'UNQUALIFIED-POLICY-TEMPLATE.json').read_bytes())
refused('all real empirical inputs still unknown',lambda:call(policy=template),'empirical-policy-unqualified')
refused('no policy',lambda:call(policy=None),'empirical-policy-missing-or-open')
refused('unknown or outside-calibration actual load',lambda:call(load_current=False),'actual-load-unknown-or-outside-calibration')
refused('source/profile/code/cut/dependency/load/instrumentation mismatch',lambda:call(identity={**IDENTITY,'code_closure_sha256':'3'*64}),'empirical-execution-identity-differs')
bad=copy.deepcopy(POLICY);bad['phase_upper_bounds_us']['original-cleanup']=None
refused('missing cleanup bound',lambda:call(policy=bad),'empirical-phase-bound-unknown')
bad=copy.deepcopy(POLICY);bad['gate_overhead_upper_bound_us']=None
refused('unknown new gate overhead',lambda:call(policy=bad),'empirical-uncertainty-or-gate-overhead-unknown')
refused('missing actual parent Session deadline',lambda:call(deadlines={k:v for k,v in DEADLINES.items() if k!='Session'}),'real-lifetime-bound-missing')
refused('exact equality refuses before any hypothetical effect',lambda:call(deadlines={**DEADLINES,'Session':'2030-01-01T00:00:12Z'}),'real-lease-cannot-fit-observed-tail')
refused('shortest Context deadline controls independently',lambda:call(deadlines={**DEADLINES,'Context_delivery':'2030-01-01T00:00:11Z'}),'real-lease-cannot-fit-observed-tail')
refused('later observation cannot reuse earlier remaining lease',lambda:call(current='2030-01-01T00:00:49Z'),'real-lease-cannot-fit-observed-tail')
bad=copy.deepcopy(POLICY);bad['valid_until']=CURRENT
refused('expired empirical qualification',lambda:call(policy=bad),'empirical-policy-expired')
bad=copy.deepcopy(POLICY);bad['uncertainty_reserve_us']=True
refused('bool is not numeric uncertainty bound',lambda:call(policy=bad),'empirical-uncertainty-or-gate-overhead-unknown')
bad=copy.deepcopy(POLICY);bad['evidence_bindings'][0]['path']='../private'
refused('unsafe empirical binding locator',lambda:call(policy=bad),'empirical-evidence-path-unsafe')
refused('invalid actual calendar date',lambda:call(current='2030-02-30T00:00:00Z'),'invalid-real-deadline')
refused('actual observation requires timezone',lambda:call(current='2030-01-01T00:00:00'),'timezone-required')
assert POLICY['execution_identity']==IDENTITY and DEADLINES['Session']=='2030-01-01T00:01:00Z'
cases.append({'case':'pure decision does not extend deadlines or alter inputs','result':'PASS'})
report={'schema_version':'lab-T03-margin-pure-controls/v1-candidate','authority_effect':'none',
        'result':'PASS-synthetic-arithmetic-only','cases':cases,'case_count':len(cases),
        'synthetic_values_are_real_empirical_thresholds':False,'production_callback_or_clock_replaced':False,
        'actual_native_Service_Session_lease_or_runtime_constructor':False,'task_complete':False}
(HERE/'pure-controls-result.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
print(json.dumps({'result':report['result'],'case_count':len(cases),'result_sha256':hashlib.sha256((HERE/'pure-controls-result.json').read_bytes()).hexdigest()}))
