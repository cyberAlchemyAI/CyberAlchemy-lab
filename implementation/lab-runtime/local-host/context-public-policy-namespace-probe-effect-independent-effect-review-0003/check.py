"""Independent read-only reconciliation of the consumed public policy probe."""
import hashlib
import json
import re
import stat
from pathlib import Path

LOCAL=Path('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host')
STATE=Path('/home/vlad_/.local/state/cyberalchemy-lab')
OBS=Path('/home/vlad_/.local/state/cyberalchemy-lab-observations')
ATTEMPT=STATE/'context-public-policy-probe-20261020-0003'
INNER=OBS/'context-public-policy-probe-20261020-0003'
OUTER=OBS/'context-public-policy-probe-effect-20261020-0003'
HOST=OBS/'context-public-policy-probe-wrapper-release-20261020-0003'
CID='d5a25a17e1a5c47fe501614b7a8610dd8c084c070936620900d5943b2d526b9a'
NAME='cal-context-public-policy-probe-20261020-0003'
def raw(path): return path.read_bytes()
def sha(body): return hashlib.sha256(body).hexdigest()
def data(path): return json.loads(raw(path))
def exact_json(body):
    value=json.loads(body)
    assert body==(json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode()
    return value

freeze_path=LOCAL/'context-public-policy-namespace-probe-effect-0003/freeze.json'
assert sha(raw(freeze_path))=='fbcf33ed639157d3f4571471c5b13b70f0a0c0ffe721e707b48bf7bceaceea44'
freeze=data(freeze_path)
for name,digest in freeze['members'].items():
    assert sha(raw(freeze_path.parent/name))==digest
for directory in ('context-public-policy-namespace-probe-0003',
                  'context-public-policy-namespace-probe-effect-0002'):
    source_dir=LOCAL/directory
    source_freeze=data(source_dir/'freeze.json')
    for name,digest in source_freeze['members'].items():
        assert sha(raw(source_dir/name))==digest
for path,digest in (
 (LOCAL/'context-public-policy-namespace-probe-0003/freeze.json',freeze['release_freeze_sha256']),
 (LOCAL/'context-public-policy-namespace-probe-effect-0002/freeze.json',freeze['source_freeze_sha256']),
 (LOCAL/'context-public-policy-namespace-probe-independent-static-review-0003/review.json',freeze['release_review_sha256']),
 (LOCAL/'context-public-policy-namespace-probe-effect-independent-static-review-0002/review.json',freeze['source_review_sha256']),
 (LOCAL/'context-public-policy-namespace-probe-effect-independent-static-review-0003/review.json','07a01486b9cb8bb28318be6d40ff8e705f1d34803a58d9d00689c785e269a2f1')):
    assert sha(raw(path))==digest
assert data(LOCAL/'context-public-policy-namespace-probe-independent-static-review-0003/review.json')['verdict']=='PASS_BOUNDED_PUBLIC_ONLY_STATIC'
assert data(LOCAL/'context-public-policy-namespace-probe-effect-independent-static-review-0002/review.json')['verdict']=='PASS_BOUNDED_EFFECT_DISABLED_WRAPPER_ONLY'
assert data(LOCAL/'context-public-policy-namespace-probe-effect-independent-static-review-0003/review.json')['verdict']=='PASS_BOUNDED_PUBLIC_ONLY_ONE_SHOT_STATIC'

host=data(HOST/'result.json')
assert host['status']=='OS_OBSERVED' and type(host['exit_code']) is int and host['exit_code']==0
assert host['error'] is None and host['retry_allowed'] is False
assert data(HOST/'intent.json')['command']==[
    '/usr/bin/python3.14','-I','-B','-S',
    str(LOCAL/'context-public-policy-namespace-probe-effect-0003/wrapper.py'),
    '--observe-reviewed-one-shot','--review-sha256',
    '07a01486b9cb8bb28318be6d40ff8e705f1d34803a58d9d00689c785e269a2f1']
assert len(raw(HOST/'stdout.bin'))==host['stdout']['bytes']==567
assert sha(raw(HOST/'stdout.bin'))==host['stdout']['sha256']=='3a9c567871d9457ebf4589feaeba5c5e074985193c30585f068180df279c7ba7'
assert raw(HOST/'stderr.bin')==b'' and host['stderr']['bytes']==0
assert sha(raw(HOST/'stderr.bin'))==host['stderr']['sha256']
assert data(HOST/'intent.json')['review_sha256']=='07a01486b9cb8bb28318be6d40ff8e705f1d34803a58d9d00689c785e269a2f1'
outer_summary=exact_json(raw(HOST/'stdout.bin'))
outer_record=data(OUTER/'observation.json')
assert outer_record['status']=='PROVISIONAL_UNTIL_POSTCLOSE_OS_REVIEW'
assert outer_record['candidate']==outer_summary and outer_record['retry_allowed'] is False
assert outer_record['error_class'] is None and outer_record['error_detail'] is None
assert sha(raw(OUTER/'stdout'))==outer_summary['outer_stdout_sha256']
assert raw(OUTER/'stderr')==b'' and sha(b'')==outer_summary['outer_stderr_sha256']
assert outer_summary['outer_os_exit']==0 and outer_summary['retry_allowed'] is False
assert outer_summary['name']==NAME and sha(raw(OUTER/'stdout'))==outer_summary['inner_candidate_sha256']
assert sha(raw(INNER/'observation.json'))==outer_summary['inner_record_sha256']
assert data(OUTER/'consumed.json')['retry_allowed'] is False
assert data(INNER/'consumed.json')['retry_allowed'] is False
assert data(ATTEMPT/'consumed.json')['retry_allowed'] is False
assert data(OUTER/'intent.json')['review_sha256']==data(HOST/'intent.json')['review_sha256']

inner_candidate=exact_json(raw(OUTER/'stdout'))
inner_record=data(INNER/'observation.json')
assert inner_record['status']=='PROVISIONAL_MATCH' and inner_record['candidate']==inner_candidate
assert inner_record['error_class'] is None and inner_record['error_detail'] is None
assert raw(INNER/'stderr')==b''
inner_release_summary=exact_json(raw(INNER/'stdout'))
assert inner_release_summary['status']=='PROVISIONAL_EXTERNAL_OS_REVIEW_REQUIRED'
assert inner_release_summary['retry_allowed'] is False
terminal=data(ATTEMPT/'terminal.json')
assert sha(raw(ATTEMPT/'terminal.json'))==inner_candidate['terminal_sha256']
assert inner_release_summary['terminal_sha256']==inner_candidate['terminal_sha256']
assert terminal['status']=='PROVISIONAL_EXTERNAL_OS_REVIEW_REQUIRED'
assert terminal['cid']==CID and terminal['name']==NAME
assert type(terminal['child_os_exit']) is int and terminal['child_os_exit']==0
assert terminal['erofs_errno']==30 and terminal['policy_erofs_errno']==30
assert terminal['six_read_only_mounts'] is True
assert terminal['nested_writable_or_private_mount'] is False
assert terminal['post_ack_visibility'] is True
assert terminal['cid_absent'] is True and terminal['name_absent'] is True
assert terminal['retry_allowed'] is False
assert terminal['parent_peer']==[terminal['child_pid'],1000,1000]
assert sha(raw(ATTEMPT/'child-mountinfo.txt'))==terminal['mountinfo_sha256']==inner_candidate['child_mountinfo_sha256']
assert sha(raw(ATTEMPT/'stage/probe/public-only/packages/0001/request.json'))==terminal['request_sha256']==inner_candidate['request_sha256']
assert sha(raw(ATTEMPT/'policy-public/permission.json'))==terminal['policy_sha256']==inner_candidate['public_policy_sha256']

targets=('/workspace','/control','/runner','/cache-disabled',
         '/attempt/input/lab-context-native-reader','/context-policy')
rows=[]
for line in raw(ATTEMPT/'child-mountinfo.txt').decode('ascii').splitlines():
    before,_sep,_after=line.partition(' - ')
    parts=before.split()
    path=re.sub(r'\\([0-7]{3})',lambda match:chr(int(match.group(1),8)),parts[4])
    rows.append((path,parts[5].split(',')))
for target in targets:
    selected=[options for path,options in rows if path==target]
    assert len(selected)==1 and 'ro' in selected[0] and 'rw' not in selected[0]
    assert not any(path.startswith(target+'/') for path,_ in rows)
assert inner_candidate['six_child_read_only_mounts'] is True
assert inner_candidate['no_nested_writable_or_private_mount'] is True
assert inner_candidate['post_ack_parent_writer_visibility'] is True
assert inner_candidate['container_cid_absent'] is True
assert inner_candidate['container_name_absent'] is True
assert inner_candidate['policy_authority_qualification'] is False
for directory in (HOST,OUTER,INNER,ATTEMPT):
    st=directory.stat()
    assert stat.S_ISDIR(st.st_mode) and st.st_uid==1000 and stat.S_IMODE(st.st_mode)==0o700
for directory in (HOST,OUTER,INNER):
    for path in directory.iterdir():
        assert path.is_file() and path.stat().st_uid==1000 and stat.S_IMODE(path.stat().st_mode)==0o600
assert stat.S_IMODE((ATTEMPT/'policy-public/permission.json').stat().st_mode)==0o600
assert stat.S_IMODE((ATTEMPT/'stage/probe/public-only/packages/0001/request.json').stat().st_mode)==0o444
daemon=data(Path(__file__).resolve().parent/'daemon.json')
assert daemon['cid']['exit_code']==1 and daemon['name']['exit_code']==0
assert raw(Path(__file__).resolve().parent/'cid.stdout')==b'[]\n'
assert raw(Path(__file__).resolve().parent/'cid.stderr')==f'Error response from daemon: No such container: {CID}\n'.encode()
assert raw(Path(__file__).resolve().parent/'name.stdout')==b''
assert raw(Path(__file__).resolve().parent/'name.stderr')==b''
print(json.dumps({'status':'PASS_BOUNDED_PUBLIC_ONLY_EFFECT','mounts':6,
                  'outer_exit':0,'child_exit':0,'cid_absent':True,'name_absent':True,
                  'erofs_errno':30,'policy_erofs_errno':30,'no_retry':True},sort_keys=True))
