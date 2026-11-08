"""One no-replace bounded technical T08 run with class-only failure receipt."""

import contextlib
import argparse
import json
import os
from pathlib import Path
import resource
import sys
import time

import run_boundary

HERE = Path(__file__).resolve().parent
WORK = HERE / 'working'


def new_file(name):
    fd = os.open(WORK / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    return os.fdopen(fd, 'w', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--serial', choices=('0002',), required=True)
    args = parser.parse_args()
    WORK.mkdir(mode=0o700, exist_ok=True)
    started = time.monotonic()
    with new_file('RUN-' + args.serial + '.log') as log, contextlib.redirect_stderr(log):
        try:
            result = run_boundary.run()
        except BaseException as error:
            result = {'schema_version': 'lab-T08-current-mixed-full-boundary/v1-candidate',
                      'result': 'REFUSED', 'failure_class': type(error).__name__,
                      'authority_effect': 'none', 'T08_complete': False,
                      'full_verified_boundary_passed': False}
        result['elapsed_seconds'] = round(time.monotonic() - started, 3)
        result['maxrss_kib'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    with new_file('RESULT-' + args.serial + '.json') as out:
        out.write(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + '\n')
        out.flush()
        os.fsync(out.fileno())
    print(json.dumps({'result': result['result'], 'elapsed_seconds': result['elapsed_seconds'],
                      'maxrss_kib': result['maxrss_kib'],
                      'authority_effect': 'none', 'T08_complete': False}, sort_keys=True))
    return 0 if result['result'] == 'PASS-bounded-technical-full-boundary' else 1


if __name__ == '__main__':
    sys.exit(main())
