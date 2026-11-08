"""Select three actual retained original Work stages for native coordination."""
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
import original_bundle as B


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def enc(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode()


def prepare(selection, output):
    captured = B.consume(selection)
    kind = selection['kind']
    definition_path = ROOT / 'docs/proposals/0007-lab-integrated-schema-package/workflows' / (kind + '.json')
    definition = json.loads(definition_path.read_bytes())
    routes = {row['transition_ref']: row for row in definition['transitions']}
    ordered = [('transition:' + kind + ':' + phase) for phase in
               (('designed', 'implemented', 'assessed') if kind == 'engineering'
                else ('designed', 'executed', 'evaluated'))]
    need(set(routes) == set(ordered) == set(captured['transitions']),
         'exact three original Work transitions required')
    manifest = json.loads(captured['manifest_raw'])
    initial = {}
    for row in manifest['records']:
        if row['origin'] != 'original-selected-input':
            continue
        header = row['artifact']
        need(header['carrier_ref'] not in initial, 'ambiguous original Work input carrier')
        initial[header['carrier_ref']] = header['version_ref']
    latest = dict(initial)
    stages = []
    for transition in ordered:
        route = routes[transition]
        outputs = captured['transitions'][transition]
        input_refs = {}
        for carrier in route['input_carriers']:
            if carrier in latest:
                input_refs[carrier] = latest[carrier]
            else:
                # The original Research design method validates and returns
                # the exact pre-existing ready ExperimentDesign body.
                same = [h for h in outputs if h['carrier_ref'] == carrier]
                need(kind == 'research' and transition.endswith(':designed')
                     and carrier == 'cal.artifact-type.experiment-design/v1'
                     and len(same) == 1,
                     'stage input has no selected original body')
                input_refs[carrier] = same[0]['version_ref']
        need(set(input_refs) == set(route['input_carriers']),
             'complete original Work input set required')
        need({h['carrier_ref'] for h in outputs} == set(route['output_carriers'])
             and len(outputs) == len(route['output_carriers']),
             'complete original Work output set required')
        stages.append({'transition_ref': transition, 'input_refs': input_refs,
                       'output_refs': [h['version_ref'] for h in outputs]})
        latest.update({h['carrier_ref']: h['version_ref'] for h in outputs})
    config = {'schema_version': 'lab-actual-retained-workflow-run/v1',
              'kind': kind, 'selections': [], 'typed_productions': [],
              'original_bundles': [selection], 'stages': stages,
              'final_state': routes[ordered[-1]]['to_state']}
    output = Path(output).absolute()
    need(not output.exists() and output.parent.is_dir()
         and not output.is_relative_to(ROOT)
         and not any(p.is_symlink() for p in output.parents),
         'fresh external private workflow config required')
    raw = enc(config)
    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    return {'config_path': str(output), 'config_sha256': hashlib.sha256(raw).hexdigest(),
            'kind': kind, 'selected_transitions': ordered,
            'original_work_source_cut': manifest['original_producer_source_cut'],
            'authority_effect': 'none'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for name in ('kind', 'manifest-path', 'manifest-sha256', 'output'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    result = prepare({'kind': args.kind, 'manifest_path': args.manifest_path,
                      'manifest_sha256': args.manifest_sha256}, args.output)
    print(json.dumps(result, sort_keys=True))
