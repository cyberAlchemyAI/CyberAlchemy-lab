#!/usr/bin/env python3
"""Join a valid saved attempt after an observed missing native handle.

Requires a caller-recorded native lookup witness. Never claims to have observed
the unavailable terminal response, regenerates output, or changes role criteria.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
from runtime_confirmation import runtime

R = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('unit')
parser.add_argument('role', choices=['Z', 'A', 'D'])
parser.add_argument('agent')
parser.add_argument('witness')
args = parser.parse_args()
module, schedule = runtime()
witness_path = R / args.witness
witness = json.loads(witness_path.read_text())
assert witness['agent_id'] == args.agent and witness['native_handle_missing_observed'] is True
assert witness['lookup_tool'] == 'collaboration.list_agents' and witness['returned_agents'] == []
events = [json.loads(x) for x in (R / 'receipts/events.jsonl').read_text().splitlines()]
prior = [e for e in events if e['unit_id'] == args.unit and e['role'] == args.role]
assert len(prior) == 1 and prior[0]['event'] == 'spawn' and prior[0]['agent_id'] == args.agent
receipt_path = R / 'receipts' / f'{args.unit}-{args.role}.json'
assert not receipt_path.exists()
value = module.validate(args.unit, args.role)
assert value['valid'], 'Missing or invalid saved output requires a separate failure disposition'
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
observation = {'native_terminal_response_observed': False, 'native_handle_missing_observed': True,
               'native_observation_witness': args.witness,
               'native_observation_witness_sha256': hashlib.sha256(witness_path.read_bytes()).hexdigest()}
event = {'observed_at_utc': now, 'event': 'join', 'unit_id': args.unit, 'role': args.role,
         'agent_id': args.agent, 'fork_turns': 'none', 'parent_reported_native_event': True,
         'artifact_validation': value, **observation}
receipt = {'unit_id': args.unit, 'role': args.role, 'agent_id': args.agent,
           'join_status': 'completed', 'close_status': 'native_handle_absent',
           'close_reason': 'Native lookup confirms the handle is absent after goal continuation; the saved first-attempt artifact passes the unchanged validator. Terminal response was unavailable.',
           'artifact_validation': value, 'sampling_call_count': None, 'actual_tokens': None,
           **observation,
           'limitations': ['Completion here means a valid saved artifact plus an observed absent native handle, not an observed terminal response.',
                          'No generation retry, substantive reconstruction, output repair or operating-system isolation is claimed.']}
receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
with (R / 'receipts/events.jsonl').open('a') as handle:
    handle.write(json.dumps(event) + '\n')
print(json.dumps(event, indent=2))
