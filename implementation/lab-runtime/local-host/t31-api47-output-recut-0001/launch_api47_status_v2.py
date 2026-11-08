"""Execute the pinned API47 smoke runner from held bytes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SELECTION = HERE / 'API47-STATUS-RUNNER-SELECTION-0002.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def held(path, expected):
    if path.is_symlink() or any(parent.is_symlink() for parent in path.parents):
        raise ValueError('selected API47 runner path linked')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            raise ValueError('selected API47 runner path not regular')
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            raw = stream.read(before.st_size + 1)
        after = os.fstat(fd)
        if len(raw) != before.st_size or (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns) != (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns):
            raise ValueError('selected API47 runner changed during capture')
    finally:
        os.close(fd)
    if sha(raw) != expected:
        raise ValueError('selected API47 runner bytes differ')
    return raw


def run():
    if not sys.flags.isolated or not sys.dont_write_bytecode:
        raise ValueError('run with python3 -I -B')
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--selection-sha256', required=True)
    args = parser.parse_args()
    selected_raw = held(SELECTION, args.selection_sha256)
    selected = json.loads(selected_raw)
    if set(selected) != {'schema_version','launcher_binding','runner_binding','api_source_binding','api_profile_binding','static_diff_binding','receipt_binding','authority_effect'} or selected['schema_version'] != 'lab-T31-API47-status-runner-selection/v2' or selected['authority_effect'] != 'none':
        raise ValueError('closed API47 runner selection required')
    for role, path in (('launcher',Path(__file__)),('runner',HERE/'run_api47_status_v2.py')):
        binding = selected[role+'_binding']
        if set(binding) != {'path','sha256'} or binding['path'] != path.relative_to(ROOT).as_posix():
            raise ValueError('selected API47 '+role+' path differs')
        raw = held(path,binding['sha256'])
        if role == 'runner':
            runner = raw
    for role,path in (('api_source',ROOT/'product/lab/release-candidates/v1/interface/api-integration-v47-t31-output-current-0001/source-manifest.json'),
                      ('api_profile',ROOT/'product/lab/release-candidates/v1/interface/api-integration-v47-t31-output-current-0001/contract-profile.json'),
                      ('static_diff',HERE/'STATIC-VERIFY-0001.json'),
                      ('receipt',ROOT/'product/lab/release-candidates/v1/interface/api-integration-v47-t31-output-current-0001/rebind-receipt.json')):
        binding=selected[role+'_binding']
        if set(binding)!={'path','sha256'} or binding['path']!=path.relative_to(ROOT).as_posix():
            raise ValueError('selected API47 '+role+' binding differs')
        held(path,binding['sha256'])
    scope = {'__name__':'__main__','__file__':str(HERE/'run_api47_status_v2.py'),
             '__package__':None,'_HELD_RUNNER_SELECTION':selected_raw,
             '_HELD_RUNNER_SHA256':sha(runner)}
    exec(compile(runner,str(HERE/'run_api47_status_v2.py'),'exec',dont_inherit=True),scope)
    if held(SELECTION,args.selection_sha256)!=selected_raw:
        raise ValueError('API47 runner selection changed during execution')


if __name__=='__main__':
    run()
