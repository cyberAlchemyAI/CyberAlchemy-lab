"""Copy the exact selected T07 runtime closure into an owned mode0700 root."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import uuid

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
SELECTION = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json'
SELECTION_SHA = '2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'
ORIGINAL = ROOT / 'implementation/lab-runtime/local-host/t06-current-composite-successor-0001/working/installation-0001'
ORIGINAL_META_SHA = '5821d37ce536e08c639493ceb8d165949e65cf5dd9771af5576a724082cca13b'
DESTINATION = HERE / 'working/installation-0001'
RECEIPT = HERE / 'installation-receipt.json'


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def member(path: str) -> PurePosixPath:
    p = PurePosixPath(path)
    if not path or p.is_absolute() or '..' in p.parts or p.as_posix() != path:
        raise ValueError('unsafe selected installation member')
    return p


def build() -> dict:
    if DESTINATION.exists() or RECEIPT.exists():
        raise ValueError('owned installation successor already exists')
    if sha(SELECTION.read_bytes()) != SELECTION_SHA or sha((ORIGINAL / 'installation.json').read_bytes()) != ORIGINAL_META_SHA:
        raise ValueError('selected installation provenance changed')
    selection = json.loads(SELECTION.read_bytes())
    original = json.loads((ORIGINAL / 'installation.json').read_bytes())
    if original['result'] != 'PASS' or original['selection_sha256'] != SELECTION_SHA or len(original['installed_files']) != 1010:
        raise ValueError('original installation receipt differs')
    rows = {r['destination']: {**r, 'mode': 0o755 if r['kind'] in {'interpreter', 'native-executable'} else 0o644}
            for r in selection['inputs']}
    rows.update(selection['wheel_members'])
    rows['lib/abi/ld-linux-x86-64.so.2']['mode'] = 0o755
    if len(rows) != 1010 or len({member(p) for p in rows}) != 1010:
        raise ValueError('selected installation closure differs')
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    pending = DESTINATION.parent / ('installation-0001.pending-' + uuid.uuid4().hex)
    pending.mkdir(mode=0o700)
    copied = 0
    try:
        for name, row in sorted(rows.items()):
            relative = member(name)
            source = ORIGINAL / relative
            if source.is_symlink() or not source.is_file():
                raise ValueError('selected source installation member missing or linked')
            raw = source.read_bytes()
            if sha(raw) != row['sha256'] or len(raw) != row['size_bytes']:
                raise ValueError('selected source installation member changed: ' + name)
            target = pending / relative
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            with target.open('xb') as output:
                output.write(raw)
                output.flush()
                os.fsync(output.fileno())
            target.chmod(row['mode'])
            if sha(target.read_bytes()) != row['sha256'] or stat.S_IMODE(target.stat().st_mode) != row['mode']:
                raise ValueError('owned installation copy differs: ' + name)
            copied += 1
        if copied != 1010:
            raise ValueError('owned installation incomplete')
        pending.replace(DESTINATION)
    except BaseException:
        shutil.rmtree(pending)
        raise
    result = {'schema_version': 'lab-T03-d95-owned-margin-installation/v1-candidate',
              'selected_dependency_sha256': SELECTION_SHA,
              'original_installation_sha256': ORIGINAL_META_SHA,
              'owned_member_count': copied,
              'owned_root_mode': oct(stat.S_IMODE(DESTINATION.stat().st_mode)),
              'owned_root': DESTINATION.relative_to(ROOT).as_posix(),
              'authority_effect': 'none', 'runtime_executed': False}
    RECEIPT.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    return result


if __name__ == '__main__':
    print(json.dumps(build(), sort_keys=True, indent=2))
