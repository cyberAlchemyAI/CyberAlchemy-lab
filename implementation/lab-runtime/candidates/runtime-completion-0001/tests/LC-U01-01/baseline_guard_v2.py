"""Anchored, bounded read-only successor; original capture records stay immutable.

Expected baseline and supplement hashes MUST come from a separately retained
accepted review. Neither is derived from the candidate being validated.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess

from baseline_guard import (absent, claim_pair, exclusive_file, fail, open_directory,
                            safe_relative, unique_pairs, verify_root, witness)

MAX_RECORD_BYTES = 1024 * 1024
MAX_SOURCE_BYTES = 32 * 1024 * 1024
MAX_BINDINGS = 1024


def digest_shape(value):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
        fail('independently supplied SHA-256 required')


def relative_to_root(root, path):
    path = Path(path)
    if path.is_absolute():
        try:
            path = path.relative_to(root)
        except ValueError:
            fail('path outside selected repository')
    return str(safe_relative(str(path)))


def read_verified(root, relative, expected_sha256, expected_size=None, limit=MAX_SOURCE_BYTES):
    """Return the SAME bounded held bytes whose digest/attachment was verified."""
    digest_shape(expected_sha256)
    rel = safe_relative(relative)
    if expected_size is not None and (type(expected_size) is not int or not 0 <= expected_size <= limit):
        fail('size shape or bound')
    parent = open_directory(Path(root) / rel.parent)
    try:
        fd = os.open(rel.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC, dir_fd=parent)
        try:
            before = os.fstat(fd)
            # O_NONBLOCK ensures a FIFO cannot stall before this type check.
            if not stat.S_ISREG(before.st_mode):
                fail('nonregular binding')
            if before.st_size > limit or (expected_size is not None and before.st_size != expected_size):
                fail('size shape or bound')
            data = bytearray()
            while chunk := os.read(fd, min(1024 * 1024, limit - len(data) + 1)):
                if len(data) + len(chunk) > limit:
                    fail('read bound exceeded')
                data.extend(chunk)
            after = os.fstat(fd)
            identity = lambda x: (x.st_dev, x.st_ino, x.st_size, x.st_mtime_ns, x.st_ctime_ns)
            attached = os.stat(rel.name, dir_fd=parent, follow_symlinks=False)
            if identity(before) != identity(after) or (attached.st_dev, attached.st_ino) != (after.st_dev, after.st_ino):
                fail('input changed or detached during read')
            if hashlib.sha256(data).hexdigest() != expected_sha256:
                fail('selected source drift: digest drift')
            if expected_size is not None and len(data) != expected_size:
                fail('selected source size drift')
            return bytes(data)
        finally:
            os.close(fd)
    finally:
        os.close(parent)


def read_binding(root, row):
    if not isinstance(row, dict) or set(row) != {'path', 'sha256', 'size_bytes'}:
        fail('binding shape')
    return read_verified(root, row['path'], row['sha256'], row['size_bytes'])


def verify_bindings(root, rows):
    if not isinstance(rows, list) or not 1 <= len(rows) <= MAX_BINDINGS:
        fail('nonempty bounded binding inventory required')
    seen = set()
    for row in rows:
        if not isinstance(row, dict):
            fail('binding shape')
        if row.get('path') in seen:
            fail('duplicate binding path')
        seen.add(row.get('path'))
        read_binding(root, row)
    return len(seen)


def parse_verified(data):
    return json.loads(data.decode('utf-8'), object_pairs_hook=unique_pairs,
                      parse_constant=lambda _: fail('nonfinite JSON value'))


def anchored_record(root, path, expected_sha256):
    rel = relative_to_root(root, path)
    return parse_verified(read_verified(root, rel, expected_sha256, limit=MAX_RECORD_BYTES))


def verify_current(root, baseline_path, *, expected_baseline_sha256,
                   supplement_path, expected_supplement_sha256):
    root = Path(root)
    baseline_rel = relative_to_root(root, baseline_path)
    # Verify the independent anchor BEFORE parsing any selector fields.
    baseline = anchored_record(root, baseline_rel, expected_baseline_sha256)
    if baseline.get('schema_version') != 'lab-completion-authoring-baseline/v1' or baseline.get('selection_kind') != 'code':
        fail('inert authoring baseline required')
    if baseline.get('runtime_eligible') is not False or baseline.get('authority_effect') != 'none':
        fail('baseline cannot grant runtime authority')
    # Parse only the exact paths bytes verified under the anchored baseline.
    paths = parse_verified(read_binding(root, baseline['paths_binding']))
    if paths.get('schema_version') != 'lab-completion-authoring-path-reservations/v1' or set(paths.get('roots', {})) != {'S', 'I', 'E'}:
        fail('path reservation shape')
    for name in ('S', 'E'):
        row = paths['roots'][name]
        verify_root(root / safe_relative(row['path']), row['identity'])
    install = paths['roots']['I']
    if install.get('created') is not False or install.get('os_exclusion_claimed') is not False:
        fail('installation must remain a logical reservation')
    absent(root / safe_relative(install['path']))
    supplement = anchored_record(root, supplement_path, expected_supplement_sha256)
    if set(supplement) != {'schema_version', 'unit', 'baseline_binding', 'active_guard_binding',
                          'helper_bindings', 'supersedes', 'authority_effect', 'runtime_eligible', 'claim_ceiling'}:
        fail('supplement shape')
    if supplement['schema_version'] != 'lab-LC-U01-01-guard-supplement/v1' or supplement['unit'] != 'LC-U01-01':
        fail('supplement identity')
    if supplement['authority_effect'] != 'none' or supplement['runtime_eligible'] is not False:
        fail('supplement cannot grant runtime authority')
    bound = supplement['baseline_binding']
    if bound['path'] != baseline_rel or bound['sha256'] != expected_baseline_sha256:
        fail('supplement selects a different baseline')
    if supplement['active_guard_binding'] not in supplement['helper_bindings']:
        fail('active guard absent from supplement closure')
    if supplement['active_guard_binding']['path'] != relative_to_root(root, __file__):
        fail('active guard origin differs')
    verify_bindings(root, supplement['helper_bindings'])
    # Original helpers are preservation witnesses, not the active dispatch guard.
    verify_bindings(root, baseline['implementation_helpers'])
    read_binding(root, baseline['preflight_binding'])
    count = verify_bindings(root, baseline['selected_inputs'])
    head = subprocess.run(['git', '--no-optional-locks', 'rev-parse', 'HEAD'], cwd=root,
                          capture_output=True, check=True, timeout=10).stdout.decode().strip()
    if head != baseline['git_head']:
        fail('HEAD drift')
    return {'result': 'PASS', 'selected_inputs_verified': count, 'I_absent': True,
            'baseline_sha256': expected_baseline_sha256, 'supplement_sha256': expected_supplement_sha256,
            'active_guard': supplement['active_guard_binding'], 'authority_effect': 'none', 'runtime_eligible': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True)
    parser.add_argument('--baseline', required=True)
    parser.add_argument('--baseline-sha256', required=True)
    parser.add_argument('--supplement', required=True)
    parser.add_argument('--supplement-sha256', required=True)
    args = parser.parse_args()
    print(json.dumps(verify_current(args.root, args.baseline,
                                  expected_baseline_sha256=args.baseline_sha256,
                                  supplement_path=args.supplement,
                                  expected_supplement_sha256=args.supplement_sha256), sort_keys=True))
