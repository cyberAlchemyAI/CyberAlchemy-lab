"""Explicit typed targets only; protocol/file bindings do not become admissions."""
import argparse
import ast
import base64
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from jsonschema import Draft202012Validator
import build_runtime as B

HERE = Path(__file__).resolve().parent
ROOT = B.ROOT

def original(row):
    B.need(set(row) == {'path', 'sha256'}, 'closed independent binding required')
    path = ROOT / row['path']
    B.need(B.bind(path) == row, 'bound original input changed: ' + row['path'])
    return B.read(path)

def family(api, pin, profile_pin):
    B.need(api.parent == B.BASE, 'actual selected API family required')
    guard = B.module('_typed_materializer_guard_' + uuid.uuid4().hex, api / 'guard.py')
    guard.verify(pin)
    B.exact(api / 'contract-profile.json', profile_pin)
    name = '_typed_materializer_' + uuid.uuid4().hex
    B.module(name, api, True)
    bridge = __import__(name + '.source_bridge', fromlist=['replay_source'])
    return guard, bridge

def inventory(path, pin, additional=None):
    value = B.exact(path, pin)
    B.need(value['authority_effect'] == 'none' and value['actual_owner_outcome'] is None,
           'preparation inventory grants no authority')
    rows = list(value['members'])
    if additional:
        rows.append(json.loads(original(additional)))
    by_id = {}
    for row in rows:
        identity = row.get('member_id') or row.get('member_ref')
        B.need(identity and identity not in by_id, 'exact unique member identity required')
        B.need(row.get('actual_answering_principal_ref') is None and row.get('current_owner_authority_verified') is False,
               'this preparation cannot invent owner recognition')
        by_id[identity] = row
    return by_id

def diagnose(args):
    """Report representation work, without inferring an operation or core."""
    members = inventory(Path(args.inventory), args.inventory_sha256)
    groups = {}
    protocol_only = []
    governed = []
    for identity, row in members.items():
        value = row.get('selected_record')
        bindings = row.get('targets', [])
        kinds = []
        for binding in bindings:
            raw = original(binding)
            if raw.lstrip().startswith(b'{'):
                try:
                    candidate = json.loads(raw)
                    if isinstance(candidate, dict) and candidate.get('kind') and candidate.get('schema_version'):
                        kinds.append({'binding': binding, 'kind': candidate['kind'], 'schema_version': candidate['schema_version']})
                except json.JSONDecodeError:
                    pass
        state = 'governed-record-needs-explicit-carrier-operation-preimage-selection' if kinds or isinstance(value, dict) and value.get('kind') else 'protocol-only-needs-proper-governed-representation'
        entry = {'member_ref': identity, 'member_class': row['member_class'],
                 'observed_governed_record_candidates': kinds, 'posture': state,
                 'proposed_roles': row['proposed_owner_roles'], 'owner_authority_resolved': False,
                 'operation_selected': False, 'stable_core_created': False}
        (governed if state.startswith('governed') else protocol_only).append(entry)
        groups[row['member_class']] = groups.get(row['member_class'], 0) + 1
    report = {'schema_version': 'lab-explicit-target-materializer-inventory-audit/v1-candidate',
              'observed_at': datetime.now(timezone.utc).isoformat(), 'inventory_binding': B.bind(Path(args.inventory)),
              'materializer_binding': B.bind(Path(__file__)), 'member_count': len(members), 'member_classes': groups,
              'governed_record_candidates': governed, 'protocol_only_members': protocol_only,
              'no_generic_file_admission': True, 'all_member_targets_materialized': False,
              'owner_authority_resolved': False, 'actual_owner_outcome': None, 'authority_effect': 'none',
              'ready_for_R08': False, 'task_complete': False, 'goal_complete': False}
    B.emit(Path(args.output), report)
    print(json.dumps({'result': 'AUDITED-UNMATERIALIZED', 'members': len(members),
                      'protocol_only_members': len(protocol_only), 'report_binding': B.bind(Path(args.output))}), flush=True)

