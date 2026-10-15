"""Original public fixture observation, directed only to selected owned output."""
import base64,hashlib,os
from pathlib import Path

def record(output,test_ref,service,raw,reply):
    root=Path(service.vault.root)
    assert root.is_relative_to(Path('/tmp')) and root.resolve()==root
    assert root.stat().st_uid==os.getuid() and root.stat().st_mode&0o777==0o700
    journal=root/'journal';snapshots=[]
    for path in sorted(journal.glob('*.json')):
        assert path.is_file() and not path.is_symlink()
        data=path.read_bytes();assert len(data)<=1024*1024
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
    return output.observe(value)
