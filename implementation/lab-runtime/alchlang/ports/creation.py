"""Inert draft creation using the original Lab carrier/schema and proposal checks.

No key loading, approval signing, admission, registry mutation or native HEAD write.
"""
from __future__ import annotations
import copy
import os
from pathlib import Path
import sys

MODEL = Path(__file__).resolve().parents[1]
REPO = MODEL.parents[2]
NATIVE = REPO / 'implementation/lab-runtime/v2'
sys.path.insert(0, str(NATIVE))
from lab_runtime.common import RuntimeFault, byte_digest, digest, encoded, fsync_dir, identity, load, require, sealed, verify_seal
from lab_runtime.operations import current_contract, prepare, validate_record, protocol_check
from lab_runtime.store import Store
from lab_runtime.sources import validate_schema
from lab_runtime.protocols import CONTRACT_BINDING_SCHEMA

ARTIFACT_TYPE_CARRIER = 'cal.artifact-type.artifact-type/v3'
DEFINITION_CARRIER = 'cal.artifact-type.definition/v2'
DERIVED = {'project-state', 'project-semantic-event-history', 'project-governance-event-history', 'admission-transaction'}
MAX_BODY_BYTES = 8 * 1024 * 1024


def binding(raw, name):
    return {'path': name, 'sha256': byte_digest(raw), 'bytes': len(raw), 'digest_kind': 'original-file-sha256'}


def selected_sources():
    for name, expected in load(MODEL / 'native-source.json')['files'].items():
        require(byte_digest((REPO / name).read_bytes()) == expected, 'native-source-drift: ' + name)


def schema_material(data, contract):
    """Bind a frozen file or a schema reconstructed from a verified native transaction."""
    path = contract['schema_path']
    document = data['projection']['documents'][path]
    for tx in reversed(data['transactions'][1:]):
        if path in tx['proposal']['schemas']:
            require(tx['proposal']['schemas'][path] == document, 'creation-committed-schema-mismatch')
            raw = encoded(document)
            require(byte_digest(raw) == contract['schema_sha256'], 'creation-carrier-schema-binding-mismatch')
            return {**binding(raw, path), 'digest_kind': 'native-json-sha256',
                    'selector': contract.get('schema_selector'), 'provenance_digest': tx['digest']}
    schema_file = REPO / path
    require(schema_file.is_file(), 'creation-original-carrier-schema-required')
    raw = schema_file.read_bytes()
    require(byte_digest(raw) == contract['schema_sha256'] and load(schema_file) == document,
            'creation-carrier-schema-binding-mismatch')
    return {**binding(raw, path), 'selector': contract.get('schema_selector'),
            'provenance_digest': data['baseline']['snapshot_digest']}


def read_original(path):
    path = Path(path)
    require(path.is_file(), 'creation-source-required')
    raw = path.read_bytes()
    require(0 < len(raw) <= MAX_BODY_BYTES, 'creation-body-byte-limit')
    body = load(path)
    require(path.read_bytes() == raw, 'creation-source-changed-during-read')
    require(isinstance(body, dict), 'creation-body-object-required')
    return raw, body


