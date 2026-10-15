#!/usr/bin/env python3
"""One actual candidate episode; preserve every numbered attempt."""
import argparse
import traceback
from episode import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--native-executable', required=True)
    args = parser.parse_args(); executable = Path(args.native_executable).resolve()
    expected = load(ROOT / 'implementation/lab-context/candidates/v1/packages/0004/generator-manifest.json')['native_executable_sha256']
    require(byte_digest(executable.read_bytes()) == expected, 'wrong exact native executable')
    packages = PACKAGE / 'packages'; packages.mkdir(exist_ok=True); index = 1
    while (packages / f'{index:04d}').exists(): index += 1
    destination = packages / f'{index:04d}'; destination.mkdir()
    sources = [binding(p) for p in PACKAGE.glob('*.py')] + [binding(PACKAGE / 'README.md')]
    (destination / 'execution-manifest.json').write_bytes(encoded({'authority_effect': 'none', 'files': sources, 'native_executable_sha256': expected}))
    try:
        result = perform(destination, executable)
        print(json.dumps({'result': 'PASS', 'actual_bounded_Work': True, 'package': destination.relative_to(ROOT).as_posix(), 'local_transaction': result['local_transaction']['transaction_digest'], 'repository_admissions_applied': 0}), flush=True)
    except BaseException as error:
        (destination / 'failure.json').write_bytes(encoded({'result': 'FLAG', 'authority_effect': 'none', 'observed_error': str(error), 'traceback': traceback.format_exc(), 'repository_admissions_applied': 0}))
        raise
