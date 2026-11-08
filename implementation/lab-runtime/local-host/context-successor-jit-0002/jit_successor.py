"""Inert Context JIT successor selection for the durable development family.

Only public Source receipts, period and manifests are read. No Source archive,
Reader signed view, issuer, key, private root, policy leaf, or Docker effect is
opened or created. A future Mapper effect must be independently reviewed.
"""
from __future__ import annotations

import base64
import datetime as dt
import hashlib
import importlib.util
import json
import os
import re
import stat
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

REPO = Path('/home/vlad_/projects/CyberAlchemy-lab')
LOCAL = REPO / 'implementation/lab-runtime/local-host'
FAMILY = Path('/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001')
SOURCE_ATTEMPT = FAMILY / 'source-attempt'
CONTEXT_ATTEMPT = FAMILY / 'context-attempt'
CONTEXT_ROOT = CONTEXT_ATTEMPT / 'root'
PRIVATE_ROOT = FAMILY / 'context-jit-private-attempt-0001'
BASE = 'product/lab/release-candidates/v1/interface/'
SOURCE_ROLE = BASE + 'docker-source-20261020-0002'
CONTEXT_ROLE = BASE + 'docker-context-20261020-0002'
SOURCE_PACKAGE = SOURCE_ATTEMPT / 'root' / SOURCE_ROLE / 'packages/0001'
SOURCE_MANIFEST = SOURCE_ATTEMPT / 'root' / SOURCE_ROLE / 'source-manifest.json'
SOURCE_REVIEW = LOCAL / 'context-successor-source-independent-effect-review-0001/review.json'
SOURCE_TERMINAL = SOURCE_ATTEMPT / 'evidence/source-once.terminal.json'
SOURCE_REVIEW_SHA = '599d7cca4b87b98809e33636ad1326bc60ddba589123ec5a0a0c5e00b58a4440'
SOURCE_TERMINAL_SHA = '66c51614278e38e061eac7cc195288444efa176f36f13dd4243462faaa34c7b9'
SOURCE_MANIFEST_SHA = '2843a67fd28a295f5c175b8d8c2b31f701040bb8d7dedeade8d76bbdf057d1d1'
SOURCE_PACKAGE_SHA = 'bdb5eac92cbb3f96857c4d2ccb00880441d55fb8f1dbbeb5cdaae8d81c720653'
SOURCE_PERIOD_SHA = '3ff862090a38b346a384001c2d87da7cf648f18726fb056653a0fb4df40473ba'
PERIOD_REF = 'protocol:R03-docker-source-20261020-0002-period/v1'
PRINCIPAL_REF = 'principal:R03-docker-source-20261020-0002'
EXPECTED_SCOPE = 'scope:cyberalchemy-lab-first-agent-episode'
CONTEXT_SELECTOR = LOCAL / 'context-successor-selector-0001/adapter.py'
CONTEXT_SELECTOR_SHA = '23177529919f1737f94b08daa18e8710cc51f55d72e6afa71365c0c5d5ec6929'
CONTEXT_SELECTOR_FREEZE = LOCAL / 'context-successor-selector-0001/freeze.json'
CONTEXT_SELECTOR_FREEZE_SHA = 'd4aed1b9047f0e125dc13b3c248b75c63e76150dcf49e45183a8deb2a4aece6d'
PREDECESSOR_FREEZES = {
    'context-jit-policy-0002/freeze.json': 'e0286814e0e34770a0fa4b7fe0d9ab08161e5ea3264386c9f0b6cb76f201a391',
    'context-jit-provision-0001/freeze.json': 'fab03502c79f807eb33c1617cae3480d9a1e3fe2d6e26d2ef6dcb9a0a7b1d522',
    'context-jit-effect-0003/freeze.json': 'aad1b0fe361629363e18c535205a37c44bdcba996d7464b58d74f9fea5792d99',
    'context-docker-release-0001/freeze.json': 'f95ef5db94679793de5cf75578ef36b378f645245d27bf336f549ed1431aaab7',
    'context-successor-jit-0001/freeze.json': '7335a0880a8e6f2c3269d75c6a983f69b64f630f9e6a4b9a4230e4ad4ed48840',
    'CONTEXT-SUCCESSOR-JIT-INDEPENDENT-STATIC-REVIEW-0001.md': '3f24cea8e7c8174aec102000a1fd0a32e1051ef0c72f06c92da10ed346736a09',
}
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


