"""Effect-disabled Context stage-copy and JIT-authority successor design.

The actual Mapper effect/review is not selected. No provided bytes can turn this
module into a stage writer, issuer, key generator, policy writer, or Docker runner.
"""
from __future__ import annotations

import hashlib
import importlib.util
import os
import stat
from pathlib import Path

LOCAL = Path('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host')
FINAL = LOCAL / 'context-successor-final-stage-0002/final_stage.py'
FINAL_FREEZE = LOCAL / 'context-successor-final-stage-0002/freeze.json'
FINAL_REVIEW = LOCAL / 'CONTEXT-SUCCESSOR-FINAL-STAGE-INDEPENDENT-STATIC-REVIEW-0002.md'
JIT = LOCAL / 'context-successor-jit-0002/jit_successor.py'
JIT_FREEZE = LOCAL / 'context-successor-jit-0002/freeze.json'
JIT_REVIEW = LOCAL / 'CONTEXT-SUCCESSOR-JIT-INDEPENDENT-STATIC-REVIEW-0002.md'
GUARDED_BUILD = LOCAL / 'context-jit-provision-0001/projected-build.py'
GUARDED_CONTROL = LOCAL / 'context-jit-provision-0001/projected-control.py'
PINS = {
    FINAL: 'e31d75f137e065e747f04ae85ce1e7cfdea2a6e184ce4f46d866b25155d67c71',
    FINAL_FREEZE: '4ba5f738e432f7dda855f0bab57de0495ae1105da1e8650e15864c5d2a81536f',
    FINAL_REVIEW: '1da3d7a361be23b81b6ea665cac07b29d110ea25aead6c422476010bb9b31404',
    JIT: '519053bc518a6d1822d731a3133e3219c7a80350e4384cec5c922b4895183f01',
    JIT_FREEZE: '06501e59f66afcec5ff360750bec142b7293abdcb82d418f4800d9fd965b6136',
    JIT_REVIEW: '5a01e697c80beb877777c8c722d1c027922924ebab44ec5c8546add6a96cc081',
    GUARDED_BUILD: '30149a0388f3eb32fb30dd5b07bc11a8309ed7ab3fafa56ef8b5d714d39f93f0',
    GUARDED_CONTROL: 'ebd63979ce378070e6d5647c240234548a9fb38d141b6ed0d57885925f66c7e1',
}
EFFECT_ENABLED = False
MAPPER_REVIEW_SELECTION = None
BOUND_ROWS = 1570
FINAL_ROWS = 1571
MAPPER_SOURCE_ROWS = 953
SEQUENCE = (
    'RECHECK_CURRENT_SOURCE_PERIOD_AND_REVIEWED_SOURCE_READER_EVIDENCE',
    'SELECT_ACTUAL_MAPPER_EFFECT_BY_OUTSIDE_INDEPENDENT_REVIEW',
    'RECOMPUTE_EXACT_953_MAPPER_SOURCE_ROWS_AND_55_PACKAGE_FILES',
    'PROJECT_EXACT_1570_ROWS_AND_GUARDED_CONTEXT_API_ROLES',
    'REVIEW_PROTECTED_ARCHIVE_COPY_AS_SEPARATE_BOUND_EFFECT',
    'READ_ONLY_HOLD_NOFOLLOW_OWNER_0700_ANCESTRY_AND_CHECK_STAGE_ABSENCE',
    'EXCLUSIVELY_CREATE_STAGE_ROOT_AS_CONSUMED_ATTEMPT_CLAIM',
    'ON_POSTCLAIM_PREMARKER_UNCERTAINTY_RETAIN_ROOT_INODES_UNKNOWN_NO_RETRY',
    'WRITE_CLOSE_AND_FSYNC_DURABLE_NO_RETRY_MARKER_BEFORE_STAGE_CONTENT',
    'COPY_EXACT_1570_FILES_WITH_HASH_MODE_AND_HELD_READBACK',
    'VERIFY_PHYSICAL_STAGE_CLOSURE_NO_EXTRAS_AND_FSYNC',
    'OPEN_READER_SIGNED_SCOPE_ONCE_AND_JOIN_CURRENT_SOURCE_PERIOD',
    'OBTAIN_OUTSIDE_APPROVED_ISSUER_FOR_EXACT_CONTEXT_FAMILY',
    'WRITE_AUTH_EXCLUSIVE_OWNER_0600_NOFOLLOW_FSYNC_AND_HELD_READBACK',
    'VERIFY_EXACT_1571_FILES_WITH_UNMINTED_AUTH_REPLACED_BY_ISSUED_LEAF',
    'CREATE_DISJOINT_PRIVATE_ROOT_EXCLUSIVE_OWNER_0700',
    'GENERATE_ONE_USE_IN_MEMORY_ED25519_KEY',
    'CONSTRUCT_BYTE_BOUND_POLICY_FROM_SIGNED_SCOPE_AND_CURRENT_PERIOD',
    'WRITE_PRIVATE_POLICY_EXCLUSIVE_OWNER_0600_NOFOLLOW_FSYNC_READBACK',
    'OPEN_HOSTCHANNEL_AND_AUTHENTICATE_EXACT_CHALLENGE_ONCE',
    'DISPATCH_EXACT_CONTEXT_DOCKER_RELEASE_AND_OBSERVE_EXTERNAL_OS_EXIT',
    'CLOSE_CHANNEL_AND_DROP_IN_MEMORY_KEY_KEEP_PRIVATE_EVIDENCE',
    'VERIFY_TERMINAL_OUTPUT_EXTERNAL_OS_AND_DOCKER_ABSENCE_BEFORE_CLEANUP',
    'REMOVE_ONLY_HELD_VERIFIED_EPHEMERAL_INODES_AFTER_ABSENCE',
    'FSYNC_AND_DURABLY_RECORD_CONSUMED_ATTEMPT',
)


