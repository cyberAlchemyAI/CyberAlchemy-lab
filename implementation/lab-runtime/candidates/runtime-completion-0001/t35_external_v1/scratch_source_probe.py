"""Disposable historical Source builder probe; never a production effect gate.

The selected repository inputs are copied by exact digest to a sparse snapshot.
Only that snapshot and a disposable output tree enter the bubblewrap namespace.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import selectors
import signal
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import tempfile
import time

from . import constructor_paths, role_stage
from .hardener import harden
from .held_paths import HeldCanonicalDirectory, _parse_closed
from .path_contract import check_binding, require

REPO = Path('/home/vlad_/projects/CyberAlchemy-lab')
INTERFACE = role_stage.INTERFACE
PREDECESSOR_MANIFESTS = (
    INTERFACE / 'legacy-session-fixture-source-v1-action-0148/source-manifest.json',
    INTERFACE / 'current-participation-v5/source-manifest.json',
    INTERFACE / 'current-participation-v5/packages/0001/manifest.json',
)
PREDECESSOR_SHA = (
    'f3cbec21c32dce3938460a1203e6e3f3575608f463aa3f3fffae9f9338a798f2',
    'dc0462ce29d24bf571b56c0c0eeafad0511812a8464ce66e52914671256e7cb4',
    '8c34a37e1dfa185fc21f323aa08d99c4f097b413c3e0fcf90c0da6d98c731aaf',
)
EXTRA_INPUTS = (
    INTERFACE / 'legacy-session-fixture-source-v1-action-0148/episode-contract.json',
    INTERFACE / 'current-participation-v5/episode-contract.json',
    INTERFACE / 'current-participation-v5/packages/0001/period.json',
    PurePosixPath('docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'),
    INTERFACE / 'custody-correction-v4/engine-manifest.json',
    INTERFACE / 'custody-correction-v4/pins.json',
    INTERFACE / 'custody-correction-v4/loader.py',
    INTERFACE / 'custody-correction-v4/reader_adapter.py',
)
EXTRA_SHA = (
    'bc6acaa6022791ea102ced5b1dfc8621403f8e5e557a937765e187a90d887055',
    '73c2afe2663bb80da0cf3a8f52a2951346a47dcefb34c8c04ac05ca1e37f4559',
    '5d2184e3491509b6c8d15939d97c6f95609d5277c61bb8f3f0bbd911ff3f35e3',
    '4d3c34a7f19b4b47892b3fbf5673544b36b0517e516961adcc77722f5d08e906',
    '329403eb89eb989a834cba02c7fb09f920d328e8ecdca9a0880660b1e97cbcaa',
    'd59fc534f60483fe9df93b2e6d45431d00ccec082332fbf4e76a91b0944e6b4d',
    'f1953bf08d36756810fbc7ec051df5d0e362f745e84644223b9dddd0df1b13ef',
    '6f57bf712f09ce162754cd5515432b3f99cc2191b021b271987e37bb19cb3f41',
)
SCHEMA_REFERENCE_SHA = {
    'tooling/schemas/ctx01/v1/schema.json': 'a82455314d7e9007b09c3ba47ce64cb8bb6e1115ba1c8ce3be4a132d428c2075',
    'tooling/schemas/ctx07/v2/schema.json': 'e15aee32c5781ca0d25c9c6c4e5c58caab5a5f5f286b6389298d18c2208696ec',
}
PROFILE_IMPLEMENTATION_SHA = {
    'docs/decisions/0074-governance-transaction-surface-admission/apply.py': '7f048a9c56d6b57d69ec3bd41a1e46cb4d78e02471ddf90ae46f943202a89f67',
    'authority/governance/candidates/0001-three-lens-module/project.py': 'c88e8db7ea77b4a3255c826365fbe7d610be098c8656e5c186ba891f403edc32',
    'ontology-lifecycle/runtime-candidates/cal-ontology-graph-read-model/v1/README.md': '30fe8dcb3fbbaaf7baf5fbe74237a0b5caa73231962874427e51ff5703cef3e6',
    'implementation/lab-runtime/v1/lab.py': '723014efe775ee18a493991fe8859b40cdacc403284e7d6ff4cba4cb6187b054',
}
MAPPING_PROPOSAL = {
    'path': 'implementation/lab-runtime/candidates/repeatable-operation/design/contract-impact.json',
    'sha256': 'c0f69674bd37802c669a29fff208232549a3bcfdd28673fc1999c074ad82396a',
}
HISTORICAL_SOURCE_PACKAGE = {
    'path': str(INTERFACE / 'legacy-session-fixture-source-v1-action-0148/packages/0001/manifest.json'),
    'sha256': '8e7b675666308e0e73fb23962b310ea3a89baa48ad6bf2c9cf1c5c9ce9e96964',
}
ROLE_TEMPLATE_SHA = {
    'product/lab/release-candidates/v1/interface/legacy-session-fixture-source-v1-action-0148/__init__.py': 'a3e7a2b9ec2c69a93c8ace06aa927816972435789274c10ffe8e0f32a542e6ed',
    'product/lab/release-candidates/v1/interface/legacy-session-fixture-source-v1-action-0148/base.py': 'b4b0e65b2d547ffc57a4345094fbdcf467a588cb2c9bda4bd1d01c6046037195',
    'product/lab/release-candidates/v1/interface/legacy-session-fixture-source-v1-action-0148/build.py': 'bedfe45b3d5f7c8dcc8a7c480f92d896afa9d665975acc459bd22e142455d96b',
    'product/lab/release-candidates/v1/interface/legacy-session-fixture-source-v1-action-0148/cold.py': '5dbdad7f2511168d65fe73ba34a8d677ac64d4c98c171e5044f6f1e4685a3ee3',
    'product/lab/release-candidates/v1/interface/legacy-session-fixture-source-v1-action-0148/records.py': '083134095603c6f070dbffcb28f6de9e8d4db73a8dbe27b692656c44f862e7ea',
    'product/lab/release-candidates/v1/interface/legacy-session-fixture-reader-v1-action-0148/__init__.py': '1b88f99e5c0621338bf462d41cb54effcf2ec08cba8884fdf8dedc6179709529',
    'product/lab/release-candidates/v1/interface/legacy-session-fixture-reader-v1-action-0148/adapter.py': '85646307fa07c768105258ef0d49226b2d06fc70af3e5993fb2f58ca2124c399',
    'product/lab/release-candidates/v1/interface/legacy-session-fixture-reader-v1-action-0148/base.py': 'd677d3ab9ff523c07404ab95e3a77509b0a016323d4b8a0cd8c2c1f42e8c7d39',
    'product/lab/release-candidates/v1/interface/legacy-session-fixture-reader-v1-action-0148/eligibility.py': '5d16158070ddfcdc026a59390041b11db39556435754f67623390c0bc6d4c2ba',
    'product/lab/release-candidates/v1/interface/legacy-session-fixture-reader-v1-action-0148/inspection.py': '49770bd3c1f3c873840545a09f4ac207371b510b29e38f11a0523e0acb81cc11',
    'product/lab/release-candidates/v1/interface/legacy-session-fixture-reader-v1-action-0148/model.py': '687f42b643cfadaa2c9782cd1630c3ae26fff03c37d5f10ab2e9e0da4c8e70c7',
    'product/lab/release-candidates/v1/interface/legacy-session-fixture-reader-v1-action-0148/reader.py': 'f93a1f218238c05b18a7c355f9bc1363bbf42d2b1d442d03e191e121f8e9c9b9',
    'product/lab/release-candidates/v1/interface/legacy-session-fixture-mapped-v2-action-0148/__init__.py': 'a88e78979e6f4ddfaf89055996e294a92987e42ca63526252a56defb8bc05362',
    'product/lab/release-candidates/v1/interface/legacy-session-fixture-mapped-v2-action-0148/base.py': '02f0481cb20dd81c5e4b6228ce4657987d8960ea9930893434b364a48f5b12ad',
    'product/lab/release-candidates/v1/interface/legacy-session-fixture-mapped-v2-action-0148/build.py': 'dced09f9432318ef286475081ea5f4f7e6fa633c7cefbd9db76c0ec3c47ecbbb',
    'product/lab/release-candidates/v1/interface/legacy-session-fixture-mapped-v2-action-0148/policy.json': '1c2ddd360e56666fec0f4ff2095f32369705cff7b96edecbc5ba0720136457ab',
    'product/lab/release-candidates/v1/interface/legacy-session-fixture-context-v1-action-0148/__init__.py': '51b5ebb11220f544d54359ab3e92c27d47d92635a9c2f44f9ba9ecceb7a74925',
    'product/lab/release-candidates/v1/interface/legacy-session-fixture-context-v1-action-0148/base.py': 'a2ba4ff87d48c03d821d6168204e4efdc75d6d76cd8771b581e3bb29e23eb402',
    'product/lab/release-candidates/v1/interface/legacy-session-fixture-context-v1-action-0148/build.py': '072a06b8b93ea301ab433389448c70ddab437c494316cac223d36c2ac46137b3',
    'product/lab/release-candidates/v1/interface/legacy-session-fixture-context-v1-action-0148/control.py': '088412f6eb37ab05c1ea86c1f0caf51ea257743585c67ec897df8c0a1a15ea49',
    'product/lab/release-candidates/v1/interface/legacy-session-fixture-context-v1-action-0148/generation.py': '1603cd607ab7eb82d1d434ce9e1fd8238985a48595ecad3f303557f4276190fb',
    'product/lab/release-candidates/v1/interface/legacy-session-fixture-context-v1-action-0148/lifetime-policy.json': '57f1a7b4757b551aefd05ed6efeada6ce416988d14b3aab73a4119f2b3f31e4a',
    'product/lab/release-candidates/v1/interface/legacy-session-fixture-context-v1-action-0148/protocols/evidence-contract.json': 'a2a07253f1c19bfe2d789d046516eee770cad3fa674ad7be8b9b523b1aac81d2',
    'product/lab/release-candidates/v1/interface/legacy-session-fixture-context-v1-action-0148/protocols/failure-boundary.json': 'eab4efdf032d65b96f62fc7bd1e91c9ff06543099f3bbd37bd8fe24482a77e58',
    'product/lab/release-candidates/v1/interface/legacy-session-fixture-context-v1-action-0148/protocols/input-contract.json': '1fca3d81b5977f80ecf27aeb0e99b25bcc4447ab9a92e85c2ba8b2deeb61f4fb',
    'product/lab/release-candidates/v1/interface/legacy-session-fixture-context-v1-action-0148/protocols/output-contract.json': '7deef2d3248d8bc59fd419696af33700b427c0b9e71bc99c1aba463fae42823e',
    'product/lab/release-candidates/v1/interface/legacy-session-fixture-context-v1-action-0148/protocols/policy.json': 'a0e3b1ec5b719b8291b7ceb6a261612a722e9a72b0cbf569e100ebee9c243fa2',
}
BWRAP = Path('/usr/bin/bwrap')
BWRAP_SHA = '523da3e7399044be5163aee6f57a77a6bef7454376e28f0a0627920bae1b76b6'
SANDBOX_RUNNER = '''import hashlib,importlib.util,json,os,sys
from pathlib import Path
for forbidden in ('/home/vlad_','/var/lib/cyberalchemy-lab','/run/cyberalchemy-lab'):
    if Path(forbidden).exists():raise RuntimeError('forbidden host root visible in scratch namespace')
sys.path.insert(0,'/work/snapshot')
family=Path('/work/out/legacy-fixture-source')
spec=importlib.util.spec_from_file_location('_t35_scratch_source',family/'source/__init__.py',submodule_search_locations=[str(family/'source')])
module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
build=__import__(spec.name+'.build',fromlist=['main'])
pin=hashlib.sha256((family/'source/source-manifest.json').read_bytes()).hexdigest()
build.main(pin)
print(json.dumps({'sandbox_host_checkout_absent':True,'sandbox_protected_roots_absent':True,'source_package_manifest_sha256':hashlib.sha256((family/'source/packages/0001/manifest.json').read_bytes()).hexdigest()}),flush=True)
'''
SCRATCH_BRIDGE = '''"""Fixture-only selected input reader inside isolated scratch namespace."""
import functools,hashlib,json,os,stat
from pathlib import Path,PurePosixPath
SNAPSHOT=Path('/work/snapshot')
FAMILY=Path('/work/out/legacy-fixture-source')
MANIFEST=FAMILY/'source/source-manifest.json'
STAGE=SNAPSHOT/'_t35_stage_selection.json'
MANIFEST_SHA='__SOURCE_MANIFEST_SHA__'
STAGE_SHA='__STAGE_SELECTION_SHA__'
def _sha(raw):return hashlib.sha256(raw).hexdigest()
def _parse(raw):
    def pairs(items):
        value={}
        for key,item in items:
            if key in value:raise ValueError('duplicate fixture selection key')
            value[key]=item
        return value
    return json.loads(raw,object_pairs_hook=pairs,
        parse_constant=lambda _:(_ for _ in ()).throw(ValueError('nonfinite fixture selection')))
@functools.lru_cache(maxsize=1)
def _selected():
    raw=MANIFEST.read_bytes()
    if _sha(raw)!=MANIFEST_SHA:raise ValueError('selected source manifest pin differs')
    value=_parse(raw)
    return {row['path']:row['sha256'] for row in value['files']}
@functools.lru_cache(maxsize=1)
def _stage():
    raw=STAGE.read_bytes()
    if _sha(raw)!=STAGE_SHA:raise ValueError('selected stage control pin differs')
    value=_parse(raw)
    return {row['path']:row['sha256'] for row in value}
def read(row):
    if type(row) is not dict or set(row)!={'path','sha256'}:raise ValueError('closed fixture binding required')
    name=row['path'];p=PurePosixPath(name)
    if type(name) is not str or p.as_posix()!=name or '..' in p.parts or '\\\\' in name:raise ValueError('noncanonical fixture input')
    if p.is_absolute():
        if FAMILY not in Path(name).parents:raise ValueError('external fixture read outside family')
        path=Path(name)
        stage=_stage().get(name)
        package=FAMILY/'source/packages/0001'
        package_reads={package/'artifacts'/('%02d.json'%i) for i in range(21)}
        if path!=MANIFEST and stage is None and path not in package_reads:
            raise ValueError('unselected family input')
        if stage is not None and (stage!=row['sha256'] or _selected().get(name)!=stage):
            raise ValueError('selected stage digest differs')
    else:
        if _selected().get(name)!=row['sha256']:raise ValueError('snapshot input not selected')
        path=SNAPSHOT/name
    if path.is_symlink() or any(a.is_symlink() for a in path.parents):raise ValueError('symlink fixture input')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        before=os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink!=1 or before.st_size>32*1024*1024:
            raise ValueError('nonregular or linked fixture input')
        raw=bytearray()
        while len(raw)<before.st_size:
            chunk=os.read(fd,min(1024*1024,before.st_size-len(raw)))
            if not chunk:raise ValueError('truncated fixture input')
            raw.extend(chunk)
        after=os.fstat(fd);attached=path.stat(follow_symlinks=False)
        key=lambda x:(x.st_dev,x.st_ino,x.st_mode,x.st_uid,x.st_gid,x.st_nlink,x.st_size,x.st_mtime_ns,x.st_ctime_ns)
        if key(before)!=key(after) or key(before)!=key(attached) or _sha(raw)!=row['sha256']:
            raise ValueError('fixture input changed during held read')
        return bytes(raw)
    finally:os.close(fd)
def verify_inputs(rows,*,selected_external=()):
    if type(rows) is not list:raise ValueError('closed fixture rows required')
    external=[r for r in rows if r['path'].startswith('/')]
    if selected_external:
        if external!=list(selected_external):raise ValueError('external fixture rows not selected')
    elif any(_stage().get(r['path'])!=r['sha256'] or
             _selected().get(r['path'])!=r['sha256'] for r in external):
        raise ValueError('external stage rows not in exact source selection')
    for row in rows:read(row)
    return len(rows)
def run_native(*a,**k):raise RuntimeError('native execution unavailable in source-only probe')
'''


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _bind(path: Path, raw: bytes) -> dict:
    return {'path': path.as_posix(), 'sha256': _sha(raw)}


def _held_input(row: dict) -> bytes:
    check_binding(row, kind='source_api')
    path = REPO / row['path']
    with HeldCanonicalDirectory(str(path.parent)) as parent:
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC,
                     dir_fd=parent.fd)
        try:
            before = os.fstat(fd)
            require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
                    before.st_size <= 32 * 1024 * 1024,
                    'bounded single-link selected input required')
            raw = bytearray()
            while len(raw) < before.st_size:
                chunk = os.read(fd, min(1024 * 1024, before.st_size - len(raw)))
                require(bool(chunk), 'selected source truncated during read')
                raw.extend(chunk)
            after = os.fstat(fd)
            signature = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_uid,
                                   s.st_gid, s.st_nlink, s.st_size, s.st_mtime_ns,
                                   s.st_ctime_ns)
            attached = os.stat(path.name, dir_fd=parent.fd, follow_symlinks=False)
            require(signature(before) == signature(after) == signature(attached) and
                    parent.attached() and _sha(raw) == row['sha256'],
                    'selected input changed or detached during held read')
            return bytes(raw)
        finally:
            os.close(fd)


def _source_rows() -> tuple[dict[str, dict], dict[str, bytes]]:
    selected = {}
    captured = {}
    for manifest, pin in zip(PREDECESSOR_MANIFESTS, PREDECESSOR_SHA):
        row = {'path': str(manifest), 'sha256': pin}
        raw = _held_input(row)
        selected[manifest.as_posix()] = row
        captured[manifest.as_posix()] = raw
        value = _parse_closed(raw)
        for row in value['files']:
            check_binding(row, kind='source_api')
            old = selected.setdefault(row['path'], row)
            require(old == row, 'predecessor manifest input digest conflict')
    for item, pin in zip(EXTRA_INPUTS, EXTRA_SHA):
        row = {'path': str(item), 'sha256': pin}
        require(selected.setdefault(item.as_posix(), row) == row,
                'extra original input pin conflicts with predecessor')
    for path, pin in ROLE_TEMPLATE_SHA.items():
        row = {'path': path, 'sha256': pin}
        require(selected.setdefault(path, row) == row,
                'role template input pin conflicts with predecessor')
    require(selected.setdefault(HISTORICAL_SOURCE_PACKAGE['path'], HISTORICAL_SOURCE_PACKAGE) ==
            HISTORICAL_SOURCE_PACKAGE, 'original source package pin conflicts')
    engine_path = str(INTERFACE / 'custody-correction-v4/engine-manifest.json')
    engine = _parse_closed(_held_input(selected[engine_path]))
    parent = engine['parent_binding']
    for row in (parent, *engine['files'], engine['profile_binding'],
                engine['mapping_binding'], engine['correction_profile_binding']):
        check_binding(row, kind='source_api')
        require(selected.setdefault(row['path'], row) == row,
                'engine input conflicts with predecessor')
    parent_manifest = _parse_closed(_held_input(parent))
    for row in parent_manifest['files']:
        check_binding(row, kind='source_api')
        require(selected.setdefault(row['path'], row) == row,
                'engine parent input conflicts with predecessor')
    profile = _parse_closed(_held_input(engine['profile_binding']))
    require({item['path'] for item in profile['implementation_bindings']} ==
            set(PROFILE_IMPLEMENTATION_SHA),
            'profile implementation input set differs from pinned selection')
    for path, pin in PROFILE_IMPLEMENTATION_SHA.items():
        row = {'path': path, 'sha256': pin}
        require(selected.setdefault(path, row) == row,
                'profile implementation input conflicts')
    require(all(name in selected for name in profile['runtime_materials']),
            'profile runtime material outside pinned engine manifest')
    for root_binding in (*profile['roots'], *profile['operational_roots']):
        check_binding(root_binding, kind='source_api')
        require(selected.setdefault(root_binding['path'], root_binding) == root_binding,
                'profile root conflicts with predecessor')
        bundle = _parse_closed(_held_input(root_binding))
        bundle_parent = PurePosixPath(root_binding['path']).parent
        for material in bundle['files']:
            row = {'path': str(bundle_parent / material['path']),
                   'sha256': material['sha256']}
            check_binding(row, kind='source_api')
            require(selected.setdefault(row['path'], row) == row,
                    'profile bundle material conflicts with predecessor')
    d74_registry = selected['authority/admissions/governance-transaction-surface/v1/registries/definition-registry.json']
    registry_alias = {'path': 'authority/definitions/registry.json',
                      'sha256': d74_registry['sha256']}
    require(selected.setdefault(registry_alias['path'], registry_alias) == registry_alias,
            'current definition registry differs from pinned D74 postimage')
    lookup = profile['current_selection']['lookup']
    check_binding(lookup, kind='source_api')
    require(selected.setdefault(lookup['path'], lookup) == lookup,
            'current lookup conflicts with selected profile')
    registry_paths = (
        'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json',
        'authority/admissions/governance-transaction-surface/v1/registries/definition-registry.json',
        'authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json',
    )
    registries = [_parse_closed(_held_input(selected[path])) for path in registry_paths]
    referenced = []
    for item in registries[0]['admitted_contracts']:
        referenced.extend(({'path': item['artifact_path'], 'sha256': item['artifact_sha256']},
                           {'path': item['schema_path'], 'sha256': item['schema_sha256']}))
    referenced.extend({'path': item['path'], 'sha256': item['sha256']}
                      for item in registries[1]['entries'])
    referenced.extend({'path': item['instance_path'], 'sha256': item['instance_sha256']}
                      for item in registries[2]['entries'])
    for row in referenced:
        check_binding(row, kind='source_api')
        require(selected.setdefault(row['path'], row) == row,
                'profile registry reference conflicts with predecessor')
    require(selected.setdefault(MAPPING_PROPOSAL['path'], MAPPING_PROPOSAL) == MAPPING_PROPOSAL,
            'selected mapping proposal conflicts with predecessor')
    mapping = _parse_closed(_held_input(engine['mapping_binding']))
    for item in mapping['mappings']:
        for row in (item['schema_binding'], item['descriptor_binding']):
            check_binding(row, kind='source_api')
            require(selected.setdefault(row['path'], row) == row,
                    'selected mapping input conflicts with predecessor')
    correction = _parse_closed(_held_input(engine['correction_profile_binding']))
    correction_rows = [engine['correction_profile_binding'],
                       correction['review_manifest_binding'],
                       correction['source_proof_binding'],
                       correction['parent_engine_binding'],
                       *correction['member_bindings']]
    for member_row in correction['member_bindings']:
        member = _parse_closed(_held_input(member_row))
        correction_rows.extend(member[key] for key in
                               ('record_binding', 'original_source_binding', 'schema_binding'))
        correction_rows.append({'path': member['signature_binding']['ref'],
                                'sha256': member['signature_binding']['sha256']})
        for witness in member['endpoint_witnesses']:
            correction_rows.extend((witness['source_binding'],
                                    witness['admission_overlay']['binding']))
    for row in correction_rows:
        check_binding(row, kind='source_api')
        require(selected.setdefault(row['path'], row) == row,
                'correction source conflicts with predecessor')
    for path, pin in SCHEMA_REFERENCE_SHA.items():
        row = {'path': path, 'sha256': pin}
        require(selected.setdefault(path, row) == row,
                'schema reference conflicts with predecessor')
    for row in tuple(selected.values()):
        if not row['path'].startswith('authority/admissions/') or not row['path'].endswith('.json'):
            continue
        value = _parse_closed(_held_input(row))
        binding = value.get('authorization') if type(value) is dict else None
        if type(binding) is dict and set(binding) == {'path', 'sha256'}:
            target = binding['path']
            check_binding({'path': target, 'sha256': binding['sha256']}, kind='source_api')
            if not (REPO / target).is_file():
                target = str(PurePosixPath(row['path']).parent / target)
            derived = {'path': target, 'sha256': binding['sha256']}
            check_binding(derived, kind='source_api')
            require(selected.setdefault(target, derived) == derived,
                    'admission authorization conflicts with predecessor')
    history_base = profile['current_selection']['history_base']
    for name in ('project-semantic-event-history', 'project-governance-event-history'):
        history_path = history_base + '/' + name + '.json'
        history = _parse_closed(_held_input(selected[history_path]))
        for event in history['payload']['events']:
            for binding in event.get('material_refs', ()):
                check_binding(binding, kind='source_api')
                require(selected.setdefault(binding['path'], binding) == binding,
                        'selected history material conflicts with predecessor')
            if 'authorization_ref' in event:
                row = {'path': event['authorization_ref'],
                       'sha256': event['authorization_sha256']}
                check_binding(row, kind='source_api')
                require(selected.setdefault(row['path'], row) == row,
                        'selected history authorization conflicts')
    for row in selected.values():
        captured[row['path']] = _held_input(row)
    return selected, captured


def _copy_snapshot(snapshot: Path, rows: dict[str, dict], captured: dict[str, bytes]) -> None:
    for row in rows.values():
        target = snapshot / row['path']
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(captured[row['path']])
        require(_sha(target.read_bytes()) == row['sha256'], 'sparse snapshot copy changed')


def _unsealed_source(raw: bytes, layout: role_stage.DisposableLayout, name: str) -> bytes:
    # Same pure relocation/hardener as role_stage, but the source builder's
    # ordinary writes are permitted only inside the disposable bwrap mount.
    text = raw.decode()
    prefix = 'completion-' + layout.instance
    text = text.replace('R03-legacy-session-fixture-0257', prefix)
    text = text.replace('_cal_legacy_', '_cal_' + layout.instance.replace('-', '_') + '_legacy_')
    text = text.replace('HERE.parents[5]', f'Path({str(layout.snapshot)!r})')
    text = text.replace(str(REPO), str(layout.snapshot))
    text = text.replace(role_stage.OLD_NATIVE, str(layout.snapshot / role_stage.NATIVE_REL))
    for selected_role, old in role_stage.ORIGINS.items():
        text = text.replace("HERE.parent/'" + old, "HERE.parent/'" + selected_role)
        text = text.replace("ADAPTER_ROOT.parent/'" + old,
                            "ADAPTER_ROOT.parent/'" + selected_role)
    for external in ('custody-correction-v4', 'current-participation-v5', 'api-v25', 'fact-read-scope-v1'):
        root = "(ROOT/'product/lab/release-candidates/v1/interface')"
        text = text.replace("HERE.parent/'" + external, root + "/'" + external)
    text = harden('source', name, text)
    tree = role_stage._PathCalls().visit(ast.parse(text))
    at = 1 if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant) else 0
    tree.body[at:at] = role_stage._helper(layout.family, layout.snapshot)
    ast.fix_missing_locations(tree)
    rendered = (ast.unparse(tree) + '\n').encode()
    compile(rendered, '<disposable-source-' + name + '>', 'exec', optimize=0)
    compile(rendered, '<disposable-source-' + name + '>', 'exec', optimize=2)
    return rendered


def _tree_files(family_root: Path) -> dict[str, str]:
    result = {}
    for path in family_root.rglob('*'):
        info = path.lstat()
        require(not stat.S_ISLNK(info.st_mode), 'disposable output symlink refused')
        if stat.S_ISDIR(info.st_mode):
            continue
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1,
                'disposable output must be a single-link regular leaf')
        result[path.relative_to(family_root).as_posix()] = _sha(path.read_bytes())
    return result


def _tree_dirs(family_root: Path) -> set[str]:
    result = set()
    for path in family_root.rglob('*'):
        info = path.lstat()
        require(not stat.S_ISLNK(info.st_mode), 'disposable output symlink refused')
        if stat.S_ISDIR(info.st_mode):
            result.add(path.relative_to(family_root).as_posix())
    return result


def _historical_package_names(raw: bytes) -> set[str]:
    value = _parse_closed(raw)
    original_base = PurePosixPath(HISTORICAL_SOURCE_PACKAGE['path']).parent
    names = set()
    for row in value['files']:
        check_binding(row, kind='source_api')
        relative = PurePosixPath(row['path']).relative_to(original_base)
        require(str(relative) not in names and relative.parts,
                'duplicate historical source package member')
        names.add(str(relative))
    require(len(names) == 36, 'exact historical source package member set differs')
    return names


def _run_bounded(argv: list[str], *, timeout: int = 180,
                 stream_limit: int = 128 * 1024) -> tuple[int, bytes, bytes]:
    """Bound diagnostics independently of the builder's legitimate file writes."""
    process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               start_new_session=True)
    output = {process.stdout: bytearray(), process.stderr: bytearray()}
    selector = selectors.DefaultSelector()
    for stream in output:
        selector.register(stream, selectors.EVENT_READ)
    deadline = time.monotonic() + timeout
    forced = None
    try:
        while selector.get_map():
            if time.monotonic() >= deadline:
                forced = 124
                break
            for event, _ in selector.select(timeout=min(0.5, deadline - time.monotonic())):
                chunk = os.read(event.fileobj.fileno(), 65536)
                if not chunk:
                    selector.unregister(event.fileobj)
                    continue
                target = output[event.fileobj]
                if len(target) + len(chunk) > stream_limit:
                    forced = 125
                    break
                target.extend(chunk)
            if forced is not None:
                break
        if forced is not None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        returncode = process.wait(timeout=10)
        return (forced if forced is not None else returncode,
                bytes(output[process.stdout]), bytes(output[process.stderr]))
    finally:
        selector.close()
        for stream in output:
            stream.close()
        if process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait(timeout=10)