def parse(raw, limit=2 * 1024 * 1024, *, canonical_required=True):
    need(type(raw) is bytes and 0 < len(raw) <= limit, 'BOUNDED_JSON_REQUIRED')
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


def public_leaf(path, pin, maximum=2 * 1024 * 1024):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
             0 < before.st_size <= maximum, 'PUBLIC_LEAF_SHAPE')
        raw = os.read(fd, before.st_size + 1)
        after = os.fstat(fd)
        need(len(raw) == before.st_size and
             (before.st_dev, before.st_ino, before.st_mode, before.st_size) ==
             (after.st_dev, after.st_ino, after.st_mode, after.st_size) and
             sha(raw) == pin, 'PUBLIC_LEAF_PIN')
        return raw
    finally:
        os.close(fd)


def utc(value):
    need(type(value) is str, 'UTC_INSTANT_REQUIRED')
    instant = dt.datetime.fromisoformat(value)
    need(instant.tzinfo is not None and instant.utcoffset() == dt.timedelta(),
         'UTC_INSTANT_REQUIRED')
    return instant


def source_preflight(now=None):
    """Read exact public Source effect evidence; never open branch.snapshot."""
    now = now or dt.datetime.now(dt.timezone.utc)
    need(type(now) is dt.datetime and now.tzinfo is not None and
         now.utcoffset() == dt.timedelta(), 'CURRENT_UTC_REQUIRED')
    for relative, pin in PREDECESSOR_FREEZES.items():
        public_leaf(LOCAL / relative, pin)
    review = parse(public_leaf(SOURCE_REVIEW, SOURCE_REVIEW_SHA, 16 * 1024))
    terminal = parse(public_leaf(SOURCE_TERMINAL, SOURCE_TERMINAL_SHA, 64 * 1024),
                     canonical_required=False)
    manifest = parse(public_leaf(SOURCE_PACKAGE / 'manifest.json', SOURCE_PACKAGE_SHA))
    source_manifest_raw = public_leaf(SOURCE_MANIFEST, SOURCE_MANIFEST_SHA)
    source_manifest = parse(source_manifest_raw)
    period = parse(public_leaf(SOURCE_PACKAGE / 'period.json', SOURCE_PERIOD_SHA, 16 * 1024),
                   16 * 1024)
    need(review == {'schema':'lab-successor-source-effect-review/v1',
                    'verdict':'PASS_BOUNDED_SOURCE_ONLY_EFFECT',
                    'attempt':str(SOURCE_ATTEMPT),
                    'source_manifest_sha256':SOURCE_MANIFEST_SHA,
                    'package_manifest_sha256':SOURCE_PACKAGE_SHA,
                    'terminal_sha256':SOURCE_TERMINAL_SHA},
         'SOURCE_INDEPENDENT_EFFECT_REVIEW_JOIN')
    need(terminal.get('overall') == terminal.get('operation') == terminal.get('cleanup') == 'PASS' and
         terminal.get('source_effect') == 'DEVELOPMENT_SOURCE_ONLY' and
         terminal.get('package_manifest_sha256') == SOURCE_PACKAGE_SHA and
         terminal.get('daemon_exit') == terminal.get('client_exit') == 0 and
         terminal.get('postclose_inputs') == terminal.get('output_attachment') == 'PASS',
         'SOURCE_HOST_TERMINAL_JOIN')
    need(manifest.get('schema_version') == 'lab-owned-current-participation-package/v1-candidate' and
         manifest.get('authority_effect') == 'none' and
         manifest.get('actual_owner_outcome') is None and
         manifest.get('source_manifest_binding') ==
         {'path':SOURCE_ROLE+'/source-manifest.json','sha256':SOURCE_MANIFEST_SHA} and
         manifest.get('period_binding') ==
         {'path':SOURCE_ROLE+'/packages/0001/period.json','sha256':SOURCE_PERIOD_SHA} and
         {'path':SOURCE_ROLE+'/packages/0001/period.json','sha256':SOURCE_PERIOD_SHA}
         in manifest.get('files', []), 'SOURCE_PERIOD_PACKAGE_JOIN')
    need(source_manifest.get('schema_version') == 'lab-distinct-legacy-typed-v3-fixture-source/v1-candidate' and
         source_manifest.get('authority_effect') == 'none' and
         source_manifest.get('actual_owner_outcome') is None,
         'CURRENT_SOURCE_MANIFEST_CONTENT')
    start, end = utc(period['not_before']), utc(period['expires_at'])
    need(period.get('schema_version') == 'lab-owned-absolute-participation-period/v1-candidate' and
         period.get('period_ref') == PERIOD_REF and
         period.get('principal_ref') == PRINCIPAL_REF and
         period.get('authority_effect') == 'none' and
         period.get('actual_owner_outcome') is None and
         period.get('episode_contract_binding') ==
         {'path':SOURCE_ROLE+'/episode-contract.json',
          'sha256':'0347227ff0730dd154448ca4b1ec0cae84fe6d068a48020e6a14c9f54ea1d36f'} and
         end-start == dt.timedelta(hours=24) and start <= now < end,
         'CURRENT_SOURCE_PERIOD_JOIN')
    return {'status':'SOURCE_PUBLIC_EFFECT_REVIEWED',
            'period_ref':PERIOD_REF,'period_start':period['not_before'],
            'period_end':period['expires_at'],'period_sha256':SOURCE_PERIOD_SHA,
            'source_manifest_sha256':SOURCE_MANIFEST_SHA,
            'source_package_manifest_sha256':SOURCE_PACKAGE_SHA,
            'source_effect_review_sha256':SOURCE_REVIEW_SHA,
            'scope_ref':EXPECTED_SCOPE,'scope_attestation':'NOT_OPENED_SIGNED_SOURCE_VIEW',
            'protected_archive_body':'UNREAD'}


