"""Two separately provisioned owned hosts; exact private five-member selection."""
import copy
from contextlib import contextmanager
from pathlib import Path
import tempfile
import uuid
from . import protocol as P, workspace as W, auth as A, fixtures as F, handlers as H
from . import challenge_fixture as CF, review_fixture as RF, artifact_model as M
from .challenge_submission import ChallengeSubmission
from .guarded_candidate import selection
from .review_preparation import header
from .service import Service

@contextmanager
def example(view, schemas, *, resolve_references=False):
    # The seed host runs original pure preparation. Its signer, policy and
    # authenticated grant are never edited or transferred to the second host.
    with CF.example(view, schemas) as (seed, request, witness):
        call = request()
        with selection(seed):
            builder = ChallengeSubmission(seed, seed.channel.policy['challenge_control']['routing_binding'])
            plan = builder._plan(call['message'], call['expected_source_cut'], call['idempotency_key'])
        materials = {row['ref']: W.read_private(seed.vault.root / row['path'])
                     for row in seed.vault.manifest['materials']}
        challenge_routing = copy.deepcopy(witness['routing'])
        candidate_original = witness['candidate_original']
    metadata = {}
    preference = RF.preference_target(view, materials, metadata)
    preference_raw = P.compact(preference)
    materials['candidate:workflow-preference-target'] = preference_raw
    current = A.now()
    expires = A.instant(challenge_routing['expires_at'])
    authority = challenge_routing['development_authorization_binding']
    scope = view.data['config']['scope_ref']
    control = {'schema_version': 'lab-independent-workflow-composition/v1-candidate',
        'principal_ref': call['message']['actor']['principal_ref'], 'scope_ref': scope,
        'authorization_basis_binding': authority,
        'base_cut_binding': P.binding('selected-workflow-source-cut', P.compact(H.cut(view))),
        'not_before': current.isoformat(), 'expires_at': expires.isoformat(), 'revoked': False,
        'proposal_ref': 'proposal:R03-composed-challenge:' + uuid.uuid4().hex,
        'idempotency_key': 'fixture:workflow-composition',
        'members': [{'source': 'completed-producer', 'operation': 'challenge.submit',
            'idempotency_key': call['idempotency_key'], 'target_version_ref': item['version'],
            'byte_sha256': P.source.sha(item['raw']),
            'core_sha256': P.source.sha(view.handle.common.encoded(item['core']))}
            for item in plan['targets']] + [{'source': 'provisioned-input',
                'target_binding': P.binding('candidate:workflow-preference-target', preference_raw)}],
        'authority_effect': 'none', 'actual_owner_outcome': None}
    materials['candidate:workflow-composition'] = P.compact(control)
    profile = M.artifact_ref(view, RF.selected(view, 'workflow-decision-profile:lab-governance-single-checkpoint'))
    owner = M.artifact_ref(view, RF.selected(view, 'principal:repository-owner'))
    with tempfile.TemporaryDirectory(prefix='cal-R03-workflow-composition-') as temporary:
        root = Path(temporary); root.chmod(0o700)
        key, path, _ = F.provision(root, 'reference-corrected', materials, metadata,
                                  principal=control['principal_ref'])
        policy = P.frame_parse(path.read_bytes())
        vault = Path(policy['workspace']['root'])
        manifest = P.frame_parse((vault / 'workspace.json').read_bytes())
        def object_binding(raw):
            digest = P.source.sha(raw)
            return {'ref': 'workspace-object:' + manifest['workspace_ref'] + ':' + digest, 'sha256': digest}
        route_raw = P.compact(challenge_routing)
        W.atomic(vault / 'objects' / (P.source.sha(route_raw) + '.json'), route_raw)
        routes = []
        cores = [(item['core']['decision_ref'], object_binding(view.handle.common.encoded(item['core'])))
                 for item in plan['targets']]
        preference_core = P.frame_parse(materials[preference['decision_core_binding']['ref']])
        cores.append((preference_core['decision_ref'], preference['decision_core_binding']))
        for decision, core in cores:
            routes.append({'decision_ref': decision, 'core_binding': copy.deepcopy(core),
                'required_owner_voices': [{'role_ref': 'role:repository-owner',
                    'principal': copy.deepcopy(owner), 'role_declaration': copy.deepcopy(profile)},
                    {'role_ref': 'role:definition-owner', 'principal': copy.deepcopy(owner),
                     'role_declaration': M.artifact_ref(view, RF.selected(view, 'decision-bundle:governance-transaction-surface-0074'))}]})
        routing = {'schema_version': 'lab-independent-candidate-review-routing/v1-candidate',
            'principal_ref': control['principal_ref'], 'scope_ref': scope,
            'not_before': current.isoformat(), 'expires_at': expires.isoformat(),
            'authorization_basis_binding': authority,
            'base_cut_binding': P.binding('selected-review-source-cut', P.compact(H.cut(view))),
            'workflow_decision_profile': profile, 'user_decision_preference': header(preference['artifact']),
            'preference_basis': 'proposed-target', 'accountable_owner': owner,
            'workflow_protocol': {'reference': 'protocol:R03-review-workflow:' + uuid.uuid4().hex,
                'reference_class': 'protocol-review-workflow', 'authority_effect': 'none'},
            'members': routes, 'allowed_operation': 'proposal.review',
            'scope_posture': 'isolated-candidate-review-preparation',
            'current_owner_authority_verified': False, 'actual_owner_outcome': None, 'authority_effect': 'none'}
        schema = P.frame_parse((Path(__file__).resolve().parent / 'review-routing.schema.json').read_bytes())
        P.Draft202012Validator(schema, registry=schemas.registry, format_checker=schemas.checker).validate(routing)
        raw = P.compact(routing)
        input_path = 'inputs/workflow-review-routing.json'
        W.atomic(vault / input_path, raw)
        manifest['materials'].append({'ref': 'candidate:review-routing', 'path': input_path, 'sha256': P.source.sha(raw)})
        # Finalize the fresh provisioning before authentication. No existing
        # host's manifest, policy, grant, callback or clock is modified.
        manifest_raw = P.source.encoded(manifest)
        (vault / 'workspace.json').write_bytes(manifest_raw)
        policy['workspace']['manifest_sha256'] = P.source.sha(manifest_raw)
        policy.update(schema_version='lab-local-challenge-review-policy/v1-candidate',
            source_name='custody-participation', allowed_operations=list(P.WORKFLOW_SUPPORTED),
            purpose='durable-metadata-and-exact-challenge-review-composition',
            development_authorization_binding=authority, scope_control=None,
            challenge_control={'routing_binding': object_binding(route_raw)},
            composition_control={'selection_binding': P.binding('candidate:workflow-composition', materials['candidate:workflow-composition'])},
            expires_at=expires.isoformat(), max_request_bytes=1048576)
        if resolve_references:
            from .carrier_references import KIND,CARRIERS
            policy.update(schema_version=KIND,purpose='durable-metadata-and-exact-reference-closed-review',reference_control={
                'resolver_binding':P.binding(str((Path(__file__).resolve().parent/'carrier_references.py').relative_to(P.ROOT)),(Path(__file__).resolve().parent/'carrier_references.py').read_bytes()),
                'routing_binding':copy.deepcopy(policy['challenge_control']['routing_binding']),'supported_carriers':list(CARRIERS)})
        raw = P.compact(policy); path.write_bytes(raw)
        channel = A.ReaderChannel(path, P.source.sha(raw), schemas)
        authenticated = channel.authenticate(F.proof(key, channel.challenge))
        service = Service(view, channel, schemas)
        try:
            def submit():
                value = F.call(channel.context, 'lab.status', H.cut(view))
                value.update(operation='challenge.submit', idempotency_key=call['idempotency_key'],
                             deadline=expires.isoformat(), message=copy.deepcopy(call['message']))
                return value
            def compose(proposal):
                result = copy.deepcopy(proposal)
                result.update(proposal_ref=control['proposal_ref'], idempotency_key=control['idempotency_key'])
                result['targets'].append(copy.deepcopy(preference))
                result['evidence_bindings'].extend([control['members'][-1]['target_binding'],
                    policy['composition_control']['selection_binding']])
                result['evidence_bindings'] = list({(b['ref'], b['sha256']): b for b in result['evidence_bindings']}.values())
                return result
            yield service, submit, compose, {'root': root, 'routing': routing,
                'composition': control, 'candidate_original': candidate_original,
                'authentication_reply': authenticated}
        finally:
            service.close(); key = None
    P.source.require(not root.exists(), 'owned workflow fixture remained after cleanup')
