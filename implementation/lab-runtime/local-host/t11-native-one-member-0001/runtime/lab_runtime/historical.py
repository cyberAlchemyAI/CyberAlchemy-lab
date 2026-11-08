"""Closed original-v2 read-only dispatch; never reinterpret a legacy signature."""
from pathlib import Path
from .common import byte_digest,load,require
HERE=Path(__file__).resolve().parent
MANIFEST_SHA='787d0074a556536ac501f10da87a96b82d8ecb179efff59f4ea00148c172dc98'
def guard():
    path=HERE/'historical-v2-manifest.json'
    require(path.is_file() and not path.is_symlink() and byte_digest(path.read_bytes())==MANIFEST_SHA,
        'independent historical code manifest differs')
    m=load(path);require(m['authority_effect']=='none' and m['actual_owner_outcome'] is None,'historical code cannot grant authority')
    root=HERE/'historical_v2'
    actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    require(actual=={r['path'] for r in m['files']},'historical code closure differs')
    for row in m['files']:
        p=root/row['path']
        require(not p.is_symlink() and not any(q.is_symlink() for q in p.parents)
            and byte_digest(p.read_bytes())==row['sha256'],'historical code bytes differ')
        if row['original_binding']:require(row['original_binding']['sha256']==row['sha256'],'historical source copy differs')
    require(byte_digest((root/'profile.json').read_bytes())==m['profile_sha256'],'original historical profile differs')
    return root
def recognizes(config,baseline):
    # A distinct coupled or raw-family source is never silently downgraded.
    if config.get('endpoint_engine_id') is not None:return False
    root=guard()
    return baseline['profile']==load(root/'profile.json')
def replay_original(path,repo):
    guard()
    from .historical_v2.lab_runtime.store import Store
    data=Store(path,repo).replay()
    guard()
    return data
