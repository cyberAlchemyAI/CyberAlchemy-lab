"""Independent inert inode-custody counterexample for frozen signed controller."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import types
from unittest import mock
sys.path.insert(0,'/usr/lib/python3/dist-packages')

LOCAL = Path('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host')
CANDIDATE = LOCAL/'context-successor-signed-scope-controller-0001'
FREEZE_SHA = '24cee28817f8517356a73e1d2c8918753a9b6478c79cb35b5bcc862816db6fb9'
NOW = dt.datetime(2026,10,20,18,30,tzinfo=dt.timezone.utc)

def need(ok,code):
    if not ok: raise AssertionError(code)
def sha(raw): return hashlib.sha256(raw).hexdigest()
def audit(event,args):
    if event == 'open' and args and str(args[0]).endswith('branch.snapshot'):
        raise RuntimeError('PRIVATE_ARCHIVE_BODY_DISABLED')
    if event.startswith(('subprocess.','socket.')) or event in ('os.system','os.fork','os.exec'):
        raise RuntimeError('EFFECT_DISABLED')
sys.addaudithook(audit)

freeze_raw=(CANDIDATE/'freeze.json').read_bytes()
need(sha(freeze_raw)==FREEZE_SHA,'FROZEN_CANDIDATE_DRIFT')
freeze=json.loads(freeze_raw)
for name,pin in freeze['members'].items():
    need(sha((CANDIDATE/name).read_bytes())==pin,'MEMBER_DRIFT_'+name)
need(freeze['effect_enabled'] is False and freeze['checked_real_reader_loader']=='UNIMPLEMENTED_REAL_EFFECT_REFUSED',
     'REAL_EFFECT_SCOPE')
need(not os.path.lexists(freeze['real_attempt']),'REAL_ATTEMPT_PRESENT')
module=types.ModuleType('checked_signed_controller')
module.__file__=str(CANDIDATE/'controller.py')
exec(compile((CANDIDATE/'controller.py').read_bytes(),module.__file__,'exec'),module.__dict__)
selected=module.preflight(NOW)['selected']
need(selected['reader']['sha256']==freeze['reader_code_sha256'] and
     selected['reader']['manifest_sha256']==freeze['reader_manifest_sha256'],
     'READER_PINS')
for effect in (module.run_real_once,module.issue_auth_or_grant,
               module.create_private_policy,module.launch_docker):
    try: effect()
    except module.Refused: pass
    else: raise AssertionError('REAL_EFFECT_REACHABLE')

with tempfile.TemporaryDirectory(prefix='fixture-signed-scope-',dir='/tmp') as parent:
    original_open=os.open
    swapped=False
    reader=module.SyntheticSelectedReader(selected)
    def intercept(name,flags,*args,**kwargs):
        global swapped
        if name=='attempt' and kwargs.get('dir_fd') is not None and not swapped:
            swapped=True
            Path(parent,'attempt').rename(Path(parent,'detached-original'))
            Path(parent,'attempt').mkdir(mode=0o700)
        return original_open(name,flags,*args,**kwargs)
    with mock.patch.object(module.os,'open',side_effect=intercept):
        result=module.run_fixture_once(parent,selected,reader=reader)
    need(swapped,'SWAP_NOT_REACHED')
    need(result['status']=='PROVISIONAL_FIXTURE_SIGNED_SCOPE_EXTERNAL_OS_REVIEW_REQUIRED',
         'RACE_DID_NOT_SUCCEED')
    need(list(Path(parent,'detached-original').iterdir())==[],
         'ORIGINAL_CLAIM_NOT_EMPTY')
    foreign={p.name for p in Path(parent,'attempt').iterdir()}
    need(foreign=={'consumed.json','signed-scope.attestation.json'},
         'REPLACEMENT_DID_NOT_RECEIVE_BOTH_RECORDS')
    need(reader.calls[0]=='open_signed' and reader.calls[-1]=='close',
         'SYNTHETIC_READER_NOT_INVOKED')
    record=json.loads(Path(parent,'attempt/signed-scope.attestation.json').read_bytes())
    need(record['attempt_dev']==os.stat(Path(parent,'attempt')).st_dev and
         record['attempt_ino']==os.stat(Path(parent,'attempt')).st_ino,
         'ATTESTATION_DID_NOT_ADOPT_REPLACEMENT')

need(not os.path.lexists(freeze['real_attempt']),'REAL_ATTEMPT_AFTER_TEST')
print(json.dumps({'schema':'context-signed-controller-independent-causal/v1',
                  'candidate_freeze_sha256':FREEZE_SHA,
                  'finding':'NEW_ATTEMPT_INODE_REPLACED_BEFORE_FIRST_OPEN_AND_ADOPTED',
                  'fixture_success_on_foreign_inode':True,
                  'original_claim_empty':True,
                  'foreign_received':['consumed.json','signed-scope.attestation.json'],
                  'synthetic_reader_opened':True,
                  'real_effect':'NOT_RUN','private_archive_body':'UNOPENED'},sort_keys=True))
