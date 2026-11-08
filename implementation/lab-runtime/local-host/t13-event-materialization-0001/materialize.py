"""Inert native sealing over exact original O06 predecessor evidence.

Original archive bodies remain in memory or an owned temporary directory and
are never emitted in the public receipt. This does not adopt any representation.
"""

import argparse
import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[4]
ACCOUNT = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T13/native-event-closure-preparation-0001/ACCOUNTING-88.json'
ACCOUNT_SHA = 'c783761f5180365cbec59ef8ab654cb3d9bb3376e408eee37f06216ccaf46f1d'
ARCHIVE = ROOT / 'implementation/lab-ontology/candidates/v1/migration/candidate/0001/native.snapshot'
ARCHIVE_SHA = '763ca7730e05fe4bb1545b4a1fb4f613274a4f07a6e97a18cf6bac86ed2152c7'
NATIVE = ROOT / 'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/ontology-0002-tu00qs02/bin/lab-ontology-native'
NATIVE_SHA = '82713671f1c1271f92b7ae675ccee531c0ee972828e25899c0c19e64015025f6'
INSTALL = NATIVE.parent.parent / 'installation.json'
INSTALL_SHA = 'abbdccba598f7663082d094347712bb8d324aa2042154f4102ab676ad0260527'


class Refusal(ValueError):
    pass


