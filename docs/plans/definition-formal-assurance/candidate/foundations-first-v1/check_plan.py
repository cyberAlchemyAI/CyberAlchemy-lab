#!/usr/bin/env python3
"""Check successor planning structure/currentness; no implementation executes."""
import hashlib
import json
import re
from pathlib import Path

HERE=Path(__file__).resolve().parent
LAB=HERE.parents[4]
BASE=HERE.parent/'detailed-plan-v1'
IMPL='craft/formalization/candidates/definition-assurance-v1/'
DATA='docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def validate():
    assertions=0
    def require(condition, message):
        nonlocal assertions
        assertions+=1
        if not condition:
            raise ValueError(message)
    dag=load(HERE/'dag.json')
    units=load(HERE/'swu-manifest.json')['units']
    old=load(BASE/'dag.json')
    oldunits=load(BASE/'swu-manifest.json')['units']
    baseline=load(BASE/'source-baseline.json')
    tasks={t['id']:t for t in dag['tasks']}
    byunit={u['id']:u for u in units}
    require(len(tasks)==len(dag['tasks'])==dag['task_count']==121,'Task denominator/identity mismatch')
    require(len(byunit)==len(units)==dag['swu_count']==797,'Unit denominator/identity mismatch')
    require(dag['authority_effect']=='none' and dag['execution_policy']['implementation_readiness']=='not-run','Fabricated effect or implementation')
    for row in load(HERE/'predecessor-bindings.json')['files']:
        require(sha((HERE/row['path']).resolve())==row['sha256'],'Changed predecessor input')
    require(dag['definition_queue']==old['definition_queue'] and dag['families']==old['families'],'Dropped or reclassified existing identities')
    for task in old['tasks']:
        new=tasks[task['id']]
        require(set(task['depends_on'])<=set(new['depends_on']),'Removed existing prerequisite')
        for key in ('implementation_rules','acceptance','swu_ids','layer','stage','condition'):
            require(task[key]==new[key],'Changed inherited semantic/verification contract')
    for unit in oldunits:
        new=byunit[unit['id']]
        for key in ('outputs','write_scope','validation','ordered_rules','edge_cases','closeout'):
            require(unit[key]==new[key],'Changed inherited unit output/criterion')
    for task in tasks.values():
        require(task['status']=='planned','Future execution/review falsely claimed')
        require(set(task['depends_on'])<=set(tasks) and len(task['depends_on'])==len(set(task['depends_on'])),'Unbound/duplicate dependency')
        require(bool(task['implementation_rules'] and task['acceptance']),'Missing task criterion')
        require(set(task['swu_ids'])<=set(byunit),'Missing task unit')
    remaining,done,frontiers=set(tasks),set(),[]
    while remaining:
        ready=sorted(t for t in remaining if set(tasks[t]['depends_on'])<=done)
        require(bool(ready),'Cyclic execution DAG')
        frontiers.append(ready);done.update(ready);remaining-=set(ready)
    require(frontiers==load(HERE/'topological-frontiers.json')['frontiers'],'Stale frontiers')
    require(frontiers[0]==['M01'] and dag['first_unit']=='M01.1','Foundations are not first')
    def ancestors(ident):
        result=set()
        def visit(item):
            if item in result:return
            result.add(item)
            for dep in tasks[item]['depends_on']:visit(dep)
        visit(ident)
        return result
    require(ancestors('H04')==set(tasks),'Task disconnected from closeout')
    for task in old['tasks']:
        require({f'M{i:02}' for i in range(1,10)}<=ancestors(task['id']),'Old task can bypass foundation gate')
    owners={}
    for unit in units:
        parent=tasks[unit['parent_task']]
        require(unit['id'] in parent['swu_ids'],'Orphaned unit')
        require(unit['depends_on_tasks']==parent['depends_on'],'Stale unit prerequisites')
        require(unit['execution_condition']==parent['condition'],'Conditional route mismatch')
        require(unit['validation']['phase']=='post-produce' and bool(unit['pre_execution_check']),'Missing verification phase')
        require(bool(unit['validation']['command'] or unit['validation']['reviewable_check']),'No validation surface')
        require({d['path'] for d in unit['target_dispositions']}==set(unit['outputs']),'Incomplete target dispositions')
        for output in unit['outputs']:
            require(output.startswith((IMPL,DATA)) and '..' not in Path(output).parts,'Protected/outside candidate output')
            require(output not in owners,'Conflicting output writers')
            require(any(output==s or s.endswith('/') and output.startswith(s) for s in unit['write_scope']),'Output outside scope')
            owners[output]=unit['id']
        for scope in unit['write_scope']:
            require(scope.startswith((IMPL,DATA)) and '..' not in Path(scope).parts,'Protected write scope')
    registry=load(LAB/'authority/definitions/registry.json')
    require(sha(LAB/'authority/definitions/registry.json')==dag['source_registry_sha256'],'Registry drift')
    require(len(registry['current_lookup'])==183 and len(registry['entries'])==189,'Source denominator drift')
    for row in baseline['sources']:
        require(sha(LAB/row['path'])==row['sha256'],'Inspected source drift')
    for row in dag['definition_queue']:
        require(registry['current_lookup'][row['definition_id']]==row['version_ref'],'Current version drift')
        require(sha(LAB/row['source_path'])==row['source_sha256'],'Current source digest drift')
        for phase in ('T','O','E','R'):
            ident=row['family_id']+'-'+phase+'.'+row['definition_id']
            require(ident in byunit and byunit[ident]['version_ref']==row['version_ref'],'Missing source-bound phase')
    queue=load(HERE/'foundation-source-queue.json')['sources']
    require({q['definition_id'] for q in queue}=={r['definition_id'] for r in dag['definition_queue'] if r['family_id']=='F01'},'Foundation source selection changed')
    for row in queue:
        source=load(LAB/row['source_path'])
        require(row['current_normative_statement']==source['voices']['scientific_formal']['normative_statement'],'Altered foundation source excerpt')
        require(row['current_formal_expression']==source['voices']['scientific_formal']['formal_expression'],'Altered foundation formal excerpt')
    links=0
    for path in HERE.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
            if target.startswith(('http://','https://')):continue
            resolved=(path.parent/target.split('#')[0]).resolve()
            require(resolved.exists() or resolved==HERE/'planning-validation.json','Broken local link')
            links+=1
    receipt={'result':'PASS','authority_effect':'none','validated_assertions':assertions,'task_nodes':len(tasks),
             'task_edges':sum(len(t['depends_on']) for t in tasks.values()),'swus':len(units),'current_definitions':183,
             'foundation_source_definitions':len(queue),'logical_frontiers':len(frontiers),'first_unit':'M01.1',
             'all_prior_tasks_preserved':True,'all_prior_tasks_require_foundation_gate':True,'local_links':links,
             'dag_sha256':sha(HERE/'dag.json'),'swu_manifest_sha256':sha(HERE/'swu-manifest.json'),'validator_sha256':sha(Path(__file__)),
             'claim_ceiling':'Priority ordering, planning integrity and exact source bindings only; no executed foundation review, implementation, proof or admission.'}
    (HERE/'planning-validation.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    return receipt


if __name__=='__main__':
    print(json.dumps(validate(),indent=2))
