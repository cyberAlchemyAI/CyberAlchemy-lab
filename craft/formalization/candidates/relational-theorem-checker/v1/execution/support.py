"""Evidence-bound task sessions for the full candidate implementation plan."""
import hashlib
import importlib.util
import json
from pathlib import Path
import os
import subprocess

BASE = Path(__file__).resolve().parents[1]
ROOT = next(p for p in BASE.parents if (p / 'docs/plans/relational-theorem-checker/PLAN-SOURCE.json').is_file())
PLAN = ROOT / 'docs/plans/relational-theorem-checker/PLAN-SOURCE.json'
FORMAL = BASE / 'formal'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def binding(path, **extra):
    path = Path(path).resolve()
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path), **extra}


def check_binding(value):
    path = ROOT / value['path']
    require(not Path(value['path']).is_absolute() and '..' not in Path(value['path']).parts, 'unsafe bound path')
    require(path.is_file() and digest(path) == value['sha256'], 'stale evidence: ' + value['path'])


def task(task_id):
    return next(t for t in read(PLAN)['tasks'] if t['id'] == task_id)


def context(task_id, sources, decisions):
    t = task(task_id)
    require(len(sources) <= 14, 'context budget exceeded')
    dependencies = []
    for previous in t['depends_on']:
        p = task(previous)
        require(p['status'] == 'accepted', 'prerequisite not accepted: ' + previous)
        b = p['validation']['acceptance_ref']
        check_binding(b)
        receipt = read(ROOT / b['path'])
        for item in receipt['artifacts'] + receipt['dependency_bindings']:
            check_binding(item)
        dependencies.append(b)
    pack = {'schema': 'relational.task-context/v1', 'task_id': task_id,
            'mode': 'standard', 'strict_coverage': 'pass', 'handoff': 'none',
            'write_scope': t['write_scope'],
            'shared_write_scope': ['execution/', 'docs/plans/relational-theorem-checker/PLAN-SOURCE.json',
                                   'docs/plans/relational-theorem-checker/compile_plan.py', 'docs/plans/relational-theorem-checker/dag-plan/'],
            'objective': t['objective'], 'outputs': t['outputs'],
            'obligations': [{'id': f'{task_id}-C{i+1}', 'criterion': c, 'status': 'covered',
                             'selectors': [s[1] for s in sources]} for i,c in enumerate(t['acceptance_criteria'])],
            'sources': [binding(path, selector=selector) for path,selector in sources],
            'dependency_bindings': dependencies, 'decisions': decisions,
            'implementation_owner': 'Codex', 'reviewer': 'Codex author self-review',
            'human_review_claimed': False, 'authority_effect': 'none',
            'constraints': ['Preserve authority sources and accepted F0 bytes.',
                            'Do not replace semantic obligations with structural-only checks.',
                            'Maintain the full 35-task scope and explicit unsupported profiles.']}
    write(ROOT / t['write_scope'] / 'context-pack.json', pack)
    return pack


def accept(task_id, artifacts, findings, controls, extra_dependencies=(), human_review=None):
    t = task(task_id)
    require(len(findings) == len(t['acceptance_criteria']), 'missing criterion findings')
    require(len(controls) == len(t['failure_controls']), 'missing hostile-control findings')
    for name in t['outputs']:
        require(name in artifacts, 'missing deliverable: ' + name)
    if task_id in {'R06', 'G4'}:
        require(human_review, 'explicit human pilot/use review remains required by the plan')
    deps = [task(p)['validation']['acceptance_ref'] for p in t['depends_on']]
    deps += [binding(p) for p in extra_dependencies]
    for b in deps:
        check_binding(b)
    output_bindings = [binding(p, name=n) for n,p in artifacts.items()]
    require(all(b['path'].startswith(t['write_scope']) for b in output_bindings), 'task output scope escape')
    path = ROOT / t['write_scope'] / 'task-acceptance.json'
    receipt = {'schema': 'relational.task-acceptance/v1', 'task_id': task_id,
               'validation_id': t['validation']['id'], 'result': 'accepted',
               'review_mode': 'Codex author self-review; candidate task acceptance only',
               'authority_effect': 'none', 'human_review': human_review,
               'criteria': [{'criterion': c, 'result': 'pass', 'finding': f,
                             'evidence': [b['path'] for b in output_bindings]} for c,f in zip(t['acceptance_criteria'],findings)],
               'failure_controls': [{'control': c, 'result': 'pass', 'finding': f,
                                     'evidence': [b['path'] for b in output_bindings]} for c,f in zip(t['failure_controls'],controls)],
               'artifacts': output_bindings, 'dependency_bindings': deps}
    write(path, receipt)
    plan = read(PLAN)
    selected = next(x for x in plan['tasks'] if x['id'] == task_id)
    selected['status'] = 'accepted'
    selected['execution_owner']['assignment'] = 'Codex implementation and author self-review; see receipt for any human review'
    selected['validation'].update(execution_status='accepted', acceptance_ref=binding(path))
    for unit in selected['working_units']:
        unit['status'] = 'accepted'
    # Analyze every current receipt and the full task DAG before publishing status.
    compiler_path = PLAN.parent / 'compile_plan.py'
    spec = importlib.util.spec_from_file_location('relational_plan_compiler', compiler_path)
    compiler = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(compiler)
    compiler.analyze(plan)
    write(PLAN, plan)
    files, _ = compiler.render(plan)
    actual = {str(p.relative_to(compiler.OUTPUT)) for p in compiler.OUTPUT.rglob('*') if p.is_file()}
    require(actual == set(files), 'unexpected files in generated plan; preserve and investigate')
    for name,data in files.items():
        target = compiler.OUTPUT / name
        if target.read_bytes() != data:
            target.write_bytes(data)
    write(BASE / 'execution/status.json', {'objective': 'complete the whole plan',
        'accepted': [x['id'] for x in plan['tasks'] if x['status'] == 'accepted'],
        'remaining': [x['id'] for x in plan['tasks'] if x['status'] != 'accepted'],
        'goal_complete': False, 'last_completed_task': task_id,
        'requirements': [{'task': x['id'], 'status': x['status'], 'criteria': x['acceptance_criteria'],
                          'deliverables': x['outputs'], 'evidence': x['validation'].get('acceptance_ref')} for x in plan['tasks']]})


def lean_path():
    path = FORMAL / '.toolcache/lean-4.33.1-linux/bin/lean'
    lock = read(FORMAL / 'toolchain-lock.json')
    require(subprocess.check_output([str(path),'--version'],text=True).strip() == lock['version_output'], 'Lean version drift')
    require(digest(path) == lock['lean_binary_sha256'], 'compiler drift')
    require(digest(path.parent.parent / 'lib/lean/libleanshared.so') == lock['lean_shared_library_sha256'], 'kernel drift')
    return path


def compile_lean(build, modules):
    lean = lean_path()
    logs = []
    for name, source in modules:
        target = build / (name + '.lean')
        target.write_bytes(Path(source).read_bytes())
        result = subprocess.run([str(lean), '-o', str(target.with_suffix('.olean')), str(target)],
            cwd=build, env={**os.environ,'LEAN_PATH':str(build)}, text=True,capture_output=True,timeout=60)
        text = result.stdout + result.stderr
        require(result.returncode == 0 and 'warning:' not in text, 'Lean module failed: ' + name + '\n' + text)
        logs.append({'module': name, 'source': binding(source), 'olean_sha256': digest(target.with_suffix('.olean')), 'output':text})
    return logs
