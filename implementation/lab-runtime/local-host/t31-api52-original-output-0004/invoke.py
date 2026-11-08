"""Select the actual current context.get producer and one private late invocation.

This module prepares and dispatches only inside an already authenticated,
test-owned fixture. It does not declare canonical authority or Work completion.
"""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v52-t31-agent-context-guard-0003'
SOURCE_SHA = 'd14fc1c7e1a4bc941873a5b7fc0adb2dcd95ca16383788df25055e6ee5bb9b72'
ADAPTER = ROOT / 'implementation/lab-runtime/local-host/t31-api52-original-output-bootstrap-0003/bootstrap.py'
ADAPTER_SHA = '1396f1a67865a41f9043db638799a09a6b8e18b40d0f926df8c686d17f2f21c6'
REF = 'transition:agent-context:context-ready'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def selected_public(binding, rows):
    if (type(binding) is not dict or set(binding) != {'path', 'sha256'} or
            (binding['path'], binding['sha256']) not in rows):
        raise ValueError('public binding absent from selected Source')
    path = ROOT / binding['path']
    if (not path.is_relative_to(ROOT) or path.is_symlink() or
            any(parent.is_symlink() for parent in path.parents)):
        raise ValueError('selected public path detached')
    raw = path.read_bytes()
    if sha(raw) != binding['sha256']:
        raise ValueError('selected public byte changed')
    return raw


