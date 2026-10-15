#!/usr/bin/env python3
"""Author a no-effect foundations-first successor of the sealed detailed plan."""
import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / 'detailed-plan-v1'
LAB = HERE.parents[4]
DATA = 'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


# These are future production/review units. Documents in this package are
# inspectable initial drafts, not their executed/accepted output receipts.
FOUNDATIONS = [
 ('M01', [], 'Definition forms and classification axes', 'definition-kinds.json',
  'Separate artifact kind, definitional form, logical statement role, signature shape and logic features. Classify clauses, not just whole artifacts; allow mixed forms and unresolved classifications. Read the eight F01 sources first.',
  'Primitive, explicit, axiomatic, inductive and operational cases are distinct; Axiom artifact is not an axiom assertion; inherited labels do not force equivalence.', 'design'),
 ('M02', ['M01'], 'Logical roles and assumption discipline', 'statement-roles.json',
  'Specify definitions, selected axioms, premises, hypotheses, obligations, derived claims and observations. Separate vocabulary/theory declarations from properties to establish. Record selection, scope, dependence and source precedence for each premise.',
  'Invariant to be checked cannot be inserted as an assumption to prove itself; hypothesis is not silently adopted as a premise; an accepted premise is not established truth.', 'design'),
 ('M03', ['M01'], 'Signatures, carriers and identity', 'signatures.json',
  'Specify sorts, constants, total/partial functions, predicates, typed relations, arity and scope-qualified identifiers; distinguish semantic primitives from programming types; require explicit common-carrier alignment.',
  'Ill-typed application and unbound symbol diagnosed; same labels retain distinct scope identities; nominal disjoint types cannot manufacture semantic distinction.', 'design'),
 ('M04', ['M02', 'M03'], 'Logical language and fragment boundaries', 'logical-language.json',
  'Specify grammar, binding and typing rules for a candidate classical many-sorted first-order static core; declare finite evaluation as a bounded profile. Specify entry criteria for inductive/recursive, temporal, deontic and empirical/probabilistic extensions without claiming their implementation.',
  'No guessed meaning for iff, implication, quantification or non-entailment notation; recursive iff is not a least fixed point; unsupported operators remain unresolved.', 'design'),
 ('M05', ['M04'], 'Denotation, truth and information state', 'denotation.json',
  'Define structures, environments and satisfaction independently from executable checking. Declare domain/cardinality policies, partial values, unknown versus absent versus false, open/closed-world behavior and state/trace interpretations.',
  'Missing evidence is not falsehood; empty required population is not a useful distinction proof; operational unknown is not silently made a third truth value; plain-language authority strings are not authentication.', 'design'),
 ('M06', ['M02', 'M03', 'M05'], 'Theory composition and semantic relationships', 'composition.json',
  'Specify definition expansion, selected assumptions and constraints, external dependencies, shared carriers and SCC semantics. Specify aliases, subtype inclusion/properness, overlap, disjointness and forbidden inferences; separate allowed-state theory from invariant-preservation proof domain.',
  'Keep allowed couplings and subtype overlap; no pairwise consistency aggregation; no label-derived edges; legitimate recursion and prohibited constraining cycles are separately handled.', 'design'),
 ('M07', ['M02', 'M05', 'M06'], 'Obligation types and evidence strengths', 'obligation-types.json',
  'Specify source fidelity, well-formedness, closure, model existence, joint inhabitation, relation obligations, transition preservation and separately selected conservativity. Give each exact statement, prerequisites, minimum evidence strength and failure outcomes.',
  'Witness non-entailment differs from universal separation; bounded absence differs from unbounded proof; contradictory assumptions cannot count as non-vacuity; observations do not prove universal laws.', 'design'),
 ('M08', ['M06', 'M07'], 'Worked foundation examples and ambiguity ledger', 'worked-examples.json',
  'Apply the model first to Definition, Semantic Primitive, Schema, Axiom, Premise, Hypothesis, Invariant and Governed Model. Bind exact source selectors; add small alias/subtype/induction/transition controls as explicitly synthetic examples. Record every omission and unresolved clause precedence.',
  'Expose Hypothesis target meaning versus inherited Premise expression; do not fix canonical sources; show theorem versus premise separation and a non-vacuous invariant-preservation case; do not claim full translation from fragments.', 'design'),
 ('M09', ['M08'], 'Foundation model review and implementation contract', 'foundation-review.json',
  'Assemble exact taxonomy, logical language, semantics, relationships, obligations, examples and unresolved decisions. Obtain actual attributable model-design disposition; carry required unresolved issues as blockers before lowering to schemas and evaluators.',
  'Actual review of exact bytes or pending/rejected outcome; no generated approval; agreed core and explicit fragment limits before A01; this review grants no source revision or semantic admission.', 'review'),
]