def draft_from_file(data, source, *, kind, project, scope, work, carrier, version, decision, schema_source=None, contract_source=None, owner=None):
    """Return an inert candidate and its complete original native target; no writes."""
    require(kind in ('definition', 'record', 'artifact-type'), 'unknown-creation-kind')
    require(scope in ('project', 'work'), 'invalid-draft-scope')
    require(scope != 'work' or isinstance(work, str) and bool(work), 'work-required')
    require(scope != 'project' or work is None, 'project-scope-has-work')
    require(data['freshness']['status'] == 'current', 'source-stale')
    branch_project = data['projection']['state']['payload']['project_ref']
    require(project == branch_project, 'project-mismatch')
    require(isinstance(decision, str) and bool(decision), 'decision-reference-required')
    raw, body = read_original(source)
    contract = current_contract(data['projection'], carrier)
    semantic_kind = contract['semantic_kind']
    identity_field = contract['artifact'].get('instance_contract', {}).get('identity_field')
    if kind == 'artifact-type':
        require(carrier == ARTIFACT_TYPE_CARRIER and semantic_kind == 'artifact-type', 'artifact-type-carrier-required')
        validate_schema(body, contract['schema_path'], '#/properties/registered_types/items', data['projection']['documents'])
        ident = body['artifact_type_ref'].rsplit('/', 1)[0]
    else:
        validate_record(body, carrier, data['projection'])
        ident = identity(body, identity_field)
    require(isinstance(ident, str) and bool(ident), 'creation-identity-required')
    require(not any(entry['identity'] == ident for entry in data['projection']['subjects'].values()), 'creation-identity-exists')
    require(semantic_kind not in DERIVED, 'creation-derived-target')
    if kind == 'definition':
        require(carrier == DEFINITION_CARRIER and semantic_kind == 'definition', 'definition-carrier-required')
        exact_version = ident + '@' + body['version']
        require(version is None or version == exact_version, 'definition-version-mismatch')
        version = exact_version
        owner = body['semantic_owner_ref']
        candidate = body['classification']['lifecycle_posture_ref'] == 'CAL-LIFECYCLE-DEFINITION-V1:candidate-authored'
        require(candidate, 'creation-requires-candidate')
        require(body['schema_digest'] == contract['schema_sha256'], 'definition-schema-binding-mismatch')
        category = 'definition'
        location = 'ProjectDefinitions' if scope == 'project' else 'WorkDefinitions'
    elif kind == 'artifact-type':
        require(isinstance(owner, str) and bool(owner), 'artifact-type-owner-required')
        require(version is None or version == body['artifact_type_ref'], 'artifact-type-version-mismatch')
        version = body['artifact_type_ref']
        require(schema_source is not None and contract_source is not None, 'artifact-type-schema-and-contract-required')
        schema_raw, schema_doc = read_original(schema_source)
        contract_raw, native_contract = read_original(contract_source)
        protocol_check(native_contract, CONTRACT_BINDING_SCHEMA)
        path = native_contract['schema_path']
        # Native schema-package path immutability and contract/descriptor agreement are checked by prepare_bundle.
        require(native_contract['schema_sha256'] == byte_digest(encoded(schema_doc)), 'artifact-type-schema-digest-mismatch')
        documents = {**data['projection']['documents'], path: schema_doc}
        try:
            validate_schema({}, path, native_contract['schema_selector'], documents)
        except RuntimeFault as error:
            # A dummy instance can fail required fields; schema/closure/resolution failures cannot pass.
            if not str(error).startswith('schema invalid: '):
                raise
        candidate = False  # Draft status is metadata; the closed native descriptor has no lifecycle field.
        category, location = 'artifact-type', 'ArtifactTypes'
    else:
        require(semantic_kind != 'definition', 'use-definition-creation')
        require(semantic_kind not in {'typed-relation', 'artifact-type', 'relation-kind'}, 'use-specialized-creation')
        require(isinstance(version, str) and version.startswith(ident + '@') and len(version) > len(ident) + 1, 'explicit-record-version-required')
        owner = body.get('owner_ref')
        require(isinstance(owner, str) and bool(owner), 'record-owner-required')
        candidate = body.get('lifecycle_state') == 'candidate'
        category, location = 'artifact-instance', 'RecordOutputs'
        if semantic_kind == 'work':
            require(body['payload']['project_ref'] == project, 'record-project-mismatch')
    require(version not in data['projection']['subjects'], 'creation-version-exists')
    name = {'definition': 'definition.json', 'record': 'record.json', 'artifact-type': 'artifact-type.json'}[kind]
    original = binding(raw, name)
    schema = schema_material(data, contract)
    target = {'category': category, 'operation': 'admit', 'version_ref': version, 'carrier_ref': carrier,
              'record': copy.deepcopy(body), 'predecessor_ref': None, 'decision_ref': decision, 'contract': native_contract if kind == 'artifact-type' else None}
    validation = {'source': original, 'carrier': carrier, 'carrier_schema': schema, 'identity_ref': ident, 'version': version,
                  'owner': owner, 'semantic_kind': semantic_kind, 'project': project, 'head': data['head']['transaction_digest'],
                  'snapshot': data['baseline']['snapshot_digest'], 'current_carrier': True, 'schema_valid': True,
                  'identity_available': True, 'candidate_payload': candidate, 'authored_target': True}
    request = {'project': project, 'scope': scope, 'work': work, 'identity_ref': ident, 'version': version, 'owner': owner,
               'decision': decision, 'carrier': carrier, 'source': original, 'validation': validation}
    draft = {'project': project, 'scope': scope, 'work': work, 'identity_ref': ident, 'owner': owner, 'location': location,
             'target': {'category': category, 'effect': 'admit', 'version': version, 'carrier': carrier, 'predecessor': None,
                        'decision': decision, 'authored_record': original, 'contract': target['contract']}, 'schemas': [], 'status': 'candidate', 'authority_effect': 'none'}
    result = {'kind': kind, 'request': request, 'draft': draft, 'target': target, 'body_name': name, 'raw': raw,
              'identity_field': identity_field, 'schemas': {}, 'extra_files': {}}
    if kind == 'artifact-type':
        material = {**binding(encoded(schema_doc), path), 'selector': native_contract['schema_selector'],
                    'digest_kind': 'native-json-sha256', 'provenance_digest': byte_digest(schema_raw)}
        draft['schemas'] = [material]
        result.update(schemas={path: schema_doc}, extra_files={'schema.json': schema_raw, 'contract.json': contract_raw},
                      artifact_type_request={'creation': request, 'schema_source': binding(schema_raw, 'schema.json'),
                                             'contract_source': binding(contract_raw, 'contract.json'),
                                             'schema': material, 'contract': native_contract, 'registration_valid': True})
    return result


