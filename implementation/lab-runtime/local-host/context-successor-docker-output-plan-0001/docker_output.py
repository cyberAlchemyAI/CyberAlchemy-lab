"""Effect-disabled Context Docker/output contract for the durable successor.

All selected predecessors are public static designs. Actual Mapper, issued AUTH,
physical stage, Context source manifest, private JIT, and output are absent.
"""
from __future__ import annotations

import hashlib
import os
import stat
import types
from pathlib import Path

LOCAL = Path('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host')
STAGE_JIT = LOCAL / 'context-successor-stage-jit-release-plan-0002/release_plan.py'
STAGE_JIT_FREEZE = LOCAL / 'context-successor-stage-jit-release-plan-0002/freeze.json'
STAGE_JIT_REVIEW = LOCAL / 'CONTEXT-SUCCESSOR-STAGE-JIT-RELEASE-PLAN-INDEPENDENT-STATIC-REVIEW-0002.md'
FINAL_FREEZE = LOCAL / 'context-successor-final-stage-0002/freeze.json'
FINAL_REVIEW = LOCAL / 'CONTEXT-SUCCESSOR-FINAL-STAGE-INDEPENDENT-STATIC-REVIEW-0002.md'
JIT_FREEZE = LOCAL / 'context-successor-jit-0002/freeze.json'
JIT_REVIEW = LOCAL / 'CONTEXT-SUCCESSOR-JIT-INDEPENDENT-STATIC-REVIEW-0002.md'
RUNNER = LOCAL / 'context-docker-runner-0001/runner.py'
CHILD = LOCAL / 'context-docker-runner-0001/child.py'
BRIDGE = LOCAL / 'context-docker-runner-0001/wire_bridge.py'
RUNNER_FREEZE = LOCAL / 'context-docker-runner-0001/freeze.json'
RUNNER_REVIEW = LOCAL / 'CONTEXT-DOCKER-RUNNER-INDEPENDENT-STATIC-REVIEW-0001.md'
VALIDATOR = LOCAL / 'context-output-validator-0003/validator.py'
VALIDATOR_FREEZE = LOCAL / 'context-output-validator-0003/freeze.json'
VALIDATOR_REVIEW = LOCAL / 'CONTEXT-OUTPUT-VALIDATOR-INDEPENDENT-STATIC-REVIEW-0003.md'
FINALIZATION = LOCAL / 'context-docker-release-0001/finalization.py'
OBSERVER = LOCAL / 'context-docker-release-0001/observer.py'
RELEASE_FREEZE = LOCAL / 'context-docker-release-0001/freeze.json'
RELEASE_REVIEW = LOCAL / 'CONTEXT-DOCKER-RELEASE-INDEPENDENT-STATIC-REVIEW-0001.md'
PINS = {
    STAGE_JIT:'1e403bdee4eb38da88ca8463e607ba923965117d48dc3419b60f6a000cc9c090',
    STAGE_JIT_FREEZE:'8569cfc5593de49ebe19484cc25b64a78f04250175a3833c46d5471d8d37e17f',
    STAGE_JIT_REVIEW:'08cbff29bdebc93b63d2cf4930a0bfcca5fb24f80ec37cc474f9dd0d9aa8840d',
    FINAL_FREEZE:'4ba5f738e432f7dda855f0bab57de0495ae1105da1e8650e15864c5d2a81536f',
    FINAL_REVIEW:'1da3d7a361be23b81b6ea665cac07b29d110ea25aead6c422476010bb9b31404',
    JIT_FREEZE:'06501e59f66afcec5ff360750bec142b7293abdcb82d418f4800d9fd965b6136',
    JIT_REVIEW:'5a01e697c80beb877777c8c722d1c027922924ebab44ec5c8546add6a96cc081',
    RUNNER:'7140f6885b5bc3f796bbe46aaad8813ab3443de7c19a407503ce27417afbc0c5',
    CHILD:'e7ebb4697d8afebd11b6eaaa0af76830ae201c5caf4c9327897167045acc8dcc',
    BRIDGE:'87980dfe8eb563bb89702010f1ecf43c99601cf546d2a6bb01fa0b7621080884',
    RUNNER_FREEZE:'81781565789819c18f85b13c602069b37573b4e0f4a23f4f15c312b3dd3da5bc',
    RUNNER_REVIEW:'da5b2d752cbebe4f41899af0334303b0e53ce4d6cefe2b0616a63eb531099372',
    VALIDATOR:'44f041ad716af570c2378eb0b0493b85dbf48a0151baeb7a52366dc014bd99d9',
    VALIDATOR_FREEZE:'3d061e574afc23f3e348a40e092e1f574e37a899097b656d25a57c87434c4a24',
    VALIDATOR_REVIEW:'c53de6056345e0e225ae1132140b5d6abafaffaf45543a6e989e0e4060647fa5',
    FINALIZATION:'69db06649848eeff8b51a69d2a1bdbb9f2d7fe0d7f5d09722b80eab8404d9bb4',
    OBSERVER:'37b7285de216377413bfce52dc80be8ed6039a46e6803f4b129ad46d42bf7c64',
    RELEASE_FREEZE:'f95ef5db94679793de5cf75578ef36b378f645245d27bf336f549ed1431aaab7',
    RELEASE_REVIEW:'5fa567d1e9ea1b63e85b86d89f1435754666f51ce8cbaae514caf002bbc24e94',
}
CONTEXT_ROLE = 'product/lab/release-candidates/v1/interface/docker-context-20261020-0002'
IMAGE = 'sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874'
NATIVE_SHA = 'fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'
EFFECT_ENABLED = False
MAX_LEAF = 65536
MAX_TOTAL = 2 * 1024 * 1024
CAPTURE_COMBINED = 8192


