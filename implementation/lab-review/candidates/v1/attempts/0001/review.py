"""Read-only exact C10 preparation. Protocol proposals grant no authority."""
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath

from jsonschema import Draft202012Validator

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[3]
RUN = 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
RUNTIME = 'implementation/lab-runtime/candidates/repeatable-operation'
BOOTSTRAP = 'implementation/lab-bootstrap/candidates/v1/packages/0004'
CONTEXT = 'implementation/lab-context/candidates/v1/packages/0004'
INTEGRATION = 'implementation/lab-integration/candidates/v1'
REGISTRY = 'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json'
RECEIPT = INTEGRATION + '/receipts/C09/0001/receipt.json'
EXCLUSIONS = ['canonical admission before R08', 'activation or provisioning',
              'external effects', 'actual owner outcome or signature',
              'Product adoption or usefulness', 'new Relation Kind or pair']


def encoded(value):
    # Internal protocol encoding, not a JCS implementation or native event encoder.
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + '\n').encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    p = PurePosixPath(path)
    if p.is_absolute() or '..' in p.parts or p.as_posix() != path:
        raise ValueError('not an exact repository-relative path')
    full = ROOT / path
    if not full.is_file() or full.is_symlink() or not full.resolve().is_relative_to(ROOT):
        raise ValueError('not a regular in-repository file: ' + path)
    return full.read_bytes()


def load(path):
    return json.loads(read(path))


def binding(path):
    raw = read(path)
    return {'path': path, 'sha256': sha(raw)}


def verify_rows(rows):
    paths = [r['path'] for r in rows]
    if len(set(paths)) != len(paths):
        raise ValueError('duplicate exact file binding')
    for row in rows:
        if sha(read(row['path'])) != row['sha256']:
            raise ValueError('changed exact file binding: ' + row['path'])


def verify_upstream():
    receipt = load(RECEIPT)
    if not (receipt['result'] == 'PASS' and receipt['task_complete'] is True
            and receipt['cases'] == receipt['passed_cases'] == 213
            and receipt['inventory_complete'] and receipt['observations_complete']
            and receipt['actual_owner_outcome'] is None and receipt['authority_effect'] == 'none'):
        raise ValueError('incomplete or authority-bearing C09 evidence')
    verify_rows(receipt['files'])
    verify_rows(receipt['source_bindings'])
    verify_rows(load(RUN + '/context-C10.json')['source_bindings'])
    return receipt


def registry_candidate():
    original = load(REGISTRY)
    candidate = copy.deepcopy(original)
    artifact = load(BOOTSTRAP + '/method/artifact.json')
    mechanics = load(BOOTSTRAP + '/method/mechanics.json')
    if any(r['artifact_type_ref'] == artifact['artifact_type_ref'] for r in original['descriptors']):
        raise ValueError('Method candidate would overwrite an existing descriptor')
    candidate['version'] = 'C10-preparation-1'
    candidate['claim_ceiling'] = 'Candidate Method descriptor addition only; inherited admitted contracts unchanged. No admission or activation.'
    candidate['descriptors'].append({
        'activation_state': 'not-activated', 'artifact_type_id': mechanics['artifact_type_id'],
        'artifact_type_ref': artifact['artifact_type_ref'],
        'descriptor_path': BOOTSTRAP + '/method/artifact.json',
        'descriptor_sha256': sha(read(BOOTSTRAP + '/method/artifact.json')),
        'descriptor_version': '1.0.0-candidate.1', 'effective_decision_refs': [],
        'effective_state': 'candidate-unadmitted', 'embedded_status': 'candidate-unadmitted',
        'instance_discriminator': mechanics['instance_discriminator'],
        'proposed_primary_definition_ref': artifact['semantic_definition_refs'][0],
        'resolution_target_ref': None, 'schema_path': BOOTSTRAP + '/method/schema.json',
        'schema_sha256': artifact['schema_sha256'], 'semantic_binding_posture': 'current-as-declared',
        'semantic_definition_refs': artifact['semantic_definition_refs']})
    rows = candidate['descriptors']; inventory = candidate['inventory']
    inventory['descriptor_count'] = len(rows)
    inventory['descriptor_declared_ref_count'] = len({r['artifact_type_ref'] for r in rows})
    inventory['descriptor_identity_count'] = len({r['artifact_type_id'] for r in rows})
    inventory['descriptor_resolved_ref_count'] = len({r['resolution_target_ref'] or r['artifact_type_ref'] for r in rows})
    inventory['state_counts'] = dict(Counter(r['effective_state'] for r in rows))
    inventory['semantic_binding_counts'] = dict(Counter(r['semantic_binding_posture'] for r in rows))
    schema = load('authority/artifact-types/candidates/0006-effective-state-registry/schema.json')
    Draft202012Validator(schema).validate(candidate)
    if candidate['admitted_contracts'] != original['admitted_contracts'] or candidate['current_by_identity'] != original['current_by_identity']:
        raise ValueError('preparation changed admitted registry')
    return candidate


