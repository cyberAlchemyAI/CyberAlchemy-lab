#!/usr/bin/env python3
"""Execute only the frozen T32 runner bytes, including its child bootstrap."""
import hashlib
import os
from pathlib import Path
import stat

HERE = Path(__file__).resolve().parent
RUNNER_SHA256 = '847515e5f767c907bd0c0ee1afd9ff71d0bfb126cfa8e3dbd50983eb5800c8b1'


def main():
    path = HERE / 'run.py'
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ValueError('selected runner is not a regular file')
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            raw = stream.read()
    finally:
        os.close(fd)
    if hashlib.sha256(raw).hexdigest() != RUNNER_SHA256:
        raise ValueError('selected runner bytes changed')
    scope = {'__name__': '__main__', '__file__': str(path),
             '_SELECTED_RUNNER_RAW': raw}
    exec(compile(raw, str(path), 'exec'), scope)


if __name__ == '__main__':
    main()
