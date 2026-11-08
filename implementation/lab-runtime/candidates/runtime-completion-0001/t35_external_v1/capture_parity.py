"""Disposable external-root exercise of the exact frozen T03 capture/caller.

This adapter has no writer or production activation API. It proves that T03's
held read semantics work with a snapshot root and explicitly selected absolute
family outputs. It does not turn construction rows into phase receipts.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
from types import ModuleType, SimpleNamespace

from .constructor_paths import STAGE_CONTROLS
from .held_paths import HeldCanonicalDirectory
from .path_contract import canonical_path, check_binding, require
from .role_stage import DisposableLayout, entries

CAPTURE = {
    'path': 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T03/integrity-comparison-preparation-0001/capture.py',
    'sha256': 'eba3611c44fb76d89c7e741aac36ebcf52d3dc59786006af044d0ad98dc34962',
}
CALLER = {
    'path': 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T03/integrity-hardening-0002/caller_contract.py',
    'sha256': '4222b3ac165fa5ee8a9bed801290ffe42f63e69002ced521d4ac7e9e84bb7135',
}


def _held_raw(path: Path, expected: str) -> bytes:
    """Pin a scratch code leaf before loading it; T03 rechecks its own leaf."""
    canonical_path(str(path), absolute=True)
    with HeldCanonicalDirectory(str(path.parent)) as parent:
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC,
                     dir_fd=parent.fd)
        try:
            before = os.fstat(fd)
            require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
                    0 < before.st_size < 256 * 1024,
                    'bounded single-link T03 source required')
            raw = bytearray()
            while len(raw) <= before.st_size:
                chunk = os.read(fd, min(65536, before.st_size + 1 - len(raw)))
                if not chunk:
                    break
                raw.extend(chunk)
            after = os.fstat(fd)
            def stable(info):
                return (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid,
                        info.st_nlink, info.st_size, info.st_mtime_ns, info.st_ctime_ns)
            require(len(raw) == before.st_size and stable(after) == stable(before) and
                    parent.attached(),
                    'T03 source changed during held read')
            attached = os.stat(path.name, dir_fd=parent.fd, follow_symlinks=False)
            require(stable(attached) == stable(before), 'T03 source detached')
            require(hashlib.sha256(raw).hexdigest() == expected, 'exact frozen T03 source differs')
            return bytes(raw)
        finally:
            os.close(fd)


def _load(path: Path, pin: str, name: str):
    raw = _held_raw(path, pin)
    module = ModuleType(name)
    module.__file__ = str(path)
    module.__spec__ = SimpleNamespace(loader=SimpleNamespace(selected_source_sha256=pin))
    exec(compile(raw, str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


def _single_link(path: Path) -> None:
    canonical_path(str(path), absolute=True)
    with HeldCanonicalDirectory(str(path.parent)) as parent:
        leaf = os.stat(path.name, dir_fd=parent.fd, follow_symlinks=False)
        require(parent.attached() and stat.S_ISREG(leaf.st_mode) and leaf.st_nlink == 1,
                'single-link regular selected T03 leaf required')


class DisposableT03Parity:
    """One exact disposable snapshot and 30-leaf external stage read selection."""

    def __init__(self, layout: DisposableLayout, input_rows: list[dict],
                 stage_outputs: dict[str, dict]):
        require(type(layout) is DisposableLayout and type(input_rows) is list and
                type(stage_outputs) is dict, 'disposable T03 selection required')
        expected_outputs = {target for _, _, target in entries(layout)} | {
            str(layout.family / suffix) for suffix in STAGE_CONTROLS.values()}
        require(set(stage_outputs) == expected_outputs and len(stage_outputs) == 30,
                'exact external 30-leaf stage paths required')
        for path, row in stage_outputs.items():
            require(type(row) is dict and set(row) == {'path', 'sha256'} and row['path'] == path,
                    'exact external stage binding required')
            canonical_path(path, absolute=True)
            require(layout.family in PurePosixPath(path).parents, 'external stage outside family')
        selected = {}
        for row in input_rows:
            check_binding(row, kind='source_api')
            require(row['path'] not in selected, 'duplicate selected snapshot row')
            selected[row['path']] = copy.deepcopy(row)
        require(selected.get(CAPTURE['path']) == CAPTURE and
                selected.get(CALLER['path']) == CALLER,
                'exact frozen T03 kernel and caller must be snapshot-selected')
        self.layout = layout
        self._inputs = selected
        self._outputs = copy.deepcopy(stage_outputs)
        self._selection_digest = self._digest()
        kernel_path = Path(layout.snapshot / CAPTURE['path'])
        caller_path = Path(layout.snapshot / CALLER['path'])
        self._kernel = _load(kernel_path, CAPTURE['sha256'], '_t35_disposable_t03_kernel')
        self._caller = _load(caller_path, CALLER['sha256'], '_t35_disposable_t03_caller')
        self._kernel_path = kernel_path
        self._caller_path = caller_path
        self._caller_check = self._caller.check
        self._capture_one = self._kernel.capture_one
        self._verify_all = self._kernel.verify_all
        self._callback_codes = (self._caller_check.__code__, self._capture_one.__code__,
                                self._verify_all.__code__)
        self._caller_globals = tuple(self._caller.__dict__.items())
        self._contract = self._caller.select(self._kernel, expected_path=kernel_path,
                                             expected_sha256=CAPTURE['sha256'])
        self._caller_check(self._contract, self._kernel)

    def _check(self):
        require(self._digest() == self._selection_digest, 'T03 disposable selection mutated')
        require(self._caller.check is self._caller_check and
                self._kernel.capture_one is self._capture_one and
                self._kernel.verify_all is self._verify_all,
                'T03 selected callback replaced')
        require((self._caller_check.__code__, self._capture_one.__code__,
                 self._verify_all.__code__) == self._callback_codes and
                set(self._caller.__dict__) == {key for key, _ in self._caller_globals} and
                all(self._caller.__dict__[key] is value for key, value in self._caller_globals),
                'T03 selected callback code or caller globals changed')
        _held_raw(self._caller_path, CALLER['sha256'])
        self._caller_check(self._contract, self._kernel)

    def _digest(self):
        return hashlib.sha256(json.dumps({'layout': [str(self.layout.family), str(self.layout.snapshot),
                                           self.layout.instance], 'inputs': self._inputs,
                                          'outputs': self._outputs}, sort_keys=True,
                                         separators=(',', ':'), allow_nan=False).encode()).hexdigest()

    def read_input(self, row: dict) -> bytes:
        self._check()
        check_binding(row, kind='source_api')
        require(self._inputs.get(row['path']) == row, 'snapshot row not selected')
        leaf = Path(self.layout.snapshot / row['path'])
        _single_link(leaf)
        raw = self._capture_one(self.layout.snapshot, row,
                                code_sha256=CAPTURE['sha256'])
        _single_link(leaf)
        self._check()
        return raw

    def read_stage(self, row: dict) -> bytes:
        self._check()
        require(type(row) is dict and set(row) == {'path', 'sha256'} and
                self._outputs.get(row['path']) == row, 'external stage row not selected')
        _single_link(Path(row['path']))
        raw = self._capture_one(self.layout.snapshot, row,
                                code_sha256=CAPTURE['sha256'],
                                selected_external=(row,))
        _single_link(Path(row['path']))
        self._check()
        return raw

    def verify_stage(self) -> int:
        rows = [self._outputs[path] for path in sorted(self._outputs)]
        self._check()
        for row in rows:
            _single_link(Path(row['path']))
        count = self._verify_all(self.layout.snapshot, rows,
                                 code_sha256=CAPTURE['sha256'],
                                 selected_external=rows)
        for row in rows:
            _single_link(Path(row['path']))
        self._check()
        require(count == 30, 'T03 external stage count differs')
        return count
