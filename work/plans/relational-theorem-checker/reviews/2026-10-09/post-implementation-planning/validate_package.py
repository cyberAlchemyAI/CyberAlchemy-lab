"""Read-only validation of a plan, its coverage and current planning inputs.

Writes only this package's validation report; never runs predecessor task runners,
kernel replay or application. This does not qualify successor implementation.
"""
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'docs/plans/relational-theorem-checker/PLAN-SOURCE.json').is_file())


def read(path):
    return json.loads(path.read_text())


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def check_binding(binding):
    relative = Path(binding['path'])
    require(not relative.is_absolute() and '..' not in relative.parts, 'unsafe binding')
    path = ROOT / relative
    require(path.is_file(), 'missing input ' + str(relative))
    require(hashlib.sha256(path.read_bytes()).hexdigest() == binding['sha256'], 'changed input ' + str(relative))
    return path


def main():
    plan = read(HERE / 'plan.json')
    coverage = read(HERE / 'coverage.json')
    tasks = plan['tasks']
    ids = [t['id'] for t in tasks]
    require(len(ids) == len(set(ids)), 'duplicate successor unit')
    require(plan['first_step'] == 'P00' and plan['formalization_first'], 'formalization is not first')
    require([t['id'] for t in tasks if not t['depends_on']] == ['P00'], 'unexpected ungrounded root')
    require(len(plan['core_units']) == 12 and len(plan['optional_units']) == 7, 'selection inventory drift')
    require(set(plan['core_units'] + plan['optional_units']) == set(ids), 'unselected unit')
    order, pending = [], {t['id']: set(t['depends_on']) for t in tasks}
    while pending:
        ready = sorted(k for k, v in pending.items() if not v)
        require(bool(ready), 'dependency cycle')
        for id in ready:
            order.append(id)
            pending.pop(id)
        for v in pending.values():
            v.difference_update(ready)
    for t in tasks:
        require(set(t['depends_on']) <= set(ids), 'unknown dependency')
        require(t['status'] == 'planned-not-implemented' and t['authority_effect'] == 'none', 'false execution claim')
        require(t['write_scope'].startswith(plan['implementation_namespace'] + '/'), 'write scope escapes successor')
        for field in ['problem', 'implementation_steps', 'contract', 'formal_targets', 'negative_controls', 'acceptance', 'outputs']:
            require(bool(t[field]), 'missing task detail ' + t['id'] + ':' + field)
    v2 = ROOT / 'craft/formalization/candidates/relational-theorem-checker/v2'
    predecessor = read(v2 / 'execution/plan.json')['tasks']
    require({x['id'] for x in predecessor} == {x['id'] for x in coverage['predecessor_tasks']}, 'predecessor coverage gap')
    require(len(coverage['predecessor_tasks']) == 19, 'predecessor count')
    for t in coverage['predecessor_tasks']:
        old = next(x for x in predecessor if x['id'] == t['id'])
        require(t['current_status'] == old['status'], 'stale predecessor state')
        check_binding(t['receipt'])
        require(set(t['next_units']) <= set(ids), 'unknown successor task reference')
    status = read(v2 / 'execution/status.json')
    require(status['goal_complete'] and not status['remaining'] and len(status['accepted']) == 18, 'completed baseline changed')
    final = read(v2 / 's14/final-review.json')
    require(final['whole_plan_complete'] and final['authority_effect'] == 'none', 'invalid completed baseline')
    require(final['original_human_gates'] == [{'id': 'R06', 'status': 'not-started'}, {'id': 'G4', 'status': 'not-started'}], 'original human scope changed')
    check_binding(final['reviewed_packet'])
    check_binding(final['human_feedback'])
    inventory = read(check_binding(coverage['retained_definition_inventory']))
    require(len(coverage['concepts']) == 17 and {x['name'] for x in coverage['concepts']} == {x['name'] for x in inventory['proposed_definitions']}, 'concept coverage gap')
    require(len(coverage['relations']) == 41 and {x['id'] for x in coverage['relations']} == {x['id'] for x in inventory['relations']}, 'relation coverage gap')
    selected = [x for x in coverage['relations'] if x['selection'] == 'selected-fragment']
    require(len(selected) == 5, 'selected-fragment expansion')
    for x in coverage['concepts'] + coverage['relations']:
        require(bool(x['next_units']) and set(x['next_units']) <= set(ids), 'coverage has unresolved unit')
    declarations = read(HERE / 'retained-declaration-review.json')['declarations']
    require(len(declarations) == 176 and {x['id'] for x in declarations} == {x['id'] for x in inventory['formal_definitions']}, 'retained declaration coverage gap')
    source_text = {}
    for d in inventory['formal_definitions']:
        b = d['source']
        if b['path'] not in source_text:
            source_text[b['path']] = check_binding(b).read_text()
        excerpt = d['definition_excerpt']
        require(hashlib.sha256(excerpt.encode()).hexdigest() == d['definition_excerpt_sha256'], 'changed inventory excerpt')
        tail = ''.join(source_text[b['path']].splitlines(keepends=True)[d['line'] - 1:])
        require(tail.startswith(excerpt), 'stale declaration excerpt ' + d['id'])
    for d in declarations:
        require(set(d['next_units']) <= set(ids), 'unknown declaration integration unit')
    bindings = read(HERE / 'source-bindings.json')['bindings']
    for b in bindings:
        check_binding(b)
    link_count = 0
    for document in HERE.glob('*.md'):
        for target in re.findall(r'\]\((/[^)]+)\)', document.read_text()):
            path = Path(re.sub(r':\d+$', '', target))
            require(path.is_file(), 'broken document link ' + str(path))
            link_count += 1
    probe = read(HERE / 'readonly-probe-report.json')
    require([x['outcome'] for x in probe['checks']] == ['accepted', 'rejected', 'accepted', 'rejected'], 'probe result mismatch')
    report = {
        'schema': 'relational.planning-validation/v1', 'result': 'pass',
        'status': 'plan-and-author-review-complete; successor-not-implemented',
        'core_units': 12, 'optional_units': 7, 'predecessor_tasks': 19,
        'concepts': 17, 'relations': 41, 'selected_fragments': 5,
        'deferred_semantic_improvements': 36, 'retained_declarations': 176,
        'retained_modules_checked': len(source_text), 'current_input_bindings': len(bindings),
        'existing_local_links': link_count, 'topological_order': order,
        'formalization_first': True, 'original_human_gates_preserved': True,
        'readonly_boundary_probes': 4, 'fresh_kernel_replay': False,
        'implementation_or_application_executed': False, 'authority_effect': 'none',
        'ceiling': 'Plan structure, scoped current inputs, exact declaration excerpts and four saved-boundary probes; no new theorem, performance or human qualification.'
    }
    (HERE / 'validation-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
