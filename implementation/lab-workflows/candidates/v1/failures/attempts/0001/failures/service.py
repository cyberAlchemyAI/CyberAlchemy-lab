"""W05 evidence-backed annotation and independent failure axes."""
from dataclasses import dataclass
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evidence.service import EvidenceService, OUTPUT_KINDS, OLD_BUILDER, NEW_BUILDER, VERSION, utc
from research import ROOT, CAPABILITY, require, parse, byte_sha, encoded


@dataclass(frozen=True)
class IncidentPolicy:
    version_ref: str
    allow_controlled: bool
    minimum_failed_preparations: int


class FailureService:
    def __init__(self, evidence):
        require(isinstance(evidence, EvidenceService), 'host-selected evidence service required')
        self.e = evidence
        self.assignments = {}
        for ref in evidence.records:
            record = evidence.get(ref)
            if record['kind'] == 'classification-assignment' and record['payload']['status'] == 'candidate-annotation':
                a = record['payload']
                key = (a['subject_version_ref'], a['scheme_version_ref'], a['axis_ref'])
                require(key not in self.assignments, 'duplicate reconstructed classification axis')
                self.assignments[key] = ref
        # Host-selected local policies, not an Incident/classification field.
        self.policies = {
            'protocol:W05-production-threshold@1': IncidentPolicy('protocol:W05-production-threshold@1', False, 1),
            'protocol:W05-controlled-threshold@1': IncidentPolicy('protocol:W05-controlled-threshold@1', True, 1)}

    def classify(self, name, subject, scheme, value, action, observation, evidence_set, implementation):
        e = self.e
        s, v, x = e.get(scheme, 'classification-scheme'), e.get(value, 'classification-value'), e.get(subject)
        e.get(action, 'agent-action'); e.get(observation, 'operational-observation'); e.get(evidence_set, 'evidence-set')
        require(action == e.action_ref and e.get(observation)['payload']['action_ref'] == action
            and e.manifest_ref in e.get(observation)['payload']['evidence_refs'], 'classification Action/observation provenance differs')
        e.get(implementation, 'implementation')
        axis = v['payload']['axis_ref']
        require(v['payload']['scheme_ref'] == scheme and value in s['payload']['value_refs'], 'exact Scheme/Value mismatch')
        require(axis in s['payload']['axis_refs'] and s['payload']['cardinality_rules'] == ['one-active-value-per-subject-axis'], 'classification axis/cardinality unresolved')
        require(s['payload']['compatibility_rules'] == ['annotation-never-grants-authority'], 'classification compatibility rule unresolved')
        slot = (subject, scheme, axis)
        require(slot not in self.assignments, 'duplicate active classification on axis')
        require(observation in e.get(evidence_set)['payload']['item_refs'], 'classification observation outside Evidence Set')
        result = e.put(e.make('classification-assignment', name, {
            'subject_ref': x['node_id'], 'subject_version_ref': subject, 'scheme_version_ref': scheme,
            'axis_ref': axis, 'value_ref': value, 'basis': 'actual-controlled-schema-rejection',
            'action_ref': action, 'method_ref': 'protocol:W05-exact-schema-manifest-method@1',
            'implementation_ref': implementation, 'evidence_refs': [observation, evidence_set],
            'effective_period': 'protocol:W05-selected-controlled-episode', 'status': 'candidate-annotation'}))
        self.assignments[slot] = result
        return result

    def assess(self, name, occurrence, assignment, cause_hypotheses, *, cause_posture='proposed',
               impact='bounded-controlled-preparation', containment='stopped-before-publication', recovery='successor-verified-old-revision-unresolved'):
        e = self.e
        o, a = e.get(occurrence, 'failure-occurrence'), e.get(assignment, 'classification-assignment')
        require(a['payload']['subject_version_ref'] == occurrence, 'assessment classification applies to another revision')
        v = e.get(a['payload']['value_ref'], 'classification-value')
        e.get(v['payload']['definition_ref'], 'failure-mode')
        require(cause_posture in ['proposed', 'unresolved'] and o['payload']['cause_posture'] in ['proposed', 'unresolved'], 'cause hypothesis cannot become a fact')
        for h in cause_hypotheses:
            require(e.get(h, 'hypothesis')['payload']['disposition'] == 'open', 'unverified cause must remain open')
        manifest_ref = e.manifest_ref
        require(manifest_ref is not None and manifest_ref in e.get(o['payload']['detection_evidence_refs'][0], 'operational-observation')['payload']['evidence_refs'], 'occurrence original observation chain unresolved')
        m = parse(e.original(manifest_ref))
        require(m['controlled'] is True and m['failed_preparations'] == 1 and m['subject_bytes_unchanged'], 'controlled failure manifest differs')
        require(o['payload']['subject_ref'] == e.subject_ref and o['payload']['observed_manifestations'] == [m['observations'][0]['result']['exception_message']], 'occurrence manifestation/subject differs from observation')
        require(impact == 'bounded-controlled-preparation' and containment == 'stopped-before-publication', 'unsupported impact/containment inference')
        require(recovery == 'successor-verified-old-revision-unresolved' and m['observations'][1]['result']['preparation_posture'] == 'completed'
            and m['observations'][1]['result']['validated_records'] == 13, 'recovery evidence not established')
        return e.put(e.make('failure-assessment', name, {'occurrence_ref': occurrence, 'mode_assignment_ref': assignment,
            'occurrence_posture': 'supported-controlled', 'mode_posture': 'supported-manifestation-only',
            'cause_hypothesis_refs': cause_hypotheses, 'impact_posture': impact, 'containment_posture': containment,
            'recovery_posture': recovery, 'uncertainty_refs': ['protocol:W05-cause-unconfirmed', 'protocol:W05-old-revision-review-pending', 'protocol:W05-no-production-generalization']}))

    def incident(self, name, occurrence, assessment, policy_ref, *, production=False):
        e = self.e
        e.get(occurrence, 'failure-occurrence')
        a = e.get(assessment, 'failure-assessment')
        require(a['payload']['occurrence_ref'] == occurrence, 'Incident Assessment applies elsewhere')
        require(policy_ref in self.policies, 'host-selected Incident policy absent')
        policy = self.policies[policy_ref]
        m = parse(e.original(e.manifest_ref))
        require(not production or not m['controlled'], 'controlled case cannot be labeled production Incident')
        threshold = m['failed_preparations'] >= policy.minimum_failed_preparations
        accepted = threshold and (policy.allow_controlled or not m['controlled'])
        disposition = {'policy_ref': policy.version_ref, 'controlled': m['controlled'], 'failed_preparations': m['failed_preparations'],
            'threshold_met': threshold, 'eligible': accepted, 'authority_effect': 'none', 'actual_owner_outcome': None}
        if not accepted:
            return None, disposition
        ref = e.put(e.make('incident', name, {'occurrence_refs': [occurrence],
            'impact_summary': 'Controlled Incident: one owned candidate preparation rejected; no production effects observed.',
            'accountable_principal_ref': e.host.ref('principal'), 'timeline_refs': [e.manifest_ref],
            'containment_refs': [assessment], 'recovery_refs': [assessment], 'communication_refs': [], 'decision_refs': [],
            'closure_state': 'controlled-contained-review-pending', 'residue_refs': ['protocol:W05-old-revision-review-pending']}))
        return ref, disposition

    def materialize(self, manifest_ref):
        e = self.e
        require(manifest_ref == e.manifest_ref, 'only attributable host probe evidence accepted')
        m = parse(e.original(manifest_ref))
        require(m['controlled'] and m['failed_preparations'] == 1 and m['subject_bytes_unchanged'], 'bounded controlled preparation result required')
        bad, good = [v['result'] for v in m['observations']]
        require(bad['exception_type'] == 'BoundaryFault' and 'experiment-design' in bad['exception_message']
            and good['preparation_posture'] == 'completed' and good['validated_records'] == 13, 'actual expected builder outcome missing')
        refs = {}
        for label, path in [('evidence_adapter', Path(__file__).resolve().parents[1]/'evidence/service.py'),
                            ('failure_adapter', Path(__file__)), ('challenge_adapter', Path(__file__).resolve().parents[1]/'challenges/service.py'),
                            ('probe_adapter', Path(__file__).resolve().parents[1]/'evidence/probe_child.py')]:
            refs[label] = e.put(e.make('implementation', label.replace('_', '-'), {
                'implementation_kind': 'controlled-W05-'+label.replace('_', '-'), 'realizes_capability_refs': [CAPABILITY+'@foundation.1'],
                'conforms_to_schema_refs': ['protocol:W05-selected-current-carriers'],
                'execution_entrypoint_ref': path.relative_to(ROOT).as_posix()+'#sha256='+e.sources[path],
                'environment_contract_ref': 'protocol:W05-current-Python-and-current-schema-closure'}))
        for label, path in [('historical', OLD_BUILDER), ('successor', NEW_BUILDER)]:
            refs[label] = e.put(e.make('implementation', label+'-builder', {
                'implementation_kind': 'controlled-source-preparation', 'realizes_capability_refs': [CAPABILITY+'@foundation.1'],
                'conforms_to_schema_refs': ['protocol:W05-selected-current-carriers'],
                'execution_entrypoint_ref': path.relative_to(ROOT).as_posix()+'#prepare:sha256='+e.sources[path],
                'environment_contract_ref': 'protocol:W05-current-Python-and-current-schema-closure'}))
        e.subject_ref = refs['historical']
        refs['action'] = e.put(e.make('agent-action', 'controlled-probe', {
            'action_kind': 'controlled-source-preparation-probe', 'agent_instance_ref': e.host.ref('agent-instance'),
            'session_ref': e.host.ref('agent-session'), 'assignment_ref': e.host.ref('agent-assignment'),
            'authority_evidence_refs': [e.host.grant.evidence_ref], 'tool_refs': [e.host.ref('tool')],
            'implementation_refs': [refs['evidence_adapter'], refs['probe_adapter'], refs['historical'], refs['successor']], 'input_refs': ['protocol:W05-input:'+byte_sha(e.input)],
            'output_refs': [manifest_ref], 'receipt_refs': [manifest_ref], 'posture': 'completed', 'residue_refs': ['protocol:W05-owner-review-pending']}))
        e.action_ref = refs['action']
        refs['observation'] = e.put(e.make('operational-observation', 'builder-preparation', {
            'action_ref': refs['action'], 'datum': 'Original controlled process manifest '+manifest_ref,
            'evidence_refs': [manifest_ref], 'interpretation_posture': 'uninterpreted-original-process-results',
            'method_ref': 'protocol:W05-exact-schema-manifest-method@1', 'observed_at': m['observations'][0]['observed_at'], 'project_ref': e.host.scope}))
        refs['evidence'] = e.put(e.make('evidence-set', 'controlled-preparation', {
            'coverage_statement': 'Actual retained historical builder rejection and independently verified corrected builder.',
            'item_refs': [refs['observation']], 'source_refs': [manifest_ref],
            'limitations': ['Controlled historical-source replay against current dependencies; not the original runtime environment.',
                'No production Incident or confirmed cause.', 'No mutation or admission of challenged source.']}))
        refs['mode'] = e.put(e.make('failure-mode', 'invalid-candidate-builder-output', {
            'subject_kind_ref': 'implementation', 'expected_boundary_ref': 'protocol:W05-valid-candidate-preparation',
            'manifestation': 'Intended valid candidate preparation aborts on unsupported Hypothesis inline counterpart.',
            'exclusions': ['Expected hostile validator test', 'A negative research hypothesis'],
            'detection_method_refs': ['protocol:W05-exact-schema-manifest-method@1'], 'signal_refs': [refs['observation']],
            'control_binding_refs': ['failure-control-binding:lab-W05:schema-detection@'+VERSION], 'recovery_expectation': 'Validate a separate successor; preserve old source and review residue.'}))
        refs['occurrence'] = e.put(e.make('failure-occurrence', 'retained-builder-rejection', {
            'subject_ref': refs['historical'], 'expected_boundary_ref': 'protocol:W05-valid-candidate-preparation',
            'observed_manifestations': [bad['exception_message']], 'detection_evidence_refs': [refs['observation']],
            'occurrence_posture': 'supported-controlled', 'cause_posture': 'unresolved', 'impact_refs': [refs['historical']],
            'response_action_refs': [refs['action']], 'recovery_posture': 'successor-verified-old-revision-unresolved',
            'residue_refs': ['protocol:W05-old-revision-review-pending']}))
        predicted_value = 'classification-value:lab-W05:invalid-inline-counterpart@'+VERSION
        refs['scheme'] = e.put(e.make('classification-scheme', 'failure-manifestation', {
            'scheme_name': 'Controlled preparation failure manifestation', 'axis_refs': ['axis:failure-manifestation'],
            'value_refs': [predicted_value], 'cardinality_rules': ['one-active-value-per-subject-axis'],
            'compatibility_rules': ['annotation-never-grants-authority'], 'mapping_refs': []}))
        refs['value'] = e.put(e.make('classification-value', 'invalid-inline-counterpart', {
            'axis_ref': 'axis:failure-manifestation', 'scheme_ref': refs['scheme'], 'value_code': 'invalid-inline-counterpart',
            'definition_ref': refs['mode'], 'parent_value_refs': [], 'compatibility_refs': ['protocol:W05-annotation-no-authority']}))
        refs['assignment'] = self.classify('observed-mode', refs['occurrence'], refs['scheme'], refs['value'], refs['action'], refs['observation'], refs['evidence'], refs['failure_adapter'])
        refs['cause'] = e.put(e.make('hypothesis', 'cause-proposal', {
            'proposition': 'Builder preparation attempted a Hypothesis inline counterpart outside the selected carrier contract.',
            'falsification_conditions': ['Independent code/schema review contradicts this causal explanation'],
            'observation_targets': [refs['observation']], 'disposition': 'open'}))
        refs['assessment'] = self.assess('independent-failure-axes', refs['occurrence'], refs['assignment'], [refs['cause']])
        refs['control'] = e.put(e.make('failure-control-binding', 'schema-detection', {
            'failure_mode_ref': refs['mode'], 'control_subject_ref': 'protocol:W05-selected-current-schema-validator',
            'primary_control_role': 'detect', 'owner_ref': e.host.ref('principal'), 'installation_posture': 'candidate-current-replay-only',
            'execution_evidence_refs': [refs['observation']], 'effectiveness_evidence_refs': []}))
        refs['incident'], controlled = self.incident('owned-preparation', refs['occurrence'], refs['assessment'], 'protocol:W05-controlled-threshold@1')
        _, production = self.incident('production', refs['occurrence'], refs['assessment'], 'protocol:W05-production-threshold@1')
        e.blob('incident-dispositions.json', encoded({'controlled': controlled, 'production': production}))
        signatures = [
            ('historical-capability', 'realizes', 'historical', 'capability', {'realization_role': 'declared-candidate-preparation-intent', 'exact_target_version_ref': e.capability_ref}),
            ('successor-capability', 'realizes', 'successor', 'capability', {'realization_role': 'declared-candidate-preparation-intent', 'exact_target_version_ref': e.capability_ref}),
            ('action-observation', 'produces', 'action', 'observation', {'action_receipt_ref': manifest_ref, 'production_role': 'original-controlled-observation', 'output_posture': 'candidate-unadmitted'}),
            ('evidence-cause', 'evidence-bears-on', 'evidence', 'cause', {'polarity': 'cause-proposed-unconfirmed'}),
            ('observation-occurrence', 'evidence-bears-on', 'observation', 'occurrence', {'polarity': 'supports-controlled-manifestation'}),
            ('occurrence-subject', 'affects', 'occurrence', 'historical', {'impact_scope': 'owned-preparation-only', 'evidence_posture': 'observed-controlled'}),
            ('occurrence-action', 'occurs-during', 'occurrence', 'action', {'envelope_version_ref': refs['action'], 'temporal_scope': 'controlled-probe'}),
            ('value-scheme', 'member-of', 'value', 'scheme', {'membership_role': 'declared-axis-value'}),
            ('assignment-scheme', 'governed-by', 'assignment', 'scheme', {'governance_role': 'annotation-rule-only'}),
            ('assignment-evidence', 'derives-from', 'assignment', 'evidence', {'derivation_role': 'actual-controlled-manifestation'}),
            ('occurrence-mode', 'instance-of', 'occurrence', 'mode', {'parent_version_ref': refs['mode'], 'binding_ref': refs['assignment']}),
            ('assessment-occurrence', 'evaluates', 'assessment', 'occurrence', {'evaluation_role': 'independent-failure-axes', 'evaluation_purpose': 'bounded-controlled-assessment'}),
            ('control-mode', 'controls', 'control', 'mode', {'control_role': 'detect', 'control_version_ref': refs['control'], 'installation_posture': 'candidate-current-replay-only'}),
            ('occurrence-incident', 'member-of', 'occurrence', 'incident', {'membership_role': 'controlled-threshold-qualified-occurrence'})]
        refs['capability'] = e.capability_ref
        for label in ['evidence_adapter', 'failure_adapter', 'challenge_adapter', 'probe_adapter']:
            signatures.append((label+'-capability', 'realizes', label, 'capability',
                {'realization_role': 'declared-controlled-candidate-mechanism', 'exact_target_version_ref': e.capability_ref}))
        relations = [e.edge(n, 'relation.'+k, refs[a], refs[b], q) for n, k, a, b, q in signatures]
        return refs, relations
