"""Actual selected source, owned Operator grant and exact prospective materials."""
import copy
from contextlib import contextmanager
import json
from pathlib import Path
import tempfile
import uuid

from . import protocol as P, fixtures as F, artifact_model as M, handlers as H, auth as A, workspace as W
from .service import Service

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]


def target(view, body, materials, metadata, *, suffix='1'):
    kind = body['kind']
    identity = body['node_id']
    version = identity + '@classification.candidate.' + suffix
    carrier = 'cal.artifact-type.' + kind + '/v1'
    contract = view.data['projection']['contracts'][carrier]
    raw = (json.dumps(body, indent=3, ensure_ascii=False) + '\n').encode()
    prefix = 'candidate:' + identity
    runtime = {'category': 'artifact-instance', 'operation': 'admit', 'version_ref': version,
               'carrier_ref': carrier, 'record': body, 'predecessor_ref': None,
               'decision_ref': 'decision:' + identity, 'contract': None}
    if view.selected['name'] == 'custody-participation':
        runtime['content'] = view.handle.custody.content_entry(raw)
    core = {'decision_ref': runtime['decision_ref'], 'category': runtime['category'],
            'operation': runtime['operation'], 'version_ref': version,
            'target_digest': view.handle.common.digest(runtime)}
    meta = {'schema_version': 'lab-candidate-target-metadata/v1-candidate',
            'category': runtime['category'], 'decision_ref': runtime['decision_ref'], 'contract': None}
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
            'requested_effect': 'Prepare exact classification candidate for later owner review; no admission',
            'decision_core_binding': P.binding(prefix + ':core', materials[prefix + ':core'])}


def records(view, *, mode='single'):
    scope = view.data['config']['scope_ref']
    subjects = [row for row in view.subjects.values()
                if row['identity'] == 'product:cyberalchemy-lab'
                and row['effective_state'] in ('admitted-current', 'local-admitted-current')]
    P.source.require(len(subjects) == 1, 'exact current Product fixture subject required')
    subject = M.artifact_ref(view, subjects[0])
    definition = next(row for row in view.subjects.values()
                      if row['kind'] == 'definition' and row['effective_state'] in ('admitted-current', 'local-admitted-current'))
    bodies = {}
    for kind in ['classification-scheme', 'classification-value', 'classification-assignment']:
        body = P.frame_parse((ROOT / 'authority/artifact-types' / kind / 'v1/fixtures/valid/record.json').read_bytes())
        body.update(node_id=kind + ':R03-public-preparation', scope_ref=scope,
                    relation_refs=[], evidence_refs=[], successor_refs=[], authority_effect='none')
        body['claim_ceiling'] = 'Isolated prospective annotation consistency fixture; no admission, owner outcome, runtime conformance or causality.'
        bodies[kind] = body
    scheme, value, assignment = [bodies[kind] for kind in ['classification-scheme', 'classification-value', 'classification-assignment']]
    scheme_ref = scheme['node_id'] + '@classification.candidate.1'
    value_ref = value['node_id'] + '@classification.candidate.1'
    axis = 'axis:product-evidence-posture'
    scheme['payload'].update(axis_refs=[axis], value_refs=[value_ref],
                             cardinality_rules=['one-active-value-per-subject-axis'],
                             compatibility_rules=['annotation-never-grants-authority'], mapping_refs=[])
    value['payload'].update(scheme_ref=scheme_ref, axis_ref=axis, value_code='candidate-only',
                            definition_ref=definition['version_ref'], parent_value_refs=[], compatibility_refs=[])
    assignment['payload'].update(subject_ref=subject['identity_ref'], subject_version_ref=subject['version_ref'],
                                 scheme_version_ref=scheme_ref, axis_ref=axis, value_ref=value_ref,
                                 basis='isolated-candidate-fixture', action_ref='protocol:R03-candidate-classification-action',
                                 method_ref='protocol:R03-candidate-classification-method',
                                 implementation_ref='protocol:R03-candidate-classification-implementation',
                                 evidence_refs=['candidate:classification-basis'], effective_period='protocol:R03-candidate-only',
                                 status='candidate-annotation')
    extra = []
    if mode in ('conflict', 'missing-reference'):
        other = copy.deepcopy(assignment)
        other['node_id'] += ':other'
        if mode == 'missing-reference':
            other['payload']['subject_version_ref'] = 'product:missing@1'
        extra.append(other)
    elif mode == 'independent-axis':
        other_value = copy.deepcopy(value)
        other_value['node_id'] += ':other-axis'
        other_value['payload']['axis_ref'] = 'axis:independent-product-dimension'
        other_ref = other_value['node_id'] + '@classification.candidate.1'
        scheme['payload']['axis_refs'].append(other_value['payload']['axis_ref'])
        scheme['payload']['value_refs'].append(other_ref)
        other = copy.deepcopy(assignment)
        other['node_id'] += ':other-axis'
        other['payload'].update(axis_ref=other_value['payload']['axis_ref'], value_ref=other_ref)
        extra.extend([other_value, other])
    elif mode == 'unknown-rule':
        scheme['payload']['compatibility_rules'].append('unselected-classification-rule')
    elif mode == 'invalid-schema':
        assignment['payload']['undeclared'] = True
    elif mode != 'single' and mode != 'bad-core':
        raise ValueError('undeclared classification fixture mode')
    return subject, [scheme, value, assignment] + extra, axis


