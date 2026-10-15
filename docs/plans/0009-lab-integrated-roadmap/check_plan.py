#!/usr/bin/env python3
"""Check planning structure/source bindings; never execute the Lab runtime."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
RECEIPT = HERE / 'receipts/planning-check.json'


def load(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def topo(dependencies):
    done = set()
    remaining = dict(dependencies)
    while remaining:
        ready = sorted(k for k, deps in remaining.items() if set(deps) <= done)
        require(ready, 'cycle or unresolved dependencies: ' + ', '.join(remaining))
        for key in ready:
            done.add(key)
            del remaining[key]
    return sorted(done)


def check():
    dag = load(HERE / 'dag.json')
    swus = load(HERE / 'swu-manifest.json')['units']
    baseline = load(HERE / 'SOURCE-BASELINE.json')
    coverage = load(HERE / 'contract-coverage.json')
    nodes = {n['id']: n for n in dag['nodes']}
    require(len(nodes) == len(dag['nodes']), 'duplicate node identity')
    require(dag['authority_effect'] == 'none' and dag['implementation_execution_authorized'] is False, 'planning scope changed')
    require(set(n['layer'] for n in nodes.values()) == {'L0','L1','L2','L3','L4'}, 'missing roadmap layer')
    require(set(dag['milestone_joins'].values()) <= nodes.keys(), 'unknown milestone join')
    order = topo({i: n['depends_on'] for i, n in nodes.items()})
    expected_edges = {(d, n['id']) for n in nodes.values() for d in n['depends_on']}
    require(expected_edges == {(e['source'], e['target']) for e in dag['edges']}, 'edge/dependency mismatch')
    require({n['id'] for n in nodes.values() if n['status'] != 'not-started'} == {'B00','B01'}, 'future task claimed complete')
    unit_map = {u['id']: u for u in swus}
    require(len(unit_map) == len(swus), 'duplicate SWU identity')
    require(set(unit_map) == {u for n in nodes.values() for u in n['swu_ids']}, 'SWU task mapping mismatch')
    unit_deps = {}
    for u in swus:
        require(u['parent_task'] in nodes, 'orphan SWU ' + u['id'])
        n = nodes[u['parent_task']]
        for key in ('objective','source_anchors','related_context','write_scope','done_criteria','acceptance_evidence','reviewable_check','execution_owner','handoff_note'):
            require(u.get(key), 'missing SWU field ' + u['id'] + ':' + key)
        require(set(u['write_scope']) <= set(n['write_scope']), 'SWU writes beyond parent scope')
        deps=[]
        for d in u['depends_on']:
            if d in unit_map:
                deps.append(d)
            else:
                require(d in nodes, 'unknown SWU dependency ' + d)
                deps.extend(nodes[d]['swu_ids'][-1:])
        unit_deps[u['id']]=deps
    topo(unit_deps)
    for n in nodes.values():
        p=HERE/n['task_contract']
        require(p.is_file(), 'missing task contract ' + n['id'])
        text=p.read_text()
        for u in n['swu_ids']:
            require(u in text, 'task omits its SWU ' + u)
        for source in n['source_anchors']:
            require((REPO/source).is_file(), 'missing task source ' + source)
        if n['layer']!='L0':
            require(n['inputs'] and n['outputs'] and n['ordered_rules'] and n['failure_modes'] and n['acceptance_evidence'], 'incomplete task detail ' + n['id'])
    for s in baseline['sources']:
        p=REPO/s['path']
        require(p.is_file() and sha(p)==s['sha256'] and p.stat().st_size==s['size_bytes'], 'source drift: ' + s['path'])
    expected_digest=hashlib.sha256(json.dumps(baseline['sources'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
    require(expected_digest==baseline['source_manifest_digest'], 'source manifest digest mismatch')
    regbase=REPO/'authority/admissions/governance-transaction-surface/v1/registries'
    types=load(regbase/'artifact-type-registry.json')
    relations=load(regbase/'relation-kind-registry.json')
    require({t['current_ref'] for t in coverage['types']}==set(types['current_by_identity'].values()), 'incomplete current type coverage')
    require({r['ref'] for r in coverage['relations']}=={e['relation_kind_ref'] for e in relations['entries']}, 'incomplete relation coverage')
    for t in coverage['types']:
        require(sha(REPO/t['schema_path'])==t['schema_sha256'], 'schema binding drift')
        require(sha(REPO/t['descriptor_path'])==t['descriptor_sha256'], 'descriptor binding drift')
        require(set(t['proposed_consumer_tasks'])<=nodes.keys(), 'unknown carrier consumer')
    rel_entries={e['relation_kind_ref']:e for e in relations['entries']}
    for r in coverage['relations']:
        require(sha(REPO/r['source_path'])==r['source_sha256'], 'relation binding drift')
        require(len(r['exact_endpoint_pairs'])==rel_entries[r['ref']]['exact_endpoint_pair_count'], 'endpoint coverage mismatch')
        require(r['qualifier_contract'] is not None, 'qualifier contract omitted')
    package_preservation=[]
    for version in ('v1','v2'):
        receipt=load(REPO/f'implementation/lab-runtime/{version}/receipts/validation.json')
        for entry in receipt['source_manifest']:
            require(sha(REPO/entry['path'])==entry['sha256'], 'reviewed runtime package drift: '+entry['path'])
        package_preservation.append(dict(package=version,manifest_files=len(receipt['source_manifest']),matches_existing_receipt=True))
    missing=[]
    markdown_files=[*HERE.rglob('*.md'), REPO/'docs/ROADMAP.md', REPO/'README.md']
    for p in markdown_files:
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if '://' in target or target.startswith('#'):
                continue
            name=target.split('#',1)[0].strip('<>')
            if name and not (p.parent/name).exists():
                if (p.parent/name).resolve()==RECEIPT.resolve():
                    continue
                missing.append(dict(file=str(p.relative_to(REPO)),target=target))
    require(not missing, 'missing Markdown links: '+json.dumps(missing))
    manifest=[dict(path=str(p.relative_to(REPO)),sha256=sha(p),size_bytes=p.stat().st_size)
              for p in sorted(HERE.rglob('*')) if p.is_file() and p!=RECEIPT and '__pycache__' not in p.parts]
    return dict(schema_version='cyberalchemy-lab-planning-check/v1',authority_effect='none',result='PASS',
        check_scope='Planning structure, complete current registry coverage, source/package hashes and local links. No runtime execution or semantic conformance certification.',
        nodes=len(nodes),edges=len(expected_edges),swus=len(swus),waves=len({n['wave'] for n in nodes.values()}),
        node_kinds=dict(Counter(n['kind'] for n in nodes.values())),current_type_count=len(coverage['types']),
        relation_kind_count=len(coverage['relations']),exact_endpoint_pair_count=sum(len(r['exact_endpoint_pairs']) for r in coverage['relations']),
        source_files=len(baseline['sources']),source_manifest_digest=baseline['source_manifest_digest'],
        source_bindings_match=True,dag_acyclic=True,swu_graph_acyclic=True,one_parent_per_swu=True,
        roadmap_layers_complete=True,local_markdown_links_valid=True,reviewed_package_preservation=package_preservation,
        runtime_tests_executed=False,benchmarks_executed=False,admissions_applied=0,stores_provisioned=0,
        plan_artifact_manifest=manifest)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-receipt',action='store_true',help='save only the proposed planning evidence receipt')
    args=parser.parse_args()
    result=check()
    if args.write_receipt:
        RECEIPT.parent.mkdir(parents=True,exist_ok=True)
        RECEIPT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    elif RECEIPT.exists():
        require(load(RECEIPT)==result,'planning receipt stale; regenerate after reviewable planning edits')
    print(json.dumps({k:v for k,v in result.items() if k!='plan_artifact_manifest'},indent=2,sort_keys=True))


if __name__=='__main__':
    main()
