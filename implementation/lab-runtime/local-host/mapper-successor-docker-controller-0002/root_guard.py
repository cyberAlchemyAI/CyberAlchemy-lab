"""Held staged root and Mapper package-parent custody across one Docker run."""
from __future__ import annotations

import os
from pathlib import Path
import stat
import sys

from anchored_copy import FLAGS, close_all, dir_identity, parent_chain, require


class RootGuard:
    def __init__(self, root: Path, package_parent: str):
        self.root = Path(root)
        self.package_parts = tuple(package_parent.split('/'))
        require(bool(self.package_parts) and
                all(part not in ('', '.', '..') for part in self.package_parts),
                'closed package parent required')
        self.parent_fd: int | None = None
        self.root_fd: int | None = None
        self.package_fd: int | None = None
        self.ancestor_chain: tuple[tuple[int, ...], ...] | None = None
        self.root_identity: tuple[int, ...] | None = None
        self.package_chain: tuple[tuple[int, ...], ...] | None = None

    def acquire(self) -> None:
        require(self.root_fd is None, 'root guard already acquired')
        with parent_chain(self.root) as (parent, chain):
            self.parent_fd = os.dup(parent)
            self.ancestor_chain = chain
            self.root_fd = os.open(self.root.name, FLAGS, dir_fd=self.parent_fd)
            root_info = os.fstat(self.root_fd)
            require(stat.S_ISDIR(root_info.st_mode) and root_info.st_uid == os.getuid() and
                    root_info.st_gid == os.getgid() and
                    stat.S_IMODE(root_info.st_mode) == 0o755,
                    'staged root owner/mode differs')
            self.root_identity = dir_identity(root_info)
            parent_fd = self.root_fd
            identities = []
            opened = []
            try:
                for part in self.package_parts:
                    child = os.open(part, FLAGS, dir_fd=parent_fd)
                    opened.append(child)
                    info = os.fstat(child)
                    require(stat.S_ISDIR(info.st_mode) and info.st_uid == os.getuid() and
                            info.st_gid == os.getgid(),
                            'package ancestor owner differs')
                    identities.append(dir_identity(info))
                    parent_fd = child
                require(stat.S_IMODE(os.fstat(parent_fd).st_mode) == 0o700,
                        'Mapper package parent is not owner-only')
                self.package_fd = opened.pop()
                self.package_chain = tuple(identities)
            finally:
                close_all(opened, sys.exception())
        self.attached()

    def attached(self) -> None:
        require(self.parent_fd is not None and self.root_fd is not None and
                self.package_fd is not None and self.ancestor_chain is not None and
                self.root_identity is not None and self.package_chain is not None,
                'root guard not acquired')
        with parent_chain(self.root) as (parent, chain):
            named = os.stat(self.root.name, dir_fd=parent, follow_symlinks=False)
            require(chain == self.ancestor_chain and
                    dir_identity(os.fstat(self.parent_fd)) == chain[-1] and
                    dir_identity(named) == self.root_identity ==
                    dir_identity(os.fstat(self.root_fd)),
                    'staged root pathname detached')
        opened = [os.dup(self.root_fd)]
        try:
            for index, part in enumerate(self.package_parts):
                opened.append(os.open(part, FLAGS, dir_fd=opened[-1]))
                require(dir_identity(os.fstat(opened[-1])) == self.package_chain[index],
                        'Mapper package ancestor detached')
            require(dir_identity(os.fstat(self.package_fd)) == self.package_chain[-1] ==
                    dir_identity(os.fstat(opened[-1])),
                    'Mapper package parent detached')
        finally:
            close_all(opened, sys.exception())

    def close(self, primary: BaseException | None = None) -> None:
        fds = [fd for fd in (self.parent_fd, self.root_fd, self.package_fd)
               if fd is not None]
        self.parent_fd = self.root_fd = self.package_fd = None
        close_all(fds, primary)