def topology():
    """Persistent successor paths, with private policy outside public root."""
    need(CONTEXT_ROOT not in PRIVATE_ROOT.parents and
         PRIVATE_ROOT not in CONTEXT_ROOT.parents and
         CONTEXT_ROOT != PRIVATE_ROOT and
         SOURCE_ATTEMPT != CONTEXT_ATTEMPT,
         'JIT_PRIVATE_PUBLIC_ROOT_OVERLAP')
    return {'context_attempt':str(CONTEXT_ATTEMPT),
            'stage_root':str(CONTEXT_ROOT),
            'context_family_ref':str(CONTEXT_ROOT / CONTEXT_ROLE),
            'source_root':str(CONTEXT_ROOT / SOURCE_ROLE),
            'authorization_path':str(CONTEXT_ROOT / SOURCE_ROLE /
                                      'authorization/context-development.json'),
            'private_root':str(PRIVATE_ROOT),
            'policy_path':str(PRIVATE_ROOT / 'permission.json'),
            'authorization_directory_mode':'0700',
            'authorization_leaf_mode':'0600',
            'private_root_mode':'0700','policy_leaf_mode':'0600',
            'effect':'NOT_RUN'}


def wait_for_mapper(now=None):
    source = source_preflight(now)
    return {'status':'WAIT_INDEPENDENT_MAPPER_EFFECT_AND_SIGNED_SCOPE',
            'source':source,'topology':topology(),
            'mapper_effect_review':'UNSELECTED',
            'authorization_issuer':'UNSELECTED',
            'private_key':'UNCREATED','policy':'UNWRITTEN',
            'docker_effect':'REFUSED'}


