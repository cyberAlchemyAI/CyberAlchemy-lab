#!/usr/bin/env python3
"""Render only this candidate package's human projections."""
import argparse
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def definition_projection(data):
    source = ROOT / 'authority/artifact-types/definition/v2/generator.py'
    namespace = {'__name__': 'candidate_definition_renderer'}
    exec(compile(source.read_text(), str(source), 'exec'), namespace)
    return namespace['render'](data)


def package_projection(data):
    lines = ['<!-- GENERATED: edit package.json; run render.py. -->', '',
        '# ' + data['package_id'], '',
        'Candidate package declaration only; no admission or source migration.', '',
        '- Root: `' + data['package_root'] + '`',
        '- Lifecycle owner route: `' + data['lifecycle_owner_ref'] + '`',
        '- Unit of change: ' + data['unit_of_change'], '',
        '| Path | Role | Artifact Type |', '| --- | --- | --- |']
    lines += ['| `' + e['path'] + '` | ' + e['role'] + ' | ' + str(e['artifact_type_ref'] or '') + ' |'
        for e in data['surface_entries']]
    lines += ['', 'Independent nested homes: ' + str(len(data['nested_packages'])), '', data['claim_ceiling']]
    return '\n'.join(lines) + '\n'


def projections():
    definition = HERE / 'definition/lab-workspace/definition.json'
    if definition.exists():
        yield definition.with_name('DEFINITION.md'), definition_projection(json.loads(definition.read_text()))
    for source in sorted(HERE.rglob('package.json')):
        yield source.with_name('PACKAGE.md'), package_projection(json.loads(source.read_text()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    errors = []
    for path, expected in projections():
        if args.check:
            if not path.exists() or path.read_text() != expected:
                errors.append(str(path.relative_to(HERE)))
        else:
            path.write_text(expected)
    if errors:
        raise SystemExit('Projection drift: ' + ', '.join(errors))
    print('Projection parity passed.' if args.check else 'Candidate projections rendered.')


if __name__ == '__main__':
    main()