class Refused(ValueError):
    pass


def need(ok, why):
    if not ok:
        raise Refused(why)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def pinned_public(path):
    need(path in PINS, 'UNSELECTED_PUBLIC_INPUT')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
             0 < before.st_size <= 2 * 1024 * 1024, 'PUBLIC_PIN_SHAPE')
        raw = os.read(fd, before.st_size + 1)
        after = os.fstat(fd)
        need(len(raw) == before.st_size and
             (before.st_dev,before.st_ino,before.st_mode,before.st_size) ==
             (after.st_dev,after.st_ino,after.st_mode,after.st_size) and
             digest(raw) == PINS[path], 'PUBLIC_PIN_DRIFT')
        return raw
    finally:
        os.close(fd)


def reviewed_modules():
    for path in PINS:
        pinned_public(path)
    build = pinned_public(GUARDED_BUILD)
    control = pinned_public(GUARDED_CONTROL)
    need(build.count(b'def _t35_effect_refused():') == 1 and
         build.count(b"raise RuntimeError('Generated T35 role effects require the uninstalled T02 custody gate')") == 1 and
         b'_jit_private_root() as tmp:' in build and
         b'HostChannel(policy_path, policy_pin, source_pin, source, schemas)' in build and
         control.count(b'def read_auth_bytes(') == 1 and
         control.count(b'def read_policy_bytes(') == 1 and
         control.count(b'def authenticate(self, proof_raw):') == 1 and
         control.count(b'def _t35_effect_refused():') == 1,
         'FROZEN_CONTEXT_ROLE_GUARD')
    modules = []
    for name, path in (('cal_final_stage_reviewed_0002',FINAL),
                       ('cal_jit_reviewed_0002',JIT)):
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        modules.append(module)
    return modules


def checked_sequence(steps):
    """Reject plans that reorder the two custody-sensitive transitions."""
    need(type(steps) is tuple and len(steps) == len(set(steps)),
         'RELEASE_SEQUENCE_DUPLICATE_OR_SHAPE')
    def ordered(*names):
        need(all(name in steps for name in names) and
             list(map(steps.index,names)) == sorted(map(steps.index,names)),
             'RELEASE_SEQUENCE_CUSTODY_ORDER')
    ordered('READ_ONLY_HOLD_NOFOLLOW_OWNER_0700_ANCESTRY_AND_CHECK_STAGE_ABSENCE',
            'EXCLUSIVELY_CREATE_STAGE_ROOT_AS_CONSUMED_ATTEMPT_CLAIM',
            'ON_POSTCLAIM_PREMARKER_UNCERTAINTY_RETAIN_ROOT_INODES_UNKNOWN_NO_RETRY',
            'WRITE_CLOSE_AND_FSYNC_DURABLE_NO_RETRY_MARKER_BEFORE_STAGE_CONTENT',
            'COPY_EXACT_1570_FILES_WITH_HASH_MODE_AND_HELD_READBACK',
            'VERIFY_PHYSICAL_STAGE_CLOSURE_NO_EXTRAS_AND_FSYNC')
    ordered('DISPATCH_EXACT_CONTEXT_DOCKER_RELEASE_AND_OBSERVE_EXTERNAL_OS_EXIT',
            'CLOSE_CHANNEL_AND_DROP_IN_MEMORY_KEY_KEEP_PRIVATE_EVIDENCE',
            'VERIFY_TERMINAL_OUTPUT_EXTERNAL_OS_AND_DOCKER_ABSENCE_BEFORE_CLEANUP',
            'REMOVE_ONLY_HELD_VERIFIED_EPHEMERAL_INODES_AFTER_ABSENCE',
            'FSYNC_AND_DURABLY_RECORD_CONSUMED_ATTEMPT')
    return list(steps)