@contextmanager
def example(view, schemas, *, mode='single', grant=True):
    materials = {'candidate:classification-basis': b'{"candidate_fixture":true,"authority_effect":"none"}\n'}
    metadata = {}
    subject, bodies, axis = records(view, mode=mode)
    targets = [target(view, body, materials, metadata) for body in bodies]
    if mode == 'bad-core':
        selected = targets[2]['decision_core_binding']
        core = P.frame_parse(materials[selected['ref']])
        core['target_digest'] = '0' * 64
        materials[selected['ref']] = view.handle.common.encoded(core)
        selected['sha256'] = P.source.sha(materials[selected['ref']])
    principal = 'principal:R03-classification-operator:' + uuid.uuid4().hex
    actor = {'principal_ref': principal, 'agent_instance_ref': None, 'assignment_ref': None,
             'session_ref': None, 'role_assignment_refs': []}
    with tempfile.TemporaryDirectory(prefix='cal-R03-public-classification-') as temporary:
        root = Path(temporary)
        root.chmod(0o700)
        proposal = {'schema_version': 'lab-change-proposal/v1-candidate',
                    'proposal_ref': 'proposal:R03-classification-candidate', 'actor': actor,
                    'scope_ref': view.data['config']['scope_ref'], 'base_cut': H.cut(view),
                    'source_profile_binding': {'ref': view.handle.manifest['profile_binding']['path'],
                                               'sha256': view.handle.manifest['profile_binding']['sha256']},
                    'workspace_binding': None, 'targets': targets, 'schema_bindings': [],
                    'connection_proposals': [], 'evidence_bindings': [],
                    'idempotency_key': 'fixture:classification',
                    'challenge_route': view.data['config']['challenge_route'], 'authority_effect': 'none'}
        # Workspace self-binding cannot include an input that contains its own
        # hash. The proposal selects a separate original provisioned workspace,
        # and is then staged as a content-addressed object in that same vault.
        key, path, _ = F.provision(root, 'reference-corrected', materials, metadata, principal=principal)
        policy = P.frame_parse(path.read_bytes())
        authority = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
        policy.update(schema_version='lab-local-classification-candidate-policy/v1-candidate' if grant else 'lab-local-metadata-candidate-policy/v1-candidate',
                      source_name='custody-participation', session_control=None, scope_control=None,
                      allowed_operations=list(P.CLASSIFICATION_SUPPORTED if grant else P.METADATA_SUPPORTED),
                      purpose='durable-metadata-and-exact-classification-preparation' if grant else 'durable-metadata-and-exact-candidate-preparation',
                      development_authorization_binding=P.binding(str(authority.relative_to(ROOT)), authority.read_bytes()),
                      max_request_bytes=1048576)
        workspace=json.loads((root/'workspace/workspace.json').read_bytes())
        proposal['workspace_binding']={'ref':'workspace:'+workspace['workspace_ref'],
                                       'sha256':policy['workspace']['manifest_sha256']}
        def staged_object(raw):
            digest=P.source.sha(raw)
            W.atomic(root/'workspace/objects'/(digest+'.json'),raw)
            return {'ref':'workspace-object:'+workspace['workspace_ref']+':'+digest,'sha256':digest}
        proposal_binding=staged_object(P.source.encoded(proposal))
        from .classification_preparation import selected as composition
        routing={'schema_version':'lab-classification-preparation-routing/v1-candidate',
                 'scope_ref':proposal['scope_ref'],'source_cut':proposal['base_cut'],
                 'proposal_binding':proposal_binding,
                 'rule_source_binding':P.binding(str((composition.RULES/'source-manifest.json').relative_to(ROOT)),(composition.RULES/'source-manifest.json').read_bytes()),
                 'rule_proof_binding':P.binding(str((composition.RULES/'receipts/proof-0001.json').relative_to(ROOT)),(composition.RULES/'receipts/proof-0001.json').read_bytes()),
                 'record_basis':'current-plus-exact-prospective-postimage','authority_effect':'none','actual_owner_outcome':None}
        routing_binding=staged_object(P.source.encoded(routing))
        if grant:policy['classification_control']={'routing_binding':routing_binding}
        path.write_bytes(P.compact(policy))
        channel=A.ReaderChannel(path,P.source.sha(path.read_bytes()),schemas)
        proof=F.proof(key,channel.challenge)
        authenticated=channel.authenticate(proof)
        service=Service(view,channel,schemas)
        try:
            request = F.call(channel.context, 'lab.status', H.cut(view))
            request.update(operation='classification.prepare', idempotency_key='fixture:classification',
                           message={'schema_version': 'lab-classification-request/v1-candidate',
                                    'request_ref': 'request:R03-public-classification:' + uuid.uuid4().hex,
                                    'actor': actor, 'source_cut': H.cut(view),
                                    'subject': subject, 'scheme': targets[0]['artifact'], 'value': targets[1]['artifact'],
                                    'axis_ref': axis, 'basis_bindings': [P.binding('candidate:classification-basis', materials['candidate:classification-basis'])],
                                    'assignment_candidate_binding': P.binding(targets[2]['content']['content_ref'], materials[targets[2]['content']['content_ref']]),
                                    'authority_effect': 'none'})
            yield service, request, {'root': root, 'policy_path': path, 'proposal': proposal,
                                     'proposal_binding': proposal_binding, 'routing': routing,
                                     'routing_binding': routing_binding, 'signed_proof': P.frame_parse(proof),
                                     'authentication': authenticated, 'mode': mode}
        finally:
            service.close()
            key = None
    P.source.require(not root.exists(), 'owned classification policy, signer or workspace remained')
