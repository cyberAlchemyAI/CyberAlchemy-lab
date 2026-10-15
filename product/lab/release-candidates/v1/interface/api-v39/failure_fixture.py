"""Owned public failure fixtures with separate nodes, relations and evidence."""
import copy
from contextlib import contextmanager
import json
from pathlib import Path
import tempfile
import uuid

from . import protocol as P, fixtures as F, artifact_model as M, handlers as H, auth as A, workspace as W
from . import classification_fixture as CF
from .service import Service
from .failure_preparation import selected as composition

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]


def revision(body):
    return body['node_id'] + '@failure.candidate.1'


def target(view, body, materials, metadata):
    kind = body['kind']; identity = body['node_id']; version = revision(body)
    carrier = 'cal.artifact-type.' + kind + ('/v3' if kind == 'typed-relation' else '/v1')
    contract = view.data['projection']['contracts'][carrier]
    raw = (json.dumps(body, indent=3, ensure_ascii=False) + '\n').encode()
    prefix = 'candidate:' + identity
    category = 'typed-relation' if kind == 'typed-relation' else 'artifact-instance'
    runtime = {'category': category, 'operation': 'admit', 'version_ref': version,
               'carrier_ref': carrier, 'record': body, 'predecessor_ref': None,
               'decision_ref': 'decision:' + identity, 'contract': None,
               'content': view.handle.custody.content_entry(raw)}
    core = {'decision_ref': runtime['decision_ref'], 'category': category,
            'operation': 'admit', 'version_ref': version,
            'target_digest': view.handle.common.digest(runtime)}
    meta = {'schema_version': 'lab-candidate-target-metadata/v1-candidate',
            'category': category, 'decision_ref': runtime['decision_ref'], 'contract': None}
    materials[prefix + ':content'] = raw
    materials[prefix + ':core'] = view.handle.common.encoded(core)
    materials[prefix + ':metadata'] = P.source.encoded(meta)
    metadata[version] = P.binding(prefix + ':metadata', materials[prefix + ':metadata'])
    header = {'scope_ref': body['scope_ref'], 'identity_ref': identity, 'version_ref': version,
              'carrier_ref': carrier, 'byte_sha256': P.source.sha(raw),
              'candidate_contract_binding': {'ref': contract['schema_path'], 'sha256': contract['schema_sha256']}}
    return {'operation': 'admit', 'artifact': header, 'predecessor': None,
            'content': {'content_ref': prefix + ':content', 'byte_sha256': P.source.sha(raw),
                        'size_bytes': len(raw), 'media_type': 'application/json'},
            'candidate_binding': metadata[version],
            'requested_effect': 'Prepare a bounded failure assessment candidate for later owner review',
            'decision_core_binding': P.binding(prefix + ':core', materials[prefix + ':core'])}


def records(view, mode):
    return failure_bodies(view.data['config']['scope_ref'], CF.records(view)[0], mode)


