#!/usr/bin/env python3
"""Resolve legacy source locations; refresh active representation pins explicitly."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

CRAFT = Path(__file__).resolve().parents[2]
LAB = next(parent for parent in CRAFT.parents if (parent / 'authority/definitions/registry.json').is_file() and (parent / 'implementation/lab-runtime').is_dir())
UPSTREAM = LAB.parent / 'cyberAlchemy-v2'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def resolve_source(relative):
    """Current paths are Lab-relative or explicitly use the sibling namespace."""
    parts = Path(relative).parts
    if not parts or Path(relative).is_absolute() or '..' in parts or '\\' in relative:
        raise ValueError('Unsafe semantic source path: ' + relative)
    if relative.startswith('cyberAlchemy-v2/'):
        return 'upstream', UPSTREAM / relative.removeprefix('cyberAlchemy-v2/')
    if relative.startswith('craft/'):
        return 'lab', LAB / relative
    # Compatibility for old path declarations during an explicit source review.
    if relative.startswith('projects/domainspec-v2/'):
        return 'upstream', UPSTREAM / 'craft' / relative
    raise ValueError('Undeclared semantic source namespace: ' + relative)


def reconcile():
    rows = []
    for name in ['product-bridge', 'orodi-bridge']:
        registry = CRAFT / 'ontology/packages' / name / 'sources.json'
        for source in json.loads(registry.read_text())['sources']:
            relative = source['path']
            root, target = resolve_source(relative)
            actual = sha(target) if target.is_file() else None
            state = ('missing' if actual is None else 'current' if actual == source['sha256'] else 'drifted')
            rows.append(dict(package=name, source_id=source['source_id'], source_path=relative,
                             resolved_root=root, expected_sha256=source['sha256'],
                             current_sha256=actual, state=state,
                             authority_effect='none'))
    counts = dict(current=0, missing=0, drifted=0)
    counts.update(Counter(r['state'] for r in rows))
    return dict(schema_version='craft.ontology.source-reconciliation/v1', authority_effect='none',
                status='lineage-needs-owner-review' if counts.get('missing') or counts.get('drifted') else 'current',
                roots={'lab': '.', 'upstream': '../cyberAlchemy-v2'}, root_base='Lab root',
                counts=counts, bindings=rows, representation_inputs='separately pinned by application/source-manifest.json',
                semantic_review_ref='craft/ontology/sources/review.json',
                interpretation='Current source choices and bounded claims follow the explicit owner review. Reconciliation compares expected pins; it never updates semantic source expectations or grants admission.',
                open_questions=['Current source matching and reference classification do not qualify broader application/provider/runtime behavior or adopt Product candidates.'])


def refresh_manifest():
    path = CRAFT / 'ontology/application/source-manifest.json'
    manifest = json.loads(path.read_text())
    extra = ['ontology/sources/reconciliation.json', 'ontology/sources/review.json',
             'work/experiments/body-war-reference/application.json',
             'work/experiments/body-war-reference/README.md']
    # Include the reader itself in provenance without creating a manifest self-reference.
    extra += ['ontology/application/derive.mjs']
    first = manifest['packages'][0]
    present = {d['path'] for d in first['documents']}
    for relative in extra:
        if relative not in present:
            first['documents'].append(dict(root='craft', path=relative, sha256=sha(CRAFT / relative)))
    for package in manifest['packages']:
        for ref in [package['profile'], package['nodes']['source'], package['relations']['source'], *package['documents']]:
            relative = Path(ref['path'])
            assert not relative.is_absolute() and '..' not in relative.parts
            ref['sha256'] = sha(CRAFT / relative)
    write(path, manifest)
    return sum(len(p['documents']) for p in manifest['packages'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--refresh-manifest', action='store_true')
    args = parser.parse_args()
    if args.refresh_manifest and not args.write:
        parser.error('--refresh-manifest requires --write')
    report = reconcile()
    if args.write:
        write(CRAFT / 'ontology/sources/reconciliation.json', report)
    documents = refresh_manifest() if args.refresh_manifest else None
    print(json.dumps(dict(status=report['status'], counts=report['counts'], representation_documents=documents)))
