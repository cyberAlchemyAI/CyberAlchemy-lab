"""Exact public source/installed-byte checks before selected helper execution."""
import hashlib,json,os,stat,subprocess
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
COMP=ROOT/'product/lab/release-candidates/v1/interface/composite-operator-v1-completion-0001'
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06'
INSTALL=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
MANIFEST_SHA='d04253291d7b6850b00e7be4f5f2996d1f8c6bdfa1f6d84bbaffc7e3508be7fc'
SELECT=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json'
SELECT_SHA='2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'
def sha(raw):return hashlib.sha256(raw).hexdigest()
manifest_raw=(COMP/'source-manifest.json').read_bytes();assert sha(manifest_raw)==MANIFEST_SHA;manifest=json.loads(manifest_raw)
selection_raw=SELECT.read_bytes();assert sha(selection_raw)==SELECT_SHA;selected=json.loads(selection_raw)
expected={r['destination']:{'sha256':r['sha256'],'size_bytes':r['size_bytes'],'mode':0o755 if r['kind'] in {'interpreter','native-executable'} else 0o644} for r in selected['inputs']};expected.update(selected['wheel_members']);expected['lib/abi/ld-linux-x86-64.so.2']['mode']=0o755
assert len(expected)==1010 and len(selected['inputs'])==720 and len(selected['original_bindings'])==5
def guard():
    assert (COMP/'source-manifest.json').read_bytes()==manifest_raw and SELECT.read_bytes()==selection_raw
    for row in manifest['files']:
        p=ROOT/row['path'];assert p.is_file() and not any(q.is_symlink() for q in [p,*p.parents]);assert p.stat().st_size==row['size_bytes'] and sha(p.read_bytes())==row['sha256']
    for name,row in expected.items():
        p=INSTALL/name;assert not any(q.is_symlink() for q in [p,*p.parents]);s=p.stat();assert s.st_uid==os.getuid() and stat.S_IMODE(s.st_mode)==row['mode'] and s.st_size==row['size_bytes'] and sha(p.read_bytes())==row['sha256']
guard()
code='import sys;sys.path[:0]=['+repr(str(INSTALL/'deps'))+','+repr(str(COMP))+'];from checks import checks;checks("focused-evidence-0002.json")'
command=[str(INSTALL/'lib/abi/ld-linux-x86-64.so.2'),'--inhibit-cache','--library-path',str(INSTALL/'lib/abi'),str(INSTALL/'bin/python'),'-I','-X','utf8','-B','-S','-c',code]
result=subprocess.run(command,env={'PATH':'/usr/bin:/bin','LC_ALL':'C'},capture_output=True,text=True);guard();assert result.returncode==0,result.stderr
evidence=json.loads((RUN/'focused-evidence-0002.json').read_bytes());controlled=Path(evidence['owned_roots'][1]);config=controlled/'config.json';config_sha=sha(json.dumps(json.loads(config.read_bytes()),sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode())
launcher=[os.sys.executable,str(COMP/'launch.py'),'--launcher-source-sha256',MANIFEST_SHA,'--config',str(config),'--config-sha256',config_sha]
launched=subprocess.run(launcher,input=b'',env={'PATH':'/usr/bin:/bin','LC_ALL':'C'},capture_output=True);guard()
assert launched.returncode==2 and json.loads(launched.stdout)['code']=='startup-or-channel-refused' and b'challenge' not in launched.stdout
record={'schema_version':'lab-T06-guarded-focused-qualification/v1-candidate','result':'PASS','source_manifest_sha256':MANIFEST_SHA,'source_files':len(manifest['files']),'T07_selection_sha256':SELECT_SHA,'installed_files':len(expected),'guards':'before selected runtime/helper import and after both processes','command':command,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'maintained_launcher_command':launcher,'maintained_launcher_missing_credentials_returncode':launched.returncode,'maintained_launcher_output':json.loads(launched.stdout),'actual_full34_construction':False,'API17_guard_PASS_claimed':False,'actual_independent_three_branch_authentication_tested':False,'genuine_issuer_authority_proven':False,'task_complete':False,'authority_effect':'none'}
p=RUN/'qualification-0001.json';assert not p.exists();p.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n');print(json.dumps({'result':'PASS','source_files':len(manifest['files']),'installed_files':len(expected),'helper_checks':len(evidence['cases']),'maintained_launcher_missing_credentials_returncode':launched.returncode}))
