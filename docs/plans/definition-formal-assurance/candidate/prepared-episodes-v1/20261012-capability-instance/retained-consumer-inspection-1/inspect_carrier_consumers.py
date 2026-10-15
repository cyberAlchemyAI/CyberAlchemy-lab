"""Source-bound CI consumer observations; finite comparisons confer no authority."""
from pathlib import Path
import ast, copy, json, sys
import build_candidate as b
import verify_candidate as a
import verifier as v


def load(path):
    return json.loads(path.read_bytes())


def pure(path, names, constants=()):
    nodes = []
    for node in ast.parse(path.read_bytes()).body:
        if isinstance(node, ast.FunctionDef) and node.name in names:
            nodes.append(node)
        elif isinstance(node, ast.Assign) and any(isinstance(x, ast.Name) and x.id in constants for x in node.targets):
            nodes.append(node)
    assert {x.name for x in nodes if isinstance(x, ast.FunctionDef)} == set(names)
    namespace = {'json': json, 'Any': object}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), namespace)
    return namespace


# Positive-source coordinates stay distinct from carrier spelling and meaning.
COORDINATES = [
    ('id', 'instanceIdentity', 'capability_instance_id', 'Resolve local identity on the common identity carrier; compare with the parent capability identity, not raw version text.'),
    ('capability_version_ref', 'instanceCapabilityVersion', 'capability_version_ref', 'Resolve exactly one admitted capability version and its parent identity; nonempty text does not prove exactness.'),
    ('coordination_context_ref', 'instanceCoordinationContext', 'coordination_context_ref', 'Resolve the declared coordination context and local-owner relation.'),
    ('bounded_context_refs', 'instanceBoundedContexts', 'bounded_context_refs', 'Resolve nominated collection membership and every semantic context; retain one-or-more without inventing exact cardinality or partition.'),
    ('parent_authority_claim', 'instanceParentAuthorityClaim', 'parent_authority_claim_ref', 'Map a parent claim to its exact parent lane; reference inequality alone is insufficient.'),
    ('instance_authority_claim', 'instanceAuthorityClaim', 'instance_authority_claim_ref', 'Map an instance claim to the exact instance lane; concrete claim-record identity policy remains unresolved.'),
    ('inherited_contract_ref', 'instanceInheritedContract', 'inherited_contract_ref', 'Resolve the inherited contract and permitted inheritance; a nominated reference is not successful inheritance.'),
    ('extension_scope', 'instanceExtensionScope', 'extension_scope', 'Map statement and exclusions to the extension scope without creating extension permission.'),
    ('adoption_decision_ref', 'instanceAdoptionDecision', 'adoption_decision_ref', 'Resolve the adopting decision, actor, exact subject, scope and outcome; no adoption is inferred.'),
    ('construction_binding_ref', 'instanceConstructionBinding', 'construction_binding_ref', 'Resolve the D65 construction-stage binding and its evidence; completion is independent.'),
    ('conformance_refs', 'instanceConformanceRefs', 'conformance_refs', 'Map the evidence collection and conformance scope; the allowed empty list does not prove any conformance or authority.'),
    ('lifecycle', 'instanceLifecycle', None, 'Select an owner-accepted lifecycle representation; candidate/admission status and classification posture do not supply it automatically.'),
    ('drift_route', 'instanceDriftRoute', 'drift_route', 'Resolve the route and accountable handler; nonempty nomination is not actual drift handling.'),
    ('recomposition_route', 'instanceRecompositionRoute', 'recomposition_route', 'Resolve recomposition scope and route; retain this coordinate independently of recursion-stop shape.'),
    ('recursion_stop', 'instanceRecursionContract', 'recursion_stop', 'Resolve the budget or stop contract and its semantics; budget/condition schema labels do not prove enforcement or termination.'),
    ('terminal_handoff', 'instanceTerminalHandoff', 'terminal_handoff_ref', 'Resolve a terminal recipient, contract and handoff condition; a string is not performed handoff.'),
    ('local_owner_companion', 'instanceLocalOwner', 'owner_ref', 'Resolve the local owner and owner-to-coordination relation without adding owner to the canonical sixteen-coordinate tuple.'),
]


