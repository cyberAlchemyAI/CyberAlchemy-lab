"""Effect-disabled parent-Writer/child-read-only mount reconciliation."""
from __future__ import annotations

import hashlib
import os
import stat
import types
from pathlib import Path

LOCAL = Path('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host')
PREVIOUS = LOCAL / 'context-successor-docker-output-plan-0001/docker_output.py'
PREVIOUS_FREEZE = LOCAL / 'context-successor-docker-output-plan-0001/freeze.json'
PREVIOUS_REVIEW = LOCAL / 'CONTEXT-SUCCESSOR-DOCKER-OUTPUT-INDEPENDENT-STATIC-REVIEW-0001.md'
PINS = {
    PREVIOUS:'bebb3686cc49f94885d2f89761e7ff093cfce3c3ce848c47cb51afc777f6ee75',
    PREVIOUS_FREEZE:'09498aa6bdb060e1de6c1f25d5a26fbde69f304ede1a2c60a6c5cf9a9e507993',
    PREVIOUS_REVIEW:'d34b1e5b46193af626309681e5f31079ed4b7609743e330c35d528cdcf3dc381',
}
FAMILY = Path('/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001')
DOCKER_ATTEMPT = FAMILY / 'context-docker-attempt-0001'
NATIVE = Path('/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004/bin/lab-context-native-reader')
NATIVE_SHA = 'fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'
GUARD_SHA = '1d320473ba057e508a1b52176c556cd2f368e3edfc4f8de4d7de076edf831538'
EFFECT_ENABLED = False


class Refused(ValueError):
    pass


def need(ok, why):
    if not ok:
        raise Refused(why)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pinned(path):
    need(path in PINS, 'UNSELECTED_PREDECESSOR')
    fd = os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        a = os.fstat(fd)
        need(stat.S_ISREG(a.st_mode) and a.st_nlink == 1 and
             0 < a.st_size <= 2*1024*1024,'PREDECESSOR_SHAPE')
        raw = os.read(fd,a.st_size+1)
        b = os.fstat(fd)
        need(len(raw) == a.st_size and
             (a.st_dev,a.st_ino,a.st_mode,a.st_size) ==
             (b.st_dev,b.st_ino,b.st_mode,b.st_size) and
             sha(raw) == PINS[path],'PREDECESSOR_DRIFT')
        return raw
    finally:
        os.close(fd)


def predecessor():
    for path in PINS:
        pinned(path)
    module = types.ModuleType('cal_context_docker_output_reviewed_0001')
    module.__file__ = str(PREVIOUS)
    exec(compile(pinned(PREVIOUS),str(PREVIOUS),'exec'),module.__dict__)
    return module


def vector(now=None):
    prior = predecessor().plan(now)
    need(prior['status'] == 'WAIT_MAPPER_STAGE_AUTH_AND_CONTEXT_SOURCE' and
         prior['physical_stage_files_required'] == 1571 and
         prior['output_leaf_count'] == 40 and
         prior['manifest_member_rows'] == 39 and
         prior['writer_private_release_ordinal'] == 38 and
         prior['finish_ordinal'] == 41 and
         prior['wire_request_count'] == 42 and
         prior['authorization'] == 'UNMINTED' and
         prior['docker'] == 'REFUSED' and
         prior['context'] == 'REFUSED' and
         prior['cleanup'] == 'REFUSED',
         'REVIEWED_ORIGINAL_PROTOCOL_GATE')
    public = FAMILY/'context-attempt/root'
    need(prior['physical_output_root'] ==
         str(public/prior['context_role']/'packages/0001'),
         'DURABLE_PUBLIC_BIND_SOURCE')
    mounts = (
        {'source':str(public),'target':'/workspace','read_only':True},
        {'source':str(DOCKER_ATTEMPT/'control'),'target':'/control','read_only':True},
        {'source':str(DOCKER_ATTEMPT/'runner-code'),'target':'/runner','read_only':True},
        {'source':str(DOCKER_ATTEMPT/'cache-guard'),'target':'/cache-disabled','read_only':True},
        {'source':str(NATIVE),'target':'/attempt/input/lab-context-native-reader',
         'read_only':True},
    )
    targets = {row['target'] for row in mounts}
    need(len(targets) == len(mounts) == 5 and
         all(row['read_only'] is True for row in mounts) and
         not any(target.startswith('/workspace/') for target in targets) and
         '/workspace' in targets and '/control' in targets and '/runner' in targets and
         '/cache-disabled' in targets and
         '/attempt/input/lab-context-native-reader' in targets,
         'EXACT_FIVE_READ_ONLY_BINDS_NO_NESTED_OUTPUT')
    return {'status':'INERT_PARENT_WRITER_CHILD_RO_MOUNT_VECTOR',
            'effect_enabled':False,'mounts':list(mounts),
            'physical_output_root':prior['physical_output_root'],
            'logical_output_root':prior['logical_output_root'],
            'parent_writer_access':'RW_HELD_DESCRIPTOR',
            'child_workspace_access':'RO_BIND',
            'child_nested_output_bind':'ABSENT',
            'context_role':prior['context_role'],
            'context_source_manifest':'UNCREATED',
            'authorization':'UNMINTED',
            'original_guard_sha256':GUARD_SHA,
            'native_sha256':NATIVE_SHA,
            'ready_before_parent_package_creation':True,
            'mountinfo_workspace':'REQUIRE_RO_AND_NO_NESTED_WORKSPACE_MOUNT',
            'child_write_sentinel':'REQUIRE_ERRNO_EROFS_30',
            'post_ack_visibility':'REQUIRE_EXACT_CHILD_READBACK_SHA',
            'probe':'SYNTHETIC_ONLY_REAL_NAMESPACE_UNRUN',
            'docker':'REFUSED','authority':'REFUSED','cleanup':'REFUSED'}


