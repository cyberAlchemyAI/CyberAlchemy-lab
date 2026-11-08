"""Stage and run a disjoint signed native family with one technical Lesson.

No phase mutates an existing family. Source/Reader/Mapper/Context remain
separately selected; the live API33 product must receive a later versioned
binding to this new family.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import re
import secrets

from transform import transform

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
NATIVE_ROOT = HERE.parent / 'source8-current-fixture'
FAMILY_ROOT = NATIVE_ROOT / 'instances'
NATIVE_RUNNER = NATIVE_ROOT / 'native_successor.py'
CONSTRUCTOR = HERE / 'construct_learning.py'
PHASES = ('stage', 'source', 'cold', 'reader', 'mapped', 'context')
TRANSFORMED = (('source', 'records.py'), ('source', 'build.py'),
               ('mapped', 'build.py'), ('context', 'generation.py'),
               ('context', 'build.py'))
EVIDENCE = ROOT / 'implementation/lab-runtime/local-host/working/api33-native-dispositions-independent-review-0003/REVIEW.md'
COLD_MANIFEST = ROOT / 'implementation/lab-runtime/local-host/t03-current-learning-fixture-0001/source-manifest.json'
LESSON_FIXTURE = ROOT / 'authority/artifact-types/operational-lesson/v1/fixtures/valid/record.json'
LESSON_SCHEMA = ROOT / 'authority/artifact-types/operational-lesson/v1/schema.json'
NATIVE_MANIFEST = HERE / 'source-manifest.json'
EXPECTED_FILES = {f'implementation/lab-runtime/local-host/t03-native-learning-successor-0001/{name}'
                  for name in ('transform.py', 'stage_learning.py', 'construct_learning.py', 'test_transform.py', 'README.md')}
EXPECTED_INPUTS = {
    NATIVE_RUNNER.relative_to(ROOT).as_posix(),
    'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T02/fresh-legacy-current-runtime-preparation-0009/construct_legacy_v3.py',
    EVIDENCE.relative_to(ROOT).as_posix(), COLD_MANIFEST.relative_to(ROOT).as_posix(),
    LESSON_FIXTURE.relative_to(ROOT).as_posix(), LESSON_SCHEMA.relative_to(ROOT).as_posix(),
} | {f'implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-947e6c2a5b3d10f8/{role}/{name}'
     for role, name in TRANSFORMED}


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def binding(path: Path) -> dict:
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': digest(path)}


def require(value, reason):
    if not value:
        raise ValueError(reason)


def load(path: Path):
    return json.loads(path.read_bytes())


def verify_manifest(reviewed_sha256: str):
    require(type(reviewed_sha256) is str and re.fullmatch(r'[0-9a-f]{64}', reviewed_sha256),
            'independent native constructor manifest pin required')
    require(digest(NATIVE_MANIFEST) == reviewed_sha256,
            'independent native constructor manifest pin differs')
    manifest = load(NATIVE_MANIFEST)
    rows = manifest['files'] + manifest['input_bindings']
    require(set(manifest) == {'schema_version', 'files', 'input_bindings', 'claim_ceiling'}
            and manifest['schema_version'] == 'lab-t03-native-learning-constructor/v1'
            and {row['path'] for row in manifest['files']} == EXPECTED_FILES
            and {row['path'] for row in manifest['input_bindings']} == EXPECTED_INPUTS
            and len(rows) == len({row['path'] for row in rows})
            and all(set(row) == {'path', 'sha256'} for row in rows),
            'native learning constructor inventory differs')
    for row in rows:
        path = ROOT / row['path']
        require(path.is_file() and not path.is_symlink() and path.resolve() == path
                and digest(path) == row['sha256'], 'native learning selected input differs: ' + row['path'])
    return manifest


def load_module(label: str, path: Path):
    require(path.is_file() and not path.is_symlink(), 'constructor origin differs')
    spec = importlib.util.spec_from_file_location(label, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def stage(instance: str, private_home: Path, reviewed_manifest_sha256: str):
    verify_manifest(reviewed_manifest_sha256)
    require(re.fullmatch(r'legacy-local-[0-9a-f]{16}', instance), 'closed fresh instance required')
    require(not (FAMILY_ROOT / instance).exists(), 'native family already exists')
    runner = load_module('t03_retained_native_runner', NATIVE_RUNNER)
    staged = runner.stage(instance, private_home)
    family = FAMILY_ROOT / instance
    selection_path = family / 'construction-selection.json'
    selection = load(selection_path)
    require(selection['instance'] == instance and selection['status'] == 'staged-unqualified', 'retained stage selection differs')
    require(not any((family / role / 'source-manifest.json').exists() for role in ('source', 'reader', 'mapped', 'context')),
            'selected role already exists')
    rows = {row['new']['path']: row for row in selection['template_rows']}
    for role, filename in TRANSFORMED:
        path = family / role / filename
        key = path.relative_to(ROOT).as_posix()
        row = rows.get(key)
        require(row is not None and path.is_file() and not path.is_symlink() and row['new'] == binding(path),
                'retained stage byte differs before transform: ' + key)
        original = path.read_text()
        changed = transform(role, filename, original)
        require(changed != original, 'required native successor transform absent: ' + key)
        path.write_text(changed)
        row['new'] = binding(path)
        row['changed'] = True
    require(digest(EVIDENCE) == 'd76090f5e8e501282c9234b00cad68b8d53a36b81be8549cc119c990615b3c29',
            'independent Lesson evidence changed')
    require(COLD_MANIFEST.is_file(), 'cold Lesson fixture manifest absent')
    inputs = {row['path']: row for row in selection['current_runtime_input_bindings']}
    for path in (HERE / 'transform.py', HERE / 'stage_learning.py', CONSTRUCTOR,
                 NATIVE_MANIFEST, EVIDENCE, COLD_MANIFEST, LESSON_FIXTURE, LESSON_SCHEMA):
        row = binding(path)
        require(inputs.get(row['path'], row) == row, 'successor source input collision')
        inputs[row['path']] = row
    selection['current_runtime_input_bindings'] = [inputs[key] for key in sorted(inputs)]
    predecessor_packet = selection['Root_packet_binding']
    predecessor_path = ROOT / predecessor_packet['path']
    require(predecessor_path.is_file() and binding(predecessor_path) == predecessor_packet,
            'retained stage packet differs')
    packet = load(predecessor_path)
    require(packet['instance'] == instance and packet['authority_effect'] == 'none',
            'retained packet identity differs')
    packet['schema'] = 'cal-native-local-learning-successor-selection/v1'
    packet['constructor_ref'] = HERE.relative_to(ROOT).as_posix()
    packet['predecessor_packet_binding'] = predecessor_packet
    packet['current_runtime_input_bindings'] = selection['current_runtime_input_bindings']
    packet['technical_lesson_evidence_binding'] = binding(EVIDENCE)
    packet['cold_fixture_binding'] = binding(COLD_MANIFEST)
    packet['reviewed_constructor_manifest_binding'] = binding(NATIVE_MANIFEST)
    successor_packet = runner.write_new(NATIVE_ROOT / 'selections' / (instance + '-learning.json'), packet)
    selection['Root_packet_binding'] = successor_packet
    selection['predecessor_Root_packet_binding'] = predecessor_packet
    selection['predecessor_generator_binding'] = selection['generator_binding']
    selection['successor_transform_binding'] = binding(HERE / 'transform.py')
    selection['successor_constructor_binding'] = binding(CONSTRUCTOR)
    selection['technical_lesson_evidence_binding'] = binding(EVIDENCE)
    selection['cold_fixture_binding'] = binding(COLD_MANIFEST)
    selection['reviewed_constructor_manifest_binding'] = binding(NATIVE_MANIFEST)
    selection['complete_current_Lesson_target_count'] = 1
    selection['status'] = 'staged-learning-unqualified'
    raw = json.dumps(selection, indent=2, sort_keys=True).encode() + b'\n'
    tmp = selection_path.with_suffix('.json.tmp')
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, selection_path)
    staged['learning_selection_binding'] = binding(selection_path)
    staged['technical_lesson_target_count'] = 1
    staged['reviewed_constructor_manifest_sha256'] = reviewed_manifest_sha256
    return staged


def phase(instance: str, name: str, reviewed_manifest_sha256: str):
    verify_manifest(reviewed_manifest_sha256)
    require(name in PHASES[1:] and re.fullmatch(r'legacy-local-[0-9a-f]{16}', instance), 'closed phase/instance required')
    family = FAMILY_ROOT / instance
    selection = load(family / 'construction-selection.json')
    require(selection['status'] == 'staged-learning-unqualified'
            and selection['successor_transform_binding'] == binding(HERE / 'transform.py')
            and selection['successor_constructor_binding'] == binding(CONSTRUCTOR)
            and selection['reviewed_constructor_manifest_binding'] == binding(NATIVE_MANIFEST),
            'learning successor selection changed')
    runner = load_module('t03_retained_native_runner', NATIVE_RUNNER)
    runner.protected_output_preflight(family)
    runner.technical_preflight()
    constructor = load_module('t03_native_learning_constructor', CONSTRUCTOR)
    constructor.HERE = NATIVE_ROOT
    result = getattr(constructor, name)(family)
    runner.write_new(family / (name + '-result.json'), result)
    return {**result, 'reviewed_constructor_manifest_sha256': reviewed_manifest_sha256}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=PHASES)
    parser.add_argument('--instance')
    parser.add_argument('--private-home', type=Path)
    parser.add_argument('--reviewed-manifest-sha256', required=True)
    args = parser.parse_args()
    instance = args.instance or 'legacy-local-' + secrets.token_hex(8)
    require(args.phase == 'stage' or args.instance is not None, 'phase needs exact instance')
    require(args.phase != 'stage' or args.private_home is not None, 'fresh private home required')
    result = (stage(instance, args.private_home, args.reviewed_manifest_sha256)
              if args.phase == 'stage' else phase(instance, args.phase, args.reviewed_manifest_sha256))
    print(json.dumps({'phase': args.phase, 'instance': instance, 'result': result}, sort_keys=True))


if __name__ == '__main__':
    main()