class Refused(ValueError):
    pass


def need(ok, reason):
    if not ok:
        raise Refused(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pin(path):
    need(path in PINS, 'UNSELECTED_ORIGINAL_PREIMAGE')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
             0 < before.st_size <= 2*1024*1024, 'ORIGINAL_PREIMAGE_SHAPE')
        raw = os.read(fd,before.st_size+1)
        after = os.fstat(fd)
        need(len(raw) == before.st_size and
             (before.st_dev,before.st_ino,before.st_mode,before.st_size) ==
             (after.st_dev,after.st_ino,after.st_mode,after.st_size) and
             sha(raw) == PINS[path], 'ORIGINAL_PREIMAGE_DRIFT')
        return raw
    finally:
        os.close(fd)


def module_from_pinned(name,path):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(pin(path),str(path),'exec'),module.__dict__)
    return module


def originals():
    for path in PINS:
        pin(path)
    runner = pin(RUNNER)
    bridge = module_from_pinned('cal_context_original_bridge_selected',BRIDGE)
    validator = module_from_pinned('cal_context_original_validator_selected',VALIDATOR)
    need(tuple(bridge.LEAVES) == tuple(validator.LEAVES) and
         len(bridge.LEAVES) == 40 and
         tuple(bridge.LEAVES[4:34]) == tuple(f'artifacts/{i:02d}.json' for i in range(30)) and
         bridge.LEAVES[38:] == ('build-result.json','manifest.json') and
         bridge.MAX_LEAF == validator.MAX_LEAF == MAX_LEAF and
         bridge.MAX_TOTAL == validator.MAX_TOTAL == MAX_TOTAL and
         b"self.exchange('RELEASE_PRIVATE', 38)" in pin(BRIDGE) and
         b"self.exchange('FINISH', 41)" in pin(BRIDGE) and
         b"len(manifest['files']) == 39" in pin(VALIDATOR) and
         b"def launch(*_args, **_kwargs):" in pin(VALIDATOR) and
         b"raise RuntimeError('DOCKER_CONTEXT_EFFECT_DISABLED')" in runner and
         b"B.need(EFFECT_ENABLED is True, 'DOCKER_CONTEXT_EFFECT_DISABLED')" in runner and
         b"--userns', 'host'" in runner and b"--read-only'" in runner and
         b"--network', 'none'" in runner and
         b"def execute(*args, **kwargs):" in pin(OBSERVER),
         'ORIGINAL_ROLE_EMIT_RELEASE_FINISH_VALIDATOR_CONTRACT')
    validator.integration()
    return bridge, validator


def project_inert_controller():
    """Exact one-span successor rebind; returned bytes are never written/run."""
    runner = pin(RUNNER)
    child = pin(CHILD)
    old_role = b'docker-context-20261020-0001'
    new_role = b'docker-context-20261020-0002'
    old_name = b'cal-context-docker-runner-0001'
    new_name = b'cal-context-successor-20261020-0002'
    need(runner.count(old_role) == child.count(old_role) == 1 and
         runner.count(old_name) == 1 and
         new_role not in runner and new_role not in child and
         new_name not in runner,
         'ORIGINAL_CONTROLLER_PROJECTION_SPAN')
    projected_runner = runner.replace(old_role,new_role).replace(old_name,new_name)
    projected_child = child.replace(old_role,new_role)
    need(projected_runner.replace(new_role,old_role).replace(new_name,old_name) == runner and
         projected_child.replace(new_role,old_role) == child and
         b'EFFECT_ENABLED = False' in projected_runner and
         b"raise RuntimeError('DOCKER_CONTEXT_EFFECT_DISABLED')" in projected_runner and
         b'synthetic_public_body' in projected_child,
         'INERT_CONTROLLER_INVERSE_AND_REFUSAL')
    compile(projected_runner,'successor-inert-runner.py','exec',optimize=0)
    compile(projected_runner,'successor-inert-runner.py','exec',optimize=2)
    compile(projected_child,'successor-inert-child.py','exec',optimize=0)
    compile(projected_child,'successor-inert-child.py','exec',optimize=2)
    return projected_runner,projected_child