def rebind_guarded_build(build):
    """Move only the inert private-root literal into this durable family."""
    need(type(build) is bytes, 'GUARDED_BUILD_BYTES_REQUIRED')
    pattern = rb"^JIT_PRIVATE_ROOT = Path\('[^']+'\)$"
    matches = re.findall(pattern, build, flags=re.MULTILINE)
    need(len(matches) == 1 and matches[0].startswith(b"JIT_PRIVATE_ROOT = Path('/tmp/"),
         'PREDECESSOR_JIT_PRIVATE_ROOT_SPAN')
    replacement = ("JIT_PRIVATE_ROOT = Path('" + str(PRIVATE_ROOT) + "')").encode()
    result = re.sub(pattern, lambda _: replacement, build, count=1,
                    flags=re.MULTILINE)
    need(not any(line.startswith(b"JIT_PRIVATE_ROOT = Path('/tmp/")
                 for line in result.splitlines()) and
         result.count(b'def _t35_effect_refused():') == 1 and
         result.count(b"raise RuntimeError('Generated T35 role effects require the uninstalled T02 custody gate')") == 1,
         'CONTEXT_GUARD_OR_PRIVATE_ROOT_PROJECTION')
    compile(result, CONTEXT_ROLE+'/build.py', 'exec')
    return result


def select_after_mapper(mapper_inputs, *, now=None):
    """Future pure selector; no current Mapper review is supplied or assumed."""
    source = source_preflight(now)
    need(type(mapper_inputs) is dict and
         sha(public_leaf(CONTEXT_SELECTOR, CONTEXT_SELECTOR_SHA)) == CONTEXT_SELECTOR_SHA and
         sha(public_leaf(CONTEXT_SELECTOR_FREEZE, CONTEXT_SELECTOR_FREEZE_SHA)) == CONTEXT_SELECTOR_FREEZE_SHA,
         'FROZEN_CONTEXT_SELECTOR_REQUIRED')
    spec = importlib.util.spec_from_file_location('cal_context_successor_selector', CONTEXT_SELECTOR)
    selector = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(selector)
    selected = selector.select(**mapper_inputs)
    pins = selected['pins']
    need(selected['status'] == 'CONTEXT_DYNAMIC_SELECTION_ONLY' and
         selected['effect_enabled'] is False and
         pins['source'] == SOURCE_MANIFEST_SHA and
         pins['source_package'] == SOURCE_PACKAGE_SHA and
         selected['attempt'] == str(CONTEXT_ATTEMPT) and
         selected['mapper_effect_review_sha256'] ==
         mapper_inputs['outside_mapper_review_sha'],
         'CURRENT_MAPPER_CONTEXT_SELECTION_JOIN')
    roles = dict(selected['projected_context'])
    roles['build.py'] = rebind_guarded_build(roles['build.py'])
    return {'status':'MAPPER_SELECTED_JIT_AUTHORITY_HOLD',
            'source':source,'topology':topology(),
            'mapper_effect_review_sha256':selected['mapper_effect_review_sha256'],
            'pins':pins,'projected_context':roles,
            'signed_scope_attestation':'NOT_OPENED',
            'authorization_issuer':'UNSELECTED',
            'authority_effect':'NONE','docker_effect':'REFUSED'}


