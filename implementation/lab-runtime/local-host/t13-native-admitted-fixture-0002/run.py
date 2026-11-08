"""Run 88 synthetic admitted-state effects against disposable native storage."""
import base64
import copy
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import stat
import tempfile
import types

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

import gate


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
APPEND = ROOT / 'implementation/lab-runtime/local-host/t13-native-append-0001/append.py'
APPEND_SHA = '09c8c1475ba456d3b6d6ee130bed85e9be94a6218509e10e304606cffb58d8e5'
SCRATCH = HERE / 'scratch'


def selected_append():
    raw = APPEND.read_bytes()
    gate.need(gate.sha(raw) == APPEND_SHA, 'selected native append changed')
    module = types.ModuleType('_cal_t13_selected_native_append')
    module.__file__ = str(APPEND)
    exec(compile(raw, str(APPEND), 'exec', dont_inherit=True), module.__dict__)
    return module


def scratch_ready():
    if not SCRATCH.exists():
        SCRATCH.mkdir(mode=0o700)
    mode = SCRATCH.lstat()
    gate.need(stat.S_ISDIR(mode.st_mode) and not SCRATCH.is_symlink()
              and mode.st_uid == os.getuid() and stat.S_IMODE(mode.st_mode) == 0o700,
              'task-owned main-filesystem scratch required')


def redirect_native_tempfile(module, root):
    """Replace only the selected preparation's /tmp scratch destination."""
    def temporary_directory(*, prefix, dir):
        gate.need(dir == '/tmp' and prefix == 'cal-t13-inert-',
                  'selected native seal scratch call changed')
        return tempfile.TemporaryDirectory(prefix=prefix, dir=root)
    module.tempfile = types.SimpleNamespace(TemporaryDirectory=temporary_directory)


def files_digest(directory):
    rows = []
    for path in sorted(directory.rglob('*')):
        state = path.lstat()
        relative = path.relative_to(directory).as_posix()
        if stat.S_ISDIR(state.st_mode):
            rows.append((relative, 'directory'))
        elif stat.S_ISREG(state.st_mode):
            rows.append((relative, gate.sha(path.read_bytes())))
        else:
            raise ValueError('native directory contains an unsafe attachment')
    return rows


def refused(call, reason):
    try:
        call()
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return True
    raise ValueError(reason + ' was not refused')


def exact_original_representation_intents(module, rows):
    for row in rows:
        intent = module.parse(module.selected_binding(row['intent_binding']))
        rule = intent['consequence_rule']
        gate.need(rule['resulting_candidate_or_maturity_status'] ==
                  'admitted-representation' and
                  rule['source_meaning_admitted'] is False,
                  'original O06 representation/source-meaning distinction changed')


