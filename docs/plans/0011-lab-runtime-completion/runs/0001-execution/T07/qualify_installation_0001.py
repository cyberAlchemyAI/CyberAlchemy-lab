"""Cold retained staging of the separately pinned partial T07 component."""
from pathlib import Path
import hashlib
import json
import sys
import time

ROOT=Path(__file__).resolve().parents[6]
RUN=Path(__file__).resolve().parent
COMPONENT=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v1-completion-0001'
MANIFEST_SHA='ad4b0e91db27ea16cc6481230942e128839d9ec1b16b2105be07525c3513f2a3'
SELECTION_SHA='ec9e0c2d10e4aca3e54e9a1538c1a6f583d7d4e2059da750c0c8418cd1b61cae'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def guard():
    raw=(COMPONENT/'source-manifest.json').read_bytes()
    assert sha(raw)==MANIFEST_SHA
    for row in json.loads(raw)['files']:
        p=ROOT/row['path'];assert not any(x.is_symlink() for x in [p,*p.parents])
        assert sha(p.read_bytes())==row['sha256'] and p.stat().st_size==row['size_bytes']
    assert sha((RUN/'dependency-selection.json').read_bytes())==SELECTION_SHA

guard();sys.path.insert(0,str(COMPONENT));import install
owned=json.loads((RUN/'owned-installation-selection-0001.json').read_bytes())
start=time.monotonic()
result=install.install(RUN/'dependency-selection.json',SELECTION_SHA,owned['parent'],(owned['device'],owned['inode']),owned['name'])
guard()
report={'schema_version':'lab-task-local-dependency-install-qualification/v1-candidate','component_manifest_sha256':MANIFEST_SHA,'selection_sha256':SELECTION_SHA,'elapsed_seconds':time.monotonic()-start,'result':result,'T07_complete':False,'goal_complete':False,'authority_effect':'none'}
with (RUN/'installation-qualification-0001.json').open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps({'result':result['result'],'installed_files':len(result['installed_files']),'native_history_replay_proven':False,'runtime_start_proven':False}))
