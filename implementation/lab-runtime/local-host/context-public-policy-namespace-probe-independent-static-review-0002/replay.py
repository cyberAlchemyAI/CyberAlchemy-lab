import pathlib,hashlib,json,subprocess,time,sys,types
L=pathlib.Path('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host'); C=L/'context-public-policy-namespace-probe-0002'; E=pathlib.Path(__file__).parent
sha=lambda b:hashlib.sha256(b).hexdigest()
expected='6acbf36dea4997ea9a2815eacb171d50505036ea694b584defee5c451104807d'
raw=(C/'freeze.json').read_bytes(); assert sha(raw)==expected
members=json.loads(raw)['members']
def check():
 for n,h in members.items(): assert sha((C/n).read_bytes())==h,n
 for p,h in json.loads((C/'test-selection-0001.json').read_bytes()).items(): assert sha(pathlib.Path(p).read_bytes())==h,p
check(); runs=[]
def run(label,argv):
 start=time.time_ns(); p=subprocess.run(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=45)
 for stream in ('stdout','stderr'): (E/(label+'.'+stream)).write_bytes(getattr(p,stream))
 runs.append(dict(label=label,argv=argv,start_ns=start,end_ns=time.time_ns(),os_exit=p.returncode,stdout_sha256=sha(p.stdout),stderr_sha256=sha(p.stderr)))
 return p
py='/usr/bin/python3.14'
assert sha(pathlib.Path(py).read_bytes())=='52e0a13e60a981d8c4b6478be2ba5176f69da07948a056bf49cf6f077e30cb41'
for label,flags in [('normal',[]),('optimized',['-O'])]:
 p=run(label,[py,'-I','-B','-S',*flags,str(C/'run_tests.py'),'test-selection-0001.json']); assert p.returncode==0
m=types.ModuleType('reviewed_observer');m.__file__=str(C/'observer.py');exec(compile((C/'observer.py').read_bytes(),m.__file__,'exec'),m.__dict__)
p=run('checked-buffer-preflight',m.checked_child_argv('--preflight'));assert p.returncode==0 and p.stderr==b''
value=json.loads(p.stdout);assert value['host']['name_absent'] and value['host']['attempt_absent']
for label,flags in [('independent-normal',[]),('independent-optimized',['-O'])]:
 p=run(label,[py,'-I','-B',*flags,str(E/'independent.py')]);assert p.returncode==0
check()
absence={str(p):not p.exists() and not p.is_symlink() for p in (m.OBSERVATION,m.R.ATTEMPT)};assert all(absence.values())
(E/'execution.json').write_text(json.dumps(dict(candidate_freeze_sha256=expected,members_verified=len(members),runs=runs,roots_absent=absence,effect='UNRUN',private_archive='UNOPENED'),indent=2)+'\n')
print(json.dumps({'runs':[(r['label'],r['os_exit']) for r in runs],'members':len(members)}))
