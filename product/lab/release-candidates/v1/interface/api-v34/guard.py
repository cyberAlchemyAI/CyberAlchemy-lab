"""Exact API source and selected environment before owned effects."""
import hashlib,importlib.metadata,json,platform
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
def verify(pin):
    path=HERE/'source-manifest.json';raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==pin,'independent API source pin differs'
    manifest=json.loads(raw)
    assert manifest['environment']=={'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},'API environment differs'
    assert manifest['authority_effect']=='none' and manifest['actual_owner_outcome'] is None
    for row in manifest['files']:
        p=ROOT/row['path'];assert p.is_file() and not p.is_symlink() and not any(a.is_symlink() for a in p.parents),'unsafe source '+row['path']
        assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],'source changed '+row['path']
    return manifest
