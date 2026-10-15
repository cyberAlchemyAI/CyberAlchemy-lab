#!/usr/bin/env python3
"""Synchronize execution evidence without changing frozen planning predecessors."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PREPARATION = HERE.parents[1]


def load(path):
    return json.loads(path.read_text())


def put(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def mark(task, evidence_path, completion_mode):
    path = ROOT / evidence_path
    receipt = load(path)
    if receipt.get('result') != 'PASS':
        raise ValueError('receipt has not passed')
    partial = completion_mode == 'candidate-partial'
    if not partial and receipt.get('task_complete') is False:
        raise ValueError('passing scoped evidence does not complete the task')
    if partial and receipt.get('task_complete') is not False:
        raise ValueError('partial evidence must explicitly retain incomplete task criteria')
    sources = receipt.get('files', receipt.get('source_files', []))
    for source in sources:
        source_path = ROOT / source['path']
        if hashlib.sha256(source_path.read_bytes()).hexdigest() != source['sha256']:
            raise ValueError('evidence file changed: ' + source['path'])
    evidence_binding = {'path': evidence_path, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'completion_mode': completion_mode, 'authority_effect': 'none'}
    dag = load(HERE / 'dag.json')
    nodes = {n['id']: n for n in dag['nodes']}
    if task not in nodes:
        raise ValueError('unknown task')
    for prerequisite in nodes[task]['depends_on']:
        if nodes[prerequisite]['status'] not in ['complete', 'complete-existing-evidence', 'complete-planning', 'satisfied-scoped']:
            raise ValueError('prerequisite incomplete: ' + prerequisite)
    nodes[task]['status'] = 'in-progress' if partial else 'complete'
    nodes[task]['completion_mode'] = completion_mode
    if partial:
        nodes[task]['progress_evidence'] = [evidence_binding]
        nodes[task]['remaining_obligations'] = receipt.get('remaining_obligations', [])
    else:
        nodes[task]['completion_evidence'] = [evidence_binding]
    dag['status'] = 'candidate-construction-in-progress'
    dag['execution_authorization_ref'] = 'authorization.json'
    dag['implementation_execution_authorized'] = True
    for node in dag['nodes']:
        node['contract_path'] = '../../work-pack/tasks/' + node['id'] + '.md'
    put(HERE / 'dag.json', dag)
    manifest = load(HERE / 'swu-manifest.json')
    for unit in manifest['units']:
        unit['contract_path'] = '../../work-pack/tasks/' + unit['parent_task'] + '.md'
        if unit['parent_task'] == task:
            unit['progress_evidence' if partial else 'completion_evidence'] = [evidence_binding]
            unit['status'] = 'in-progress' if partial else 'complete'
    put(HERE / 'swu-manifest.json', manifest)
    evidence = load(HERE / 'evidence.json')
    evidence.setdefault('task_progress' if partial else 'task_completion', {})[task] = evidence_binding
    if completion_mode != 'candidate-design':
        evidence['runtime_tests_executed'] = True
    evidence['claim_ceiling'] = 'Completed candidate task criteria only; no actual owner outcome, operational admission or stable release.'
    put(HERE / 'evidence.json', evidence)
    board = '# Active full-plan execution\n\nGoal: complete the plan. One final R08 owner checkpoint; no owner outcome is fabricated.\n\n'
    board += '| Task | Phase | Status | Evidence |\n| --- | --- | --- | --- |\n'
    for node in dag['nodes']:
        refs = node.get('completion_evidence', node.get('progress_evidence', []))
        ref = refs[0]['path'] if refs else ''
        board += f'| {node["id"]} | {node["phase"]} | {node["status"]} | {ref} |\n'
    (HERE / 'WORK-PACK.md').write_text(board)
    print(json.dumps({'task': task, 'status': nodes[task]['status'], 'completion_mode': completion_mode,
                      'complete_tasks': [n['id'] for n in dag['nodes'] if n['status'] in ['complete', 'complete-existing-evidence', 'complete-planning', 'satisfied-scoped']],
                      'goal_complete': False, 'authority_effect': 'none'}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('task')
    parser.add_argument('evidence_path')
    parser.add_argument('--mode', required=True, choices=['candidate-design', 'candidate-implementation-verified', 'candidate-measurement', 'candidate-partial'])
    args = parser.parse_args()
    mark(args.task, args.evidence_path, args.mode)
