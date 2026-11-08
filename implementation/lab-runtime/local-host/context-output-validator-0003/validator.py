"""Effect-disabled Context output contract with held-to-body and raw-byte joins."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta
import base64
import binascii
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

REPO = Path(__file__).resolve().parents[4]
LOCAL = Path(__file__).resolve().parents[1]
BRIDGE = LOCAL / 'context-bridge-0002/bridge.py'
BRIDGE_SHA = '5bf35088d43f781453ee8f4e9397a033bd2acdd671142a5a7c05adad709bb52a'
INTEGRATION = LOCAL / 'context-runtime-integration-0003/integration.py'
INTEGRATION_SHA = '45e0524107a3680f07c8ee19c6ff6025398331edd14e106c29fa1a85d3473f89'
CLAIM = 'Actual historical construction delivery at its recorded expiry; later use must revalidate current source, host permission and expiry.'
LEAVES = ('request.json', 'authentication-proof.json', 'trusted-context.json',
          'host-permission-public.json', *(f'artifacts/{i:02d}.json' for i in range(30)),
          'artifact-index.json', 'delivery.json', 'lesson-selection.json',
          'delivery-provenance.json', 'build-result.json', 'manifest.json')
VERSIONS = {'ontology-node': 'v2', 'ontology-edge': 'v1', 'ontology': 'v1',
            'ontology-cut': 'v1', 'ontology-view': 'v1', 'context-request': 'v1',
            'context-view': 'v1'}
SCHEMA_SHA = {
    'ontology-node': '447c413cc61a7a627d8f657437a1784f77b579b3d9f84f5823e0dd5c9c48317f',
    'ontology-edge': '968999eac9b9f37cbb97edf7d0e146edbc78a8bb3e171c0afd997d296dc18c5f',
    'ontology': '89f831b26155857e7e9f9d1a467f2c5f950e05526d72d65832338db7a58ef6d1',
    'ontology-cut': 'ae5f8e23cb0d5b34b1e55d6816a03ee4618b884c51262d86c46af4260c025471',
    'ontology-view': '32c12b7e917e8872b82174d963d4a17e2b2e5ff64d7c798774a72cfcdb497d4b',
    'context-request': 'c4db5d934a8b5d39bd14d231e5f8353d3f1a288ba7f314f987d62ef58d767615',
    'context-view': '08b7e0667bc43b45bc125c06c18bc21b91fc72d0f9c2d7c1dade2b7e6b7668c2',
}
DELIVERY_SCHEMA = REPO / 'docs/proposals/0007-lab-integrated-schema-package/schemas/context-delivery.schema.json'
DELIVERY_SCHEMA_SHA = '03a28d61e1c55e24b882834c47386561570b225d46f82f9169cfdf29283d698e'
QUERY_SCHEMA = REPO / 'docs/proposals/0007-lab-integrated-schema-package/schemas/context-query.schema.json'
QUERY_SCHEMA_SHA = 'ebc44fa120e65f12f2aa0e67c9442d278394e2186d7342923e20f4388e44b556'
COMMON_SCHEMA = REPO / 'docs/proposals/0007-lab-integrated-schema-package/schemas/common.schema.json'
COMMON_SCHEMA_SHA = 'd41f2b8811d0cbea6845f13f1c586665afe03d49ddf7c0974d0632bb3ceded74'
STORAGE_SCHEMA = REPO / 'docs/proposals/0006-lab-artifact-storage/schemas/artifact-package-manifest.schema.json'
STORAGE_SCHEMA_SHA = '52f4efabb39e3a9ac26da208ffe0950f85a8f51d3d591097eb5c19a544e46e60'
MAX_LEAF = 65536
MAX_TOTAL = 2 * 1024 * 1024


class Refused(ValueError):
    pass


def need(value, code):
    if not value:
        raise Refused(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def wire(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode()


def original_leaf_bytes(leaf, value):
    compact = wire(value)
    return compact if leaf in ('request.json', 'authentication-proof.json') else compact + b'\n'


def pairs(rows):
    out = {}
    for key, value in rows:
        need(key not in out, 'DUPLICATE_JSON_KEY')
        out[key] = value
    return out


def parse(raw, code):
    try:
        value = json.loads(raw, object_pairs_hook=pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(Refused(code)))
    except (UnicodeError, ValueError, TypeError, RecursionError):
        raise Refused(code) from None
    return value


def instant(value):
    need(type(value) is str and (value.endswith('Z') or value.endswith('+00:00')), 'TIME_FORMAT')
    try:
        moment = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        raise Refused('TIME_FORMAT') from None
    need(moment.utcoffset() == timedelta(0), 'TIME_FORMAT')
    return moment


def integration():
    need(sha(INTEGRATION.read_bytes()) == INTEGRATION_SHA and
         sha(BRIDGE.read_bytes()) == BRIDGE_SHA, 'SELECTED_IMPLEMENTATION_DRIFT')
    spec = importlib.util.spec_from_file_location('context_integration_0003_selected', INTEGRATION)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    need(tuple(module.expected_leaves()) + ('build-result.json', 'manifest.json') == LEAVES,
         'LEAF_SCHEDULE_DRIFT')
    return module


def schema(kind):
    if kind == 'delivery':
        path, expected = DELIVERY_SCHEMA, DELIVERY_SCHEMA_SHA
    elif kind == 'query':
        path, expected = QUERY_SCHEMA, QUERY_SCHEMA_SHA
    else:
        need(kind in VERSIONS, 'CARRIER_KIND')
        path = REPO / 'authority/artifact-types' / kind / VERSIONS[kind] / 'schema.json'
        expected = SCHEMA_SHA[kind]
    raw = path.read_bytes()
    need(sha(raw) == expected, 'SCHEMA_DRIFT')
    value = parse(raw, 'SCHEMA_JSON')
    Draft202012Validator.check_schema(value)
    common_raw = COMMON_SCHEMA.read_bytes()
    need(sha(common_raw) == COMMON_SCHEMA_SHA, 'SCHEMA_DRIFT')
    common = parse(common_raw, 'SCHEMA_JSON')
    storage_raw = STORAGE_SCHEMA.read_bytes()
    need(sha(storage_raw) == STORAGE_SCHEMA_SHA, 'SCHEMA_DRIFT')
    storage = parse(storage_raw, 'SCHEMA_JSON')
    registry = Registry().with_resource(common['$id'], Resource.from_contents(common))
    registry = registry.with_resource(storage['$id'], Resource.from_contents(storage))
    return Draft202012Validator(value, format_checker=FormatChecker(), registry=registry)


def _chain(path):
    need(isinstance(path, Path) and path.is_absolute() and
         str(path) == os.path.normpath(str(path)), 'PACKAGE_PATH')
    fds = [os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)]
    try:
        for part in path.parts[1:]:
            fds.append(os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW |
                               os.O_CLOEXEC, dir_fd=fds[-1]))
        return fds
    except BaseException:
        for fd in reversed(fds):
            os.close(fd)
        raise


def _names(fd, wanted, code):
    with os.scandir(fd) as entries:
        actual = {entry.name for entry in entries}
    need(actual == set(wanted), code)


def _file(fd, name, uid, gid):
    child = os.open(name, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC,
                    dir_fd=fd)
    try:
        before = os.fstat(child)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
             stat.S_IMODE(before.st_mode) == 0o444 and
             before.st_uid == uid and before.st_gid == gid and
             before.st_size <= MAX_LEAF, 'LEAF_CUSTODY')
        raw = bytearray()
        while len(raw) <= before.st_size:
            part = os.read(child, before.st_size + 1 - len(raw))
            if not part:
                break
            raw.extend(part)
        after = os.fstat(child)
        need((before.st_dev, before.st_ino, before.st_mode, before.st_nlink,
              before.st_uid, before.st_gid, before.st_size, before.st_mtime_ns,
              before.st_ctime_ns) ==
             (after.st_dev, after.st_ino, after.st_mode, after.st_nlink,
              after.st_uid, after.st_gid, after.st_size, after.st_mtime_ns,
              after.st_ctime_ns) and len(raw) == before.st_size, 'READBACK')
        return bytes(raw)
    finally:
        os.close(child)


def package_bytes(root):
    fds = _chain(root)
    try:
        fd = fds[-1]
        info = os.fstat(fd)
        need(stat.S_IMODE(info.st_mode) == 0o500, 'PACKAGE_MODE')
        _names(fd, [leaf for leaf in LEAVES if '/' not in leaf] + ['artifacts'],
               'PACKAGE_INVENTORY')
        art = os.open('artifacts', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW |
                      os.O_CLOEXEC, dir_fd=fd)
        fds.append(art)
        ai = os.fstat(art)
        need(stat.S_IMODE(ai.st_mode) == 0o500 and
             (ai.st_uid, ai.st_gid) == (info.st_uid, info.st_gid), 'ARTIFACT_DIR_CUSTODY')
        _names(art, [f'{i:02d}.json' for i in range(30)], 'ARTIFACT_INVENTORY')
        raw = {leaf: _file(art if '/' in leaf else fd, leaf.split('/')[-1],
                           info.st_uid, info.st_gid) for leaf in LEAVES}
        need(sum(map(len, raw.values())) <= MAX_TOTAL, 'PACKAGE_BUDGET')
        return raw, info.st_uid, info.st_gid
    finally:
        for fd in reversed(fds):
            os.close(fd)


def binding(root, leaf, raw):
    return {'path': str(root / leaf), 'sha256': sha(raw)}


def check_policy(policy, held, uid, now):
    keys = {'schema_version', 'host_uid', 'principal_ref', 'scope_ref',
            'reader_public_key', 'not_before', 'expires_at', 'max_input_bytes',
            'max_output_bytes', 'max_session_seconds', 'period_binding',
            'allowed_operations', 'authority_effect', 'actual_owner_outcome'}
    need(type(policy) is dict and set(policy) == keys and
         policy['schema_version'] == 'lab-context-host-policy/v1-candidate' and
         type(policy['host_uid']) is int and policy['host_uid'] == uid and
         policy['principal_ref'] == held.get('principal_ref') and
         policy['scope_ref'] == held.get('scope_ref') and
         policy['period_binding'] == held.get('period_binding') and
         policy['allowed_operations'] == ['context.get', 'session.open'] and
         policy['authority_effect'] == 'none' and policy['actual_owner_outcome'] is None and
         policy['not_before'] == held.get('policy_start') and
         policy['expires_at'] == held.get('policy_end') and
         all(type(policy[key]) is int and 1 <= policy[key] <= bound for key, bound in
             (('max_input_bytes', 1048576), ('max_output_bytes', 2097152),
              ('max_session_seconds', 900))) and
         instant(policy['not_before']) <= now < instant(policy['expires_at']) and
         instant(policy['expires_at']) - instant(policy['not_before']) <=
         timedelta(seconds=1200), 'POLICY_ENVELOPE')
    try:
        key = base64.b64decode(policy['reader_public_key'], validate=True)
    except (TypeError, ValueError, binascii.Error):
        raise Refused('POLICY_PUBLIC_KEY') from None
    need(len(key) == 32 and base64.b64encode(key).decode() == policy['reader_public_key'],
         'POLICY_PUBLIC_KEY')


def check_query(query, held, policy, now):
    need(type(query) is dict and not list(schema('query').iter_errors(query)) and
         query.get('source_cut') == held.get('source_cut') and
         query.get('assignment') == held.get('assignment') and
         query.get('work') == held.get('work') and
         query.get('coordination_context') == held.get('coordination_context') and
         query.get('actor', {}).get('principal_ref') == held.get('principal_ref') and
         query.get('freshness_requirement') == 'current' and
         query.get('selectors') == [] and
         query.get('exclusions') == ['historical-session-memory', 'private-source-archives',
                                     'external-effects', 'unrelated-work'] and
         query.get('authority_effect') == 'none', 'QUERY_ENVELOPE')
    budget = query['budget']
    need(budget['max_actions'] == 0 and
         0 < budget['max_input_bytes'] <= policy['max_input_bytes'] and
         0 < budget['max_output_bytes'] <= policy['max_output_bytes'] and
         now < instant(budget['deadline']) <= instant(policy['expires_at']),
         'QUERY_BUDGET')


def expected_native_correspondence(held):
    """Derive pairs only from separately selected native rows, never output rows."""
    rows = held.get('native_rows')
    need(type(rows) is list and len(rows) == 25, 'HELD_NATIVE_ROWS')
    expected = []
    subjects = set()
    carriers = set()
    for row in rows:
        need(type(row) is dict and set(row) ==
             {'native_identity', 'semantic_event_ref', 'governance_event_ref'} and
             type(row['native_identity']) is dict and
             type(row['native_identity'].get('subject_id')) is str and
             type(row['native_identity'].get('subject_kind')) is str and
             type(row['governance_event_ref']) is str and
             type(row['semantic_event_ref']) is dict, 'HELD_NATIVE_ROW_SHAPE')
        native = row['native_identity']
        kind = native['subject_kind']
        subject = native['subject_id']
        need(kind in ('node', 'edge') and ':' in subject and
             subject.split(':', 1)[1] and subject not in subjects,
             'HELD_NATIVE_ROW_IDENTITY')
        subjects.add(subject)
        carrier = (('ontology-node' if kind == 'node' else 'ontology-edge') + ':' +
                   subject.split(':', 1)[1])
        need(carrier not in carriers, 'HELD_NATIVE_ROW_IDENTITY')
        carriers.add(carrier)
        expected.append({'native_identity': native, 'carrier_identity': carrier,
                         'semantic_event_ref': row['semantic_event_ref'],
                         'governance_event_ref': row['governance_event_ref']})
    need(Counter(r['native_identity']['subject_kind'] for r in rows) ==
         Counter({'node': 15, 'edge': 10}) and
         [r['native_identity'] for r in rows] == held.get('native_subject_identities'),
         'HELD_NATIVE_ROW_COUNT')
    return expected


def check_synthetic(root, held, receipt):
    """Validate public synthetic package and fake held oracles; no real-effect verdict."""
    need(type(held) is dict and held.get('held_origin') == 'synthetic-held-public-metadata',
         'HELD_ORIGIN')
    need(type(receipt) is dict and receipt.get('held_origin') == 'synthetic-held-os-transport',
         'RECEIPT_ORIGIN')
    bridge = integration()
    root = Path(root)
    raw, uid, gid = package_bytes(root)
    need(uid == held.get('uid') == receipt.get('uid') and
         gid == held.get('gid') == receipt.get('gid'), 'OUTPUT_UID_GID')
    document = {leaf: parse(value, 'OUTPUT_JSON') for leaf, value in raw.items()}
    need(all(type(document[leaf]) is dict for leaf in LEAVES
             if leaf not in ('artifact-index.json',)), 'OUTPUT_OBJECT_SHAPE')
    need(type(held.get('context_source_binding')) is dict, 'HELD_SOURCE_BINDING')
    manifest = document['manifest.json']
    rows = [binding(root, leaf, raw[leaf]) for leaf in LEAVES[:-1]]
    expected = {'schema_version': 'lab-actual-context-delivery-package/v1-candidate',
                'files': sorted(rows, key=lambda row: row['path']),
                'source_manifest_binding': held.get('context_source_binding'),
                'authority_effect': 'none', 'actual_owner_outcome': None,
                'delivery_binding': rows[LEAVES.index('delivery.json')],
                'provenance_binding': rows[LEAVES.index('delivery-provenance.json')],
                'claim_ceiling': CLAIM}
    need(manifest == expected and len(manifest['files']) == 39, 'ORIGINAL_MANIFEST_JOIN')
    need(receipt.get('manifest_sha256') == sha(raw['manifest.json']) and
         receipt.get('source_binding') == held.get('context_source_binding') and
         receipt.get('output_bytes') == sum(map(len, raw.values())) and
         receipt.get('inventory_sha256') ==
         sha(wire([binding(root, leaf, raw[leaf]) for leaf in LEAVES])),
         'RECEIPT_PACKAGE_JOIN')
    result, delivery = document['build-result.json'], document['delivery.json']
    provenance, lesson = document['delivery-provenance.json'], document['lesson-selection.json']
    required_result = {'result': 'PASS', 'actual_generated_artifact_carriers': 30,
                       'ontology_nodes': 15, 'ontology_edges': 10,
                       'context_request_view_and_ontology_cut_view_records': 5,
                       'actual_original_schema_validation': True,
                       'real_nonce_transport_authentication': True,
                       'current_independent_host_permission': True,
                       'current_absolute_Assignment_period': True,
                       'actual_Context_Delivery_posture': 'ready',
                       'native_domain_mapping_supplied': True,
                       'source_and_native_cuts_distinct': True,
                       'owned_host_policy_and_transport_key_removed': True,
                       'active_Agents_created': 0, 'public_API_operations_added': 0,
                       'source_sha256': held.get('context_source_binding', {}).get('sha256'),
                       'mapped_package_sha256': held.get('mapper_package_sha256'),
                       'authority_effect': 'none', 'actual_owner_outcome': None,
                       'task_complete': False}
    need(set(result) == set(required_result) | {'duration_seconds', 'owned_host_root'} and
         all(result.get(k) == v for k, v in required_result.items()) and
         type(result.get('duration_seconds')) in (int, float) and
         0 <= result['duration_seconds'] <= 900 and
         type(result.get('owned_host_root')) is str,
         'RESULT_JOIN')
    now = instant(held.get('observed_at'))
    policy = document['host-permission-public.json']
    check_policy(policy, held, uid, now)
    query = document['request.json']
    check_query(query, held, policy, now)
    for start, end in (('source_start', 'source_end'), ('auth_start', 'auth_end'),
                       ('policy_start', 'policy_end')):
        need(instant(held.get(start)) <= now < instant(held.get(end)), 'CURRENT_AUTHORITY')
    need(instant(held['source_start']) <= instant(held['auth_start']) <=
         instant(held['policy_start']) and instant(held['policy_end']) <=
         instant(held['auth_end']) <= instant(held['source_end']) and
         held.get('signed_source_guard') is True and
         held.get('auth_validated') is True and held.get('policy_validated') is True and
         document['host-permission-public.json'] == held.get('public_policy') and
         held.get('scope_ref') == document['host-permission-public.json'].get('scope_ref') and
         held.get('source_cut') != held.get('native_cut_digest'), 'AUTHORITY_POSTURE')
    lesson_keys = {'schema_version', 'source_cut', 'assignment', 'current_catalog_lessons',
                   'selected_lesson_refs', 'selection_rule', 'authority_effect'}
    need(set(lesson) == lesson_keys and
         lesson['schema_version'] == 'lab-context-lesson-selection/v1-candidate' and
         lesson['source_cut'] == held['source_cut'] and
         lesson['assignment'] == held.get('assignment') and
         type(lesson['current_catalog_lessons']) is int and
         lesson['current_catalog_lessons'] == 0 and
         lesson['selected_lesson_refs'] == [] and
         lesson['selection_rule'] ==
         'Actual current source catalog checked; new lessons require explicit applicability closure.' and
         lesson['authority_effect'] == 'none', 'LESSON_ENVELOPE')
    provenance_keys = {'schema_version', 'posture', 'scope_enforced', 'freshness',
                       'source_cut', 'assignment', 'work', 'coordination_context',
                       'authenticated_principal_ref', 'authority_envelope_binding',
                       'expires_at', 'native_cut_digest', 'mapped_package_sha256',
                       'correspondence', 'source_material_provenance',
                       'generated_artifact_refs', 'authority_effect',
                       'actual_owner_outcome', 'verified_original_binding'}
    need(set(provenance) == provenance_keys and
         provenance['schema_version'] == 'lab-verified-context-delivery-provenance/v1-candidate' and
         provenance['assignment'] == held.get('assignment') and
         provenance['work'] == held.get('work') and
         provenance['coordination_context'] == held.get('coordination_context') and
         provenance['authenticated_principal_ref'] == held.get('principal_ref') and
         provenance['authority_envelope_binding'] == held.get('authority_envelope_binding') and
         type(provenance['authority_envelope_binding']) is dict and
         set(provenance['authority_envelope_binding']) == {'ref', 'sha256'} and
         provenance['authority_envelope_binding']['ref'] ==
         held.get('authority_envelope_ref') and
         provenance['authority_envelope_binding']['sha256'] ==
         sha(raw['host-permission-public.json']),
         'PROVENANCE_ENVELOPE')
    need(not list(schema('delivery').iter_errors(delivery)) and
         delivery.get('source_cut') == provenance.get('source_cut') ==
         lesson.get('source_cut') == held.get('source_cut') and
         delivery.get('posture') == provenance.get('posture') == 'ready' and
         delivery.get('freshness') == provenance.get('freshness') == 'current' and
         delivery.get('scope_enforced') is provenance.get('scope_enforced') is True and
         delivery.get('authority_effect') == provenance.get('authority_effect') == 'none' and
         provenance.get('actual_owner_outcome') is None and
         provenance.get('native_cut_digest') == held.get('native_cut_digest') and
         provenance.get('mapped_package_sha256') == held.get('mapper_package_sha256') and
         provenance.get('verified_original_binding') ==
         binding(root, 'delivery.json', raw['delivery.json']) and
         delivery.get('expires_at') == provenance.get('expires_at') and
         now < instant(delivery.get('expires_at')) <= instant(held['policy_end']),
         'DELIVERY_CUT_EXPIRY')
    index = document['artifact-index.json']
    need(type(index) is list and len(index) == 30, 'ARTIFACT_INDEX')
    kinds = Counter()
    refs = []
    identities = set()
    for number in range(30):
        leaf = f'artifacts/{number:02d}.json'
        body = document[leaf]
        need(type(body) is dict, 'CARRIER_BODY')
        kind = body.get('kind')
        need(kind in VERSIONS and not list(schema(kind).iter_errors(body)) and
             body.get('scope_ref') == held.get('scope_ref') and
             body.get('authority_effect') == 'none' and
             type(body.get('node_id')) is str and body['node_id'] not in identities,
             'CARRIER_SCHEMA_SCOPE')
        identities.add(body['node_id'])
        kinds[kind] += 1
        entry = index[number]
        need(type(entry) is dict and set(entry) == {'artifact', 'original_binding'} and
             entry['original_binding'] == binding(root, leaf, raw[leaf]) and
             type(entry['artifact']) is dict and
             entry['artifact'].get('byte_sha256') == sha(raw[leaf]) and
             entry['artifact'].get('identity_ref') == body['node_id'] and
             entry['artifact'].get('scope_ref') == held['scope_ref'], 'ARTIFACT_INDEX_JOIN')
        refs.append(entry['artifact'])
    need(kinds == Counter({'ontology-node': 15, 'ontology-edge': 10, 'ontology': 1,
                           'ontology-cut': 1, 'ontology-view': 1,
                           'context-request': 1, 'context-view': 1}) and
         provenance.get('generated_artifact_refs') == refs and
         delivery.get('context_view') == next(r for r in refs if r['identity_ref'] ==
                                               next(document[f'artifacts/{i:02d}.json']['node_id']
                                                    for i in range(30) if document[f'artifacts/{i:02d}.json']['kind'] == 'context-view')) and
         delivery.get('ontology_view') == next(r for r in refs if r['identity_ref'] ==
                                                next(document[f'artifacts/{i:02d}.json']['node_id']
                                                     for i in range(30) if document[f'artifacts/{i:02d}.json']['kind'] == 'ontology-view')),
         'CARRIER_COUNTS_REFS')
    need(document['request.json'].get('source_cut') == held['source_cut'] and
         delivery.get('request_binding') ==
         {'ref': 'request:' + document['request.json']['request_ref'],
          'sha256': sha(raw['request.json'])} and
         delivery.get('lesson_selection_binding', {}).get('sha256') ==
         sha(raw['lesson-selection.json']) and
         document['host-permission-public.json'].get('authority_effect') == 'none',
         'REQUEST_POLICY_LESSON_JOIN')
    selected = held.get('selected_source_refs')
    source_provenance = provenance.get('source_material_provenance')
    need(type(selected) is list and len(selected) == 25 and
         len({wire(x) for x in selected}) == 25 and
         delivery.get('included_refs') == selected and
         type(source_provenance) is list and len(source_provenance) == 25 and
         source_provenance == held.get('source_material_provenance') and
         all(type(p) is dict and set(p) ==
             {'artifact', 'original_material', 'selected_original_body_sha256',
              'selected_body_encoding', 'visibility'} and
             type(p['original_material']) is dict and
             set(p['original_material']) == {'source_ref', 'selector', 'sha256'} and
             p['visibility'] ==
             'selected-body-only; enclosing archives remain private'
             for p in source_provenance) and
         [p.get('artifact') for p in source_provenance if type(p) is dict] == selected and
         all(p.get('selected_original_body_sha256') == p['artifact']['byte_sha256']
             for p in source_provenance if type(p) is dict), 'SOURCE_REF_JOIN')
    carrier_expiry = [document[f'artifacts/{i:02d}.json'] for i in range(30)
                      if document[f'artifacts/{i:02d}.json']['kind'] in ('context-view', 'ontology-view')]
    need(all((b.get('expires_at', b.get('payload', {}).get('expires_at')) ==
              delivery['expires_at'] for b in carrier_expiry)), 'CARRIER_EXPIRY')
    cut = next(document[f'artifacts/{i:02d}.json'] for i in range(30)
               if document[f'artifacts/{i:02d}.json']['kind'] == 'ontology-cut')
    view = next(document[f'artifacts/{i:02d}.json'] for i in range(30)
                if document[f'artifacts/{i:02d}.json']['kind'] == 'ontology-view')
    context_view = next(document[f'artifacts/{i:02d}.json'] for i in range(30)
                        if document[f'artifacts/{i:02d}.json']['kind'] == 'context-view')
    need(cut['payload'].get('calculated_digest') ==
         view['payload'].get('cut_digest') == held.get('native_cut_digest') and
         cut['payload'].get('source_event_set_digest') ==
         view['payload'].get('source_event_set_digest') ==
         held.get('native_source_event_set_digest') and
         context_view.get('source_epoch') ==
         'protocol:source-cut:' + sha(original_leaf_bytes('context-view.json', held['source_cut'])),
         'NATIVE_VIEW_CUT_JOIN')
    correspondence = provenance.get('correspondence')
    expected_pairs = expected_native_correspondence(held)
    need(correspondence == expected_pairs and
         {r['carrier_identity'] for r in expected_pairs} ==
         {document[f'artifacts/{i:02d}.json']['node_id'] for i in range(30)
          if document[f'artifacts/{i:02d}.json']['kind'] in ('ontology-node', 'ontology-edge')},
         'NATIVE_CORRESPONDENCE')
    by_carrier = {document[f'artifacts/{i:02d}.json']['node_id']:
                  document[f'artifacts/{i:02d}.json'] for i in range(30)}
    for row in expected_pairs:
        body = by_carrier[row['carrier_identity']]
        payload = body.get('payload')
        need(type(payload) is dict, 'NATIVE_CARRIER_CONTENT_JOIN')
        if body['kind'] == 'ontology-node':
            governance = payload.get('governance_binding')
            need(type(governance) is dict and
                 governance.get('semantic_event_ref') == row['semantic_event_ref'] and
                 governance.get('governance_event_refs') == [row['governance_event_ref']],
                 'NATIVE_CARRIER_CONTENT_JOIN')
        else:
            need(body['kind'] == 'ontology-edge' and
                 payload.get('semantic_event_ref') == row['semantic_event_ref'],
                 'NATIVE_CARRIER_CONTENT_JOIN')
    need(receipt.get('trace') == list(bridge.expected_trace()) and
         receipt.get('writer_closed') is receipt.get('client_closed') is
         receipt.get('parent_closed') is receipt.get('child_exited_zero') is True and
         receipt.get('child_stderr') == '' and receipt.get('private_root_absent') is True and
         receipt.get('transport_private_path') == str(root.parent / 'private') and
         receipt.get('host_private_path') == result['owned_host_root'] and
         not os.path.lexists(receipt['transport_private_path']) and
         not os.path.lexists(receipt['host_private_path']), 'EXTERNAL_TERMINAL_RECEIPT')
    need(all(raw[leaf] == original_leaf_bytes(leaf, document[leaf]) for leaf in LEAVES),
         'ORIGINAL_EMIT_ENCODING')
    return {'status': 'SYNTHETIC_OUTPUT_CONTRACT_PASS_ONLY',
            'manifest_sha256': sha(raw['manifest.json']), 'leaves': 40,
            'manifest_rows': 39, 'carriers': dict(kinds), 'effect_enabled': False,
            'actual_context': 'NOT_RUN'}


def launch(*_args, **_kwargs):
    raise Refused('effect disabled: real held authority, output and terminal receipts unselected')
