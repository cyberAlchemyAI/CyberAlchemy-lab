"""Owned original metadata observation under independently supplied code/pins."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
RUN = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/accounting-0001'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-sha256', required=True)
    parser.add_argument('--selection-sha256', required=True)
    parser.add_argument('--output-name', required=True)
    args = parser.parse_args()
    manifest_raw = (HERE / 'source-manifest.json').read_bytes()
    if hashlib.sha256(manifest_raw).hexdigest() != args.source_sha256:
        raise SystemExit('independent accounting code selection differs')
    manifest = json.loads(manifest_raw)
    def guard():
        for entry in manifest['files']:
            path = ROOT / entry['path']
            if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
                raise SystemExit('selected accounting code/metadata changed')
        if (HERE / 'source-manifest.json').read_bytes() != manifest_raw:
            raise SystemExit('accounting source manifest changed')
    guard()
    sys.path.insert(0, str(HERE))
    import accounting as A
    source_path = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v16/source-manifest.json'
    profile_path = source_path.parent / 'contract-profile.json'
    source_raw, profile_raw = source_path.read_bytes(), profile_path.read_bytes()
    missing_raw = (RUN / 'unavailable-original-inputs.json').read_bytes()
    selection_raw = (RUN / 'observation-selection.json').read_bytes()
    missing = {entry['binding']['path'] for entry in A.parse(missing_raw)['rows']}
    current = [entry for entry in A.parse(source_raw)['files'] if entry['path'] not in missing]
    report = A.verify(source_raw, profile_raw, missing_raw, A.UNAVAILABLE_SHA,
                      selection_raw, args.selection_sha256, current, ROOT)
    guard()
    A.require(source_path.read_bytes() == source_raw and profile_path.read_bytes() == profile_raw,
              'original source/profile bytes changed during observation')
    name = args.output_name
    A.require(Path(name).name == name and name.endswith('.json') and name not in ('.', '..'),
              'owned observation output required')
    report['accounting_code_manifest_sha256'] = args.source_sha256
    report['selection_sha256'] = args.selection_sha256
    report['current_API17_dependencies_selected_or_verified'] = False
    report['consumption_inventory_meaning'] = 'Original metadata/presence observation only; no actual current API17 consumed callback inventory qualified.'
    with (RUN / name).open('xb') as handle:
        handle.write((json.dumps(report, indent=2, sort_keys=True) + '\n').encode())
    print(json.dumps({'result': report['result'], 'source_rows': len(report['original_source_files']),
                      'profile_rows': len(report['original_profile_files']),
                      'present_current_metadata_rows': len(report['current_guard_files']),
                      'missing_original_locators': report['unavailable_original_count'],
                      'historical_physical_closure': report['historical_original_physical_closure'],
                      'output': str(RUN / name)}))


if __name__ == '__main__':
    main()
