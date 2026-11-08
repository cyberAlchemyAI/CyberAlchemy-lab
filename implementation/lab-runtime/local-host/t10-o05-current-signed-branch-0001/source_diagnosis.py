"""Read-only exact O05 source-observation diagnosis; never exports source bodies."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
SELECTION = ROOT / 'implementation/lab-ontology/candidates/v1/migration/source-selection.json'
SELECTION_SHA = '0efe0f6a59c8339211feb919757f3ec7541e044cb9ce0fd7c4a4f6ea154c7aa7'
EXPECTED_MISSING = {
    '/home/vlad_/projects/domainspec-core/arcanum/spells/invoke/define/README.md': '03ccb341f266fa2404e7430a5d2cea21d0b00bb72b345772cb513f952fd3f738',
    '/home/vlad_/projects/domainspec-core/arcanum/framework/CYBERALCHEMY-METHOD.md': '16ff65dd97f33f2ac3cd0034c8c395084c8933b3cd3deed5e8c332662eb7ba8e',
    '/home/vlad_/projects/cyberAlchemy-v2/.git/refs/heads/main': 'dc064a539d5a525fbe777769a3496840c99aaba7271ccc8a3790ac40a99ade04',
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def checked(path, expected):
    path = Path(path)
    if any(p.is_symlink() for p in (path, *path.parents)):
        return 'unsafe-symlink'
    if not path.is_file():
        return 'missing'
    return 'match' if sha(path.read_bytes()) == expected else 'changed'


def diagnose():
    raw = SELECTION.read_bytes()
    if sha(raw) != SELECTION_SHA or SELECTION.is_symlink():
        raise ValueError('original O05 source selection changed')
    selected = json.loads(raw)
    if (len(selected['external_observations']) != 76 or
            len(selected['external_source_bindings']) != 66 or
            set(selected['root_bindings']) != {'historical-cav2', 'historical-workspace', 'standalone-cav2'}):
        raise ValueError('original O05 source selection closure changed')
    roots = {}
    for name, row in selected['root_bindings'].items():
        actual = subprocess.check_output(['git', '-C', row['git_root'], 'rev-parse', 'HEAD'], text=True).strip()
        roots[name] = {'git_root': row['git_root'], 'selected_head': row['head'],
                       'observed_head': actual, 'status': 'match' if actual == row['head'] else 'changed'}
    observations = []
    for row in selected['external_observations']:
        if not row['available'] or not row['expected_bytes_match']:
            continue
        observations.append({'path': row['material_path'], 'selected_sha256': row['expected_sha256'],
                             'status': checked(row['material_path'], row['expected_sha256'])})
    bindings = []
    for row in selected['external_source_bindings']:
        bindings.append({'path': row['path'], 'selected_sha256': row['sha256'],
                         'status': checked(row['path'], row['sha256'])})
    changed = {(row['path'], row['selected_sha256'], row['status'])
               for row in observations + bindings if row['status'] != 'match'}
    if changed != {(path, digest, 'missing') for path, digest in EXPECTED_MISSING.items()}:
        raise ValueError('O05 external source mismatch differs from selected diagnosis')
    if any(row['status'] != 'match' for row in roots.values()):
        raise ValueError('O05 selected Git roots changed')
    relocated = '/home/vlad_/projects/domainspec-core/.agents/skills/invoke/define/README.md'
    if checked(relocated, EXPECTED_MISSING['/home/vlad_/projects/domainspec-core/arcanum/spells/invoke/define/README.md']) != 'match':
        raise ValueError('exact moved Define source candidate changed')
    head_bytes = (roots['standalone-cav2']['observed_head'] + '\n').encode()
    if sha(head_bytes) != EXPECTED_MISSING['/home/vlad_/projects/cyberAlchemy-v2/.git/refs/heads/main']:
        raise ValueError('packed Git ref cannot reconstruct selected loose-ref bytes')
    return {'schema_version': 'lab-T10-O05-original-source-diagnosis/v1',
            'source_selection_sha256': SELECTION_SHA,
            'root_bindings': roots,
            'observation_count': len(selected['external_observations']),
            'originally_exact_observation_count': len(observations),
            'source_binding_count': len(bindings),
            'mismatch_occurrences': sum(row['status'] != 'match' for row in observations + bindings),
            'distinct_missing_sources': [{'path': p, 'selected_sha256': d} for p, d in sorted(EXPECTED_MISSING.items())],
            'exact_byte_recovery_candidates': [
                {'original_path': '/home/vlad_/projects/domainspec-core/arcanum/spells/invoke/define/README.md',
                 'candidate_path': relocated, 'sha256': EXPECTED_MISSING['/home/vlad_/projects/domainspec-core/arcanum/spells/invoke/define/README.md'],
                 'original_origin_restored': False},
                {'original_path': '/home/vlad_/projects/cyberAlchemy-v2/.git/refs/heads/main',
                 'candidate_derivation': 'pinned HEAD commit plus newline; ref currently packed',
                 'sha256': sha(head_bytes), 'original_origin_restored': False}],
            'unrecovered_original_paths': ['/home/vlad_/projects/domainspec-core/arcanum/framework/CYBERALCHEMY-METHOD.md'],
            'historical_o05_translation_currently_replayable': False,
            'source_bodies_exported': False,
            'authority_effect': 'none'}


if __name__ == '__main__':
    print(json.dumps(diagnose(), sort_keys=True, indent=2))
