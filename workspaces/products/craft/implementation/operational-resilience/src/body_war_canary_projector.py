"""Argv-only adapter for the existing TypeScript offline projector."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence


@dataclass(frozen=True)
class ProjectorInvocation:
    argv: tuple[str, ...]
    cwd: str


def projector_invocation(repo_root: Path, snapshot_path: Path, raw_pack_path: Path, projected_at: str) -> ProjectorInvocation:
    root = repo_root.resolve()
    for path in (snapshot_path.resolve(), raw_pack_path.resolve()):
        if root not in path.parents:
            raise ValueError("PROJECTOR_INPUT_OUTSIDE_REPOSITORY")
    argv = (
        "/home/vrondelli/.nvm/versions/node/v22.13.0/bin/node", "--import",
        "./projects/domainspec-v2/impl/node_modules/tsx/dist/loader.mjs",
        "projects/domainspec-v2/impl/operational-resilience/src/body-war-runtime-projection-cli.ts",
        "project", str(snapshot_path.resolve()), "--raw-pack", str(raw_pack_path.resolve()), "--at", projected_at,
    )
    return ProjectorInvocation(argv, str(root))


def invoke_projector(invocation: ProjectorInvocation, runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run) -> subprocess.CompletedProcess[str]:
    if isinstance(invocation.argv, str): raise ValueError("PROJECTOR_SHELL_TEXT_FORBIDDEN")
    return runner(invocation.argv, cwd=invocation.cwd, text=True, capture_output=True, timeout=120, check=False)
