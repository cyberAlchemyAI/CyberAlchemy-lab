"""Select actual current API originals for an output-bearing WorkflowRun.

The spec names exact native terminal files and exact artifact revisions. This
utility reads their retained originals, checks their selected Source/profile,
and writes a fresh private run_current configuration. It cannot create an
output, decision, or admission record.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode()


def original_reader(root):
    path = root / 'implementation/lab-runtime/local-host/t31-retained-api-0001/retained.py'
    need(path.is_file() and not path.is_symlink(), 'selected installed original reader absent')
    spec = importlib.util.spec_from_file_location('_cal_t31_remaining_originals', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def selected_case(reader, terminal_path, operation, source_sha, profile_sha):
    path = Path(terminal_path)
    need(path.is_absolute(), 'absolute terminal required')
    raw = reader.read(path)
    terminal = json.loads(raw)
    need(terminal['result'] == 'PASS' and terminal['source_sha256'] == source_sha
         and terminal['profile_sha256'] == profile_sha,
         'successful exact Source/profile terminal required')
    cases = [row for row in terminal['cases']
             if row['operation'] == operation and row['expected_kind'] == 'result'
             and row['result'] == 'PASS']
    need(len(cases) == 1, 'exactly one positive retained producer case required')
    retained = cases[0]['retained_originals']
    selection = {'archive': retained['path'],
                 'observation_sha256': retained['observation_sha256'],
                 'terminal_result': str(path), 'terminal_sha256': sha(raw),
                 'source_sha256': source_sha, 'profile_sha256': profile_sha,
                 'operation': operation}
    return selection, reader.consume(**selection)


def prepare(root, source_sha, profile_sha, spec_path, output):
    root = Path(root).absolute()
    spec_path = Path(spec_path).absolute()
    output = Path(output).absolute()
    need(root.is_dir() and not root.is_symlink()
         and output.parent.is_dir() and not output.exists()
         and not output.is_relative_to(root)
         and not any(p.is_symlink() for p in output.parents),
         'selected installation and fresh external output required')
    need(all(len(pin) == 64 and all(c in '0123456789abcdef' for c in pin)
             for pin in (source_sha, profile_sha)), 'exact digest pins required')
    reader = original_reader(root)
    selection_spec = json.loads(reader.read(spec_path))
    need(type(selection_spec) is dict
         and set(selection_spec) == {'schema_version', 'kind', 'producer_terminals',
                                     'stages', 'final_state'}
         and selection_spec['schema_version'] == 'lab-t31-exact-api-output-selection/v1'
         and type(selection_spec['producer_terminals']) is list
         and selection_spec['producer_terminals']
         and type(selection_spec['stages']) is list and selection_spec['stages'],
         'closed current API output selection required')
    selections = []
    records = {}
    for item in selection_spec['producer_terminals']:
        need(type(item) is dict and set(item) == {'terminal_path', 'operation'},
             'closed exact producer terminal selection required')
        selection, observed = selected_case(reader, item['terminal_path'],
                                             item['operation'], source_sha, profile_sha)
        selections.append(selection)
        for header, raw in observed['outputs']:
            ref = header['version_ref']
            need(ref not in records or records[ref] == (header, raw),
                 'ambiguous original output revision')
            records[ref] = (header, raw)
    stages = selection_spec['stages']
    need(len({row['transition_ref'] for row in stages}) == len(stages),
         'duplicate transition selection')
    kind = selection_spec['kind']
    definition_path = root / 'docs/proposals/0007-lab-integrated-schema-package/workflows' / (kind + '.json')
    need(definition_path.is_file() and not definition_path.is_symlink(),
         'original selected workflow definition absent')
    definition = json.loads(definition_path.read_bytes())
    expected = {row['transition_ref']: row for row in definition['transitions']}
    for row in stages:
        need(type(row) is dict and set(row) == {'transition_ref', 'input_refs', 'output_refs'},
             'closed exact stage required')
        transition = row['transition_ref']
        need(transition in expected and transition.startswith('transition:' + kind + ':'),
             'transition outside selected original workflow')
        need(type(row['input_refs']) is dict
             and set(row['input_refs']) == set(expected[transition]['input_carriers'])
             and all(type(ref) is str and ref for ref in row['input_refs'].values()),
             'complete exact input carrier selection required')
        need(type(row['output_refs']) is list and row['output_refs']
             and len(row['output_refs']) == len(set(row['output_refs']))
             and all(ref in records for ref in row['output_refs']),
             'output revision lacks retained successful API original')
        actual_carriers = [records[ref][0]['carrier_ref'] for ref in row['output_refs']]
        need(len(actual_carriers) == len(set(actual_carriers))
             and set(actual_carriers) == set(expected[transition]['output_carriers']),
             'retained API output carrier closure differs')
    need(stages[-1]['transition_ref'] == expected[stages[-1]['transition_ref']]['transition_ref']
         and selection_spec['final_state'] == expected[stages[-1]['transition_ref']]['to_state'],
         'selected final state differs from original transition')
    config = {'schema_version': 'lab-actual-retained-workflow-run/v1',
              'kind': kind, 'selections': selections, 'typed_productions': [],
              'stages': stages, 'final_state': selection_spec['final_state']}
    raw = encoded(config)
    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    return {'config_path': str(output), 'config_sha256': sha(raw),
            'producer_count': len(selections), 'stage_count': len(stages),
            'selected_output_refs': sorted({ref for row in stages for ref in row['output_refs']}),
            'authority_effect': 'none'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for name in ('installed-repository', 'source-sha256', 'profile-sha256', 'spec', 'output'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.installed_repository, args.source_sha256,
                             args.profile_sha256, args.spec, args.output), sort_keys=True))
