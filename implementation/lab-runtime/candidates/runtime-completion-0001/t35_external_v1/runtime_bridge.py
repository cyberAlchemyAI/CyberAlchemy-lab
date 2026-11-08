"""Standalone selected-snapshot bridge for generated roles; no effect API."""
from contextlib import contextmanager
from contextvars import ContextVar

_ACTIVE = ContextVar('t35_selected_capture', default=None)


@contextmanager
def selected_read_scope(capture):
    if _ACTIVE.get() is not None or capture is None:
        raise ValueError('one selected read scope required')
    token = _ACTIVE.set(capture)
    try:
        yield
    finally:
        _ACTIVE.reset(token)


def read(row):
    capture = _ACTIVE.get()
    if capture is None:
        raise ValueError('no active Root-selected binding capture')
    return capture.read(row)


def verify_inputs(rows, *, selected_external=()):
    if type(rows) is not list or type(selected_external) not in (tuple, list):
        raise ValueError('closed selected input list required')
    external = []
    seen = set()
    for row in rows:
        if type(row) is not dict or set(row) != {'path', 'sha256'} or row['path'] in seen:
            raise ValueError('duplicate or malformed selected source input')
        seen.add(row['path'])
        if row['path'].startswith('/'):
            external.append(row)
        read(row)
    if external != list(selected_external):
        raise ValueError('external input selection differs')
    return len(rows)


def run_native(*_args, **_kwargs):
    raise RuntimeError('No selected native executor or phase effect capability is installed')