def runtime_artifact():
    artifact = load('authority/admissions/lab-operational-runtime/v1/instances/implementation.json')
    artifact.update(node_id='implementation:cyberalchemy-lab:repeatable-operation',
                    name='Lab repeatable operation candidate',
                    scope_ref='protocol:lab-final-review:C10',
                    evidence_refs=[RECEIPT], successor_refs=[],
                    claim_ceiling='Exact C09 candidate code/profile closure only. No actual admission, general API certification, adoption, activation or power-loss durability.')
    artifact['payload']['execution_entrypoint_ref'] = RUNTIME + '/lab.py'
    artifact['payload']['environment_contract_ref'] = INTEGRATION + '/packages/0001/manifest.json'
    artifact['payload']['conforms_to_schema_refs'] = []
    artifact['payload']['implementation_kind'] = 'candidate-repeatable-local-operation'
    Draft202012Validator(load('authority/artifact-types/implementation/v1/schema.json')).validate(artifact)
    return artifact


def assemble():
    receipt = verify_upstream()
    members = []
    def add(key, category, roles, paths, effect, dependencies=(), extra_exclusions=()):
        members.append({'member_id': 'protocol:C10:' + key, 'member_class': category,
            'proposed_owner_roles': roles, 'actual_answering_principal_ref': None,
            'current_owner_authority_verified': False, 'selected_outcome': None,
            'targets': [binding(p) for p in paths], 'evidence': [binding(RECEIPT)],
            'requested_effect': effect, 'dependencies': ['protocol:C10:' + d for d in dependencies],
            'exclusions': EXCLUSIONS + list(extra_exclusions),
            'invalidation': ['target bytes changed', 'source cut changed', 'evidence changed',
                             'owner authority unavailable or changed', 'new effect or semantic target'],
            'scope': 'Only these exact targets; final S02 assembly and R08 disposition required.'})
    # Generated postimages are targets by exact staged path; their bindings are added by prepare().
    mappings = load(RUNTIME + '/design/contract-impact.json')['endpoint_proposals']
    for row in mappings:
        kind = row['endpoint_kind']
        add('mapping-' + kind, 'semantic-mappings', ['role:definition-owner'],
            [RUNTIME + '/design/contract-impact.json', RUNTIME + '/design/reference-gap-dispositions.md', row['schema_binding']['path']],
            'Admit only the selected ' + kind + ' identity-selector representation; preserve carrier record identity.',
            ('method-type',) if kind == 'method' else (), ['blanket carrier alias', 'semantic noncollapse certification from schema validation'])
        members[-1]['selected_record'] = row
    catalog = load(BOOTSTRAP + '/catalog.snapshot')
    for version, row in sorted(catalog['candidate_subjects'].items()):
        if row['decision_ref'] is not None or row['effective_state'] != 'candidate-unadmitted':
            raise ValueError('candidate catalog claims admission')
        semantic = row['semantic_kind']
        paths = [BOOTSTRAP + '/' + row['path']]
        if semantic == 'artifact-type':
            key = 'method-type'; category = 'carrier-contracts'; roles = ['role:artifact-type-owner']
            paths += [BOOTSTRAP + '/method/schema.json', BOOTSTRAP + '/method/mechanics.json']
            deps = (); effect = 'Admit exact Method carrier and its selected registry entry; instance admission remains independent.'
        elif semantic == 'method':
            key = 'method-instance'; category = 'semantic-instances'; roles = ['role:repository-owner']
            deps = ('method-type', 'mapping-method'); effect = 'Admit this exact repeatable Method specification; applying it requires separate authority.'
        elif semantic == 'implementation':
            key = 'catalog-generator'; category = 'runtime-implementation'; roles = ['role:artifact-type-owner']
            paths += [BOOTSTRAP + '/generator-manifest.json', BOOTSTRAP + '/environment-contract.json']
            deps = ('method-type',); effect = 'Admit exact catalog generator Implementation and frozen code binding; no activation.'
        else:
            key = Path(row['path']).stem; category = 'typed-connections'; roles = ['role:identity-graph-owner']
            if key == 'generator-realizes-capability': deps = ('catalog-generator',)
            elif key == 'project-uses-method': deps = ('mapping-project', 'method-instance')
            elif key == 'product-uses-method': deps = ('mapping-product', 'method-instance')
            else: raise ValueError('undeclared candidate connection')
            effect = 'Admit only this exact Typed Relation instance under its already declared ordered pair and qualifiers.'
        add(key, category, roles, paths, effect, deps)
        members[-1]['subject_version_ref'] = version
        members[-1]['selected_record'] = row['record']
    add('context-generator', 'runtime-implementation', ['role:repository-owner'],
        [CONTEXT + '/implementation_record.json', CONTEXT + '/generator-manifest.json'],
        'Admit the exact context generator Implementation; Session projections remain ephemeral and candidate until independently governed.')
    add('context-realizes-capability', 'typed-connections', ['role:identity-graph-owner'],
        [CONTEXT + '/realization_record.json'], 'Admit the exact existing realizes pair; no Capability Realization Binding adoption.',
        ('context-generator',))
    add('successor-runtime', 'runtime-implementation', ['role:repository-owner'],
        [INTEGRATION + '/packages/0001/manifest.json', INTEGRATION + '/packages/0001/selection.json'],
        'Admit this exact C09 successor implementation closure; frozen v1/v2 remain historical.',
        ('source-profile',), ['general trusted API completion', 'Product SLA'])
    add('source-profile', 'source-selection', ['role:repository-owner'],
        [RUNTIME + '/profiles/selections.json'] + [RUNTIME + '/profiles/d75/' + name for name in ('profile.json', 'policy.json', 'selection-review.json', 'content-manifest.json')],
        'Select only the exact D75 source/profile/capture policy for this implementation; no silent rebase or old signature carry.',
        (), ['live-store migration', 'admission of source declarations', 'D74 profile activation'])
    if len(members) != 13: raise ValueError('incomplete C10 member inventory')
    return {'schema_version': 'lab-C10-member-preparation/v1-candidate', 'task': 'C10',
        'authority_effect': 'none', 'status': 'candidate-preparation',
        'actual_owner_outcome': None, 'actual_answering_principal_ref': None,
        'final_checkpoint': 'R08', 'application_task': 'A01', 'atomicity': 'final all-or-nothing admission bundle only; local actions are separate',
        'members': members, 'evidence': binding(RECEIPT),
        'observed_example': binding(INTEGRATION + '/receipts/C09/0001/observed-predecision-example.json'),
        'retained_performance_posture': receipt['performance_posture'],
        'final_assembly_obligations': ['complete remaining workflow, ontology, adoption, action and release members',
            'verify actual answering principal authority for every proposed role',
            'revalidate exact source epochs and target/evidence bindings',
            'materialize exact admitted registry and transaction postimages with independently scoped Decision cores',
            'derive deterministic Project State, histories and indexes in the same transaction; no second checkpoint',
            'invalidate readiness on rejection or revision; do not partially admit the final bundle'],
        'claim_ceiling': 'Thirteen scoped C10 preparation members only; not a Decision Bundle, owner response, current authority proof or release.'}


