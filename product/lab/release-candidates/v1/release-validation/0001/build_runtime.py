"""Materialize an independently pinned final runtime draft, never an admission."""
import argparse
import ast
import base64
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import uuid
from datetime import datetime, timezone
from jsonschema import Draft202012Validator

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OUTPUT_BASE = HERE.parent
CAPABILITY = 'product-capability:cyberalchemy-lab:governed-knowledge-lifecycle'
IMPL = ROOT / 'authority/artifact-types/implementation/v1'
HISTORIC = ROOT / 'implementation/lab-review/candidates/v1/packages/0001/runtime-implementation.json'

def need(value, reason):
    if not value:
        raise ValueError(reason)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def read(path):
    path = Path(path)
    need(path.is_file() and not path.is_symlink() and not any(p.is_symlink() for p in path.parents), 'unsafe original custody')
    return path.read_bytes()

def bind(path):
    path = Path(path)
    return {'path': str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path), 'sha256': sha(read(path))}

def load(path):
    def pairs(rows):
        value = {}
        for key, item in rows:
            need(key not in value, 'duplicate JSON key')
            value[key] = item
        return value
    return json.loads(read(path), object_pairs_hook=pairs)

def exact(path, expected):
    need(bind(path)['sha256'] == expected, 'independent input pin differs: ' + str(path))
    return load(path)

def emit(path, value):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write('\n')
    path.chmod(0o600)

def module(name, path, package=False):
    spec = importlib.util.spec_from_file_location(name, path / '__init__.py' if package else path,
        submodule_search_locations=[str(path)] if package else None)
    selected = importlib.util.module_from_spec(spec)
    sys.modules[name] = selected
    spec.loader.exec_module(selected)
    return selected

def declared_source(api):
    """Read the exact selected original archive, retaining both posture axes."""
    namespace = '_final_runtime_source_' + uuid.uuid4().hex
    module(namespace, api, True)
    bridge = __import__(namespace + '.source_bridge', fromlist=['source_selection'])
    selected = bridge.source_selection('source8-session-participation')
    archive = load(ROOT / selected['archive_binding']['path'])
    need(bind(ROOT / selected['archive_binding']['path']) == selected['archive_binding'], 'selected signed archive changed')
    original = archive['files']['baseline.json']
    raw = base64.b64decode(original['base64_original_bytes'], validate=True)
    need(sha(raw) == original['sha256'], 'original captured baseline bytes differ')
    baseline = json.loads(raw)
    need(baseline['snapshot_digest'] == selected['baseline_snapshot_digest'], 'independent baseline cut differs')
    contract = baseline['contracts']['cal.artifact-type.implementation/v1']
    need(contract['semantic_kind'] == 'implementation' and contract['instance_discriminator']['value'] == 'cyberalchemy-lab-implementation/v1', 'actual Implementation declaration differs')
    need(bind(IMPL / 'schema.json') == {'path': contract['schema_path'], 'sha256': contract['schema_sha256']}, 'actual declared Implementation schema differs')
    descriptor = load(IMPL / 'artifact.json')
    need(bind(IMPL / 'artifact.json') == {'path': contract['artifact_path'], 'sha256': contract['artifact_sha256']}, 'actual descriptor bytes differ')
    need(any(r['relation_kind_ref'] == 'relation.realizes' and r['direction'] == 'source'
        and r['counterpart_kinds'] == ['product-capability'] for r in descriptor['relation_roles']), 'new or undeclared realization relation')
    relation = baseline['relation_contracts']['relation.realizes']
    need({'source_kind': 'implementation', 'target_kind': 'product-capability'} in relation['payload']['allowed_endpoint_pairs'], 'undeclared exact ordered pair')
    candidates = [s for s in baseline['subjects'].values() if s['identity'] == CAPABILITY]
    need(len(candidates) == 1 and candidates[0]['carrier_ref'] == 'cal.artifact-type.product-capability/v1', 'actual capability source declaration missing or ambiguous')
    capability = candidates[0]
    need(bind(ROOT / capability['source']['path']) == {'path': capability['source']['path'], 'sha256': capability['source']['sha256']}, 'original capability body differs')
    body = load(ROOT / capability['source']['path'])
    need(body['node_id'] == CAPABILITY and body['kind'] == 'product-capability' and body['product_ref'] == 'product:cyberalchemy-lab', 'capability kind/identity/Product differs')
    return {'source_selection': selected, 'archive_binding': selected['archive_binding'],
        'baseline_original_sha256': original['sha256'], 'implementation_contract': contract,
        'implementation_descriptor_binding': bind(IMPL / 'artifact.json'),
        'implementation_descriptor_body_status': descriptor['status'],
        'implementation_signed_source_eligibility': contract['lifecycle_state'],
        'capability_body_binding': bind(ROOT / capability['source']['path']),
        'capability_version_ref': capability['version_ref'], 'capability_body_status': body['status'],
        'capability_body_lifecycle': body['lifecycle_posture']['status'],
        'capability_signed_source_eligibility': capability['effective_state'],
        'realization_relation_body': relation, 'new_axis_created': False,
        'new_global_typed_relation_created': False, 'new_realization_binding_admitted': False,
        'native_signed_replay_reexecuted_by_this_generator': False}

