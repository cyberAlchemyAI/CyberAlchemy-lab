"""Independent, inert source-selection check for public probe wrapper 0002."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from unittest import mock

candidate = Path(__file__).resolve().parent.parent / 'context-public-namespace-probe-effect-0002'
sys.path.insert(0, str(candidate))
import wrapper as W

def need(condition, code):
    if not condition:
        raise RuntimeError(code)

freeze_raw = (candidate / 'freeze.json').read_bytes()
need(hashlib.sha256(freeze_raw).hexdigest() == '57ed09a70c67da497bbfae7f5fe1b47ecb38cba849ff68d830e27b00dce34bd5', 'FREEZE_SHA')
freeze = json.loads(freeze_raw)
need(set(freeze['bindings']) == {'HANDOFF.md', 'wrapper.py', 'test_wrapper.py'}, 'BINDING_SET')
for name, digest in freeze['bindings'].items():
    need(hashlib.sha256((candidate / name).read_bytes()).hexdigest() == digest, 'BINDING_SHA')
need(hashlib.sha256(W.CORRECTION_REVIEW.read_bytes()).hexdigest() == W.CORRECTION_REVIEW_SHA, 'HOLD_REVIEW_SHA')

calls = []
def refuse_second_loader(*args, **kwargs):
    calls.append((args, kwargs))
    raise AssertionError('unchecked second pathname load')

with mock.patch.object(importlib.util, 'spec_from_file_location', side_effect=refuse_second_loader):
    release, observer = W.basis()
need(calls == [], 'SECOND_LOADER_CALLED')
need(observer.R is release, 'OBSERVER_RELEASE')
need(observer.run_observer.__kwdefaults__['preflight'] is release.preflight, 'PREFLIGHT_DEFAULT')
need(observer.run_observer.__kwdefaults__['read_file'] is release.check_file, 'READ_DEFAULT')
need(observer.run_observer.__kwdefaults__['docker_call'].__code__.co_filename == str(W.PREVIOUS/'release.py'), 'DOCKER_DEFAULT_CHECKED_SOURCE')
need(release.docker_call is W.selected_docker_call, 'SELECTED_DOCKER_CALL')
need(release.EFFECT_ENABLED is False and observer.EFFECT_ENABLED is False, 'EFFECT_DISABLED')
raw = W.read_file(W.PREVIOUS/'observer.py', W.PREVIOUS_MEMBERS['observer.py'])
projected = W.observer_projection(raw)
need(projected.count(W.OBSERVER_IMPORT_POSTIMAGE) == 1, 'PROJECTION_COUNT')
need(W.OBSERVER_IMPORT_PREIMAGE not in projected, 'PREIMAGE_REMNANT')
need(projected.replace(W.OBSERVER_IMPORT_POSTIMAGE, W.OBSERVER_IMPORT_PREIMAGE, 1) == raw, 'PROJECTION_INVERSE')
print(json.dumps({'status':'PASS_INERT_SELECTION', 'second_loader_calls':len(calls),
                  'definition_defaults_checked':True, 'effect':'UNRUN'}, sort_keys=True))