def prepare_bundle(data, drafts, proposal_id):
    require(isinstance(proposal_id, str) and bool(proposal_id), 'proposal-id-required')
    require(1 <= len(drafts) <= 16, 'creation-target-limit')
    require(all(draft['request']['project'] == data['projection']['state']['payload']['project_ref'] and
                draft['request']['validation']['head'] == data['head']['transaction_digest'] and
                draft['request']['validation']['snapshot'] == data['baseline']['snapshot_digest'] for draft in drafts), 'creation-validation-stale')
    schemas = {}
    for draft in drafts:
        for path, schema in draft.get('schemas', {}).items():
            require(path not in schemas or schemas[path] == schema, 'creation-schema-conflict')
            schemas[path] = schema
    cfg = data['config']
    proposal = {'schema_version': 'lab-runtime-proposal/v1', 'proposal_id': proposal_id,
                'expected_head': data['head']['transaction_digest'], 'source_snapshot_digest': data['baseline']['snapshot_digest'],
                'scope_ref': cfg['scope_ref'], 'policy_ref': cfg['policy_ref'], 'challenge_route': cfg['challenge_route'],
                'targets': [draft['target'] for draft in drafts], 'schemas': schemas}
    # Original whole-bundle staging/schema/relation/Decision checks, without approval or commit.
    prepare(data['projection'], proposal, data['head']['transaction_digest'], cfg)
    return proposal


def inspect_creation(directory):
    directory = Path(directory)
    require(not directory.is_symlink(), 'unsafe-creation-output')
    receipt_path = directory / 'creation.json'
    require(receipt_path.is_file() and not receipt_path.is_symlink(), 'creation-publication-incomplete: inspect existing output; no overwrite')
    receipt = load(receipt_path)
    verify_seal(receipt)
    require(receipt.get('schema_version') == 'cal.lab.creation-draft/v1' and receipt.get('authority_effect') == 'none' and receipt.get('status') == 'candidate', 'invalid-creation-receipt')
    require(set(p.name for p in directory.iterdir()) == set(receipt['files']) | {'creation.json'}, 'creation-file-inventory-mismatch')
    for name, expected in receipt['files'].items():
        require(name in ('definition.json', 'record.json', 'artifact-type.json', 'schema.json', 'contract.json', 'proposal.json'), 'invalid-creation-file')
        path = directory / name
        require(path.is_file() and not path.is_symlink(), 'unsafe-creation-file')
        require(binding(path.read_bytes(), name) == expected, 'creation-original-byte-mismatch')
    proposal = load(directory / 'proposal.json')
    require('approval' not in proposal and 'signature' not in proposal, 'creation-must-be-unsigned')
    body_name = next(name for name in ('definition.json', 'record.json', 'artifact-type.json') if name in receipt['files'])
    body = load(directory / body_name)
    require(len(proposal.get('targets', [])) == 1, 'creation-target-inventory-mismatch')
    target = proposal['targets'][0]
    request = receipt['creation_request']
    require(target['record'] == body and target['operation'] == 'admit' and target['predecessor_ref'] is None, 'creation-proposal-body-mismatch')
    require(target['version_ref'] == request['version'] and target['carrier_ref'] == request['carrier'] and target['decision_ref'] == request['decision'], 'creation-target-binding-mismatch')
    if body_name == 'artifact-type.json':
        require(target['contract'] == load(directory / 'contract.json'), 'creation-contract-binding-mismatch')
        schema = load(directory / 'schema.json')
        c = target['contract']
        require(proposal['schemas'] == {c['schema_path']: schema} and c['schema_sha256'] == byte_digest(encoded(schema)), 'creation-schema-binding-mismatch')
        require(receipt['artifact_type_request']['contract'] == c and receipt['artifact_type_request']['creation'] == request,
                'creation-registration-binding-mismatch')
        ident = body['artifact_type_ref'].rsplit('/', 1)[0]
        owner = request['owner']  # Explicit draft steward, not a field invented in the native descriptor.
    else:
        require(target['contract'] is None and proposal['schemas'] == {}, 'creation-unexpected-contract')
        ident = identity(body, receipt.get('identity_field'))
        owner = body['semantic_owner_ref'] if body_name == 'definition.json' else body['owner_ref']
    require(receipt['draft']['identity_ref'] == request['identity_ref'] == ident, 'creation-identity-binding-mismatch')
    require(receipt['draft']['owner'] == request['owner'] == owner, 'creation-owner-binding-mismatch')
    require(receipt['project'] == request['project'] == receipt['draft']['project'], 'creation-project-binding-mismatch')
    require(request['source'] == receipt['files'][body_name] and receipt['draft']['target']['authored_record'] == receipt['files'][body_name], 'creation-source-binding-mismatch')
    require(proposal['expected_head'] == receipt['expected_head'] and proposal['source_snapshot_digest'] == receipt['source_snapshot'], 'creation-envelope-binding-mismatch')
    return receipt


