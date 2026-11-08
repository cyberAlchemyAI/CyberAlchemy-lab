"""Successor execution evidence. Writes only v3; accepted predecessors are inputs."""
from pathlib import Path
import glob
import hashlib
import json
import os
import re
import subprocess
import time

BASE = Path(__file__).resolve().parents[1]
ROOT = next(p for p in BASE.parents if (p / 'docs/plans/relational-theorem-checker/PLAN-SOURCE.json').is_file())
V2 = BASE.parent / 'v2'
SOURCE = ROOT / 'docs/plans/relational-theorem-checker/reviews/2026-10-09/post-implementation-planning/plan.json'
PLAN = BASE / 'execution/plan.json'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path).resolve()
    require(path.is_relative_to(BASE), 'write outside v3 execution scope')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def identity(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


def binding(path):
    path = Path(path).resolve()
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path)}


def check(ref):
    relative = Path(ref['path'])
    require(not relative.is_absolute() and '..' not in relative.parts, 'unsafe input binding')
    path = ROOT / relative
    require(path.is_file() and digest(path) == ref['sha256'], 'missing/stale input ' + str(relative))
    return path


def initialize():
    if PLAN.exists():
        require(read(PLAN)['source_plan'] == binding(SOURCE), 'execution source plan changed')
        return
    plan = read(SOURCE)
    plan['source_plan'] = binding(SOURCE)
    plan['status'] = 'executing'
    plan['authorization'] = {'objective': 'run the complete plan', 'extensions': 'Core plus all extensions (Recommended)', 'scope': 'all 12 core and all seven extension units; no deployment/publication/live authority'}
    for task in plan['tasks']:
        task['status'] = 'not-started'
        task['selected'] = True
    write(PLAN, plan)
    sync()


def sync():
    plan = read(PLAN)
    accepted = [t['id'] for t in plan['tasks'] if t['status'] == 'accepted']
    remaining = [{'id': t['id'], 'status': t['status']} for t in plan['tasks'] if t['selected'] and t['status'] != 'accepted']
    write(BASE / 'execution/status.json', {'schema': 'relational.v3-execution-status/v1', 'objective': 'run the complete plan', 'accepted': accepted, 'remaining': remaining, 'goal_complete': not remaining, 'authority_effect': 'none'})
    required=[];optional=[];resolved=[]
    for entry in plan['tasks']:
        extension=entry['selection']=='optional-separate-profile'
        require(entry['status']!='not-needed' or not entry['selected'],'selected work cannot be not-needed')
        if entry['status']=='accepted':continue
        if not entry['selected']:
            require(extension,'required work cannot be resolved as not-needed')
            resolved.append({'id':entry['id'],'resolution':'not-needed'})
        elif extension:optional.append(entry['id'])
        else:required.append(entry['id'])
    write(BASE / 'execution/state-v3.json',{'schema':'relational.execution-state/v3','accepted':accepted,
                                         'remaining_required':required,'remaining_optional':optional,
                                         'resolved_optional':resolved,'complete':not(required or optional),'authority_effect':'none'})


def task(id):
    return next(t for t in read(PLAN)['tasks'] if t['id'] == id)


def context(id, selectors, decisions):
    initialize()
    t = task(id)
    require(len(selectors) <= 14, 'context file budget exceeded')
    dependencies = []
    for predecessor in t['depends_on']:
        p = task(predecessor)
        require(p['status'] == 'accepted', 'dependency not accepted ' + predecessor)
        receipt = read(check(p['receipt']))
        for b in receipt['artifacts'] + receipt['inputs']:
            check(b)
        dependencies.append(p['receipt'])
    sources = []
    for path, selector, excerpt, obligations in selectors:
        require(excerpt and excerpt in Path(path).read_text(), 'invalid context selector ' + selector)
        sources.append({**binding(path), 'selector': selector, 'excerpt': excerpt, 'obligations': obligations})
    require(sum(len(s['excerpt'].splitlines()) for s in sources) <= 280, 'context excerpt budget exceeded')
    criteria = [{'id': id + '-C' + str(n + 1), 'criterion': c} for n, c in enumerate(t['acceptance'])]
    covered = {o for s in sources for o in s['obligations']}
    require({c['id'] for c in criteria} <= covered, 'uncovered task obligation')
    pack = {'schema': 'relational.v3-task-context/v1', 'task': id, 'mode': 'standard', 'write_scope': t['write_scope'], 'shared_write_scope': str((BASE / 'execution').relative_to(ROOT)), 'source_plan': binding(SOURCE), 'sources': sources, 'criteria': criteria, 'dependency_receipts': dependencies, 'decisions': decisions, 'strict_coverage': 'pass', 'delegation': 'none', 'authority_effect': 'none'}
    write(BASE / id.lower() / 'context-pack.json', pack)
    plan = read(PLAN)
    next(x for x in plan['tasks'] if x['id'] == id)['status'] = 'in-progress'
    write(PLAN, plan)
    sync()
    return pack


