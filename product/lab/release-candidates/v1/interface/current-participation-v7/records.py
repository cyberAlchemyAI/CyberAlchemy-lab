"""Actual carrier bodies and separately declared closed connection tuples."""
import copy
from .base import ROOT, encoded, require, sha
import json

PREFIX = 'R03-current-episode-0005'
VERSION = '1.0.0-candidate.1'
PRINCIPAL = 'principal:' + PREFIX
PRINCIPAL_REFERENCE = 'principal-reference:' + PREFIX
PROFILE = 'agent-profile:' + PREFIX
GOAL = 'goal:' + PREFIX
WORK = 'work:' + PREFIX
INTENT = 'intent:' + PREFIX
ASSIGNMENT = 'agent-assignment:' + PREFIX
COORDINATION = 'coordination:' + PREFIX
CONTEXT = 'context:' + PREFIX
CAPABILITY = 'agent-capability:' + PREFIX
IMPLEMENTATION = 'implementation:' + PREFIX + '-source-reader'
PRODUCT_CAPABILITY = 'product-capability:cyberalchemy-lab:governed-knowledge-lifecycle'
POLICY = 'protocol:R03-current-episode-0005-policy/v1'
PERIOD = 'protocol:R03-current-episode-0005-period/v1'
EVIDENCE = 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
CLAIM = 'Owned candidate source for exact Context/Session integration. This body grants no action, owner admission, activation, truth, or completed Product realization.'


def fixture(kind, version='v1', filename='record.json'):
    return json.loads((ROOT / 'authority/artifact-types' / kind / version / 'fixtures/valid' / filename).read_bytes())


def common(kind, identity, scope):
    body = fixture(kind)
    body.update(node_id=identity, owner_ref=PRINCIPAL, scope_ref=scope, evidence_refs=[EVIDENCE],
        challenge_route='protocol:R03-fresh-participation-review', successor_refs=[], relation_refs=[], claim_ceiling=CLAIM)
    return body


def relation_ref(kind, counterpart_kind, counterpart):
    return {'relation_kind_ref': kind, 'direction': 'source', 'counterpart_kind': counterpart_kind, 'counterpart_ref': counterpart}


