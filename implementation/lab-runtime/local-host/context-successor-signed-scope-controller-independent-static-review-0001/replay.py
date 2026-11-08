"""Freeze-checked inert replay for signed-scope controller review."""
import hashlib,json,os,subprocess,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
CANDIDATE=HERE.parent/'context-successor-signed-scope-controller-0001'
PYTHON='/usr/bin/python3.14'
EXPECTED='24cee28817f8517356a73e1d2c8918753a9b6478c79cb35b5bcc862816db6fb9'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def need(ok,code):
    if not ok:raise RuntimeError(code)
freeze=json.loads((CANDIDATE/'freeze.json').read_bytes())
need(sha((CANDIDATE/'freeze.json').read_bytes())==EXPECTED,'FREEZE_DRIFT')
for name,pin in freeze['members'].items():
    need(sha((CANDIDATE/name).read_bytes())==pin,'MEMBER_DRIFT_'+name)
need(not os.path.lexists(freeze['real_attempt']),'REAL_ATTEMPT_EXISTS')
rows=[]
cases=[('normal',[PYTHON,'-B',str(CANDIDATE/'run_tests.py')]),
       ('optimized',[PYTHON,'-B','-O',str(CANDIDATE/'run_tests.py')]),
       ('preflight',[PYTHON,'-B',str(CANDIDATE/'controller.py'),'--preflight']),
       ('causal-normal',[PYTHON,'-I','-B','-S',str(HERE/'check.py')]),
       ('causal-optimized',[PYTHON,'-I','-B','-S','-O',str(HERE/'check.py')])]
for name,argv in cases:
    start=time.time_ns()
    result=subprocess.run(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,timeout=45,check=False)
    end=time.time_ns()
    (HERE/(name+'.stdout')).write_bytes(result.stdout)
    (HERE/(name+'.stderr')).write_bytes(result.stderr)
    need(result.returncode==0,'REPLAY_FAILED_'+name)
    value=json.loads(result.stdout)
    if name in ('normal','optimized'):
        need(value['tests']==10 and value['passed'] is True and
             value['real_effect']=='NOT_RUN','AUTHOR_TEST_CONTRACT_'+name)
    elif name=='preflight':
        need(value['status']=='EFFECT_DISABLED_READER_LOADER_PENDING' and
             value['signed_scope']=='NOT_OPENED' and value['auth']=='UNMINTED_UNSELECTED' and
             result.stderr==b'','PREFLIGHT_SCOPE')
    else:
        need(value['fixture_success_on_foreign_inode'] is True and
             value['original_claim_empty'] is True,'CAUSAL_COUNTEREXAMPLE_'+name)
    rows.append({'case':name,'argv':argv,'start_ns':start,'end_ns':end,
                 'os_exit':result.returncode,'stdout_sha256':sha(result.stdout),
                 'stderr_sha256':sha(result.stderr)})
need(not os.path.lexists(freeze['real_attempt']),'REAL_ATTEMPT_AFTER_REPLAY')
for name,pin in freeze['members'].items():
    need(sha((CANDIDATE/name).read_bytes())==pin,'POST_MEMBER_DRIFT_'+name)
(HERE/'execution.json').write_text(json.dumps({
    'schema':'context-signed-scope-controller-independent-static-execution/v1',
    'candidate_freeze_sha256':EXPECTED,'real_effect':'NOT_RUN',
    'private_archive_body':'UNOPENED','real_attempt_absent_after':True,
    'runs':rows},indent=2,sort_keys=True)+'\n')
print(json.dumps({'runs':len(rows),'all_exit_zero':True,'real_effect':'NOT_RUN',
                  'causal_foreign_success_reproduced_normal_optimized':True},sort_keys=True))
