"""Select live first-Session originals for two fresh agent-context transitions."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'implementation/lab-runtime/local-host/t31-retained-api-0001'))
import native_emission_bundle as B


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def enc(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode()


def prepare(selection, output):
    captured = B.consume(selection)
    definition_path = ROOT / 'docs/proposals/0007-lab-integrated-schema-package/workflows/agent-context.json'
    definition = json.loads(definition_path.read_bytes())
    routes = {row['transition_ref']: row for row in definition['transitions']}
    ordered = ('transition:agent-context:context-ready',
               'transition:agent-context:session-ready')
    need(set(routes) == set(ordered) == set(captured['transitions']),
         'two exact agent-context transitions required')
    inputs = dict(captured['input_refs'])
    stages = []
    for transition in ordered:
        route = routes[transition]
        outputs = captured['transitions'][transition]
        need(set(inputs) >= set(route['input_carriers'])
             and {h['carrier_ref'] for h in outputs} == set(route['output_carriers'])
             and len(outputs) == len(route['output_carriers']),
             'actual native input/output carrier closure differs')
        stages.append({'transition_ref': transition,
                       'input_refs': {carrier: inputs[carrier] for carrier in route['input_carriers']},
                       'output_refs': [h['version_ref'] for h in outputs]})
        inputs.update({h['carrier_ref']: h['version_ref'] for h in outputs})
    config = {'schema_version': 'lab-actual-retained-workflow-run/v1',
              'kind': 'agent-context', 'selections': [], 'typed_productions': [],
              'native_emissions': [selection],
              'identity_selection': captured['identity'],
              'stages': stages,
              'final_state': routes[ordered[-1]]['to_state']}
    output = Path(output).absolute()
    need(not output.exists() and output.parent.is_dir()
         and not output.is_relative_to(ROOT)
         and not any(p.is_symlink() for p in output.parents),
         'fresh external private workflow configuration required')
    raw = enc(config)
    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    return {'config_path': str(output), 'config_sha256': hashlib.sha256(raw).hexdigest(),
            'native_first_result_sha256': selection['terminal_sha256'],
            'selected_transitions': list(ordered), 'authority_effect': 'none'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for name in ('terminal-result', 'terminal-sha256', 'process-result',
                 'process-sha256', 'cold-readback', 'cold-sha256',
                 'source-sha256', 'profile-sha256', 'run-ref', 'output'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    selection = {'terminal_result': args.terminal_result,
                 'terminal_sha256': args.terminal_sha256,
                 'process_result': args.process_result,
                 'process_sha256': args.process_sha256,
                 'cold_readback': args.cold_readback,
                 'cold_sha256': args.cold_sha256,
                 'source_sha256': args.source_sha256,
                 'profile_sha256': args.profile_sha256,
                 'run_ref': args.run_ref}
    print(json.dumps(prepare(selection, args.output), sort_keys=True))
