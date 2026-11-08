"""Check selected executable bytes before importing the connector dependencies."""
import hashlib
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parents[1]
REPO = PACKAGE.parents[3]


def integrity():
    manifest = json.loads((PACKAGE / 'runtime-manifest.json').read_bytes())
    for row in manifest['files']:
        path = REPO / row['path']
        if path.is_symlink() or not path.resolve().is_relative_to(REPO):
            raise ValueError('selected dependency escapes repository')
        raw = path.read_bytes()
        if len(raw) != row['bytes'] or hashlib.sha256(raw).hexdigest() != row['sha256']:
            raise ValueError('selected connector dependency changed')
    sys.path.insert(0, str(REPO / 'implementation/define-cli/standalone'))
    sys.path.insert(0, str(REPO / 'implementation/lab-runtime/v2'))
    return manifest