def plan(now=None):
    bridge, validator = originals()
    projected_runner, projected_child = project_inert_controller()
    stage_jit = module_from_pinned('cal_context_stage_jit_reviewed_0002',STAGE_JIT)
    prior = stage_jit.plan(now)
    need(prior['status'] == 'WAIT_OUTSIDE_PINNED_MAPPER_EFFECT' and
         prior['mapper_source_rows_required'] == 953 and
         prior['bound_rows_after_mapper'] == 1570 and
         prior['final_rows_after_issued_auth'] == 1571 and
         prior['authorization'] == 'UNMINTED' and
         prior['stage_copy'] == 'REFUSED' and
         prior['docker_effect'] == 'REFUSED' and
         prior['protected_archive']['body'] == 'UNOPENED' and
         prior['cleanup_requirement'] ==
         'TERMINAL_OUTPUT_EXTERNAL_OS_AND_DOCKER_ABSENCE_VERIFIED_FIRST',
         'FRESH_STAGE_JIT_GATE')
    topology = prior['topology']
    stage_root = Path(topology['stage_root'])
    need(stage_root.is_absolute() and '/tmp/' not in str(stage_root) and
         Path(topology['private_root']).is_absolute() and
         '/tmp/' not in topology['private_root'], 'DURABLE_SUCCESSOR_PATHS')
    physical_here = stage_root / CONTEXT_ROLE
    logical_here = Path('/workspace') / CONTEXT_ROLE
    return {'status':'WAIT_MAPPER_STAGE_AUTH_AND_CONTEXT_SOURCE',
            'effect_enabled':False,
            'source_period_sha256':prior['source_period_sha256'],
            'mapper_review':'UNSELECTED',
            'physical_stage_files_required':1571,
            'authorization':'UNMINTED','context_source_manifest':'UNCREATED',
            'physical_output_root':str(physical_here/'packages/0001'),
            'logical_output_root':str(logical_here/'packages/0001'),
            'output_parent_access':'HOST_WRITER_RW_CHILD_WORKSPACE_RO',
            'docker_image':IMAGE,'native_sha256':NATIVE_SHA,
            'context_role':CONTEXT_ROLE,
            'proposed_docker_name':'cal-context-successor-20261020-0002',
            'inert_controller_sha256':sha(projected_runner),
            'inert_child_sha256':sha(projected_child),
            'controller_projection':'IN_MEMORY_SYNTHETIC_ONLY_NOT_RUNNABLE_REAL_CONTEXT',
            'context_build_control':'PROJECTED_GUARDED_ROLES_PENDING_MAPPER',
            'output_leaves':list(bridge.LEAVES),
            'output_leaf_count':40,'manifest_member_rows':39,
            'emit_ordinals':list(range(1,41)),
            'writer_private_release_ordinal':38,
            'writer_private_release_scope':'EMPTY_WRITER_SCRATCH_ONLY_NOT_JIT_PRIVATE_ROOT',
            'finish_ordinal':41,'wire_request_count':42,
            'max_leaf_bytes':MAX_LEAF,'max_total_output_bytes':MAX_TOTAL,
            'max_combined_stdout_stderr_bytes':CAPTURE_COMBINED,
            'validator':'SYNTHETIC_CONTRACT_ONLY_REAL_OUTPUT_PENDING',
            'terminal_required':{'os_exit':0,'daemon_exit':0,'stderr':'EMPTY',
                'cid_absent':True,'name_absent':True,'writer_closed':True,
                'mediator_joined':True,'postclose_readback':True,
                'external_observer':'REQUIRED'},
            'uncertainty':'UNKNOWN_PRESERVE_MARKER_OUTPUT_PRIVATE_EVIDENCE_NO_RETRY',
            'docker':'REFUSED','context':'REFUSED','cleanup':'REFUSED'}


def structural_manifest_rows(rows):
    """Fixture-only logical-to-physical row map; no body/receipt validation."""
    current = plan()
    leaves = current['output_leaves'][:-1]
    logical = current['logical_output_root']
    physical = current['physical_output_root']
    need(type(rows) is list and len(rows) == 39 and
         all(type(row) is dict and set(row) == {'path','sha256'} and
             row['path'] == logical+'/'+leaf and
             type(row['sha256']) is str and len(row['sha256']) == 64 and
             all(c in '0123456789abcdef' for c in row['sha256'])
             for row,leaf in zip(rows,leaves)),
         'STRUCTURAL_39_LOGICAL_ROWS_ONLY')
    return {'status':'STRUCTURAL_39_ROW_PROJECTION_ONLY',
            'physical_rows':[{'path':physical+'/'+leaf,'sha256':row['sha256']}
                             for row,leaf in zip(rows,leaves)],
            'real_output_validated':False}


def select_mapper_stage_or_auth(*_args,**_kwargs):
    raise Refused('OUTSIDE_MAPPER_AND_FRESH_1571_STAGE_NOT_SELECTED')


def issue_auth_or_write_policy(*_args,**_kwargs):
    raise Refused('EFFECT_DISABLED_NO_AUTH_KEY_POLICY')


def run_docker_or_context(*_args,**_kwargs):
    raise Refused('EFFECT_DISABLED_NO_DOCKER_OR_CONTEXT')


def validate_real_output_or_cleanup(*_args,**_kwargs):
    raise Refused('EFFECT_DISABLED_NO_REAL_OUTPUT_OR_CLEANUP')
