#!/usr/bin/env python3
"""Apply reviewed allowlists with exact collision guards; dry-run by default."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

PLAN = Path(__file__).resolve().parent
LAB = PLAN.parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_path(base, relative):
    parts = Path(relative).parts
    if Path(relative).is_absolute() or '..' in parts or not parts:
        raise ValueError('Unsafe import path: ' + relative)
    result = base / relative
    for parent in [result, *result.parents]:
        if parent == base:
            break
        if parent.is_symlink():
            raise ValueError('Symlink in import destination: ' + str(parent))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    functional = json.loads((PLAN / 'IMPORT.json').read_text())
    evidence = json.loads((PLAN / 'EVIDENCE-EXPORT.json').read_text())
    policy = json.loads((PLAN / 'APPLY.json').read_text())
    collisions = {r['target']: r for r in policy['existing_targets']}
    rows = functional['payload'] + evidence['payload']
    assert len({r['target'] for r in rows}) == len(rows), 'Duplicate destination'
    protected = {}
    for relative in policy['must_keep_existing_paths']:
        target = LAB / relative
        if target.is_file():
            protected[relative] = digest(target)
    writes = []
    identical = 0
    for row in rows:
        source = safe_path(PLAN, row['source'])
        target = safe_path(LAB, row['target'])
        assert source.is_file() and digest(source) == row['sha256'], row['source']
        assert source.stat().st_size == row['bytes'], row['source']
        assert not any(row['target'] == x or row['target'].startswith(x + '/')
                       for x in policy['must_keep_existing_paths']), row['target']
        if target.exists():
            assert target.is_file(), 'Non-file collision: ' + row['target']
            current = digest(target)
            if current == row['sha256']:
                identical += 1
                continue
            collision = collisions.get(row['target'])
            assert collision and current == collision['expected_current_sha256'], 'Unreviewed collision: ' + row['target']
            assert row['sha256'] == collision['candidate_sha256'], 'Candidate changed'
        writes.append((row, source, target))
    summary = dict(schema_version='craft.local-import-application/v1',
                   mode='apply' if args.apply else 'dry-run', files=len(rows),
                   writes=len(writes), identical=identical,
                   guarded_existing_targets=len(collisions), protected_files=protected,
                   imported_archives=False, consumer_cutover=False, publication=False)
    if args.apply:
        for row, source, target in writes:
            target.parent.mkdir(parents=True, exist_ok=True)
            # Recheck at the write boundary; never clobber a concurrent edit.
            if target.exists():
                assert digest(target) == collisions[row['target']]['expected_current_sha256'], 'Concurrent edit'
            with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as temporary:
                temporary_path = Path(temporary.name)
            try:
                shutil.copyfile(source, temporary_path)
                os.chmod(temporary_path, row.get('mode', source.stat().st_mode & 0o777))
                os.replace(temporary_path, target)
            finally:
                temporary_path.unlink(missing_ok=True)
        for relative, expected in protected.items():
            assert digest(LAB / relative) == expected, 'Protected file changed: ' + relative
        summary['status'] = 'applied'
        summary['import_manifest_sha256'] = digest(PLAN / 'IMPORT.json')
        summary['evidence_manifest_sha256'] = digest(PLAN / 'EVIDENCE-EXPORT.json')
        (PLAN / 'APPLIED.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
