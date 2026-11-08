#!/usr/bin/env python3
"""Explicit maintainer packaging; never invoked by a user operation."""
from pathlib import Path
import hashlib
import json

PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parents[3]


def main():
    selected = [p for p in PACKAGE.rglob('*') if p.is_file() and p.name != 'runtime-manifest.json'
                and '__pycache__' not in p.parts and 'evidence' not in p.parts]
    native = REPO / 'implementation/lab-runtime/v2'
    selected += list((native / 'lab_runtime').glob('*.py'))
    selected += [native / 'profile.json',
                 REPO / 'define/define-lab',
                 REPO / 'define/define',
                 REPO / 'implementation/define-cli/standalone/define_core/runtime-manifest.json']
    core = REPO / 'implementation/define-cli/standalone/define_core'
    selected += [core / row['path'] for row in json.loads((core / 'runtime-manifest.json').read_bytes())['files']]
    candidate = REPO / 'authority/definitions/candidates/0017-user-journey'
    selected += [p for p in candidate.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    rows = [{'path': str(p.relative_to(REPO)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
             'bytes': p.stat().st_size} for p in sorted(set(selected))]
    (PACKAGE / 'runtime-manifest.json').write_text(json.dumps({
        'schema_version': 'cal.define.lab-connector-manifest/v1', 'files': rows,
        'standing': 'local connector candidate; no repository runtime adoption', 'authority_effect': 'none'
    }, sort_keys=True, indent=2) + '\n')
    print(json.dumps({'selected_files': len(rows)}))


if __name__ == '__main__':main()
