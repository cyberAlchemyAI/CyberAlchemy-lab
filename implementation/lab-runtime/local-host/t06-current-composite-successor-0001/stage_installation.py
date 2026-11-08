#!/usr/bin/env python3
"""Copy the exact selected public T07 dependency closure into T06 working space."""
import hashlib
import json
import os
from pathlib import Path
import runpy
import stat

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
CONTROL = ROOT / 'product/lab/release-candidates/v1/interface/composite-operator-v1-current-api33-0001/revision-0001/control.py'
SELECTION = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json'
SELECTION_SHA = '2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'
SOURCE = ROOT / 'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
DESTINATION = HERE / 'working/installation-0001'
RECEIPT = HERE / 'working/INSTALLATION-0001.json'


def main():
    control = runpy.run_path(str(CONTROL))
    raw = control['capture'](SELECTION, SELECTION_SHA, owner=os.getuid())
    selection = control['parse'](raw)
    expected = {
        row['destination']: {'sha256': row['sha256'], 'size_bytes': row['size_bytes'],
                             'mode': 0o755 if row['kind'] in {'interpreter', 'native-executable'} else 0o644}
        for row in selection['inputs']
    }
    expected.update(selection['wheel_members'])
    expected['lib/abi/ld-linux-x86-64.so.2']['mode'] = 0o755
    control['need'](len(selection['inputs']) == 720 and len(selection['wheel_members']) == 290
                    and len(expected) == 1010, 'selected dependency closure differs')
    control['need'](not DESTINATION.exists() and not DESTINATION.is_symlink(),
                    'task-local installation already exists')
    DESTINATION.mkdir(mode=0o700)
    directories = {DESTINATION}
    try:
        for name, row in sorted(expected.items()):
            relative = Path(name)
            control['need'](relative.as_posix() == name and not relative.is_absolute()
                            and '..' not in relative.parts and '\\' not in name,
                            'unsafe selected installation path')
            raw = control['capture'](SOURCE / relative, row['sha256'],
                                     limit=row['size_bytes'], owner=os.getuid(),
                                     mode=row['mode'], size=row['size_bytes'])
            target = DESTINATION / relative
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            directories.update(target.parents)
            fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, row['mode'])
            try:
                with os.fdopen(fd, 'wb') as output:
                    output.write(raw)
                    output.flush()
                    os.fsync(output.fileno())
                os.chmod(target, row['mode'], follow_symlinks=False)
            except BaseException:
                try: os.close(fd)
                except OSError: pass
                raise
        metadata = SOURCE / 'installation.json'
        handle = os.open(metadata, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        try:
            info = os.fstat(handle)
            control['need'](stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid()
                            and stat.S_IMODE(info.st_mode) == 0o600 and info.st_size < 1024 * 1024,
                            'historical installation metadata differs')
            source_metadata = os.read(handle, info.st_size + 1)
            control['need'](len(source_metadata) == info.st_size, 'metadata changed during read')
        finally:
            os.close(handle)
        digest = hashlib.sha256(source_metadata).hexdigest()
        control['need'](digest == control['INSTALLATION_METADATA_SHA']
                        and len(source_metadata) == control['INSTALLATION_METADATA_SIZE'],
                        'historical installation metadata binding differs')
        source_metadata = control['capture'](metadata, digest, limit=len(source_metadata),
                                              owner=os.getuid(), mode=0o600,
                                              size=len(source_metadata))
        fd = os.open(DESTINATION / 'installation.json',
                     os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'wb') as output:
            output.write(source_metadata)
            output.flush()
            os.fsync(output.fileno())
        count = control['installed'](DESTINATION, expected)
        # The selected child runs with -B; frozen directories additionally
        # prevent routine Python execution from adding unselected bytecode.
        for directory in sorted((p for p in directories if p.is_relative_to(DESTINATION)),
                                key=lambda p: len(p.parts), reverse=True):
            os.chmod(directory, 0o555)
        count = control['installed'](DESTINATION, expected)
        receipt = {
            'schema_version': 'lab-T06-task-local-installation/v1-candidate',
            'authority_effect': 'none', 'source_selection_sha256': SELECTION_SHA,
            'source_installation': str(SOURCE), 'destination': str(DESTINATION),
            'selected_file_count': count, 'inventory_file_count': count + 1,
            'historical_installation_metadata_sha256': digest,
            'selected_bytes_verified_twice': True,
            'excluded_unselected_generated_caches': True,
            'actual_full34_startup': False,
        }
        fd = os.open(RECEIPT, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'wb') as output:
            output.write(json.dumps(receipt, sort_keys=True, indent=2).encode() + b'\n')
        print(json.dumps(receipt, sort_keys=True))
    except BaseException:
        # Preserve an incomplete directory for diagnosis; never select it.
        raise


if __name__ == '__main__':
    main()
