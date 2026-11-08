"""Effect-disabled host issuer projection for one disposable Context family.

Only public staged metadata and names are inspected. Actual Reader cold-open,
grant creation, private key creation, Context import and launch are disabled.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import importlib.util
import json
import os
import stat
import sys
from pathlib import Path

LOCAL = Path('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host')
ATTEMPT = Path('/tmp/cal-context-family-20261020-0001')
ROOT = ATTEMPT / 'root'
INTERFACE = Path('product/lab/release-candidates/v1/interface')
SOURCE = ROOT / INTERFACE / 'docker-source-20261020-0001'
CONTEXT = ROOT / INTERFACE / 'docker-context-20261020-0001'
READER = ROOT / INTERFACE / 'docker-reader-20261020-0001'
AUTH_DIR = SOURCE / 'authorization'
AUTH_LEAF = AUTH_DIR / 'context-development.json'
PRIVATE_ROOT = Path('/tmp/cal-context-jit-private-20261020-0001')
EXPECTED_SCOPE = 'scope:cyberalchemy-lab-first-agent-episode'
AUTH_REL = str(AUTH_LEAF.relative_to(ROOT))
SOURCE_REL = str(SOURCE.relative_to(ROOT))
AUTH_DIR_REL = str(AUTH_DIR.relative_to(ROOT))
PINS = {
    ATTEMPT / 'stage-receipt.json': '29f423fdd02e49931be361dd475be54457af383b58dd1ac4cb38f40a48125b6d',
    SOURCE / 'packages/0001/approval.json': '1dfa7d55643631d9669ea1e40bef329300a0a2939d736d36fd84f1a7a0453dfe',
    SOURCE / 'packages/0001/manifest.json': 'f132b3e1908e9e116464ad29c3db7f56ca17d4dee080e60ffa62547dd9588a5b',
    SOURCE / 'packages/0001/period.json': 'f2633ba3d6c9868740749a3e7d8f288ea7abb461246f964e64c5dc9bf8b14bca',
    SOURCE / 'source-manifest.json': '7e0938e70ac00b5308851b5a5a7c7bdb92041efab3be17296998acb4160395c1',
    READER / 'source-manifest.json': '4b61293453ec763f1c3567d3dac114e0d0782a2c58b85bc941ca34a0c974d251',
    READER / 'reader.py': 'f93a1f218238c05b18a7c355f9bc1363bbf42d2b1d442d03e191e121f8e9c9b9',
    READER / 'adapter.py': '85646307fa07c768105258ef0d49226b2d06fc70af3e5993fb2f58ca2124c399',
    LOCAL / 'context-stage-effect-0005/freeze.json': 'eef7bc55738be2dd5c7d493d19961592b5dce314a5004f4efb842f9a0029b659',
    LOCAL / 'context-stage-effect-independent-review-0001/result.json': 'e3d212e38205b41846961966230dd9b039942e68a18b900101a9a46a3e436aae',
    LOCAL / 'context-jit-provision-0001/freeze.json': 'fab03502c79f807eb33c1617cae3480d9a1e3fe2d6e26d2ef6dcb9a0a7b1d522',
    LOCAL / 'context-jit-effect-0003/freeze.json': 'aad1b0fe361629363e18c535205a37c44bdcba996d7464b58d74f9fea5792d99',
    LOCAL / 'context-jit-policy-0002/jit_policy.py': 'f40ca49a9f9f72e1c8490d753633c1db4307736a1b2f41080ee8a5f684c33a7a',
}
EFFECT_ENABLED = False


class Refused(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise Refused(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def wire(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False,
                       allow_nan=False) + '\n').encode()


def pinned(path):
    """A small public preimage only; never an archive, key, or AUTH leaf."""
    need(path in PINS, 'unselected preimage')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
             0 < before.st_size <= 2 * 1024 * 1024, 'bounded regular preimage required')
        raw = os.read(fd, before.st_size + 1)
        after = os.fstat(fd)
        need(len(raw) == before.st_size and
             (before.st_dev, before.st_ino, before.st_mode, before.st_size) ==
             (after.st_dev, after.st_ino, after.st_mode, after.st_size) and
             sha(raw) == PINS[path], 'preimage changed')
        return raw
    finally:
        os.close(fd)


def public_selection():
    for path in PINS:
        pinned(path)
    approval = json.loads(pinned(SOURCE / 'packages/0001/approval.json'))
    manifest = json.loads(pinned(SOURCE / 'packages/0001/manifest.json'))
    period_raw = pinned(SOURCE / 'packages/0001/period.json')
    receipt = json.loads(pinned(ATTEMPT / 'stage-receipt.json'))
    review = json.loads(pinned(LOCAL / 'context-stage-effect-independent-review-0001/result.json'))
    need(approval['authorized_domain_scope_refs'] == [EXPECTED_SCOPE] and
         approval['outcome'] == 'authorize-exact-local-effects',
         'selected public approval differs')
    approval_rel = str((SOURCE / 'packages/0001/approval.json').relative_to(ROOT))
    need(sum(row == {'path': approval_rel,
                     'sha256': PINS[SOURCE / 'packages/0001/approval.json']}
             for row in manifest['files']) == 1, 'approval not bound by Source package')
    period_rel = str((SOURCE / 'packages/0001/period.json').relative_to(ROOT))
    need(manifest['period_binding'] == {'path': period_rel,
                                        'sha256': PINS[SOURCE / 'packages/0001/period.json']},
         'period not bound by Source package')
    need(receipt['status'] == 'STAGE_ONLY_PASS' and
         receipt['security_profile'] == 'trusted_local_fixture' and
         receipt['stage_files'] == 1570 and receipt['stage_directories'] == 1021 and
         receipt['context_launch'] == 'REFUSED', 'selected staged family differs')
    need(review['verdict'] == 'PASS_TRUSTED_LOCAL_STAGE_EFFECT' and
         review['stage_receipt_sha256'] == PINS[ATTEMPT / 'stage-receipt.json'] and
         review['stage_files'] == 1570 and
         review['original_protected_G01_G02'] == 'UNSATISFIED',
         'independent trusted-local stage effect review differs')
    return period_raw


def instant(value):
    need(type(value) is str, 'timestamp required')
    try:
        parsed = dt.datetime.fromisoformat(value)
    except ValueError as error:
        raise Refused('valid UTC timestamp required') from error
    need(parsed.tzinfo is not None and parsed.utcoffset() == dt.timedelta(),
         'UTC timestamp required')
    return parsed


def period_window(period_raw, now):
    need(type(period_raw) is bytes and sha(period_raw) ==
         PINS[SOURCE / 'packages/0001/period.json'], 'selected period bytes differ')
    need(type(now) is dt.datetime and now.tzinfo is not None and
         now.utcoffset() == dt.timedelta() and now.microsecond == 0,
         'whole-second UTC effect time required')
    period = json.loads(period_raw)
    start, end = instant(period['not_before']), instant(period['expires_at'])
    need(period['period_ref'] == 'protocol:R03-docker-source-20261020-0001-period/v1' and
         period['principal_ref'] == 'principal:R03-docker-source-20261020-0001' and
         period['authority_effect'] == 'none' and period['actual_owner_outcome'] is None and
         end - start == dt.timedelta(hours=24) and start <= now < end,
         'current exact 24-hour Source period required')
    expiry = min(end, now + dt.timedelta(minutes=20))
    need(now < expiry and expiry - now <= dt.timedelta(minutes=20),
         'no finite authorization interval')
    return period, expiry


def stage_names():
    """Read names and inode metadata only; no staged file body is opened."""
    need(ROOT.is_dir() and SOURCE.is_dir() and CONTEXT.is_dir(),
         'exact staged role directories required')
    st = os.lstat(SOURCE)
    need(stat.S_ISDIR(st.st_mode) and stat.S_IMODE(st.st_mode) == 0o700 and
         st.st_uid == os.getuid() == os.geteuid() and
         st.st_gid == os.getgid() == os.getegid(),
         'Source role must be owned 0700')
    files, dirs = set(), set()
    for base, children, leaves, dirfd in os.fwalk(ROOT, follow_symlinks=False):
        base_rel = Path(base).relative_to(ROOT)
        for name in children:
            relative = str(base_rel / name)
            info = os.stat(name, dir_fd=dirfd, follow_symlinks=False)
            need(stat.S_ISDIR(info.st_mode), 'non-directory in staged directory namespace')
            dirs.add(relative)
        for name in leaves:
            relative = str(base_rel / name)
            info = os.stat(name, dir_fd=dirfd, follow_symlinks=False)
            need(stat.S_ISREG(info.st_mode) and info.st_nlink == 1,
                 'non-regular staged file')
            files.add(relative)
    return files, dirs


def topology_projection(files, dirs):
    need(type(files) is set and type(dirs) is set and len(files) == 1570 and
         len(dirs) == 1021 and AUTH_REL not in files and AUTH_DIR_REL not in dirs and
         SOURCE_REL in dirs and all(type(x) is str for x in files | dirs),
         'exact absent AUTH namespace and 1570-file baseline required')
    final_files = files | {AUTH_REL}
    final_dirs = dirs | {AUTH_DIR_REL}
    need(len(final_files) == 1571 and len(final_dirs) == 1022 and
         final_files - files == {AUTH_REL} and final_dirs - dirs == {AUTH_DIR_REL},
         'versioned 1571 namespace projection differs')
    return {'baseline_files': 1570, 'baseline_directories': 1021,
            'projected_files': 1571, 'projected_directories': 1022,
            'added_file': AUTH_REL, 'added_directory': AUTH_DIR_REL,
            'source_mode': '0700', 'authorization_directory_mode': '0700',
            'authorization_leaf_mode': '0600', 'authorization_sha256': 'UNMINTED',
            'actual_namespace_effect': 'NOT_RUN'}


def selected_jit(period_raw, now, scope_ref):
    """Synthetic projection; caller scope is never evidence of a signed view."""
    need(scope_ref == EXPECTED_SCOPE, 'signed scope must match public approval')
    period_window(period_raw, now)
    path = LOCAL / 'context-jit-policy-0002/jit_policy.py'
    pinned(path)
    spec = importlib.util.spec_from_file_location('_authority_jit_policy', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    need(module.EFFECT_ENABLED is False, 'selected JIT policy must be inert')
    selection = module.select({
        'family_ref': str(CONTEXT), 'source_root': str(SOURCE),
        'private_root': str(PRIVATE_ROOT), 'uid': os.getuid(), 'gid': os.getgid(),
        'principal_ref': 'principal:R03-docker-source-20261020-0001',
        'scope_ref': scope_ref, 'reader_code_sha256': module.READER_CODE_SHA,
        'reader_manifest_sha256': module.READER_MANIFEST_SHA,
        'source_package_sha256': module.SOURCE_PACKAGE_SHA,
        'mapper_package_sha256': module.MAPPER_PACKAGE_SHA,
        'period_sha256': module.PERIOD_SHA}, period_raw, now)
    need(selection['authorization_path'] == str(AUTH_LEAF) and
         selection['private_root'] == str(PRIVATE_ROOT),
         'exact JIT roots differ')
    return module, selection


def project_authorization(period_raw, now, scope_ref):
    """Construct schema bytes from synthetic scope; does not issue or write."""
    period, expiry = period_window(period_raw, now)
    jit, selected = selected_jit(period_raw, now, scope_ref)
    value = {'schema_version': 'lab-context-development-authorization/v1-candidate',
             'family_ref': str(CONTEXT), 'episode_ref': period['period_ref'],
             'scope_ref': scope_ref,
             'period_binding': {'path': jit.PERIOD_REL, 'sha256': jit.PERIOD_SHA},
             'not_before': now.strftime('%Y-%m-%dT%H:%M:%SZ'),
             'expires_at': expiry.strftime('%Y-%m-%dT%H:%M:%SZ'),
             'authority_effect': 'none', 'actual_owner_outcome': None,
             'claim_ceiling': jit.CLAIM}
    raw = wire(value)
    result = jit.validate_authorization(raw, selected, now)
    need(result['authorization_sha256'] == sha(raw), 'authorization projection differs')
    return raw, {'sha256': sha(raw), 'expires_at': value['expires_at'],
                 'claim': 'SYNTHETIC_PROJECTION_UNISSUED'}


def future_signed_reader_contract():
    """The effect owner must implement this ordered, held Reader transaction."""
    return ('RESERVE_EXCLUSIVE_DURABLE_ONE_SHOT_MARKER_OUTSIDE_AUTH_DIRECTORY',
            'PIN_EXACT_STAGED_READER_CODE_AND_SOURCE_PACKAGE',
            'OPEN_READER_OPEN_SIGNED_ON_EXACT_STAGED_FAMILY',
            'CHECK_SIGNED_GUARD_AND_VIEW_CONFIG_SCOPE_AGAINST_PUBLIC_APPROVAL',
            'CHECK_SIGNED_SOURCES_SCOPE_EQUALS_VIEW_CONFIG_SCOPE',
            'READ_EXACT_MANIFEST_BOUND_PERIOD_WHILE_SIGNED_VIEW_HELD',
            'CHECK_24_HOUR_PERIOD_CURRENT_AND_20_MINUTE_WINDOW',
            'CLOSE_SIGNED_VIEW_AND_REQUIRE_SUCCESSFUL_FINAL_GUARD_AND_CLOSE')


def effect_time_signed_scope(reader, now):
    """Future held Reader extraction; unreachable while effect is disabled.

    The caller must load the selected Reader from the pinned staged package.
    Returning is only possible after open_signed's final guard and close.
    """
    need(EFFECT_ENABLED, 'effect disabled: signed Source archive body is not opened')
    for path in (READER / 'reader.py', READER / 'adapter.py',
                 READER / 'source-manifest.json', SOURCE / 'source-manifest.json'):
        pinned(path)
    loaded = sys.modules.get(type(reader).__module__)
    need(type(reader).__name__ == 'SelectedReader' and loaded is not None and
         Path(getattr(loaded, '__file__', '')) == READER / 'reader.py' and
         reader.HERE == SOURCE and
         reader.adapter_pin == PINS[READER / 'source-manifest.json'] and
         reader.source_pin == PINS[SOURCE / 'source-manifest.json'] and
         reader.package_pin == PINS[SOURCE / 'packages/0001/manifest.json'],
         'exact staged Reader instance required')
    reader.guard()
    with reader.open_signed(reader.source_pin, reader.package_pin) as signed:
        signed.guard()
        scope = signed.view.data['config']['scope_ref']
        need(type(scope) is str and scope == EXPECTED_SCOPE and
             signed.sources.scope_ref == scope,
             'held signed Source scope differs from public approval')
        period_raw = pinned(SOURCE / 'packages/0001/period.json')
        period_window(period_raw, now)
        signed.guard()
    # The contextmanager's exit performed its final selected.guard(),
    # reader.guard() and selected.close(); no authority effect precedes it.
    reader.guard()
    period_window(period_raw, now)
    public_selection()
    return scope, period_raw


def future_release_contract():
    """Design of the real successor; no step is executed by this module."""
    return (
        'RECHECK_CONSUMED_STAGE_RECEIPT_AND_CLOSED_1570_NAMESPACE',
        *future_signed_reader_contract(),
        'REQUIRE_TRUSTED_COOPERATIVE_SINGLE_WRITER_UID_AND_DOCKER_NAMESPACE',
        'CREATE_AUTH_DIRECTORY_EXCLUSIVE_OWNER_0700_NOFOLLOW_AND_FSYNC_SOURCE',
        'OBTAIN_APPROVED_LOCAL_ISSUER_BYTES_FOR_EXACT_CONTEXT_FAMILY',
        'VALIDATE_HELD_AUTH_BYTES_DIGEST_SCOPE_PERIOD_AND_20_MINUTE_WINDOW',
        'CREATE_AUTH_LEAF_EXCLUSIVE_OWNER_0600_NOFOLLOW_FSYNC_CLOSE_READBACK',
        'VERIFY_EXACT_1571_FILES_AND_1022_DIRECTORIES_PLUS_ALL_SELECTED_HASHES',
        'WRITE_VERSIONED_FINAL_SELECTION_AND_DURABLE_AUTHORITY_RECEIPT',
        'ON_ANY_UNCERTAINTY_RECORD_UNKNOWN_RETAIN_INODE_CUSTODY_AND_NEVER_RETRY',
        'CHILD_GENERATES_ONE_USE_KEY_IN_ITS_EXCLUSIVE_0700_PRIVATE_ROOT',
        'CHILD_WRITES_0600_POLICY_WITH_HELD_DIGEST_AND_BOUND_INTERVAL',
        'CHILD_AUTHENTICATES_ONE_HOSTCHANNEL_CHALLENGE_AND_CLOSES_CHANNEL',
        'CHILD_DROPS_KEY_REFERENCE_AND_RETAINS_UNKNOWN_OBJECTS_FOR_DISPOSITION',
        'NO_BY_NAME_CLEANUP_AFTER_UNCERTAINTY_OR_SAME_UID_INTERFERENCE',
    )


def _fixture_dir(base):
    path = Path(base)
    need(path.is_absolute() and path.parent == Path('/tmp') and
         path.name.startswith('cal-authority-release-fixture-'),
         'isolated fixture directory required')
    info = os.lstat(path)
    need(stat.S_ISDIR(info.st_mode) and stat.S_IMODE(info.st_mode) == 0o700 and
         info.st_uid == os.getuid() == os.geteuid() and
         info.st_gid == os.getgid() == os.getegid(),
         'owned fixture directory required')
    return path


def fixture_reserve(base, inject=None):
    """Durable dummy attempt marker only. It never authorizes real work.

    Failure leaves a possibly partial marker and always consumes its name.
    The caller owns fixture cleanup after inspecting the retained evidence.
    """
    path = _fixture_dir(base) / 'attempt.jsonl'
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                 os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    uncertain = None
    try:
        raw = wire({'event': 'INTENT', 'effect': 'FIXTURE_ONLY',
                    'status': 'CONSUMED_NO_RETRY'})
        need(os.write(fd, raw) == len(raw), 'short fixture intent write')
        if inject == 'write':
            raise OSError('injected write uncertainty')
        os.fsync(fd)
    except BaseException as error:
        uncertain = error
    try:
        os.close(fd)
        if inject == 'close':
            raise OSError('injected close uncertainty')
    except BaseException as error:
        uncertain = error
    try:
        parent_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY |
                            os.O_NOFOLLOW | os.O_CLOEXEC)
        try:
            os.fsync(parent_fd)
        finally:
            os.close(parent_fd)
    except BaseException as error:
        uncertain = error
    return {'status': 'UNKNOWN_PRESERVE_NO_RETRY' if uncertain else 'FIXTURE_INTENT_DURABLE',
            'marker': str(path), 'retry_allowed': False,
            'effect': 'FIXTURE_ONLY'}


def issue_actual(*_args, **_kwargs):
    raise Refused('effect disabled: no actual signed view, issuer grant, AUTH write or Context launch')


def mutate_stage(*_args, **_kwargs):
    raise Refused('effect disabled: consumed stage and 1570-file receipt are immutable')


def create_runtime_key(*_args, **_kwargs):
    raise Refused('effect disabled: one-use key belongs only to future Docker child')
