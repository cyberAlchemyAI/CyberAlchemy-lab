"""Actual source-bound Context delivery under current owned host permission."""

def _t35_effect_refused():
    raise RuntimeError('Generated T35 role effects require the uninstalled T02 custody gate')

def _t35_binding_path(path):
    from pathlib import Path, PurePosixPath
    value = Path(path)
    name = value.as_posix()
    if not value.is_absolute() or '//' in name or any((x in ('.', '..') for x in name.split('/'))):
        raise ValueError('noncanonical generated binding path')
    family = PurePosixPath(Path(__file__).resolve().parent)
    snapshot = PurePosixPath(Path(__file__).resolve().parent.parents[5])
    item = PurePosixPath(name)
    if family in item.parents:
        return name
    if snapshot in item.parents:
        return str(item.relative_to(snapshot))
    raise ValueError('generated path outside external output and input snapshot')