def run():
    scratch_ready()
    a = selected_append()
    m = a.selected_preparation()
    account = m.parse(m.exact(m.ACCOUNT, m.ACCOUNT_SHA))
    snapshot = m.parse(m.exact(m.ARCHIVE, m.ARCHIVE_SHA))
    original = m.archive_events(snapshot)
    drafts, rows = m.prepare(account, snapshot)
    exact_original_representation_intents(m, rows)
    drafts = gate.admitted_drafts(drafts, rows)
    # Keep the selected preparation's Rust seal and byte extraction mechanics;
    # only redirect its disposable input file away from the nearly full /tmp.
    redirect_native_tempfile(m, SCRATCH)
    successors, bodies, aggregate_sha = m.native_seal(drafts)
    gate.need(len(successors) == len(bodies) == 88 and all(
        all(event[k] == draft[k] for k in draft if k != 'event_digest')
        for event, draft in zip(successors, drafts)),
        'actual native seal changed an admitted-state fixture draft')
    plan = gate.fixed_plan(rows, successors, bodies,
                           account_sha=m.ACCOUNT_SHA, archive_sha=m.ARCHIVE_SHA,
                           native_sha=m.NATIVE_SHA)
    original_batch = {'semantic': [original['semantic'][i] for i in range(1, 89)],
                      'governance': [original['governance'][i] for i in range(1, 89)]}
    with tempfile.TemporaryDirectory(prefix='native-effect-', dir=SCRATCH) as name:
        native_root = Path(name)
        semantic_dir = native_root / 'semantic'
        governance_dir = native_root / 'governance'
        semantic_dir.mkdir(mode=0o700)
        governance_dir.mkdir(mode=0o700)
        first = a.append_batch(m, semantic_dir, governance_dir, original_batch, native_root)
        gate.need(first.returncode == 0 and not first.stderr, 'original frozen native bootstrap refused')
        first_read = a.native_call(m, 'read', semantic_dir, governance_dir, 88)
        gate.need(first_read.returncode == 0 and not first_read.stderr,
                  'original native cold read refused')
        observed = m.parse(first_read.stdout)
        gate.need(observed['result'] == 'PASS' and observed['checkpoint_parity'] == 'PASS'
                  and observed['semantic_events'] == original_batch['semantic']
                  and observed['governance_events'] == original_batch['governance'],
                  'observed original native predecessor bodies differ')
        observed_originals = observed['governance_events']
        key = Ed25519PrivateKey.generate()
        public = key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex()
        now = datetime.now(timezone.utc)
        ctx = gate.context(public, now)
        payload = gate.response_payload(plan, ctx, now.isoformat(),
                                        (now + timedelta(minutes=5)).isoformat())
        response_raw = gate.encoded({'payload': payload,
            'signature_hex': key.sign(gate.RESPONSE_DOMAIN + gate.encoded(payload)).hex()})
        decision_raw = gate.encoded(gate.decision(plan, ctx, response_raw)) + b'\n'
        witness_raw = gate.encoded(gate.witness(plan, ctx, response_raw, decision_raw)) + b'\n'
        before = files_digest(governance_dir)
        changed_payload = copy.deepcopy(payload)
        changed_payload['plan_byte_sha256'] = 'f' * 64
        changed_response = gate.encoded({'payload': changed_payload,
            'signature_hex': key.sign(gate.RESPONSE_DOMAIN + gate.encoded(changed_payload)).hex()})
        gate.need(refused(lambda: gate.verify_bundle(rows, successors, bodies,
                    observed_originals, plan, ctx, changed_response, decision_raw,
                    witness_raw, now, expected_originals=original_batch['governance']),
                    'changed response'), 'changed response refusal')
        changed_bodies = list(bodies)
        changed_bodies[0] += b' '
        gate.need(refused(lambda: gate.verify_bundle(rows, successors, changed_bodies,
                    observed_originals, plan, ctx, response_raw, decision_raw,
                    witness_raw, now, expected_originals=original_batch['governance']),
                    'changed target'), 'changed target refusal')
        changed_heads = copy.deepcopy(observed_originals)
        changed_heads[0]['event_digest'] = 'f' * 64
        gate.need(refused(lambda: gate.verify_bundle(rows, successors, bodies,
                    changed_heads, plan, ctx, response_raw, decision_raw,
                    witness_raw, now, expected_originals=original_batch['governance']),
                    'changed predecessor'), 'changed predecessor refusal')
        gate.need(refused(lambda: gate.verify_bundle(rows, successors, bodies,
                    observed_originals, plan, ctx, response_raw, decision_raw,
                    witness_raw, now + timedelta(minutes=6),
                    expected_originals=original_batch['governance']),
                    'expired response'), 'expired response refusal')
        gate.need(files_digest(governance_dir) == before,
                  'negative fixture gate changed native state')
        # Verify against the actual clock immediately before the native effect;
        # the issuance instant above is never reused as an execution clock.
        gate.verify_bundle(rows, successors, bodies, observed_originals, plan, ctx,
                           response_raw, decision_raw, witness_raw,
                           datetime.now(timezone.utc),
                           expected_originals=original_batch['governance'])
        second = a.append_batch(m, semantic_dir, governance_dir,
                                {'semantic': [], 'governance': successors}, native_root)
        gate.need(second.returncode == 0 and not second.stderr,
                  'signed fixture target native append refused')
        cold = a.fresh_read(m, semantic_dir, governance_dir)
        gate.need(cold['semantic_events'] == original_batch['semantic'] and
                  cold['governance_events'][:88] == observed_originals and
                  cold['governance_events'][88:] == successors,
                  'signed fixture native cold read differs')
        # The response and external Decision never enter the native event body.
        gate.need(all(gate.sha(raw) == target['event_byte_sha256']
                      for raw, target in zip(bodies, plan['targets'])),
                  'response modified sealed native target bytes')
        cold_join = {
            'predecessor_event_digests': [event['event_digest'] for event in observed_originals],
            'successor_event_digests': [event['event_digest'] for event in cold['governance_events'][88:]],
            'sealed_successor_body_sha256': [gate.sha(raw) for raw in bodies]}
        gate.need(cold_join['predecessor_event_digests'] ==
                  [t['predecessor']['event_digest'] for t in plan['targets']] and
                  cold_join['successor_event_digests'] ==
                  [t['event_digest'] for t in plan['targets']] and
                  cold_join['sealed_successor_body_sha256'] ==
                  [t['event_byte_sha256'] for t in plan['targets']],
                  'cold native predecessor/successor byte joins differ')
        admitted_count = sum(event['complete_resulting_governance_state']
                             ['candidate_or_maturity_status'] == 'admitted-representation'
                             for event in cold['governance_events'][88:])
        gate.need(admitted_count == 88 and all(
            event['complete_resulting_governance_state']['authority_effect'] == 'none'
            for event in cold['governance_events'][88:]),
            'cold native admitted-state fixture effect differs')
        result = {
            'schema_version': 'lab-T13-native-admitted-state-fixture-append/v1',
            'status': 'PASS-bounded-native-admitted-state-fixture',
            'fixture_only': True, 'authority_effect': 'none',
            'source_meaning_admitted': False,
            'original_accounting_sha256': m.ACCOUNT_SHA,
            'original_archive_sha256': m.ARCHIVE_SHA,
            'selected_preparation_sha256': a.PREPARATION_SHA,
            'selected_append_sha256': APPEND_SHA,
            'selected_native_executable_sha256': m.NATIVE_SHA,
            'native_aggregate_successor_seal_sha256': aggregate_sha,
            'fixed_plan_byte_sha256': gate.sha(gate.encoded(plan)),
            'response_byte_sha256': gate.sha(response_raw),
            'Decision_byte_sha256': gate.sha(decision_raw),
            'witness_byte_sha256': gate.sha(witness_raw),
            'ephemeral_owner_public_sha256': gate.sha(bytes.fromhex(public)),
            'synthetic_decision_identity_ref': gate.FIXTURE_DECISION,
            'fixture_plan': plan,
            'fixture_context': ctx,
            'signed_response_base64': base64.b64encode(response_raw).decode(),
            'external_Decision_base64': base64.b64encode(decision_raw).decode(),
            'external_witness_base64': base64.b64encode(witness_raw).decode(),
            'private_key_exported': False,
            'original_semantic_events_appended': 88,
            'original_governance_events_appended': 88,
            'fixture_admitted_state_governance_events_appended': admitted_count,
            'cold_semantic_events': len(cold['semantic_events']),
            'cold_governance_events': len(cold['governance_events']),
            'cold_checkpoint_parity': cold['checkpoint_parity'],
            'cold_88_join': cold_join,
            'cold_88_join_sha256': gate.sha(gate.encoded(cold_join)),
            'changed_response_refused_without_effect': True,
            'changed_target_refused_without_effect': True,
            'changed_predecessor_refused_without_effect': True,
            'expired_response_refused_without_effect': True,
            'native_event_bytes_changed_by_response': False,
            'original_owner_or_adoption_count': 0,
            'original_T13_complete': False,
            'repository_authority_effects': 0,
            'temporary_native_root_removed_on_return': False,
            'claim_ceiling': '88 exact native-sealed fixture admitted-representation states bound to an ephemeral signed response, deterministic external synthetic Decision and witness, then appended in disposable native storage; no actual owner, original adoption, current live head, or repository authority.'}
    gate.need(not native_root.exists(), 'private native storage remained')
    gate.need(not any(SCRATCH.iterdir()), 'task-owned scratch remained occupied')
    result['temporary_native_root_removed_on_return'] = True
    result['runner_sha256'] = gate.sha(Path(__file__).read_bytes())
    result['gate_sha256'] = gate.sha((HERE / 'gate.py').read_bytes())
    return result


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, indent=2))
