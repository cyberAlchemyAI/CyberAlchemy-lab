#!/usr/bin/env python3
"""Check only proposed plan structure, source bindings and claim boundaries."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
RECEIPT = HERE / 'receipts/planning-check.json'


def load(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def check():
    dag = load(HERE / 'dag.json')
    original = load(HERE.parent / 'dag.json')
    mapping = load(HERE / 'task-transformation.json')['mappings']
    policy = load(HERE / 'approval-boundary.json')
    baseline = load(HERE / 'SOURCE-BASELINE.json')
    nodes = {n['id']: n for n in dag['nodes']}
    old = {n['id']: n for n in original['nodes']}
    require(len(nodes) == len(dag['nodes']) == dag['node_count'], 'duplicate node or incorrect count')
    require(dag['authority_effect'] == policy['authority_effect'] == 'none', 'unexpected authority effect')
    require(dag['implementation_execution_authorized'] is policy['implementation_execution_authorized'] is False, 'execution scope changed')
    require(dag['final_targets_materialized'] is policy['exact_targets_materialized'] is False, 'unconstructed targets claimed materialized')
    require(dag['literal_full_admitted_completion_before_checkpoint'] is False, 'admitted completion claimed before approval')
    require({n['id'] for n in nodes.values() if n['kind'] == 'owner-decision'} == {'R08'}, 'extra owner checkpoint')
    require(dag['target_human_checkpoint_count'] == policy['target_checkpoints'] == 1, 'checkpoint count drift')
    require(set(old) <= set(nodes), 'original task omitted')
    require({m['original_task'] for m in mapping} == set(old) and len(mapping) == len(old), 'incomplete transformation')
    for m in mapping:
        require(m['preserved_original_criteria'] == old[m['original_task']]['acceptance_evidence'], 'lost original criterion')
        require((HERE / nodes[m['variant_task']]['original_task_contract']).is_file(), 'missing original contract reference')
    require({n['id'] for n in nodes.values() if n['status'] != 'not-started'} == {'B00', 'B01'}, 'future task claimed complete')
    done = set()
    remaining = dict(nodes)
    waves = 0
    while remaining:
        ready = [i for i, n in remaining.items() if set(n['depends_on']) <= done]
        require(ready, 'cycle or unresolved prerequisite')
        for i in ready:
            done.add(i)
            del remaining[i]
        waves += 1
    edges = {(d, n['id']) for n in nodes.values() for d in n['depends_on']}
    require(edges == {(e['source'], e['target']) for e in dag['edges']} and len(edges) == dag['edge_count'], 'edge mismatch')
    require(policy['atomic_admission_limits'] == {'runtime_activations': 0, 'external_effect_refs': []}, 'admission action limits widened')
    sources = baseline['sources']
    require(hashlib.sha256(json.dumps(sources, sort_keys=True, separators=(',', ':')).encode()).hexdigest() == baseline['source_manifest_digest'], 'source manifest mismatch')
    for s in sources:
        p = REPO / s['path']
        require(p.is_file() and sha(p) == s['sha256'] and p.stat().st_size == s['size_bytes'], 'source drift: ' + s['path'])
    manifest = [{'path': str(p.relative_to(REPO)), 'sha256': sha(p)}
                for p in sorted(HERE.rglob('*')) if p.is_file() and p != RECEIPT and '__pycache__' not in p.parts]
    return {'schema_version': 'cyberalchemy-lab-single-checkpoint-planning-check/v1',
            'result': 'PASS', 'authority_effect': 'none',
            'check_scope': 'Proposed graph, exact source hashes, preserved criteria and claim boundaries only; no semantic conformance or operational success certification.',
            'nodes': len(nodes), 'edges': len(edges), 'dependency_waves': waves,
            'original_tasks_mapped': len(mapping), 'original_swus_referenced': 57,
            'human_checkpoint_count': 1, 'acyclic': True, 'source_files': len(sources),
            'source_manifest_digest': baseline['source_manifest_digest'],
            'runtime_tests_executed': False, 'admissions_applied': 0, 'stores_provisioned': 0,
            'feasibility_verdict': 'flag-conditional', 'plan_artifact_manifest': manifest}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-receipt', action='store_true')
    args = parser.parse_args()
    result = check()
    if args.write_receipt:
        RECEIPT.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    elif RECEIPT.exists():
        require(load(RECEIPT) == result, 'planning receipt stale')
    print(json.dumps({k: v for k, v in result.items() if k != 'plan_artifact_manifest'}, indent=2, sort_keys=True))
