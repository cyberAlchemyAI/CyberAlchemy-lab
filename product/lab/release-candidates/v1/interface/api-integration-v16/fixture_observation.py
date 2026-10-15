"""Preserve public fixture replies and exact durable journal bytes before assertions.

This observes only a test-owned temporary workspace. It never inspects RAM,
private signing keys, frame locals or Session notes, and changes no production
source, authentication, permission, clock or lifecycle callback.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import uuid

HERE=Path(__file__).resolve().parent


def record(test_ref,service,raw,reply):
    root=Path(service.vault.root)
    assert root.is_relative_to(Path('/tmp')) and root.resolve()==root
    assert root.stat().st_uid==os.getuid() and root.stat().st_mode&0o777==0o700
    journal=root/'journal';snapshots=[]
    for path in sorted(journal.glob('*.json')):
        assert path.is_file() and not path.is_symlink()
        data=path.read_bytes();assert len(data)<=1024*1024
        # Journal metadata is the persisted operation state, not Session RAM.
        snapshots.append({'path':path.relative_to(root).as_posix(),
                          'sha256':hashlib.sha256(data).hexdigest(),
                          'base64_original_bytes':base64.b64encode(data).decode()})
    value={'schema_version':'lab-test-owned-public-call-observation/v1-candidate',
           'test_ref':test_ref,'request_sha256':hashlib.sha256(raw).hexdigest(),
           'actual_public_reply':reply,
           'owned_workspace_ref':service.vault.manifest['workspace_ref'],
           'durable_journal_snapshots':snapshots,'Session_RAM_inspected':False,
           'private_key_inspected':False,'fixture_cleanup_proven':False,
           'task_complete':False,'authority_effect':'none','actual_owner_outcome':None}
    output=HERE/'receipts'/'per-call-observations';output.mkdir(parents=True,mode=0o700,exist_ok=True)
    path=output/(uuid.uuid4().hex+'.json')
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w') as stream:
        json.dump(value,stream,sort_keys=True,indent=2);stream.write('\n')
        stream.flush();os.fsync(stream.fileno())
