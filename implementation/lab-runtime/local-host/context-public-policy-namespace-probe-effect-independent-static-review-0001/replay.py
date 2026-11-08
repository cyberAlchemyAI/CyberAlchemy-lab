"""Rehash frozen wrapper, replay effect-denying tests and read-only host preflight."""
import hashlib,json,subprocess,time,os
from pathlib import Path
HERE=Path(__file__).resolve().parent
CANDIDATE=HERE.parent/'context-public-policy-namespace-probe-effect-0001'
PYTHON='/usr/bin/python3.14'
EXPECTED='49041c108e1d056ba6450fa9b2223db5af375940e641304a098a0547adb2034a'
def sha(raw):return hashlib.sha256(raw).hexdigest()
freeze=json.loads((CANDIDATE/'freeze.json').read_bytes())
assert sha((CANDIDATE/'freeze.json').read_bytes())==EXPECTED
for name,pin in {**freeze['members'],**freeze['evidence_sha256']}.items():
    assert sha((CANDIDATE/name).read_bytes())==pin,name
assert not os.path.lexists(freeze['attempt']) and not os.path.lexists(freeze['observation'])
rows=[]
cases=[('normal',['-I','-B']),('optimized',['-I','-B','-O']),
       ('isolated',['-I','-B','-S']),('isolated-optimized',['-I','-B','-S','-O'])]
for name,flags in cases+[('preflight',['-I','-B','-S'])]:
    target=(CANDIDATE/('run_tests.py' if name!='preflight' else 'wrapper.py'))
    argv=[PYTHON,*flags,str(target)]+(['--preflight'] if name=='preflight' else [])
    start=time.time_ns()
    result=subprocess.run(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,timeout=45,check=False)
    end=time.time_ns()
    (HERE/(name+'.stdout')).write_bytes(result.stdout)
    (HERE/(name+'.stderr')).write_bytes(result.stderr)
    assert result.returncode==0,(name,result.stderr[-2000:])
    if name!='preflight':
        record=json.loads(result.stdout)
        assert record['tests']==7 and record['passed'] is True and record['docker_effect']=='UNRUN'
    else:
        record=json.loads(result.stdout)
        assert record['effect']=='NOT_RUN' and record['host']['attempt_absent'] is True
        assert record['host']['name_absent'] is True and len(record['mounts'])==6
        assert result.stderr==b''
    rows.append({'case':name,'argv':argv,'os_exit':result.returncode,
                 'start_ns':start,'end_ns':end,'stdout_sha256':sha(result.stdout),
                 'stderr_sha256':sha(result.stderr)})
assert not os.path.lexists(freeze['attempt']) and not os.path.lexists(freeze['observation'])
for name,pin in {**freeze['members'],**freeze['evidence_sha256']}.items():
    assert sha((CANDIDATE/name).read_bytes())==pin,name
(HERE/'execution.json').write_text(json.dumps({'schema':'context-public-policy-wrapper-independent-static-execution/v1',
    'candidate_freeze_sha256':EXPECTED,'docker_effect':'UNRUN','private_inputs':'UNOPENED',
    'attempt_absent_after':True,'observation_absent_after':True,'runs':rows},indent=2,sort_keys=True)+'\n')
print(json.dumps({'runs':len(rows),'all_exit_zero':True,'effect':'NOT_RUN',
                  'attempts_absent':True},sort_keys=True))
