"""One-shot no-replace baseline capture after the separately recorded root claim."""
import collections
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import _sqlite3

import baseline_guard as guard

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
PLAN = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/acceleration-audit-20261018/implementation-plan-0001'
S = ROOT / 'implementation/lab-runtime/candidates/runtime-completion-0001'
E = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U01-01'


def binding(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'size_bytes': path.stat().st_size}


def encode(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()


def main():
    pre = guard.load(E / 'preflight.json')
    guard.verify_bindings(ROOT, pre['selected_inputs'])
    for name in ('S', 'E'):
        guard.verify_root(ROOT / pre['root_paths'][name], pre['created_root_witnesses'][name])
    guard.absent(ROOT / pre['root_paths']['I'])
    dag = guard.load(ROOT / 'docs/plans/0011-lab-runtime-completion/dag.json')
    cross = guard.load(ROOT / 'docs/plans/0011-lab-runtime-completion/obligation-crosswalk.json')
    state = guard.load(ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/execution-state.json')
    if (len(dag['nodes']), len(dag['edges']), len(cross['tasks']), len(cross['original_units'])) != (36, 73, 46, 63):
        guard.fail('original obligation accounting drift')
    task_status = {k: {'status': v['status'], 'claim_ceiling': v.get('claim_ceiling', 'Original task-local accepted evidence only; no new runtime qualification or broader completion inferred.')}
                   for k, v in state['task_states'].items()}
    if len(task_status) != 36 or {k for k, v in task_status.items() if v['status'] == 'complete'} != {'T00', 'T01', 'T04'}:
        guard.fail('accepted task status drift')
    versions = dict(pre['toolchain'])
    tools = []
    for tool in ('rustc', 'cargo'):
        proxy = shutil.which('rustup')
        if not proxy:
            versions[tool]['actual_binary'] = {'status': 'unavailable', 'claim_ceiling': 'Proxy observation only, insufficient for compiler selection.'}
            continue
        args = [proxy, 'which', tool]
        result = subprocess.run(args, cwd=ROOT, capture_output=True, timeout=30,
                                env=dict(os.environ, RUSTUP_AUTO_INSTALL='0'))
        tools.append({'argv': args, 'returncode': result.returncode, 'stdout': result.stdout.decode().strip(), 'stderr': result.stderr.decode().strip()})
        if result.returncode != 0:
            versions[tool]['actual_binary'] = {'status': 'unavailable', 'claim_ceiling': 'Proxy observation only, insufficient for compiler selection.'}
        else:
            path = Path(result.stdout.decode().strip()).resolve(strict=True)
            versions[tool]['proxy_identity_only'] = True
            versions[tool]['actual_binary'] = {'status': 'observed', 'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'size_bytes': path.stat().st_size}
    versions['sqlite']['extension'] = {'path': _sqlite3.__file__, 'sha256': hashlib.sha256(Path(_sqlite3.__file__).read_bytes()).hexdigest()}
    packages = {}
    for name in ('jsonschema', 'cryptography', 'referencing'):
        try:
            packages[name] = {'version': importlib.metadata.version(name), 'selected_for_this_unit': False}
        except importlib.metadata.PackageNotFoundError:
            packages[name] = {'status': 'unavailable', 'selected_for_this_unit': False}
    versions['ambient_packages'] = packages
    versions['runtime_dependency_claim'] = 'This unit uses standard-library Python only. Ambient packages are observations, not selected replacements for the pinned audit environment. Native runtime ABI/dependency closure is not qualified.'
    status_command = ['git', '--no-optional-locks', 'status', '--porcelain=v1', '-z', '--untracked-files=all']
    status = subprocess.run(status_command, cwd=ROOT, capture_output=True, check=True, timeout=120)
    dirty = {'sha256': hashlib.sha256(status.stdout).hexdigest(), 'byte_length': len(status.stdout),
             'raw_metadata_retained': False, 'privacy': 'Digest of Git status/path metadata only, never file bodies; filenames not persisted.',
             'claim_ceiling': 'Metadata drift signal only, not integrity proof for unrelated dirty bytes.'}
    vfs = os.statvfs(ROOT)
    resources = {'logical_cpu_count': os.cpu_count(), 'load_average': list(os.getloadavg()),
                 'filesystem_available_bytes': vfs.f_bavail * vfs.f_frsize,
                 'physical_memory_bytes': os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES'),
                 'reservation': 'none', 'live_runtime_jobs_inspected': False,
                 'claim_ceiling': 'Host resource observations only; no lease/CPU/memory budget or live-service ownership asserted.'}
    tests = Path(__file__).parent
    helper_bindings = [binding(tests / x) for x in ('baseline_guard.py', 'test_baseline_guard.py', 'finalize_baseline.py')]
    paths = {'schema_version': 'lab-completion-authoring-path-reservations/v1', 'claim_id': pre['claim_id'],
             'unit': 'LC-U01-01', 'integration_owner': '/root', 'merge_and_freeze_owner': '/root',
             'implementer': '/root/architecture_review', 'roots': {}, 'write_scope': pre['unit_write_scope'],
             'reviewer_reserved_names': ['review.json', 'reviewer-*'], 'coordinator_reserved_names': ['coordinator-*'],
             'host_custody_qualified': False, 'cross_root_atomicity': False, 'authority_effect': 'none',
             'cleanup': 'No inherited state is owned. Do not delete claimed roots on ambiguous/foreign attachment. Test cleanup is restricted to newly created owned-case-* trees. No installation, private scratch, credential, source-family or rollback dependency was created.'}
    for name in ('S', 'E'):
        paths['roots'][name] = {'path': pre['root_paths'][name], 'state': 'created-no-replace-local-authoring', 'identity': pre['created_root_witnesses'][name]}
    paths['roots']['I'] = {'path': pre['root_paths']['I'], 'state': 'logical-reservation-only', 'created': False,
                           'os_exclusion_claimed': False, 'before_installation': 'Recheck absence, current selected authority and exact no-replace write envelope.'}
    # No data file is created until all exact source/tool/ownership preconditions finish.
    guard.verify_bindings(ROOT, pre['selected_inputs'])
    guard.verify_bindings(ROOT, helper_bindings)
    for name in ('S', 'E'):
        guard.verify_root(ROOT / pre['root_paths'][name], pre['created_root_witnesses'][name])
    guard.absent(ROOT / pre['root_paths']['I'])
    head = subprocess.run(['git', '--no-optional-locks', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, check=True, timeout=10).stdout.decode().strip()
    if head != pre['git_head']:
        guard.fail('HEAD drift')
    fd = guard.open_directory(S / 'control')
    try:
        guard.exclusive_file(fd, 'paths.json', encode(paths))
        base = {'schema_version': 'lab-completion-authoring-baseline/v1', 'selection_kind': 'code',
                'selection_id': 'LC-U01-01/baseline/0001', 'captured_at_unix': time.time(), 'git_head': head,
                'unit': 'LC-U01-01', 'integration_owner': '/root', 'implementer': '/root/architecture_review',
                'selected_inputs': pre['selected_inputs'], 'paths_binding': binding(S / 'control' / 'paths.json'),
                'preflight_binding': binding(E / 'preflight.json'), 'implementation_helpers': helper_bindings,
                'toolchain': versions, 'resources': resources, 'dirty_metadata_before': pre['dirty_metadata_before'],
                'dirty_metadata_after_claim': dirty, 'original_accounting': {'tasks': 36, 'edges': 73, 'original_task_bodies': 46, 'original_swu_bodies': 63},
                'original_task_states': task_status, 'status_counts': dict(collections.Counter(v['status'] for v in task_status.values())),
                'baseline_source': 'Current API30 public file inventory plus exact accepted design/plan inputs; historical API16 planning selection remains historical, never silently repinned.',
                'permitted_scope': 'Reversible inert authoring in a separately selected unit write manifest only.',
                'dispatch_guard': 'Run baseline_guard.py against this immutable baseline, verify its detached accepted hash, unit inputs and current exact write scope before dependent dispatch. Any selected drift requires a separately reviewed successor; never rewrite or automatically repin this file.',
                'runtime_eligible': False, 'family_selected': False, 'host_activation_selected': False, 'authority_effect': 'none',
                'independent_acceptance': 'Not supplied by implementer; reviewer creates a separate immutable record binding this file.',
                'remaining_original_obligations': ['No new original T00/T15/T24 acceptance.', 'Native runtime ABI, protected scratch, leases, grants, live-job/custody ownership, complete execution closure and actual runtime budget remain later unit/gate obligations.', 'No original ledger status, frozen source or rollback state changed.']}
        guard.exclusive_file(fd, 'baseline.json', encode(base))
    finally:
        os.close(fd)
    fd = guard.open_directory(E)
    try:
        guard.exclusive_file(fd, 'toolchain-resolution.json', encode({'commands': tools, 'claim_ceiling': versions['runtime_dependency_claim']}))
        guard.exclusive_file(fd, 'capture-terminal.json', encode({'result': 'CAPTURED-REVIEW-PENDING', 'baseline_binding': binding(S / 'control' / 'baseline.json'), 'paths_binding': binding(S / 'control' / 'paths.json'), 'I_created': False, 'source_postcheck': guard.verify_current(ROOT, S / 'control' / 'baseline.json'), 'authority_effect': 'none'}))
    finally:
        os.close(fd)
    print(json.dumps({'result': 'CAPTURED-REVIEW-PENDING', 'selected_inputs': len(pre['selected_inputs']), 'I_created': False}))


if __name__ == '__main__':
    main()
