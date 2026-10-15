"""Immutable isolated replay of authored tests with one fixture-loader correction."""
import hashlib, json, os, stat
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
P=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T31/output-integration-preparation-0005'
OUT=Path(__file__).parent
DEST=OUT/'inputs'
assert not DEST.exists()
DEST.mkdir(mode=0o700)
changed=[];rows=[]
before="C=load('workflow_output_contracts',POST/'workflow_output_contracts.py');M=load('workflow_output_material',POST/'workflow_output_material.py')"
after="C=load('workflow_output_contracts',POST/'workflow_output_contracts.py');load('workflow_output_validation',POST/'workflow_output_validation.py');M=load('workflow_output_material',POST/'workflow_output_material.py')"
for source in sorted(P.rglob('*')):
    assert not source.is_symlink()
    if not source.is_file():continue
    relative=source.relative_to(P)
    assert '__pycache__'not in relative.parts
    raw=source.read_bytes();new=raw
    if relative.as_posix()=='scope_controls.py':
        assert raw.decode().count(before)==1
        new=raw.decode().replace(before,after).encode()
        changed.append(relative.as_posix())
    if relative.as_posix()=='pure/protocol.py':
        old="HERE=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T31/output-integration-preparation-0005/postimages/product/lab/release-candidates/v1/interface/api-integration-v17'"
        assert new.decode().count(old)==1
        new=new.decode().replace(old,"HERE=Path(__file__).absolute().parent.parent/'postimages/product/lab/release-candidates/v1/interface/api-integration-v17'").encode()
        changed.append(relative.as_posix())
    target=DEST/relative;target.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_CLOEXEC|os.O_NOFOLLOW,stat.S_IMODE(source.stat().st_mode))
    try:
        with os.fdopen(fd,'wb',closefd=False)as f:f.write(new);f.flush();os.fsync(fd)
    finally:os.close(fd)
    rows.append({'path':str(target.relative_to(ROOT)),'sha256':hashlib.sha256(new).hexdigest(),'size_bytes':len(new),
                 'original_binding':{'path':str(source.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest()},
                 'changed':new!=raw})
assert changed==['pure/protocol.py','scope_controls.py']
with (OUT/'replay-inputs.json').open('x')as f:json.dump({'authority_effect':'none','files':rows,'changed_owned_test_files':changed,
'production_postimage_bytes_changed':False,'original_failure_preserved':True,'no_original_runtime_function_or_callback_patched':True},f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps({'result':'STAGED-inert-test-only-replay','files':len(rows),'changed':changed,'production_changes':False},sort_keys=True))

