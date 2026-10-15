#!/usr/bin/env python3
"""Materialize candidate preparation; never run or admit the Lab runtime."""
import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OLD = ROOT / 'docs/plans/0009-lab-integrated-roadmap'
SCHEMA = ROOT / 'docs/proposals/0007-lab-integrated-schema-package'
API = ROOT / 'docs/proposals/0008-lab-api-contracts'
DESIGN = ROOT / 'implementation/lab-runtime/candidates/repeatable-operation/design'
PRODUCT = ROOT / 'product/lab/release-candidates/v1'


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def md(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.strip() + '\n')


def binding(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'size_bytes': path.stat().st_size}


def pointer(document, selector):
    for part in selector.removeprefix('#').removeprefix('/').split('/') if selector else []:
        document = document[part.replace('~1', '/').replace('~0', '~')]
    return document


def schema_properties(schema, path, dependencies, seen=None):
    """Inspect top-level fields using pinned local refs; no network or body coercion."""
    result = dict(schema.get('properties', {}))
    ref = schema.get('$ref')
    if ref:
        document, _, fragment = ref.partition('#')
        mapped = dependencies.get((str(path.relative_to(ROOT)), ref))
        if mapped:
            target = ROOT / mapped['target_path']
            if binding(target)['sha256'] != mapped['target_sha256']:
                raise ValueError('compatibility dependency drift')
        elif not document:
            target = path
        elif ':' not in document:
            target = (path.parent / document).resolve()
            target.relative_to(ROOT)
        else:
            raise ValueError('undeclared remote schema reference: ' + ref)
        key = (str(target), fragment)
        if key not in (seen or set()):
            result.update(schema_properties(pointer(read(target), fragment), target, dependencies, (seen or set()) | {key}))
    for child in schema.get('allOf', []):
        result.update(schema_properties(child, path, dependencies, seen))
    return result


