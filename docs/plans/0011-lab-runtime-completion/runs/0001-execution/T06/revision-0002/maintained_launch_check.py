"""Actual maintained candidate launcher, missing Governance policy refusal."""
import hashlib,json,os,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[7];INTERFACE=ROOT/'product/lab/release-candidates/v1/interface';HERE=INTERFACE/'composite-operator-v1-completion-0001/revision-0002';INSTALL=INTERFACE/'runtime-dependencies-v2-completion-0001/installations/0004'
sys.path[:0]=[str(INSTALL/'deps'),str(HERE)]
import checks
from control import compact,parse,sha
root,config,_,_=checks.fixture();missing=root/'governance/operator-policy.json';missing.rename(root/'governance-policy-retained.json');path=root/'operator-config.json';checks.put(path,compact(config))
manifest=HERE/'source-manifest.json';before=manifest.read_bytes();start=time.time()
cmd=[str(INSTALL/'lib/abi/ld-linux-x86-64.so.2'),'--inhibit-cache','--library-path',str(INSTALL/'lib/abi'),str(INSTALL/'bin/python'),'-I','-X','utf8','-B','-S',str(HERE/'launch.py'),'--launcher-source-sha256',sha(before),'--config',str(path),'--config-sha256',sha(compact(config))]
r=subprocess.run(cmd,input=b'',capture_output=True,env={'PATH':'/usr/bin:/bin','LC_ALL':'C'})
assert r.returncode==2 and r.stderr==b'' and parse(r.stdout)['code']=='startup-or-channel-refused' and b'challenge' not in r.stdout and not list(root.rglob('*.lock')) and manifest.read_bytes()==before
report={'schema_version':'lab-T06-maintained-launch-proof/v2-candidate','result':'PASS','started_at_unix':start,'finished_at_unix':time.time(),'launcher_source_manifest_sha256':sha(before),'launcher_returncode':r.returncode,'actual_selected_launcher':str(HERE/'launch.py'),'owned_root':str(root),'error_code':'startup-or-channel-refused','credentials_missing':'governance original independent policy','challenge_emitted':False,'lock_created':False,'actual_full34_construction':False,'authority_effect':'none','task_complete':False}
out=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/revision-0002/maintained-launch-evidence-0001.json';checks.put(out,json.dumps(report,indent=2,sort_keys=True).encode()+b'\n');print(json.dumps({'result':'PASS','launcher_returncode':r.returncode,'report':str(out)}),flush=True)
