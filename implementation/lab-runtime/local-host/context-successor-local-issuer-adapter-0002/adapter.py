"""Inert local signed-scope/fixture-issuer selection; no authority effects."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import types

HERE = Path(__file__).resolve().parent
LOCAL = HERE.parent
FAMILY = Path('/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001')
BASELINE = LOCAL/'context-successor-authority-selection-0001'
BASELINE_CODE = BASELINE/'authority_selection.py'
BASELINE_FREEZE = BASELINE/'freeze.json'
BASELINE_REVIEW = LOCAL/'context-successor-authority-selection-independent-static-review-0001/REVIEW.md'
FEASIBILITY = LOCAL/'CONTEXT-LOCAL-AUTHORITY-FEASIBILITY-READONLY-AUDIT-0001.md'
BASELINE_CODE_SHA = '208f248560b206c91552b6cecb8721476507d96ac046c30a13dadd98c930e40c'
BASELINE_FREEZE_SHA = '36f301cb2f2359815eb2474b10a4d33124bfe894e222330d4a2e7f8a54ce3345'
BASELINE_REVIEW_SHA = '2b35db66dab54f4f9e132751a570a8d3f9ccb2a7aee6a7550d42e6a010a8b824'
FEASIBILITY_SHA = '2b0c46b13f78cf45e4aa640a73338d7623a0fd50c165ba3a9eedf7c79f0cc884'
READER_ROLE = 'product/lab/release-candidates/v1/interface/docker-reader-20261020-0002'
READER_ROOT = FAMILY/'reader-stage-attempt/root'/READER_ROLE
READER_CODE = READER_ROOT/'reader.py'
READER_MANIFEST = READER_ROOT/'source-manifest.json'
READER_CODE_SHA = 'f93a1f218238c05b18a7c355f9bc1363bbf42d2b1d442d03e191e121f8e9c9b9'
READER_MANIFEST_SHA = '048ef6c1f54387fc6e593f38b29723cb06f84649f12e9c75a0340d389b0f5756'
SOURCE_ROLE = 'product/lab/release-candidates/v1/interface/docker-source-20261020-0002'
SOURCE_ROOT = FAMILY/'source-attempt/root'/SOURCE_ROLE
SOURCE_APPROVAL = SOURCE_ROOT/'packages/0001/approval.json'
SOURCE_APPROVAL_SHA = 'abb88dff37930e54ff454ea64a0cf94740346944f6c83fbb57e9fb13400c8177'
ISSUER_REF = 'issuer:local-disposable-vlad-context-development-20261020-0001'
ISSUER_UID = 1000
ISSUER_GID = 1000
CLAIM = 'Local disposable development episode only; no protected Source8 issuer grant or owner outcome.'
EFFECT_ENABLED = False


class Refused(ValueError):
    pass


def need(ok, code):
    if not ok: raise Refused(code)


def sha(raw): return hashlib.sha256(raw).hexdigest()


def checked_baseline():
    # The predecessor handles all current Source/Reader/Mapper evidence joins.
    for path,digest in ((BASELINE_FREEZE,BASELINE_FREEZE_SHA),
                        (BASELINE_REVIEW,BASELINE_REVIEW_SHA),
                        (FEASIBILITY,FEASIBILITY_SHA)):
        raw = read_public(path,digest)
        if path == BASELINE_FREEZE:
            freeze = json.loads(raw)
            need(freeze['effect_enabled'] is False and
                 freeze['actual_bound_rows'] == 1570 and
                 freeze['auth_row'] == 'UNMINTED_UNSELECTED' and
                 freeze['members']['authority_selection.py'] == BASELINE_CODE_SHA,
                 'BASELINE_FREEZE_SCOPE')
        elif path == BASELINE_REVIEW:
            need(b'**Verdict: PASS_BOUNDED_INERT_SELECTION_ONLY.**' in raw and
                 BASELINE_FREEZE_SHA.encode() in raw,'BASELINE_REVIEW_SCOPE')
    raw = read_public(BASELINE_CODE,BASELINE_CODE_SHA)
    module = types.ModuleType('reviewed_actual_authority_selection_0001')
    module.__file__ = str(BASELINE_CODE)
    exec(compile(raw,str(BASELINE_CODE),'exec'),module.__dict__)
    need(module.EFFECT_ENABLED is False and module.CLAIM == CLAIM,
         'BASELINE_CODE_SCOPE')
    return module


def read_public(path, digest, limit=2*1024*1024):
    fd = os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
             before.st_uid == os.getuid() and
             not(before.st_mode & 0o022) and
             0 < before.st_size <= limit,'PUBLIC_PIN_CUSTODY')
        raw = os.read(fd,before.st_size+1)
        after = os.fstat(fd)
        need(len(raw) == before.st_size and
             (before.st_dev,before.st_ino,before.st_mode,before.st_size,
              before.st_mtime_ns,before.st_ctime_ns) ==
             (after.st_dev,after.st_ino,after.st_mode,after.st_size,
              after.st_mtime_ns,after.st_ctime_ns) and
             sha(raw) == digest,'PUBLIC_PIN_DRIFT')
        return raw
    finally:
        os.close(fd)


def select(now=None, *, baseline=checked_baseline):
    now = dt.datetime.now(dt.timezone.utc) if now is None else now
    need(type(now) is dt.datetime and now.tzinfo is not None and
         now.utcoffset() == dt.timedelta(),'CURRENT_UTC')
    A = baseline()
    selected = A.current_selection(now)
    stage = selected['stage']
    source = selected['source']
    need(selected['status'] == 'ACTUAL_MAPPER_SELECTED_AUTHORITY_HOLD' and
         selected['effect'] == 'NOT_RUN' and
         stage['bound_file_count'] == 1570 and
         stage['final_count_with_auth'] == 1571 and
         selected['auth_row'] == 'UNMINTED_UNSELECTED' and
         selected['issuer'] == 'UNSELECTED' and
         selected['required_signed_scope']['status'] ==
         'NOT_OPENED_REQUIRES_REVIEWED_READER_SIGNED_VIEW' and
         source['scope_attestation'] == 'NOT_OPENED_SIGNED_SOURCE_VIEW' and
         A.utc(source['period_start']) <= now < A.utc(source['period_end']),
         'BASELINE_UNISSUED_CURRENT')
    manifest_raw = read_public(READER_MANIFEST,READER_MANIFEST_SHA)
    manifest = A.parse(manifest_raw)
    reader_raw = read_public(READER_CODE,READER_CODE_SHA,65536)
    approval = A.parse(read_public(SOURCE_APPROVAL,SOURCE_APPROVAL_SHA,65536))
    rows = [row for row in manifest['files']
            if row['path'] == READER_ROLE+'/reader.py']
    need(len(rows) == 1 and rows[0]['sha256'] == READER_CODE_SHA and
         manifest['producer_source_binding'] ==
         {'path':SOURCE_ROLE+'/source-manifest.json',
          'sha256':source['source_manifest_sha256']} and
         manifest['producer_package_binding'] ==
         {'path':SOURCE_ROLE+'/packages/0001/manifest.json',
          'sha256':source['source_package_manifest_sha256']} and
         manifest['authority_effect'] == 'none' and
         approval['authorized_domain_scope_refs'] == [A.SCOPE] and
         b'def open_signed(self, source_pin, package_pin):' in reader_raw and
         b'with C.open_source(source_pin,package_pin) as cold:' in reader_raw and
         b'                selected.guard()' in reader_raw and
         b'            finally:selected.close()' in reader_raw,
         'SELECTED_ORIGINAL_READER_CONTRACT')
    need(os.getuid() == ISSUER_UID and os.getgid() == ISSUER_GID and
         stage['auth_placeholder']['path'] == A.AUTH_PATH and
         stage['auth_placeholder']['sha256'] == 'UNMINTED_UNSELECTED',
         'LOCAL_FIXTURE_ISSUER_IDENTITY')
    candidate = A.auth_template(selected,now)
    need(candidate['status'] == 'UNTRUSTED_UNISSUED_AUTH_TEMPLATE_ONLY' and
         candidate['signed_scope'] == 'NOT_OPENED' and
         candidate['issuer'] == 'UNSELECTED' and
         candidate['actual_bound_count'] == 1570 and
         candidate['would_be_final_count'] == 1571,
         'UNISSUED_PREIMAGE_ONLY')
    auth = A.parse(candidate['bytes'])
    end = A.utc(auth['expires_at'])
    need(auth['schema_version'] == 'lab-context-development-authorization/v1-candidate' and
         auth['family_ref'] == stage['topology']['context_family_ref'] and
         auth['episode_ref'] == A.PERIOD_REF and
         auth['scope_ref'] == A.SCOPE and
         auth['period_binding']['sha256'] == A.SOURCE_PERIOD_SHA and
         auth['authority_effect'] == 'none' and
         auth['actual_owner_outcome'] is None and
         auth['claim_ceiling'] == CLAIM and
         now < end <= min(now+dt.timedelta(minutes=20),
                          A.utc(source['period_end'])),
         'BOUNDED_LOCAL_AUTH_PREIMAGE')
    return {'schema':'context-local-issuer-selection/v1-inert',
            'status':'LOCAL_FIXTURE_ISSUER_SELECTED_AUTH_UNISSUED',
            'effect':'NOT_RUN','source_period_start':source['period_start'],
            'source_period_end':source['period_end'],
            'source_period_sha256':A.SOURCE_PERIOD_SHA,
            'source_effect_review_sha256':A.SOURCE_REVIEW_SHA,
            'reader_effect_review_sha256':A.READER_REVIEW_SHA,
            'mapper_effect_review_sha256':A.MAPPER_REVIEW_SHA,
            'scope_expected':A.SCOPE,'scope_actual':'NOT_OPENED',
            'reader':{'path':str(READER_CODE),'sha256':READER_CODE_SHA,
                      'manifest_sha256':READER_MANIFEST_SHA,
                      'method':'SelectedReader.open_signed',
                      'source_manifest_sha256':source['source_manifest_sha256'],
                      'source_package_manifest_sha256':source['source_package_manifest_sha256'],
                      'required_close':'FINAL_SIGNED_GUARD_READER_GUARD_CLOSE'},
            'issuer':{'ref':ISSUER_REF,'uid':ISSUER_UID,'gid':ISSUER_GID,
                      'kind':'DISPOSABLE_LOCAL_HOST_ONLY',
                      'protected_source8_grant':False,
                      'selected':'INERT_IDENTITY_ONLY','grant':'UNISSUED'},
            'auth':{'path':A.AUTH_PATH,'mode':'0600','candidate_sha256':candidate['sha256'],
                    'candidate_bytes_status':'UNTRUSTED_UNISSUED',
                    'schema_version':auth['schema_version'],
                    'not_before':auth['not_before'],
                    'expires_at':auth['expires_at'],
                    'issued_sha256':'UNMINTED_UNSELECTED',
                    'final_count_after_issuance':1571},
            'stage_root':stage['topology']['stage_root'],
            'authority_attempt':str(FAMILY/'context-local-authority-attempt-0001'),
            'private_root':stage['topology']['private_root'],
            'claim_ceiling':CLAIM}


ORDER = (
    'RECHECK_ACTUAL_1570_SOURCE_READER_MAPPER_AND_PERIOD',
    'CLAIM_EXCLUSIVE_AUTHORITY_ATTEMPT_ROOT_CONSUMED',
    'DURABLE_AUTHORITY_NO_RETRY_MARKER_BEFORE_PRIVATE_OPEN',
    'OPEN_EXACT_SELECTED_READER_OPEN_SIGNED_ONCE',
    'CHECK_HELD_VIEW_CONFIG_AND_SIGNED_SOURCES_SCOPE',
    'CHECK_PERIOD_AND_SOURCE_READER_MAPPER_PINS_WHILE_HELD',
    'REQUIRE_FINAL_SIGNED_GUARD_READER_GUARD_AND_CLOSE',
    'PUBLISH_DURABLE_EXTERNAL_SIGNED_SCOPE_ATTESTATION_OR_UNKNOWN',
    'SELECT_DISPOSABLE_LOCAL_ISSUER_WITH_NO_PROTECTED_GRANT',
    'CLAIM_EXCLUSIVE_CONTEXT_STAGE_ROOT_CONSUMED',
    'DURABLE_STAGE_NO_RETRY_MARKER_BEFORE_CONTENT',
    'COPY_REHASH_EXACT_1570_ROWS_WITH_PRIVATE_BODY_CUSTODY',
    'RECHECK_PERIOD_AND_BOUND_SIGNED_SCOPE_ATTESTATION_BEFORE_AUTH_WRITE',
    'REQUIRE_PUBLISHED_ATTESTATION_DIGEST_AND_BOTH_ATTEMPT_IDENTITIES',
    'ISSUE_ONE_0600_AUTH_LEAF_EXCLUSIVE_NOFOLLOW',
    'FSYNC_CLOSE_HELD_AUTH_READBACK_AND_EXACT_1571_CLOSURE',
    'PUBLISH_DURABLE_EXTERNAL_LOCAL_ISSUER_RECEIPT',
    'ONLY_THEN_SELECT_SEPARATE_PRIVATE_POLICY_AND_CONTEXT_EFFECT',
)


def protocol(selection):
    need(selection['status'] == 'LOCAL_FIXTURE_ISSUER_SELECTED_AUTH_UNISSUED' and
         selection['scope_actual'] == 'NOT_OPENED' and
         selection['issuer']['grant'] == 'UNISSUED' and
         selection['auth']['issued_sha256'] == 'UNMINTED_UNSELECTED',
         'INERT_SELECTION_ONLY')
    return {'schema':'context-local-issuer-protocol/v1-inert',
            'steps':list(ORDER),'effect':'NOT_RUN',
            'claim_is_consumption':True,
            'premarker_root_exists':'UNKNOWN_CONSUMED_NO_RETRY',
            'failed_signed_close':'UNKNOWN_CONSUMED_NO_RETRY',
            'failed_signed_attestation_publication':'UNKNOWN_CONSUMED_NO_RETRY',
            'failed_auth_close_or_fsync':'UNKNOWN_CONSUMED_NO_RETRY',
            'retry_allowed':False,
            'actual_signed_scope':'NOT_OPENED',
            'actual_auth':'UNMINTED_UNSELECTED',
            'fixture_attestation':'NOT_PUBLISHED'}


class FixtureOneShotModel:
    """Pure fixture transitions; no observation or supplied publication is authority."""
    def __init__(self, selection):
        need(selection['status'] == 'LOCAL_FIXTURE_ISSUER_SELECTED_AUTH_UNISSUED' and
             selection['effect'] == 'NOT_RUN' and
             selection['scope_actual'] == 'NOT_OPENED','FIXTURE_INERT_SELECTION_REQUIRED')
        self.selection = json.loads(json.dumps(selection, sort_keys=True, allow_nan=False))
        self.expected_scope = self.selection['scope_expected']
        self.state = 'NEW'
        self.authority_attempt_identity = None
        self.stage_attempt_identity = None
        self._attestation_raw = None
        self.attestation_sha256 = None

    def claim(self, attempt_identity):
        need(self.state == 'NEW','ATTEMPT_ALREADY_CONSUMED')
        self.state = 'UNKNOWN_CONSUMED'
        need(type(attempt_identity) is str and attempt_identity.startswith('fixture-inode:') and
             len(attempt_identity) <= 128,'AUTHORITY_ATTEMPT_IDENTITY_REQUIRED')
        self.authority_attempt_identity = attempt_identity
        self.state = 'AUTHORITY_MARKER_PENDING'

    def marker(self, durable):
        need(self.state == 'AUTHORITY_MARKER_PENDING','ATTEMPT_NOT_FRESHLY_CLAIMED')
        self.state = 'UNKNOWN_CONSUMED'  # Failure is absorbing, even if retried via marker().
        need(durable is True,'MARKER_UNKNOWN_NO_RETRY')
        self.state = 'MARKED'

    def begin_signed(self):
        need(self.state == 'MARKED','MARKER_REQUIRED_BEFORE_SIGNED_OPEN')
        self.state = 'SIGNED_OPEN_PENDING'

    def observe_signed_fixture(self, *, view_scope, sources_scope,
                               first_guard, final_guard, reader_guard,
                               close_ok, current, selected_basis,
                               period_sha256, source_review_sha256,
                               reader_review_sha256, mapper_review_sha256,
                               now_at_close):
        need(self.state == 'SIGNED_OPEN_PENDING','SIGNED_OPEN_NOT_SELECTED')
        self.state = 'UNKNOWN_CONSUMED'
        selected = self.selection
        expected_basis = {
            'manifest_sha256':selected['reader']['source_package_manifest_sha256'],
            'source_manifest_sha256':selected['reader']['source_manifest_sha256'],
            'adapter_source_sha256':selected['reader']['manifest_sha256']}
        need(type(view_scope) is str and view_scope == self.expected_scope and
             sources_scope == view_scope and selected_basis == expected_basis and
             period_sha256 == selected['source_period_sha256'] and
             source_review_sha256 == selected['source_effect_review_sha256'] and
             reader_review_sha256 == selected['reader_effect_review_sha256'] and
             mapper_review_sha256 == selected['mapper_effect_review_sha256'] and
             type(now_at_close) is dt.datetime and
             now_at_close.tzinfo is not None and
             now_at_close.utcoffset() == dt.timedelta() and
             dt.datetime.fromisoformat(selected['source_period_start']) <=
             now_at_close < dt.datetime.fromisoformat(selected['source_period_end']) and
             first_guard is True and final_guard is True and
             reader_guard is True and close_ok is True and current is True,
             'SIGNED_SCOPE_OR_CLOSE_UNKNOWN_NO_RETRY')
        # The fixture closes once, then emits a canonical candidate for an
        # independent durable publication step. No signed view is reopened.
        attestation = {
            'schema':'context-local-fixture-signed-scope-attestation/v1-inert',
            'authority_attempt':selected['authority_attempt'],
            'authority_attempt_identity':self.authority_attempt_identity,
            'scope_ref':view_scope,
            'selected_basis':expected_basis,
            'source_period_sha256':period_sha256,
            'source_effect_review_sha256':source_review_sha256,
            'reader_effect_review_sha256':reader_review_sha256,
            'mapper_effect_review_sha256':mapper_review_sha256,
            'closed_at':now_at_close.isoformat(),
            'first_guard':True,'final_guard':True,'reader_guard':True,
            'close_ok':True}
        self._attestation_raw = (json.dumps(attestation,sort_keys=True,
                                 separators=(',',':'),allow_nan=False)+'\n').encode()
        self.state = 'SIGNED_CLOSED_ATTESTATION_PENDING'

    def attestation_candidate(self):
        need(self.state == 'SIGNED_CLOSED_ATTESTATION_PENDING',
             'CLOSED_SIGNED_OBSERVATION_REQUIRED')
        return self._attestation_raw

    def publish_attestation_fixture(self, raw, *, durable, published_identity):
        need(self.state == 'SIGNED_CLOSED_ATTESTATION_PENDING',
             'ATTESTATION_PUBLICATION_NOT_PENDING')
        self.state = 'UNKNOWN_CONSUMED'  # A failed first publication cannot resume.
        need(type(raw) is bytes and raw == self._attestation_raw and
             durable is True and
             type(published_identity) is str and
             published_identity == self.authority_attempt_identity,
             'ATTESTATION_PUBLICATION_UNKNOWN_NO_RETRY')
        self.attestation_sha256 = sha(raw)
        self.state = 'ATTESTED_FIXTURE_ONLY'
        return self.attestation_sha256

    def stage_claim(self, stage_identity):
        need(self.state == 'ATTESTED_FIXTURE_ONLY','PUBLISHED_ATTESTATION_REQUIRED')
        self.state = 'UNKNOWN_CONSUMED'
        need(type(stage_identity) is str and stage_identity.startswith('fixture-inode:') and
             len(stage_identity) <= 128 and
             stage_identity != self.authority_attempt_identity,
             'STAGE_ATTEMPT_IDENTITY_REQUIRED')
        self.stage_attempt_identity = stage_identity
        self.state = 'STAGE_MARKER_PENDING'

    def stage_marker(self, durable):
        need(self.state == 'STAGE_MARKER_PENDING','STAGE_NOT_FRESHLY_CLAIMED')
        self.state = 'UNKNOWN_CONSUMED'
        need(durable is True,'STAGE_MARKER_UNKNOWN_NO_RETRY')
        self.state = 'STAGE_MARKED_FIXTURE_ONLY'

    def issuer_ready(self, *, rows, current, issuer_local, scope_rechecked,
                     attestation_sha256, authority_attempt_identity,
                     stage_attempt_identity):
        need(self.state == 'STAGE_MARKED_FIXTURE_ONLY','STAGE_MARKER_REQUIRED')
        self.state = 'UNKNOWN_CONSUMED'
        need(type(rows) is int and rows == 1570 and current is True and
             issuer_local is True and scope_rechecked is True and
             type(attestation_sha256) is str and
             attestation_sha256 == self.attestation_sha256 and
             authority_attempt_identity == self.authority_attempt_identity and
             stage_attempt_identity == self.stage_attempt_identity and
             self._attestation_raw is not None and
             sha(self._attestation_raw) == self.attestation_sha256,
             'AUTH_PREWRITE_UNKNOWN_NO_RETRY')
        self.state = 'AUTH_WRITE_ELIGIBLE_MODEL_ONLY'

    def issue(self):
        raise Refused('EFFECT_DISABLED_NO_ISSUED_AUTH')

    def retry(self):
        raise Refused('CONSUMED_ATTEMPT_NO_RETRY')


def open_actual_signed_scope(*_args,**_kwargs):
    raise Refused('EFFECT_DISABLED_NO_PRIVATE_SIGNED_REOPEN')


def issue_actual_auth_or_grant(*_args,**_kwargs):
    raise Refused('EFFECT_DISABLED_NO_LOCAL_OR_PROTECTED_ISSUANCE')


def create_stage_or_private_policy(*_args,**_kwargs):
    raise Refused('EFFECT_DISABLED_NO_STAGE_KEY_OR_POLICY')


def launch_context(*_args,**_kwargs):
    raise Refused('EFFECT_DISABLED_NO_CONTEXT_DOCKER')


if __name__ == '__main__':
    if sys.argv[1:] != ['--preview']:
        raise SystemExit('expected --preview')
    value = select()
    print(json.dumps({'status':value['status'],'effect':value['effect'],
                      'issuer':value['issuer']['selected'],
                      'grant':value['issuer']['grant'],
                      'signed_scope':value['scope_actual'],
                      'auth':value['auth']['issued_sha256'],
                      'source_period_end':value['source_period_end']},sort_keys=True))
