"""Disposable, source-bound technical capabilities for one selected native writer."""
import hashlib
import os
from pathlib import Path
import stat
import subprocess


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class FixtureExecutor:
    def __init__(self, executable_path, executable_sha256):
        self.executable_path = Path(executable_path)
        self.executable_sha256 = executable_sha256
        self.stop_stage = None
        self.stop_family = None
        self.marker = None
        self.guard()

    def guard(self):
        path = self.executable_path
        need(path.is_absolute() and path.is_file() and not path.is_symlink(), 'selected native executable origin required')
        need(stat.S_IMODE(path.stat().st_mode) == 0o755 and sha(path.read_bytes()) == self.executable_sha256,
             'selected native executable changed')

    def run_native(self, mode, args):
        self.guard()
        need(mode in ('seal', 'append', 'read'), 'unselected native mode')
        environment = os.environ.copy()
        if mode == 'append' and self.stop_stage is not None:
            environment.update(CAL_T32_STOP_STAGE=self.stop_stage,
                               CAL_T32_STOP_FAMILY=self.stop_family,
                               CAL_T32_MARKER=str(self.marker))
        return subprocess.run([str(self.executable_path), mode, *map(str, args)],
                              capture_output=True, timeout=120, env=environment)


class FixtureBoundary:
    def __init__(self, owned_parent, identity):
        self.owned_parent = Path(owned_parent)
        self.identity = tuple(identity)
        self.guard()

    def guard(self):
        path = self.owned_parent
        need(path.is_absolute() and path.is_dir() and not path.is_symlink(), 'selected owned parent required')
        value = path.stat()
        need((value.st_dev, value.st_ino, value.st_uid, stat.S_IMODE(value.st_mode)) == self.identity
             and value.st_uid == os.geteuid() and stat.S_IMODE(value.st_mode) == 0o700,
             'selected owned parent identity changed')


class FixtureTranslator:
    def guard(self):
        return None
