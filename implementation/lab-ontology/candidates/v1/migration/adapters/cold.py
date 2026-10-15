"""Fresh source-qualified reconstruction plus original native archive replay."""
from check import *


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('usage: cold.py package-path independent-manifest-sha256')
    files = load_package(sys.argv[1])
    with signed_catalog() as (catalog, operations):
        translator = SourceTranslation(catalog, operations)
        actual = validate_payload(files, translator, sys.argv[2], native=True)
    reconstructed = build()
    require(set(reconstructed) == set(files)
        and all(reconstructed[k] == raw for k, raw in files.items()), 'fresh build differs from exact original package bytes')
    print(json.dumps({'result': 'PASS', 'authority_effect': 'none', 'actual_owner_outcome': None,
        'independent_source_reconstruction': True, 'same_original_bytes': True,
        'files_compared': len(files), 'native_original_replay': actual,
        'source_execution': False, 'source_effects_applied': 0}, sort_keys=True))
