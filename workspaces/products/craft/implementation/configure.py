#!/usr/bin/env python3
"""Link shared dependencies to local packages without modifying shared installs."""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAB = next(parent for parent in (ROOT, *ROOT.parents) if (parent / 'authority/definitions/registry.json').is_file() and (parent / 'implementation/lab-runtime').is_dir())
UPSTREAM = LAB.parent / 'cyberAlchemy-v2'
CORE = ROOT / 'cli'
ALCH = ROOT / 'alchlang'
AI = ROOT / 'profiles/ai'
DIST = UPSTREAM / 'output/craft-connected-applications-2026-11-02/distribution-repaired'


def link(target, source, allow_missing=False):
    if not source.exists() and not allow_missing:
        raise ValueError('Missing shared dependency: ' + str(source))
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_symlink():
        if target.resolve() == source.resolve():
            return
        raise ValueError('Conflicting dependency link: ' + str(target))
    if target.exists():
        raise ValueError('Refusing to overwrite dependency: ' + str(target))
    target.symlink_to(os.path.relpath(source, target.parent), target_is_directory=source.is_dir())


def dependencies(home, shared, overrides):
    modules = home / 'node_modules'
    modules.mkdir(exist_ok=True)
    local_bins = {}
    for source in overrides.values():
        metadata = json.loads((source / 'package.json').read_text())
        bins = metadata.get('bin', {})
        if isinstance(bins, str):
            bins = {metadata['name'].split('/')[-1]: bins}
        local_bins.update({name: source / relative for name, relative in bins.items()})
    for item in shared.iterdir():
        if item.name.startswith('@'):
            for member in item.iterdir():
                name = item.name + '/' + member.name
                if name not in overrides:
                    link(modules / name, member)
        elif item.name == '.bin':
            for member in item.iterdir():
                if member.exists() and member.name not in local_bins:
                    link(modules / '.bin' / member.name, member)
        elif not item.name.startswith('.') and item.name not in overrides:
            link(modules / item.name, item)
    for name, source in overrides.items():
        link(modules / name, source)
    for name, source in local_bins.items():
        target = modules / '.bin' / name
        if target.is_symlink() and target.resolve() != source.resolve():
            # Repair only the shared aliases created by the original import setup.
            if not str(target.resolve()).startswith(str(DIST) + os.sep):
                raise ValueError('Conflicting command alias: ' + str(target))
            target.unlink()
        # Build outputs may not exist on a first configuration; package.json owns the alias.
        link(target, source, allow_missing=True)
        if source.is_file():
            source.chmod(source.stat().st_mode | 0o111)


if __name__ == '__main__':
    dependencies(CORE, UPSTREAM / 'craft/projects/domainspec-v2/impl/cli/node_modules', {})
    dependencies(ALCH, UPSTREAM / 'language/capabilities/alchlang/plans/general-compiler-v1/implementation/node_modules',
                 {'@domainspec-v2/cli': CORE, '@craft/ai-profiles': AI})
    dependencies(AI, DIST / 'agent-consumer/node_modules',
                 {'@domainspec-v2/cli': CORE, '@cyberalchemy/alchlang': ALCH, '@craft/ai-profiles': AI})
    # Implementation-level resolution serves tests and generated local consumers.
    dependencies(ROOT, DIST / 'agent-consumer/node_modules',
                 {'@domainspec-v2/cli': CORE, '@cyberalchemy/alchlang': ALCH, '@craft/ai-profiles': AI})
    for name in ['typescript', 'tsx']:
        target = ROOT / 'node_modules' / name
        if not target.exists():
            link(target, ALCH / 'node_modules' / name)
    dependencies(ROOT / 'test-derivation-engine',
                 UPSTREAM / 'craft/projects/domainspec-v2/impl/test-derivation-engine/node_modules', {})
    print(json.dumps({'status': 'configured', 'copied_runtime_bytes': 0,
                      'local_packages': [str(x.relative_to(LAB)) for x in [CORE, ALCH, AI]]}))