def probe() -> dict:
    require(BWRAP.is_file() and _sha(BWRAP.read_bytes()) == BWRAP_SHA,
            'exact selected bubblewrap executable differs')
    version = subprocess.check_output([str(BWRAP), '--version'], text=True).strip()
    require(version == 'bubblewrap 0.11.1', 'selected bubblewrap version differs')
    with tempfile.TemporaryDirectory(prefix='lc-u02-05-source-probe-') as scratch:
        root = Path(scratch)
        snapshot, output = root / 'snapshot', root / 'output'
        snapshot.mkdir(); output.mkdir()
        rows, captured = _source_rows()
        _copy_snapshot(snapshot, rows, captured)
        (snapshot / '_t35_source_runner.py').write_text(SANDBOX_RUNNER)
        layout = role_stage.DisposableLayout(PurePosixPath('/work/out/legacy-fixture-source'),
                                              PurePosixPath('/work/snapshot'), 'legacy-fixture-source')
        staged = role_stage.stage_rows(layout, lambda name: captured[name])
        for row in staged:
            name = PurePosixPath(row['output']['path']).name
            raw = row['bytes']
            if row['role'] == 'source' and name.endswith('.py'):
                raw = _unsealed_source(captured[row['input']['path']], layout, name)
            row['bytes'] = raw
            row['output'] = _bind(Path(row['output']['path']), raw)
            leaf = output / 'legacy-fixture-source' / row['role'] / Path(row['output']['path']).relative_to(
                str(layout.family / row['role']))
            leaf.parent.mkdir(parents=True, exist_ok=True); leaf.write_bytes(raw)
        original_episode = _parse_closed(captured[str(EXTRA_INPUTS[0])])
        from datetime import datetime, timedelta, timezone
        now = datetime.now(timezone.utc)
        episode = {k: v.replace('R03-legacy-session-fixture-0257', 'completion-legacy-fixture-source')
                   if type(v) is str else v for k, v in original_episode.items()}
        episode['not_before'] = (now - timedelta(minutes=1)).isoformat()
        episode['expires_at'] = (now + timedelta(hours=23, minutes=59)).isoformat()
        episode['purpose'] = 'Disposable source-builder fixture only; no host authority.'
        episode_leaf = output / 'legacy-fixture-source/source/episode-contract.json'
        episode_raw = (json.dumps(episode, sort_keys=True, indent=2) + '\n').encode()
        episode_leaf.write_bytes(episode_raw)
        # Current source preflight selects exact immutable predecessor inputs and
        # all generated role bytes. The probe is a separate effect-capable stage.
        family = Path('/work/out/legacy-fixture-source')
        role_control_raw = b'{"schema_version":"lab-T35-disposable-native-role/v1","authority_effect":"none"}\n'
        role_control_leaf = output / 'legacy-fixture-source/source/context-native-role.json'
        role_control_leaf.write_bytes(role_control_raw)
        control_value = {
            'schema_version': 'lab-T35-external-root-stage-selection/v1-inactive',
            'authority_effect': 'none', 'instance': layout.instance,
            'output_family_path': str(layout.family),
            'template_rows': [{key: item[key] for key in ('role', 'input', 'output')}
                              for item in staged],
            'episode_binding': _bind(family / 'source/episode-contract.json', episode_raw),
            'current_role_binding': _bind(family / 'source/context-native-role.json', role_control_raw),
            'status': 'staged-unqualified',
        }
        construction_raw = (json.dumps(control_value, sort_keys=True,
                                       separators=(',', ':')) + '\n').encode()
        construction_leaf = output / 'legacy-fixture-source/construction-selection.json'
        construction_leaf.write_bytes(construction_raw)
        controls = {'episode_contract': episode_raw,
                    'context_native_role': role_control_raw,
                    'construction_selection': construction_raw}
        stage_map = constructor_paths.stage_30_membership(layout, staged, controls)
        stage_inputs = [stage_map[name] for name in sorted(stage_map)]
        require(len(stage_inputs) == 30 and
                {p.relative_to(output / 'legacy-fixture-source').as_posix()
                 for p in (output / 'legacy-fixture-source').rglob('*') if p.is_file()} ==
                {Path(name).relative_to(family).as_posix() for name in stage_map},
                'exact 30-leaf disposable source stage required')
        stage_control = (json.dumps(stage_inputs, sort_keys=True, separators=(',', ':')) + '\n').encode()
        (snapshot / '_t35_stage_selection.json').write_bytes(stage_control)
        manifest = {'schema_version': 'lab-T35-disposable-source-probe/v1-inactive',
                    'files': sorted([*rows.values(), *stage_inputs], key=lambda r: r['path']),
                    'environment': {'python': '3.14.4', 'jsonschema': '4.19.2', 'cryptography': '46.0.5'},
                    'authority_effect': 'none', 'actual_owner_outcome': None,
                    'fixture_only': True}
        manifest_leaf = output / 'legacy-fixture-source/source/source-manifest.json'
        manifest_raw = (json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode()
        manifest_leaf.write_bytes(manifest_raw)
        bridge_raw = (SCRATCH_BRIDGE.replace('__SOURCE_MANIFEST_SHA__', _sha(manifest_raw))
                      .replace('__STAGE_SELECTION_SHA__', _sha(stage_control))).encode()
        (snapshot / '_t35_external_runtime_capture.py').write_bytes(bridge_raw)
        family_host = output / 'legacy-fixture-source'
        package_host = family_host / 'source/packages'
        package_host.mkdir()
        pre_state = _tree_files(family_host)
        pre_dirs = _tree_dirs(family_host)
        require(set(pre_state) == {Path(name).relative_to(family).as_posix()
                                   for name in stage_map} | {'source/source-manifest.json'},
                'pre-effect family has unexpected leaf')
        expected_package = _historical_package_names(captured[HISTORICAL_SOURCE_PACKAGE['path']])
        argv = [str(BWRAP), '--die-with-parent', '--unshare-all', '--clearenv',
                '--setenv', 'PATH', '/usr/bin:/bin',
                '--setenv', 'HOME', '/nonexistent',
                '--setenv', 'TMPDIR', '/tmp',
                '--setenv', 'LC_ALL', 'C.UTF-8',
                '--ro-bind', '/usr', '/usr',
                '--ro-bind', '/lib', '/lib', '--ro-bind', '/lib64', '/lib64',
                '--proc', '/proc', '--dev', '/dev', '--tmpfs', '/tmp', '--dir', '/work',
                '--dir', '/work/out',
                '--ro-bind', str(snapshot), '/work/snapshot',
                '--ro-bind', str(family_host), '/work/out/legacy-fixture-source',
                '--bind', str(package_host), '/work/out/legacy-fixture-source/source/packages',
                '--chdir', '/work',
                '--', '/usr/bin/python3', '-I', '-B', '/work/snapshot/_t35_source_runner.py']
        returncode, stdout_raw, stderr_raw = _run_bounded(argv)
        post_state = _tree_files(family_host)
        post_dirs = _tree_dirs(family_host)
        package = package_host / '0001/manifest.json'
        package_prefix = 'source/packages/0001/'
        expected_files = set(pre_state) | {package_prefix + name for name in expected_package} | {
            package_prefix + 'manifest.json'}
        expected_dirs = pre_dirs | {'source/packages/0001',
                                    'source/packages/0001/artifacts',
                                    'source/packages/0001/setup-artifacts'}
        tree_ok = (set(post_state) == expected_files and post_dirs == expected_dirs and
                   all(post_state[path] == digest for path, digest in pre_state.items()))
        missing_names = sorted(expected_files - set(post_state))
        unexpected_names = sorted(set(post_state) - expected_files)
        safe_success = None
        if returncode == 0 and tree_ok and package.is_file():
            lines = stdout_raw.splitlines()
            require(len(lines) == 2, 'exact two closed success records required')
            builder, runner = (_parse_closed(line) for line in lines)
            package_raw = package.read_bytes()
            package_sha = _sha(package_raw)
            builder_path = str(family / 'source/packages/0001/manifest.json')
            require(type(builder) is dict and set(builder) ==
                    {'result', 'package_binding', 'actual_original_targets', 'records'} and
                    builder['result'] == 'PASS' and builder['package_binding'] ==
                    {'path': builder_path, 'sha256': package_sha} and
                    builder['actual_original_targets'] == 23 and builder['records'] == 21,
                    'historical source success record differs')
            require(type(runner) is dict and set(runner) ==
                    {'sandbox_host_checkout_absent', 'sandbox_protected_roots_absent',
                     'source_package_manifest_sha256'} and
                    runner['sandbox_host_checkout_absent'] is True and
                    runner['sandbox_protected_roots_absent'] is True and
                    runner['source_package_manifest_sha256'] == package_sha,
                    'sandbox source success record differs')
            package_value = _parse_closed(package_raw)
            require(type(package_value) is dict and set(package_value) ==
                    {'schema_version', 'files', 'source_manifest_binding',
                     'archive_binding', 'expected_replay_binding', 'period_binding',
                     'episode_contract_binding', 'visibility',
                     'public_package_export_allowed', 'authority_effect',
                     'actual_owner_outcome'} and
                    package_value['schema_version'] ==
                    'lab-owned-current-participation-package/v1-candidate' and
                    package_value['visibility'] == 'private-candidate-original-custody' and
                    package_value['public_package_export_allowed'] is False and
                    package_value['authority_effect'] == 'none' and
                    package_value['actual_owner_outcome'] is None,
                    'historical source package claims differ')
            expected_core = {
                'source_manifest_binding': ('source/source-manifest.json',
                                            pre_state['source/source-manifest.json']),
                'archive_binding': ('source/packages/0001/branch.snapshot',
                                    post_state[package_prefix + 'branch.snapshot']),
                'expected_replay_binding': ('source/packages/0001/expected-replay.json',
                                            post_state[package_prefix + 'expected-replay.json']),
                'period_binding': ('source/packages/0001/period.json',
                                   post_state[package_prefix + 'period.json']),
                'episode_contract_binding': ('source/episode-contract.json',
                                             pre_state['source/episode-contract.json']),
            }
            require(all(package_value[key] == {'path': str(family / suffix),
                                               'sha256': digest}
                        for key, (suffix, digest) in expected_core.items()),
                    'historical source package core bindings differ')
            members = package_value['files']
            require(len(members) == 36 and
                    {PurePosixPath(row['path']).relative_to(family / 'source/packages/0001').as_posix()
                     for row in members} == expected_package and
                    all(post_state[package_prefix +
                                   PurePosixPath(row['path']).relative_to(family / 'source/packages/0001').as_posix()]
                        == row['sha256'] for row in members),
                    'historical source package inventory differs')
            build_result = _parse_closed((package_host / '0001/build-result.json').read_bytes())
            require(build_result['result'] == 'PASS' and
                    build_result['owned_store_and_key_removed'] is True and
                    build_result['private_keys_exported'] is False and
                    build_result['canonical_effects_applied'] == 0,
                    'historical source build result exceeds fixture ceiling')
            safe_success = package_sha
        summary = {'status': 'PASS-fixture-only' if safe_success else 'FAIL-inert-probe',
                   'returncode': returncode, 'selected_input_count': len(rows),
                   'selected_input_bytes': sum(len(raw) for raw in captured.values()),
                   'selected_input_selection_sha256': _sha((json.dumps(
                       [rows[name] for name in sorted(rows)], sort_keys=True,
                       separators=(',', ':')) + '\n').encode()),
                   'bwrap_sha256': BWRAP_SHA, 'bwrap_version': version,
                   'bwrap_argv_shape': [('<sparse-snapshot>' if arg == str(snapshot) else
                                        '<disposable-family>' if arg == str(family_host) else
                                        '<disposable-package>' if arg == str(package_host) else arg)
                                        for arg in argv],
                   'runner_sha256': _sha(SANDBOX_RUNNER.encode()),
                   'bridge_sha256': _sha(bridge_raw),
                   'stage_selection_sha256': _sha(stage_control),
                   'source_manifest_sha256': _sha(manifest_leaf.read_bytes()),
                   'preexisting_leaf_count': len(pre_state),
                   'post_leaf_count': len(post_state),
                   'post_tree_exact': tree_ok,
                   'missing_expected_leaf_names': missing_names,
                   'unexpected_leaf_names': unexpected_names,
                   'unexpected_directory_names': sorted(post_dirs - expected_dirs),
                   'source_package_manifest_sha256': safe_success,
                   'stdout_sha256': _sha(stdout_raw), 'stdout_bytes': len(stdout_raw),
                   'stderr_sha256': _sha(stderr_raw), 'stderr_bytes': len(stderr_raw),
                   'private_signer_path_exposed': False,
                   'claim_ceiling': 'disposable-historical-source-build-only'}
    require(not root.exists(), 'disposable scratch root remained after cleanup')
    summary['scratch_cleaned_after_return'] = True
    return summary


if __name__ == '__main__':
    value = probe()
    print(json.dumps(value, sort_keys=True, indent=2))
    if value['status'] != 'PASS-fixture-only':
        raise SystemExit(1)
