"""Cold-select native first-Session originals for agent-context coordination."""
import base64
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(name, path):
    need(path.is_file() and not path.is_symlink()
         and not any(p.is_symlink() for p in path.parents),
         'selected native output helper absent or linked')
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def consume(selection):
    import retained as R
    need(type(selection) is dict and set(selection) == {
        'terminal_result', 'terminal_sha256', 'source_sha256',
        'profile_sha256', 'run_ref', 'process_result', 'process_sha256',
        'cold_readback', 'cold_sha256'}, 'closed native emission selection required')
    terminal_path = Path(selection['terminal_result'])
    process_path = Path(selection['process_result'])
    cold_path = Path(selection['cold_readback'])
    need(terminal_path.is_absolute() and terminal_path.name == 'FIRST-SESSION.json'
         and terminal_path.parent.name == 'first'
         and process_path == terminal_path.parent.parent / 'first.PROCESS-RESULT.json'
         and cold_path == terminal_path.parent.parent / 'first.COLD-READBACK.json',
         'exact supervised first-Session receipt layout required')
    terminal_raw = R.read(terminal_path)
    need(sha(terminal_raw) == selection['terminal_sha256'],
         'selected first-Session terminal changed')
    process_raw = R.read(process_path)
    cold_raw = R.read(cold_path)
    need(sha(process_raw) == selection['process_sha256']
         and sha(cold_raw) == selection['cold_sha256'],
         'selected first-Session supervisor receipts changed')
    process = json.loads(process_raw)
    cold = json.loads(cold_raw)
    need(process['phase'] == cold['phase'] == 'first'
         and process['passed'] is True and process['exit_code'] == 0
         and process['timed_out'] is False and cold['passed'] is True
         and cold['private_originals_retained'] is True
         and process['terminal_receipt_path'] == str(terminal_path)
         and process['terminal_receipt_sha256'] == sha(terminal_raw)
         and cold['process_result_sha256'] == sha(process_raw)
         and cold['phase_originals']['FIRST-SESSION.json']['sha256'] == sha(terminal_raw)
         and process['api_source_sha256'] == selection['source_sha256']
         and process['profile_sha256'] == selection['profile_sha256']
         and process['authority_effect'] == cold['authority_effect'] == 'none',
         'supervised first-Session process or cold readback did not pass')
    package_path = ROOT / '.cal-package-manifest.json'
    need(package_path.is_file() and not package_path.is_symlink(),
         'selected installed package manifest absent or linked')
    package_raw = package_path.read_bytes()
    need(sha(package_raw) == process['package_manifest_sha256'],
         'supervised first-Session installed package bytes differ')
    package = json.loads(package_raw)
    terminal = json.loads(terminal_raw)
    need(cold['terminal_result'] == terminal['result'],
         'cold first-Session result differs from terminal')
    source_binding = terminal['api_source_binding']
    profile_binding = terminal['profile_binding']
    source_path = ROOT / R.relative(source_binding['path'])
    profile_path = ROOT / R.relative(profile_binding['path'])
    need(source_path.parent == profile_path.parent
         and source_path.parent.parent == ROOT / 'product/lab/release-candidates/v1/interface'
         and package['entrypoint']['api_directory'] == str(source_path.parent.relative_to(ROOT))
         and package['binding_paths']['api.source'] == source_binding['path']
         and package['binding_paths']['api.profile'] == profile_binding['path']
         and source_path.name == 'source-manifest.json'
         and profile_path.name == 'contract-profile.json'
         and sha(source_path.read_bytes()) == source_binding['sha256']
         and sha(profile_path.read_bytes()) == profile_binding['sha256'],
         'first-Session API source/profile path or bytes differ')
    need(terminal['result'] == 'PASS-local-current-one-Lesson-selection-and-close'
         and terminal['api_source_binding']['sha256'] == selection['source_sha256']
         and terminal['profile_binding']['sha256'] == selection['profile_sha256']
         and terminal['explicitly_closed'] is True
         and terminal['memory_erased'] is True
         and terminal['selection_registry_erased'] is True,
         'actual first Session did not pass and close on selected installed cut')
    evidence = terminal['native_first_emission']
    need(evidence['posture'] == 'produced-uncommitted'
         and evidence['formal_output_count'] == 3,
         'three pre-close native originals required')
    path = Path(evidence['receipt_path'])
    need(path.is_absolute() and path.name == 'emission.json',
         'exact private native emission receipt required')
    emission_raw = R.read(path)
    need(sha(emission_raw) == evidence['receipt_sha256'],
         'native emission receipt differs from first Session terminal')
    emission = json.loads(emission_raw)
    emitter_path = ROOT / 'implementation/lab-runtime/local-host/t31-native-first-emitter-0002/native_first_emitter.py'
    need(sha(emitter_path.read_bytes()) == evidence['adapter_sha256']
         == emission['adapter_sha256'] == process['first_emitter_sha256'],
         'exact installed native emitter bytes differ')
    need(emission['installed_repository'] == str(ROOT)
         and emission['api_source_binding'] == terminal['api_source_binding']
         and emission['api_profile_sha256'] == selection['profile_sha256']
         and emission['source_cut'] == terminal['source_cut']
         and sha(emission['session_ref'].encode()) == terminal['session_ref_sha256']
         and emission['actual_RAM_memory_accessed'] is False
         and emission['actual_RAM_memory_persisted'] is False
         and emission['WorkflowRun_committed'] is False
         and emission['authority_effect'] == 'none'
         and emission['actual_owner_outcome'] is None,
         'native original lineage, memory or authority boundary differs')
    run_ref = selection['run_ref']
    need(type(run_ref) is str and run_ref.startswith('workflow-run:')
         and len(run_ref) <= 200, 'bounded fresh coordination Run required')
    E = load('_cal_t31_selected_native_emitter_' + sha(str(ROOT).encode())[:12], emitter_path)
    originals = E.retained(path.parent, evidence['receipt_sha256'])
    need([h['carrier_ref'] for h, _ in originals] == [
        'cal.artifact-type.context-view/v1',
        'cal.artifact-type.ontology-view/v1',
        'cal.artifact-type.agent-session/v1'],
        'exact native context/ontology/Session output roles required')
    inputs = {row['origin']['semantic_kind']: row for row in emission['coordination_inputs']}
    need(len(emission['coordination_inputs']) == len(inputs) == 6
         and set(inputs) == {'intent', 'work', 'goal', 'coordination-context',
                          'agent-assignment', 'context-request'},
         'complete native Source/generated coordination inputs required')
    retained_inputs = {}
    for kind, row in inputs.items():
        need(row['path'] == 'input-' + kind + '.json',
             'native coordination input locator differs')
        original = R.read(path.parent / row['path'])
        need(sha(original) == row['sha256'] == row['artifact']['byte_sha256']
             and original == base64.b64decode(row['private_original_base64'], validate=True),
             'native coordination input retained original differs')
        retained_inputs[kind] = original
    request = inputs['context-request']
    request_raw = retained_inputs['context-request']
    need(request['origin']['posture'] == 'produced-uncommitted'
         and request['artifact']['carrier_ref'] == 'cal.artifact-type.context-request/v1',
         'native generated ContextRequest original differs')
    capsule_path = ROOT / 'implementation/lab-runtime/local-host/t31-durable-output-0001/owned_coordination_capsule.py'
    CC = load('_cal_t31_selected_native_coordination_' + sha(str(ROOT).encode())[:12], capsule_path)
    capsule, capsule_raws = CC.build(emission, run_ref=run_ref,
        principal_ref=emission['principal_ref'], scope_ref=emission['scope_ref'])
    capsule_raw = CC.encoded(capsule)
    delegation = capsule['artifacts']['delegation']
    delegation_raw = capsule_raws[delegation['version_ref']]
    records = {h['version_ref']: (h, raw) for h, raw in originals}
    for header, raw in ((request['artifact'], request_raw),
                        (delegation, delegation_raw)):
        need(header['version_ref'] not in records and sha(raw) == header['byte_sha256'],
             'native coordination artifact revision/bytes differ')
        records[header['version_ref']] = (header, raw)
    transitions = {
        'transition:agent-context:context-ready': [h for h, _ in originals[:2]],
        'transition:agent-context:session-ready': [originals[2][0]],
    }
    return {'records': records, 'transitions': transitions,
            'terminal_binding': {'ref': str(terminal_path), 'sha256': sha(terminal_raw)},
            'process_binding': {'ref': str(process_path), 'sha256': sha(process_raw)},
            'cold_binding': {'ref': str(cold_path), 'sha256': sha(cold_raw)},
            'emission_binding': {'ref': str(path), 'sha256': sha(emission_raw)},
            'capsule_binding': {'ref': 'private-native-coordination:' + sha(capsule_raw),
                                'sha256': sha(capsule_raw)},
            'capsule_raw': capsule_raw,
            'identity': {'principal_ref': emission['principal_ref'], 'run_ref': run_ref},
            'input_refs': {
                'cal.artifact-type.agent-assignment/v1': inputs['agent-assignment']['artifact']['version_ref'],
                'cal.artifact-type.delegation/v1': delegation['version_ref'],
                'cal.artifact-type.context-request/v1': request['artifact']['version_ref'],
            },
            'source_binding': source_binding,
            'profile_binding': profile_binding,
            'package_pin': process['package_manifest_sha256'],
            'coordination_inputs': {
                kind: (copy.deepcopy(row['artifact']), retained_inputs[kind])
                for kind, row in inputs.items()},
            'source_cut': emission['source_cut']}