def bodies(projection, scope, config):
    current_product = [s for s in projection['subjects'].values() if s['identity'] == 'product:cyberalchemy-lab' and s['effective_state'] in ['admitted-current', 'local-admitted-current']]
    require(len(current_product) == 1, 'exact current Product unresolved')
    product = current_product[0]['identity']
    principal = common('principal', PRINCIPAL, scope)
    principal['name'] = 'Controlled development reader Principal'
    principal['payload'].update(principal_kind='isolated-fixture-operator', stable_subject_ref='protocol:R03-current-episode-0005-key-subject',
        registry_ref='protocol:R03-current-episode-0005-reader-registry', recognition_boundary_refs=['protocol:R03-current-episode-0005-reader-authentication'], status='active')
    public_identity = 'ed25519-public-key-sha256:' + sha(bytes.fromhex(config['public_key']))
    principal['payload']['stable_subject_ref'] = public_identity
    principal['relation_refs'] = [{'relation_kind_ref': 'relation.asserts-identity-of', 'direction': 'target',
        'counterpart_kind': 'principal-reference', 'counterpart_ref': PRINCIPAL_REFERENCE + '@' + VERSION}]
    principal_reference = common('principal-reference', PRINCIPAL_REFERENCE, scope)
    principal_reference['name'] = 'Bounded controlled signer reference'
    principal_reference['payload'].update(principal_ref=PRINCIPAL, principal_kind='isolated-fixture-operator',
        issuer_ref=config['owner_ref'], resolution_route='protocol:R03-current-episode-0005-signed-source-resolution',
        integrity_digest=public_identity, privacy_posture='Public key digest only; no private key or human identity')
    principal_reference['relation_refs'] = [relation_ref('relation.asserts-identity-of', 'principal', PRINCIPAL + '@' + VERSION)]
    intent = fixture('intent');intent.update(node_id=INTENT, owner_ref=PRINCIPAL, attributed_to=PRINCIPAL, scope_ref=scope,
        direction='Consume trustworthy current candidate Project State through bounded Context and Ontology Views.',
        motivation='Real integration needs a fresh eligible consumer and exact current participation.',
        target_pressure='The prior bounded episode expired. A new identity, source cut and independently bounded Assignment are required for current participation.',
        constraints=['One exact current source cut', 'Ephemeral Machine identity and Session-only short memory', 'Independent host permission', 'Final S02/R08 review'],
        current_output_hypothesis={'artifact_type_ref': 'cal.artifact-type.context-view/v1', 'description': 'Actual same-cut derived views for a fresh ephemeral consumer'},
        review_route='protocol:R03-fresh-participation-review', revision_route='protocol:R03-fresh-participation-review',
        revision_history=[], successor_refs=[], satisfaction_refs=[])
    goal = fixture('goal', filename='goal.json');goal.update(goal_id=GOAL, version=VERSION, name='Fresh same-cut context participation',
        outcome='A separately owned source branch can supply trustworthy bounded views to a fresh ephemeral consumer.',
        rationale='Prevent stale instance reuse and cross-branch state substitution.', success_conditions=['Exact current typed source closure', 'Same signed source and native mapped cuts', 'Fresh classified ephemeral Agent and verified disposal'],
        evidence_requirements=['Signed cold replay', 'Original byte/reference parity', 'Actual Context/Session API and process evidence'],
        accountable_owner_ref=PRINCIPAL, challenge_route='protocol:R03-fresh-participation-review', claim_ceiling=CLAIM)
    work = common('work', WORK, scope);work['name'] = 'Read current scoped Project State'
    work['payload'].update(project_ref=scope, goal_refs=[GOAL + '@' + VERSION], input_refs=[INTENT + '@' + VERSION],
        output_refs=['protocol:R03-fresh-context-delivery'], completion_state='pending', work_statement='Generate current bounded views and consume them in a fresh Session under independent permission.')
    work['relation_refs'] = [relation_ref('relation.member-of', 'project', scope)]
    profile = common('agent-profile', PROFILE, scope);profile['name'] = 'Fresh exact-source reader Profile'
    profile['payload'].update(profile_purpose='Inspect bounded exact original domain sources in a fresh ephemeral Session.',
        allowed_input_kinds=['context-view', 'ontology-view', 'project-state'], allowed_output_kinds=['generated-output'],
        policy_refs=[POLICY], tool_class_refs=[], stop_conditions=['source-invalid', 'period-ended', 'host-permission-revoked'])
    profile['relation_refs'] = [relation_ref('relation.has-capability', 'agent-capability', CAPABILITY + '@' + VERSION)]
    assignment = common('agent-assignment', ASSIGNMENT, scope);assignment['name'] = 'Fresh Profile-eligible reader Assignment'
    assignment['payload'].update(owner_ref=PRINCIPAL, eligible_agent_ref=PROFILE + '@' + VERSION, project_ref=scope,
        work_ref=WORK + '@' + VERSION, intent_ref=INTENT + '@' + VERSION, period=PERIOD,
        expected_output_refs=work['payload']['output_refs'], stop_conditions=['source-invalid', 'period-ended', 'host-permission-revoked'])
    assignment['relation_refs'] = [relation_ref('relation.member-of', 'project', scope), relation_ref('relation.addresses-intent', 'intent', INTENT + '@' + VERSION)]
    coordination = fixture('coordination-context', 'v2', 'product-project-goal.json')
    coordination.update(coordination_context_id=COORDINATION, version=VERSION, name='Fresh reader coordination' if 'name' in coordination else coordination.get('name'))
    coordination.pop('name', None)
    coordination.update(owner_ref=PRINCIPAL, owner_route='protocol:R03-fresh-participation-review', purpose='Coordinate one fresh reader Work and one Goal.',
        project_ref=scope, product_ref=product, goal_ref=GOAL + '@' + VERSION, consumer_refs=[PRINCIPAL, PROFILE + '@' + VERSION],
        intended_uses=['Read current scoped Project State'], source_policy_refs=[POLICY], bounded_context_refs=[],
        subject_scope={'statement': 'Exact current source closure for the selected Work, its Goal and Project.', 'exclusions': ['Historical Session memory', 'Authority inference', 'External effects']},
        evidence_refs=[EVIDENCE], residue_refs=['protocol:R03-native-view-and-public-Session-integration-pending'],
        predecessor_ref=None, revision_history=[], challenge_route='protocol:R03-fresh-participation-review', claim_ceiling=CLAIM)
    context = fixture('context');context.update(context_kind='goal', node_id=CONTEXT, owner_ref=PRINCIPAL, owner_route='protocol:R03-fresh-participation-review', scope_ref=scope,
        product_ref=product, project_ref=scope, goal_ref=GOAL + '@' + VERSION, consumer_refs=[PRINCIPAL, PROFILE + '@' + VERSION],
        intended_uses=coordination['intended_uses'], source_policy_refs=[POLICY], bounded_context_refs=[],
        purpose='Define relevance for the exact signed fresh reader Work source cut.', subject_scope=['Current Project State', 'Fresh participation', 'Declared exact Typed Relations'],
        profile_ref='protocol:R03-owned-source-context-profile', revision_history=[], successor_refs=[],
        challenge_route='protocol:R03-fresh-participation-review', claim_ceiling=CLAIM)
    implementation = common('implementation', IMPLEMENTATION, scope);implementation['name'] = 'Controlled original-source reader'
    implementation['payload'].update(implementation_kind='exact-source-reader',
        execution_entrypoint_ref='product/lab/release-candidates/v1/interface/current-source-adapter-v6/reader.py#SelectedReader.open_signed',
        environment_contract_ref='protocol:R03-selected-R02-reader-environment', conforms_to_schema_refs=['protocol:R03-exact-original-source-view/v1'],
        realizes_capability_refs=[PRODUCT_CAPABILITY])
    implementation['relation_refs'] = [relation_ref('relation.realizes', 'product-capability', PRODUCT_CAPABILITY)]
    capability = common('agent-capability', CAPABILITY, scope);capability['name'] = 'Exact current domain source reading'
    capability['payload'].update(capability_statement='Resolve exact current original domain records from a verified signed source cut without granting action permission.',
        implementation_refs=[IMPLEMENTATION + '@' + VERSION], input_contract_refs=['protocol:R03-original-source-input/v1'],
        output_contract_refs=['protocol:R03-exact-original-source-view/v1'], evidence_contract_refs=['protocol:R03-source-replay-evidence/v1'],
        failure_mode_refs=['protocol:R03-source-invalidation/v1'])
    capability['relation_refs'] = [{'relation_kind_ref': 'relation.has-capability', 'direction': 'target',
        'counterpart_kind': 'agent-profile', 'counterpart_ref': PROFILE + '@' + VERSION}]
    return {'principal': principal, 'principal-reference': principal_reference, 'intent': intent, 'goal': goal, 'work': work, 'agent-profile': profile,
        'agent-assignment': assignment, 'coordination-context': coordination, 'context': context,
        'implementation': implementation, 'agent-capability': capability}


