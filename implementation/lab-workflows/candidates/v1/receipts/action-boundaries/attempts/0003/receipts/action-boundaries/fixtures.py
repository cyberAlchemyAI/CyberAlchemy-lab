"""Owned isolated W02 host fixture; these are not production authority records."""
import copy
from dataclasses import replace
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PACKAGE/'authority'))
from evaluator import *
from dispatch import *
from counter import INPUT_CONTRACT, OUTPUT_CONTRACT


class Fixture:
    def __init__(self, *, session=None, head='protocol:w02-isolated-head'):
        self.now = [1791460800.0]
        self.session = session or SessionLease(clock=lambda: self.now[0])
        self.scope = 'project:cyberalchemy-v2-to-lab-migration'
        self.records = {}; self.by_kind = {}
        for kind in ['principal', 'role', 'role-assignment', 'agent-assignment', 'delegation', 'tool', 'agent-instance', 'agent-session', 'agent-profile']:
            value = parse((ROOT/f'authority/artifact-types/{kind}/v1/fixtures/valid/record.json').read_bytes())
            value['node_id'] = kind + ':w02-isolated-fixture'; value['scope_ref'] = self.scope
            self.by_kind[kind] = value
        for kind in ['agent-instance','agent-session']:
            self.by_kind[kind]['node_id'] = kind+':w02:'+self.session.instance_ref.split(':')[-1]
        principal = self.by_kind['principal']; assignment = self.by_kind['agent-assignment']['payload']
        role = self.by_kind['role-assignment']; delegation = self.by_kind['delegation']['payload']
        role['assignee_ref'] = principal['payload']['stable_subject_ref']; role['role_ref'] = self.by_kind['role']['node_id']
        assignment.update(eligible_agent_ref=self.by_kind['agent-instance']['node_id'], owner_ref=principal['node_id'], project_ref=self.scope, period='protocol:w02-period')
        delegation.update(eligible_agent_ref=self.by_kind['agent-instance']['node_id'], delegator_principal_ref=principal['node_id'], scope_refs=[self.scope], allowed_action_kinds=['increment-local-counter'], approval_gate_refs=[], policy_refs=['protocol:w02-local-policy'], effective_period='protocol:w02-period')
        self.by_kind['agent-instance']['payload'].update(accountable_principal_ref=principal['node_id'],profile_ref=self.ref('agent-profile'),session_ref=self.by_kind['agent-session']['node_id'])
        self.by_kind['agent-session']['payload'].update(agent_instance_ref=self.by_kind['agent-instance']['node_id'],assignment_ref=self.ref('agent-assignment'),authority_envelope_ref=self.ref('delegation'),policy_refs=['protocol:w02-local-policy'])
        self.by_kind['agent-profile']['payload'].update(allowed_output_kinds=['agent-action'],tool_class_refs=['tool-class:bounded-local-counter'],policy_refs=['protocol:w02-local-policy'])
        self.by_kind['tool']['payload'].update(interface_version='bounded-local-counter/v1-candidate', input_contract_ref='protocol:w02-counter-input:'+byte_sha(encoded(INPUT_CONTRACT)), output_contract_ref='protocol:w02-counter-output:'+byte_sha(encoded(OUTPUT_CONTRACT)))
        for kind in self.by_kind: self.reselect(kind)
        evidence = encoded({'scope': 'explicit owned isolated W02 tests', 'authorization_ref': 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json', 'fixture_only': True, 'actual_owner_outcome': None})
        self.adapter_sha256 = byte_sha((PACKAGE/'tools/counter.py').read_bytes())
        self.environment_sha256 = byte_sha(encoded({'python': sys.version, 'network': False, 'filesystem': 'owned isolated fixture root only'}))
        self.grant = HostGrant(self.ref('principal'), self.scope, frozenset({'increment-local-counter'}), self.ref('tool'), self.ref('role-assignment'), self.now[0]-60, self.now[0]+900, 8, 4096, 4096, 'protocol:w02-explicit-fixture-development-permission', evidence, byte_sha(evidence), self.adapter_sha256, self.environment_sha256, recovery_allowed=True)
        self.status = {'head': head, 'stopped': False, 'revoked_refs': [], 'periods': {'protocol:w02-period': [self.now[0]-60, self.now[0]+900]}, 'reached_stop_conditions': [], 'active_policy_refs': ['protocol:w02-local-policy'], 'gates': {}, 'role_versions': {self.by_kind['role']['node_id']: self.ref('role')}}
        self.status.update(runtime_handle_bindings={self.ref('agent-instance'):self.session.instance_ref,self.ref('agent-session'):self.session.session_ref},tool_classes={self.ref('tool'):'tool-class:bounded-local-counter'},selected_work_ref=assignment['work_ref'])
        self.authority = HostAuthority(self.session, lambda ref: self.records.get(ref), lambda: copy.deepcopy(self.status), lambda: self.grant, adapter_sha256=self.adapter_sha256, environment_sha256=self.environment_sha256)
        self.input = encoded({'increment': 1})
        self.request = {'principal_ref': self.ref('principal'), 'instance_ref': self.session.instance_ref, 'session_ref': self.session.session_ref, 'assignment_ref': self.ref('agent-assignment'), 'delegation_ref': self.ref('delegation'), 'role_assignment_ref': self.ref('role-assignment'), 'tool_ref': self.ref('tool'), 'scope_ref': self.scope, 'action_kind': 'increment-local-counter', 'idempotency_key': 'w02-case-1', 'input_sha256': byte_sha(self.input), 'deadline': datetime.fromtimestamp(self.now[0]+800, timezone.utc).isoformat(), 'expected_head': head, 'redelegating': False}
        self.request.update(instance_record_ref=self.ref('agent-instance'),session_record_ref=self.ref('agent-session'),profile_ref=self.ref('agent-profile'))

    def ref(self, kind):
        suffix = self.session.instance_ref.split(':')[-1] if kind in {'agent-assignment', 'delegation'} else '1'
        return self.by_kind[kind]['node_id'] + '@isolated-candidate.' + suffix

    def reselect(self, kind):
        raw = encoded(self.by_kind[kind]); ref = self.ref(kind)
        self.records[ref] = SelectedRecord(ref, raw, byte_sha(raw), 'isolated-candidate-current', 'protocol:w02-original-selected-fixture:'+ref)

    def raw(self): return encoded(self.request)
