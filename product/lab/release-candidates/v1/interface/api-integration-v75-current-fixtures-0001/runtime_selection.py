"""Stable API adapter for bootstrap-selected installed Source inputs.

Copied into the portable API package as runtime_selection.py. No wire field,
working directory or environment variable selects the provider or its root.
"""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[6]
PROVIDER_NAME = 'cal_installed_runtime_selection_v1'
PROVIDER_PATH = ROOT/'implementation/lab-runtime/local-host/t25-integrated-runtime-0004/installed_selection.py'


def provider():
    selected = sys.modules.get(PROVIDER_NAME)
    if selected is None or Path(selected.__file__)!=PROVIDER_PATH:
        raise ValueError('trusted installed selection provider was not captured before API import')
    selected.require_runtime_ready()
    if selected.root()!=ROOT:
        raise ValueError('installed API and bootstrap repository roots differ')
    return selected


def binding(slot):
    return provider().binding(slot)


def value(slot):
    return provider().value(slot)


def guard():
    return provider().guard()


def member_pin(slot, relative):
    selected = provider()
    selected.relative(relative)
    row = selected.binding(slot)
    body = selected.parse(selected.capture(ROOT/row['path'],row['sha256']))
    rows = [item for item in body['files'] if item['path']==relative]
    if len(rows)!=1 or set(rows[0])!={'path','sha256'}:
        raise ValueError('independently selected metadata does not bind the requested public code member')
    return rows[0]['sha256']


def actual_python():
    """The public child launcher is distinct from the actual loaded ELF."""
    selected = provider()
    path = Path(sys._base_executable)
    expected = Path(selected.value('native.root'))/'bin/python'
    if path!=expected:
        raise ValueError('actual native interpreter path differs from selected installation')
    proof = selected.process_proof()
    if proof['actual_python']!=str(path) or proof['all_executable_maps_selected'] is not True:
        raise ValueError('actual native executable mapping proof differs')
    return path


def fixture_record(name):
    """One immutable dataset body selected by the public package contract."""
    selected=provider();selected.guard();entry=dict(selected.current().package['fixture_records'][name])
    selected.closed(entry,('path','sha256','version_ref'),'closed public fixture record required')
    selected.relative(entry['path'])
    rows=[row for row in selected.current().package['members'] if row['path']==entry['path']]
    if len(rows)!=1 or rows[0]['sha256']!=entry['sha256']:
        raise ValueError('fixture record outside independently selected stable public members')
    selected.capture(ROOT/entry['path'],entry['sha256'])
    return dict(entry)
