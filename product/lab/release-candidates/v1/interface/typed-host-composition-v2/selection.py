"""Closed independent routing and complete schema destination selection.

These checks provide no Actor, permission, semantic review or source authority.
The actual host must supply the selected route and original proposal bytes.
"""
from pathlib import PurePosixPath


class SelectionFault(ValueError):
    pass


def require(value, message):
    if not value:
        raise SelectionFault(message)


def schema_paths(route, proposal):
    """Require a bijection with the complete original proposal schema inventory."""
    rows = route['schema_destinations']
    require(type(rows) is list and len(rows) <= 1000,
            'schema destination inventory exceeds the original frame array bound')
    expected = proposal['schema_bindings']
    require(type(expected) is list and len(expected) <= 1000,
            'proposal schema inventory exceeds the original frame array bound')
    bindings, paths, selected = {}, set(), {}
    for row in rows:
        require(type(row) is dict and set(row) == {'schema_binding', 'runtime_schema_path'},
                'closed schema destination row required')
        binding, path = row['schema_binding'], row['runtime_schema_path']
        require(type(binding) is dict and set(binding) == {'ref', 'sha256'}
                and type(binding['ref']) is str and binding['ref']
                and type(binding['sha256']) is str and len(binding['sha256']) == 64
                and all(c in '0123456789abcdef' for c in binding['sha256']),
                'closed exact schema binding required')
        require(type(path) is str and path.startswith('runtime/schemas/')
                and path.endswith('.json') and '\\' not in path
                and not PurePosixPath(path).is_absolute()
                and all(segment not in ('', '.', '..') for segment in path.split('/'))
                and PurePosixPath(path).as_posix() == path,
                'schema destination must be a canonical relative runtime path without dot segments')
        require(binding['ref'] not in bindings and path not in paths,
                'schema reference and runtime destination must each be unique')
        bindings[binding['ref']] = binding
        selected[binding['ref']] = path
        paths.add(path)
    require(all(type(b) is dict and set(b) == {'ref', 'sha256'} for b in expected),
            'closed proposal schema bindings required')
    require(len({b['ref'] for b in expected}) == len(expected)
            and len(expected) == len(bindings)
            and all(bindings.get(b['ref']) == b for b in expected),
            'complete exact schema inventory differs from independently selected destinations')
    return selected


def target_metadata(proposal, manifest):
    """Every target selects the exact independently provisioned metadata binding."""
    targets = proposal['targets']
    require(type(targets) is list and 1 <= len(targets) <= 64,
            'original complete target bound required')
    versions = [target['artifact']['version_ref'] for target in targets]
    require(len(set(versions)) == len(versions), 'duplicate candidate target revision')
    for target in targets:
        binding = manifest['target_metadata'].get(target['artifact']['version_ref'])
        require(binding is not None and binding == target['candidate_binding'],
                'target metadata differs from independently provisioned version selection')
