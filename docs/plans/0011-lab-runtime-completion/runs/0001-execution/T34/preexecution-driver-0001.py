"""Trusted orchestration: verify selected public code/installation before import."""
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess

ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
COMP=ROOT/'product/lab/release-candidates/v1/interface/operational-provisioning-v1-completion-0001'
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T34'
INSTALL=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
MANIFEST_SHA='0d1c60d1b9a3d5b7e28a7baae838fd712887ba7fdd855c88800cf446ae6d1923'
PREVIOUS_QUALIFICATION_SHA='4d987becf62c490945d66c9a30922062e1242ab68cee06495a91e214d261b031'
def sha(raw):return hashlib.sha256(raw).hexdigest()
manifest_raw=(COMP/'source-manifest-0002.json').read_bytes();assert sha(manifest_raw)==MANIFEST_SHA
manifest=json.loads(manifest_raw)
prior_raw=(RUN/'qualification-0002.json').read_bytes();assert sha(prior_raw)==PREVIOUS_QUALIFICATION_SHA
prior=json.loads(prior_raw);assert prior['T07_selection_sha256']=='2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'
expected=prior['installation_exit'];assert expected==prior['installation_entry'] and len(expected)==1010
def guard():
    for row in manifest['files']:
        p=ROOT/row['path'];assert not any(q.is_symlink() for q in [p,*p.parents]);assert p.stat().st_size==row['size_bytes'] and sha(p.read_bytes())==row['sha256']
    for name,row in expected.items():
        p=INSTALL/name;assert not any(q.is_symlink() for q in [p,*p.parents]);s=p.stat();assert s.st_uid==os.getuid() and stat.S_IMODE(s.st_mode)==row['mode'] and s.st_size==row['size_bytes'] and sha(p.read_bytes())==row['sha256']
guard()
code='import sys;sys.path[:0]=['+repr(str(INSTALL/'deps'))+','+repr(str(COMP))+'];from qualify import main;main('+repr(MANIFEST_SHA)+',"focused-evidence-0004.json","source-manifest-0002.json","qualification-0003.json")'
command=[str(INSTALL/'lib/abi/ld-linux-x86-64.so.2'),'--inhibit-cache','--library-path',str(INSTALL/'lib/abi'),str(INSTALL/'bin/python'),'-I','-X','utf8','-B','-S','-c',code]
result=subprocess.run(command,env={'PATH':'/usr/bin:/bin','LC_ALL':'C'},capture_output=True,text=True)
guard()
record={'schema_version':'lab-T34-preexecution-guard/v1-candidate','source_manifest_sha256':MANIFEST_SHA,'prior_qualification_sha256':PREVIOUS_QUALIFICATION_SHA,'source_files':len(manifest['files']),'selected_installed_files':len(expected),'guards':'before selected interpreter/code import and after process completion','command':command,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'authority_effect':'none','task_complete':False}
assert not (RUN/'preexecution-guards-0001.json').exists()
(RUN/'preexecution-guards-0001.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
print(json.dumps({'returncode':result.returncode,'guards':'PASS','report':str(RUN/'preexecution-guards-0001.json')}))
assert result.returncode==0