def validate_members(value):
    if value['authority_effect'] != 'none' or value['actual_owner_outcome'] is not None or value['actual_answering_principal_ref'] is not None:
        raise ValueError('preparation cannot carry actual authority')
    ids = [m['member_id'] for m in value['members']]
    if len(ids) != 13 or len(set(ids)) != len(ids):
        raise ValueError('missing or duplicate independent member')
    graph = {m['member_id']: m['dependencies'] for m in value['members']}
    def visit(node, stack):
        if node in stack: raise ValueError('cyclic member dependency')
        if node not in graph: raise ValueError('unresolved member dependency')
        for dep in graph[node]: visit(dep, stack | {node})
    for m in value['members']:
        if m['selected_outcome'] is not None or m['actual_answering_principal_ref'] is not None or m['current_owner_authority_verified']:
            raise ValueError('member fabricated owner outcome or authority')
        if not m['proposed_owner_roles'] or not m['targets'] or not m['evidence'] or not m['requested_effect']:
            raise ValueError('incomplete independent member scope')
        if not set(EXCLUSIONS) <= set(m['exclusions']): raise ValueError('missing effect exclusion')
        verify_rows(m['targets']); verify_rows(m['evidence']); visit(m['member_id'], set())
    return True


def validate_preparation(path, external_sha256):
    raw = read(path)
    if sha(raw) != external_sha256: raise ValueError('independent preparation pin mismatch')
    value = json.loads(raw); validate_members(value)
    expected = assemble()
    parent = PurePosixPath(path).parent.as_posix()
    expected['generated_targets'] = [binding(parent + '/' + name) for name in ('runtime-implementation.json', 'method-registry-candidate.json')]
    for member in expected['members']:
        if member['member_id'] == 'protocol:C10:successor-runtime': member['targets'].append(expected['generated_targets'][0])
        if member['member_id'] == 'protocol:C10:method-type': member['targets'].append(expected['generated_targets'][1])
    if read(parent + '/runtime-implementation.json') != encoded(runtime_artifact()): raise ValueError('changed runtime postimage')
    if read(parent + '/method-registry-candidate.json') != encoded(registry_candidate()): raise ValueError('changed candidate registry postimage')
    if value != expected: raise ValueError('changed or incomplete exact preparation')
    return value
