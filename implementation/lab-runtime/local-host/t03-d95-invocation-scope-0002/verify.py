"""Cold exact-byte closure check for the measured pure-scope API successor."""
from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
OLD=BASE/'api-integration-v33-t03-one-lesson-native-v4-preclaim-diagnostic-0003'
NEW=BASE/'api-integration-v33-t03-one-lesson-native-v4-invocation-scope-0002'
MANIFEST='4e752f33caba970a1b5a169df5ae050e95b08aadd069e33b9561fe894ceaadad'
PROFILE='df87a7f569ae301ba7389d8909916231a6a3913b434a49e7dd54e3f16b1596fb'

def sha(path):
    if not path.is_file() or path.is_symlink():raise ValueError('selected file absent or linked: '+str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check():
    if sha(NEW/'source-manifest.json')!=MANIFEST or sha(NEW/'contract-profile.json')!=PROFILE:
        raise ValueError('selected manifest/profile changed')
    source=json.loads((NEW/'source-manifest.json').read_bytes())
    profile=json.loads((NEW/'contract-profile.json').read_bytes())
    receipt=json.loads((NEW/'rebind-receipt.json').read_bytes())
    if len(source['files'])!=211 or len(profile['files'])!=len(json.loads((OLD/'contract-profile.json').read_bytes())['files']):
        raise ValueError('selected closure count differs')
    for row in source['files']:
        if sha(ROOT/row['path'])!=row['sha256']:
            raise ValueError('selected file changed: '+row['path'])
    if source['profile_binding']['sha256']!=PROFILE or receipt['successor_manifest_sha256']!=MANIFEST:
        raise ValueError('source/receipt binding changed')
    old_prefix=OLD.relative_to(ROOT).as_posix()+'/'
    new_prefix=NEW.relative_to(ROOT).as_posix()+'/'
    changed=[]
    for row in source['files']:
        if row['path'].startswith(new_prefix):
            leaf=row['path'][len(new_prefix):]
            if sha(OLD/leaf)!=row['sha256']:
                changed.append(leaf)
    if sorted(changed)!=['contract-profile.json','service.py','t03_lesson_host.py']:
        raise ValueError('selected code delta differs: '+repr(changed))
    guard=importlib.import_module(NEW.name+'.guard')
    guard.verify(MANIFEST)
    schemas=importlib.import_module(NEW.name+'.protocol').Schemas(PROFILE)
    schemas.guard()
    return {'manifest_sha256':MANIFEST,'profile_sha256':PROFILE,'selected_rows':211,
            'changed_own_files':sorted(changed),'selected_guard':'passed','schema_guard':'passed',
            'authority_effect':'none','lesson_applied':False,'lesson_assessed':False}

if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