def selected_adapter():
    if sha(ADAPTER.read_bytes()) != ADAPTER_SHA:
        raise ValueError('selected original-object assembler changed')
    spec = importlib.util.spec_from_file_location('_cal_t31_api50_assembler', ADAPTER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if sha(ADAPTER.read_bytes()) != ADAPTER_SHA:
        raise ValueError('selected assembler changed during import')
    return module


def source_rows():
    path = API / 'source-manifest.json'
    if sha(path.read_bytes()) != SOURCE_SHA:
        raise ValueError('selected API52 manifest changed')
    manifest = json.loads(path.read_bytes())
    rows = {(row['path'], row['sha256']) for row in manifest['files']}
    if len(rows) != len(manifest['files']) or len(rows) != 209:
        raise ValueError('closed selected API52 source rows required')
    return rows


def install_factory(fixture):
    protocol = fixture['protocol']
    name = protocol.__package__
    rows = source_rows()
    modules = {}
    for key in ('api_outputs', 'stage_producers', 'native_outputs',
                'ontology_outputs', 'migration_outputs', 'product_outputs',
                'original_resolvers', 'response_outputs'):
        modules[key] = __import__(name + '.workflow_' + key, fromlist=['*'])
    factory_module = __import__(name + '.workflow_output_factory', fromlist=['install_invocations'])
    return selected_adapter().assemble(
        fixture['service'], fixture['service'].completion_bridge, factory_module,
        modules=modules, read_public=lambda binding: selected_public(binding, rows),
        source_rows=rows)


def write_selected(root, relative, raw, atomic):
    destination = root / relative
    if destination.exists():
        raise ValueError('late private input already exists')
    atomic(destination, raw)
    info = os.stat(destination, follow_symlinks=False)
    if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o600:
        raise ValueError('late private input owner/mode differs')
    return {'path': relative, 'identity': [info.st_dev, info.st_ino, info.st_uid, 0o600],
            'sha256': sha(raw)}


def prepare(fixture, factory):
    """Create the exact one-shot late packet from this actual producer request."""
    protocol = fixture['protocol']
    package = protocol.__package__
    workspace = __import__(package + '.workspace', fromlist=['atomic'])
    producer = fixture['producer_service']
    context_module = __import__(package + '.current_legacy_context_sessions', fromlist=['D'])
    output_module = __import__(package + '.workflow_api_outputs', fromlist=['AuthorizedAPIProducer'])
    producer_outputs = __import__(package + '.workflow_producer_outputs', fromlist=['invocation_arguments'])
    source = fixture['view'].legacy_signed_sources
    message = context_module.D.query(source, producer.sessions.bridge)
    message['budget'].update(max_input_bytes=65536, max_output_bytes=1048576)
    request = fixture['fixtures'].call(fixture['producer_context'], 'lab.status', fixture['source_cut'])
    request.update(operation='context.get', message=message)
    raw_request = protocol.compact(request)
    plan = fixture['output_plan']
    route = plan['transitions'][REF]
    service_path = (API / 'service.py').relative_to(ROOT).as_posix()
    pins = {pin for path, pin in factory.source_rows if path == service_path}
    if len(pins) != 1:
        raise ValueError('exact original API service method absent')
    control = {
        'schema_version': 'lab-private-authorized-API-output/v1-candidate',
        'original_method_binding': {'path': service_path, 'sha256': next(iter(pins))},
        'producer_policy_binding': {'ref': str(fixture['producer_policy_path']),
                                    'sha256': fixture['producer_policy_sha']},
        'producer_source_binding': {'path': (API / 'source-manifest.json').relative_to(ROOT).as_posix(),
                                    'sha256': SOURCE_SHA},
        'operation': 'context.get', 'authority_effect': 'none'}
    from jsonschema import Draft202012Validator
    Draft202012Validator(json.loads((API / 'workflow-stage-controls.schema.json').read_bytes())).validate(control)
    control_raw = protocol.compact(control)
    control_binding = {'ref': 'private:T31:api-context:producer-control',
                       'sha256': sha(control_raw)}
    root = fixture['owned_root'] / 'late-invocation-inputs'
    materials = []
    for index, (binding, raw) in enumerate((
            (fixture['run_binding'], fixture['materials'][fixture['run_binding']['ref']]),
            (fixture['definition_binding'], fixture['materials'][fixture['definition_binding']['ref']]),
            (control_binding, control_raw))):
        selector = write_selected(root, f'materials/{index:02d}.json', raw, workspace.atomic)
        materials.append({'binding': copy.deepcopy(binding), 'selector': selector})
    dummy = object.__new__(output_module.AuthorizedAPIProducer)
    _, input_seal = producer_outputs.invocation_arguments(
        dummy.invoke, (raw_request,), None,
        {'run_binding': fixture['run_binding'],
         'work_ref': fixture['headers']['work']['version_ref'],
         'source_cut': fixture['source_cut']})
    packet = {
        'schema_version': 'lab-private-late-workflow-invocation/v1-candidate',
        'invocation_ref': route['invocation_ref'], 'transition_refs': [REF],
        'principal_ref': fixture['policy']['principal_ref'],
        'scope_ref': fixture['grant']['scope_ref'],
        'source_cut': fixture['source_cut'],
        'run_binding': fixture['run_binding'],
        'work_ref': fixture['headers']['work']['version_ref'],
        'producer_binding': route['producer_binding'],
        'producer_entrypoint': route['producer_entrypoint'],
        'producer_control_binding': control_binding,
        'scope_contract_bindings': {REF: None},
        'input_seal': input_seal,
        'object_lineage': {'kind': 'original-API-request',
                           'request_sha256': sha(raw_request),
                           'operation': 'context.get'},
        'run_material_binding': fixture['run_binding'],
        'materials': materials, 'authority_effect': 'none'}
    schema = json.loads((API / 'workflow-output-plan.schema.json').read_bytes())['$defs']['late_invocation']
    Draft202012Validator(schema).validate(packet)
    selected = write_selected(root, 'invocations/api-context.json',
                              protocol.compact(packet), workspace.atomic)
    return selected, raw_request, packet


def dispatch(fixture, factory, selection, raw_request):
    return factory.invoke(
        REF, run_binding=fixture['run_binding'],
        work_ref=fixture['headers']['work']['version_ref'],
        source_cut=fixture['source_cut'], late_selection=selection,
        objects={'service': fixture['producer_service']}, args=(raw_request,))