def materialize(args):
    selection = B.exact(Path(args.selection), args.selection_sha256)
    B.need(set(selection) == {'schema_version', 'inventory_binding', 'additional_member_binding',
        'API_source_binding', 'API_profile_binding', 'source_name', 'targets',
        'native_proposal_binding', 'authority_effect', 'actual_owner_outcome'}, 'closed explicit target selection required')
    B.need(selection['schema_version'] == 'lab-explicit-final-target-selection/v1-candidate'
        and selection['authority_effect'] == 'none' and selection['actual_owner_outcome'] is None,
        'target selection cannot supply owner authority')
    original(selection['API_source_binding']); original(selection['API_profile_binding'])
    api = (ROOT / selection['API_source_binding']['path']).parent
    B.need(selection['API_profile_binding']['path'] == str((api / 'contract-profile.json').relative_to(ROOT)), 'profile outside selected actual API')
    members = inventory(ROOT / selection['inventory_binding']['path'], selection['inventory_binding']['sha256'], selection['additional_member_binding'])
    guard, bridge = family(api, selection['API_source_binding']['sha256'], selection['API_profile_binding']['sha256'])
    output = Path(args.output_directory).resolve()
    B.need(output.parent == B.OUTPUT_BASE and not output.exists(), 'exclusive separately owned target output directory required')
    output.mkdir(mode=0o700)
    materialized = []
    selected_ids = set()
    with bridge.replay_source(selection['source_name']) as view:
        before = view.handle.common.digest(view.data['projection'])
        for index, item in enumerate(selection['targets']):
            B.need(set(item) == {'member_ref', 'operation', 'category', 'carrier_ref', 'version_ref',
                'decision_ref', 'record_binding', 'schema_binding', 'descriptor_binding', 'predecessor_binding'},
                'proper explicit typed target selection required; generic file admission refused')
            identity = item['member_ref']
            B.need(identity in members and identity not in selected_ids, 'unknown or repeated selected member')
            selected_ids.add(identity)
            raw = original(item['record_binding']); record = json.loads(raw)
            B.need(isinstance(record, dict) and record.get('schema_version'), 'raw code/file bytes are not a governed target body')
            contract = view.data['projection']['contracts'].get(item['carrier_ref'])
            B.need(contract is not None, 'carrier has no independently selected original declaration')
            B.need(item['schema_binding'] == {'path': contract['schema_path'], 'sha256': contract['schema_sha256']}
                and item['descriptor_binding'] == {'path': contract['artifact_path'], 'sha256': contract['artifact_sha256']}, 'carrier origin/schema witness differs')
            schema = json.loads(original(item['schema_binding'])); original(item['descriptor_binding'])
            B.need(contract.get('schema_selector') is None, 'fragment carrier requires an explicitly supported exact materializer successor')
            Draft202012Validator(schema).validate(record)
            category = {'artifact-type': 'artifact-type', 'definition': 'definition',
                        'relation-kind': 'relation-kind', 'typed-relation': 'typed-relation'}.get(contract['semantic_kind'], 'artifact-instance')
            B.need(item['category'] == category, 'target category disagrees with original carrier kind')
            discriminator = contract['instance_discriminator']
            B.need(view.handle.common.pointer(record, discriminator['path']) == discriminator['value'], 'schema discriminator differs')
            descriptor = json.loads(original(item['descriptor_binding']))
            selector = descriptor.get('instance_contract', {}).get('identity_field') or descriptor.get('identity_field')
            B.need(selector, 'carrier needs a separately bound exact identity-selector representation')
            record_id = view.handle.common.pointer(record, selector if selector.startswith('/') else '/' + selector)
            B.need(item['operation'] in ('admit', 'revise'), 'withdraw/registry/protocol effects need their proper exact representation')
            predecessor = item['predecessor_binding']
            if item['operation'] == 'admit':
                B.need(predecessor is None and not any(s['identity'] == record_id and s['effective_state'] in ('admitted-current', 'local-admitted-current') for s in view.subjects.values()), 'admission requires no current identity/predecessor')
            else:
                B.need(predecessor is not None, 'revision must select exact current predecessor')
                predecessor_raw = original(predecessor)
                candidates = [s for s in view.subjects.values() if s['identity'] == record_id and s['effective_state'] in ('admitted-current', 'local-admitted-current')]
                B.need(len(candidates) == 1 and json.loads(predecessor_raw) == candidates[0]['record'], 'revision predecessor is absent or differs from original current source')
            content = view.handle.custody.content_entry(raw)
            target = {'category': item['category'], 'operation': item['operation'], 'carrier_ref': item['carrier_ref'],
                      'version_ref': item['version_ref'], 'decision_ref': item['decision_ref'],
                      'predecessor_ref': None if predecessor is None else candidates[0]['version_ref'],
                      'record': record, 'content': content, 'contract': None}
            # Materialization retains source bytes; it never adds these records to the read projection.
            path = output / ('target-' + str(index).zfill(4) + '.json')
            B.emit(path, target)
            materialized.append({'member_ref': identity, 'target_binding': B.bind(path), 'original_body_binding': item['record_binding']})
        native = selection['native_proposal_binding']
        cores = None
        if native is not None:
            proposal = json.loads(original(native))
            B.need(proposal['targets'] == [B.load(ROOT / r['target_binding']['path']) for r in materialized], 'independent original native proposal target bytes differ')
            # Actual selected original Store.review over an exact restored cold source; no callbacks supplied.
            with tempfile.TemporaryDirectory(prefix='cal-final-target-original-review-0254-') as temporary:
                store = Path(temporary) / 'store'; store.mkdir(mode=0o700); (store / 'transactions').mkdir(mode=0o700)
                for name, raw in view.originals.items():
                    path = store / name; path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                    with path.open('xb') as stream: stream.write(raw)
                    path.chmod(0o600)
                reviewed = view.handle.store_module.Store(store, ROOT).review(proposal)
                cores = reviewed['decision_cores']
                B.emit(output / 'actual-original-native-review.json', reviewed)
                B.need(all((store / name).read_bytes() == raw for name, raw in view.originals.items()), 'pure review changed original source bytes')
        B.need(view.handle.common.digest(view.data['projection']) == before, 'original signed projection was modified or grafted')
        view.handle.guard()
    guard.verify(selection['API_source_binding']['sha256'])
    report = {'schema_version': 'lab-explicit-final-target-materialization/v1-candidate',
        'selection_binding': B.bind(Path(args.selection)), 'materializer_binding': B.bind(Path(__file__)),
        'materialized_targets': materialized, 'unselected_member_refs': sorted(set(members) - selected_ids),
        'actual_original_native_cores': cores, 'all_member_targets_materialized': selected_ids == set(members),
        'native_review_executed': native is not None, 'owner_authority_resolved': False,
        'actual_owner_outcome': None, 'authority_effect': 'none', 'source_admissions': 0,
        'projection_grafted': False, 'ready_for_R08': False, 'task_complete': False, 'goal_complete': False}
    B.emit(output / 'materialization.json', report)
    print(json.dumps({'result': 'MATERIALIZED-CANDIDATE-ONLY', 'targets': len(materialized),
        'report_binding': B.bind(output / 'materialization.json'), 'owner_authority_resolved': False}), flush=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('audit-inventory', 'materialize'))
    for name in ('inventory', 'inventory-sha256', 'output', 'selection', 'selection-sha256', 'output-directory'):
        parser.add_argument('--' + name)
    args = parser.parse_args()
    if args.command == 'audit-inventory':
        B.need(args.inventory and args.inventory_sha256 and args.output, 'independent inventory/output required')
        diagnose(args)
    else:
        B.need(args.selection and args.selection_sha256 and args.output_directory, 'independent typed selection/output required')
        materialize(args)

if __name__ == '__main__':
    main()