def lean_path():
    formal = BASE.parent / 'v1/formal'
    lean = formal / '.toolcache/lean-4.33.1-linux/bin/lean'
    lock = read(formal / 'toolchain-lock.json')
    require(digest(lean) == lock['lean_binary_sha256'], 'compiler drift')
    require(digest(lean.parent.parent / 'lib/lean/libleanshared.so') == lock['lean_shared_library_sha256'], 'kernel shared-library drift')
    require(subprocess.check_output([str(lean), '--version'], text=True).strip() == lock['version_output'], 'version drift')
    return lean


def predecessor_imports():
    deps_path = V2 / 's13/build/dependencies.json'
    deps = read(deps_path)
    for module in deps['modules']:
        check(module['source'])
        check(module['olean'])
    return deps_path.parent, binding(deps_path)


def compile_modules(build, modules, imports=(), timeout=60):
    build = Path(build).resolve()
    require(build.is_relative_to(BASE), 'compile output outside successor')
    build.mkdir(parents=True, exist_ok=True)
    lean = lean_path()
    records = []
    for name, path in modules:
        source = Path(path)
        require(not re.search(r'^\s*axiom\s|\bsorry\b', source.read_text(), re.M), 'admitted/custom axiom source')
        target = build / (name + '.lean')
        if target != source:
            target.write_bytes(source.read_bytes())
        start = time.monotonic()
        result = subprocess.run([str(lean), '-o', str(target.with_suffix('.olean')), str(target)], cwd=build, env={**os.environ, 'LEAN_PATH': os.pathsep.join(map(str, [build, *imports]))}, text=True, capture_output=True, timeout=timeout)
        output = result.stdout + result.stderr
        require(result.returncode == 0 and 'warning:' not in output and 'sorryAx' not in output, 'Lean failure ' + name + '\n' + output)
        records.append({'module': name, 'source': binding(source), 'olean': binding(target.with_suffix('.olean')), 'seconds': time.monotonic() - start, 'output': output})
    return records


def accept(id, findings, controls, extra=()):
    t = task(id)
    require(t['status'] == 'in-progress', 'task not executing')
    require(len(findings) == len(t['acceptance']), 'missing completion criterion')
    ctx = read(BASE / id.lower() / 'context-pack.json')
    artifacts = []
    for pattern in t['outputs']:
        files = sorted((BASE / id.lower()).glob(pattern))
        require(bool(files), 'missing deliverable ' + pattern)
        artifacts.extend(binding(p) for p in files if p.is_file())
    artifacts += [binding(BASE / id.lower() / 'context-pack.json')] + [binding(p) for p in extra]
    inputs = [dict(path=x['path'], sha256=x['sha256']) for x in ctx['sources']] + ctx['dependency_receipts'] + [ctx['source_plan']]
    for ref in artifacts + inputs:
        check(ref)
    if id == 'P11':
        feedback = read(BASE / 'p11/human-feedback.json')
        require(feedback.get('actual_answer') and feedback.get('assessment_scope') == 'v3-worked-packet', 'actual successor human feedback is required')
        check(feedback['packet'])
    receipt = {'schema': 'relational.v3-task-acceptance/v1', 'task': id, 'result': 'accepted', 'review': 'author implementation/review; bounded candidate', 'criteria': [{'criterion': c, 'evidence': f} for c, f in zip(t['acceptance'], findings)], 'controls': controls, 'artifacts': artifacts, 'inputs': inputs, 'authority_effect': 'none'}
    path = BASE / id.lower() / 'task-acceptance.json'
    write(path, receipt)
    plan = read(PLAN)
    entry = next(x for x in plan['tasks'] if x['id'] == id)
    entry['status'] = 'accepted'
    entry['receipt'] = binding(path)
    write(PLAN, plan)
    sync()
