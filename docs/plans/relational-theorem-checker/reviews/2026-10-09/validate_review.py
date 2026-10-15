#!/usr/bin/env python3
"""Check this authored proposal and its read-only baseline; never execute planned work."""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'craft/formalization').is_dir())
BASE = ROOT / 'craft/formalization/candidates/relational-theorem-checker/v1'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_binding(binding):
    path = (ROOT / binding['path']).resolve()
    require(path.is_relative_to(ROOT) and path.is_file(), 'missing/outside source: ' + binding['path'])
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    require(digest == binding['sha256'], 'stale source: ' + binding['path'])
    return path


def validate():
    baseline = read(HERE / 'baseline-audit.json')
    for binding in baseline['reviewed_source_bindings']:
        check_binding(binding)
    checked_receipts = 0
    checked_exports = 0
    for row in baseline['receipt_checks']:
        receipt = read(check_binding(row['receipt']))
        require(receipt['task_id'] == row['task'] and receipt['result'] == 'accepted', 'receipt identity/result drift')
        for binding in receipt['artifacts'] + receipt['dependency_bindings']:
            check_binding(binding)
            checked_exports += 1
        checked_receipts += 1
    for row in baseline['additional_source_audits']:
        audit = read(check_binding(row['audit']))
        for binding in audit['source_bindings']:
            check_binding(binding)
        for key in ['parent_formalization', 'parent_f0_receipt', 'selection_receipt']:
            if key in audit:
                check_binding(audit[key])
    pilot = read(BASE / 'pilot/shadow-pilot-report.json')
    machine = read(BASE / 'pilot/machine-validation-audit.json')
    check_binding(pilot['validation_script'])
    check_binding(machine['validation_script'])
    for row in pilot['fresh_cases'] + pilot['accepted_predecessor_cases']:
        check_binding(row['outcome'])
        check_binding(row['stderr'])
    for binding in machine['generated_evidence_dependencies']:
        check_binding(binding)

    plan = read(HERE / 'plan-proposal.json')
    check_binding(plan['baseline_plan_binding'])
    require(plan['status'] == 'proposal-not-executed' and plan['authority_effect'] == 'none', 'proposal posture')
    tasks = plan['tasks']
    ids = [task['id'] for task in tasks]
    require(len(ids) == len(set(ids)) and ids[0] == 'S00' and plan['first_step'] == 'S00', 'identity/first task')
    require(not tasks[0]['depends_on'] and 'Formalize' in tasks[0]['title'], 'formalization must start plan')
    by_id = {task['id']: task for task in tasks}
    changes = read(HERE / 'findings-and-changes.json')
    change_ids = {row['id'] for row in changes['changes']}
    finding_ids = {row['id'] for row in changes['findings']}
    visited = set()
    active = set()

    def visit(id):
        require(id not in active, 'DAG cycle at ' + id)
        if id in visited:
            return
        active.add(id)
        for dependency in by_id[id]['depends_on']:
            require(dependency in by_id, 'unknown dependency')
            visit(dependency)
        active.remove(id)
        visited.add(id)

    def ancestors(id):
        result = set()
        for dependency in by_id[id]['depends_on']:
            result.add(dependency)
            result |= ancestors(dependency)
        return result

    for id in ids:
        visit(id)
    units = []
    for task in tasks:
        require(task['status'] == 'proposed' and task['authority_effect'] == 'none', 'task execution/status drift')
        require(task['id'] == 'S00' or 'S00' in ancestors(task['id']), 'task bypasses formalization')
        require(set(task['change_refs']) <= change_ids and task['change_refs'], 'unmapped change')
        require(task['write_scope'].startswith(plan['implementation_namespace'] + '/') and '..' not in task['write_scope'], 'unsafe scope')
        for field in ['inputs', 'outputs', 'algorithm', 'edge_cases', 'acceptance_criteria', 'validation', 'working_units']:
            require(task[field], 'missing task detail: ' + field)
        for unit in task['working_units']:
            require(unit['parent'] == task['id'] and unit['write_scope'] == task['write_scope'], 'SWU ownership')
            require(unit['evidence'] and unit['verification'], 'SWU evidence/verification absent')
            units.append(unit)
    require(len({unit['id'] for unit in units}) == len(units), 'duplicate SWU')
    require(read(HERE / 'swu-manifest.json')['units'] == units, 'SWU manifest drift')
    require({c for task in tasks for c in task['change_refs']} == change_ids, 'unplanned change')
    require({f for change in changes['changes'] for f in change['finding_refs']} == finding_ids, 'unaddressed finding')

    refresh = read(HERE / 'refresh-report.json')
    require(refresh['mutation_mode'] == 'proposal-only' and refresh['appliedChanges'] == [] and not refresh['mutation_ready'], 'unauthorized applied-status claim')
    signals = {signal['id'] for signal in refresh['sourceSignals']}
    require({change['id'] for change in refresh['proposedChanges']} == change_ids, 'refresh/change drift')
    for change in refresh['proposedChanges']:
        require(change['signal_refs'] and set(change['signal_refs']) <= signals, 'unmapped refresh signal')
    context = read(HERE / 'context-pack.json')
    require(len(context['sources']) <= context['maximum_files'] == 24, 'context budget')
    require({r for s in context['sources'] for r in s['obligations']} == set(context['obligations']), 'context obligation gap')
    for item in context['sources']:
        check_binding(item['binding'])
        require(item['selector'] and item['excerpt'], 'selector/excerpt absent')

    links = 0
    for path in HERE.glob('*.md'):
        text = path.read_text()
        require(text.count('```') % 2 == 0, 'unbalanced code fences: ' + path.name)
        for target in re.findall(r'\]\(([^)]+)\)', text):
            if target.startswith('https://'):
                continue
            target = re.sub(r':\d+$', '', target).split('#')[0]
            file = Path(target) if target.startswith('/') else HERE / target
            require(file.is_file(), 'broken document link: ' + target)
            links += 1
    ast.parse(Path(__file__).read_text())
    package_bindings = [{'path': str(path.relative_to(ROOT)),
                         'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
                        for path in sorted(HERE.iterdir())
                        if path.is_file() and path.name != 'validation-report.json']
    return {'schema': 'relational.successor-proposal-validation/v1-candidate', 'result': 'pass',
            'date': '2026-10-09', 'accepted_receipts_current': checked_receipts,
            'accepted_artifact_dependency_bindings_checked': checked_exports,
            'reviewed_source_bindings_current': len(baseline['reviewed_source_bindings']),
            'tasks': len(tasks), 'working_units': len(units),
            'dependency_edges': sum(len(task['depends_on']) for task in tasks),
            'formalization_first': True, 'findings': len(finding_ids), 'changes': len(change_ids),
            'source_signals': len(signals), 'document_file_links': links,
            'package_artifact_bindings': package_bindings,
            'original_pending_human_tasks': baseline['pending_tasks'],
            'method': 'Proposal structure, traceability and fresh source-binding checks; no successor theorem/runtime execution',
            'authority_effect': 'none'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true', help='Update this proposal validation report only')
    args = parser.parse_args()
    result = validate()
    if args.write:
        (HERE / 'validation-report.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError) as error:
        print('Proposal validation failed: ' + str(error), file=sys.stderr)
        sys.exit(1)
