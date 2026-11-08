"""Track H task evidence, independent of human gate acceptance."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'docs/plans/relational-theorem-checker/PLAN-SOURCE.json').is_file())
PLAN = HERE/'execution/plan.json'

def read(path):
    return json.loads(Path(path).read_text())

def binding(path):
    p = Path(path).resolve()
    return {'path':str(p.relative_to(ROOT)), 'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}

def write(path, value):
    p = Path(path).resolve()
    assert p.is_relative_to(HERE/'execution'), 'task evidence write scope'
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2)+'\n')
    return binding(p)

def check(ref):
    p = (ROOT/ref['path']).resolve()
    assert p.is_relative_to(ROOT) and binding(p) == ref, 'missing/stale context '+ref['path']
    return p

def begin(task_id, sources, decisions):
    plan = read(PLAN);task = next(t for t in plan['tasks'] if t['id']==task_id)
    assert task['status'] in ['not-started','in-progress']
    inputs = [plan['source_plan']]
    for dep in task['depends_on']:
        t = next(t for t in plan['tasks'] if t['id']==dep)
        assert t['status']=='accepted', 'task prerequisite '+dep
        check(t['receipt']);inputs.append(t['receipt'])
    assert len(sources)+len(inputs)<=14, 'context budget'
    selected = [{'binding':r,'selectors':['task contract / accepted prerequisite']} for r in inputs]
    selected += [{'binding':binding(p),'selectors':selectors} for p,selectors in sources]
    for item in selected:check(item['binding'])
    write(HERE/'execution'/task_id.lower()/'context-pack.json', {
        'schema':'relational.closure-task-context/v1','task':task_id,'mode':'standard','strict_coverage':'pass',
        'sources':selected,'obligations':task['exit_criteria'],'write_scope':str(HERE.relative_to(ROOT)),
        'decisions':decisions,'runtime':'local','delegation':'none'})
    task['status']='in-progress';write(PLAN,plan)

def accept(task_id, paths, finding, controls):
    plan = read(PLAN);task = next(t for t in plan['tasks'] if t['id']==task_id)
    assert task['status']=='in-progress'
    context = read(HERE/'execution'/task_id.lower()/'context-pack.json')
    for item in context['sources']:check(item['binding'])
    assert all(c['result']=='pass' for c in controls)
    outputs = [binding(p) for p in paths]
    receipt = {'schema':'relational.closure-unit-acceptance/v1','task':task_id,'result':'accepted',
               'criteria':task['exit_criteria'],'finding':finding,'controls':controls,'artifacts':outputs,
               'inputs':[x['binding'] for x in context['sources']],'authority_effect':'none'}
    task['receipt']=write(HERE/'execution'/task_id.lower()/'task-acceptance.json',receipt)
    task['status']='accepted';write(PLAN,plan)
    return task['receipt']