def failure_bodies(scope, subject, mode):
    kinds = ['failure-occurrence', 'failure-mode', 'classification-scheme',
             'classification-value', 'classification-assignment', 'hypothesis',
             'failure-assessment', 'evidence-set']
    bodies = {}
    for kind in kinds:
        body = P.frame_parse((ROOT / 'authority/artifact-types' / kind / 'v1/fixtures/valid/record.json').read_bytes())
        body.update(node_id=kind + ':R03-public-failure', scope_ref=scope,
                    lifecycle_state='candidate', relation_refs=[], evidence_refs=[],
                    successor_refs=[], authority_effect='none')
        body['claim_ceiling'] = 'Synthetic failure workflow fixture; no real manifestation, confirmed cause, effective control, recovery or admission.'
        bodies[kind] = body
    occurrence, failure_mode, scheme, value, assignment, cause, assessment, evidence = [bodies[k] for k in kinds]
    basis_ref = 'evidence:R03-synthetic-failure-basis'
    occurrence['payload'].update(subject_ref=subject['version_ref'],
        expected_boundary_ref='contract:R03-failure-candidate-consistency',
        observed_manifestations=['Explicitly synthetic candidate preparation refusal'],
        detection_evidence_refs=[basis_ref], cause_posture='unresolved',
        recovery_posture='not-attempted', impact_refs=[], response_action_refs=[], residue_refs=[])
    failure_mode['payload'].update(subject_kind_ref=subject['carrier_ref'],
        expected_boundary_ref=occurrence['payload']['expected_boundary_ref'])
    axis = 'axis:R03-failure-manifestation'
    scheme['payload'].update(axis_refs=[axis], value_refs=[revision(value)],
        cardinality_rules=['one-active-value-per-subject-axis'],
        compatibility_rules=['annotation-never-grants-authority'], mapping_refs=[])
    value['payload'].update(scheme_ref=revision(scheme), axis_ref=axis,
        definition_ref=revision(failure_mode), parent_value_refs=[], compatibility_refs=[],
        value_code='synthetic-preparation-refusal')
    assignment['payload'].update(subject_ref=occurrence['node_id'], subject_version_ref=revision(occurrence),
        scheme_version_ref=revision(scheme), value_ref=revision(value), axis_ref=axis,
        status='candidate-annotation', evidence_refs=[basis_ref],
        action_ref='protocol:R03-failure-candidate-action', method_ref='protocol:R03-failure-candidate-method',
        implementation_ref='protocol:R03-failure-candidate-implementation',
        basis='explicit-synthetic-fixture', effective_period='protocol:R03-fixture-only')
    cause['payload']['disposition'] = 'open'
    assessment['payload'].update(occurrence_ref=revision(occurrence), mode_assignment_ref=revision(assignment),
        cause_hypothesis_refs=[revision(cause)], occurrence_posture='synthetic-controlled',
        mode_posture='candidate-annotation', impact_posture='not-assessed',
        containment_posture='not-assessed', recovery_posture='not-attempted',
        uncertainty_refs=['uncertainty:R03-no-real-failure-observation'])
    assessment['evidence_refs'] = [basis_ref]
    evidence['payload'].update(source_refs=[basis_ref], item_refs=[basis_ref],
        coverage_statement='Exact synthetic fixture bytes only',
        limitations=['No operational occurrence, causal confirmation or recovery effectiveness observed'])
    evidence['evidence_refs'] = [basis_ref]
    if mode == 'unknown-rule': scheme['payload']['compatibility_rules'].append('unselected-failure-rule')
    if mode == 'invalid-schema': assessment['payload']['undeclared'] = True
    if mode == 'independent-recovery': assessment['payload']['recovery_posture'] = 'authored-recovered-with-residue'
    nodes = [bodies[k] for k in kinds]
    edges = [(value, scheme, 'relation.member-of', {'membership_role': 'Declared failure Value membership'}),
             (assignment, scheme, 'relation.governed-by', {'governance_role': 'Annotation consistency only'}),
             (occurrence, failure_mode, 'relation.instance-of', {'parent_version_ref': revision(failure_mode), 'binding_ref': revision(assignment)}),
             (assessment, occurrence, 'relation.evaluates', {'evaluation_role': 'Candidate assessment', 'evaluation_purpose': 'Independent evidenced axes'}),
             (evidence, cause, 'relation.evidence-bears-on', {'polarity': 'Explicit synthetic basis; does not confirm cause'})]
    if mode == 'conflict':
        extra = copy.deepcopy(assignment); extra['node_id'] += ':conflict'; extra['relation_refs'] = []
        nodes.append(extra)
        edges.append((extra, scheme, 'relation.governed-by', {'governance_role': 'Independent conflicting annotation'}))
    for left, right, kind, _ in edges:
        left['relation_refs'].append({'relation_kind_ref': kind, 'direction': 'source',
            'counterpart_kind': right['kind'], 'counterpart_ref': revision(right)})
        right['relation_refs'].append({'relation_kind_ref': kind, 'direction': 'target',
            'counterpart_kind': left['kind'], 'counterpart_ref': revision(left)})
    return nodes, edges, basis_ref