def inspect(write=False):
    root, unit = b.ROOT, b.UNIT
    prepared = root/'docs/plans/definition-formal-assurance/candidate/prepared-episodes-v1/20261012-capability-instance'
    receipt = load(unit/'types-logic-receipt.json')
    audit = load(prepared/'typed-stage-audit-command-result.json')
    assert audit['exit_code'] == 0 and not (prepared/'typed-stage-audit-stderr.txt').read_bytes()
    assert receipt['full_delivery_sealed'] is False
    context = load(unit/'context.json')
    frozen = receipt['inputs'] + receipt['checker_bindings']
    prior = load(b.BASE/'definitions/CAV2-D60/delivery-manifest.json')['files']
    b.unchanged(frozen + prior + context['sources'])
    b.external_current(context)
    snapshot = b.snapshot()
    assert len(prior) == 10188 and b.r.verify(snapshot, root)['files'] == 201
    runtime = v.f.current_bindings()
    selected = {'typed_receipt': b.ref(unit/'types-logic-receipt.json'),
                'typed_audit': b.ref(prepared/'typed-stage-audit-command-result.json'),
                'discovery': b.ref(prepared/'consumer-discovery.json'),
                'checker': b.ref(Path(__file__).resolve())}
    checks = []

    def ck(name, condition):
        assert condition, name
        checks.append({'check_id': name, 'result': True})

    discovery = load(prepared/'consumer-discovery.json')
    b.unchanged(list(discovery['selected_inputs'].values()))
    ck('discovery-actual-terminal0', load(prepared/'consumer-discovery-command-result.json')['exit_code'] == 0)
    ck('bounded-discovery152-not-accepted-map', discovery['actual_check_count'] == 152 and not discovery['accepted_map_refs'])
    registry_path = root/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json'
    registry = load(registry_path)
    selected['registry'] = b.ref(registry_path)
    current = [r for r in registry['admitted_contracts'] if r['artifact_type_ref'] in registry['current_by_identity'].values()]
    ck('143contracts121current', len(registry['admitted_contracts']) == 143 and len(current) == 121)
    complete = []
    source_version = context['source_selection']['version_ref']
    for row in current:
        artifact = load(root/row['artifact_path'])
        ck('current-bytes-'+row['artifact_type_ref'], b.ref(root/row['artifact_path'])['sha256'] == row['artifact_sha256'] and b.ref(root/row['schema_path'])['sha256'] == row['schema_sha256'])
        versions = artifact.get('semantic_definition_refs', [])
        binding = artifact.get('definition_binding', {})
        if binding.get('definition_id'):
            versions = versions + [binding['definition_id']+'@'+binding.get('version', '')]
        if source_version in versions:
            complete.append(row['artifact_type_ref'])
    ck('one-current-complete-CIv2-binding', complete == ['cal.artifact-type.capability-instance/v2'])
    contracts, schemas, fixtures, projections = {}, {}, {}, []
    successor_path = root/'tooling/generators/artifact_type_successor.py'
    legacy_gen_path = root/'tooling/generators/ctx01_artifact.py'
    legacy_helper_path = root/'tooling/validators/ctx01_artifact_type.py'
    bound_validator_path = root/'tooling/validators/artifact_type_successor.py'
    for name, path in [('successor_generator', successor_path), ('legacy_generator', legacy_gen_path), ('legacy_helper', legacy_helper_path), ('bound_validator', bound_validator_path)]:
        selected[name] = b.ref(path)
    successor = pure(successor_path, ['render_artifact', 'render_instance'])
    legacy_generator = pure(legacy_gen_path, ['label', 'render_value', 'render_instance'], ['CONFIG', 'COMMON_FIELDS'])
    semantic = pure(legacy_helper_path, ['semantic_invariants'])['semantic_invariants']
    current_helpers = pure(bound_validator_path, ['roles_for', 'schema_is_closed'])
    for version in ['v1', 'v2']:
        folder = root/'authority/artifact-types/capability-instance'/version
        artifact = load(folder/'artifact.json')
        schema = load(folder/'schema.json')
        fixture_path = folder/artifact['validation_contract']['positive_witness']
        fixture = load(fixture_path)
        b.c.Draft202012Validator.check_schema(schema)
        validator = b.c.Draft202012Validator(schema)
        ck(version+'-valid-fixture', not list(validator.iter_errors(fixture)))
        ck(version+'-body-is-candidate-not-instance-admission', artifact['status'] == fixture['status'] == 'candidate-unadmitted' and artifact['authority_effect'] == fixture['authority_effect'] == 'none')
        catalog = next(r for r in registry['admitted_contracts'] if r['artifact_type_ref'] == 'cal.artifact-type.capability-instance/'+version)
        ck(version+'-exact-admitted-bytes', catalog['artifact_sha256'] == b.ref(folder/'artifact.json')['sha256'] and catalog['schema_sha256'] == b.ref(folder/'schema.json')['sha256'])
        ck(version+'-positive-lifecycle-overlay', catalog['lifecycle_state'] == ('admitted-historical' if version == 'v1' else 'admitted-current'))
        for label, path in [('artifact', folder/'artifact.json'), ('schema', folder/'schema.json'), ('fixture', fixture_path), ('projection', folder/artifact['validation_contract']['positive_projection'])]:
            selected[version+'-'+label] = b.ref(path)
        before = copy.deepcopy(fixture)
        if version == 'v2':
            rendered = successor['render_instance'](artifact, fixture)
            ck('v2-two-pure-fixture-projections', rendered == successor['render_instance'](artifact, fixture) == (root/selected['v2-projection']['path']).read_text())
            selected['v2-artifact-projection'] = b.ref(folder/'ARTIFACT.md')
            ck('v2-pure-artifact-projection', successor['render_artifact'](artifact) == (folder/'ARTIFACT.md').read_text())
            ck('v2-exact-shared-generator-validator-bindings', artifact['source_direction']['shared_generator_sha256'] == selected['successor_generator']['sha256'] and artifact['validation_contract']['shared_validator_sha256'] == selected['bound_validator']['sha256'])
            wrapper = folder/'validate.py'
            selected['v2-validator-wrapper'] = b.ref(wrapper)
            tree = ast.parse(wrapper.read_bytes())
            ck('v2-wrapper-current-successor-validator', any(isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'SHARED' for t in n.targets) and 'tooling/validators/artifact_type_successor.py' in ast.unparse(n.value) for n in tree.body))
            package = next(n for n in ast.parse(bound_validator_path.read_bytes()).body if isinstance(n, ast.FunctionDef) and n.name == 'validate_package')
            ck('current-package-does-not-call-legacy-semantic-helper', 'semantic_invariants' not in ast.unparse(package))
            relation_path = root/'authority/relation-kinds/candidates/0002-axis-orthogonal-model/model.json'
            selected['relation_model'] = b.ref(relation_path)
            ck('exact-current-relation-roles', current_helpers['schema_is_closed'](schema) and current_helpers['roles_for']('capability-instance', load(relation_path)) == artifact['relation_roles'])
        else:
            rendered = legacy_generator['render_instance'](fixture, 'capability-instance')
            ck('v1-two-pure-fixture-projections', rendered == legacy_generator['render_instance'](fixture, 'capability-instance') == (root/selected['v1-projection']['path']).read_text())
        ck(version+'-projection-input-unmutated', before == fixture)
        contracts[version], schemas[version], fixtures[version] = artifact, validator, fixture
        projections.append({'version': version, 'fixture_projection_sha256': selected[version+'-projection']['sha256'], 'pure_renderer_only': True, 'actual_owned_instance': False})
    decision_path = root/'docs/decisions/0070-definition-complete-lab-model-admission/decision.json'
    decision = load(decision_path)
    selected['C70-decision'] = b.ref(decision_path)
    auth = root/decision['authorization']['path']
    selected['C70-authorization'] = b.ref(auth)
    ck('C70-exact-owner-authorization', decision['status'] == 'owner-admitted' and selected['C70-authorization']['sha256'] == decision['authorization']['sha256'])
    effects = decision['effects']
    ck('C70-scoped-type-effects-not-CI-activation', effects['artifact_types_admitted'] == 93 and effects['artifact_type_predecessors_to_historical'] == 9 and effects['ordinary_instances_admitted'] == 1 and effects['typed_relation_instances_admitted'] == effects['consumer_activations'] == effects['runtime_activations'] == 0)
    ck('v2-source-and-predecessor-exact', contracts['v2']['semantic_definition_bindings'][0]['sha256'] == context['source_selection']['sha256'] and contracts['v2']['predecessor_contract']['sha256'] == selected['v1-artifact']['sha256'])
    # Exact current meanings are observed, not composed into the primary theory.
    core, ir = load(unit/'t.json')['payload'], load(unit/'static-ir.json')
    definition_schema_path = root/'authority/artifact-types/definition/v1/schema.json'
    definition_generator_path = root/'authority/artifact-types/definition/v1/generator.py'
    selected['Definition-schema'] = b.ref(definition_schema_path)
    selected['Definition-generator'] = b.ref(definition_generator_path)
    definition_validator = b.c.Draft202012Validator(load(definition_schema_path))
    definition_generator = pure(definition_generator_path, ['esc', 'bullets', 'render'])
    meanings = []
    for source in [context['source_selection']] + core['depends_on']:
        path = root/source['path']
        doc = load(path)
        projection = path.with_name('DEFINITION.md')
        selected[source['definition_id']] = b.ref(path)
        selected[source['definition_id']+'-projection'] = b.ref(projection)
        ck(source['definition_id']+'-exact-current-meaning', b.source_ref(snapshot, source['definition_id']) == {k: source[k] for k in ['definition_id', 'version_ref', 'path', 'sha256']})
        ck(source['definition_id']+'-Definition-schema', not list(definition_validator.iter_errors(doc)))
        before = copy.deepcopy(doc)
        rendered = definition_generator['render'](doc)
        ck(source['definition_id']+'-two-exact-pure-projections', rendered == definition_generator['render'](doc) == projection.read_text() and doc == before)
        meanings.append({'source': source, 'projection': selected[source['definition_id']+'-projection'], 'accepted_map_refs': [], 'whole_theory_imported': False})
    source_doc = load(root/context['source_selection']['path'])
    definition_probes = []

    def dp(name, mutation, expected):
        doc = copy.deepcopy(source_doc)
        mutation(doc)
        errors = sorted(e.message for e in definition_validator.iter_errors(doc))
        ck('Definition-probe-'+name, (not errors) == expected)
        definition_probes.append({'case_id': name, 'schema_accepted': not errors, 'schema_errors': errors, 'model_sha256': b.ir.digest(doc), 'accepted_semantic_map': False})

    dp('exact-source', lambda x: None, True)
    for field in definition_validator.schema['required']:
        dp('missing-'+field, lambda x, field=field: x.pop(field), False)
    for field in ['owner_accepted_map', 'actual_instance_admission', 'whole_proof']:
        dp('unknown-'+field, lambda x, field=field: x.update({field: True}), False)
    for name, text in [('parent-authority-transfer', 'Parent capability authority automatically authorizes the instance.'), ('conformance-authority-transfer', 'Conformance proves instance authority.'), ('folder-establishes-recursion', 'A copied directory establishes bounded capability recursion.'), ('carrier-shape-proves-realization', 'A schema-valid fixture is an adopted and active capability instance.'), ('owner-reference-proves-permission', 'A nominated owner string establishes owner permission.')]:
        dp(name, lambda x, text=text: x['voices']['scientific_formal'].update(normative_statement=text), True)
    carrier_probes = []

    def cp(name, mutation, expected_shape, expected_legacy=None, version='v2'):
        doc = copy.deepcopy(fixtures[version])
        mutation(doc)
        before = copy.deepcopy(doc)
        errors = sorted(e.message for e in schemas[version].iter_errors(doc))
        helper_results = semantic('capability-instance', doc)
        legacy_ok = all(x[1] for x in helper_results)
        ck('carrier-probe-'+version+'-'+name, (not errors) == expected_shape and (expected_legacy is None or legacy_ok == expected_legacy) and doc == before)
        carrier_probes.append({'case_id': name, 'version': version, 'schema_accepted': not errors, 'schema_errors': errors, 'legacy_helper_accepted': legacy_ok, 'legacy_helper_results': [{'check': x[0], 'result': x[1]} for x in helper_results], 'model': doc, 'model_sha256': b.ir.digest(doc), 'legacy_helper_is_current_bound_package': False, 'current_bound_package_executed': False, 'accepted_map': False})

    # Missing-field probes are shape observations: do not force legacy helper input contracts.
    for version in ['v1', 'v2']:
        cp('exact-fixture', lambda x: None, True, True, version)
    schema = schemas['v2'].schema
    properties = schema['$defs']['capabilityInstance']['allOf'][1]['properties']
    required = set(schema['$defs']['base']['required']) | set(schema['$defs']['capabilityInstance']['allOf'][1]['required'])
    for field in sorted(required - {'capability_instance_id', 'capability_version_ref', 'parent_authority_claim_ref', 'instance_authority_claim_ref'}):
        cp('missing-'+field, lambda x, field=field: x.pop(field), False)
    for field in ['instanceLifecycle', 'lifecycle', 'parent_capability_identity_ref', 'parent_lane', 'instance_lane', 'realization_kind', 'actual_adoption']:
        cp('unreviewed-direct-'+field, lambda x, field=field: x.update({field: 'hyp:unreviewed'}), False)
    for field in ['capability_instance_id', 'capability_version_ref', 'coordination_context_ref', 'parent_authority_claim_ref', 'instance_authority_claim_ref', 'inherited_contract_ref', 'adoption_decision_ref', 'construction_binding_ref', 'drift_route', 'owner_ref', 'recomposition_route', 'terminal_handoff_ref']:
        cp('opaque-'+field, lambda x, field=field: x.update({field: 'hyp:unresolved-'+field}), True, True)
        cp('empty-'+field, lambda x, field=field: x.update({field: ''}), False)
    cp('same-parent-instance-claim-reference', lambda x: x.update(instance_authority_claim_ref=x['parent_authority_claim_ref']), True, False)
    cp('instance-ID-equals-version-reference', lambda x: x.update(capability_instance_id=x['capability_version_ref']), True, False)
    cp('empty-semantic-contexts', lambda x: x.update(bounded_context_refs=[]), False, True)
    cp('duplicate-semantic-context', lambda x: x['bounded_context_refs'].append(x['bounded_context_refs'][0]), False, True)
    cp('multiple-semantic-contexts', lambda x: x['bounded_context_refs'].append('hyp:second-context'), True, True)
    cp('empty-conformance-list', lambda x: x.update(conformance_refs=[]), True, True)
    cp('unresolved-conformance-list', lambda x: x.update(conformance_refs=['hyp:conformance']), True, True)
    cp('budget-kind-missing-budget', lambda x: x['recursion_stop'].pop('budget'), True, True)
    cp('budget-kind-null-budget', lambda x: x['recursion_stop'].update(budget=None), True, True)
    cp('budget-zero', lambda x: x['recursion_stop'].update(budget=0), False, True)
    cp('budget-negative', lambda x: x['recursion_stop'].update(budget=-1), False, True)
    cp('budget-fractional', lambda x: x['recursion_stop'].update(budget=1.5), False, True)
    cp('budget-and-condition', lambda x: None, True, True)
    cp('budget-only-without-condition', lambda x: x['recursion_stop'].pop('condition'), False, True)
    cp('empty-condition', lambda x: x['recursion_stop'].update(condition=''), False, True)
    cp('owner-stop-no-budget', lambda x: x.update(recursion_stop={'kind': 'owner-stop', 'condition': 'hyp:owner-stop'}), True, True)
    cp('terminal-condition-no-budget', lambda x: x.update(recursion_stop={'kind': 'terminal-condition', 'condition': 'hyp:terminal'}), True, True)
    cp('admission-status-is-active', lambda x: x.update(status='active'), False, True)
    cp('authority-effect-self-grant', lambda x: x.update(authority_effect='activate'), False, True)
    cp('activation-overclaim-in-prose', lambda x: x.update(claim_ceiling='Instance adopted, activated and authorized.'), True, True)
    cp('classification-v2-replaces-inherited-v1', lambda x: x['classification'].update(artifact_type_ref='cal.artifact-type.capability-instance/v2'), False, True)
    for relative in contracts['v2']['validation_contract']['negative_witnesses']:
        path = root/'authority/artifact-types/capability-instance/v2'/relative
        selected['negative-'+relative] = b.ref(path)
        ck('current-negative-fixture-'+relative, bool(list(schemas['v2'].iter_errors(load(path)))))
    matrix = []
    for index, (coordinate, symbol, selector, obligation) in enumerate(COORDINATES, 1):
        sort = b.FUNCTIONS[symbol][1]
        row = {'map_id': 'CI-CONSUMER-MAP-'+str(index).zfill(3), 'source_coordinate': coordinate, 'candidate_symbol': symbol, 'candidate_sort': sort, 'carrier_selector': selector, 'direct_schema_field_present': selector in properties if selector else False, 'direct_fixture_value': copy.deepcopy(fixtures['v2'].get(selector)) if selector else None, 'meaning_obligation': obligation, 'status': 'pending-owner-correspondence', 'accepted_map_refs': []}
        matrix.append(row)
    ck('sixteen-coordinates-plus-owner-all-accounted', len(matrix) == 17 and {x[1] for x in COORDINATES[:16]} == set(b.INSTANCE_FIELDS) and COORDINATES[-1][1] == 'instanceLocalOwner')
    ck('lifecycle-not-direct-field-owner-present', 'lifecycle' not in properties and 'owner_ref' in properties and sum(x['direct_schema_field_present'] for x in matrix) == 16)
    ck('contract-required-fields-not-source-completeness', len(contracts['v2']['instance_contract']['required_semantic_fields']) == 12 and 'lifecycle' not in contracts['v2']['instance_contract']['required_semantic_fields'])
    ids = {x['symbol_id']: b.ir.qualified(core['source'], core['scope'], x['symbol_id']) for x in core['declarations']}
    T = [x for x in ir['clauses'] if x['disposition'] == 'encoded']
    I = [x for x in ir['populations'] if x['requirement'] == 'required']
    cases = {x['case_id']: x for x in a.controls()}
    wanted = [
        'realization-specialization-owner-context-claims-budget-stop-and-handoff',
        'no-selected-instance', 'no-independent-actual-authority', 'no-actual-conformance-population', 'no-parent-actual-authority-population',
        'independent-second-parent-actual-authority', 'realization-specialization-overlap-removed-but-genus-preserved',
        'single-semantic-context-remains-sufficient', 'recursion-overlap-removed-budget-remains-sufficient',
        'unused-parent-version-binding-absent', 'budget-only-unused-stop-binding-absent', 'stop-only-unused-budget-binding-absent',
        'unused-version-handle-empty', 'unused-parent-handle-empty', 'unused-recursion-handle-empty',
        'selected-instance-neither-realization-nor-specialization', 'missing-InstanceOwnerLocalDeclared',
        'owner-does-not-have-nominated-local-context-relation', 'nonempty-context-collection-handle-with-no-semantic-context',
        'semantic-context-member-not-in-nominated-collection', 'nominated-collection-member-without-instance-context-relation',
        'instance-identity-collapses-into-parent', 'instance-local-lane-collapses-into-parent-lane',
        'missing-parent-claim-lane-binding', 'extra-parent-claim-at-wrong-lane', 'missing-instance-claim-lane-binding',
        'selected-recursion-has-neither-budget-nor-stop', 'missing-exact-binding-instanceLifecycle',
        'missing-exact-binding-instanceRecompositionRoute', 'missing-exact-binding-instanceTerminalHandoff',
        'selected-ParentClaimGrantsInstanceAuthorityDeclared', 'selected-ConformanceInterpretedAsAuthorityDeclared',
        'selected-CopiedFolderEstablishesRecursionDeclared', 'selected-InstanceAdmissionActivatesLifecycleDeclared',
    ]
    isolate = {
        'selected-instance-neither-realization-nor-specialization': ['root-positive-genus-and-sixteen-coordinates'],
        'missing-InstanceOwnerLocalDeclared': ['owner-locality-companion'],
        'owner-does-not-have-nominated-local-context-relation': ['owner-locality-companion'],
        'nonempty-context-collection-handle-with-no-semantic-context': ['explicit-semantic-context-membership'],
        'semantic-context-member-not-in-nominated-collection': ['explicit-semantic-context-membership'],
        'nominated-collection-member-without-instance-context-relation': ['explicit-semantic-context-membership'],
        'instance-identity-collapses-into-parent': ['one-exact-parent-version-and-distinct-identity'],
        'instance-local-lane-collapses-into-parent-lane': ['parent-and-instance-claim-lanes'],
        'missing-parent-claim-lane-binding': ['parent-and-instance-claim-lanes'],
        'extra-parent-claim-at-wrong-lane': ['parent-and-instance-claim-lanes'],
        'missing-instance-claim-lane-binding': ['parent-and-instance-claim-lanes'],
        'selected-recursion-has-neither-budget-nor-stop': ['recursion-budget-or-stop'],
        'missing-exact-binding-instanceLifecycle': ['root-positive-genus-and-sixteen-coordinates'],
        'missing-exact-binding-instanceRecompositionRoute': ['root-positive-genus-and-sixteen-coordinates'],
        'missing-exact-binding-instanceTerminalHandoff': ['root-positive-genus-and-sixteen-coordinates'],
    }
    for suffix in ['ParentClaimGrantsInstanceAuthorityDeclared', 'ConformanceInterpretedAsAuthorityDeclared', 'CopiedFolderEstablishesRecursionDeclared', 'InstanceAdmissionActivatesLifecycleDeclared']:
        isolate['selected-'+suffix] = ['role-and-authority-boundaries']
    comparisons = []

    def compare(name, raw, expected_T, expected_I, failures=None):
        model = a.qualify(raw, ids)
        evaluator = v.Denotation(ir['declarations'], model)
        clauses = [{'clause_id': x['clause_id'], 'truth': evaluator.truth(x['formal_statement'])} for x in T]
        populations = [{'population_id': x['population_id'], 'truth': evaluator.truth(x['statement'])} for x in I]
        t, i = all(x['truth'] for x in clauses), all(x['truth'] for x in populations)
        ck('typed-'+name, t == expected_T and (expected_I is None or i == expected_I))
        # Independent evaluator preserves the existing global step budget.
        primitive_evaluator = v.Denotation(ir['declarations'], model)
        primitives = {n: primitive_evaluator.truth(v.renamed(z, ids)) for n, z in b.THEORY.items()}
        if failures is not None:
            ck('isolated-primitive-'+name, [n for n, truth in primitives.items() if not truth] == failures)
        comparisons.append({'case_id': name, 'model': model, 'model_sha256': b.ir.digest(model), 'T': t, 'I': i, 'primary_clause_results': clauses, 'population_results': populations, 'primitive_results': primitives, 'semantic_guard_isolated': failures is not None, 'expected_only_failed_primitives': failures or [], 'T_I_steps': evaluator.steps, 'primitive_steps': primitive_evaluator.steps, 'accepted_common_carrier_map': False, 'actual_instance_created': False})

    for name in wanted:
        case = cases[name]
        compare(name, copy.deepcopy(case['model']), case['expected_T'], case['expected_I'], isolate.get(name))
    same_claim = a.base_model()
    a.setfn(same_claim, 'instanceAuthorityClaim', 'ci0', a.getfn(same_claim, 'instanceParentAuthorityClaim', 'ci0'))
    a.refresh(same_claim)
    compare('same-claim-record-reference-with-distinct-declared-lanes', same_claim, True, True)
    # A common printed handle does not identify differently sorted/versioned records.
    same_printed = a.base_model()
    a.setfn(same_printed, b.HANDLES['IdentityReference'], 'id0', 'other')
    a.setfn(same_printed, b.HANDLES['ProductCapabilityVersionReference'], 'v0', 'other')
    compare('same-printed-instance-identity-and-version-handle-with-distinct-denotation', same_printed, True, True)
    issues = [
        'C70 admits the current CI v2 Artifact Type and makes v1 historical. Its one ordinary instance is separately scoped; type admission, fixtures and eligible relation roles do not adopt, construct, activate or authorize a CI.',
        'All sixteen source coordinates and the local-owner companion are accounted. Lifecycle has no direct carrier field. Candidate/admission body status and classification posture need a separate accepted lifecycle map; absence of a direct field does not prove an external representation is absent.',
        'Current v2 schema uses a v2 discriminator while inheriting the v1 classification reference and legacy instance generator metadata. A v2 classification replacement fails shape. The current successor pure projection matches; neither an alias nor full correspondence is inferred.',
        'Budget-kind recursion without a budget, or with null budget, passes shape. Every recursion kind requires condition text; a budget-only object without condition fails shape even though frozen T permits budget-only contracts. Kind, condition and budget require reviewed denotation maps; enforcement, termination, recomposition and handoff remain separate.',
        'Equal parent and instance claim references pass schema but fail the isolated legacy helper. Frozen T permits the same claim-record denotation with separately declared parent and instance lanes. The legacy helper is not called by the current bound package validator. Claim-record identity and lane policy require explicit owner correspondence.',
        'Legacy helper compares instance ID with parent version text. Frozen T compares instance and parent capability identities on one identity carrier. Equal printed identity/version handles preserve T and I; actual common-carrier identity resolution remains unaccepted.',
        'Schema enforces at least one distinct semantic-context reference, while frozen T additionally requires nominated collection membership and declared targets. Opaque context and owner references pass shape; actual context resolution and owner-local relation or permission are unresolved.',
        'The carrier permits empty conformance references and opaque adoption, construction and inherited-contract references. None establishes actual conformance, adoption, completed D65 stages, inheritance or authority. Their collection, decision and stage meanings require accepted maps.',
        'Source Definition schema accepts contrary authority, folder-recursion and realization prose. Deterministic projection proves bytes only. Exact source and thirty dependency meanings are kept qualified without importing their whole theories or accepting translations.',
        'T and required populations I are evaluated independently. Removing coverage examples may preserve T while making I false. Isolated owner, context, parent identity, claim lane, recursion, lifecycle tuple and authority-boundary counterexamples retain the other primitive guards.',
        'The bounded earlier scan selected coordination, product, contexts, craft/impl, implementation and evidence. Its 130 nested/schema/reference matches contain no top-level CI records. This is scoped discovery rather than global or private absence evidence.',
        'No package validator, writer, native operational consumer or live CI is invoked. Schema, pure helper and candidate T/I evidence cannot establish actual correspondence, authenticated principals, authority policy, source fidelity, shared consistency or whole-definition proof.',
    ]
    findings = [{'finding_id': 'CI-CONSUMER-FINDING-'+str(n).zfill(3), 'issue': issue, 'status': 'unresolved', 'accepted_map_refs': [], 'owner_route': 'role:definition-owner with capability, context, identity, lifecycle, construction and authority owners'} for n, issue in enumerate(issues, 1)]
    b.unchanged(frozen + prior + context['sources'] + list(selected.values()))
    b.external_current(context)
    ck('201sources-still-current', b.r.verify(snapshot, root)['files'] == 201)
    ck('runtime-bindings-preserved', runtime == v.f.current_bindings())
    report = {
        'schema_version': 'definition-assurance-CapabilityInstance-consumer-inspection/v1-candidate',
        'result': 'PASS-exact-CapabilityInstance-consumer-observations-and-finite-comparisons',
        'authority_effect': 'none', 'source': context['source_selection'], 'selected_inputs': selected,
        'checks': checks, 'check_count': len(checks), 'meaning_observations': meanings,
        'direct_current_definition_binding_types': complete,
        'historical_and_current_contracts': {version: {'artifact_type_ref': contracts[version].get('artifact_type_ref'), 'body_status': contracts[version]['status'], 'schema_ref': selected[version+'-schema'], 'fixture_ref': selected[version+'-fixture'], 'owned_instance_admission_established': False} for version in contracts},
        'positive_C70_effects': effects, 'source_coordinate_correspondence': matrix,
        'source_coordinate_account_complete': True, 'accepted_semantic_correspondence_complete': False,
        'definition_shape_probes': definition_probes, 'definition_shape_probe_count': len(definition_probes),
        'definition_shape_acceptances': sum(x['schema_accepted'] for x in definition_probes),
        'carrier_shape_probes': carrier_probes, 'carrier_shape_probe_count': len(carrier_probes),
        'carrier_shape_acceptances': sum(x['schema_accepted'] for x in carrier_probes),
        'projection_observations': projections, 'typed_comparison_models': comparisons,
        'typed_comparison_count': len(comparisons), 'isolated_primitive_comparison_count': len(isolate),
        'bounded_prior_scan': discovery['scan'], 'unresolved_consumer_findings': findings,
        'accepted_semantic_map_refs': [], 'legacy_helper_is_current_bound_package': False,
        'bound_package_validator_executed': False, 'canonical_or_candidate_carrier_writer_executed': False,
        'native_or_live_consumer_executed': False, 'actual_instance_adoption_conformance_or_authority_created': False,
        'source_fidelity': 'pending', 'semantic_ready': False, 'mechanized_proof': False,
        'whole_inventory_refresh_complete': False, 'frozen_inputs_preserved': 17,
        'frozen_checker_bindings_preserved': 5, 'prior_candidate_files_preserved': 10188,
        'source_files_current': 201, 'runtime_bindings': runtime,
        'claim_ceiling': 'Complete source-coordinate observations with proposed owner maps, exact current/historical carrier shapes, pure projections and isolated candidate T/I comparisons. No accepted semantic correspondence, actual instance effects, source fidelity, shared consistency or whole proof.'}
    if write:
        b.put('carrier-consumer-inspection.json', report)
    else:
        assert b.r.same_json(report, load(unit/'carrier-consumer-inspection.json')), 'Fresh CI consumer observations differ'
    return report


if __name__ == '__main__':
    result = inspect('--write' in sys.argv)
    print(json.dumps({k: result[k] for k in ['result', 'check_count', 'definition_shape_probe_count', 'definition_shape_acceptances', 'carrier_shape_probe_count', 'carrier_shape_acceptances', 'typed_comparison_count', 'isolated_primitive_comparison_count', 'source_coordinate_account_complete', 'accepted_semantic_correspondence_complete', 'semantic_ready']}, indent=2))