def main():
    original = json.loads((BASE / 'dag.json').read_text())
    dag = copy.deepcopy(original)
    units = copy.deepcopy(json.loads((BASE / 'swu-manifest.json').read_text())['units'])
    baseline = json.loads((BASE / 'source-baseline.json').read_text())
    for row in baseline['sources'] + [{'path':r['source_path'], 'sha256':r['source_sha256']} for r in baseline['definitions']]:
        assert sha(LAB / row['path']) == row['sha256'], 'Input drift: ' + row['path']
    foundation_tasks, foundation_units = [], []
    for ident, deps, title, output, rules, acceptance, kind in FOUNDATIONS:
        target = f'{DATA}/foundations/{output}'
        receipt = f'{DATA}/units/{ident}/receipt.json'
        task = {'id':ident, 'depends_on':deps, 'title':title, 'status':'planned', 'layer':'L0', 'stage':'D1',
                'owner':'role:formalization-reviewer' if kind=='review' else 'role:formal-assurance-designer',
                'risk':'human' if kind=='review' else 'high', 'condition':None, 'swu_ids':[ident+'.1'],
                'implementation_rules':rules, 'acceptance':acceptance, 'estimated_effort':'medium-to-high; no calendar commitment',
                'priority_band':'foundation-first'}
        foundation_tasks.append(task)
        foundation_units.append({'id':ident+'.1', 'parent_task':ident, 'kind':'model-review' if kind=='review' else 'formal-model-design',
            'purpose':title, 'inputs':['FORMALIZATION-MODEL.md','foundation-source-queue.json',*deps],
            'outputs':[target,receipt], 'write_scope':[target,f'{DATA}/units/{ident}/'],
            'ordered_rules':rules, 'edge_cases':acceptance,
            'failure_behavior':'Keep ambiguity, insufficient support and pending review visible; preserve exact sources; new attempt on rejection.',
            'validation':{'phase':'post-produce','command':None,'reviewable_check':acceptance,
                          'runner_state':'Future design production and actual review; no dependency on an unbuilt decoder or CLI.'},
            'closeout':'Bind exact source selectors, produced bytes, actual criterion outcomes, assumptions and attributable dispositions; no semantic admission.'})
    extra = {'A01':['M09'], 'A04':['M02','M06'], 'A05':['M06','M07'], 'A06':['M07'],
             'C01':['M03','M04'], 'C02':['M05'], 'C03':['M06'], 'P01':['M04','M07'], 'E01':['M07']}
    for task in dag['tasks']:
        task['depends_on'] = list(dict.fromkeys(task['depends_on'] + extra.get(task['id'],[])))
        task['priority_band'] = 'foundational-definition-drafts' if task['id']=='F01-T' else 'downstream'
        task['inherited_content_ref'] = f'../detailed-plan-v1/tasks/{task["id"]}.md'
    dag['tasks'] = foundation_tasks + dag['tasks']
    bytask = {t['id']:t for t in dag['tasks']}
    units = foundation_units + units
    for unit in units:
        unit['depends_on_tasks'] = bytask[unit['parent_task']]['depends_on'].copy()
        unit['inputs'] = list(dict.fromkeys(unit['inputs'] + extra.get(unit['parent_task'], [])))
        unit['execution_condition'] = bytask[unit['parent_task']]['condition']
        unit.setdefault('target_dispositions',[{'path':p,'disposition':'create','activation_condition':None} for p in unit['outputs']])
        unit.setdefault('pre_execution_check','Verify exact source and upstream artifact digests; outputs absent; review sources before producing the candidate design.')
    dag.update({'schema_version':'definition-assurance-foundations-first-dag/v1-candidate',
                'status':'foundations-first candidate plan; foundation preview drafted; execution and review not claimed',
                'priority_request':'Definition kinds, logical and other formalization foundations before tooling and all-definition rollout.',
                'predecessor':{'path':'../detailed-plan-v1/dag.json','sha256':sha(BASE/'dag.json'), 'preservation':'Exact predecessor retained; this successor owns the new ordering.'},
                'task_count':len(dag['tasks']), 'swu_count':len(units), 'first_unit':'M01.1',
                'layers':['L0 formalization foundations and worked model slice','L1 reusable selected-scope workflow','L2 all-current formalization and coverage','L3 complete combined theory and owner disposition'],
                'source_baseline_ref':'../detailed-plan-v1/source-baseline.json',
                'scheduling_policy':'M01-M09 gate all prior implementation. Prefer F01-T after its actual prerequisites; no invented semantic dependency order or early full-definition proof claim.'})
    remaining,done,frontiers = set(bytask),set(),[]
    while remaining:
        ready = sorted(t for t in remaining if set(bytask[t]['depends_on']) <= done)
        assert ready, 'Cyclic or unbound DAG'
        frontiers.append(ready); done.update(ready); remaining -= set(ready)
    dump('dag.json',dag)
    dump('swu-manifest.json',{'schema_version':'definition-assurance-foundations-first-units/v1-candidate','authority_effect':'none','units':units})
    dump('topological-frontiers.json',{'authority_effect':'none','frontiers':frontiers,'note':'Logical ordering; no duration, implementation acceptance or delegation authorization.'})
    selected = [r for r in dag['definition_queue'] if r['family_id']=='F01']
    queue=[]
    for row in selected:
        src = json.loads((LAB/row['source_path']).read_text())
        queue.append({**row, 'priority':'first foundation sample set; classification/fidelity not accepted',
                      'current_normative_statement':src['voices']['scientific_formal']['normative_statement'],
                      'current_formal_expression':src['voices']['scientific_formal']['formal_expression'],
                      'source_role':'Defines the named concept; does not automatically insert an instance of that concept into the theory.'})
    dump('foundation-source-queue.json',{'authority_effect':'none','sources':queue,'classification':'draft only; roles assigned per clause after source reading'})
    (HERE/'tasks').mkdir(exist_ok=True)
    for task in foundation_tasks:
        (HERE/'tasks'/f'{task["id"]}.md').write_text(f'# {task["id"]}: {task["title"]}\n\nStatus: planned. Authority effect: none. Dependencies: '+(', '.join(task['depends_on']) or 'none')+'\n\n'+task['implementation_rules']+'\n\nAcceptance: '+task['acceptance']+'\n\nExact outputs and validation: [unit manifest](../swu-manifest.json). Initial candidate content: [formalization model](../FORMALIZATION-MODEL.md).\n')
    graph=['# Full foundations-first execution DAG','', '[dag.json](dag.json) owns the revised ordering. Previous artifacts remain intact. Semantic dependencies are separately declared/reviewed.','', '```mermaid','flowchart TD']
    for task in dag['tasks']:
        graph.append(f'  {task["id"].replace("-","_")}["{task["id"]}: {task["title"]}"]')
    for task in dag['tasks']:
        for dep in task['depends_on']:
            graph.append(f'  {dep.replace("-","_")} --> {task["id"].replace("-","_")}')
    graph.extend(['```','','## Logical frontiers',''])
    graph.extend(f'- W{i:02}: '+', '.join(f) for i,f in enumerate(frontiers))
    (HERE/'DAG.md').write_text('\n'.join(graph)+'\n')
    dump('predecessor-bindings.json',{'authority_effect':'none','files':[{'path':f'../detailed-plan-v1/{name}','sha256':sha(BASE/name)} for name in ['dag.json','swu-manifest.json','source-baseline.json','manifest.json']]})
    print(json.dumps({'tasks':len(bytask),'units':len(units),'frontiers':len(frontiers),'first_unit':'M01.1'}))


if __name__ == '__main__':
    main()
