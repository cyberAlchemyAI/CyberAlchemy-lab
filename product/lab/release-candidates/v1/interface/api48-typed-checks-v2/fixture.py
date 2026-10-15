"""Owned operator execution fixture; synthetic model change and pending review.

Actual authenticated transport, policy bytes, source replay and original journal
are exercised. No genuine semantic verdict or operational scope grant is made.
"""
import copy
from contextlib import contextmanager
import importlib
import json
from pathlib import Path
import tempfile
import uuid


@contextmanager
def example(API, view, schemas, *, mode='exact', grant=True):
    P, F, M, H, Auth, W, ServiceModule = [importlib.import_module(API + '.' + suffix) for suffix in
        ('protocol', 'fixtures', 'artifact_model', 'handlers', 'auth', 'workspace', 'service')]
    composition = importlib.import_module(API + '.typed_preparation').selected
    A, S, R, T = composition.helpers()
    Fixtures = importlib.import_module(A.__package__ + '.test_postimage')
    Fixtures.PostimageTests.setUpClass()
    fixture = Fixtures.PostimageTests()
    fixture.setUp()
    C = view.handle.common
    proposal = copy.deepcopy(fixture.proposal)
    inspection = copy.deepcopy(fixture.inspection)
    # The postimage prototype and C14 inspector used distinct fixture names.
    # Join them before any exact proposal/review/scope bytes are published.
    proposal['proposal_ref'] = inspection['proposal_ref']
    relation_target = next(t for t in proposal['targets']
                           if t['artifact']['carrier_ref'] == 'cal.artifact-type.relation-kind/v2')
    inspection['successor_version_ref'] = relation_target['artifact']['version_ref']
    materials = dict(fixture.materials)
    principal = 'principal:R03-typed-operator:' + uuid.uuid4().hex
    actor = {'principal_ref': principal, 'agent_instance_ref': None, 'session_ref': None,
             'assignment_ref': None, 'role_assignment_refs': []}
    scope, cut = view.data['config']['scope_ref'], H.cut(view)
    proposal.update(schema_version='lab-change-proposal/v1-candidate', actor=actor, scope_ref=scope, base_cut=cut,
        source_profile_binding={'ref': view.handle.manifest['profile_binding']['path'],
                                'sha256': view.handle.manifest['profile_binding']['sha256']},
        challenge_route=view.data['config']['challenge_route'], idempotency_key='fixture:typed-exact',
        connection_proposals=[], evidence_bindings=[], authority_effect='none')
    metadata = {}
    for target in proposal['targets']:
        target['artifact']['scope_ref'] = scope
        target['requested_effect'] = 'Synthetic coupled typed preparation fixture; no admission'
        if target['predecessor'] is not None:
            target['predecessor'] = M.artifact_ref(view, view.data['projection']['subjects'][target['predecessor']['version_ref']])
        metadata[target['artifact']['version_ref']] = target['candidate_binding']
    if mode == 'bad-core':
        selected = proposal['targets'][0]['decision_core_binding']
        core = P.frame_parse(materials[selected['ref']])
        core['target_digest'] = '0' * 64
        materials[selected['ref']] = C.encoded(core)
        selected['sha256'] = P.source.sha(materials[selected['ref']])
    assert mode in ('exact', 'bad-core', 'bad-review', 'duplicate-path')
    with tempfile.TemporaryDirectory(prefix='cal-R03-public-typed-') as temporary:
        root = Path(temporary)
        root.chmod(0o700)
        signer, policy_path, _ = F.provision(root, 'reference-corrected', materials, metadata, principal=principal)
        service = None
        try:
            policy = P.frame_parse(policy_path.read_bytes())
            authority = P.ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
            policy.update(schema_version='lab-local-typed-extension-candidate-policy/v1-candidate' if grant else 'lab-local-metadata-candidate-policy/v1-candidate',
                source_name='custody-participation', session_control=None, scope_control=None,
                allowed_operations=list(P.TYPED_SUPPORTED if grant else P.METADATA_SUPPORTED),
                purpose='durable-metadata-and-exact-typed-extension-preparation' if grant else 'durable-metadata-and-exact-candidate-preparation',
                development_authorization_binding=P.binding(str(authority.relative_to(P.ROOT)), authority.read_bytes()),
                max_request_bytes=1048576)
            workspace = P.frame_parse((root / 'workspace/workspace.json').read_bytes())
            proposal['workspace_binding'] = {'ref': 'workspace:' + workspace['workspace_ref'],
                                             'sha256': policy['workspace']['manifest_sha256']}
            def stage(value):
                raw = C.encoded(value)
                digest = P.source.sha(raw)
                W.atomic(root / 'workspace/objects' / (digest + '.json'), raw)
                return {'ref': 'workspace-object:' + workspace['workspace_ref'] + ':' + digest, 'sha256': digest}
            proposal_binding = stage(proposal)
            inspection_binding = stage(inspection)
            profile_path = P.ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/typed-scope-diagnostic-profile-0001.json'
            profile = P.frame_parse(profile_path.read_bytes())
            profile.update(proposal_structural_sha256=C.digest(proposal),
                inspection_structural_sha256=C.digest(inspection), impact_structural_sha256=C.digest(fixture.impact),
                ordered_target_version_refs=[t['artifact']['version_ref'] for t in proposal['targets']],
                ordered_decision_core_bindings=[t['decision_core_binding'] for t in proposal['targets']],
                schema_bindings=copy.deepcopy(proposal['schema_bindings']))
            scope_binding = stage(profile)
            review_path = P.ROOT / 'docs/proposals/0007-lab-integrated-schema-package/examples/proposal-review.json'
            review = P.frame_parse(review_path.read_bytes())
            review.update(source_cut=cut, proposal_binding=proposal_binding,
                          stable_core_bindings=[t['decision_core_binding'] for t in proposal['targets']],
                          authority_effect='none')
            if mode == 'bad-review':
                review['proposal_binding'] = {**proposal_binding, 'sha256': '0' * 64}
            review_binding = stage(review)
            pairs = [stage(pair) for pair in inspection['allowed_endpoint_pairs']]
            domains = []
            for pair in inspection['allowed_endpoint_pairs']:
                if pair['qualifier_schema_binding'] not in domains:
                    domains.append(pair['qualifier_schema_binding'])
            relation = next(t for t in proposal['targets'] if t['artifact']['carrier_ref'] == 'cal.artifact-type.relation-kind/v2')
            prior = fixture.selection['relations'][inspection['relation_kind_ref']]['signature_binding']
            message = {'schema_version': 'lab-typed-extension-request/v1-candidate',
                'request_ref': 'request:R03-typed:' + uuid.uuid4().hex, 'actor': actor,
                'relation_kind_candidate': A.public_header(relation['artifact']), 'prior_signature_binding': prior,
                'unique_semantic_question': inspection['unique_question'], 'axis_ref': inspection['axis_ref'],
                'pair_contract_bindings': pairs, 'qualifier_domain_bindings': domains,
                'noncollapse_report_binding': inspection['noncollapse_report_binding'],
                'canonical_writable_authority_ref': 'cal.artifact-type.typed-relation/v3',
                'affected_carrier_successor_refs': [A.public_header(t['artifact']) for t in proposal['targets']
                                                   if t['artifact']['carrier_ref'] == 'cal.artifact-type.artifact-type/v3'],
                'semantic_owner_review_binding': review_binding, 'source_cut': cut, 'authority_effect': 'none'}
            profile_pin = composition.CATALOG_PROFILE
            catalog_row = next(r for r in A.parse((A.KERNEL / 'profiles/selections.json').read_bytes())['selections'] if r['name'] == 'd75')
            route = {'schema_version': 'lab-typed-preparation-routing/v3-candidate', 'scope_ref': scope, 'source_cut': cut,
                'proposal_binding': proposal_binding, 'inspection_binding': inspection_binding,
                'helper_source_binding': composition.binding(composition.HELPER / 'source-manifest.json'),
                'helper_proof_binding': composition.binding(composition.HELPER / 'receipts/proof-0001.json'),
                'catalog_profile_binding': {'ref': catalog_row['profile_path'], 'sha256': profile_pin},
                'catalog_review_binding': {'ref': catalog_row['review_path'], 'sha256': composition.CATALOG_REVIEW},
                'catalog_snapshot_digest': fixture.selection['snapshot_digest'],
                'representation_profile_binding': composition.binding(P.HERE / 'catalog-representations.json'),
                'canonical_writable_authority_ref': 'cal.artifact-type.typed-relation/v3',
                'schema_destinations': [{'schema_binding': selected, 'runtime_schema_path': fixture.schema_paths[selected['ref']]}
                                        for selected in proposal['schema_bindings']],
                'scope_preparation_profile_binding': scope_binding,
                'record_basis': 'complete-current-and-exact-prospective-postimage', 'actual_owner_outcome': None, 'authority_effect': 'none'}
            if mode == 'duplicate-path':
                route['schema_destinations'][1]['runtime_schema_path'] = route['schema_destinations'][0]['runtime_schema_path']
            route_binding = stage(route)
            if grant:
                policy['typed_control'] = {'routing_binding': route_binding}
            policy_path.write_bytes(P.compact(policy))
            channel = Auth.ReaderChannel(policy_path, P.source.sha(policy_path.read_bytes()), schemas)
            channel.authenticate(F.proof(signer, channel.challenge))
            service = ServiceModule.Service(view, channel, schemas)
            call = F.call(channel.context, 'lab.status', cut)
            # Match the declared 900-second current public candidate bound.
            from datetime import timedelta
            call.update(operation='typed.extension.prepare', idempotency_key=proposal['idempotency_key'], message=message,
                        deadline=(Auth.now() + timedelta(seconds=900)).isoformat())
            yield service, call, {'root': root, 'policy_path': policy_path, 'proposal': proposal,
                                  'routing': route, 'routing_binding': route_binding,
                                  'synthetic_model_change': True, 'genuine_semantic_review_provided': False}
        finally:
            try:
                if service is not None:
                    service.close()
            finally:
                signer = None
    assert not root.exists(), 'owned typed policy, signer or workspace remained'
