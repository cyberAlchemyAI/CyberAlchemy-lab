"""Select two current-source intent-framing transitions with native provenance."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / 'implementation/lab-runtime/local-host/t31-retained-api-0001'))


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode()


def module(name, path):
    need(path.is_file() and not path.is_symlink(), 'selected intent producer helper absent')
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    need(Path(value.__file__) == path, 'selected intent producer origin differs')
    return value


def prepare(bundle_selection, native_selection, output):
    B = module('_t31_selected_intent_bundle', HERE / 'intent_bundle.py')
    N = module('_t31_selected_native_emission', ROOT /
               'implementation/lab-runtime/local-host/t31-remaining-eighteen-0001/native_emission_bundle.py')
    bundle = B.consume(bundle_selection)
    native = N.consume(native_selection)
    need(bundle['run_ref'] == native['identity']['run_ref']
         and bundle['principal_ref'] == native['identity']['principal_ref']
         and bundle['source_cut'] == native['source_cut']
         and bundle['source_binding'] == native['source_binding']
         and bundle['profile_binding'] == native['profile_binding'],
         'intent-framing bundle and native first Session lineage differ')
    for intent_kind, native_kind in (('intent', 'intent'), ('work', 'work'),
                                     ('goal', 'goal'),
                                     ('coordination', 'coordination-context')):
        need(bundle['source_inputs'][intent_kind]
             == native['coordination_inputs'][native_kind],
             'intent-framing Source original differs from native first Session')
    definition_path = ROOT / 'docs/proposals/0007-lab-integrated-schema-package/workflows/intent-framing.json'
    definition = json.loads(definition_path.read_bytes())
    routes = {row['transition_ref']: row for row in definition['transitions']}
    need(set(routes) == set(B.ROUTES), 'exact two intent-framing transitions required')
    inputs = dict(bundle['input_refs'])
    outputs = bundle['transitions']
    stages = []
    for transition in B.ROUTES:
        route = routes[transition]
        headers = outputs[transition]
        need(set(inputs) >= set(route['input_carriers'])
             and len(headers) == len(route['output_carriers'])
             and {h['carrier_ref'] for h in headers} == set(route['output_carriers']),
             'exact current-source framing input/output carriers differ')
        stages.append({'transition_ref': transition,
                       'input_refs': {carrier: inputs[carrier]
                                      for carrier in route['input_carriers']},
                       'output_refs': [h['version_ref'] for h in headers]})
        inputs.update({h['carrier_ref']: h['version_ref'] for h in headers})
    need(stages[0]['output_refs'] == [bundle['intent_resolution']['version_ref']]
         and stages[1]['output_refs'] == [bundle['current_source_work']['version_ref']]
         and definition['initial_state'] == 'framed'
         and routes[B.ROUTES[-1]]['to_state'] == 'prepared',
         'resolution-to-original-Work transition ordering differs')
    config = {'schema_version': 'lab-actual-retained-workflow-run/v1',
              'kind': 'intent-framing', 'selections': [], 'typed_productions': [],
              'original_bundles': [bundle_selection],
              'native_emissions': [native_selection],
              'identity_selection': native['identity'],
              'stages': stages,
              'final_state': 'prepared'}
    output = Path(output)
    need(output.is_absolute() and not output.exists() and output.parent.is_dir()
         and not output.is_relative_to(ROOT)
         and not any(p.is_symlink() for p in output.parents),
         'fresh external private intent-framing config required')
    raw = encoded(config)
    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    return {'config_path': str(output), 'config_sha256': sha(raw),
            'selected_transitions': list(B.ROUTES),
            'current_source_work_sha256': bundle['current_source_work']['byte_sha256'],
            'private_intent_resolution_sha256': bundle['intent_resolution']['byte_sha256'],
            'authority_effect': 'none'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--bundle-selection', required=True)
    parser.add_argument('--native-selection', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    import retained as R
    bundle = json.loads(R.read(Path(args.bundle_selection)))
    native = json.loads(R.read(Path(args.native_selection)))
    print(json.dumps(prepare(bundle, native, args.output), sort_keys=True), flush=True)
