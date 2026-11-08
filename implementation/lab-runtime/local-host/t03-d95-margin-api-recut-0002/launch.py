"""Launch a repository driver in the exact d95 diagnostic dependency cut.

Usage: python3 launch.py [--optimized] path/to/driver.py [driver arguments...]
The driver must construct DiagnosticMargin itself. This launcher makes no
claim that any live Lesson operation succeeded.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
INSTALL = ROOT / 'implementation/lab-runtime/local-host/t03-d95-margin-api-recut-0001/working/installation-0001'
OVERLAY = ROOT / 'implementation/lab-runtime/local-host/t06-jsonschema-419-overlay-0001/overlay'
API_PARENT = ROOT / 'product/lab/release-candidates/v1/interface'


def command(target: Path, arguments: list[str], *, optimized: bool = False) -> list[str]:
    target = target.resolve(strict=True)
    if not target.is_file() or not target.is_relative_to(ROOT):
        raise ValueError('selected driver must be a repository file')
    loader = INSTALL / 'lib/abi/ld-linux-x86-64.so.2'
    python = INSTALL / 'bin/python'
    if not loader.is_file() or not python.is_file():
        raise ValueError('owned interpreter closure absent')
    paths = [str(OVERLAY), str(INSTALL / 'deps'), str(API_PARENT), str(ROOT)]
    bootstrap = (
        'import json,runpy,sys; '
        'sys.path[:0]=json.loads(sys.argv[1]); '
        'target=sys.argv[2]; sys.argv=[target,*sys.argv[3:]]; '
        'runpy.run_path(target,run_name="__main__")'
    )
    return [str(loader), '--inhibit-cache', '--library-path', str(INSTALL / 'lib/abi'),
            str(python), '-I', *(['-O'] if optimized else []), '-X', 'utf8', '-B', '-S', '-c', bootstrap,
            json.dumps(paths), str(target), *arguments]


def main() -> int:
    arguments = sys.argv[1:]
    optimized = bool(arguments and arguments[0] == '--optimized')
    if optimized:
        arguments = arguments[1:]
    if not arguments:
        raise SystemExit('usage: python3 launch.py [--optimized] path/to/driver.py [driver arguments...]')
    process = subprocess.run(command(Path(arguments[0]), arguments[1:], optimized=optimized), cwd=ROOT,
                             env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    return process.returncode


if __name__ == '__main__':
    raise SystemExit(main())
