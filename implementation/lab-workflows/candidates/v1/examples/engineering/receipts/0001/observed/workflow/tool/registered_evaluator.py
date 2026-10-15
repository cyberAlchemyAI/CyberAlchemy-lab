"""Candidate registered Tool evaluator; exact W02 actor guards preserved."""
from evaluator import *
from evaluator import HostAuthority as _OriginalHostAuthority

class HostAuthority(_OriginalHostAuthority):
    """Trusted host object; request bytes cannot instantiate or replace it.

    resolver(), status_reader() and grant_reader() are host-owned fresh readers.
    Dispatch must call check again under the local effect lock. Evaluation is
    evidence only, and must never be reused as a permission token.
    """
    def __init__(self, session, resolver, status_reader, grant_reader,
                 *, adapter_sha256, environment_sha256, registered_interfaces=frozenset({'bounded-local-counter/v1-candidate'})):
        require(type(registered_interfaces) is frozenset and registered_interfaces and all(type(v) is str and v for v in registered_interfaces), 'closed host interface registry required')
        self.registered_interfaces = registered_interfaces
        require(isinstance(session, SessionLease), 'host Session lease required')
        self.session = session
        self.resolver = resolver
        self.status_reader = status_reader
        self.grant_reader = grant_reader
        self.adapter_sha256 = adapter_sha256
        self.environment_sha256 = environment_sha256

    def check(self, raw, *, recovery=False):
        checks = []
        evidence = []
        request = None
        try:
            require(len(raw) <= 65536, 'request budget exceeded')
            request = parse(raw)
            require(type(request) is dict and set(request) == REQUEST_FIELDS, 'closed local action request required')
            require(all(type(request[k]) is str and request[k] for k in REQUEST_FIELDS - {'redelegating'}), 'nonempty exact request references required')
            require(type(request['redelegating']) is bool, 'redelegation must be explicit')
            require(len(request['idempotency_key']) <= 256, 'idempotency key budget exceeded')
            require(len(request['input_sha256']) == 64 and all(c in '0123456789abcdef' for c in request['input_sha256']), 'original input hash required')
            actual_context = self.session.check()
            now = self.session.clock()
            grant = self.grant_reader()
            require(isinstance(grant, HostGrant), 'explicit host grant absent')
            require(byte_sha(grant.evidence_original) == grant.evidence_sha256, 'host permission evidence changed')
            require(grant.not_before <= now < min(grant.expires_at, self.session.expires, timestamp(request['deadline'])), 'authority expired or not yet effective')
            require(request['principal_ref'] == grant.principal_ref, 'authenticated Principal mismatch')
            require(request['instance_ref'] == self.session.instance_ref and request['session_ref'] == self.session.session_ref, 'ephemeral Agent or Session mismatch')
            require(request['scope_ref'] == grant.scope_ref, 'scope denied')
            require(request['action_kind'] in grant.action_kinds, 'action denied')
            require(request['tool_ref'] == grant.tool_ref and request['role_assignment_ref'] == grant.role_assignment_ref, 'Tool or role grant mismatch')
            require(self.adapter_sha256 == grant.adapter_sha256 and self.environment_sha256 == grant.environment_sha256, 'adapter or environment changed')
            require(not recovery or grant.recovery_allowed, 'recovery authority denied')
            status = self.status_reader()
            require(status['head'] == request['expected_head'], 'stale authority cut')
            require(actual_context is None or actual_context['head'] == status['head'], 'Agent context cut differs')
            require(not status['stopped'], 'stop condition reached')
            records = {}
            for key, kind in [('principal_ref', 'principal'), ('role_assignment_ref', 'role-assignment'),
                              ('assignment_ref', 'agent-assignment'), ('delegation_ref', 'delegation'),
                              ('tool_ref', 'tool'), ('instance_record_ref', 'agent-instance'),
                              ('session_record_ref', 'agent-session'), ('profile_ref', 'agent-profile')]:
                require(request[key] not in status['revoked_refs'], 'authority revoked')
                selected = self.resolver(request[key])
                require(isinstance(selected, SelectedRecord) and selected.version_ref == request[key], 'exact authority reference unresolved')
                records[kind] = selected.record(kind)
                evidence.append({'ref': selected.source_ref, 'sha256': selected.expected_sha256})
            principal = records['principal']; role = records['role-assignment']
            assignment = records['agent-assignment']['payload']; delegation = records['delegation']['payload']
            tool = records['tool']['payload']
            instance_record = records['agent-instance']; session_record = records['agent-session']
            instance = instance_record['payload']; selected_session = session_record['payload']
            profile = records['agent-profile']['payload']
            require(status['runtime_handle_bindings'].get(request['instance_record_ref']) == self.session.instance_ref
                    and status['runtime_handle_bindings'].get(request['session_record_ref']) == self.session.session_ref,
                    'carrier and live runtime handle mapping differs')
            require(instance['accountable_principal_ref'] == principal['node_id']
                    and instance['profile_ref'] == request['profile_ref']
                    and instance['session_ref'] == session_record['node_id'], 'Instance attribution differs')
            require(selected_session['agent_instance_ref'] == instance_record['node_id']
                    and selected_session['assignment_ref'] == request['assignment_ref']
                    and selected_session['authority_envelope_ref'] == request['delegation_ref'], 'Session attribution differs')
            require(selected_session['termination_state'] == 'active'
                    and selected_session['session_memory']['expires_with_session'] is True,
                    'Session ended or persistent memory declared')
            require(instance_record['scope_ref'] == grant.scope_ref and session_record['scope_ref'] == grant.scope_ref,
                    'ephemeral carrier scope denied')
            require(set(selected_session['policy_refs']) <= set(status['active_policy_refs']), 'Session policy unresolved')
            require('agent-action' in profile['allowed_output_kinds'], 'Profile denies Action output')
            require(status['tool_classes'].get(request['tool_ref']) in profile['tool_class_refs'], 'Profile denies Tool class')
            require(set(profile['policy_refs']) <= set(status['active_policy_refs']), 'Profile policy unresolved')
            require(not set(profile['stop_conditions']) & set(status['reached_stop_conditions']), 'Profile stop condition reached')
            require(principal['payload']['status'] == 'active', 'Principal inactive')
            require(role['assignment_state'] == 'active' and role['scope_ref'] == grant.scope_ref, 'role inactive or out of scope')
            require(role['assignee_kind'] == 'person-reference' and role['assignee_ref'] == principal['payload']['stable_subject_ref'], 'role assignee differs from recognized Principal')
            role_version = status['role_versions'].get(role['role_ref'])
            require(role_version not in status['revoked_refs'], 'Role revoked')
            selected_role = self.resolver(role_version)
            require(isinstance(selected_role, SelectedRecord) and selected_role.version_ref == role_version, 'current Role unresolved')
            resolved_role = selected_role.record('role')
            require(resolved_role['node_id'] == role['role_ref'], 'Role identity mismatch')
            evidence.append({'ref': selected_role.source_ref, 'sha256': selected_role.expected_sha256})
            require(timestamp(role['period']['start']) <= now and (role['period']['end'] is None or now < timestamp(role['period']['end'])), 'role period expired')
            require(assignment['eligible_agent_ref'] == instance_record['node_id'], 'Assignment belongs to another ephemeral Agent')
            require(assignment['work_ref'] == status['selected_work_ref'], 'Assignment Work differs from selected Work')
            require(assignment['owner_ref'] == principal['node_id'] and delegation['delegator_principal_ref'] == principal['node_id'], 'assignment or delegation Principal differs')
            require(assignment['project_ref'] == grant.scope_ref and grant.scope_ref in delegation['scope_refs'], 'assignment or delegation scope denied')
            require(delegation['eligible_agent_ref'] == instance_record['node_id'], 'Delegation Agent differs')
            require(delegation['revocation_state'] == 'not-revoked', 'delegation revoked')
            require(request['action_kind'] in delegation['allowed_action_kinds'], 'delegated action denied')
            require(not request['redelegating'] or delegation['redelegation_allowed'], 'redelegation denied')
            for period_ref in [assignment['period'], delegation['effective_period']]:
                require(period_ref in status['periods'], 'unknown authority period')
                begin, end = status['periods'][period_ref]
                require(begin <= now < end, 'resolved authority period expired')
            require(not set(assignment['stop_conditions']) & set(status['reached_stop_conditions']), 'assignment stop condition reached')
            require(set(delegation['policy_refs']) <= set(status['active_policy_refs']), 'delegation policy unresolved')
            for gate in delegation['approval_gate_refs']:
                approval = status['gates'].get(gate)
                require(approval is not None and approval['scope_ref'] == grant.scope_ref
                        and approval['action_kind'] == request['action_kind']
                        and approval['input_sha256'] == request['input_sha256']
                        and now < approval['expires_at'], 'gate-required')
            require(tool['availability_posture'] == 'available', 'Tool unavailable')
            require(tool['interface_version'] in self.registered_interfaces, 'unsupported Tool interface')
            evidence.append({'ref': grant.evidence_ref, 'sha256': grant.evidence_sha256})
            checks.append({'check': 'exact-current-bounded-host-authority', 'result': 'PASS'})
            return {'posture': 'permitted', 'authority_effect': 'none', 'request_sha256': byte_sha(raw),
                    'request': request, 'checks': checks, 'evidence_bindings': evidence,
                    'grant': grant, 'tool_contract': tool}
        except Exception as exc:
            reason = str(exc)
            return {'posture': 'gate-required' if reason == 'gate-required' else 'denied',
                    'authority_effect': 'none', 'request_sha256': byte_sha(raw),
                    'request': request, 'checks': [{'check': reason, 'result': 'FLAG'}],
                    'evidence_bindings': evidence}