def _write_exclusive(path, raw):
    with path.open('xb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def create_draft(store, source, *, kind, project, scope, work, carrier, version, decision, proposal_id, output, schema_source=None, contract_source=None, owner=None):
    """Publish only a candidate asset, unsigned native proposal and integrity receipt."""
    selected_sources()
    data = store.replay(require_current=True)
    source = Path(source)
    raw, _ = read_original(source)
    extras = {}
    if kind == 'artifact-type':
        require(schema_source is not None and contract_source is not None, 'artifact-type-schema-and-contract-required')
        extras = {'schema.json': read_original(schema_source)[0], 'contract.json': read_original(contract_source)[0]}
    request_identity = {'config_digest': digest(data['config']), 'kind': kind, 'project': project, 'scope': scope, 'work': work,
                        'carrier': carrier, 'version': version, 'decision': decision, 'proposal_id': proposal_id, 'body_sha256': byte_digest(raw)}
    if kind == 'artifact-type':
        request_identity.update(owner=owner, extras={name: byte_digest(value) for name, value in extras.items()})
    request_key = digest(request_identity)
    output = Path(output).absolute()
    require(output.resolve() == output and not output.is_symlink(), 'unsafe-creation-output')
    require(not output.is_relative_to(store.path), 'creation-output-inside-native-store')
    if output.exists():
        prior = inspect_creation(output)
        require(prior['request_digest'] == request_key, 'creation-output-conflict')
        name = {'definition': 'definition.json', 'record': 'record.json', 'artifact-type': 'artifact-type.json'}[kind]
        require(prior['files'].get(name) == binding(raw, name), 'creation-output-differs-from-requested-original')
        return {'outcome': 'replayed', 'directory': str(output), 'receipt': prior, 'authority_effect': 'none'}
    draft = draft_from_file(data, source, kind=kind, project=project, scope=scope, work=work, carrier=carrier, version=version, decision=decision,
                            schema_source=schema_source, contract_source=contract_source, owner=owner)
    proposal = prepare_bundle(data, [draft], proposal_id)
    require(draft['raw'] == raw and source.read_bytes() == raw, 'creation-source-changed-before-publication')
    require(draft['extra_files'] == extras, 'creation-registration-input-changed')
    require(all(Path(path).read_bytes() == extras[name] for path, name in [(schema_source, 'schema.json'), (contract_source, 'contract.json')] if path is not None), 'creation-registration-source-changed')
    contents = {draft['body_name']: draft['raw'], **extras, 'proposal.json': encoded(proposal)}
    files = {name: binding(value, name) for name, value in contents.items()}
    receipt = sealed({'schema_version': 'cal.lab.creation-draft/v1', 'status': 'candidate', 'authority_effect': 'none',
                      'repository_admission_effect': 'none', 'store_id': data['config']['store_id'], 'project': project,
                      'identity_field': draft['identity_field'], 'artifact_type_request': draft.get('artifact_type_request'),
                      'request_digest': request_key, 'draft': draft['draft'], 'creation_request': draft['request'], 'files': files,
                      'expected_head': proposal['expected_head'], 'source_snapshot': proposal['source_snapshot_digest'],
                      'approval_required': True, 'registry_updated': False,
                      'native_record_sha256': byte_digest(encoded(draft['target']['record'])),
                      'transformation': 'explicit-original-json-to-native-record; original bytes retained'})
    require(store.replay(require_current=True)['head'] == data['head'], 'creation-head-changed-before-publication')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.mkdir(mode=0o700)
    try:
        for name, value in contents.items():
            _write_exclusive(output / name, value)
        fsync_dir(output)
        # Receipt is the visibility marker. Existing incomplete output is never overwritten.
        _write_exclusive(output / 'creation.json', encoded(receipt))
        fsync_dir(output)
        fsync_dir(output.parent)
    except BaseException as error:
        raise RuntimeFault('creation-publication-outcome-unknown: inspect ' + str(output)) from error
    inspect_creation(output)
    return {'outcome': 'created', 'directory': str(output), 'receipt': receipt, 'authority_effect': 'none'}