def main():
    original = read(OLD / 'dag.json')
    variant = read(OLD / 'single-checkpoint/dag.json')
    transformations = {m['original_task']: m for m in read(OLD / 'single-checkpoint/task-transformation.json')['mappings']}
    domain = read(SCHEMA / 'domain-bindings.json')
    relation_registry = read(ROOT / 'authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json')
    api = read(API / 'api-contracts.json')
    workflows = read(SCHEMA / 'workflow-catalog.json')['workflows']

    # Sources are captured before outputs; immutable predecessors are never regenerated.
    source_paths = {ROOT / s['path'] for s in read(API / 'SOURCE-BASELINE.json')['sources']}
    source_paths.update(p for base in [OLD, SCHEMA, API] for p in base.rglob('*')
                        if p.is_file() and '__pycache__' not in p.parts)
    source_paths.update(ROOT / p for p in [
        'authority/definitions/registry.json',
        'authority/definitions/candidates/0006-craft-identity/definitions/method/v1/definition.json',
        'authority/owners/foundation-01/v1/candidates/0004-craft-identity/owners.json',
        'authority/admissions/governance-transaction-surface/v1/instances/governance/workflow-decision-profile.json',
        'authority/admissions/governance-transaction-surface/v1/instances/governance/authority-boundary.json',
        'authority/admissions/lab-operational-runtime/v1/instances/governance/authority-boundary.json'])
    sources = [binding(p) for p in sorted(source_paths)]
    write(HERE / 'SOURCE-BASELINE.json', {
        'schema_version': 'lab-one-shot-preparation-sources/v1-candidate', 'authority_effect': 'none',
        'sources': sources,
        'source_manifest_digest': hashlib.sha256(json.dumps(sources, sort_keys=True, separators=(',', ':')).encode()).hexdigest()})

    scope = {
        'schema_version': 'lab-candidate-execution-scope/v1-candidate', 'authority_effect': 'none',
        'authorization_provenance': {'kind': 'conversation-instruction', 'exact_text': 'Do recommendation',
            'interpretation': 'Carry out the recommended governance preparation and reconcile its execution contracts.',
            'is_admission_decision': False, 'is_operator_signature': False},
        'authorized_now': ['source inspection', 'candidate design and schema authoring', 'task and SWU reconciliation',
                           'source/hash/JSON/schema/graph authoring checks'],
        'runtime_tests_authorized_by_this_record': False,
        'candidate_build_plan_status': 'prepared; runtime execution and its test scope are not asserted by this preparation record',
        'write_roots': [str(p.relative_to(ROOT)) for p in [HERE, DESIGN.parent, PRODUCT]],
        'isolated_store_policy': 'New candidate namespace, separate keys and journal; no pointer or mount to an admitted/live store. Actual store execution requires selected execution authority.',
        'excluded_effects': ['canonical admission before R08', 'editing frozen runtime v1/v2', 'editing predecessor plans or receipts',
            'editing unrelated dirty work', 'operating existing stores', 'key/credential creation', 'service activation',
            'external publication', 'push', 'deployment', 'retirement or deletion'],
        'stop_conditions': ['unresolved carrier or actor binding at affected dispatch', 'source drift', 'effect beyond selected scope',
            'missing real owner authority', 'test execution lacking applicable authorization', 'uncertain effect without reconciliation',
            'release requiring unavailable evidence or unknown future semantic target']}
    write(HERE / 'execution-scope.json', scope)

    profile = copy.deepcopy(read(ROOT / 'authority/artifact-types/workflow-decision-profile/v1/fixtures/valid/record.json'))
    profile.update(node_id='workflow-decision-profile:lab-integrated-candidate-final-review',
        name='Integrated Lab candidate final review', owner_ref='role:repository-owner',
        scope_ref='scope:lab-integrated-candidate-final-review',
        evidence_refs=['docs/plans/0010-lab-one-shot-execution/execution-scope.json'],
        challenge_route='challenge-contract:cyberalchemy-lab-operational-foundation',
        claim_ceiling='Candidate profile for a distinct workflow type. No D74 authority extension, admission or execution permission.')
    profile['relation_refs'] = [{'relation_kind_ref': 'relation.governed-by', 'direction': 'source',
        'counterpart_kind': 'policy', 'counterpart_ref': 'policy:cyberalchemy-lab-operational-foundation'}]
    profile['payload']['workflow_type_ref'] = 'workflow-type:lab-integrated-candidate-final-review'
    profile['payload']['invalidation_conditions'] += ['target-bytes-change', 'source-cut-change', 'unmet-acceptance', 'new-semantic-target']
    write(HERE / 'governance/workflow-decision-profile.json', profile)
    write(HERE / 'governance/continuation-contract.json', {
        'schema_version': 'lab-workflow-continuation-contract/v1-candidate', 'authority_effect': 'none',
        'status': 'proposed-interpretation-requires-final-review',
        'profile_ref': profile['node_id'], 'workflow_type_ref': profile['payload']['workflow_type_ref'],
        'unit': 'one declared application continuation for this resolved exact bundle', 'limit': 1,
        'ordered_steps': ['A01', 'A02', 'A03', 'A04'],
        'steps_are_not_new_owner_decisions': True,
        'recovery': 'Resume the same continuation from verified journal state; never redispatch uncertain effects. Recovery changes neither targets nor scope.',
        'expiry': 'Completion, revocation, invalidation, or a required new semantic target ends this continuation.',
        'carrier_fit_gate': 'C02/S02 must establish this unit with the selected workflow contract. The existing integer field alone does not prove this interpretation.'})
    write(HERE / 'governance/member-matrix.json', {'authority_effect': 'none',
        'status': 'preparation-matrix-not-a-decision-bundle', 'actual_answering_principal_ref': None,
        'members': [{'member_class': name, 'proposed_owner_role': role, 'requested_effect': effect,
                     'materialized_final_targets': [], 'current_owner_authority_verified': False,
                     'selected_outcome': None, 'scope_rule': boundary}
            for name, role, effect, boundary in [
                ('semantic-mappings', 'role:definition-owner', 'exact endpoint representation admission', 'Project/Product/Method representations; no execution authority'),
                ('carrier-contracts', 'role:artifact-type-owner', 'exact carrier and registry postimage admission', 'Method and any selected successors; no implicit instance admission'),
                ('typed-connections', 'role:identity-graph-owner', 'selected exact endpoint/qualifier binding admission', 'Preserve all existing axes and exact pairs; endpoint meaning remains separately owned'),
                ('runtime-implementation', 'role:repository-owner', 'exact implementation admission', 'New code package; frozen v1/v2 remain historical sources'),
                ('workflow-governance', 'role:repository-owner', 'exact workflow/profile/continuation admission', 'New workflow type; no widening D74 boundary'),
                ('ontology-import', 'role:repository-owner', 'selected exact ontology/import dispositions', 'Independent source and ontology authority; no blanket migration'),
                ('capability-adoption', 'role:repository-owner', 'exact realization/adoption binding admission', 'Do not infer usefulness or operation from binding'),
                ('local-operations', 'role:repository-owner', 'separately represented bounded local action authorization', 'Requires actual actor, environment, scope, prerequisites and recovery; outside admission atomicity'),
                ('release-disposition', 'role:repository-owner', 'exact local release disposition', 'No service activation, push, deployment or unknown later semantic target')]]})

    # C01: closed implementation metadata, independent from governed domain carriers.
    string = {'type': 'string', 'minLength': 1}
    digest = {'type': 'string', 'pattern': '^[a-f0-9]{64}$'}
    ref = {'type': 'object', 'additionalProperties': False, 'properties': {'path': string, 'sha256': digest}, 'required': ['path', 'sha256']}
    schema = {'$schema': 'https://json-schema.org/draft/2020-12/schema',
        '$id': 'urn:cyberalchemy-lab:implementation:source-profile:v1-candidate', 'type': 'object', 'additionalProperties': False,
        'properties': {'schema_version': {'const': 'lab-independent-source-profile/v1-candidate'},
            'authority_effect': {'const': 'none'}, 'profile_id': string,
            'protocol_version': {'const': 1}, 'executable_manifest_sha256': digest, 'policy_core_sha256': digest,
            'authority_basis': {'type': 'array', 'minItems': 1, 'items': ref},
            'registries': {'type': 'array', 'minItems': 1, 'items': ref},
            'content_manifest': ref, 'expected_cut': string,
            'domain_posture': {'enum': ['isolated-candidate', 'admitted-source']},
            'transition_basis': {'type': 'object', 'additionalProperties': False,
                'properties': {'mode': {'enum': ['initial', 'declared-consequence', 'reviewed-successor']},
                    'basis_refs': {'type': 'array', 'minItems': 1, 'items': ref}}, 'required': ['mode', 'basis_refs']}},
        'required': ['schema_version', 'authority_effect', 'profile_id', 'protocol_version', 'executable_manifest_sha256',
            'policy_core_sha256', 'authority_basis', 'registries', 'content_manifest', 'expected_cut', 'domain_posture', 'transition_basis']}
    write(DESIGN.parent / 'schemas/source-profile.schema.json', schema)
    md(DESIGN / 'profile-contract.md', '''# Independent source profile protocol

Status: candidate implementation protocol metadata; no canonical Source Profile type is invented.

An executable manifest identifies code. A policy core identifies permitted capture roots, exact selectors, accepted schema/profile versions, authority rules and transition rules. An independent capture pins the original-byte manifest, registry bytes, authority basis and expected source cut. Two captures may use the same executable without changing its identity.

## Capture and authority

1. Resolve immutable admission evidence before mutable lookup hints. Require complete original bytes and all selected schema dependencies.
2. Restrict paths to declared repository-relative roots; reject traversal, duplicate normalized paths, escaping symlinks and undeclared files. Schema selection is exact, including JSON Pointer selectors; never assume every identity is node_id.
3. Read the authoritative cut, capture original bytes, then reread the cut. Reject races, mismatched hashes or unavailable closure. Derived lookup and SQLite data are disposable projections.
4. Separate isolated candidate policy, signing keys, stores and journals from admitted operation. A candidate capture cannot satisfy an admitted-write gate.
5. Verify byte SHA separately from parsed meaning. Wire hashing, JCS command fingerprints and artifact byte hashing retain their distinct subjects.

## Profiles and transitions

The source-profile schema is transport/implementation metadata. It does not replace Project State, Ontology Cut or their governance. All references resolve against exact pinned bytes and dependencies.

A declaration of deterministic post-admission capture is allowed only when the reviewed policy core already covers the exact transaction consequences. Keep that stable core outside the changing capture and transaction postimage. Otherwise prepare a separately reviewed successor profile, retaining predecessor history and revalidating carried-forward inputs. Never rewrite an old profile or infer a successor admission.

## Four specified acceptance cases

| Case | Required result |
| --- | --- |
| Same executable, two distinct data cuts | Two capture identities; unchanged executable identity; each cut and original bytes verified independently. |
| Unsupported protocol | Reject before interpreting the capture or executing effects. |
| Changed lookup hint | Follow immutable authority evidence; reject a conflicting hint rather than treating it as admission. |
| Post-admission capture | Accept only declared consequence closure under the reviewed stable core; otherwise require an exact successor target. |

These are design cases. No profile loader, signature channel, original-byte capture implementation or runtime case was executed here.
''')
    write(DESIGN / 'profile-acceptance-cases.json', {'authority_effect': 'none', 'execution_status': 'not-run',
        'cases': [{'id': i, 'expected': result} for i, result in [
            ('same-code-two-cuts', 'preserve executable identity; distinguish capture identities'),
            ('unsupported-protocol', 'reject'), ('changed-lookup', 'follow immutable evidence or reject conflict'),
            ('post-admission-capture', 'declared consequence only; otherwise reviewed successor')]]})
    code_sources = [binding(p) for p in sorted((ROOT / 'implementation/lab-runtime/v1').rglob('*'))
                    if p.is_file() and '__pycache__' not in p.parts]
    write(DESIGN / 'profile-examples/executable-manifest.json', {'authority_effect': 'none', 'files': code_sources})
    executable_sha = binding(DESIGN / 'profile-examples/executable-manifest.json')['sha256']
    authority_file = ROOT / 'docs/decisions/0075-lab-operational-runtime-v1-admission/authorization.json'
    registry_file = ROOT / 'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json'
    for label, manifest_path in [('domain', SCHEMA / 'SOURCE-BASELINE.json'), ('api', API / 'SOURCE-BASELINE.json')]:
        write(DESIGN / f'profile-examples/{label}.json', {
            'schema_version': 'lab-independent-source-profile/v1-candidate', 'authority_effect': 'none',
            'profile_id': 'illustration:source-profile:' + label, 'protocol_version': 1,
            'executable_manifest_sha256': executable_sha,
            'policy_core_sha256': binding(DESIGN / 'profile-contract.md')['sha256'],
            'authority_basis': [{'path': str(authority_file.relative_to(ROOT)), 'sha256': binding(authority_file)['sha256']}],
            'registries': [{'path': str(registry_file.relative_to(ROOT)), 'sha256': binding(registry_file)['sha256']}],
            'content_manifest': {'path': str(manifest_path.relative_to(ROOT)), 'sha256': binding(manifest_path)['sha256']},
            'expected_cut': 'illustration:cut:' + label, 'domain_posture': 'isolated-candidate',
            'transition_basis': {'mode': 'initial', 'basis_refs': [{'path': str((DESIGN / 'profile-contract.md').relative_to(ROOT)),
                                                                   'sha256': binding(DESIGN / 'profile-contract.md')['sha256']}]}})
    md(DESIGN / 'profile-examples/README.md', '''# Two source-profile shape examples

The two examples pin the same exact frozen executable and two different source metadata manifests. Their illustration cut identities do not describe a real captured store cut. The referenced manifests retain available original-file bindings but are not deployed content-package closure or execution authority. D75 evidence supplies provenance for the executable only; it does not authorize these profiles or candidate operation. No runtime example was executed.
''')

    # C02 exact carrier identity dispatch plus candidate endpoint proposals.
    carrier_rows = []
    dependencies = {(b['source_path'], b['source_ref']): b for b in read(SCHEMA / 'schema-dependencies.json')['bindings']}
    for b in domain['bindings']:
        path = ROOT / b['schema_path']
        s = pointer(read(path), b['schema_selector'])
        properties = schema_properties(s, path, dependencies)
        candidates = [key for key in properties if key in ['id', 'node_id'] or key.endswith('_id')]
        identity = 'record_id' if b['carrier_ref'] == 'cal.artifact-type.foundation-manifest/v1' else candidates[0] if len(candidates) == 1 else None
        carrier_rows.append(dict(b, identity_selector='/' + identity if identity else None,
            identity_disposition='exact-schema-field' if identity else 'explicit-instance-adapter-required',
            operational_use='read-only-historical' if b['write_posture'] != 'current' else 'requires-authority-and-semantic-reference-checks'))
    endpoint_rows = []
    for endpoint, carrier, selector in [('project', 'cal.artifact-type.project-identity/v1', '/project_id'),
            ('product', 'cal.artifact-type.product-identity/v2', '/product_id')]:
        b = next(b for b in domain['bindings'] if b['carrier_ref'] == carrier)
        endpoint_rows.append({'endpoint_kind': endpoint, 'carrier_ref': carrier, 'identity_selector': selector,
            'schema_binding': {'path': b['schema_path'], 'sha256': b['schema_sha256']},
            'status': 'candidate-semantic-mapping-not-an-admitted-alias',
            'meaning': 'Identity carrier represents the governed endpoint; carrier record and represented subject retain distinct kinds.',
            'requires': ['exact semantic owner review at R08', 'existing exact endpoint pair', 'qualifier constraints', 'admitted instance eligibility']})
    endpoint_rows.append({'endpoint_kind': 'method', 'carrier_ref': 'cal.artifact-type.method/v1',
        'identity_selector': '/method_id', 'schema_binding': binding(DESIGN.parent / 'semantic-proposals/method/v1/schema.json')
            if (DESIGN.parent / 'semantic-proposals/method/v1/schema.json').exists() else None,
        'status': 'candidate-carrier-required', 'meaning': 'A governed transformation specification; neither its Definition nor its application binding is the Method instance.',
        'requires': ['candidate Method carrier', 'artifact-type and semantic owner review at R08', 'exact relation binding and current eligibility']})
    relation_rows = []
    for r in relation_registry['entries']:
        raw = read(ROOT / r['instance_path'])['payload']
        for pair in raw['allowed_endpoint_pairs']:
            relation_rows.append({'relation_kind_ref': r['relation_kind_ref'], 'axis_id': r['axis_id'],
                'source_kind': pair['source_kind'], 'target_kind': pair['target_kind'],
                'qualifier_contract': raw['qualifier_contract'], 'relation_binding': {'path': r['instance_path'], 'sha256': r['instance_sha256']},
                'disposition': 'existing-exact-pair; selected instances still need meaning, qualifier-domain and authority checks',
                'endpoint_mapping_gaps': [k for k in [pair['source_kind'], pair['target_kind']] if k in ['project', 'product', 'method']]})
    write(DESIGN / 'contract-impact.json', {'schema_version': 'lab-contract-impact/v1-candidate', 'authority_effect': 'none',
        'registered_versions': domain['registered_version_count'], 'current_identities': domain['current_count'],
        'carriers': carrier_rows, 'endpoint_proposals': endpoint_rows, 'relation_kinds': len(relation_registry['entries']),
        'exact_pairs': relation_rows, 'noncollapse_verdict': 'not-certified; targeted candidate rationale in reference-gap-dispositions.md'})

    # Materialize the missing Method specification, outside the admitted dispatcher.
    method_fields = ['method_id', 'version', 'name', 'scope', 'inputs', 'actions', 'roles', 'gates', 'outputs',
                     'evidence_requirements', 'residue_rule', 'validation_rule', 'recomposition_rule', 'boundary', 'owner_ref', 'evidence_refs']
    method_props = {key: string for key in method_fields}
    for key in ['inputs', 'actions', 'roles', 'gates', 'outputs', 'evidence_requirements', 'boundary']:
        method_props[key] = {'type': 'array', 'minItems': 1, 'uniqueItems': True, 'items': string}
    method_props['evidence_refs'] = {'type': 'array', 'uniqueItems': True, 'items': string}
    method_props.update(schema_version={'const': 'cyberalchemy-lab-method/v1-candidate'},
        kind={'const': 'method'}, authority_effect={'const': 'none'}, status={'const': 'candidate-unadmitted'},
        semantic_definition_ref={'const': 'CAV2-D32@1.0.0-candidate.1'})
    method_schema = {'$schema': 'https://json-schema.org/draft/2020-12/schema',
        '$id': 'urn:cyberalchemy-lab:candidate-carrier:method:v1', 'type': 'object', 'additionalProperties': False,
        'properties': method_props, 'required': list(method_props)}
    method_path = DESIGN.parent / 'semantic-proposals/method/v1/schema.json'
    write(method_path, method_schema)
    endpoint_rows[-1]['schema_binding'] = binding(method_path)
    impact = read(DESIGN / 'contract-impact.json')
    impact['endpoint_proposals'] = endpoint_rows
    write(DESIGN / 'contract-impact.json', impact)
    write(method_path.parent / 'artifact.json', {'schema_version': 'lab-candidate-carrier-descriptor/v1',
        'artifact_type_ref': 'cal.artifact-type.method/v1', 'semantic_kind': 'method',
        'identity_selector': '/method_id', 'semantic_definition_ref': 'CAV2-D32@1.0.0-candidate.1',
        'schema_binding': binding(method_path), 'authority_effect': 'none', 'status': 'candidate-not-registered',
        'required_final_members': ['definition-owner semantic conformance', 'artifact-type-owner exact carrier', 'typed-endpoint-owner mapping'],
        'open_obligations': ['governed artifact-type instance and generator fit', 'version/lifecycle rules', 'admitted registry postimage', 'negative and roundtrip evidence']})
    write(method_path.parent / 'example.json', {
        'schema_version': 'cyberalchemy-lab-method/v1-candidate', 'kind': 'method', 'authority_effect': 'none',
        'status': 'candidate-unadmitted', 'semantic_definition_ref': 'CAV2-D32@1.0.0-candidate.1',
        'method_id': 'method:lab-governed-state-inspection', 'version': '1.0.0-candidate.1',
        'name': 'Governed state inspection', 'scope': 'Read permitted Lab artifacts at one exact captured cut.',
        'inputs': ['selected read scope', 'exact source profile and cut', 'artifact selector and budgets'],
        'actions': ['lab.status', 'catalog.get', 'artifact.query', 'artifact.inspect'],
        'roles': ['bounded reader'], 'gates': ['actual read authority', 'exact source/dependency closure', 'budget and cut validity'],
        'outputs': ['bounded result with original body, effective admission evidence, lifecycle, typed relations and gaps'],
        'evidence_requirements': ['source byte hashes', 'query cut', 'selected exact contract', 'admission evidence when applicable'],
        'residue_rule': 'Report unresolved or unavailable references explicitly; never manufacture an admitted result.',
        'validation_rule': 'Cross-check the returned claims against pinned canonical bytes and independent admission evidence.',
        'recomposition_rule': 'Combine bounded inspection results only for the same verified cut and scope; preserve each claim basis.',
        'boundary': ['read-only', 'no admission', 'no inferred action authority', 'no durable Agent memory'],
        'owner_ref': 'role:repository-owner', 'evidence_refs': []})
    md(DESIGN / 'reference-gap-dispositions.md', '''# Contract and reference dispositions

Status: candidate design. Exact shapes are mapped; operational semantic closure remains gated.

## Endpoint meaning and noncollapse

Project Identity/v1 represents a Project through project_id, purpose and coordination scope. Product Identity/v2 represents a Product through product_id, value promise and scope. The proposed endpoint adapters read those exact identity fields. They do not rename every carrier of either kind into a Project/Product or admit a new alias. Owner review of these mappings is one final-bundle member.

Method Binding records applying a Method to a Product or Project. Its binding_id is not the Method's identity. A Definition states reusable meaning; a Method instance specifies one repeatable transformation. Governed Model records a model with its own contract and rules. None is substituted for Method. The proposed Method carrier follows admitted CAV2-D32's minimum fields, with no execution grant. Its complete type mechanics, lifecycle and registry integration remain S01/C02 obligations before use.

No Relation Kind or pair is added here. The impact matrix retains every admitted exact pair and qualifier shape. Proposed endpoint representation changes require exact role bindings, owner evidence, writable eligibility and admitted no-collapse/orthogonality checks. Noncollapse is not established by schema validation.

## Named gaps and dispositions

| Gap | Disposition | Affected use |
| --- | --- | --- |
| Project/Product endpoint representation | Explicit candidate mappings, final semantic review | All selected pairs involving either endpoint |
| Method carrier absent | Materialized candidate schema; complete governed type mechanics and admission member | All selected Method connections |
| Identity fields behind wrappers/allOf | Follow the nine explicit compatibility mappings and local selectors; all 143 carriers have exact field dispositions | Every selected carrier |
| Qualifier value domains | Source shapes retained; bind selected allowed values and pair semantics | Affected relation dispatch |
| Ten workflow templates | Per-transition binding requirements in workflow-bindings.json | Workflow execution |
| Local effects versus admission | Separate action authorization member; no activation/external effect in admission | A02/A04 |
| Continuation unit unspecified | New scoped candidate workflow continuation contract; prove fit at S02 | Application after R08 |
| Legacy wrapper resolution | Preserve the nine explicit pinned compatibility mappings | Runtime schema resolver |

An exact binding or a named gap meets C02's design-disposition criterion. A named gap never permits the affected runtime action. New carrier schemas stay outside the admitted dispatcher until exact final admission.

Foundation Manifest uses record_id for the manifest record. Its principal_id names the separate subject principal; it is not substituted for the record identity. This explicit disposition and the wrapper field inventory are authoring evidence, with runtime resolver conformance still required.
''')

    wf_rows = []
    by_ref = {b['carrier_ref']: b for b in domain['bindings']}
    for w in workflows:
        definition = read(SCHEMA / w['path'])
        transitions = []
        for t in definition['transitions']:
            transitions.append({'transition_ref': t['transition_ref'], 'from_state': t['from_state'], 'to_state': t['to_state'],
                'carriers': [dict(by_ref[c], mapped_state_selector=None, mapped_state_value=None)
                            for c in sorted(set(t['input_carriers'] + t['output_carriers']))],
                'actor_roles': t['actor_role_refs'], 'actor_assignment_bindings': [],
                'satisfaction_requirements': t['satisfaction_check_refs'], 'implemented_check_bindings': [],
                'authority_requirements': t['authority_requirement_refs'],
                'recovery': {'known_failure': t['failure_state'], 'uncertain_effect': t['indeterminate_state'],
                    'rule': 'inspect exact journal/cut; reconcile under exact recovery contract; no blind retry'},
                'status': 'blocked-for-runtime-until-bindings-exist'})
        wf_rows.append({'name': w['name'], 'source_binding': binding(SCHEMA / w['path']),
            'domain_state_rule': 'Coordination phase is separate from commitment, admission, carrier lifecycle and outcome satisfaction.',
            'profile_route': 'bounded read/candidate substeps use explicit existing authority; exact semantic decisions go to R08; no nested automatic checkpoint',
            'transitions': transitions})
    write(DESIGN / 'workflow-bindings.json', {'authority_effect': 'none', 'workflows': wf_rows,
        'status': 'complete-required-binding-inventory; not-executable',
        'closure_owner_tasks': ['W01', 'W02', 'W03', 'S01', 'S02']})

    acceptance = [
        ('AC01', 'All 34 API operations conform to their exact request/result/error contracts; no success asserted from result envelope alone.', 'implementation and negative conformance evidence'),
        ('AC02', 'Every selected persisted object resolves its exact eligible schema, original bytes and complete dependencies; all selected semantic references close.', 'artifact dispatch and byte roundtrip evidence'),
        ('AC03', 'Every selected connection uses its exact declared pair, endpoint mapping, qualifier values and separate authority.', 'typed-axis review and rejected-connection evidence'),
        ('AC04', 'Fresh process and fresh Agent reconstruct Project State and trace decisions from bounded Context/Ontology Views; session memory expires.', 'actual restart/session observations'),
        ('AC05', 'Canonical publication is all-or-nothing within its reviewed scope; interruption and uncertain response reconcile without duplicate effects.', 'publisher and recovery evidence'),
        ('AC06', 'SQLite rebuild matches canonical query results at the same cut; stale generations/cursors cannot become authority.', 'projection parity and stale-cut evidence'),
        ('AC07', 'Managed file generation preserves original artifact bytes or records the exact rendering; unauthorized overwrite and escaped paths are rejected.', 'file/export boundary evidence'),
        ('AC08', 'Real candidate engineering work and research work record satisfaction independently from schema validity or admission.', 'genuine bounded task observations, not fixtures'),
        ('AC09', 'An observed failure yields an evidence-bound candidate lesson; a later genuine task applies it and assesses outcome and counterevidence.', 'actual learning episode; no automatic lesson admission'),
        ('AC10', 'Selected ontology/import mapping preserves source authority, ontology cut and target decisions; every selected input has an explicit disposition.', 'mapping/parity and selected migration evidence'),
        ('AC11', 'Installation, upgrade, replay and rollback behave within the declared isolated local environment with explicit residue.', 'candidate operation and recovery evidence'),
        ('AC12', 'A repository owner completes the three inspection journeys with correct independently checkable answers and no concealed gaps.', 'human pilot observations; Agent-only pilot does not prove owner usability'),
        ('AC13', 'Final targets, owners, profiles, source cut, evidence, privacy and local effects form a closed exact bundle with acyclic digests.', 'S02 frozen review closure')]
    write(PRODUCT / 'release-scope.json', {'schema_version': 'lab-product-release-scope/v1-candidate', 'authority_effect': 'none',
        'product_ref': 'product:cyberalchemy-lab', 'interface': 'local CLI with proposed authenticated stdio adapter',
        'environment': 'local Linux repository; concrete Python/SQLite versions recorded before actual evaluation',
        'operations': [o['operation'] for o in api['operations']],
        'candidate_readiness_basis': 'genuine isolated candidate Work, pilot and conformance evidence; final owner may reject this basis',
        'stable_operational_release_basis': 'actual admitted local operation and acceptance closure; candidate proof alone never establishes this',
        'human_pilot_required_for_value_claim': True,
        'activation_count': 0, 'external_effect_refs': [],
        'publication_selected': False, 'deployment_selected': False,
        'candidate_acceptance': [{'id': i, 'condition': c, 'required_evidence': e, 'observation': None} for i, c, e in acceptance],
        'release_rule': 'R08 resolves exact existing targets. A04 may execute only separately represented selected effects with satisfied conditions. New evidence-dependent semantic targets require new review.',
        'performance_rule': 'Record actual duration, query latency, artifact count and byte sizes. No invented SLA or storage-saving claim.',
        'condition_representation_gate': 'Operational and conditional-release carriers must fit the actual final bundle; this file grants no authority.'})
    md(PRODUCT / 'PRODUCT-ACCEPTANCE.md', '''# CyberAlchemy Lab acceptance

Status: proposed before implementation and pilot. This is a local candidate readiness contract, with separately tracked admitted operational closure.

The Product serves repository owners and collaborators who need to inspect meaning, current status, evidence and authority, and give bounded context to an ephemeral Agent. The migration Project is one use of that Product. Neither the Product's admitted identity nor successful migration proves its usefulness.

## Interface and environment

Start with a local CLI and the proposed authenticated stdio adapter. All 34 selected operations remain in implementation scope. Record concrete local Linux, Python and SQLite versions before evaluation. Network listeners, public publication, deployment and service activation are outside this release scope.

## Three owner journeys

1. List Definitions; inspect an admitted-current, historical and unadmitted case. Identify exact bytes, effective status, authority evidence and open gaps. Every selected answer must match independently inspected source evidence.
2. Inspect one Project and its Product. Trace their distinct purpose/value, Work, decisions and typed connections. Identify any missing endpoint mapping rather than treating it as valid.
3. Close one Agent session and start another. Reconstruct continuity from Project State and pinned Context/Ontology Views. Trace a real candidate change, observed failure, lesson and later outcome; distinguish candidate evidence from admitted operation.

A human repository owner must actually perform the value pilot; record actor, inputs, attempts, incorrect answers, elapsed time, findings and source cut. Agent execution can prove technical behavior but does not substitute for human usefulness evidence. No measurements have been observed by this preparation.

## Acceptance conditions

''' + '\n\n'.join(f'### {i}\n\n{c}\n\nEvidence: {e}. Current observation: **not collected**.' for i, c, e in acceptance) + '''

## Final decision and later operation

Candidate readiness may be reviewed at R08 from genuine candidate evidence. Actual admitted operation remains A02/A03 evidence. Stable operational release waits for that closure and exactly represented release conditions. If it requires a new semantic target or owner judgment based on later evidence, record a later review requirement; do not weaken acceptance to preserve an approval count.
''')

    # Concrete phase-aware task/SWU contracts preserve all predecessor criteria.
    dag = copy.deepcopy(variant)
    dag.update(schema_version='lab-one-shot-execution-dag/v1-candidate', status='reconciled-preparation',
        implementation_execution_authorized=False,
        execution_scope_ref='execution-scope.json', source_dag_binding=binding(OLD / 'single-checkpoint/dag.json'))
    revised_criteria = {
        'C10': ['Prepare exact runtime/profile/admission members with independent targets, evidence, owners and exclusions; defer actual outcomes to R08 and application to A01.'],
        'C11': ['Prepare real operator/store instructions and authorized isolated bootstrap evidence; admitted local provisioning remains A02.'],
        'C12': ['Record actual authorized candidate Work and original criteria with candidate provenance; admitted Work observation remains A03.'],
        'C13': ['Record candidate replay/restart/session closure evidence; admitted continuity remains A03.'],
        'W08': ['Prepare closed workflow/learning model members and exact evidence for R08; record no owner outcomes or admission here.'],
        'W09': ['Assess genuine authorized candidate engineering/research/learning; original admitted-operation criteria remain A03.'],
        'O06': ['Prepare exact ontology/import/mapping members and scope exclusions for R08; do not infer import or source retirement.'],
        'O07': ['Assess selected candidate ontology/import parity and complete item dispositions; admitted operational coherence remains A03.'],
        'R04': ['Prepare realization/adoption declarations and authentic candidate-use evidence; actual admitted adoption remains A03.'],
        'R05': ['Gather genuine authorized candidate pilot observations under predeclared measures; admitted pilot obligations remain A03.'],
        'R07': ['Close original validation/alignment obligations for exact candidate bytes; record post-admission evidence requirements; no stable release claim.'],
        'R08': ['Resolve actual final outcomes for every exact independently scoped member; all materialized targets/roles/evidence/cuts match; no unknown future target; application follows A01-A04.']}
    for node in dag['nodes']:
        tid = node['id']
        node['contract_path'] = f'work-pack/tasks/{tid}.md'
        node['preparation_evidence_status'] = 'materialized-design' if tid in ['C01', 'C02', 'R01'] else 'not-collected'
        if 'original_task_contract' in node:
            node['original_task_contract'] = str((OLD / 'work-pack/tasks' / f'{tid}.md').relative_to(ROOT))
        phase = node['phase']
        criteria = node.get('original_acceptance_evidence', node.get('acceptance_evidence', []))
        node['phase_acceptance_evidence'] = revised_criteria.get(tid, criteria)
        node['original_criteria_obligation_route'] = node.get('post_approval_obligation_ref') or ('R08/A01' if tid in ['C10', 'W08', 'O06'] else tid)
        predecessor = (OLD / 'work-pack/tasks' / f'{tid}.md') if tid in transformations else None
        text = f'# {tid} — {node["name"]}\n\nStatus: {node["status"]}. Phase: {phase}. Authority effect: none.\n\n'
        text += 'This is the phase overlay. Original construction criteria remain obligations; candidate proof never closes admitted operation.\n\n'
        if predecessor:
            text += f'Original contract: [{tid}]({predecessor}). Exact source hash is in ../../SOURCE-BASELINE.json.\n\n'
        text += '## Dependencies\n\n' + ', '.join(node['depends_on']) + '\n\n## Scope\n\n' + node['scope_rule'] + '\n\n'
        text += '## Input and authority gates\n\n'
        if phase == 'preparation':
            text += 'Use hash-bound admitted sources or explicitly isolated candidate inputs. An upstream preparation task supplies evidence and candidate bytes, never admission or action authority. Resolve design dispositions before affected implementation; obtain applicable authorization before runtime/test effects.\n\n'
        elif tid == 'R08':
            text += 'Every selected member exists, source/base matches, accountable owners and role evidence resolve, required real observations exist, carrier fit and publisher recovery are proved. Collect the actual final response; never generate an approving outcome.\n\n'
        else:
            text += 'Require the actual resolved exact bundle and admitted prerequisites. Each operation needs its own represented scope and current authority. Stop on invalidation, missing evidence or uncertain effects; inspect/reconcile instead of retrying blindly.\n\n'
        text += '## Preserved acceptance obligations\n\n' + '\n'.join('- ' + c for c in criteria) + '\n\n'
        text += '## Acceptance in this phase\n\n' + '\n'.join('- ' + c for c in node['phase_acceptance_evidence']) + '\n\n'
        text += 'Original operational/owner criterion route: ' + node['original_criteria_obligation_route'] + '.\n\n'
        if node.get('post_approval_obligation_ref'):
            text += '## Deferred admitted-operation obligation\n\n' + node['post_approval_obligation_ref'] + '\n\n'
        text += '## Write and evidence rules\n\nCandidate outputs stay in the selected candidate roots or a reviewed task-specific candidate staging path. Canonical paths from original contracts denote proposed postimages before R08, not writable authority. Record exact output paths, observations and checks in evidence.json; synchronize this overlay DAG and SWU evidence. Frozen runtime v1/v2, original plans/receipts, unrelated dirty work and live stores are excluded.\n'
        md(HERE / node['contract_path'], text)
    write(HERE / 'dag.json', dag)
    swus = copy.deepcopy(read(OLD / 'swu-manifest.json')['units'])
    node_map = {n['id']: n for n in dag['nodes']}
    for unit in swus:
        node = node_map[unit['parent_task']]
        unit['original_swu_binding'] = binding(OLD / 'swu-manifest.json')
        unit['original_write_scope'] = unit.pop('write_scope')
        unit['candidate_write_scope'] = []
        for scope_index, target in enumerate(unit['original_write_scope']):
            if target.startswith(('implementation/lab-runtime/candidates/', 'product/lab/release-candidates/')):
                unit['candidate_write_scope'].append(target)
            elif ' ' not in target and '<' not in target and not target.startswith('Future'):
                unit['candidate_write_scope'].append(str((DESIGN.parent / 'staged' / target).relative_to(ROOT)))
            else:
                unit['candidate_write_scope'].append(str((DESIGN.parent / 'staged-targets' / unit['id'] / str(scope_index)).relative_to(ROOT)) + '/')
        unit['phase'] = node['phase']
        unit['phase_scope_rule'] = node['scope_rule']
        unit['contract_path'] = node['contract_path']
        unit['write_scope_rule'] = 'Candidate staging before R08; exact original canonical targets are proposed postimages only. Actual application requires resolved authority.'
        unit['operational_obligation_ref'] = node.get('post_approval_obligation_ref')
        unit['phase_done_criteria'] = node['phase_acceptance_evidence'] if unit['parent_task'] in revised_criteria else unit['done_criteria']
        unit['original_criteria_obligation_route'] = node['original_criteria_obligation_route']
        unit['original_ordered_rules'] = copy.deepcopy(unit['ordered_rules'])
        if node['phase'] == 'preparation' and unit['parent_task'] in revised_criteria:
            unit['ordered_rules'] = ['Prepare attributable candidate evidence for this original obligation; defer its admission/operational consequence to ' +
                                     node['original_criteria_obligation_route'] + ': ' + rule for rule in unit['original_ordered_rules']]
        unit['original_handoff_note'] = unit['handoff_note']
        unit['handoff_note'] = 'Use this phase contract, scoped authority and exact sources. Candidate evidence is not an admitted prerequisite. Record missing bindings before affected use; no fabricated owner outcome or runtime evidence.'
        unit['related_context'] = [str((OLD / p).relative_to(ROOT)) for p in unit['related_context']]
        unit['completion_evidence'] = []
    for tid in ['S01', 'S02', 'A01', 'A02', 'A03', 'A04']:
        n = node_map[tid]
        swus.append({'id': f'SWU-{tid}-01', 'parent_task': tid, 'objective': n['name'],
            'phase': n['phase'], 'depends_on': n['depends_on'], 'contract_path': n['contract_path'],
            'done_criteria': n['acceptance_evidence'], 'acceptance_evidence': n['acceptance_evidence'],
            'phase_scope_rule': n['scope_rule'], 'completion_evidence': [], 'execution_owner': 'local-collaborator'})
    write(HERE / 'swu-manifest.json', {'schema_version': 'lab-one-shot-swu-manifest/v1-candidate',
        'authority_effect': 'none', 'original_units_preserved': 57, 'units': swus})
    write(HERE / 'evidence.json', {'authority_effect': 'none', 'design_deliverables': {
        'C01': ['implementation/lab-runtime/candidates/repeatable-operation/design/profile-contract.md',
                'implementation/lab-runtime/candidates/repeatable-operation/schemas/source-profile.schema.json'],
        'C02': ['implementation/lab-runtime/candidates/repeatable-operation/design/contract-impact.json',
                'implementation/lab-runtime/candidates/repeatable-operation/design/reference-gap-dispositions.md'],
        'R01': ['product/lab/release-candidates/v1/PRODUCT-ACCEPTANCE.md', 'product/lab/release-candidates/v1/release-scope.json']},
        'runtime_tests_executed': False, 'admissions_applied': 0, 'stores_provisioned': 0,
        'pilot_observations': [], 'final_owner_outcomes': None,
        'milestone_completion_rule': 'Design preparation is not complete implementation, governed operation or stable release.'})
    write(HERE / 'readiness.json', {'authority_effect': 'none',
        'governance_preparation': 'materialized', 'candidate_construction': 'not-started',
        'final_review_ready': False, 'stable_release_ready': False,
        'gates': [{'id': name, 'disposition': disposition, 'resolve_at': task, 'new_human_approval_required_by_this_gate': extra}
            for name, disposition, task, extra in [
                ('execution-scope', 'preparation instruction recorded; select actual runtime/test scope before those effects', 'effect entry', 'only if applicable authority is absent'),
                ('independent-profile', 'candidate protocol/schema and examples materialized', 'C01/C03', False),
                ('endpoint-representation', 'Project/Product mappings and Method carrier proposed; canonical use waits for exact admission', 'C02/S01/R08', False),
                ('workflow-bindings', 'all required bindings inventoried; real actors, lifecycle values, checks and recovery remain', 'W01-W03/S01', False),
                ('continuation-carrier-fit', 'one declared continuation proposed; meaning and carrier fit must be proved', 'C02/S02/R08', False),
                ('publisher-and-recovery', 'implementation and interruption evidence missing', 'C07/S02', False),
                ('pilot-and-value', 'conditions predeclared; real candidate and human observations missing', 'C12/W09/R05', False),
                ('owner-and-target-closure', 'independent member matrix prepared; final exact targets and actual role verification pending', 'S02/R08', False),
                ('later-semantic-target', 'a new target or evidence-dependent semantic judgment cannot be preadmitted', 'A03/A04', 'yes if it actually arises')]]})

    write(HERE / 'decision-ledger.json', {'authority_effect': 'none', 'decisions': [
        {'id': i, 'disposition': d, 'basis': b, 'requires_final_review': review} for i, d, b, review in [
            ('profile-carrier', 'implementation metadata', 'existing C01 recommendation; no new canonical carrier inferred', False),
            ('interface', 'local CLI/authenticated stdio', 'existing R01 recommendation and prepared API surface', True),
            ('endpoint-project-product', 'explicit representation adapters', 'exact identity fields; no generic kind alias', True),
            ('endpoint-method', 'new candidate Method carrier', 'CAV2-D32 explicit minimum; Method Binding is separate', True),
            ('workflow-continuation', 'one declared application continuation', 'new scoped proposal; D74 integer does not establish unit', True),
            ('candidate-evidence', 'supports candidate readiness', 'real authorized use; separate actual admitted operation', True),
            ('stable-release', 'requires actual operational closure', 'preserve A03/A04; new later targets need review', True),
            ('external-effects', 'none selected', 'default local scope; admission activation zero', False)]]})
    context_sources = [
        (OLD / 'single-checkpoint/approval-boundary.json', '/required_preflight', ['G01', 'G05']),
        (OLD / 'work-pack/tasks/C01.md', 'Implementation detail: ordered rules', ['G02']),
        (OLD / 'work-pack/tasks/C02.md', 'Implementation detail: ordered rules', ['G03']),
        (OLD / 'work-pack/tasks/R01.md', 'Implementation detail: ordered rules', ['G04']),
        (SCHEMA / 'FIT-REPORT.md', 'Endpoint mappings; workflow and actor bindings', ['G03']),
        (API / 'REVIEW.md', 'Execution requirements', ['G05']),
        (ROOT / 'authority/admissions/governance-transaction-surface/v1/instances/governance/workflow-decision-profile.json', '/payload', ['G01']),
        (ROOT / 'authority/definitions/candidates/0006-craft-identity/definitions/method/v1/definition.json', '/voices/scientific_formal', ['G03'])]
    write(HERE / 'session-evidence/context-index.json', {'authority_effect': 'none', 'kind': 'preparation-session-evidence',
        'mode': 'lean', 'handoff': None, 'strict_coverage': 'covered-for-preparation-only',
        'obligations': [{'id': i, 'status': 'covered', 'description': s} for i, s in [
            ('G01', 'Scope and checkpoint constraints'), ('G02', 'Independent source profiles'),
            ('G03', 'Exact carrier/reference dispositions'), ('G04', 'Acceptance before pilot'), ('G05', 'Task/SWU and effect reconciliation')]],
        'sources': [dict(binding(p), selector=sel, obligation_refs=obs,
                        excerpt=p.read_text().splitlines()[0] if p.suffix == '.md' else json.dumps(pointer(read(p), sel))[:900])
                    for p, sel, obs in context_sources],
        'runtime_handoff_runnable': False, 'runtime_handoff_blockers': ['runtime actor/check/carrier fit and real pilot evidence still require construction']})
    md(HERE / 'session-evidence/CONTEXT.md', '''# Preparation context

Session evidence for the governance preparation request. Mode: lean; eight selected source files; no runtime handoff.

The source index maps each selector to G01 scope/profile, G02 source captures, G03 reference/endpoint fit, G04 Product acceptance, or G05 phase/effect reconciliation. The exact source manifest pins the wider dependencies used to generate the matrix and task overlays. Excluded: unrelated formal-assurance work, live stores, secrets and unselected external effects.

All preparation obligations have evidence. Runtime obligations remain construction work; this context is not runnable authority for actual Lab operations.
''')
    md(HERE / 'PLAN.md', '''# Integrated Lab: preparation for one final review

Status: candidate governance preparation materialized. Authority effect: none. The original roadmap, variant and receipts are preserved.

## Prepared

- A bounded preparation scope with the actual conversation instruction; no owner outcomes or operator signatures are fabricated.
- A new scoped candidate Workflow Decision Profile and an explicit proposed continuation unit; D74's authority is not widened.
- Independent source-profile protocol/schema and four specified design cases.
- Exact disposition of 143 contract versions, 121 current identities, 41 Relation Kinds and 550 exact endpoint pairs.
- Project/Product representation proposals and a missing Method carrier candidate. The ten workflow templates now have a complete required-binding inventory; their runtime bindings still need implementation.
- Product acceptance declared before pilot: all 34 API operations, three owner journeys and thirteen acceptance conditions.
- All 46 task contracts and all 57 original SWUs reconciled for the new phases, plus six SWUs for integration/application tasks. Original acceptance obligations and post-admission work remain visible.

## Run order

1. Recheck the exact source baseline and this preparation receipt.
2. Implement C03 onward and S01 in isolated candidate staging, following the reconciled DAG. Resolve each named semantic/actor/lifecycle/check gap before affected use. Runtime tests and real candidate operations require their applicable execution scope.
3. Gather actual engineering, research, learning and human pilot observations; preserve failures and counterevidence. Complete S02's publisher/recovery, owner-role, exact target, profile and evidence closure.
4. Present one frozen package at R08 with independent member identities and actual owner outcomes. No partial admission of an all-or-nothing bundle.
5. Apply A01 repository admission. A02 operational actions require separately represented exact authorization; verify A03; complete A04 only when its actual conditions and authority exist.

## Remaining stops

The final package is not built. Workflow lifecycle/actor/check bindings, Method type mechanics, operational/continuation carrier fit, authenticated channels, idempotency journal, mixed-target publisher/recovery and pilot evidence remain implementation gates. They need no automatic intermediate semantic approval while built as candidates. Missing authority at an actual effect, unknown future targets or release needing a new evidence-dependent decision cause a specific stop.

Candidate readiness may be reviewed from genuine candidate evidence. Stable operational release requires actual admitted operation. No source drift, hidden gap, altered acceptance or assumed owner role is accepted merely to retain one checkpoint.

## Evidence

See execution-scope.json, decision-ledger.json, evidence.json, SOURCE-BASELINE.json, dag.json, swu-manifest.json and receipts/preparation-check.json. Authoring checks establish source/shape/phase consistency only. No runtime suite, store, signature, pilot, admission or release occurred.
''')
    md(HERE / 'WORK-PACK.md', '# Reconciled task board\n\nAuthority effect: none. Status is execution status; design deliverables do not imply runtime completion.\n\n| Task | Phase | Status | Contract |\n| --- | --- | --- | --- |\n' + '\n'.join(
        f'| {n["id"]} | {n["phase"]} | {n["status"]} | [{n["name"]}]({n["contract_path"]}) |' for n in dag['nodes']))
    print(json.dumps({'prepared_tasks': len(dag['nodes']), 'swus': len(swus), 'carrier_versions': len(carrier_rows),
                      'relation_pairs': len(relation_rows), 'workflow_models': len(wf_rows), 'authority_effect': 'none'}))


if __name__ == '__main__':
    main()
