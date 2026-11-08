"""Exact reviewed-family one-shot stage; real effect callable but not run here."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import stat
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOCAL = HERE.parent
REPO = Path('/home/vlad_/projects/CyberAlchemy-lab')
STAGE5 = LOCAL / 'context-stage-effect-0005'
STAGE5_CODE_SHA = 'fe5c4109e3c23cddf0c99c602f56cf014ddce053a14e71deb0a69e766c0544eb'
STAGE5_FREEZE_SHA = 'eef7bc55738be2dd5c7d493d19961592b5dce314a5004f4efb842f9a0029b659'
STAGE5_PROFILE_SHA = '8bc35686b0febeab0306b2eb51a9bbd2270d1e9274fe53385ae3e45300993d20'
STAGE5_REVIEW_SHA = '8a7b596ed09ab46f498187e7fd09557bd3d460601898a794104c0e1617ffe987'
SELECTION_SHA = '6721210d076da6462f904b2836a9e3ff5853be92f395a05ee2b141b517e078bf'
RELEASE_SELECTION_SHA = 'c686db8fd070a422cc92a82fb219049bbd1e922a59a4388134ce7fc8e996059c'
RELEASE1_FREEZE_SHA = '172d28c67d5be389081bfb25d723df15ff7929989bc5b1ceff46b171b009fc0f'
RELEASE1_REVIEW_SHA = 'a00559f767fac5229be712491d8881b6816f6a87b6f83856dfb1f1b4ca927cc3'
PERIOD_REL = ('product/lab/release-candidates/v1/interface/'
              'docker-source-20261020-0001/packages/0001/period.json')
PERIOD_SHA = 'f2633ba3d6c9868740749a3e7d8f288ea7abb461246f964e64c5dc9bf8b14bca'
PERIOD_REF = 'protocol:R03-docker-source-20261020-0001-period/v1'
ARCHIVE = ('product/lab/release-candidates/v1/interface/'
           'docker-source-20261020-0001/packages/0001/branch.snapshot')
ARCHIVE_SHA = '6d3cfc3f721b9be4fb8a1df14d4f43214709887213eaeae543927f214fdb9323'
ARCHIVE_SIZE = 23550300
NATIVE_SHA = 'fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'
SOURCE_ROOT = Path('/tmp/cal-mapper-only-dev-20261020-0001-release3/root')
ATTEMPT = Path('/tmp/cal-context-family-20261020-0001')
MARKER = Path('/tmp/.cal-context-family-20261020-0001-one-shot.json')
ROLE_PINS = {
    'product/lab/release-candidates/v1/interface/docker-source-20261020-0001/packages/0001/manifest.json':
        'f132b3e1908e9e116464ad29c3db7f56ca17d4dee080e60ffa62547dd9588a5b',
    'product/lab/release-candidates/v1/interface/docker-reader-20261020-0001/source-manifest.json':
        '4b61293453ec763f1c3567d3dac114e0d0782a2c58b85bc941ca34a0c974d251',
    'product/lab/release-candidates/v1/interface/docker-reader-20261020-0001/reader.py':
        'f93a1f218238c05b18a7c355f9bc1363bbf42d2b1d442d03e191e121f8e9c9b9',
    'product/lab/release-candidates/v1/interface/docker-mapped-20261020-0001/packages/0001/manifest.json':
        '0b3635dc9896034203e9e318ad99d58f2c37ca5acd419841d338f6ec9e4a1aea',
}
RELEASE_EFFECT_ENABLED = True
SECURITY_PROFILE = 'trusted_local_fixture'


class Refused(RuntimeError):
    pass


class Unknown(Refused):
    def __init__(self, primary, attempt_inode, marker, cleanup=()):
        self.primary = primary
        self.attempt_inode = attempt_inode
        self.marker = str(marker)
        self.cleanup = tuple(cleanup)
        self.outcome = 'UNKNOWN'
        self.retry_allowed = False
        self.disposition = 'RETAIN_OWNED_INODE_NO_NAME_UNLINK'
        super().__init__('one-shot stage outcome unknown; retain evidence and do not retry')


def need(ok, why):
    if not ok:
        raise Refused(why)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def close_once_all(fds):
    errors = []
    for fd in reversed(fds):
        try:
            os.close(fd)
        except BaseException as exc:
            errors.append((fd, repr(exc)))
    fds.clear()
    return errors


def held_public(path, pin, limit=2*1024*1024):
    """No-follow, bounded, single-inode read of a pinned public predecessor."""
    path = Path(path)
    need(path.is_absolute() and path.is_relative_to(REPO), 'public repository path required')
    owned = []; primary = None; result = None
    try:
        fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        owned.append(fd)
        for part in path.parts[1:-1]:
            fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW |
                         os.O_CLOEXEC, dir_fd=fd)
            owned.append(fd)
        fd = os.open(path.name, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW |
                     os.O_CLOEXEC, dir_fd=fd)
        owned.append(fd)
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
             0 <= before.st_size <= limit, 'public predecessor type/size differs')
        raw = bytearray()
        while True:
            block = os.read(fd, min(65536, before.st_size + 1 - len(raw)))
            if not block:
                break
            raw.extend(block)
            need(len(raw) <= before.st_size, 'public predecessor grew')
        after = os.fstat(fd)
        need((before.st_dev, before.st_ino, before.st_mode, before.st_uid,
              before.st_gid, before.st_nlink, before.st_size) ==
             (after.st_dev, after.st_ino, after.st_mode, after.st_uid,
              after.st_gid, after.st_nlink, after.st_size) and
             len(raw) == before.st_size and digest(raw) == pin,
             'public predecessor changed or digest differs')
        result = bytes(raw)
    except BaseException as exc:
        primary = exc
    cleanup = close_once_all(owned)
    if primary or cleanup:
        raise Refused('public predecessor read or FD cleanup uncertain') from primary
    return result


def reviewed_stage():
    freeze = json.loads(held_public(STAGE5 / 'freeze.json', STAGE5_FREEZE_SHA))
    held_public(LOCAL / 'CONTEXT-STAGE-EFFECT-INDEPENDENT-REVIEW-0005.md',
                STAGE5_REVIEW_SHA)
    profile = json.loads(held_public(STAGE5 / 'trusted-local-profile.json',
                                     STAGE5_PROFILE_SHA))
    code = held_public(STAGE5 / 'controller.py', STAGE5_CODE_SHA, 128*1024)
    need(freeze['files_sha256']['controller.py'] == STAGE5_CODE_SHA and
         freeze['files_sha256']['trusted-local-profile.json'] == STAGE5_PROFILE_SHA and
         profile['adversarial_same_uid_write_envelope'] == 'NOT_CLAIMED' and
         profile['real_protected_qualification'] == 'SEPARATE_UNSATISFIED_G01_G02' and
         profile['eventual_local_archive']['sha256'] == ARCHIVE_SHA and
         profile['eventual_local_archive']['size'] == ARCHIVE_SIZE and
         profile['eventual_local_archive']['body_this_unit'] == 'UNOPENED_UNCOPIED',
         'reviewed trusted-local stage contract differs')
    namespace = {'__file__': str(STAGE5 / 'controller.py'),
                 '__name__': '_pinned_context_stage_effect_0005'}
    exec(compile(code, str(STAGE5 / 'controller.py'), 'exec'), namespace)
    need(namespace['REAL_EFFECT_ENABLED'] is False, 'predecessor effect gate differs')
    return namespace


def utc_instant(value):
    need(type(value) is str, 'UTC instant required')
    time = dt.datetime.fromisoformat(value)
    need(time.tzinfo is not None and time.utcoffset() == dt.timedelta(0),
         'UTC instant required')
    return time


def current_period(stage, now):
    need(type(now) is dt.datetime and now.tzinfo is not None and
         now.utcoffset() == dt.timedelta(0), 'current UTC clock required')
    raw = stage['held_measure'](SOURCE_ROOT, PERIOD_REL, PERIOD_SHA, limit=16*1024,
                                capture=True)['bytes']
    period = json.loads(raw)
    need((json.dumps(period, indent=2, sort_keys=True, ensure_ascii=False,
                     allow_nan=False) + '\n').encode() == raw,
         'selected Source period bytes noncanonical')
    start = utc_instant(period['not_before']); end = utc_instant(period['expires_at'])
    need(period['period_ref'] == PERIOD_REF and period['authority_effect'] == 'none' and
         period['actual_owner_outcome'] is None and end-start == dt.timedelta(hours=24)
         and start <= now < end, 'selected disposable Source period not current')
    return {'path': PERIOD_REL, 'sha256': PERIOD_SHA,
            'not_before': period['not_before'], 'expires_at': period['expires_at'],
            'period_ref': PERIOD_REF, 'authority_effect': 'none'}


def predispatch(now=None):
    """One read-only same-process predispatch; archive body stays unopened."""
    need(os.getuid() == os.geteuid() and os.getgid() == os.getegid(),
         'selected real/effective identity split')
    now = now or dt.datetime.now(dt.timezone.utc)
    release_selection = json.loads(held_public(HERE / 'selection.json',
                                                RELEASE_SELECTION_SHA))
    predecessor = json.loads(held_public(LOCAL / 'context-stage-release-0001' /
                                         'freeze.json', RELEASE1_FREEZE_SHA))
    held_public(LOCAL / 'CONTEXT-STAGE-RELEASE-INDEPENDENT-STATIC-REVIEW-0001.md',
                RELEASE1_REVIEW_SHA)
    need(release_selection['security_profile'] == SECURITY_PROFILE and
         release_selection['schema_version'] ==
             'lab-context-stage-release-selection/v2-effect-enabled-unrun' and
         release_selection['status'] == 'EFFECT_ENABLED_ONE_SHOT_NOT_RUN' and
         release_selection['stage_selection_sha256'] == SELECTION_SHA and
         release_selection['predecessor_stage_review_sha256'] == STAGE5_REVIEW_SHA and
         release_selection['source_period']['sha256'] == PERIOD_SHA and
         release_selection['archive']['sha256'] == ARCHIVE_SHA and
         release_selection['archive']['size'] == ARCHIVE_SIZE and
         release_selection['stage_root_file_count'] == 1570 and
         release_selection['effect'] ==
             'ENABLED_NOT_RUN_PENDING_INDEPENDENT_STATIC_REVIEW' and
         release_selection['one_shot_attempt'] == str(ATTEMPT) and
         release_selection['one_shot_marker'] == str(MARKER) and
         release_selection['predecessor_release_freeze_sha256'] ==
             RELEASE1_FREEZE_SHA and
         release_selection['predecessor_release_review_sha256'] ==
             RELEASE1_REVIEW_SHA and
         predecessor['files_sha256']['release.py'] ==
             '0889bf23e57005627e3863b47deadb5b06790b00ebfd52747de72b9d568da05c' and
         release_selection['original_protected_G01_G02'] == 'UNSATISFIED',
         'closed release selection differs')
    stage = reviewed_stage()
    selected, rows = stage['closed_selection']()
    need(selected['source_family_root'] == str(SOURCE_ROOT) and
         selected['future_exclusive_stage_root'] == str(ATTEMPT / 'root') and
         selected['future_root_file_count_if_protected_copied_under_separate_effect'] == 1570,
         'exact reviewed 1570-file stage not selected')
    bound = stage['preflight_public'](rows)  # 1,569 public hashes; archive metadata only.
    native = stage['native_binding'](selected)
    by_path = {x['path']: x for x in bound}
    need(len(by_path) == 1570 and len(bound) == 1570 and
         all(by_path[path]['sha256'] == pin for path, pin in ROLE_PINS.items()) and
         by_path[ARCHIVE]['sha256'] == ARCHIVE_SHA and
         by_path[ARCHIVE]['size'] == ARCHIVE_SIZE and
         by_path[ARCHIVE]['mode'] == '0600' and
         by_path[ARCHIVE]['protected'] is True and
         native['sha256'] == NATIVE_SHA,
         'Source/Reader/Mapper/native/privately-bound role joins differ')
    period = current_period(stage, now)
    need(by_path[PERIOD_REL]['sha256'] == PERIOD_SHA,
         'selected public period row differs')
    need(not os.path.lexists(ATTEMPT) and not os.path.lexists(MARKER),
         'one-shot attempt or consumed marker already exists')
    return {'stage': stage, 'selected': selected, 'rows': bound, 'native': native,
            'period': period, 'checked_at': now.isoformat(),
            'public_rehashed': 1569, 'protected_body': 'UNOPENED',
            'security_profile': SECURITY_PROFILE, 'effect': 'NOT_RUN'}


def _reserve_and_claim():
    """Future effect only: durable marker before exclusive attempt creation."""
    need(RELEASE_EFFECT_ENABLED, 'stage release effect disabled')
    need(not os.path.lexists(MARKER) and not os.path.lexists(ATTEMPT),
         'one-shot marker or attempt occupied')
    raw = (json.dumps({'schema_version': 'lab-context-stage-release-claim/v1',
                       'attempt': str(ATTEMPT), 'selection_sha256': SELECTION_SHA,
                       'security_profile': SECURITY_PROFILE,
                       'status': 'RESERVED_NO_RETRY'}, sort_keys=True,
                      separators=(',', ':')) + '\n').encode()
    parent = os.open('/tmp', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW |
                     os.O_CLOEXEC)
    marker_fd = None; attempt_fd = None; primary = None; attempt_inode = None
    try:
        marker_fd = os.open(MARKER.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                            os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=parent)
        marker_st = os.fstat(marker_fd)
        need(stat.S_ISREG(marker_st.st_mode) and marker_st.st_nlink == 1 and
             marker_st.st_uid == os.geteuid() and marker_st.st_gid == os.getegid() and
             marker_st.st_mode & 0o777 == 0o600,
             'exclusive one-shot marker inode/mode/owner differs')
        view = memoryview(raw)
        while view:
            count = os.write(marker_fd, view)
            need(type(count) is int and count > 0, 'claim marker write stalled')
            view = view[count:]
        os.fsync(marker_fd); os.fsync(parent)
        marker_name = os.stat(MARKER.name, dir_fd=parent, follow_symlinks=False)
        need((marker_name.st_dev, marker_name.st_ino) ==
             (marker_st.st_dev, marker_st.st_ino),
             'one-shot marker name detached')
        os.mkdir(ATTEMPT.name, 0o700, dir_fd=parent)
        attempt_fd = os.open(ATTEMPT.name, os.O_RDONLY | os.O_DIRECTORY |
                             os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=parent)
        st = os.fstat(attempt_fd)
        attempt_inode = (st.st_dev, st.st_ino)
        attempt_name = os.stat(ATTEMPT.name, dir_fd=parent,
                               follow_symlinks=False)
        need(st.st_uid == os.geteuid() and st.st_gid == os.getegid() and
             st.st_mode & 0o777 == 0o700 and
             (attempt_name.st_dev, attempt_name.st_ino) == attempt_inode,
             'claimed attempt attachment/owner/mode differs')
        os.fsync(parent)
    except BaseException as exc:
        primary = exc
    owned = [x for x in (parent, marker_fd, attempt_fd) if x is not None]
    cleanup = close_once_all(owned)
    if primary or cleanup:
        raise Unknown(primary, attempt_inode, MARKER, cleanup) from primary
    return attempt_inode


def _materialize_after_claim(proof, attempt_inode):
    """Future-only exact copy order; no protected FD before `_reserve_and_claim`."""
    need(RELEASE_EFFECT_ENABLED and attempt_inode is not None,
         'stage release effect disabled or unclaimed')
    try:
        rows = proof['rows']
        need(len(rows) == 1570 and len({x['path'] for x in rows}) == 1570 and
             proof['selected']['future_exclusive_stage_root'] == str(ATTEMPT / 'root') and
             rows[-1].get('protected') is True and
             sum(x.get('protected', False) for x in rows) == 1,
             'exact reviewed stage proof required after claim')
        stage = proof['stage']
        stage['REAL_EFFECT_ENABLED'] = True  # Only inside this separately reviewed release.
        stage['mkdir_held'](ATTEMPT, 'root')
        stage['mkdir_held'](ATTEMPT, 'input')
        root = ATTEMPT / 'root'
        stage['create_dirs'](root, [x['path'] for x in rows])
        # The archive row is last. Every other selected file is copied first.
        for row in rows[:-1]:
            need(not row.get('protected'), 'private row must be copied last')
            stage['_copy_one_core'](row, root, allow_protected=True)
        private = rows[-1]
        need(private['path'] == ARCHIVE and private['sha256'] == ARCHIVE_SHA and
             private['size'] == ARCHIVE_SIZE and private['mode'] == '0600',
             'exact disposable family archive differs before private copy')
        # First opening of protected body in this release: after durable one-shot claim.
        stage['_copy_one_core'](private, root, allow_protected=True)
        native = stage['_copy_one_core'](proof['native'], ATTEMPT, allow_protected=True)
        verified = stage['verify_namespace'](root, rows)
        need(verified['files'] == 1570 and verified['private_digest_checked'] == 1 and
             native['sha256'] == NATIVE_SHA, 'full postcopy namespace/readback differs')
        current_period(stage, dt.datetime.now(dt.timezone.utc))
        receipt = {'schema_version': 'lab-context-stage-release-receipt/v1-candidate',
                   'status': 'STAGE_ONLY_PASS', 'security_profile': SECURITY_PROFILE,
                   'selection_sha256': SELECTION_SHA, 'attempt_inode': attempt_inode,
                   'stage_files': 1570, 'stage_directories': verified['directories'],
                   'archive_sha256': ARCHIVE_SHA, 'archive_size': ARCHIVE_SIZE,
                   'archive_body_opened_after_claim': True,
                   'native_sha256': NATIVE_SHA, 'context_launch': 'REFUSED',
                   'original_protected_G01_G02': 'UNSATISFIED'}
        receipt_sha = stage['terminal_receipt'](ATTEMPT, receipt)
        return {'status': 'STAGE_ONLY_PASS', 'receipt_sha256': receipt_sha,
                'attempt_inode': attempt_inode}
    except BaseException as exc:
        raise Unknown(exc, attempt_inode, MARKER) from exc


def release_effect():
    need(RELEASE_EFFECT_ENABLED, 'real stage release effect disabled pending review')
    proof = predispatch()  # Same process, immediately before one-shot claim.
    current_period(proof['stage'], dt.datetime.now(dt.timezone.utc))
    attempt_inode = _reserve_and_claim()
    return _materialize_after_claim(proof, attempt_inode)


def launch_context(*_args, **_kwargs):
    raise Refused('Context effect and launch remain disabled')


if __name__ == '__main__':
    if sys.argv[1:] == ['--predispatch']:
        value = predispatch()
        print(json.dumps({'status': 'EFFECT_ENABLED_PUBLIC_PREDISPATCH_ONLY',
                          'public_rehashed': value['public_rehashed'],
                          'period_expires_at': value['period']['expires_at'],
                          'protected_body': 'UNOPENED', 'context_launch': 'REFUSED'},
                         sort_keys=True))
    elif sys.argv[1:] == ['--effect']:
        print(json.dumps(release_effect(), sort_keys=True))
    else:
        raise SystemExit('closed command required')
