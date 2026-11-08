"""Effect-disabled, held-file one-shot signed-scope controller with fixture tests.

The future Docker Reader effect is deliberately absent. A separate checked-
buffer loader is an inert candidate, not a reviewed signed-open release.
No method here opens a real view.
"""
from __future__ import annotations

from contextlib import contextmanager
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import types

LOCAL = Path('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host')
ADAPTER_DIR = LOCAL/'context-successor-local-issuer-adapter-0002'
ADAPTER_FREEZE_SHA = '6a2cf9c2fe3c90aacb13b2537668fb37c9dbd94401129b175627ceeea19d7e26'
ADAPTER_CODE_SHA = 'f4500ccdfa92b60818c58a1d50072d7985d84b4811e22c922c5eb399e0860466'
ADAPTER_REVIEW = LOCAL/'context-successor-local-issuer-independent-review-0002/review.json'
ADAPTER_REVIEW_SHA = 'fab52d2b65e742c86234a1e6770322f7111c863b83457d283f5afa56044a4c4e'
ADAPTER_REVIEW_MD = LOCAL/'context-successor-local-issuer-independent-review-0002/REVIEW.md'
ADAPTER_REVIEW_MD_SHA = 'a54cff54c9cb90358818c1d52260068743fa48031b59361c996638a69e5dd259'
STAGE_REVIEW = LOCAL/'context-successor-stage-independent-effect-review-0001/review.json'
STAGE_REVIEW_SHA = 'f47f20cb46f23caff219b2ab496e168147e3854ead89fd894b31dfe409f9ab0a'
STAGE_REVIEW_MD = LOCAL/'context-successor-stage-independent-effect-review-0001/REVIEW.md'
STAGE_REVIEW_MD_SHA = '584b4867107caf82cdb87214e6936d61f9f3aa948eecf596a331f55044cf9d0c'
FAMILY = Path('/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001')
ATTEMPT = FAMILY/'context-signed-scope-attempt-0002.claim'
ATTESTATION = FAMILY/'context-signed-scope-attestation-0002.json'
EFFECT_ENABLED = False
DIR_FLAGS = os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC
WRITE_FLAGS = os.O_RDWR|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC


class Refused(RuntimeError): pass
class Unknown(Refused):
    def __init__(self, cause, attempt):
        self.cause = cause
        self.attempt = str(attempt)
        self.retry_allowed = False
        self.status = 'UNKNOWN_CONSUMED_NO_RETRY'
        super().__init__('signed-scope attempt consumed; outcome unknown; never retry')

def need(ok, code):
    if not ok: raise Refused(code)

