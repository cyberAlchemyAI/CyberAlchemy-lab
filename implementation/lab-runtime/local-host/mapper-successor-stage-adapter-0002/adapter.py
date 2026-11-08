"""Inert direct Mapper plan from the actual independently reviewed Reader effect."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat

HERE = Path(__file__).resolve().parent
LOCAL = HERE.parent
MAPPER_RELEASE = LOCAL / 'mapper-successor-release-0002'
MAPPER_FREEZE_SHA = '9177b066bad394cf1eb1b481cb988f267a3d093f85f94cb02ad8e67731c63ab2'
MAPPER_REVIEW = LOCAL / 'MAPPER-SUCCESSOR-RELEASE-INDEPENDENT-STATIC-REVIEW-0002.md'
MAPPER_REVIEW_SHA = 'b40cd9bc7de7e2499fce11f8a503431338928fb9345b8e79c200b316ccec313e'
STAGE_REVIEW = LOCAL / 'context-successor-reader-stage-independent-effect-review-0001/review.json'
STAGE_REVIEW_SHA = 'f0ba7f19d2cc478d951eaeebec9d405da3b7405f51e24196a4a9ecf54370962f'
STAGE_TERMINAL = Path('/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001/reader-stage-attempt/evidence/stage-terminal.json')
STAGE_TERMINAL_SHA = '99deb270fbed1f178996a068a4dc6efef8fef3ad640d7870d0a3b1932bc88ca7'
STAGE_PLAN_SHA = 'a5ee5e9812c4ab5d0e37b7fe99aec4f334dcb583668ad0489f267f7e2258478b'
READER_CONTROLLER = LOCAL / 'reader-successor-controller-0003'
READER_CONTROLLER_FREEZE_SHA = 'cc8a24271b58551b82a295a3cd8faaddd068e4bc6f50e6430388c5dc69f51b11'
READER_CONTROLLER_REVIEW = LOCAL / 'READER-SUCCESSOR-CONTROLLER-INDEPENDENT-STATIC-REVIEW-0003.md'
READER_CONTROLLER_REVIEW_SHA = 'b5dc21c8f52d420203ee41a9c6898a9a5a198e94d97ef59ec5cb5916918b1351'
READER_RELEASE = LOCAL / 'reader-successor-docker-release-0002'
READER_RELEASE_FREEZE_SHA = 'e704223f64073c2520813f38349072549c46a82d497107911c1860ee97bb2ea6'
READER_RELEASE_REVIEW = LOCAL / 'READER-SUCCESSOR-DOCKER-RELEASE-INDEPENDENT-STATIC-REVIEW-0002.md'
READER_RELEASE_REVIEW_SHA = 'bd5a2fd3af12c398bd43b3e360d73a22a810c37a9abe3659423c5a44629639eb'
READER_IMAGE = 'sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874'
READER_NAME = 'cal-reader-only-20261020-0002-successor-0001'
SOURCE_REVIEW_SHA = '599d7cca4b87b98809e33636ad1326bc60ddba589123ec5a0a0c5e00b58a4440'
NATIVE_SHA = 'fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'
VERIFIER_SHA = 'aa883d697a9cfec02a4671da2a76d10c5c4b23ef0a93e63c78f31ac0667ff23b'
ACTUAL_REVIEW = LOCAL / 'context-successor-reader-independent-effect-review-0001/review.json'
ACTUAL_REVIEW_SHA = 'c2f9d0307610d281784c4d3c86211dbc37bd6a5843130647ff1718561957f295'
ACTUAL_REVIEW_NARRATIVE = LOCAL / 'context-successor-reader-independent-effect-review-0001/REVIEW.md'
ACTUAL_REVIEW_NARRATIVE_SHA = 'eabef8ab2f02cc3f998a5e8d1bec78964126ec510b730e215c8c256bc55ee2a7'
ACTUAL_EXTERNAL = Path('/home/vlad_/.local/state/cyberalchemy-lab-observations/reader-successor-docker-release-0002/result.json')
ACTUAL_EXTERNAL_SHA = '5c421de1f92545ba29efaa2cb5d49d8f51ff8773a979173f8ef21bee4e3b95c5'
ACTUAL_INTENT_SHA = '54c90ff2d0226e26c4e688fa5f63e93b61a3a04338713664e606c1e954139a16'
ACTUAL_STDOUT_SHA = '29a0d5e612bead7c1c5e2960f3dd78e7e03807287bc0832e5ea9f4267ef8ffa4'
ACTUAL_STDERR_SHA = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
ACTUAL_ATTEMPT = Path('/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001/reader-attempt')
ACTUAL_FINAL_SHA = '8a4a1bf63afe5351e1f6184038e2ec13cf30e855d85c51b145122a19efcb21aa'
ACTUAL_PROVISIONAL_SHA = '5d8748a5efc5e2108c477263797bec3282968d1bb9fdfb36f2e0a8efd151bd9f'
ACTUAL_CONSUMED_SHA = '0b8d69fd60033b61d0275b30750601c66bd83bef7c843fec33611c7abf82d932'
ACTUAL_RECEIPT_SHA = 'd389c46467b2cbac48e6cec3ec9a8d58c7f036516576b718c6f796a1586eedf2'
ACTUAL_CREATE_RESPONSE_SHA = 'b3b086a37441fc87d541ce39fecb5a3dba77989dd7e9dd3a50541340e4277aff'
ACTUAL_CREATE_OBSERVATION_SHA = '398f5c3d90b0fcce1e15eb9c5bb0ca50d81e9986faebe38f7495dc31cd9f6e5b'
ACTUAL_CID_RECEIPT_SHA = '600520d26acdfc4cfec13f332e290d8cddc1c454e7c4c8207c91dc8f89176f4d'
ACTUAL_PRE_REMOVAL_SHA = '3c19151c321feda4a7111f351631dcf34cc9e8aa85394c0c39bc464139070368'


class Refused(ValueError):
    pass


def need(ok: bool, code: str) -> None:
    if not ok:
        raise Refused(code)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def encoded(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def parse(raw: bytes):
    def pairs(rows):
        result = {}
        for key, value in rows:
            need(key not in result, 'DUPLICATE_JSON_KEY')
            result[key] = value
        return result
    try:
        return json.loads(raw, object_pairs_hook=pairs,
                          parse_constant=lambda _:
                          (_ for _ in ()).throw(Refused('NONFINITE_JSON')))
    except (ValueError, TypeError, UnicodeError, RecursionError) as error:
        raise Refused('INVALID_JSON') from error


def frozen_mapper_release():
    freeze_raw = (MAPPER_RELEASE / 'freeze.json').read_bytes()
    need(sha(freeze_raw) == MAPPER_FREEZE_SHA and
         sha(MAPPER_REVIEW.read_bytes()) == MAPPER_REVIEW_SHA,
         'MAPPER_RELEASE_FREEZE_OR_REVIEW_DRIFT')
    freeze = parse(freeze_raw)
    need(freeze['effect_enabled'] is False and len(freeze['file_bindings']) == 3,
         'MAPPER_RELEASE_CONTRACT_DRIFT')
    for row in freeze['file_bindings']:
        member = MAPPER_RELEASE / Path(row['path']).name
        need(member.is_file() and not member.is_symlink() and
             member.stat().st_size == row['size'] and
             sha(member.read_bytes()) == row['sha256'],
             'MAPPER_RELEASE_MEMBER_DRIFT')
    spec = importlib.util.spec_from_file_location('cal_reviewed_mapper_release',
                                                   MAPPER_RELEASE / 'release.py')
    need(spec is not None and spec.loader is not None, 'MAPPER_RELEASE_IMPORT')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def stage_basis() -> dict:
    """Verify already observed Reader stage metadata without opening files in root."""
    review_raw = STAGE_REVIEW.read_bytes()
    terminal_raw = STAGE_TERMINAL.read_bytes()
    need(sha(review_raw) == STAGE_REVIEW_SHA and
         sha(terminal_raw) == STAGE_TERMINAL_SHA,
         'READER_STAGE_REVIEW_OR_TERMINAL_DRIFT')
    review, terminal = parse(review_raw), parse(terminal_raw)
    need(type(review) is dict and type(terminal) is dict and
         review.get('schema') == 'lab-reader-successor-stage-effect-review/v1' and
         review.get('verdict') == 'PASS_BOUNDED_STAGE_ONLY_EFFECT' and
         review.get('reader_effect') == 'NOT_RUN' and
         review.get('file_count') == 986 and
         review.get('source_effect_review_sha256') == SOURCE_REVIEW_SHA and
         review.get('terminal_sha256') == STAGE_TERMINAL_SHA and
         review.get('stage_plan_sha256') == STAGE_PLAN_SHA and
         terminal.get('overall') == 'OBSERVED_STAGE_ONLY' and
         terminal.get('reader_effect') == 'NOT_RUN' and
         terminal.get('input_files') == 986 and
         terminal.get('no_retry') is True and
         terminal.get('reader_manifest_sha256') == review.get('reader_manifest_sha256') and
         terminal.get('stage_plan_sha256') == review.get('stage_plan_sha256'),
         'READER_STAGE_EFFECT_JOIN')
    need(sha((READER_CONTROLLER / 'freeze.json').read_bytes()) ==
         READER_CONTROLLER_FREEZE_SHA and
         sha(READER_CONTROLLER_REVIEW.read_bytes()) == READER_CONTROLLER_REVIEW_SHA,
         'READER_CONTROLLER_CONTRACT_DRIFT')
    release_raw = (READER_RELEASE / 'freeze.json').read_bytes()
    need(sha(release_raw) == READER_RELEASE_FREEZE_SHA and
         sha(READER_RELEASE_REVIEW.read_bytes()) == READER_RELEASE_REVIEW_SHA,
         'READER_RELEASE_FREEZE_OR_REVIEW_DRIFT')
    release_freeze = parse(release_raw)
    need(release_freeze.get('controller_freeze_sha256') ==
         READER_CONTROLLER_FREEZE_SHA and
         release_freeze.get('stage_effect_review_sha256') == STAGE_REVIEW_SHA and
         len(release_freeze.get('file_bindings', [])) == 4,
         'READER_RELEASE_CONTRACT_DRIFT')
    for row in release_freeze['file_bindings']:
        member = READER_RELEASE / Path(row['path']).name
        need(member.is_file() and not member.is_symlink() and
             member.stat().st_size == row['size'] and
             sha(member.read_bytes()) == row['sha256'],
             'READER_RELEASE_MEMBER_DRIFT')
    return review


def strict_actual_external(raw: bytes) -> dict:
    """Check the actual observer schema before any compatibility projection."""
    result = parse(raw)
    need(type(result) is dict and
         result.get('schema') == 'reader-successor-docker-external-observation/v1' and
         type(result.get('os_exit_code')) is int and result['os_exit_code'] == 0 and
         result.get('retry_allowed') is False and
         result.get('process_error') is None and
         result.get('freeze_sha256') == READER_RELEASE_FREEZE_SHA and
         result.get('review_sha256') == READER_RELEASE_REVIEW_SHA and
         type(result.get('stderr_size')) is int and result['stderr_size'] == 0 and
         result.get('stderr_sha256') == sha(b'') and
         type(result.get('stdout_size')) is int and result['stdout_size'] > 0,
         'ACTUAL_READER_EXTERNAL_OBSERVER')
    return result


def _pinned(path: Path, digest: str, ceiling: int) -> bytes:
    need(path.is_file() and not path.is_symlink(), 'ACTUAL_READER_MEMBER_TYPE')
    info = path.lstat()
    need(stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid() and
         info.st_gid == os.getgid() and info.st_nlink == 1 and
         info.st_size <= ceiling, 'ACTUAL_READER_MEMBER_METADATA')
    raw = path.read_bytes()
    need(len(raw) == info.st_size and sha(raw) == digest and
         path.lstat().st_ino == info.st_ino and
         path.lstat().st_dev == info.st_dev,
         'ACTUAL_READER_MEMBER_DIGEST_OR_ATTACHMENT')
    return raw


def _actual_effect_bytes() -> dict[str, bytes]:
    evidence = ACTUAL_ATTEMPT / 'evidence'
    observer = ACTUAL_EXTERNAL.parent
    return {
        'review': _pinned(ACTUAL_REVIEW, ACTUAL_REVIEW_SHA, 16 * 1024),
        'external': _pinned(ACTUAL_EXTERNAL, ACTUAL_EXTERNAL_SHA, 16 * 1024),
        'intent': _pinned(observer / 'intent.json', ACTUAL_INTENT_SHA, 16 * 1024),
        'stdout': _pinned(observer / 'stdout.bin', ACTUAL_STDOUT_SHA, 16 * 1024),
        'stderr': _pinned(observer / 'stderr.bin', ACTUAL_STDERR_SHA, 16 * 1024),
        'final': _pinned(evidence / 'reader-once.final.json', ACTUAL_FINAL_SHA, 16 * 1024),
        'provisional': _pinned(evidence / 'reader-once.terminal.json',
                               ACTUAL_PROVISIONAL_SHA, 16 * 1024),
        'consumed': _pinned(evidence / 'reader-attempt-consumed.json',
                            ACTUAL_CONSUMED_SHA, 16 * 1024),
        'receipt': _pinned(ACTUAL_ATTEMPT / 'reader-output/receipt.json',
                           ACTUAL_RECEIPT_SHA, 16 * 1024),
        'create_response': _pinned(evidence / 'reader-create-response.json',
                                   ACTUAL_CREATE_RESPONSE_SHA, 16 * 1024),
        'create_observation': _pinned(evidence / 'reader-create-observation.json',
                                      ACTUAL_CREATE_OBSERVATION_SHA, 16 * 1024),
        'cid_receipt': _pinned(evidence / 'reader-container-id.json',
                               ACTUAL_CID_RECEIPT_SHA, 16 * 1024),
        'pre_removal': _pinned(evidence / 'reader-pre-removal.json',
                               ACTUAL_PRE_REMOVAL_SHA, 16 * 1024),
    }


def _marker_observed() -> None:
    marker = ACTUAL_ATTEMPT / 'evidence/reader-once.finalized'
    try:
        info = marker.lstat()
    except FileNotFoundError as error:
        raise Refused('ACTUAL_READER_FINAL_MARKER_MISSING') from error
    need(stat.S_ISDIR(info.st_mode) and stat.S_IMODE(info.st_mode) == 0o700 and
         info.st_uid == os.getuid() and info.st_gid == os.getgid() and
         not marker.is_symlink() and not list(marker.iterdir()),
         'ACTUAL_READER_FINAL_MARKER')
    for name in ('reader-release-unknown.json', 'reader-prepare-unknown.json'):
        need(not os.path.lexists(ACTUAL_ATTEMPT / name),
             'ACTUAL_READER_UNKNOWN_RELEASE_RECEIPT')


def _validated_actual_reader(raws: dict[str, bytes], stage: dict) -> dict:
    """Bind original independent review and original effect bytes directly."""
    expected = {'review': ACTUAL_REVIEW_SHA, 'external': ACTUAL_EXTERNAL_SHA,
                'intent': ACTUAL_INTENT_SHA, 'stdout': ACTUAL_STDOUT_SHA,
                'stderr': ACTUAL_STDERR_SHA,
                'final': ACTUAL_FINAL_SHA, 'provisional': ACTUAL_PROVISIONAL_SHA,
                'consumed': ACTUAL_CONSUMED_SHA, 'receipt': ACTUAL_RECEIPT_SHA,
                'create_response': ACTUAL_CREATE_RESPONSE_SHA,
                'create_observation': ACTUAL_CREATE_OBSERVATION_SHA,
                'cid_receipt': ACTUAL_CID_RECEIPT_SHA,
                'pre_removal': ACTUAL_PRE_REMOVAL_SHA}
    need(set(raws) == set(expected) and
         all(sha(raws[name]) == digest for name, digest in expected.items()),
         'ACTUAL_READER_ORIGINAL_DIGEST')
    review = parse(raws['review'])
    external = strict_actual_external(raws['external'])
    final, provisional, consumed, receipt = map(parse, (
        raws['final'], raws['provisional'], raws['consumed'], raws['receipt']))
    intent, create, created, cid_record, pre_removal = map(parse, (
        raws['intent'], raws['create_response'], raws['create_observation'],
        raws['cid_receipt'], raws['pre_removal']))
    need(all(type(row) is dict for row in
             (review, final, provisional, consumed, receipt,
              intent, create, created, cid_record, pre_removal)),
         'ACTUAL_READER_RECORD_SHAPE')
    need(intent.get('schema') == 'reader-successor-docker-external-intent/v1' and
         intent.get('argv') == [
             '/usr/bin/python3', '-B',
             str(READER_RELEASE / 'release.py'), '--execute-reviewed-one-shot'] and
         intent.get('freeze_sha256') == READER_RELEASE_FREEZE_SHA and
         intent.get('review_sha256') == READER_RELEASE_REVIEW_SHA and
         intent.get('retry_allowed') is False and
         type(intent.get('started_at_ns')) is int and
         type(external.get('finished_at_ns')) is int and
         external['finished_at_ns'] >= intent['started_at_ns'] and
         external.get('stdout_sha256') == ACTUAL_STDOUT_SHA and
         type(external.get('stdout_size')) is int and
         external['stdout_size'] == len(raws['stdout']) and
         external.get('stderr_sha256') == ACTUAL_STDERR_SHA and
         type(external.get('stderr_size')) is int and
         external['stderr_size'] == len(raws['stderr']) == 0 and
         parse(raws['stdout']) == final,
         'ACTUAL_READER_EXTERNAL_STREAM_JOIN')
    need(review.get('schema') == 'lab-reader-successor-docker-effect-review/v1' and
         review.get('verdict') == 'PASS_BOUNDED_READER_ONLY_EFFECT' and
         review.get('attempt') == str(ACTUAL_ATTEMPT) and
         review.get('stage_effect_review_sha256') == STAGE_REVIEW_SHA and
         review.get('release_freeze_sha256') == READER_RELEASE_FREEZE_SHA and
         review.get('release_review_sha256') == READER_RELEASE_REVIEW_SHA and
         review.get('external_observation_sha256') == ACTUAL_EXTERNAL_SHA and
         review.get('final_sha256') == ACTUAL_FINAL_SHA and
         review.get('provisional_sha256') == ACTUAL_PROVISIONAL_SHA and
         review.get('consumed_sha256') == ACTUAL_CONSUMED_SHA and
         review.get('receipt_sha256') == ACTUAL_RECEIPT_SHA and
         review.get('create_response_sha256') == ACTUAL_CREATE_RESPONSE_SHA and
         review.get('create_observation_sha256') == ACTUAL_CREATE_OBSERVATION_SHA and
         review.get('pre_removal_sha256') == ACTUAL_PRE_REMOVAL_SHA and
         review.get('reader_manifest_sha256') == stage['reader_manifest_sha256'] and
         type(review.get('os_exit_code')) is int and review['os_exit_code'] == 0 and
         review.get('no_retry') is True and
         review.get('container_absent') is True and
         review.get('authority_effect') == 'none' and
         type(review.get('stage_files_verified')) is int and
         review['stage_files_verified'] == 986,
         'ACTUAL_INDEPENDENT_READER_EFFECT_JOIN')
    label = final.get('attempt_label')
    need(type(label) is str and len(label) == 32 and
         all(c in '0123456789abcdef' for c in label),
         'ACTUAL_READER_ATTEMPT_LABEL')
    container_id = review.get('container_id')
    need(type(container_id) is str and len(container_id) == 64 and
         all(c in '0123456789abcdef' for c in container_id) and
         final.get('container_id') == container_id and
         create.get('schema_version') == 'lab-reader-docker-create-response/v1' and
         create.get('attempt_label') == label and
         create.get('container_name') == READER_NAME and
         create.get('image_id') == READER_IMAGE and
         create.get('stdout_cid') == container_id and
         type(create.get('returncode')) is int and create['returncode'] == 0 and
         create.get('error_class') is None and
         created.get('schema_version') == 'lab-reader-docker-create-observation/v1' and
         created.get('container_id') == container_id and
         created.get('identity') == 'MATCH' and
         created.get('state') == 'PRESENT' and
         created.get('running') is False and
         cid_record == {'attempt_label': label, 'container_id': container_id,
                        'image_id': READER_IMAGE, 'name': READER_NAME} and
         pre_removal.get('schema_version') == 'lab-reader-docker-pre-removal/v1' and
         type(pre_removal.get('daemon_wait_exit')) is int and
         pre_removal['daemon_wait_exit'] == 0 and
         type(pre_removal.get('container')) is dict and
         pre_removal['container'].get('id') == container_id and
         pre_removal['container'].get('attempt_label') == label and
         pre_removal['container'].get('name') == '/' + READER_NAME and
         pre_removal['container'].get('image_id') == READER_IMAGE and
         pre_removal['container'].get('running') is False and
         pre_removal['container'].get('status') == 'exited' and
         type(pre_removal['container'].get('exit_code')) is int and
         pre_removal['container']['exit_code'] == 0,
         'ACTUAL_READER_CONTAINER_IDENTITY_JOIN')
    need(final.get('schema_version') == 'lab-reader-only-docker-final/v1' and
         final.get('finalization') == 'CLOSED_AND_COMMITTED' and
         final.get('overall') == final.get('operation') == final.get('cleanup') == 'PASS' and
         final.get('reader_effect') == 'DISPOSABLE_READER_DIAGNOSTIC' and
         final.get('no_retry') is True and
         final.get('container_name') == READER_NAME and
         final.get('provisional_sha256') == ACTUAL_PROVISIONAL_SHA and
         final.get('receipt_sha256') == ACTUAL_RECEIPT_SHA and
         final.get('absent') is True and
         final.get('forced_cleanup') is False and
         final.get('daemon_exit_consistent') is True and
         type(final.get('daemon_exit')) is int and final['daemon_exit'] == 0 and
         type(final.get('client_exit')) is int and final['client_exit'] == 0 and
         final.get('postclose_inputs') == 'PASS' and
         final.get('output_attachment') == 'PASS' and
         provisional.get('schema_version') == 'lab-reader-only-docker-terminal/v1' and
         provisional.get('overall') == 'UNKNOWN' and
         provisional.get('candidate_overall') == 'PASS' and
         provisional.get('finalization') == 'PENDING_OUTER_CLOSES' and
         provisional.get('attempt_label') == label and
         consumed.get('schema_version') == 'lab-reader-only-consumed/v1' and
         consumed.get('state') == 'CONSUMED_NO_RETRY' and
         consumed.get('attempt_label') == label and
         consumed.get('container_name') == READER_NAME and
         consumed.get('image_id') == READER_IMAGE and
         consumed.get('reader_manifest_sha256') == stage['reader_manifest_sha256'] and
         receipt.get('schema_version') == 'lab-disposable-reader-receipt/v1-private' and
         receipt.get('authority_effect') == 'none' and
         receipt.get('actual_owner_outcome') is None and
         receipt.get('reader_manifest_sha256') == stage['reader_manifest_sha256'] and
         review.get('source_package_manifest_sha256') ==
         receipt.get('source_package_manifest_sha256'),
         'ACTUAL_READER_CLOSED_EVIDENCE_JOIN')
    return {'review': review, 'external': external, 'final': final,
            'receipt': receipt, 'label': label}


def select_actual(*, now) -> dict:
    """Directly select the actual independent Reader review; no schema bridge."""
    need(sha(ACTUAL_REVIEW_NARRATIVE.read_bytes()) ==
         ACTUAL_REVIEW_NARRATIVE_SHA, 'ACTUAL_READER_NARRATIVE_DRIFT')
    _marker_observed()
    raws = _actual_effect_bytes()
    release = frozen_mapper_release()
    stage = stage_basis()
    actual = _validated_actual_reader(raws, stage)
    mapper = release.frozen_selector()
    reader_release = release.frozen_reader_release()
    reader = mapper.reader_adapter()
    source_root = release.STATE / 'source-attempt/root'
    source_raw = (reader.PROFILE / 'generated' / reader.SOURCE /
                  'source-manifest.json').read_bytes()
    package = source_root / reader.SOURCE / 'packages/0001'
    package_raw = (package / 'manifest.json').read_bytes()
    period_raw = (package / 'period.json').read_bytes()
    source_terminal_raw = (release.STATE /
        'source-attempt/evidence/source-once.terminal.json').read_bytes()
    source_review_raw = (LOCAL /
        'context-successor-source-independent-effect-review-0001/review.json').read_bytes()
    need(sha(source_review_raw) == SOURCE_REVIEW_SHA and
         sha(source_raw) == reader.SOURCE_MANIFEST_SHA and
         sha(package_raw) == actual['review']['source_package_manifest_sha256'] and
         actual['receipt']['source_manifest_sha256'] == reader.SOURCE_MANIFEST_SHA,
         'ACTUAL_SOURCE_READER_DYNAMIC_JOIN')
    reader_selected = reader_release.select_stage(
        source_raw, package_raw, source_terminal_raw, period_raw,
        source_review_raw, SOURCE_REVIEW_SHA, now)
    reader_manifest_raw = (release.READER_STAGE_ROOT / mapper.READER /
                           'source-manifest.json').read_bytes()
    need(reader_manifest_raw ==
         reader_selected['generated_reader_bytes'][mapper.READER + '/source-manifest.json'] and
         sha(reader_manifest_raw) == stage['reader_manifest_sha256'] and
         reader_selected['plan_sha256'] == STAGE_PLAN_SHA,
         'ACTUAL_READER_MANIFEST_DYNAMIC_JOIN')
    pins = {'source': reader.SOURCE_MANIFEST_SHA,
            'package': sha(package_raw), 'reader': sha(reader_manifest_raw)}
    roles = {name: mapper.project_role(name, (mapper.REPO / mapper.OLD / name).read_bytes(),
                                       pins) for name in mapper.PREIMAGES}
    reader_manifest = parse(reader_manifest_raw)
    rows = reader_manifest['files'] + [
        {'path': mapper.READER + '/source-manifest.json', 'sha256': pins['reader']}]+[
        {'path': mapper.MAPPER + '/' + name, 'sha256': sha(raw)}
        for name, raw in roles.items()]
    need(len(rows) == len({row['path'] for row in rows}) == 953,
         'ACTUAL_MAPPER_PUBLIC_CLOSURE')
    mapper_manifest = {
        'schema_version': 'lab-docker-distinct-mapper-source/v1-candidate',
        'authority_effect': 'none', 'actual_owner_outcome': None,
        'fixture_only': True, 'qualification': False,
        'environment': {'python': '3.14.4', 'jsonschema': '4.23.0',
                        'cryptography': '46.0.5'},
        'original_source_binding': {'path': mapper.SOURCE + '/source-manifest.json',
                                    'sha256': pins['source']},
        'original_package_binding': {'path': mapper.SOURCE + '/packages/0001/manifest.json',
                                     'sha256': pins['package']},
        'adapter_source_binding': {'path': mapper.READER + '/source-manifest.json',
                                   'sha256': pins['reader']},
        'selected_native_executable': {'path': '/attempt/input/lab-context-native-reader',
                                       'sha256': NATIVE_SHA},
        'files': sorted(rows, key=lambda row: row['path'])}
    mapper_raw = mapper.encoded(mapper_manifest)
    output_contract = mapper.verify_output_template()
    generated = {mapper.MAPPER + '/' + name: raw for name, raw in roles.items()}
    generated[mapper.MAPPER + '/source-manifest.json'] = mapper_raw
    files = []
    for row in reader_selected['plan']['files']:
        files.append({'path': row['path'], 'sha256': row['sha256'],
                      'source_path': str(release.READER_STAGE_ROOT / row['path']),
                      'source_mode': row['target_mode'],
                      'target_mode': row['target_mode'],
                      'source_kind': 'reviewed-reader-stage'})
    for name, raw in generated.items():
        files.append({'path': name, 'sha256': sha(raw),
                      'source_path': None, 'source_mode': None,
                      'target_mode': '0444', 'source_kind': 'generated-mapper'})
    files.sort(key=lambda row: row['path'])
    need(len(files) == len({row['path'] for row in files}) == 991 and
         len(mapper.OUTPUT_LEAVES) == 55,
         'ACTUAL_MAPPER_STAGE_CLOSURE')
    plan = {
        'schema': 'lab-mapper-successor-stage-plan/v2-direct-reader-review',
        'status': 'SELECTION_ONLY_EFFECT_DISABLED', 'effect': 'NOT_RUN',
        'archive_body_opened': False, 'no_retry': True,
        'reader_stage_root': str(release.READER_STAGE_ROOT),
        'mapper_attempt': str(release.ATTEMPT),
        'mapper_root': str(release.ATTEMPT_ROOT),
        'container_name': release.CONTAINER_NAME, 'image': release.IMAGE,
        'source_effect_review_sha256': SOURCE_REVIEW_SHA,
        'reader_effect_review_sha256': ACTUAL_REVIEW_SHA,
        'reader_external_observation_sha256': ACTUAL_EXTERNAL_SHA,
        'reader_stage_effect_review_sha256': STAGE_REVIEW_SHA,
        'reader_stage_plan_sha256': STAGE_PLAN_SHA,
        'source_package_manifest_sha256': pins['package'],
        'reader_manifest_sha256': pins['reader'],
        'mapper_manifest_sha256': sha(mapper_raw),
        'native_sha256': NATIVE_SHA,
        'verifier_template_sha256': VERIFIER_SHA,
        'expected_package_members': list(mapper.OUTPUT_LEAVES),
        'output_acceptance_contract': {
            'verifier_rebound': False,
            'leaf_count': 55, 'semantic_leaves': 25, 'governance_leaves': 25,
            'node_count': 15, 'edge_count': 10, 'exact_governance_joins': 25,
            'native_seal_processes': 2, 'actual_cold_native_read_processes': 2,
            'cold_native_replay_byte_parity': True,
            'same_signed_source_cut': True,
            'native_domain_mapping_supplied': True,
            'context_or_ontology_view_carriers_generated': False,
            'authority_effect': 'none', 'actual_owner_outcome': None,
            'task_complete': False},
        'selector_freeze_sha256': release.SELECTOR_FREEZE_SHA,
        'selector_review_sha256': release.SELECTOR_REVIEW_SHA,
        'files': files}
    names = {row['path'] for row in files}
    directories = set()
    for name in names:
        parts = name.split('/')
        directories.update('/'.join(parts[:i]) for i in range(1, len(parts)))
    empty_receipts = mapper.SOURCE + '/receipts'
    need(len(directories) == 931 and mapper.MAPPER in directories and
         empty_receipts not in directories,
         'ACTUAL_READER_STAGE_DIRECTORY_GRAPH')
    directories.add(empty_receipts)
    directories.add(mapper.MAPPER + '/packages')
    need(len(directories) == 933,
         'ACTUAL_MAPPER_STAGE_DIRECTORY_GRAPH')
    copy = {
        'status': 'NOT_RUN', 'effect_enabled': False,
        'attempt': str(release.ATTEMPT), 'attempt_mode': '0700',
        'source_root': str(release.READER_STAGE_ROOT),
        'destination_root': str(release.ATTEMPT_ROOT),
        'source_rows': 986, 'generated_mapper_rows': 5,
        'input_files': 991, 'source_directories': 931,
        'target_directories': 933,
        'target_directory_names': sorted(directories),
        'private_source_package_rows': sum(
            row['target_mode'] == '0600' for row in files),
        'exclusive_no_retry': True,
        'nofollow_held_copy': 'REQUIRED_NOT_RUN',
        'pre_and_post_inventory_hash_mode_identity': 'REQUIRED_NOT_RUN',
        'empty_mapper_packages_0700': True,
        'package_0001_must_be_absent': True,
        'native_executable_sha256': NATIVE_SHA,
        'native_copy_target': str(release.ATTEMPT / 'input/lab-context-native-reader'),
        'reader_stage_effect_review_sha256': STAGE_REVIEW_SHA,
        'reader_effect_review_sha256': ACTUAL_REVIEW_SHA,
        'source_plan_sha256': sha(encoded(plan))}
    need(copy['private_source_package_rows'] == 37,
         'ACTUAL_PRIVATE_SOURCE_MODE_CLOSURE')
    verifier = {
        'status': 'TEMPLATE_ONLY_NOT_REBOUND',
        'template_sha256': VERIFIER_SHA, 'native_sha256': NATIVE_SHA,
        'expected_package_members': list(mapper.OUTPUT_LEAVES),
        'expected_checks': plan['output_acceptance_contract'],
        'output_package': str(release.ATTEMPT_ROOT / mapper.MAPPER / 'packages/0001'),
        'effect_verifier_adapted': False, 'actual_output_verified': False}
    provenance = {
        'independent_reader_review_sha256': ACTUAL_REVIEW_SHA,
        'independent_reader_review_narrative_sha256': ACTUAL_REVIEW_NARRATIVE_SHA,
        'original_external_observation_sha256': ACTUAL_EXTERNAL_SHA,
        'original_external_intent_sha256': ACTUAL_INTENT_SHA,
        'original_external_stdout_sha256': ACTUAL_STDOUT_SHA,
        'original_external_stderr_sha256': ACTUAL_STDERR_SHA,
        'original_final_sha256': ACTUAL_FINAL_SHA,
        'original_provisional_sha256': ACTUAL_PROVISIONAL_SHA,
        'original_consumed_sha256': ACTUAL_CONSUMED_SHA,
        'original_receipt_sha256': ACTUAL_RECEIPT_SHA,
        'original_create_response_sha256': ACTUAL_CREATE_RESPONSE_SHA,
        'original_create_observation_sha256': ACTUAL_CREATE_OBSERVATION_SHA,
        'original_cid_receipt_sha256': ACTUAL_CID_RECEIPT_SHA,
        'original_pre_removal_sha256': ACTUAL_PRE_REMOVAL_SHA,
        'review_schema': actual['review']['schema'],
        'review_verdict': actual['review']['verdict'],
        'compatibility_projection_used': False,
        'effect_gate': 'INDEPENDENT_STATIC_REVIEW_AND_NEW_EFFECT_RELEASE_REQUIRED'}
    return {'status': 'ACTUAL_READER_DIRECT_MAPPER_PLAN_PENDING_STATIC_REVIEW',
            'effect_enabled': False, 'stage_plan': plan,
            'stage_plan_sha256': sha(encoded(plan)),
            'copy_plan': copy, 'copy_plan_sha256': sha(encoded(copy)),
            'verifier_plan': verifier,
            'verifier_plan_sha256': sha(encoded(verifier)),
            'actual_reader_provenance': provenance,
            'generated_mapper_bytes': generated}

def execute_stage(*_args, **_kwargs):
    raise Refused('EFFECT_DISABLED_MAPPER_STAGE_RELEASE_REQUIRED')


def execute_mapper(*_args, **_kwargs):
    raise Refused('EFFECT_DISABLED_MAPPER_DOCKER_RELEASE_REQUIRED')


def verify_output(*_args, **_kwargs):
    raise Refused('EFFECT_DISABLED_REBOUND_55_LEAF_VERIFIER_REQUIRED')


