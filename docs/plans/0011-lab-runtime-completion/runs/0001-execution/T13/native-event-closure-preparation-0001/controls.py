"""Selected pure public accounting and conditional causal controls; no native calls."""
import argparse
import ast
import copy
import hashlib
import json
import os
import re
import sys
import types
from pathlib import Path

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE = Path(__file__).absolute().parent
INSTALL = ROOT / 'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'

def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--account-sha256', required=True)
    parser.add_argument('--selection-sha256', required=True); args = parser.parse_args()
    assert Path(sys.executable) == INSTALL / 'bin/python'
    sys.path.insert(0, str(INSTALL / 'deps'))
    import jsonschema
    checks = []; fd_start = len(os.listdir('/proc/self/fd'))
    def check(name, value):
        if not value: raise AssertionError(name)
        checks.append(name)
    path = HERE / 'account.py'; raw = path.read_bytes()
    check('independent exact own accounting code', hashlib.sha256(raw).hexdigest() == args.account_sha256)
    module = types.ModuleType('_cal_T13_owned_public_accounting'); module.__file__ = str(path)
    exec(compile(raw, str(path), 'exec', dont_inherit=True), module.__dict__)
    packet = module.parse(module.capture({'path': (HERE / 'input-selection.json').relative_to(ROOT).as_posix(),
        'sha256': args.selection_sha256}))
    value = module.analyze(packet)
    check('all88 no event or core materialization', value['explicitly_blocked_intents'] == 88 and value['actual_materialized_events'] == 0)
    for row in value['rows']:
        check('all88 explicit blockers:' + row['member_ref'], row['blockers'] == list(module.BLOCKERS)
            and all(row[k] is None for k in ['actual_owner_Decision_binding', 'actual_owner_response',
                'native_event_bytes', 'native_event_digest', 'stable_unsigned_core'])
            and row['T10_dependency_complete'] is False and row['T11_dependency_complete'] is False
            and row['single_checkpoint_ready'] is False and row['authority_effect'] == 'none')
    check('38 node/50 relation intents retained', sum(r['subject_carrier_version_ref'].startswith('ontology-node:') for r in value['rows']) == 38
        and sum(r['subject_carrier_version_ref'].startswith('ontology-relation:') for r in value['rows']) == 50)
    original_schema = next(row for row in packet['files'] if row['path'].endswith('O06/schemas/adoption-intent.schema.json'))
    schema = module.parse(module.capture(original_schema)); jsonschema.Draft202012Validator.check_schema(schema)
    for row in value['rows']:
        intent = module.parse(module.capture(row['intent_binding']))
        jsonschema.Draft202012Validator(schema).validate(intent)
        check('all88 actual original intent schema:' + row['member_ref'], True)
    def refuses(name, packet):
        try: module.analyze(packet)
        except (ValueError, OSError, KeyError): check(name, True)
        else: raise AssertionError(name)
    changed = copy.deepcopy(packet); changed['expected_intent_count'] = 87; refuses('no dropped member count', changed)
    changed = copy.deepcopy(packet); changed['real_owner_response_allowed'] = True; refuses('no forged response authority', changed)
    changed = copy.deepcopy(packet); changed['files'].append(changed['files'][0]); refuses('duplicate selected physical row', changed)
    changed = copy.deepcopy(packet); changed['final_selection_binding']['sha256'] = 'f' * 64; refuses('cross package selector digest refusal', changed)
    changed = copy.deepcopy(packet); changed['unexpected'] = 'inert'; refuses('open selection refusal', changed)
    for private_name in ['native.snapshot', 'branch.snapshot']:
        try: module.capture({'path': 'inert/' + private_name, 'sha256': '0' * 64})
        except ValueError: check('private archive refused before read:' + private_name, True)
        else: raise AssertionError('private body capture permitted')
    try: module.capture({'path': '../inert', 'sha256': '0' * 64})
    except ValueError: check('no outside root locator', True)
    else: raise AssertionError('outside root locator permitted')
    native_row = next(r for r in packet['files'] if r['path'].endswith('adapters/native/src/lib.rs'))
    native = module.capture(native_row).decode()
    def fields(name):
        text = re.search(r'pub struct ' + name + r' \{(.*?)\n\}', native, re.S).group(1)
        return re.findall(r'pub ([a-z_]+):', text)
    check('closed original five string provenance fields', fields('ProvenanceEntry') == ['source_ref', 'relation', 'operation', 'owner_route', 'posture'])
    check('original event has no response envelope', 'complete_resulting_governance_state' in fields('GovernanceEvent')
        and all('response' not in n and 'authorization' not in n for n in fields('GovernanceEvent')))
    check('append request contains only version and event', fields('AppendGovernanceEventRequest') == ['expected_stream_version', 'event'])
    digest_validator = native[native.index('fn validate_governance_event_digest'):native.index('fn load_semantic_directory')]
    check('wholeevent digest changes only own digest field', 'preimage.event_digest = ZERO_DIGEST.to_owned();' in digest_validator
        and 'digest_value(&preimage)' in digest_validator and 'provenance' not in digest_validator)
    check('schema source ref does not impose Decision hash', 'pub source_ref: String' in native)
    # This is an inert symbolic term, not a Decision, event or native serialized
    # target. It demonstrates inclusion of unknown bytes, not hash injectivity.
    a = {'analysis_only': True, 'symbolic_provenance_reference': 'UNRESOLVED_D01_A'}
    b = {'analysis_only': True, 'symbolic_provenance_reference': 'UNRESOLVED_D01_B'}
    check('symbolic unknown binding affects whole preimage', json.dumps(a) != json.dumps(b)
        and hashlib.sha256(json.dumps(a).encode()).digest() != hashlib.sha256(json.dumps(b).encode()).digest())
    lifecycle = module.capture(next(r for r in packet['files'] if r['path'].endswith('adapters/lifecycle/cold_lifecycle.py'))).decode()
    check('original challenge external witness exists; not universal schema impossibility', "original(w['source_resolution_decision_binding'])" in lifecycle)
    for row in packet['files']: module.capture(row)
    check('full199 public inputs guarded entry exit', len(packet['files']) == 199)
    check('FD delta zero', len(os.listdir('/proc/self/fd')) == fd_start)
    report = {'schema_version': 'lab-T13-pure-preparation-controls/v1-candidate', 'result': 'PASS',
        'checks': checks, 'check_count': len(checks), 'account_sha256': args.account_sha256,
        'selection_sha256': args.selection_sha256, 'public_inputs_entry_exit': 199, 'FD_delta': 0,
        'all88_original_intent_schemas_validated': True, 'actual_native_materializer_or_events': False,
        'actual_Decision_or_owner_response': False, 'original_private_archive_read': False,
        'Lab_native_engine_or_Store_or_lease': False, 'shared_change': False,
        'authority_effect': 'none', 'task_complete': False}
    with (HERE / 'CONTROLS.json').open('x') as stream:
        stream.write(json.dumps(report, sort_keys=True, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'checks'}))

if __name__ == '__main__': main()
