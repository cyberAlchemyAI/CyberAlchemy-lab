#!/usr/bin/env python3
"""Explicit umbrella/sibling source mounts; no search, redirects, or routing fallback."""
from __future__ import annotations
import json
from pathlib import Path, PurePosixPath

PACKAGE_ROOT = Path(__file__).resolve().parents[1]


class Layout:
    def __init__(self, package_root: Path = PACKAGE_ROOT):
        self.package_root = package_root.resolve()
        self.local_root = self.package_root.parent
        if self.package_root.name != 'agent-routing' or self.local_root.name != 'cyberAlchemy-v2':
            raise ValueError('unsupported routing package location')
        parent = self.local_root.parent
        self.mode = 'umbrella' if parent.name == 'domainspec-core' else 'sibling'
        self.core_root = parent if self.mode == 'umbrella' else parent / 'domainspec-core'
        # Do not accept a mount silently redirected to a different checkout.
        if self.core_root.resolve() != self.core_root:
            raise ValueError('domainspec-core mount must not be a symlink')
        self.agents_ref = 'AGENTS.md' if self.mode == 'umbrella' else 'cyberAlchemy-v2/AGENTS.md'

    @staticmethod
    def bounded(root: Path, value: str) -> Path:
        parts = value.split('/')
        if not value or '\\' in value or PurePosixPath(value).is_absolute() or any(
            part in {'', '.', '..', '.git', 'node_modules', 'arcanum', '.agents', '.claude'} for part in parts
        ):
            raise ValueError(f'unsafe routing source: {value}')
        path = (root / value).resolve()
        relative = path.relative_to(root.resolve())
        if any(part in {'.git', 'node_modules', 'arcanum', '.agents', '.claude'} for part in relative.parts):
            raise ValueError(f'forbidden resolved routing source: {value}')
        return path

    def resolve_ref(self, value: str) -> Path:
        if value == 'cyberAlchemy-v2':
            return self.local_root
        if value.startswith('cyberAlchemy-v2/'):
            return self.bounded(self.local_root, value[len('cyberAlchemy-v2/'):])
        if value == 'AGENTS.md':
            return self.bounded(self.core_root if self.mode == 'umbrella' else self.local_root, value)
        if value == 'SUBMODULE-DISCIPLINE.md' or value.startswith('projects/domainspec-v2/') or value.startswith('toolchains/node-typescript/'):
            return self.bounded(self.core_root, value)
        raise ValueError(f'undeclared routing source mount: {value}')

    def build_paths(self) -> dict:
        refs = [self.agents_ref, 'cyberAlchemy-v2/SOURCE-MAP.md',
                'cyberAlchemy-v2/authority/definitions/DEFINITIONS.md',
                'cyberAlchemy-v2/agent-routing/product-capability.json',
                'cyberAlchemy-v2/agent-routing/ontology.json',
                'projects/domainspec-v2/impl/tools/minted-project/compiler.ts',
                'projects/domainspec-v2/impl/tools/minted-project/views.ts',
                'projects/domainspec-v2/impl/package.json']
        return {'mode': self.mode, 'root_instruction_ref': self.agents_ref,
                'paths': {ref: str(self.resolve_ref(ref)) for ref in refs}}


if __name__ == '__main__':
    print(json.dumps(Layout().build_paths(), sort_keys=True))