def construct_policy_candidate(*, selected, authorization_raw, authorization_sha256,
                               reader_public_key, now):
    """Pure byte-bound policy candidate; supplied AUTH is not an issued grant."""
    need(type(selected) is dict and
         selected.get('status') == 'MAPPER_SELECTED_JIT_AUTHORITY_HOLD' and
         selected.get('signed_scope_attestation') == 'NOT_OPENED' and
         type(now) is dt.datetime and now.utcoffset() == dt.timedelta(),
         'INERT_MAPPER_SELECTION_REQUIRED')
    # Reopen the exact reviewed public Source bytes at policy-construction time.
    # A caller-supplied selection cannot extend the fixed Source interval.
    current_source = source_preflight(now)
    need(selected.get('source') == current_source and
         selected.get('topology') == topology(),
         'CURRENT_SELECTED_SOURCE_PERIOD_REQUIRED')
    need(type(authorization_raw) is bytes and len(authorization_raw) <= 16*1024 and
         type(authorization_sha256) is str and
         sha(authorization_raw) == authorization_sha256,
         'EXACT_AUTHORIZATION_BYTES_REQUIRED')
    auth = parse(authorization_raw, 16*1024)
    source = current_source
    paths = selected['topology']
    start, end = utc(auth['not_before']), utc(auth['expires_at'])
    need(set(auth) == {'schema_version','family_ref','episode_ref','scope_ref',
                       'period_binding','not_before','expires_at','authority_effect',
                       'actual_owner_outcome','claim_ceiling'} and
         auth.get('claim_ceiling') ==
         'Local disposable development episode only; no protected Source8 issuer grant or owner outcome.' and
         auth.get('schema_version') == 'lab-context-development-authorization/v1-candidate' and
         auth.get('family_ref') == paths['context_family_ref'] and
         auth.get('episode_ref') == PERIOD_REF and
         auth.get('scope_ref') == EXPECTED_SCOPE and
         auth.get('period_binding') ==
         {'path':SOURCE_ROLE+'/packages/0001/period.json','sha256':SOURCE_PERIOD_SHA} and
         auth.get('authority_effect') == 'none' and
         auth.get('actual_owner_outcome') is None and
         utc(source['period_start']) <= start <= now < end <= utc(source['period_end']) and
         end-start <= dt.timedelta(minutes=20),
         'AUTHORIZATION_SCOPE_PERIOD_POSTURE')
    need(type(reader_public_key) is str, 'PUBLIC_KEY_REQUIRED')
    try:
        key = base64.b64decode(reader_public_key, validate=True)
        Ed25519PublicKey.from_public_bytes(key)
    except (ValueError, TypeError) as exc:
        raise Refused('CANONICAL_ED25519_PUBLIC_KEY_REQUIRED') from exc
    need(len(key) == 32 and base64.b64encode(key).decode() == reader_public_key,
         'CANONICAL_ED25519_PUBLIC_KEY_REQUIRED')
    policy_end = min(now + dt.timedelta(minutes=20), end,
                     utc(source['period_end']))
    need(policy_end > now, 'CURRENT_POLICY_INTERVAL_REQUIRED')
    value = {'schema_version':'lab-context-host-policy/v1-candidate',
             'host_uid':os.getuid(),'principal_ref':PRINCIPAL_REF,
             'scope_ref':EXPECTED_SCOPE,'reader_public_key':reader_public_key,
             'not_before':now.isoformat(),'expires_at':policy_end.isoformat(),
             'max_input_bytes':1048576,'max_output_bytes':2097152,
             'max_session_seconds':900,
             'period_binding':{'path':SOURCE_ROLE+'/packages/0001/period.json',
                               'sha256':SOURCE_PERIOD_SHA},
             'allowed_operations':['context.get','session.open'],
             'authority_effect':'none','actual_owner_outcome':None}
    return {'status':'SYNTHETIC_POLICY_BYTES_ONLY',
            'authorization_sha256':authorization_sha256,
            'policy_sha256':sha(canonical(value)),
            'policy_raw':canonical(value),'effect':'NOT_RUN'}


def issue_authorization(*_args, **_kwargs):
    raise Refused('EFFECT_DISABLED_NO_REVIEWED_MAPPER_SCOPE_OR_ISSUER')


def generate_key(*_args, **_kwargs):
    raise Refused('EFFECT_DISABLED_NO_PRIVATE_KEY')


def create_private_root_or_policy(*_args, **_kwargs):
    raise Refused('EFFECT_DISABLED_NO_PRIVATE_ROOT_OR_POLICY_WRITE')


def launch_context(*_args, **_kwargs):
    raise Refused('EFFECT_DISABLED_NO_CONTEXT_DOCKER_RELEASE')
