"""Actual selected processes at verified-byte child execution boundary."""
import hashlib,json,os,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[7];HERE=ROOT/'product/lab/release-candidates/v1/interface/composite-operator-v1-completion-0001/revision-0003';INSTALL=HERE.parents[1]/'runtime-dependencies-v2-completion-0001/installations/0004';RUN=Path(__file__).parent
sys.path[:0]=[str(INSTALL/'deps'),str(HERE)]
import checks,composite as C
from control import compact,parse,sha
command=[str(INSTALL/'lib/abi/ld-linux-x86-64.so.2'),'--inhibit-cache','--library-path',str(INSTALL/'lib/abi'),str(INSTALL/'bin/python'),'-I','-X','utf8','-B','-S']
manifest=(HERE/'source-manifest.json').read_bytes();files={str(p):p.read_bytes() for p in HERE.iterdir() if p.is_file()};case_list=[];selection={'selection':{'path':C.DEPENDENCY_SELECTION,'sha256':C.DEPENDENCY_SHA},'installation':str(INSTALL)}
assert C.dependency_guard(selection)==1010
for mode in ['leaf','parent']:
    root,config,_,_=checks.fixture();path=root/'operator-config.json';checks.put(path,compact(config));observation=RUN/('bootstrap-'+mode+'-observation-0001.json')
    proc=subprocess.run(command+[str(RUN/'bootstrap_observer.py'),str(path),sha(compact(config)),mode,str(observation)],input=b'',capture_output=True,env={'PATH':'/usr/bin:/bin','LC_ALL':'C'})
    assert proc.returncode==2 and proc.stderr==b'' and b'UNAPPROVED_SDK_FILE_EXECUTED' not in proc.stdout and b'challenge' not in proc.stdout and not list(root.rglob('*.lock'))
    messages=[parse(raw) for raw in proc.stdout.splitlines()];assert messages and all(m['code']=='selected-bootstrap-refused' for m in messages)
    value=json.loads(observation.read_bytes());assert value['boundary_reached'] and value['child_returncode']==2 and value['launcher_returncode']==2
    assert files=={str(p):p.read_bytes() for p in HERE.iterdir() if p.is_file()}
    case_list.append({'case':'actual '+mode+' replacement after parent capture before child loader refuses before challenges/effects','result':'PASS','child_returncode':2,'launcher_returncode':2,'unapproved_code_executed':False,'owned_root':str(root),'observation_sha256':sha(observation.read_bytes())})
# Positive selection: capsule bootstrap reaches genuine missing-policy preflight.
root,config,_,_=checks.fixture();missing=root/'governance/operator-policy.json';missing.rename(root/'governance-policy-retained.json');path=root/'operator-config.json';checks.put(path,compact(config))
proc=subprocess.run(command+[str(HERE/'launch.py'),'--launcher-source-sha256',sha(manifest),'--config',str(path),'--config-sha256',sha(compact(config))],input=b'',capture_output=True,env={'PATH':'/usr/bin:/bin','LC_ALL':'C'})
assert proc.returncode==2 and proc.stderr==b'' and parse(proc.stdout)['code']=='startup-or-channel-refused' and b'challenge' not in proc.stdout and not list(root.rglob('*.lock'))
case_list.append({'case':'actual capsule-loaded SDK reaches original preflight and refuses missing Governance credentials','result':'PASS','launcher_returncode':2,'owned_root':str(root)})
assert C.dependency_guard(selection)==1010 and files=={str(p):p.read_bytes() for p in HERE.iterdir() if p.is_file()}
value={'schema_version':'lab-T06-bootstrap-boundary-proof/v3-candidate','result':'PASS','cases':case_list,'source_manifest_sha256':sha(manifest),'complete_dependencies_entry_exit':1010,'actual_full34_construction':False,'original_branch_callbacks_substituted':False,'authority_effect':'none','task_complete':False}
out=RUN/'bootstrap-evidence-0001.json';checks.put(out,json.dumps(value,indent=2,sort_keys=True).encode()+b'\n');print(json.dumps({'result':'PASS','cases':len(case_list),'report':str(out)}),flush=True)
