"""Effect-disabled final Context stage selector over the durable successor family.

Only public manifests, bounded Reader aggregate receipt and reviewed metadata
are read. The Source archive body is never opened and no stage/key/grant/policy
or Docker effect is performed. Actual Mapper evidence is pinned outside the records; no execution authority is emitted.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import importlib.util
import json
import os
import stat
import types
from pathlib import Path, PurePosixPath

REPO = Path('/home/vlad_/projects/CyberAlchemy-lab')
LOCAL = REPO / 'implementation/lab-runtime/local-host'
FAMILY = Path('/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001')
SOURCE_ROLE = 'product/lab/release-candidates/v1/interface/docker-source-20261020-0002'
READER_ROLE = 'product/lab/release-candidates/v1/interface/docker-reader-20261020-0002'
MAPPER_ROLE = 'product/lab/release-candidates/v1/interface/docker-mapped-20261020-0002'
CONTEXT_ROLE = 'product/lab/release-candidates/v1/interface/docker-context-20261020-0002'
API_ROLE = 'product/lab/release-candidates/v1/interface/api-v25'
READER_STAGE = FAMILY / 'reader-stage-attempt'
READER_ATTEMPT = FAMILY / 'reader-attempt'
READER_MANIFEST = READER_STAGE / 'root' / READER_ROLE / 'source-manifest.json'
READER_RECEIPT = READER_ATTEMPT / 'reader-output/receipt.json'
READER_FINAL = READER_ATTEMPT / 'evidence/reader-once.final.json'
READER_EXTERNAL = Path('/home/vlad_/.local/state/cyberalchemy-lab-observations/reader-successor-docker-release-0002/result.json')
READER_REVIEW = LOCAL / 'context-successor-reader-independent-effect-review-0001/review.json'
READER_STAGE_REVIEW = LOCAL / 'context-successor-reader-stage-independent-effect-review-0001/review.json'
READER_STAGE_PLAN = LOCAL / 'reader-successor-stage-0001/stage-plan.json'
ORIGINAL_SELECTION = LOCAL / 'context-stage-0001/selection.json'
JIT_CODE = LOCAL / 'context-successor-jit-0002/jit_successor.py'
JIT_FREEZE = LOCAL / 'context-successor-jit-0002/freeze.json'
JIT_REVIEW = LOCAL / 'CONTEXT-SUCCESSOR-JIT-INDEPENDENT-STATIC-REVIEW-0002.md'
CONTEXT_SELECTOR = LOCAL / 'context-successor-selector-0001/adapter.py'
CONTEXT_SELECTOR_FREEZE = LOCAL / 'context-successor-selector-0001/freeze.json'
JIT_CODE_SHA = '519053bc518a6d1822d731a3133e3219c7a80350e4384cec5c922b4895183f01'
JIT_FREEZE_SHA = '06501e59f66afcec5ff360750bec142b7293abdcb82d418f4800d9fd965b6136'
JIT_REVIEW_SHA = '5a01e697c80beb877777c8c722d1c027922924ebab44ec5c8546add6a96cc081'
CONTEXT_SELECTOR_SHA = '23177529919f1737f94b08daa18e8710cc51f55d72e6afa71365c0c5d5ec6929'
CONTEXT_SELECTOR_FREEZE_SHA = 'd4aed1b9047f0e125dc13b3c248b75c63e76150dcf49e45183a8deb2a4aece6d'
ORIGINAL_SELECTION_SHA = '6721210d076da6462f904b2836a9e3ff5853be92f395a05ee2b141b517e078bf'
READER_STAGE_PLAN_SHA = 'a5ee5e9812c4ab5d0e37b7fe99aec4f334dcb583668ad0489f267f7e2258478b'
READER_STAGE_REVIEW_SHA = 'f0ba7f19d2cc478d951eaeebec9d405da3b7405f51e24196a4a9ecf54370962f'
READER_REVIEW_SHA = 'c2f9d0307610d281784c4d3c86211dbc37bd6a5843130647ff1718561957f295'
READER_MANIFEST_SHA = '048ef6c1f54387fc6e593f38b29723cb06f84649f12e9c75a0340d389b0f5756'
READER_RECEIPT_SHA = 'd389c46467b2cbac48e6cec3ec9a8d58c7f036516576b718c6f796a1586eedf2'
READER_FINAL_SHA = '8a4a1bf63afe5351e1f6184038e2ec13cf30e855d85c51b145122a19efcb21aa'
READER_EXTERNAL_SHA = '5c421de1f92545ba29efaa2cb5d49d8f51ff8773a979173f8ef21bee4e3b95c5'
SOURCE_MANIFEST_SHA = '2843a67fd28a295f5c175b8d8c2b31f701040bb8d7dedeade8d76bbdf057d1d1'
SOURCE_PACKAGE_SHA = 'bdb5eac92cbb3f96857c4d2ccb00880441d55fb8f1dbbeb5cdaae8d81c720653'
SOURCE_REVIEW_SHA = '599d7cca4b87b98809e33636ad1326bc60ddba589123ec5a0a0c5e00b58a4440'
SOURCE_PERIOD_SHA = '3ff862090a38b346a384001c2d87da7cf648f18726fb056653a0fb4df40473ba'
SOURCE_ARCHIVE_SHA = '6e75c6175912a8b587e771ab7dded56bc53a07855216b97521938fb2d8121129'
NATIVE_SHA = 'fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'
EFFECT_ENABLED = False


class Refused(ValueError):
    pass


def need(ok, why):
    if not ok:
        raise Refused(why)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False,
                       allow_nan=False) + '\n').encode()


def pinned_leaf(path, pin, maximum=2 * 1024 * 1024):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
             0 < before.st_size <= maximum, 'PINNED_LEAF_SHAPE')
        raw = os.read(fd, before.st_size + 1)
        after = os.fstat(fd)
        need(len(raw) == before.st_size and
             (before.st_dev, before.st_ino, before.st_mode, before.st_size) ==
             (after.st_dev, after.st_ino, after.st_mode, after.st_size) and
             sha(raw) == pin, 'PINNED_LEAF_DRIFT')
        return raw
    finally:
        os.close(fd)


def parse(raw, *, canonical_required=True):
    need(type(raw) is bytes and 0 < len(raw) <= 2 * 1024 * 1024,
         'BOUNDED_JSON_REQUIRED')
    def pairs(items):
        value = {}
        for key, item in items:
            need(key not in value, 'DUPLICATE_JSON_KEY')
            value[key] = item
        return value
    try:
        value = json.loads(raw, object_pairs_hook=pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(Refused('NONFINITE_JSON')))
    except (UnicodeError, ValueError, TypeError, RecursionError) as exc:
        raise Refused('INVALID_JSON') from exc
    need(type(value) is dict and
         (not canonical_required or canonical(value) == raw),
         'CANONICAL_JSON_REQUIRED')
    return value


def frozen_modules():
    pinned_leaf(JIT_FREEZE, JIT_FREEZE_SHA)
    pinned_leaf(JIT_REVIEW, JIT_REVIEW_SHA)
    pinned_leaf(CONTEXT_SELECTOR_FREEZE, CONTEXT_SELECTOR_FREEZE_SHA)
    pinned_leaf(JIT_CODE, JIT_CODE_SHA)
    pinned_leaf(CONTEXT_SELECTOR, CONTEXT_SELECTOR_SHA)
    modules = []
    for name, path, pin in (('final_jit_successor_frozen', JIT_CODE, JIT_CODE_SHA),
                             ('final_context_selector_frozen', CONTEXT_SELECTOR, CONTEXT_SELECTOR_SHA)):
        raw = pinned_leaf(path, pin)
        module = types.ModuleType(name)
        module.__file__ = str(path)
        exec(compile(raw, str(path), 'exec'), module.__dict__)
        modules.append(module)
    jit, context = modules
    return jit, context


def source_reader_preflight(now=None):
    jit, context = frozen_modules()
    source = jit.source_preflight(now)
    stage_review = parse(pinned_leaf(READER_STAGE_REVIEW, READER_STAGE_REVIEW_SHA, 16*1024))
    review = parse(pinned_leaf(READER_REVIEW, READER_REVIEW_SHA, 16*1024))
    stage_plan = parse(pinned_leaf(READER_STAGE_PLAN, READER_STAGE_PLAN_SHA))
    reader_manifest = parse(pinned_leaf(READER_MANIFEST, READER_MANIFEST_SHA))
    receipt = parse(pinned_leaf(READER_RECEIPT, READER_RECEIPT_SHA, 64*1024),
                    canonical_required=False)
    reader_final = parse(pinned_leaf(READER_FINAL, READER_FINAL_SHA, 16*1024),
                         canonical_required=False)
    reader_external = parse(pinned_leaf(READER_EXTERNAL, READER_EXTERNAL_SHA, 16*1024),
                            canonical_required=False)
    original = parse(pinned_leaf(ORIGINAL_SELECTION, ORIGINAL_SELECTION_SHA))
    need(stage_review.get('verdict') == 'PASS_BOUNDED_STAGE_ONLY_EFFECT' and
         stage_review.get('stage_plan_sha256') == READER_STAGE_PLAN_SHA and
         stage_review.get('reader_manifest_sha256') == READER_MANIFEST_SHA and
         stage_review.get('source_effect_review_sha256') == SOURCE_REVIEW_SHA and
         stage_review.get('archive_sha256') == SOURCE_ARCHIVE_SHA and
         stage_review.get('file_count') == 986,
         'READER_STAGE_REVIEW_JOIN')
    need(review.get('schema') == 'lab-reader-successor-docker-effect-review/v1' and
         review.get('verdict') == 'PASS_BOUNDED_READER_ONLY_EFFECT' and
         review.get('attempt') == str(READER_ATTEMPT) and
         review.get('no_retry') is True and zero(review.get('os_exit_code')) and
         review.get('container_absent') is True and
         review.get('stage_effect_review_sha256') == READER_STAGE_REVIEW_SHA and
         review.get('source_package_manifest_sha256') == SOURCE_PACKAGE_SHA and
         review.get('reader_manifest_sha256') == READER_MANIFEST_SHA and
         review.get('receipt_sha256') == READER_RECEIPT_SHA and
         review.get('final_sha256') == READER_FINAL_SHA and
         review.get('external_observation_sha256') == READER_EXTERNAL_SHA and
         review.get('stage_files_verified') == 986,
         'ACTUAL_READER_EFFECT_REVIEW_JOIN')
    need(reader_final.get('schema_version') == 'lab-reader-only-docker-final/v1' and
         reader_final.get('overall') == reader_final.get('operation') ==
         reader_final.get('cleanup') == 'PASS' and
         zero(reader_final.get('client_exit')) and zero(reader_final.get('daemon_exit')) and
         reader_final.get('finalization') == 'CLOSED_AND_COMMITTED' and
         reader_final.get('no_retry') is True and
         reader_final.get('absent') is True and
         reader_final.get('receipt_sha256') == READER_RECEIPT_SHA and
         reader_external.get('schema') == 'reader-successor-docker-external-observation/v1' and
         zero(reader_external.get('os_exit_code')) and
         reader_external.get('retry_allowed') is False,
         'ACTUAL_READER_TERMINAL_EXTERNAL_JOIN')
    need(stage_plan.get('schema') == 'lab-reader-successor-stage-plan/v1' and
         stage_plan.get('archive_body_opened') is False and
         stage_plan.get('source_effect_review_sha256') == SOURCE_REVIEW_SHA and
         stage_plan.get('source_package_manifest_sha256') == SOURCE_PACKAGE_SHA and
         stage_plan.get('reader_manifest_sha256') == READER_MANIFEST_SHA and
         stage_plan.get('source_archive_sha256') == SOURCE_ARCHIVE_SHA and
         stage_plan.get('stage_root') == str(READER_STAGE / 'root') and
         len(stage_plan.get('files', [])) == 986,
         'READER_STAGE_PLAN_JOIN')
    stage_rows = stage_plan['files']
    stage_names = {row['path'] for row in stage_rows}
    archive = [row for row in stage_rows if row['path'] ==
               SOURCE_ROLE+'/packages/0001/branch.snapshot']
    need(len(stage_names) == 986 and len(archive) == 1 and
         archive[0]['sha256'] == SOURCE_ARCHIVE_SHA and
         archive[0]['target_mode'] == '0600',
         'PROTECTED_ARCHIVE_METADATA_ONLY')
    need(reader_manifest.get('schema_version') == 'lab-docker-distinct-reader-source/v1-candidate' and
         reader_manifest.get('authority_effect') == 'none' and
         reader_manifest.get('actual_owner_outcome') is None and
         reader_manifest.get('producer_source_binding') ==
         {'path':SOURCE_ROLE+'/source-manifest.json','sha256':SOURCE_MANIFEST_SHA} and
         reader_manifest.get('producer_package_binding') ==
         {'path':SOURCE_ROLE+'/packages/0001/manifest.json','sha256':SOURCE_PACKAGE_SHA},
         'CURRENT_READER_MANIFEST_JOIN')
    reader_code = [row for row in reader_manifest['files']
                   if row['path'] == READER_ROLE+'/reader.py']
    need(len(reader_code) == 1 and reader_code[0]['sha256'] ==
         'f93a1f218238c05b18a7c355f9bc1363bbf42d2b1d442d03e191e121f8e9c9b9',
         'CURRENT_READER_CODE_BINDING')
    need(receipt.get('schema_version') == 'lab-disposable-reader-receipt/v1-private' and
         receipt.get('source_manifest_sha256') == SOURCE_MANIFEST_SHA and
         receipt.get('source_package_manifest_sha256') == SOURCE_PACKAGE_SHA and
         receipt.get('reader_manifest_sha256') == READER_MANIFEST_SHA and
         receipt.get('authority_effect') == 'none' and
         receipt.get('actual_owner_outcome') is None,
         'CURRENT_READER_RECEIPT_JOIN')
    need(original.get('schema_version') == 'lab-context-stage-role-selection/v1-candidate' and
         original.get('effect') == 'NOT_RUN' and
         original.get('protected_body_read') is False and
         original.get('protected_body_copied') is False and
         original.get('native_sha256') == NATIVE_SHA and
         original.get('mapper_package_files') == 55 and
         original.get('context_output_mount_mode') == 'rw' and
         original.get('root_mount_mode') == 'ro' and
         original.get('native_mount_mode') == 'ro' and
         len(original.get('exact_public_checkout_additions', [])) == 512 and
         len(original.get('projected_api_additions', [])) == 5 and
         len(original.get('projected_context_additions', [])) == 7,
         'ORIGINAL_CONTEXT_OUTPUT_CONTRACT')
    additions = original['exact_public_checkout_additions']
    need(len({row['path'] for row in additions}) == 512 and
         stage_names.isdisjoint({row['path'] for row in additions}),
         'PUBLIC_ADDITION_COLLISION')
    return {'source':source,'stage_rows':stage_rows,
            'reader_manifest':reader_manifest,
            'reader_code_sha256':reader_code[0]['sha256'],
            'public_additions':additions,
            'topology':jit.topology(),
            'source_archive_metadata':{'path':archive[0]['path'],
                                       'sha256':SOURCE_ARCHIVE_SHA,
                                       'mode':'0600','body':'UNOPENED'},
            'reviews':{'jit':JIT_REVIEW_SHA,'reader_stage':READER_STAGE_REVIEW_SHA,
                       'reader_effect':READER_REVIEW_SHA},
            'context_selector':context,'jit':jit}


def preflight_plan(now=None):
    """Pure actual-evidence selection; no stage or authority effects."""
    return select_after_mapper(now)


def closed_rows(rows, expected, prefix):
    need(type(rows) is list and len(rows) == expected and
         all(type(row) is dict and set(row) == {'path','sha256'} and
             type(row['path']) is str and row['path'].startswith(prefix) and
             PurePosixPath(row['path']).as_posix() == row['path'] and
             all(part not in ('', '.', '..') for part in row['path'].split('/')) and
             type(row['sha256']) is str and len(row['sha256']) == 64 and
             all(c in '0123456789abcdef' for c in row['sha256']) for row in rows) and
         len({row['path'] for row in rows}) == expected,
         'MAPPER_CLOSED_ROWS')
    return rows


def _project(*, mapper_source_manifest_raw, mapper_package_manifest_raw,
                       mapper_role_rows, evidence, now=None):
    """Internal projection after fixed actual evidence validation; not an effect gate."""
    pre = source_reader_preflight(now)
    context, jit = pre['context_selector'], pre['jit']
    manifest = parse(mapper_source_manifest_raw)
    package = parse(mapper_package_manifest_raw)
    mapper_source_sha = sha(mapper_source_manifest_raw)
    mapper_package_sha = sha(mapper_package_manifest_raw)
    need(manifest.get('schema_version') == 'lab-docker-distinct-mapper-source/v1-candidate' and
         manifest.get('original_source_binding') ==
         {'path':SOURCE_ROLE+'/source-manifest.json','sha256':SOURCE_MANIFEST_SHA} and
         manifest.get('original_package_binding') ==
         {'path':SOURCE_ROLE+'/packages/0001/manifest.json','sha256':SOURCE_PACKAGE_SHA} and
         manifest.get('adapter_source_binding') ==
         {'path':READER_ROLE+'/source-manifest.json','sha256':READER_MANIFEST_SHA} and
         manifest.get('selected_native_executable') ==
         {'path':'/attempt/input/lab-context-native-reader','sha256':NATIVE_SHA} and
         manifest.get('authority_effect') == 'none' and
         manifest.get('actual_owner_outcome') is None,
         'MAPPER_SOURCE_BINDING')
    roles = closed_rows(mapper_role_rows, 5, MAPPER_ROLE+'/')
    required_roles = {MAPPER_ROLE+'/'+name for name in
                      ('__init__.py','base.py','build.py','policy.json','source-manifest.json')}
    expected_source_rows = (pre['reader_manifest']['files'] +
                            [{'path':READER_ROLE+'/source-manifest.json',
                              'sha256':READER_MANIFEST_SHA}] +
                            [row for row in roles if row['path'] !=
                             MAPPER_ROLE+'/source-manifest.json'])
    expected_source_map = {row['path']:row['sha256'] for row in expected_source_rows}
    selected_source_rows = manifest.get('files')
    need(len(expected_source_rows) == len(expected_source_map) == 953 and
         type(selected_source_rows) is list and len(selected_source_rows) == 953 and
         all(type(row) is dict and set(row) == {'path','sha256'} and
             type(row['path']) is str and type(row['sha256']) is str
             for row in selected_source_rows) and
         len({row['path'] for row in selected_source_rows}) == 953 and
         {row['path']:row['sha256'] for row in selected_source_rows} == expected_source_map,
         'MAPPER_EXACT_953_SOURCE_ROWS')
    need({row['path'] for row in roles} == required_roles and
         next(row['sha256'] for row in roles if row['path'].endswith('/source-manifest.json')) ==
         mapper_source_sha,
         'MAPPER_FIVE_ROLE_SOURCE_CLOSURE')
    need(package.get('schema_version') == 'lab-mapped-context-package/v1-candidate' and
         package.get('source_manifest_binding') ==
         {'path':MAPPER_ROLE+'/source-manifest.json','sha256':mapper_source_sha} and
         package.get('authority_effect') == 'none' and
         package.get('actual_owner_outcome') is None,
         'MAPPER_PACKAGE_SOURCE_JOIN')
    package_members = closed_rows(package.get('files'), 54,
                                  MAPPER_ROLE+'/packages/0001/')
    expected = {MAPPER_ROLE+'/packages/0001/'+name for name in
                context.mapper_adapter().OUTPUT_LEAVES if name != 'manifest.json'}
    need({row['path'] for row in package_members} == expected,
         'MAPPER_55_LEAF_OUTPUT_CONTRACT')
    receipt = validate_evidence(evidence, mapper_source_manifest_raw,
                                mapper_package_manifest_raw)
    outside_mapper_review_sha = receipt['review_sha256']
    selected_mapper_review_schema = REVIEW_SCHEMA
    pins = {'source':SOURCE_MANIFEST_SHA,'source_package':SOURCE_PACKAGE_SHA,
            'reader':READER_MANIFEST_SHA,'mapper':mapper_source_sha,
            'mapper_package':mapper_package_sha}
    api = context.project_api(pins)
    context_files = context.project_context(pins, sha(api['contract-profile.json']),
                                            pre['reader_code_sha256'])
    context_files['build.py'] = jit.rebind_guarded_build(context_files['build.py'])
    need(all(b'/tmp/cal-' not in raw for raw in tuple(api.values())+
             tuple(context_files.values())), 'STALE_TMP_FAMILY_LITERAL')
    projected_api = [{'path':API_ROLE+'/'+name,'sha256':sha(raw)} for name,raw in api.items()]
    projected_context = [{'path':CONTEXT_ROLE+'/'+name,'sha256':sha(raw)}
                         for name,raw in context_files.items()]
    need(len(projected_api) == 5 and len(projected_context) == 7,
         'CONTEXT_API_PROJECTION_CLOSURE')
    package_rows = package_members + [{'path':MAPPER_ROLE+'/packages/0001/manifest.json',
                                       'sha256':mapper_package_sha}]
    known = ([{'path':row['path'],'sha256':row['sha256'],
               'source':'reviewed_reader_stage_metadata',
               'mode':row['target_mode']} for row in pre['stage_rows']] +
             [{'path':row['path'],'sha256':row['sha256'],
               'source':'original_public_checkout','mode':row['mode']}
              for row in pre['public_additions']] +
             [{'path':row['path'],'sha256':row['sha256'],
               'source':'actual_reviewed_mapper_role','mode':'0444'} for row in roles] +
             [{'path':row['path'],'sha256':row['sha256'],
               'source':'actual_reviewed_mapper_package','mode':'0444'} for row in package_rows] +
             [{'path':row['path'],'sha256':row['sha256'],
               'source':'in_memory_api_projection','mode':'0444'} for row in projected_api] +
             [{'path':row['path'],'sha256':row['sha256'],
               'source':'in_memory_guarded_context_projection','mode':'0444'}
              for row in projected_context])
    names = [row['path'] for row in known]
    auth = SOURCE_ROLE+'/authorization/context-development.json'
    need(len(known) == len(set(names)) == 1570 and auth not in names and
         sum(row['path'].endswith('/branch.snapshot') for row in known) == 1 and
         all(not row['path'].startswith('/tmp/') for row in known),
         'FINAL_1571_FILE_PLAN_CLOSURE')
    return {'status':'IN_MEMORY_FINAL_STAGE_AND_AUTHORITY_PLAN_ONLY',
            'effect_enabled':False,'bound_rows':sorted(known,key=lambda r:r['path']),
            'bound_file_count':1570,'final_count_with_auth':1571,
            'auth_placeholder':{'path':auth,'sha256':'UNMINTED_UNSELECTED','mode':'0600'},
            'protected_archive_metadata':pre['source_archive_metadata'],
            'topology':pre['topology'],'pins':pins,
            'mapper_effect_review_sha256':outside_mapper_review_sha,
            'mapper_review_schema':selected_mapper_review_schema,
            'mapper_review_provenance':'EXACT_ACTUAL_REVIEW_AND_ORIGINAL_OBSERVATIONS',
            'api_bridge_sha256':sha(api['source_bridge.py']),
            'api_profile_sha256':sha(api['contract-profile.json']),
            'api_source_manifest_sha256':sha(api['source-manifest.json']),
            'context_guarded_build_sha256':sha(context_files['build.py']),
            'native':{'sha256':NATIVE_SHA,'container_path':'/attempt/input/lab-context-native-reader',
                      'mount_mode':'ro'},
            'context_output':{'path':'/workspace/'+CONTEXT_ROLE+'/packages','child_mode':'ro',
                              'parent_access':'HELD_WRITER_ONLY','topology':'PENDING_REVIEWED_RELEASE'},
            'workspace_mount_mode':'ro','source_period_sha256':SOURCE_PERIOD_SHA,
            'signed_scope':'NOT_OPENED','issuer':'UNSELECTED',
            'authorization':'UNMINTED','private_key':'UNCREATED',
            'policy':'UNWRITTEN','stage_copy':'REFUSED','docker_effect':'REFUSED'}


def copy_stage(*_args, **_kwargs):
    raise Refused('EFFECT_DISABLED_NO_FINAL_STAGE_COPY')


def issue_authority(*_args, **_kwargs):
    raise Refused('EFFECT_DISABLED_NO_ISSUER_OR_SIGNED_SCOPE')


def create_key_or_policy(*_args, **_kwargs):
    raise Refused('EFFECT_DISABLED_NO_PRIVATE_KEY_OR_POLICY')


def launch_context(*_args, **_kwargs):
    raise Refused('EFFECT_DISABLED_NO_CONTEXT_DOCKER_RELEASE')

CONTROLLER_FREEZE = LOCAL / 'mapper-successor-docker-controller-0002/freeze.json'
CONTROLLER_FREEZE_SHA = '4cac02ffa93511633ccdd45f2b0562069225f0e6e7530399ef88f5d2e692da2b'
STAGE_REVIEW = LOCAL / 'context-successor-mapper-stage-independent-effect-review-0001/review.json'
STAGE_REVIEW_SHA = 'bae85fada28780b6bcc88082d2436082402d8acfc25b420328c79df6d2f07406'
DOCKER_ATTEMPT = FAMILY / 'mapper-attempt/docker-attempt'
IMAGE = 'sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874'
NAME = 'cal-mapper-only-20261020-0002-successor-0001'
REVIEW_SCHEMA = 'lab-mapper-successor-docker-effect-review/v1'

def exact_fields(value, fields, code):
    need(type(value) is dict and set(value) == set(fields.split()), code)

def hex_digest(value):
    return type(value) is str and len(value) == 64 and all(c in '0123456789abcdef' for c in value)

def zero(value):
    return type(value) is int and value == 0


HERE = Path(__file__).resolve().parent
ACTUAL_PINS_SHA = 'fdc4bd01507adadd5a5af24a6e257fd51032c4ac66bcbc10400ee553f7ce8173'
ACTUAL_REVIEW_SHA = '5676b6b6ea2d45981ea9db637cde240a86a94983afc3411ee2eb3287e9c6b13f'
ATTEMPT = DOCKER_ATTEMPT
INNER = Path('/home/vlad_/.local/state/cyberalchemy-lab-observations/mapper-successor-docker-release-0001')
OUTER = Path('/home/vlad_/.local/state/cyberalchemy-lab-observations/mapper-successor-docker-wrapper-release-0001')

def _actual_pins():
    return parse(pinned_leaf(HERE/'actual-input-pins.json', ACTUAL_PINS_SHA))

def read_selected(row):
    # Empty stderr is a legitimate bound stream, not an absent file.
    if row['size']:
        raw = pinned_leaf(Path(row['path']), row['sha256'])
        need(len(raw) == row['size'], 'SELECTED_SIZE')
        return raw
    fd = os.open(row['path'], os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        st = os.fstat(fd)
        raw = os.read(fd, 1)
        need(stat.S_ISREG(st.st_mode) and st.st_nlink == 1 and st.st_size == 0 and
             raw == b'' and sha(raw) == row['sha256'], 'EMPTY_SELECTED_STREAM')
        return raw
    finally:
        os.close(fd)

def load_actual():
    pins = _actual_pins()
    for rel, digest in pins['predecessors'].items():
        pinned_leaf(LOCAL/rel, digest)
    for path, digest in pins['members'].items():
        pinned_leaf(Path(path), digest)
    bundle = {name:read_selected(row) for name,row in pins['evidence'].items()}
    package = parse(bundle['package'])
    members = closed_rows(package['files'], 54, MAPPER_ROLE+'/packages/0001/')
    root = DOCKER_ATTEMPT.parent/'root'
    files = {row['path']:pinned_leaf(root/row['path'], row['sha256'], 1048576)
             for row in members}
    files[MAPPER_ROLE+'/packages/0001/manifest.json'] = bundle['package']
    bundle['package_files'] = files
    return bundle

def select_after_mapper(now=None):
    bundle = load_actual()
    manifest = parse(bundle['source'])
    role_rows = [{'path':MAPPER_ROLE+'/'+name, 'sha256':sha(bundle['role:'+name])}
                 for name in ('__init__.py','base.py','build.py','policy.json')]
    role_rows.append({'path':MAPPER_ROLE+'/source-manifest.json', 'sha256':sha(bundle['source'])})
    result = _project(mapper_source_manifest_raw=bundle['source'],
                      mapper_package_manifest_raw=bundle['package'],
                      mapper_role_rows=role_rows, evidence=bundle, now=now)
    # Recheck every selected evidence/code original after projection. No claim of
    # atomic filesystem snapshot or continued custody after this function returns.
    pins = _actual_pins()
    for name,row in pins['evidence'].items():
        need(read_selected(row) == bundle[name], 'POSTSELECTION_DRIFT')
    for rel,digest in pins['predecessors'].items(): pinned_leaf(LOCAL/rel,digest)
    for path,digest in pins['members'].items(): pinned_leaf(Path(path),digest)
    result['mapper_effect_review_narrative_sha256'] = sha(bundle['narrative'])
    result['mapper_effect_audit_sha256'] = sha(bundle['audit'])
    result['selection_currentness'] = 'CHECKED_NOW_NO_FUTURE_DISPATCH_AUTHORITY'
    return result

def validate_evidence(bundle, source_raw, package_raw):
    pins = _actual_pins()
    need(type(bundle) is dict and set(bundle) == set(pins['evidence'])|{'package_files'}, 'EVIDENCE_FIELDS')
    for name,row in pins['evidence'].items():
        need(type(bundle[name]) is bytes and len(bundle[name]) == row['size'] and
             sha(bundle[name]) == row['sha256'], 'OUTSIDE_ACTUAL_PIN')
    return _semantic_joins(bundle, source_raw, package_raw)

def _semantic_joins(bundle, source_raw, package_raw):
    """Pure direct-schema joins. Tests may mutate originals here, never authority."""
    values = {k:v for k,v in bundle.items() if k not in
              {'package_files','narrative','audit_source'} and not k.startswith('role:')}
    docs = {k:parse(v,canonical_required=False) for k,v in values.items()
            if k not in ('outer_stderr','inner_stderr')}
    h = {k:sha(v) for k,v in values.items()}
    PINS = _actual_pins()['predecessors']
    exact = need
    oi,orr,osout = docs['outer_intent'],docs['outer_result'],docs['outer_stdout']
    ic,ii,cap,io,isin = (docs[x] for x in ('inner_consumed','inner_intent','inner_capture','inner_observation','inner_stdout'))
    ac,prepared,precreate,terminal,final = (docs[x] for x in ('attempt_consumed','prepared','precreate','terminal','final'))
    exact(oi['wrapper_freeze_sha256']==PINS['mapper-successor-docker-observer-effect-0001/freeze.json'] and
          oi['independent_review_sha256']==PINS['MAPPER-SUCCESSOR-DOCKER-OBSERVER-EFFECT-INDEPENDENT-STATIC-REVIEW-0001.md'] and
          oi['argv']==['/usr/bin/python3','-B',str(LOCAL/'mapper-successor-docker-observer-effect-0001/wrapper.py'),'--execute-reviewed-one-shot'] and
          oi['retry_allowed'] is False, 'OUTER_INTENT')
    exact(type(orr['os_exit_code']) is int and orr['os_exit_code']==0 and orr['process_error'] is None and
          orr['retry_allowed'] is False and orr['stdout_size']==len(values['outer_stdout']) and
          orr['stderr_size']==0 and values['outer_stderr']==b'' and
          orr['stdout_sha256']==h['outer_stdout'] and orr['stderr_sha256']==h['outer_stderr'] and
          oi['created_at_ns']<=orr['finished_at_ns'], 'OUTER_RESULT')
    from datetime import datetime, timezone
    period_start=int(datetime(2026,10,20,15,tzinfo=timezone.utc).timestamp())*10**9
    period_end=int(datetime(2026,10,21,15,tzinfo=timezone.utc).timestamp())*10**9
    exact(period_start<=oi['created_at_ns']<=orr['finished_at_ns']<period_end,
          'SOURCE_EFFECT_INTERVAL')
    exact(osout['status']=='PROVISIONAL_OS_ZERO_FINAL_JOIN' and
          osout['observation_sha256']==h['inner_observation'] and
          osout['stdout_sha256']==h['inner_stdout'] and
          osout['stderr_sha256']==h['inner_stderr'] and
          osout['release_os_exit']==0 and osout['independent_effect_review']=='PENDING' and
          osout['no_retry'] is True and osout['attempt']==str(ATTEMPT),
          'OUTER_INNER_JOIN')
    exact(ic['attempt']==str(ATTEMPT) and ic['container_name']==NAME and
          ic['no_retry'] is True and ii['attempt']==str(ATTEMPT) and
          ii['container_name']==NAME and ii['no_retry'] is True and
          ii['release_freeze_sha256']==PINS['mapper-successor-docker-release-0001/freeze.json'] and
          ii['release_review_sha256']==PINS['MAPPER-SUCCESSOR-DOCKER-RELEASE-INDEPENDENT-STATIC-REVIEW-0001.md'] and
          ii['release_entrypoint_sha256']=='cf85a26da6166e96855050ae0f511d22ff260ce4f807b9c67a077391b01bf927' and
          ii['argv']==['/usr/bin/python3','-B',str(LOCAL/'mapper-successor-docker-release-0001/release.py'),'--execute-reviewed-one-shot'],
          'INNER_CONSUMED_INTENT')
    capture=cap['capture']
    exact(cap['status']=='REAPED_PENDING_POSTCLOSE' and cap['error_class'] is None and
          cap['no_retry'] is True and type(capture['exit_code']) is int and
          capture['exit_code']==0 and capture['counts']==[len(values['inner_stdout']),0] and
          capture['retained']==capture['counts'] and capture['stdout_sha256']==h['inner_stdout'] and
          capture['stderr_sha256']==h['inner_stderr'] and capture['capture_error_class'] is None and
          capture['overflow'] is False and capture['pipe_tail_timeout'] is False and
          capture['signals']==[] and capture['child_preserved_after_signal'] is False and
          values['inner_stderr']==b'' and io['status']=='PROVISIONAL_OS_ZERO_FINAL_JOIN' and
          io['candidate']==cap['candidate'] and io['capture']==capture and
          io['independent_effect_review']=='PENDING' and io['no_retry'] is True,
          'INNER_CAPTURE_OBSERVATION')
    exact(isin==final and h['inner_stdout']!=h['final'] and
          cap['candidate']['final_sha256']==h['final'] and
          cap['candidate']['stdout_sha256']==h['inner_stdout'] and
          cap['candidate']['stderr_sha256']==h['inner_stderr'] and
          cap['candidate']['release_os_exit']==0 and
          cap['candidate']['status']=='PROVISIONAL_OS_ZERO_FINAL_JOIN',
          'RAW_STDOUT_FINAL_JOIN')
    exact(ac['attempt']==str(ATTEMPT) and ac['no_retry'] is True and
          ac['stage_effect_review_sha256']==PINS['context-successor-mapper-stage-independent-effect-review-0001/review.json'] and
          prepared['no_retry'] is True and prepared['container_name']==NAME and
          prepared['entrypoint_sha256']=='e00b863a91b5084e3ec85c662b38d912ee556fd6b1780704cb0f56d5de83cc2a' and
          prepared['label']==precreate['nonce']==terminal['nonce'] and
          prepared['create_argv_sha256']==precreate['create_argv_sha256']==terminal['create_argv_sha256'] and
          prepared['image']==precreate['image']==terminal['image'] and
          precreate['name']==terminal['name']==NAME and precreate['phase']=='BEFORE_CREATE' and
          precreate['effect']=='NOT_STARTED' and
          terminal['schema_version']=='lab-mapper-docker-one-shot-evidence/v2' and
          terminal['phase']=='TERMINAL' and terminal['overall']==terminal['cleanup']=='PASS' and
          type(terminal['client_exit']) is int and terminal['client_exit']==0 and
          type(terminal['daemon_exit']) is int and terminal['daemon_exit']==0 and
          terminal['daemon_exit_consistent'] is True and terminal['container_absent'] is True and
          terminal['forced_cleanup'] is False and terminal['create_attempted'] is True and
          type(terminal['container_id']) is str and len(terminal['container_id'])==64 and
          all(c in '0123456789abcdef' for c in terminal['container_id']),
          'ONE_SHOT_PROTOCOL')
    exact(final['schema']=='lab-mapper-successor-docker-final/v1' and
          final['overall']=='OBSERVED_DOCKER_ONLY' and final['attempt']==str(ATTEMPT) and
          final['terminal_sha256']==h['terminal'] and final['no_retry'] is True and
          final['authority_effect']=='none' and final['actual_owner_outcome'] is None and
          final['original_task_acceptance'] is False and
          final['requires_external_exit_zero_and_independent_effect_review'] is True,
          'PROVISIONAL_FINAL')
    review, audit = docs['review'], docs['audit']
    need(review['schema'] == REVIEW_SCHEMA and
         review['verdict'] == 'PASS_BOUNDED_MAPPER_ONLY_EFFECT' and
         review['retry_allowed'] is False and review['authority_effect'] == 'none' and
         review['actual_owner_outcome'] is None and review['original_task_acceptance'] is False and
         review['audit_result_sha256'] == h['audit'] and
         review['audit_source_sha256'] == sha(bundle['audit_source']), 'ACTUAL_REVIEW')
    review_hashes = {'outer_intent':'outer_intent_sha256','outer_result':'outer_external_observation_sha256',
        'outer_stdout':'outer_stdout_sha256','outer_stderr':'outer_stderr_sha256',
        'inner_consumed':'observer_consumed_sha256','inner_intent':'observer_intent_sha256',
        'inner_capture':'observer_capture_sha256','inner_observation':'external_observation_sha256',
        'inner_stdout':'stdout_sha256','inner_stderr':'stderr_sha256',
        'attempt_consumed':'attempt_consumed_sha256','prepared':'prepared_sha256',
        'precreate':'precreate_sha256','terminal':'terminal_sha256','final':'final_sha256'}
    need(all(review[field] == h[key] for key,field in review_hashes.items()) and
         audit['observation_sha256'] == {k:h[k] for k in review_hashes}, 'REVIEW_ORIGINAL_HASHES')
    lineage = {'source_effect_review_sha256':SOURCE_REVIEW_SHA,
        'reader_effect_review_sha256':READER_REVIEW_SHA,'stage_effect_review_sha256':STAGE_REVIEW_SHA,
        'source_manifest_sha256':SOURCE_MANIFEST_SHA,'source_package_manifest_sha256':SOURCE_PACKAGE_SHA,
        'reader_manifest_sha256':READER_MANIFEST_SHA,'mapper_manifest_sha256':sha(source_raw),
        'mapper_package_manifest_sha256':sha(package_raw),'native_sha256':NATIVE_SHA,
        'controller_freeze_sha256':CONTROLLER_FREEZE_SHA,'attempt':str(ATTEMPT),
        'observer_attempt':str(INNER),'outer_observation':str(OUTER),
        'container_id':terminal['container_id'],'container_name':NAME,'image':IMAGE}
    need(all(review[k] == v for k,v in lineage.items()), 'REVIEW_LINEAGE')
    for key in ('os_exit_code','outer_os_exit_code','client_exit_code','daemon_exit_code'):
        need(zero(review[key]), 'REVIEW_STRICT_EXIT')
    need(zero(osout['release_os_exit']) and zero(cap['candidate']['release_os_exit']), 'STRICT_NESTED_EXIT')
    need(all(type(n) is int for n in capture['counts']+capture['retained']) and
         type(orr['stdout_size']) is int and zero(orr['stderr_size']), 'STRICT_STREAM_COUNTS')
    need(type(oi['created_at_ns']) is int and type(orr['finished_at_ns']) is int,
         'STRICT_EFFECT_TIMES')
    need(review['container_absent'] is True and review['name_absent'] is True and
         review['effect_interval_within_source_period'] is True and
         audit['verdict_candidate'] == review['verdict'] and
         audit['container_absent_live'] is True and audit['stderr_empty'] is True and
         audit['private_body'] == 'UNOPENED' and audit['original_task_acceptance'] is False and
         audit['predecessor_pins'] == PINS, 'REVIEW_AUDIT_CEILING')
    stage = parse(pinned_leaf(STAGE_REVIEW,STAGE_REVIEW_SHA),canonical_required=False)
    need(stage['verdict'] == 'PASS_BOUNDED_STAGE_ONLY_EFFECT' and
         stage['mapper_manifest_sha256'] == sha(source_raw), 'ACTUAL_STAGE_MANIFEST_JOIN')
    exact_fields(final, 'schema overall attempt stage_effect_review_sha256 terminal_sha256 output no_retry authority_effect actual_owner_outcome original_task_acceptance requires_external_exit_zero_and_independent_effect_review claim_ceiling', 'FINAL_FIELDS')
    need(final['schema'] == 'lab-mapper-successor-docker-final/v1' and
         final['overall'] == 'OBSERVED_DOCKER_ONLY' and final['attempt'] == str(DOCKER_ATTEMPT) and
         final['stage_effect_review_sha256'] == STAGE_REVIEW_SHA and
         final['terminal_sha256'] == sha(bundle['terminal']) and final['no_retry'] is True and
         final['authority_effect'] == 'none' and final['actual_owner_outcome'] is None and
         final['original_task_acceptance'] is False and
         final['requires_external_exit_zero_and_independent_effect_review'] is True and
         type(final['claim_ceiling']) is str, 'ACTUAL_FINAL_JOIN')
    exact_fields(terminal, 'schema_version name nonce image create_argv_sha256 deadline_seconds recovery_seconds client_exit daemon_exit daemon_exit_consistent container_id phase overall cleanup container_absent forced_cleanup create_attempted', 'TERMINAL_FIELDS')
    need(terminal['schema_version'] == 'lab-mapper-docker-one-shot-evidence/v2' and
         terminal['name'] == NAME and terminal['image'] == IMAGE and
         type(terminal['nonce']) is str and len(terminal['nonce']) == 32 and
         all(c in '0123456789abcdef' for c in terminal['nonce']) and
         hex_digest(terminal['create_argv_sha256']) and hex_digest(terminal['container_id']) and
         type(terminal['deadline_seconds']) is int and terminal['deadline_seconds'] == 180 and
         type(terminal['recovery_seconds']) is int and terminal['recovery_seconds'] == 30 and
         zero(terminal['client_exit']) and zero(terminal['daemon_exit']) and
         terminal['daemon_exit_consistent'] is True and terminal['phase'] == 'TERMINAL' and
         terminal['overall'] == terminal['cleanup'] == 'PASS' and
         terminal['container_absent'] is True and terminal['forced_cleanup'] is False and
         terminal['create_attempted'] is True, 'DOCKER_TERMINAL_JOIN')
    output = final['output']
    exact_fields(output, 'schema result manifest_sha256 files semantic_leaves governance_leaves node_count edge_count exact_governance_joins native_seal_processes actual_cold_native_read_processes total_bytes authority_effect actual_owner_outcome task_complete', 'OUTPUT_FIELDS')
    counts = {'files':55,'semantic_leaves':25,'governance_leaves':25,'node_count':15,'edge_count':10,
              'exact_governance_joins':25,'native_seal_processes':2,'actual_cold_native_read_processes':2}
    need(output['schema'] == 'lab-mapper-successor-output-verification/v1' and
         output['result'] == 'PASS_CANDIDATE_OUTPUT_ONLY' and output['manifest_sha256'] == sha(package_raw) and
         all(type(output[k]) is int and output[k] == v for k,v in counts.items()) and
         output['authority_effect'] == 'none' and output['actual_owner_outcome'] is None and
         output['task_complete'] is False, 'OUTPUT_JOIN')
    package = parse(package_raw)
    files = bundle['package_files']
    need(type(files) is dict and len(files) == 55 and
         all(type(k) is str and type(v) is bytes and 0 < len(v) <= 1048576 for k,v in files.items()), 'PACKAGE_BODIES')
    expected = {r['path']:r['sha256'] for r in closed_rows(package['files'],54,MAPPER_ROLE+'/packages/0001/')}
    expected[MAPPER_ROLE+'/packages/0001/manifest.json'] = sha(package_raw)
    need(set(files) == set(expected) and all(sha(files[k]) == v for k,v in expected.items()) and
         files[MAPPER_ROLE+'/packages/0001/manifest.json'] == package_raw and
         type(output['total_bytes']) is int and output['total_bytes'] == sum(map(len,files.values())) and
         output['total_bytes'] <= 64*1024*1024, 'FULL_PACKAGE_BINDING')
    need(type(review['files_verified']) is int and review['files_verified'] == 55 and
         type(review['mapper_source_rows']) is int and review['mapper_source_rows'] == 953 and
         audit['package_manifest_sha256'] == sha(package_raw) and
         audit['package_total_bytes'] == output['total_bytes'], 'REVIEW_COUNTS_PACKAGE')
    return {'review_sha256':ACTUAL_REVIEW_SHA, 'claim':'ACTUAL_REVIEW_PINNED_SELECTION_ONLY'}
