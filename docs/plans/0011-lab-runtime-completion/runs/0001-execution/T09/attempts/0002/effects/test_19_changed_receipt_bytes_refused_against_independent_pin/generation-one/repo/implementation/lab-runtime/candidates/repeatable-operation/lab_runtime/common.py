"""Byte-preserving candidate protocol helpers; digest is not an authority grant."""
from __future__ import annotations

import json
from pathlib import Path

from ._legacy.common import (RuntimeFault, atomic, byte_digest, digest, encoded,
                             fsync_dir, pointer, require, sealed, under as legacy_under, verify_seal)


def loads(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON key: ' + key)
            result[key] = value
        return result
    try:
        if isinstance(raw, bytes):
            raw = raw.decode('utf-8')
        result = json.loads(raw, object_pairs_hook=pairs,
                            parse_constant=lambda s: (_ for _ in ()).throw(RuntimeFault('nonfinite JSON: ' + s)))
        def unicode_values(value):
            if isinstance(value, str):
                value.encode('utf-8', errors='strict')
            elif isinstance(value, list):
                for item in value:
                    unicode_values(item)
            elif isinstance(value, dict):
                for key, item in value.items():
                    unicode_values(key)
                    unicode_values(item)
        unicode_values(result)
        return result
    except (UnicodeError, ValueError) as exc:
        raise RuntimeFault('invalid UTF-8 JSON: ' + str(exc)) from exc


def load(path):
    try:
        return loads(Path(path).read_bytes())
    except OSError as exc:
        raise RuntimeFault('cannot read ' + str(path) + ': ' + str(exc)) from exc


def under(root, relative):
    require(isinstance(relative, str) and relative and '\\' not in relative and '\x00' not in relative
            and Path(relative).as_posix() == relative.rstrip('/'), 'noncanonical material path')
    return legacy_under(root, relative.rstrip('/'))


def binding(root, path):
    file = under(Path(root), path)
    raw = file.read_bytes()
    return {'path': path, 'sha256': byte_digest(raw), 'size_bytes': len(raw)}