@contextmanager
def example(view, schemas, *, mode='single', grant=True):
    modes = ('single', 'threshold-met', 'threshold-missed', 'threshold-unknown',
             'unknown-rule', 'invalid-schema', 'bad-core', 'independent-recovery', 'conflict')
    P.source.require(mode in modes, 'undeclared failure fixture mode')
    nodes, edges, basis_ref = records(view, mode)
    materials = {basis_ref: b'Explicit synthetic candidate fixture evidence; no real operation occurred.\n'}
    evidence_binding = P.binding(basis_ref, materials[basis_ref]); metadata = {}
    targets = [target(view, body, materials, metadata) for body in nodes]
    by_identity = {entry['artifact']['identity_ref']: entry for entry in targets}
    connections = []
    template = P.frame_parse((ROOT / 'authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/typed-relation/v3/fixtures/valid/record.json').read_bytes())
    for index, (left, right, kind, qualifiers) in enumerate(edges):
        body = copy.deepcopy(template)
        body.update(node_id='typed-relation:R03-public-failure:' + str(index), scope_ref=view.data['config']['scope_ref'],
                    relation_refs=[], evidence_refs=[basis_ref], successor_refs=[], authority_effect='none')
        body['payload'].update(relation_kind_ref=kind,
            source={'kind': left['kind'], 'ref': left['node_id'], 'version_ref': revision(left)},
            target={'kind': right['kind'], 'ref': right['node_id'], 'version_ref': revision(right)},
            qualifiers=qualifiers, relation_evidence_refs=[basis_ref])
        targets.append(target(view, body, materials, metadata))
        signature, binding = M.signature(view, kind)
        connections.append({'relation_kind_ref': kind, 'signature_sha256': binding['sha256'],
            'axis_ref': signature['payload']['axis_id'],
            'source': {'artifact': composition.public_artifact_ref(by_identity[left['node_id']]['artifact']), 'semantic_kind': left['kind']},
            'target': {'artifact': composition.public_artifact_ref(by_identity[right['node_id']]['artifact']), 'semantic_kind': right['kind']},
            'qualifiers': qualifiers})
    headers = [composition.public_artifact_ref(entry['artifact']) for entry in targets]
    assessment_binding = P.binding(targets[6]['content']['content_ref'], materials[targets[6]['content']['content_ref']])
    basis = {'schema_version': 'lab-failure-assessment-basis/v1-candidate',
             'scope_ref': view.data['config']['scope_ref'], 'source_cut': H.cut(view),
             'assessment_binding': assessment_binding,
             'axis_basis': {axis: [evidence_binding] for axis in ('occurrence', 'mode', 'cause', 'impact', 'containment', 'recovery', 'uncertainty')},
             'authority_effect': 'none', 'actual_owner_outcome': None}
    materials['candidate:failure-axis-basis'] = P.source.encoded(basis)
    axis_basis_binding = P.binding('candidate:failure-axis-basis', materials['candidate:failure-axis-basis'])
    threshold_binding = None
    if mode.startswith('threshold-'):
        threshold = {'schema_version': 'lab-failure-incident-threshold/v1-candidate',
            'scope_ref': basis['scope_ref'], 'source_cut': H.cut(view),
            'rule': 'unselected-threshold-rule' if mode == 'threshold-unknown' else 'minimum-evidenced-occurrences',
            'occurrences': [headers[0]], 'minimum_count': 2 if mode == 'threshold-missed' else 1,
            'authority_effect': 'none', 'actual_owner_outcome': None}
        materials['candidate:failure-threshold'] = P.source.encoded(threshold)
        threshold_binding = P.binding('candidate:failure-threshold', materials['candidate:failure-threshold'])
    if mode == 'bad-core':
        binding = targets[6]['decision_core_binding']; core = P.frame_parse(materials[binding['ref']])
        core['target_digest'] = '0' * 64; materials[binding['ref']] = view.handle.common.encoded(core)
        binding['sha256'] = P.source.sha(materials[binding['ref']])
    principal = 'principal:R03-failure-operator:' + uuid.uuid4().hex
    actor = {'principal_ref': principal, 'agent_instance_ref': None, 'assignment_ref': None, 'session_ref': None, 'role_assignment_refs': []}
    with tempfile.TemporaryDirectory(prefix='cal-R03-public-failure-') as temporary:
        root = Path(temporary); root.chmod(0o700)
        proposal = {'schema_version': 'lab-change-proposal/v1-candidate', 'proposal_ref': 'proposal:R03-failure-candidate',
            'actor': actor, 'scope_ref': basis['scope_ref'], 'base_cut': H.cut(view),
            'source_profile_binding': {'ref': view.handle.manifest['profile_binding']['path'], 'sha256': view.handle.manifest['profile_binding']['sha256']},
            'workspace_binding': None, 'targets': targets, 'schema_bindings': [], 'connection_proposals': connections,
            'evidence_bindings': [evidence_binding], 'idempotency_key': 'fixture:failure',
            'challenge_route': view.data['config']['challenge_route'], 'authority_effect': 'none'}
        key, path, _ = F.provision(root, 'reference-corrected', materials, metadata, principal=principal)
        policy = P.frame_parse(path.read_bytes())
        authority = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
        policy.update(schema_version='lab-local-failure-candidate-policy/v1-candidate' if grant else 'lab-local-metadata-candidate-policy/v1-candidate',
            source_name='custody-participation', session_control=None, scope_control=None,
            allowed_operations=list(P.FAILURE_SUPPORTED if grant else P.METADATA_SUPPORTED),
            purpose='durable-metadata-and-exact-failure-preparation' if grant else 'durable-metadata-and-exact-candidate-preparation',
            development_authorization_binding=P.binding(str(authority.relative_to(ROOT)), authority.read_bytes()), max_request_bytes=1048576)
        workspace = json.loads((root / 'workspace/workspace.json').read_bytes())
        proposal['workspace_binding'] = {'ref': 'workspace:' + workspace['workspace_ref'], 'sha256': policy['workspace']['manifest_sha256']}
        def staged(raw):
            digest = P.source.sha(raw); W.atomic(root / 'workspace/objects' / (digest + '.json'), raw)
            return {'ref': 'workspace-object:' + workspace['workspace_ref'] + ':' + digest, 'sha256': digest}
        proposal_binding = staged(P.source.encoded(proposal))
        routing = {'schema_version': 'lab-failure-preparation-routing/v1-candidate',
            'scope_ref': basis['scope_ref'], 'source_cut': H.cut(view), 'proposal_binding': proposal_binding,
            'rule_source_binding': P.binding(str((composition.RULES / 'source-manifest.json').relative_to(ROOT)), (composition.RULES / 'source-manifest.json').read_bytes()),
            'rule_proof_binding': P.binding(str((composition.RULES / 'receipts/proof-0001.json').relative_to(ROOT)), (composition.RULES / 'receipts/proof-0001.json').read_bytes()),
            'axis_basis_binding': axis_basis_binding, 'incident_threshold_binding': threshold_binding,
            'record_basis': 'current-plus-exact-prospective-postimage', 'authority_effect': 'none', 'actual_owner_outcome': None}
        routing_binding = staged(P.source.encoded(routing))
        if grant: policy['failure_control'] = {'routing_binding': routing_binding}
        path.write_bytes(P.compact(policy))
        channel = A.ReaderChannel(path, P.source.sha(path.read_bytes()), schemas)
        proof = F.proof(key, channel.challenge); authenticated = channel.authenticate(proof)
        service = Service(view, channel, schemas)
        try:
            request = F.call(channel.context, 'lab.status', H.cut(view))
            request.update(operation='failure.assess', idempotency_key='fixture:failure',
                message={'schema_version': 'lab-failure-assessment-request/v1-candidate',
                    'request_ref': 'request:R03-failure:' + uuid.uuid4().hex, 'actor': actor, 'source_cut': H.cut(view),
                    'occurrence': headers[0], 'mode_assignment': headers[4], 'cause_hypothesis_refs': [headers[5]],
                    'evidence_bindings': [evidence_binding], 'assessment_candidate_binding': assessment_binding,
                    'incident_threshold_binding': threshold_binding, 'authority_effect': 'none'})
            yield service, request, {'root': root, 'policy_path': path, 'proposal': proposal,
                'routing': routing, 'routing_binding': routing_binding, 'signed_proof': P.frame_parse(proof),
                'authentication': authenticated, 'mode': mode}
        finally:
            service.close(); key = None
    P.source.require(not root.exists(), 'owned failure workspace, policy or signer remained')
