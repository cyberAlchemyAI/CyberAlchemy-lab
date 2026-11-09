#!/usr/bin/env python3
"""Exercise uncertain publication after the real atomic rename, without runtime fault flags."""
from pathlib import Path
from tempfile import TemporaryDirectory
import exact_io
with TemporaryDirectory(prefix='artifact-publication-proof-') as directory:
    destination=Path(directory)/'published'
    original=exact_io.fsync_dir
    def fail_after_publication(path):
        if destination.exists():raise OSError('isolated injected durability failure')
        return original(path)
    exact_io.fsync_dir=fail_after_publication
    try:
        exact_io.write_package(destination,{'evidence.txt':b'exact retained bytes\n'})
        raise AssertionError('uncertain publication was reported successful')
    except exact_io.Refusal as failure:
        assert failure.code=='publication-outcome-unknown',failure.code
    finally:exact_io.fsync_dir=original
    assert (destination/'evidence.txt').read_bytes()==b'exact retained bytes\n'
    try:exact_io.write_package(destination,{'evidence.txt':b'wrong retry\n'})
    except exact_io.Refusal as failure:assert failure.code=='output-exists-or-unavailable'
    else:raise AssertionError('retry overwrote uncertain publication')
    assert (destination/'evidence.txt').read_bytes()==b'exact retained bytes\n'
print('PASS: post-rename uncertainty preserves exact bytes and refuses overwrite')