def need(ok, message):
    if not ok:
        raise Refusal(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def parse(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: need(False, 'nonfinite JSON'))


def exact(path, digest):
    need(path.is_absolute() and path.is_relative_to(ROOT)
         and path.resolve().is_relative_to(ROOT.resolve()),
         'selected file escapes checkout through parent')
    current = ROOT
    for part in path.relative_to(ROOT).parts:
        current = current / part
        need(not current.is_symlink(), 'selected file uses symlinked ancestor')
    need(path.is_file() and not path.is_symlink(), 'selected file absent or redirected')
    raw = path.read_bytes()
    need(sha(raw) == digest, 'selected file bytes changed')
    return raw


def selected_binding(binding):
    need(type(binding) is dict and set(binding) == {'path', 'sha256'}
         and type(binding['path']) is str and type(binding['sha256']) is str,
         'closed original intent binding required')
    relative = Path(binding['path'])
    need(not relative.is_absolute() and relative.as_posix() == binding['path']
         and '..' not in relative.parts and '\\' not in binding['path'],
         'original intent locator escapes selected checkout')
    return exact(ROOT / relative, binding['sha256'])


def archive_events(snapshot):
    need(snapshot['schema_version'] == 'lab-O05-private-native-archive/v1-candidate'
         and snapshot['authority_effect'] == 'none'
         and snapshot['actual_owner_outcome'] is None
         and snapshot['ontology_admission'] is False
         and snapshot['source_effects_applied'] == 0
         and snapshot['private_key_included'] is False
         and snapshot['Session_memory_included'] is False
         and len(snapshot['files']) == 176, 'original inert archive boundary changed')
    events = {'semantic': {}, 'governance': {}}
    for path, envelope in snapshot['files'].items():
        kind = path.split('/', 1)[0]
        need(kind in events and set(envelope) == {'base64_original_bytes', 'sha256'},
             'closed original native archive entry required')
        raw = base64.b64decode(envelope['base64_original_bytes'], validate=True)
        need(sha(raw) == envelope['sha256'], 'original native archive body changed')
        event = parse(raw)
        need(raw.endswith(b'\n') and type(event.get('event_digest')) is str
             and re.fullmatch('[a-f0-9]{64}', event['event_digest']),
             'original native canonical event frame changed')
        digest_token = ('"event_digest":"' + event['event_digest'] + '"').encode()
        need(raw.count(digest_token) == 1 and
             sha(raw.replace(digest_token, b'"event_digest":"' + b'0' * 64 + b'"', 1)) == event['event_digest'],
             'original native event digest preimage changed')
        cursor_key = 'semantic_cursor' if kind == 'semantic' else 'governance_cursor'
        cursor = event[cursor_key]
        need(type(cursor) is int and 1 <= cursor <= 88 and cursor not in events[kind]
             and event['event_family'] == kind and event['source_kind'] == 'canonical_event',
             'native event cursor or kind differs')
        events[kind][cursor] = event
    need(all(set(rows) == set(range(1, 89)) for rows in events.values()),
         'complete original 1..88 event histories required')
    return events


def prepare(account, snapshot):
    need(account['schema_version'] == 'lab-T13-all88-native-event-accounting/v1-candidate'
         and account['task_complete'] is False and account['actual_materialized_events'] == 0
         and len(account['rows']) == 88, 'original blocked accounting changed')
    events = archive_events(snapshot)
    drafts = []
    rows = []
    seen_members = set()
    seen_streams = set()
    for position, row in enumerate(account['rows'], 1):
        member = row['member_ref']
        need(member not in seen_members and row['status'] == 'explicitly-blocked-before-native-materialization'
             and row['actual_owner_Decision_binding'] is None and row['actual_owner_response'] is None
             and row['native_event_bytes'] is None and row['native_event_digest'] is None,
             'original O06 intent/authority posture changed')
        seen_members.add(member)
        semantic_tuple = row['semantic_tuple']
        predecessor = row['predecessor_governance_tuple']
        intent = parse(selected_binding(row['intent_binding']))
        need(intent['schema_version'] == 'lab-O06-representation-adoption-intent/v1-candidate'
             and intent['subject_carrier_version_ref'] == row['subject_carrier_version_ref']
             and intent['metadata_record_binding'] == row['metadata_record_binding']
             and intent['archive_binding'] == {'path': ARCHIVE.relative_to(ROOT).as_posix(),
                                               'sha256': ARCHIVE_SHA}
             and intent['actual_owner_outcome'] is None
             and intent['owner_outcome_required'] is True
             and intent['verified_owner_required'] is True
             and intent['consequence_rule']['append_new_governance_event_after_exact_R08_member_acceptance'] is True
             and intent['consequence_rule']['provenance_requires_actual_owner_Decision_binding'] is True,
             'original O06 intent body differs')
        need(intent['semantic_tuple'] == semantic_tuple,
             'original O06 intent semantic tuple changed')
        need(intent['predecessor_governance_tuple'] == predecessor,
             'original O06 intent predecessor tuple changed')
        cursor = predecessor['governance_cursor']
        need(semantic_tuple['semantic_cursor'] == cursor == position,
             'ordered original semantic/governance lineage changed')
        old_semantic = events['semantic'][cursor]
        old_governance = events['governance'][cursor]
        need({'semantic_event_id': old_semantic['event_id'],
              'semantic_event_digest': old_semantic['event_digest'],
              'semantic_cursor': old_semantic['semantic_cursor']} == semantic_tuple,
             'original semantic tuple changed')
        need({'event_id': old_governance['event_id'],
              'event_digest': old_governance['event_digest'],
              'governance_cursor': old_governance['governance_cursor']} == predecessor
             and old_governance['semantic_ref'] == semantic_tuple
             and old_governance['complete_resulting_governance_state']['semantic_ref'] == semantic_tuple,
             'original governance predecessor tuple changed')
        stream = old_governance['stream_id']
        need(stream not in seen_streams and old_governance['previous_event_digest'] is None,
             'expected original one-event-per-stream head changed')
        seen_streams.add(stream)
        draft = copy.deepcopy(old_governance)
        draft['event_id'] = f'fixture:T13:inert-governance:{position:03d}'
        draft['event_digest'] = '0' * 64
        draft['governance_cursor'] = 88 + position
        draft['previous_event_digest'] = predecessor['event_digest']
        state = draft['complete_resulting_governance_state']
        need(state['authority_effect'] == 'none' and state['candidate_or_maturity_status'] == 'candidate-unadmitted',
             'original candidate posture changed')
        state['provenance'].append({
            'source_ref': 'fixture:T13:intent:' + row['intent_binding']['sha256'],
            'relation': 'technical-predecessor-materialization',
            'operation': 'fixture-seal-only',
            'owner_route': 'fixture:T13:no-owner-decision',
            'posture': 'candidate-unadmitted-no-authority'})
        drafts.append(draft)
        rows.append({'position': position, 'member_ref': member,
                     'intent_binding': row['intent_binding'],
                     'semantic_tuple': semantic_tuple,
                     'predecessor_governance_tuple': predecessor,
                     'predecessor_stream_id': stream,
                     'expected_stream_version': 1,
                     'draft_event_id': draft['event_id'],
                     'draft_governance_cursor': draft['governance_cursor'],
                     'actual_owner_Decision_binding': None,
                     'authority_effect': 'none'})
    need(len(drafts) == len(rows) == len(seen_members) == len(seen_streams) == 88,
         'all 88 distinct original technical lineage rows required')
    return drafts, rows


def native_seal(drafts):
    installation = parse(exact(INSTALL, INSTALL_SHA))
    matches = [r for r in installation['added_inputs']
               if r.get('destination') == 'bin/lab-ontology-native']
    need(len(matches) == 1 and matches[0]['kind'] == 'ontology-native-executable'
         and matches[0]['sha256'] == NATIVE_SHA and matches[0]['mode'] == 0o755
         and matches[0]['source_binding']['sha256'] == NATIVE_SHA,
         'selected installed native executable lineage changed')
    source = ROOT / matches[0]['source_binding']['path']
    need(source.is_relative_to(ROOT), 'installed native source escapes repository')
    exact(source, NATIVE_SHA)
    exact(NATIVE, NATIVE_SHA)
    need(stat.S_IMODE(NATIVE.stat().st_mode) == 0o755
         and NATIVE.stat().st_size == matches[0]['size_bytes'],
         'selected native executable mode or size changed')
    with tempfile.TemporaryDirectory(prefix='cal-t13-inert-', dir='/tmp') as name:
        temp = Path(name)
        temp.chmod(0o700)
        source = temp / 'drafts.json'
        with source.open('xb') as out:
            out.write(json.dumps({'semantic': [], 'governance': drafts},
                                 separators=(',', ':'), ensure_ascii=False).encode())
        source.chmod(0o600)
        result = subprocess.run([str(NATIVE), 'seal', str(source)],
                                capture_output=True, check=False, timeout=60)
        need(result.returncode == 0 and not result.stderr,
             'actual native seal refused inert drafts')
        raw = result.stdout
        sealed = parse(raw)
        need(set(sealed) == {'semantic', 'governance'} and sealed['semantic'] == []
             and len(sealed['governance']) == 88, 'native seal output shape changed')
        # Extract each exact Rust-serialized event body from the aggregate
        # canonical stdout; Python serialization is not the native digest domain.
        text = raw.decode('utf-8')
        prefix = '{"semantic":[],"governance":['
        need(text.startswith(prefix) and text.endswith(']}\n'),
             'native aggregate canonical framing changed')
        decoder = json.JSONDecoder()
        offset = len(prefix)
        bodies = []
        for index, event in enumerate(sealed['governance']):
            observed, end = decoder.raw_decode(text, offset)
            need(observed == event, 'native event frame differs')
            bodies.append((text[offset:end] + '\n').encode('utf-8'))
            offset = end
            if index < 87:
                need(text[offset] == ',', 'native event separator differs')
                offset += 1
        need(text[offset:] == ']}\n', 'native aggregate trailing frame differs')
        return sealed['governance'], bodies, sha(raw)


def run():
    account = parse(exact(ACCOUNT, ACCOUNT_SHA))
    snapshot = parse(exact(ARCHIVE, ARCHIVE_SHA))
    drafts, rows = prepare(account, snapshot)
    sealed, bodies, aggregate_sha = native_seal(drafts)
    for draft, event, body, row in zip(drafts, sealed, bodies, rows):
        need(all(event[k] == draft[k] for k in draft if k != 'event_digest')
             and re.fullmatch('[a-f0-9]{64}', event['event_digest'])
             and event['event_digest'] != '0' * 64,
             'actual native sealed event differs from inert draft')
        token = ('"event_digest":"' + event['event_digest'] + '"').encode()
        need(body.count(token) == 1 and sha(body.replace(
             token, b'"event_digest":"' + b'0' * 64 + b'"', 1)) == event['event_digest'],
             'actual Rust canonical event zero-digest preimage differs')
        row['native_event_digest'] = event['event_digest']
        row['native_canonical_event_byte_sha256'] = sha(body)
        row['native_canonical_event_size_bytes'] = len(body)
        row['native_event_bytes_retained'] = False
    return {'schema_version': 'lab-T13-inert-native-materialization/v1-candidate',
            'result': 'PASS-bounded-inert-native-seal',
            'original_accounting_sha256': ACCOUNT_SHA,
            'original_archive_sha256': ARCHIVE_SHA,
            'selected_native_executable_sha256': NATIVE_SHA,
            'selected_native_installation_sha256': INSTALL_SHA,
            'native_aggregate_output_sha256': aggregate_sha,
            'rows': rows, 'technical_events_sealed': 88,
            'native_event_bytes_retained': False,
            'original_event_bytes_exported': False,
            'original_semantic_bytes_changed': False,
            'actual_owner_Decision_or_response_created': False,
            'native_append_calls': 0, 'repository_effects': 0,
            'authority_effect': 'none', 'T13_complete': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    output = Path(args.output)
    need(output.is_absolute() and output.is_relative_to(Path(__file__).parent)
         and not output.exists(), 'new task-local output path required')
    result = run()
    raw = (json.dumps(result, sort_keys=True, indent=2) + '\n').encode('utf-8')
    with output.open('xb') as out:
        out.write(raw)
        out.flush()
        os.fsync(out.fileno())
    print(json.dumps({'result': result['result'], 'rows': len(result['rows']),
                      'receipt_sha256': sha(raw), 'T13_complete': False}))
