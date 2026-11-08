"""Cold physical readback for the bounded public T19 export result."""
import json
import stat
from run import HERE, FIXTURES, ROOT, PINS, API, check, sha

EXPECTED_CASES = ('byte-exact', 'rendered', 'parent-traversal', 'absolute-path', 'unmanaged-overwrite')
CLAIM = 'Local technical file export over public profile-pinned fixtures only; no current Source8, owner decision, or canonical publication.'

def verify(result=None):
    if result is None:
        result = json.loads((HERE / 'RESULT.json').read_bytes())
    check(result['schema_version'] == 'lab-T19-public-export-technical-run/v1'
          and result['authority_effect'] == 'none'
          and result['historical_custody_fixture_replayed'] is False
          and result['claim_ceiling'] == CLAIM, 'result claim flags differ')
    check([row['case'] for row in result['cases']] == list(EXPECTED_CASES),
          'exact five-case result closure required')
    check(result['selected_public_fixture_bindings'] ==
          [{'path': path, 'sha256': expected} for path, expected, _, _ in FIXTURES],
          'selected public fixture list differs')
    check(result['api_source_manifest_sha256'] == PINS['source-manifest.json'], 'source pin differs')
    check(result['api_profile_sha256'] == PINS['contract-profile.json'], 'profile pin differs')
    for name in ('source-manifest.json', 'contract-profile.json', 'export_kernel.py', 'protocol.py'):
        check(sha((API / name).read_bytes()) == PINS[name], 'API36 selected bytes differ')
    base = HERE / 'working' / 'owned-export-0001'
    check(base.is_dir() and not base.is_symlink() and stat.S_IMODE(base.stat().st_mode) == 0o700,
          'owned output base differs')
    for row in result['cases']:
        if row['case'] not in ('byte-exact', 'rendered'):
            check(row['posture'] == 'refused' and row['error'] == 'invalid exact request schema',
                  'negative refusal predicate differs')
            continue
        check(row['posture'] == 'published' and row['exact_replay'] is True, 'positive changed posture')
        generation = base / row['case'] / row['request_sha256']
        check(generation.is_dir() and not generation.is_symlink(), 'generation missing')
        manifest_raw = (generation / 'manifest.json').read_bytes()
        receipt_raw = (generation / 'receipt.json').read_bytes()
        marker_raw = (generation / 'PUBLISHED.json').read_bytes()
        check(sha(manifest_raw) == row['manifest_sha256'], 'manifest digest differs')
        check(sha(receipt_raw) == row['receipt_sha256'], 'receipt digest differs')
        check(sha(marker_raw) == row['marker_sha256'], 'marker digest differs')
        marker = json.loads(marker_raw)
        check(marker == {'manifest_sha256': row['manifest_sha256'],
                         'receipt_sha256': row['receipt_sha256']}, 'marker bindings differ')
        receipt = json.loads(receipt_raw)
        manifest = json.loads(manifest_raw)
        check(receipt['posture'] == 'published' and receipt['authority_effect'] == 'none'
              and receipt['canonical_replay_source'] is False and receipt['recovery_required'] is False,
              'receipt exceeded local export claim')
        check(receipt['manifest_binding']['sha256'] == row['manifest_sha256'], 'receipt manifest binding differs')
        check(len(manifest['files']) == len(FIXTURES) == len(receipt['output_bindings']), 'output closure differs')
        observed = []
        for index, (relative, expected, carrier, output) in enumerate(FIXTURES):
            raw = (ROOT / relative).read_bytes()
            check(sha(raw) == expected, 'selected public fixture differs')
            expected_output = raw if row['case'] == 'byte-exact' else (json.dumps(json.loads(raw), indent=2,
                sort_keys=True, ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')
            actual = (generation / 'files' / output).read_bytes()
            check(actual == expected_output, 'physical output bytes differ')
            digest = sha(actual)
            check(manifest['files'][index]['relative_path'] == output
                  and manifest['files'][index]['output_sha256'] == digest
                  and manifest['files'][index]['artifact']['byte_sha256'] == expected
                  and receipt['output_bindings'][index]['byte_sha256'] == digest,
                  'output binding differs')
            observed.append(digest)
        check(observed == row['output_sha256'], 'result output list differs')
    negative = base / 'negative'
    check({p.name for p in negative.iterdir()} == {'foreign.txt'}
          and (negative / 'foreign.txt').read_bytes() == b'foreign-untouched',
          'negative cases left a managed generation or changed foreign bytes')
    print('T19 cold physical output/receipt readback PASS')

if __name__ == '__main__':
    verify()