def build(args):
    api = Path(args.api_directory).resolve()
    boundary = Path(args.boundary_directory).resolve()
    output = Path(args.output_directory).resolve()
    need(api.parent == BASE and api.name.startswith('api-integration-'), 'foreign API family')
    need(output.parent == OUTPUT_BASE and output != OUTPUT_BASE, 'owned release-validation output required')
    need(output.exists() and not any((output / n).exists() for n in ('environment-contract.json', 'runtime-implementation.json', 'review-member.json', 'validation.json')), 'exclusive fresh draft outputs required')
    source = exact(api / 'source-manifest.json', args.api_source_sha256)
    profile = exact(api / 'contract-profile.json', args.api_profile_sha256)
    guard = module('_final_runtime_guard_' + uuid.uuid4().hex, api / 'guard.py')
    guard.verify(args.api_source_sha256)
    boundary_source = exact(boundary / 'source-manifest.json', args.boundary_source_sha256)
    conformance = exact(boundary / 'receipts/conformance-0001.json', args.boundary_conformance_sha256)
    proof = exact(boundary / 'receipts/proof-0001.json', args.boundary_proof_sha256)
    terminals_path = Path(args.boundary_terminals).resolve()
    terminals = exact(terminals_path, args.boundary_terminals_sha256)
    recovery_path = Path(args.host_recovery).resolve()
    recovery = exact(recovery_path, args.host_recovery_sha256)
    boundary_guard = module('_final_boundary_guard_' + uuid.uuid4().hex, boundary / 'build.py')
    boundary_guard.frozen(args.boundary_source_sha256)
    need(boundary_source['api_source_binding'] == bind(api / 'source-manifest.json')
        and conformance['api_profile_binding'] == bind(api / 'contract-profile.json'), 'boundary review selects another family')
    need(conformance['result'] == 'PASS-candidate-preparation' and all(conformance['checks'].values())
        and proof['conformance_binding'] == bind(boundary / 'receipts/conformance-0001.json'), 'actual bounded privacy qualification absent')
    need(terminals['conformance_binding'] == proof['conformance_binding'] and terminals['proof_binding'] == bind(boundary / 'receipts/proof-0001.json'), 'terminal evidence selects another proof')
    need(set(terminals['commands']) == {'freeze', 'proposal', 'check'} and all(x['chunks'][-1]['exit_code'] == 0 for x in terminals['commands'].values()), 'actual zero-exit terminals missing')
    for row in proof['files']:
        need(bind(ROOT / row['path']) == row, 'retained boundary proof input changed')
    active = load(api / 'SCHEMA-EXECUTION-DEPENDENCIES.json')
    source_rows = {r['path']: r for r in source['files']}
    need(all(source_rows.get(r['path']) == r for r in profile['files'] + active['files']), 'profile/active closure is outside full source')
    selection = load(boundary / 'payload-selection.json')
    need(selection['api_source_binding'] == bind(api / 'source-manifest.json') and selection['api_profile_binding'] == bind(api / 'contract-profile.json'), 'public payload selects another family')
    native = load(boundary / 'native-remediation.json')
    need(recovery['result'] == 'PASS' and recovery['native_binding'] == native['original_binding']
        and recovery['native_mode'] == '0o755' and recovery['old_private_keys_or_sessions_restored'] is False, 'current host recovery differs')
    native_path = Path(native['original_binding']['path'])
    need(bind(native_path) == native['original_binding'] and stat.S_IMODE(native_path.stat().st_mode) == 0o755, 'current signed native locator/hash/mode differs')
    for row in native['host_ABI_library_bindings']:
        need(bind(Path(row['path'])) == row, 'current host ABI bytes differ')
    boundary_guard.C.environment_guard(native['expected_R02_environment'])
    declarations = declared_source(api)
    catalog = load(ROOT / profile['original_operation_catalog_binding']['path'])
    need(set(profile['implemented_operations']) == {r['operation'] for r in catalog['operations']} and len(profile['implemented_operations']) == 34, 'complete original operation declaration differs')
    dispatcher_ast = ast.parse(read(api / 'integration_dispatch.py'))
    need(any(isinstance(n, ast.ClassDef) and n.name == 'IntegrationService' and any(isinstance(f, ast.FunctionDef) and f.name == 'call' for f in n.body) for n in dispatcher_ast.body), 'actual composed public callable absent')
    historic = bind(HISTORIC)
    environment = {'schema_version': 'lab-final-runtime-environment-contract/v1-candidate',
        'API_source_binding': bind(api / 'source-manifest.json'), 'API_profile_binding': bind(api / 'contract-profile.json'),
        'schema_execution_binding': bind(api / 'SCHEMA-EXECUTION-DEPENDENCIES.json'),
        'complete_source_bindings': source['files'], 'complete_profile_bindings': profile['files'],
        'schema_execution_bindings': active['files'], 'source_rows': len(source['files']),
        'profile_rows': len(profile['files']), 'schema_execution_rows': len(active['files']),
        'public_payload_binding': selection['payload_binding'], 'public_payload_members': selection['payload_members'],
        'public_payload_file_bindings': selection['payload_files'], 'protected_dependencies': [r for r in load(boundary / 'dependency-dispositions.json')['rows'] if not r['public_payload_proposed']],
        'boundary_source_binding': bind(boundary / 'source-manifest.json'), 'boundary_conformance_binding': bind(boundary / 'receipts/conformance-0001.json'),
        'boundary_proof_binding': bind(boundary / 'receipts/proof-0001.json'), 'boundary_actual_terminal_binding': bind(terminals_path),
        'current_host_recovery_binding': bind(recovery_path), 'host_native_binding': native['original_binding'],
        'host_native_mode': '0o755', 'host_ABI_library_bindings': native['host_ABI_library_bindings'],
        'R02_environment': native['expected_R02_environment'], 'offline_environment_wheel_bindings': recovery['wheel_bindings'],
        'composite_python_entrypoint': str((api / 'integration_dispatch.py').relative_to(ROOT)) + '#IntegrationService.call',
        'composite_operations': profile['implemented_operations'], 'independently_authenticated_branch_selection_binding': profile['integration_members_binding'],
        'base_stdio_entrypoint': str((api / 'serve.py').relative_to(ROOT)), 'base_stdio_operation_count': 28,
        'composite_stdio_driver_materialized': False, 'protected_repository_and_host_dependencies_required': True,
        'historical_C10_C09_implementation_binding': historic, 'old_implementation_mutated': False,
        'implicit_global_successor_selected': False, 'source_declaration_observations': declarations,
        'whole_API_qualified': False, 'complete_original_regression_qualified': False, 'human_pilot_observed': False,
        'runtime_activations': 0, 'authority_effect': 'none', 'actual_owner_outcome': None}
    emit(output / 'environment-contract.json', environment)
    record = {'schema_version': 'cyberalchemy-lab-implementation/v1',
        'node_id': 'implementation:cyberalchemy-lab:final-common-operator:' + api.name,
        'kind': 'implementation', 'name': 'Proposed exact composed local Lab operator',
        'lifecycle_state': 'candidate', 'authority_effect': 'none', 'owner_ref': 'role:repository-owner',
        'scope_ref': 'protocol:lab-final-review:S02',
        'evidence_refs': [str((boundary / 'receipts/conformance-0001.json').relative_to(ROOT)), str(terminals_path.relative_to(ROOT))],
        'challenge_route': 'challenge-contract:cyberalchemy-lab-operational-foundation', 'successor_refs': [],
        'relation_refs': [{'relation_kind_ref': 'relation.realizes', 'direction': 'source',
            'counterpart_kind': 'product-capability', 'counterpart_ref': CAPABILITY}],
        'payload': {'implementation_kind': 'candidate-composed-Python-operator-with-independent-authenticated-branches',
            'conforms_to_schema_refs': [str((api / 'schemas/api-call.schema.json').relative_to(ROOT)), str((api / 'schemas/api-reply.schema.json').relative_to(ROOT))],
            'realizes_capability_refs': [CAPABILITY], 'execution_entrypoint_ref': environment['composite_python_entrypoint'],
            'environment_contract_ref': str((output / 'environment-contract.json').relative_to(ROOT))},
        'claim_ceiling': 'Proposed realization and exact callable/dependency draft only. Schema validity and 34 authored operation declarations do not establish complete qualification, owner admission, human pilot, activation, broad efficacy or Product value. Base stdio reader covers 28 operations; full composition uses independently authenticated Python branches.'}
    Draft202012Validator(load(IMPL / 'schema.json')).validate(record)
    emit(output / 'runtime-implementation.json', record)
    member = {'member_id': 'protocol:S02:final-common-operator:' + api.name, 'member_class': 'runtime-implementation',
        'targets': [bind(output / 'runtime-implementation.json')],
        'evidence': [bind(output / 'environment-contract.json'), historic, bind(boundary / 'receipts/conformance-0001.json'), bind(terminals_path)],
        'postimage_binding': bind(output / 'runtime-implementation.json'), 'carrier_schema_binding': bind(IMPL / 'schema.json'),
        'carrier_descriptor_binding': bind(IMPL / 'artifact.json'), 'requested_effect': 'Review the exact proposed composed Implementation realization only; no activation, private grant, new global relation or broad release effect.',
        'proposed_owner_roles': ['role:repository-owner'], 'actual_answering_principal_ref': None,
        'current_owner_authority_verified': False, 'selected_outcome': None,
        'final_target_operation_selection': None, 'final_decision_core_binding': None,
        'dependencies': [], 'unresolved_representation_inputs': [bind(output / 'environment-contract.json')],
        'environment_contract_is_protocol_only': True, 'original_C10_C09_independently_retained': historic,
        'actual_owner_outcome': None, 'authority_effect': 'none'}
    emit(output / 'review-member.json', member)
    guard.verify(args.api_source_sha256)
    boundary_guard.frozen(args.boundary_source_sha256)
    validation = {'schema_version': 'lab-final-runtime-draft-validation/v1-candidate', 'result': 'PASS-draft',
        'checked_at': datetime.now(timezone.utc).isoformat(), 'generator_binding': bind(Path(__file__)),
        'implementation_binding': bind(output / 'runtime-implementation.json'),
        'environment_contract_binding': bind(output / 'environment-contract.json'), 'additional_member_binding': bind(output / 'review-member.json'),
        'original_Implementation_v1_schema_binding': bind(IMPL / 'schema.json'),
        'full_API_and_boundary_entry_exit_guards': True, 'original_Implementation_schema_validation': True,
        'new_axis_or_global_relation_created': False, 'native_process_executed': False,
        'canonical_admissions': 0, 'owner_authority_resolved': False, 'whole_API_qualified': False,
        'human_pilot_observed': False, 'ready_for_R08': False, 'task_complete': False,
        'authority_effect': 'none', 'actual_owner_outcome': None, 'goal_complete': False}
    emit(output / 'validation.json', validation)
    print(json.dumps({'result': validation['result'], 'validation_binding': bind(output / 'validation.json'),
        'implementation_binding': bind(output / 'runtime-implementation.json'), 'source_rows': len(source['files']),
        'profile_rows': len(profile['files']), 'active_rows': len(active['files']), 'public_members': selection['payload_members']}), flush=True)

def main():
    parser = argparse.ArgumentParser()
    for name in ('api-directory', 'api-source-sha256', 'api-profile-sha256', 'boundary-directory',
        'boundary-source-sha256', 'boundary-conformance-sha256', 'boundary-proof-sha256',
        'boundary-terminals', 'boundary-terminals-sha256', 'host-recovery', 'host-recovery-sha256'):
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--output-directory', default=str(HERE))
    build(parser.parse_args())

if __name__ == '__main__':
    main()