def _mountinfo_rows(raw):
    need(type(raw) is bytes and 0 < len(raw) <= 64*1024,
         'BOUNDED_MOUNTINFO_FIXTURE')
    result = []
    try:
        for line in raw.decode('ascii').splitlines():
            head,tail = line.split(' - ',1)
            fields = head.split(' ')
            need(len(fields) >= 6 and len(tail.split(' ')) >= 3,
                 'MOUNTINFO_LINE_SHAPE')
            result.append({'mountpoint':fields[4],
                           'options':set(fields[5].split(','))})
    except (UnicodeError,ValueError) as exc:
        raise Refused('MOUNTINFO_LINE_SHAPE') from exc
    return result


def check_synthetic_probe(*, mounts, mountinfo_raw, ready, selected_token,
                          parent_absent_at_ready, sentinel, ack):
    """Fixture-only causal proof of required observations, never a live probe."""
    selected = vector()
    need(mounts == selected['mounts'],'DOCKER_INSPECT_EXACT_MOUNT_VECTOR')
    parsed = _mountinfo_rows(mountinfo_raw)
    workspace = [r for r in parsed if r['mountpoint'] == '/workspace']
    need(len(workspace) == 1 and 'ro' in workspace[0]['options'] and
         'rw' not in workspace[0]['options'] and
         not any(r['mountpoint'].startswith('/workspace/') for r in parsed),
         'CHILD_MOUNTINFO_RO_NO_NESTED_BIND')
    need(type(selected_token) is str and len(selected_token) == 32 and
         all(c in '0123456789abcdef' for c in selected_token) and
         parent_absent_at_ready is True and
         ready == {'schema':'context-child-ready/v1',
                   'attempt':selected_token,
                   'out':selected['logical_output_root'],
                   'original_guard_sha256':GUARD_SHA,
                   'output_absent':True},
         'ORIGINAL_READY_BEFORE_PARENT_WRITER')
    need(sentinel == {'path':'/workspace/'+selected['context_role']+'/.readonly-sentinel',
                      'attempted_create':True,'errno':30,'created':False},
         'CHILD_EROFS_WRITE_SENTINEL')
    need(type(ack) is dict and set(ack) ==
         {'leaf','ordinal','sha256','parent_fsync_readback_sha256',
          'ack_received','child_post_ack_readback_sha256'} and
         ack['leaf'] == 'request.json' and ack['ordinal'] == 1 and
         type(ack['sha256']) is str and len(ack['sha256']) == 64 and
         all(c in '0123456789abcdef' for c in ack['sha256']) and
         ack['parent_fsync_readback_sha256'] == ack['sha256'] and
         ack['child_post_ack_readback_sha256'] == ack['sha256'] and
         ack['ack_received'] is True,
         'PARENT_WRITE_ACK_CHILD_READBACK_JOIN')
    return {'status':'SYNTHETIC_MOUNT_VECTOR_OBSERVATIONS_ONLY',
            'actual_namespace_observed':False,'docker_effect':False,
            'nested_child_writable_output_bind':False}


def stage_or_mount_effect(*_args,**_kwargs):
    raise Refused('EFFECT_DISABLED_NO_STAGE_OR_DOCKER_MOUNT')


def run_public_namespace_probe(*_args,**_kwargs):
    raise Refused('EFFECT_DISABLED_NO_REAL_NAMESPACE_PROBE')


def issue_auth_key_policy_or_cleanup(*_args,**_kwargs):
    raise Refused('EFFECT_DISABLED_NO_AUTH_KEY_POLICY_OR_CLEANUP')