def plan(now=None):
    """Current evidence and executable design; no actual Mapper selection."""
    final, jit = reviewed_modules()
    sequence = checked_sequence(SEQUENCE)
    selected = final.preflight_plan(now)
    topology = jit.topology()
    need(selected['status'] == 'WAIT_OUTSIDE_PINNED_MAPPER_EFFECT' and
         selected['mapper_effect_review'] == 'UNSELECTED' and
         selected['reader_stage_files'] == 986 and
         selected['public_checkout_additions'] == 512 and
         selected['required_mapper_role_files'] == 5 and
         selected['required_mapper_package_files'] == 55 and
         selected['required_api_projection_files'] == 5 and
         selected['required_context_projection_files'] == 7 and
         selected['final_file_count_if_all_gates_pass'] == FINAL_ROWS and
         selected['protected_archive']['body'] == 'UNOPENED' and
         selected['stage_root'] == topology['stage_root'] and
         selected['private_root'] == topology['private_root'] and
         topology['authorization_path'].startswith(topology['stage_root']+'/') and
         not topology['private_root'].startswith(topology['stage_root']+'/') and
         topology['authorization_directory_mode'] == '0700' and
         topology['authorization_leaf_mode'] == '0600' and
         topology['private_root_mode'] == '0700' and
         topology['policy_leaf_mode'] == '0600',
         'REVIEWED_FINAL_JIT_TOPOLOGY_CLOSURE')
    return {'status':'WAIT_OUTSIDE_PINNED_MAPPER_EFFECT',
            'effect_enabled':False,
            'source_period_sha256':selected['source_period_sha256'],
            'source_manifest_sha256':selected['source_manifest_sha256'],
            'reader_manifest_sha256':selected['reader_manifest_sha256'],
            'reader_effect_review_sha256':selected['reader_effect_review_sha256'],
            'mapper_source_rows_required':MAPPER_SOURCE_ROWS,
            'bound_rows_after_mapper':BOUND_ROWS,
            'final_rows_after_issued_auth':FINAL_ROWS,
            'protected_archive':selected['protected_archive'],
            'topology':topology,'sequence':sequence,
            'root_claim':'EXCLUSIVE_ROOT_CREATION_CONSUMES_ATTEMPT',
            'premarker_uncertainty':'UNKNOWN_PRESERVE_ROOT_INODE_EVIDENCE_NO_RETRY',
            'marker_requirement':'DURABLE_BEFORE_FIRST_STAGE_CONTENT_MUTATION',
            'cleanup_requirement':'TERMINAL_OUTPUT_EXTERNAL_OS_AND_DOCKER_ABSENCE_VERIFIED_FIRST',
            'unknown_rule':'PRESERVE_ROOT_MARKER_STAGE_PRIVATE_EVIDENCE_AND_NEVER_RETRY_ATTEMPT',
            'mapper_review':'UNSELECTED',
            'signed_scope':'NOT_OPENED','issuer':'UNSELECTED',
            'stage_copy':'REFUSED','authorization':'UNMINTED',
            'private_key':'UNCREATED','policy':'UNWRITTEN',
            'docker_effect':'REFUSED'}


def select_after_mapper(*_args, **_kwargs):
    # A future revision must bind the *actual* independent Mapper review here.
    need(MAPPER_REVIEW_SELECTION is not None, 'MAPPER_REVIEW_NOT_OUTSIDE_SELECTED')
    raise Refused('MAPPER_REVIEW_SELECTION_REQUIRES_NEW_REVIEWED_REVISION')


def copy_final_stage(*_args, **_kwargs):
    raise Refused('EFFECT_DISABLED_NO_FINAL_STAGE_COPY')


def issue_authorization(*_args, **_kwargs):
    raise Refused('EFFECT_DISABLED_NO_ISSUER_OR_AUTH_LEAF')


def create_private_root_key_or_policy(*_args, **_kwargs):
    raise Refused('EFFECT_DISABLED_NO_PRIVATE_ROOT_KEY_OR_POLICY')


def launch_context(*_args, **_kwargs):
    raise Refused('EFFECT_DISABLED_NO_CONTEXT_DOCKER_RELEASE')