def sha(raw): return hashlib.sha256(raw).hexdigest()
def wire(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()

def checked_adapter():
    raw = (ADAPTER_DIR/'freeze.json').read_bytes()
    need(sha(raw) == ADAPTER_FREEZE_SHA,'ADAPTER_FREEZE_DRIFT')
    freeze = json.loads(raw)
    need(freeze['effect_enabled'] is False and
         freeze['members']['adapter.py'] == ADAPTER_CODE_SHA and
         freeze['auth_row'] == 'UNMINTED_UNSELECTED','ADAPTER_FREEZE_SCOPE')
    for name,digest in freeze['members'].items():
        need(sha((ADAPTER_DIR/name).read_bytes()) == digest,'ADAPTER_MEMBER_DRIFT')
    review_raw = ADAPTER_REVIEW.read_bytes()
    need(sha(review_raw) == ADAPTER_REVIEW_SHA and
         sha(ADAPTER_REVIEW_MD.read_bytes()) == ADAPTER_REVIEW_MD_SHA and
         json.loads(review_raw)['verdict'] == 'PASS_BOUNDED_INERT_MODEL_ONLY',
         'ADAPTER_REVIEW_DRIFT')
    code = (ADAPTER_DIR/'adapter.py').read_bytes()
    need(sha(code) == ADAPTER_CODE_SHA,'ADAPTER_CODE_DRIFT')
    module = types.ModuleType('checked_local_issuer_adapter_0002')
    module.__file__ = str(ADAPTER_DIR/'adapter.py')
    exec(compile(code,module.__file__,'exec'),module.__dict__)
    need(module.EFFECT_ENABLED is False,'ADAPTER_EFFECT_DRIFT')
    return module

def preflight(now=None):
    now = dt.datetime.now(dt.timezone.utc) if now is None else now
    need(type(now) is dt.datetime and now.tzinfo is not None and
         now.utcoffset() == dt.timedelta(),'CURRENT_UTC_REQUIRED')
    adapter = checked_adapter()
    selected = adapter.select(now)
    raw = STAGE_REVIEW.read_bytes()
    need(sha(raw) == STAGE_REVIEW_SHA and
         sha(STAGE_REVIEW_MD.read_bytes()) == STAGE_REVIEW_MD_SHA,
         'STAGE_EFFECT_REVIEW_DRIFT')
    review = json.loads(raw)
    need(review['verdict'] == 'PASS_BOUNDED_DISPOSABLE_CONTEXT_STAGE_ONLY' and
         review['external_os_exit'] == 0 and review['unknown_absent'] is True and
         review['files_verified'] == 1570 and review['directories_verified'] == 1021 and
         review['auth'] == 'UNMINTED_UNSELECTED' and
         review['attempt'] == str(FAMILY/'context-attempt') and
         review['source_period_current_at_audit'] is True and
         review['disposable_selected_archive_hashed'] is True and
         review['protected_historical_archive_opened'] is False,
         'STAGE_EFFECT_SCOPE')
    stage_root = Path(selected['stage_root'])
    need(stage_root == FAMILY/'context-attempt/root' and
         not os.path.lexists(ATTEMPT) and
         not os.path.lexists(ATTESTATION),'SEPARATE_ATTEMPT_CONSUMED')
    for path in (FAMILY,stage_root):
        st = os.stat(path,follow_symlinks=False)
        need(stat.S_ISDIR(st.st_mode) and st.st_uid == os.getuid() and
             st.st_gid == os.getgid() and stat.S_IMODE(st.st_mode) == 0o700,
             'CURRENT_STAGE_ROOT_CUSTODY')
    need(selected['reader']['method'] == 'SelectedReader.open_signed' and
         selected['reader']['sha256'] == adapter.READER_CODE_SHA and
         selected['reader']['manifest_sha256'] == adapter.READER_MANIFEST_SHA and
         selected['source_period_sha256'] == adapter.checked_baseline().SOURCE_PERIOD_SHA,
         'ORIGINAL_READER_SELECTION')
    return {'schema':'context-signed-scope-controller-preflight/v1',
            'status':'EFFECT_DISABLED_DOCKER_SIGNED_SCOPE_RELEASE_PENDING',
            'effect':'NOT_RUN','attempt':str(ATTEMPT),
            'stage_root':str(stage_root),
            'stage_review_sha256':STAGE_REVIEW_SHA,
            'adapter_review_sha256':ADAPTER_REVIEW_SHA,
            'source_period_end':selected['source_period_end'],
            'expected_scope':selected['scope_expected'],
            'signed_scope':'NOT_OPENED','grant':'UNISSUED',
            'auth':'UNMINTED_UNSELECTED','selected':selected}


def run_real_once(*_args,**_kwargs):
    raise Refused('EFFECT_DISABLED_DOCKER_SIGNED_SCOPE_RELEASE_UNIMPLEMENTED')


def _write_held(parentfd, name, raw):
    need(type(raw) is bytes and 0 < len(raw) <= 8192 and
         '/' not in name and name not in ('','.','..'),'BOUNDED_RECORD')
    fd = os.open(name,WRITE_FLAGS,0o600,dir_fd=parentfd)
    primary = None
    try:
        st = os.fstat(fd)
        need(stat.S_ISREG(st.st_mode) and st.st_nlink == 1 and
             st.st_uid == os.getuid() and st.st_gid == os.getgid() and
             stat.S_IMODE(st.st_mode) == 0o600,'RECORD_CUSTODY')
        view = memoryview(raw)
        while view:
            n = os.write(fd,view)
            need(n > 0,'RECORD_SHORT_WRITE')
            view = view[n:]
        os.fsync(fd)
        os.lseek(fd,0,os.SEEK_SET)
        need(os.read(fd,len(raw)+1) == raw,'RECORD_READBACK')
        named = os.stat(name,dir_fd=parentfd,follow_symlinks=False)
        need((named.st_dev,named.st_ino,named.st_mode,named.st_uid,named.st_gid,
              named.st_nlink,named.st_size) ==
             (os.fstat(fd).st_dev,os.fstat(fd).st_ino,os.fstat(fd).st_mode,
              os.fstat(fd).st_uid,os.fstat(fd).st_gid,
              os.fstat(fd).st_nlink,os.fstat(fd).st_size),
             'RECORD_REPLACED')
    except BaseException as exc:
        primary = exc
        raise
    finally:
        try: os.close(fd)
        except BaseException as exc:
            if primary is None: raise
            primary.add_note('secondary record close uncertainty')
    os.fsync(parentfd)
    return sha(raw)


def _write_claim_held(parentfd, claimfd, name, raw):
    """Durably mark the exact inode returned by O_EXCL; keep it held."""
    need(type(raw) is bytes and 0 < len(raw) <= 8192,'BOUNDED_CLAIM_MARKER')
    before=os.fstat(claimfd)
    need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and
         before.st_uid==os.getuid() and before.st_gid==os.getgid() and
         stat.S_IMODE(before.st_mode)==0o600 and before.st_size==0,
         'CLAIM_DESCRIPTOR_CUSTODY')
    remain=memoryview(raw)
    while remain:
        count=os.write(claimfd,remain)
        need(count>0,'CLAIM_SHORT_WRITE')
        remain=remain[count:]
    os.fsync(claimfd)
    os.lseek(claimfd,0,os.SEEK_SET)
    need(os.read(claimfd,len(raw)+1)==raw,'CLAIM_READBACK')
    named=os.stat(name,dir_fd=parentfd,follow_symlinks=False)
    held=os.fstat(claimfd)
    need((named.st_dev,named.st_ino,named.st_mode,named.st_uid,named.st_gid,
          named.st_nlink,named.st_size)==
         (held.st_dev,held.st_ino,held.st_mode,held.st_uid,held.st_gid,
          held.st_nlink,held.st_size),'CLAIM_REPLACED')
    os.fsync(parentfd)
    return sha(raw)