IDENTITY_FIELDS = {'goal': 'goal_id', 'coordination-context': 'coordination_context_id'}


def targets(projection, scope, config):
    result = []
    records = bodies(projection, scope, config)
    for kind, body in records.items():
        identity = body[IDENTITY_FIELDS.get(kind, 'node_id')]
        carrier = 'cal.artifact-type.' + kind + ('/v2' if kind == 'coordination-context' else '/v1')
        result.append({'category': 'artifact-instance', 'operation': 'admit', 'version_ref': identity + '@' + VERSION,
            'carrier_ref': carrier, 'record': body, 'predecessor_ref': None, 'decision_ref': 'decision:' + PREFIX + ':' + kind, 'contract': None})
    selected = {t['record'][IDENTITY_FIELDS.get(kind, 'node_id')]: t for kind, t in zip(records, result)}
    def endpoint(ref):
        if ref in selected:
            t = selected[ref];return {'kind': projection['contracts'][t['carrier_ref']]['semantic_kind'], 'ref': ref, 'version_ref': t['version_ref']}
        rows = [s for s in projection['subjects'].values() if s['identity'] == ref and s['effective_state'] in ['admitted-current', 'local-admitted-current']]
        require(len(rows) == 1, 'exact original typed endpoint unavailable: ' + ref)
        s = rows[0]
        kind = 'project' if s['carrier_ref'] == 'cal.artifact-type.project-identity/v1' else 'product' if s['carrier_ref'] == 'cal.artifact-type.product-identity/v2' else s['kind']
        return {'kind': kind, 'ref': ref, 'version_ref': s['version_ref']}
    specs = [
        ('reference-principal', 'relation.asserts-identity-of', PRINCIPAL_REFERENCE, PRINCIPAL,
            {'assertion_kind': 'Controlled development signer public-key digest correspondence', 'claim_scope': scope}),
        ('work-project', 'relation.member-of', WORK, scope, {'membership_role': 'Work in the selected Project'}),
        ('assignment-project', 'relation.member-of', ASSIGNMENT, scope, {'membership_role': 'Reader participation in the selected Project'}),
        ('goal-project', 'relation.member-of', GOAL, scope, {'membership_role': 'Outcome for the selected Project'}),
        ('context-project', 'relation.member-of', CONTEXT, scope, {'membership_role': 'Relevance boundary in the selected Project'}),
        ('assignment-intent', 'relation.addresses-intent', ASSIGNMENT, INTENT, {'intent_resolution_ref': INTENT + '@' + VERSION, 'addressing_role': 'Exact-source reader participation'}),
        ('goal-intent', 'relation.addresses-intent', GOAL, INTENT, {'intent_resolution_ref': INTENT + '@' + VERSION, 'addressing_role': 'Fresh same-cut view outcome'}),
        ('profile-capability', 'relation.has-capability', PROFILE, CAPABILITY, {'capability_version_ref': CAPABILITY + '@' + VERSION, 'declaration_basis': 'Exact current original-source reading'}),
        ('implementation-product-capability', 'relation.realizes', IMPLEMENTATION, PRODUCT_CAPABILITY,
            {'realization_role': 'Source-reading subset; complete Product realization remains unproved', 'exact_target_version_ref': endpoint(PRODUCT_CAPABILITY)['version_ref']}),
        ('context-goal', 'relation.frames', CONTEXT, GOAL, {'framing_role': 'Relevance for the one selected Goal'}),
    ]
    template = json.loads((ROOT / 'authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/typed-relation/v3/fixtures/valid/record.json').read_bytes())
    for name, kind, left, right, qualifiers in specs:
        record = copy.deepcopy(template);identity = 'typed-relation:' + PREFIX + ':' + name
        record.update(node_id=identity, owner_ref=PRINCIPAL, scope_ref=scope, evidence_refs=[EVIDENCE], name=name,
            claim_ceiling=CLAIM, challenge_route='protocol:R03-fresh-participation-review', relation_refs=[], successor_refs=[])
        record['payload'].update(relation_kind_ref=kind, source=endpoint(left), target=endpoint(right), qualifiers=qualifiers, relation_evidence_refs=[EVIDENCE])
        result.append({'category': 'typed-relation', 'operation': 'admit', 'version_ref': identity + '@' + VERSION,
            'carrier_ref': 'cal.artifact-type.typed-relation/v3', 'record': record, 'predecessor_ref': None,
            'decision_ref': 'decision:' + PREFIX + ':' + name, 'contract': None})
    return result
