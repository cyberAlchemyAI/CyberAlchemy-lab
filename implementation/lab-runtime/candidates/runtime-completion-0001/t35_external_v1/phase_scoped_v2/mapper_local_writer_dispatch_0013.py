"""Dispatch uses each verified byte object directly; no check/use reread."""
import hashlib
import json
from pathlib import Path
import sys
import types


def verified_read(row):
    raw=Path(row['path']).read_bytes()
    if len(raw)!=row['size_bytes'] or hashlib.sha256(raw).hexdigest()!=row['sha256']:raise RuntimeError('SELECTED_DRIFT')
    return raw


def check(inputs):
    for row in inputs['bindings']:verified_read(row)


def load_loader(inputs):
    raw=verified_read(inputs['loader'])
    name='selected_local_loader_0013'
    if name in sys.modules:raise RuntimeError('MODULE_COLLISION')
    loader=types.ModuleType(name);sys.modules[name]=loader
    exec(compile(raw,inputs['loader']['path'],'exec'),loader.__dict__)
    return loader


def load_plan(inputs):
    raw=verified_read(inputs['plan'])
    return json.loads(raw)


def run(inputs):
    if sys.argv[1:]!=['--execute-once']:raise RuntimeError('EXPLICIT_ONE_SHOT_ARGUMENT_REQUIRED')
    check(inputs);loader=load_loader(inputs);candidate=loader.load(inputs);plan=load_plan(inputs)
    result=candidate.execute(plan)
    # The candidate leaves only provisional UNKNOWN on disk. No PASS is emitted
    # until evidence closure/readback AND this final source check have succeeded.
    check(inputs)
    print(json.dumps(result,sort_keys=True),flush=True)
    return result
