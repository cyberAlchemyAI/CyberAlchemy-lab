"""Bound the current API Source/profile proof table before physical T08 capture.

This is a metadata-only preflight. It never claims protected byte verification.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[4]
API = 'product/lab/release-candidates/v1/interface/api-integration-v33-current-0001'


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def parse(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'duplicate selected JSON key')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: need(False, 'nonfinite selected JSON'))


def binding(row):
    need(type(row) is dict and set(row) == {'path', 'sha256'}, 'closed path/digest row required')
    name = row['path']
    need(type(name) is str and name and '\\' not in name and '\x00' not in name,
         'unsafe path row')
    path = PurePosixPath(name)
    need(path.as_posix() == name and '..' not in path.parts,
         'noncanonical path row')
    digest = row['sha256']
    need(type(digest) is str and len(digest) == 64 and
         all(c in '0123456789abcdef' for c in digest), 'invalid digest row')
    return name, digest


def rows(document, label):
    selected = document['files']
    need(type(selected) is list and selected, label + ' files absent')
    result = []
    seen = set()
    for row in selected:
        item = binding(row)
        need(item[0] not in seen, label + ' duplicate path')
        seen.add(item[0])
        result.append(item)
    return result


def inspect(source_raw, profile_raw, source_pin, profile_pin):
    need(sha(source_raw) == source_pin and sha(profile_raw) == profile_pin,
         'independent current source/profile pin differs')
    source, profile = parse(source_raw), parse(profile_raw)
    source_path = API + '/source-manifest.json'
    profile_path = API + '/contract-profile.json'
    need(source['profile_binding'] == {'path': profile_path, 'sha256': profile_pin},
         'current source/profile binding differs')
    source_rows, profile_rows = rows(source, 'source'), rows(profile, 'profile')
    external = profile.get('external_execution_dependency_bindings', [])
    need(type(external) is list, 'external execution rows absent')
    external_rows = [binding(row) for row in external]
    need(len(external_rows) == len(set(external_rows)), 'duplicate external execution row')
    # The reader requires these exact ordered rows and physical files. This
    # preflight does not stat or read those files and cannot provide a PASS.
    return {
        'schema_version': 'lab-T08-current-proof-table-preflight/v1-candidate',
        'authority_effect': 'none',
        'source_binding': {'path': source_path, 'sha256': source_pin},
        'profile_binding': {'path': profile_path, 'sha256': profile_pin},
        'source_row_count': len(source_rows),
        'profile_row_count': len(profile_rows),
        'absolute_profile_path_count': sum(PurePosixPath(path).is_absolute() for path, _ in profile_rows),
        'external_execution_row_count': len(external_rows),
        'ordered_proof_occurrences_required': len(source_rows) + len(profile_rows) + len(external_rows),
        'physical_rows_verified': 0,
        'protected_reader_boundary_executed': False,
        'typed_graph_executed': False,
        'host_guard_executed': False,
        'T08_complete': False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-sha256', required=True)
    parser.add_argument('--profile-sha256', required=True)
    args = parser.parse_args()
    result = inspect((ROOT / API / 'source-manifest.json').read_bytes(),
                     (ROOT / API / 'contract-profile.json').read_bytes(),
                     args.source_sha256, args.profile_sha256)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