class SyntheticSelectedReader:
    """Only fixture Reader accepted here. It cannot open the actual archive."""
    def __init__(self, selection, *, bad_scope=False, fail_final=False,
                 fail_close=False, wrong_basis=False):
        self.selection = selection
        self.bad_scope = bad_scope
        self.fail_final = fail_final
        self.fail_close = fail_close
        self.wrong_basis = wrong_basis
        self.calls = []
    def guard(self):
        self.calls.append('reader_guard')
        return True
    @contextmanager
    def open_signed(self, source_pin, package_pin):
        need(source_pin == self.selection['reader']['source_manifest_sha256'] and
             package_pin == self.selection['reader']['source_package_manifest_sha256'],
             'SYNTHETIC_READER_PIN')
        self.calls.append('open_signed')
        scope = 'scope:wrong' if self.bad_scope else self.selection['scope_expected']
        basis = {'manifest_sha256':package_pin,
                 'source_manifest_sha256':source_pin,
                 'adapter_source_sha256':self.selection['reader']['manifest_sha256']}
        if self.wrong_basis: basis['adapter_source_sha256'] = '0'*64
        reader = self
        class Signed:
            view = types.SimpleNamespace(data={'config':{'scope_ref':scope}})
            sources = types.SimpleNamespace(scope_ref=scope)
            selected = {'candidate_selection_basis':basis}
            def guard(self):
                reader.calls.append('signed_guard')
                if reader.fail_final and reader.calls.count('signed_guard') >= 3:
                    raise Refused('SYNTHETIC_FINAL_GUARD')
                return True
        signed = Signed()
        signed.guard()
        try:
            yield signed
            signed.guard()
            self.guard()
        finally:
            self.calls.append('close')
            if self.fail_close: raise OSError('SYNTHETIC_CLOSE_UNCERTAIN')


def _selection_key(value):
    keys = ('source_period_sha256','source_effect_review_sha256',
            'reader_effect_review_sha256','mapper_effect_review_sha256',
            'scope_expected','reader','stage_root')
    return {key:value[key] for key in keys}


def run_fixture_once(parent, selection, *, reader=None, at_close=None,
                     fault=None):
    """Real disposable filesystem claim; signed view and time are synthetic."""
    parent = Path(parent)
    need(parent.parent == Path('/tmp') and
         parent.name.startswith('fixture-signed-scope-'),
         'DISPOSABLE_FIXTURE_PARENT_ONLY')
    need(selection['effect'] == 'NOT_RUN' and
         selection['scope_actual'] == 'NOT_OPENED' and
         selection['auth']['issued_sha256'] == 'UNMINTED_UNSELECTED',
         'INERT_SELECTION_ONLY')
    need(_selection_key(preflight(dt.datetime.fromisoformat(
             selection['auth']['not_before']))['selected']) == _selection_key(selection),
         'INITIAL_PUBLIC_SELECTION_CHANGED')
    if reader is None: reader = SyntheticSelectedReader(selection)
    need(type(reader) is SyntheticSelectedReader,'SYNTHETIC_READER_ONLY')
    close_time = dt.datetime(2026,10,20,18,30,tzinfo=dt.timezone.utc) \
        if at_close is None else at_close
    attempt = parent/'attempt.claim'
    attestation_path = parent/'signed-scope.attestation.json'
    parentfd = os.open(parent,DIR_FLAGS)
    claimfd = None
    claimed = False
    claim_started = False
    try:
        st = os.fstat(parentfd)
        need(st.st_uid == os.getuid() and st.st_gid == os.getgid() and
             stat.S_IMODE(st.st_mode) == 0o700,'FIXTURE_PARENT_CUSTODY')
        need(not os.path.lexists(attempt) and
             not os.path.lexists(attestation_path),'ATTEMPT_CONSUMED_NO_RETRY')
        claim_started = True
        claimfd = os.open('attempt.claim',WRITE_FLAGS,0o600,dir_fd=parentfd)
        claimed = True
        os.fsync(parentfd)
        if fault == 'after_claim': raise OSError('SYNTHETIC_POSTCLAIM')
        child = os.fstat(claimfd)
        named = os.stat('attempt.claim',dir_fd=parentfd,follow_symlinks=False)
        need(stat.S_ISREG(child.st_mode) and
             (child.st_dev,child.st_ino,child.st_mode,child.st_uid,child.st_gid) ==
             (named.st_dev,named.st_ino,named.st_mode,named.st_uid,named.st_gid) and
             stat.S_IMODE(child.st_mode) == 0o600,'ATTEMPT_CLAIM_IDENTITY')
        marker_sha = None
        def attached():
            held = os.fstat(claimfd)
            named_now = os.stat('attempt.claim',dir_fd=parentfd,follow_symlinks=False)
            parent_now = os.stat(parent,follow_symlinks=False)
            parent_held = os.fstat(parentfd)
            need((held.st_dev,held.st_ino,held.st_mode,held.st_uid,held.st_gid) ==
                 (named_now.st_dev,named_now.st_ino,named_now.st_mode,
                  named_now.st_uid,named_now.st_gid) and
                 (parent_now.st_dev,parent_now.st_ino,parent_now.st_mode,
                  parent_now.st_uid,parent_now.st_gid) ==
                 (parent_held.st_dev,parent_held.st_ino,parent_held.st_mode,
                  parent_held.st_uid,parent_held.st_gid),
                 'ATTEMPT_OR_PARENT_DETACHED')
            if marker_sha is not None:
                need(0<held.st_size<=8192,'HELD_CLAIM_MARKER_SIZE')
                held_raw=os.pread(claimfd,held.st_size+1,0)
                need(0<len(held_raw)<=8192 and sha(held_raw)==marker_sha,
                     'HELD_CLAIM_MARKER_DRIFT')
        attached()
        os.fsync(parentfd)
        marker = wire({'schema':'context-signed-scope-consumed/v2-held-file',
                       'status':'CONSUMED_UNKNOWN_UNTIL_EXTERNAL_REVIEW',
                       'attempt':'fixture-only',
                       'attempt_dev':child.st_dev,'attempt_ino':child.st_ino,
                       'reader_manifest_sha256':selection['reader']['manifest_sha256'],
                       'stage_review_sha256':STAGE_REVIEW_SHA,
                       'retry_allowed':False})
        attached()
        marker_sha = _write_claim_held(parentfd,claimfd,'attempt.claim',marker)
        attached()
        if fault == 'after_marker': raise OSError('SYNTHETIC_POSTMARKER')
        need(type(close_time) is dt.datetime and close_time.tzinfo is not None and
             close_time.utcoffset() == dt.timedelta() and
             dt.datetime.fromisoformat(selection['source_period_start']) <= close_time <
             dt.datetime.fromisoformat(selection['source_period_end']),
             'SOURCE_PERIOD_EXPIRED')
        need(_selection_key(preflight(close_time)['selected']) == _selection_key(selection),
             'HELD_PUBLIC_SELECTION_CHANGED')
        basis = {'manifest_sha256':selection['reader']['source_package_manifest_sha256'],
                 'source_manifest_sha256':selection['reader']['source_manifest_sha256'],
                 'adapter_source_sha256':selection['reader']['manifest_sha256']}
        attached()
        with reader.open_signed(selection['reader']['source_manifest_sha256'],
                                selection['reader']['source_package_manifest_sha256']) as signed:
            need(signed.guard() is True and
                 signed.view.data['config']['scope_ref'] == selection['scope_expected'] and
                 signed.sources.scope_ref == selection['scope_expected'] and
                 signed.selected['candidate_selection_basis'] == basis,
                 'HELD_SIGNED_SCOPE_OR_BASIS')
            if fault == 'inside_signed': raise OSError('SYNTHETIC_HELD_FAILURE')
        need(reader.calls.count('signed_guard') >= 2 and
             'reader_guard' in reader.calls and reader.calls[-1] == 'close',
             'FINAL_READER_GUARD_CLOSE')
        attached()
        need(_selection_key(preflight(close_time)['selected']) == _selection_key(selection),
             'POSTCLOSE_PUBLIC_SELECTION_CHANGED')
        if fault == 'after_close': raise OSError('SYNTHETIC_POSTCLOSE')
        attestation = wire({
            'schema':'context-disposable-signed-scope-attestation/v1',
            'status':'PROVISIONAL_EXTERNAL_OS_AND_INDEPENDENT_REVIEW_REQUIRED',
            'claim_ceiling':selection['claim_ceiling'],
            'authority_effect':'none','actual_owner_outcome':None,
            'scope_ref':selection['scope_expected'],
            'reader_code_sha256':selection['reader']['sha256'],
            'reader_manifest_sha256':selection['reader']['manifest_sha256'],
            'reader_selected_basis':basis,
            'source_period_sha256':selection['source_period_sha256'],
            'source_effect_review_sha256':selection['source_effect_review_sha256'],
            'reader_effect_review_sha256':selection['reader_effect_review_sha256'],
            'mapper_effect_review_sha256':selection['mapper_effect_review_sha256'],
            'stage_effect_review_sha256':STAGE_REVIEW_SHA,
            'source_period_end':selection['source_period_end'],
            'closed_at':close_time.isoformat(),
            'attempt':'fixture-only','attempt_dev':child.st_dev,'attempt_ino':child.st_ino,
            'consumed_marker_sha256':marker_sha,
            'first_guard':True,'final_guard':True,'reader_guard':True,
            'close_ok':True,'retry_allowed':False})
        need(len(attestation) <= 8192,'ATTESTATION_BOUNDS')
        if fault == 'attestation_publication':
            raise OSError('SYNTHETIC_PUBLICATION_UNCERTAIN')
        attached()
        digest = _write_held(parentfd,'signed-scope.attestation.json',attestation)
        attached()
        need(not os.path.lexists(ATTEMPT),'REAL_ATTEMPT_MUST_REMAIN_ABSENT')
        return {'schema':'context-signed-scope-fixture-result/v1',
                'status':'PROVISIONAL_FIXTURE_SIGNED_SCOPE_EXTERNAL_OS_REVIEW_REQUIRED',
                'attempt':str(attempt),'marker_sha256':marker_sha,
                'attestation_sha256':digest,'retry_allowed':False,
                'real_effect':'NOT_RUN'}
    except BaseException as exc:
        if claimed or (claim_started and os.path.lexists(attempt)):
            raise Unknown(exc,attempt) from exc
        raise
    finally:
        errors=[]
        for fd in (claimfd,parentfd):
            if fd is not None:
                try:os.close(fd)
                except BaseException as exc:errors.append(exc)
        if errors:
            if sys.exception() is None:
                raise Unknown(ExceptionGroup('fixture directory close uncertain',errors),
                              attempt) if claimed else ExceptionGroup(
                                  'fixture directory close uncertain',errors)
            sys.exception().add_note('secondary directory close uncertainty')


def issue_auth_or_grant(*_args,**_kwargs):
    raise Refused('AUTH_AND_GRANTS_DISABLED')
def create_private_policy(*_args,**_kwargs):
    raise Refused('PRIVATE_POLICY_DISABLED')
def launch_docker(*_args,**_kwargs):
    raise Refused('DOCKER_DISABLED')

if __name__ == '__main__':
    if sys.argv[1:] != ['--preflight']:
        raise SystemExit('expected --preflight')
    value = preflight()
    del value['selected']
    print(json.dumps(value,sort_keys=True,separators=(',',':')))
