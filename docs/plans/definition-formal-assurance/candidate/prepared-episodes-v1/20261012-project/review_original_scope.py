"""Interim original-scope evidence accounting, not an acceptance audit."""
from pathlib import Path
import collections,hashlib,json
root=Path.cwd();out=Path(__file__).resolve().parent
plan_dir=root/'docs/plans/definition-formal-assurance/candidate/foundations-first-v1'
unit_dir=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/CAV2-D60'
def ref(path):return {'path':str(path.relative_to(root)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
inputs=[ref(plan_dir/name) for name in ['dag.json','swu-manifest.json','topological-frontiers.json','FORMALIZATION-MODEL.md']]
inputs += [ref(unit_dir/'current-inventory.json')]
alternates=[root/'craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/README.md',root/'craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/completion-audit/REVIEW.md']
inputs += [ref(path) for path in alternates]
plan=json.loads((plan_dir/'dag.json').read_bytes());work=json.loads((plan_dir/'swu-manifest.json').read_bytes())
frontiers=json.loads((plan_dir/'topological-frontiers.json').read_bytes())
inventory=json.loads((unit_dir/'current-inventory.json').read_bytes())
assert (len(plan['tasks']),sum(len(t['depends_on']) for t in plan['tasks']),len(work['units']),len(frontiers['frontiers']))==(121,511,797,36)
assert plan['current_identity_count']==inventory['current_definitions']==183
assert plan['admitted_version_count']==inventory['admitted_source_versions']==189
tasks={t['id']:t for t in plan['tasks']};drafts={d['definition_id']:d for d in inventory['draft_rows']}
counts=collections.defaultdict(collections.Counter);units=[];outputs={}
for unit in work['units']:
 observations=[]
 for name in unit['outputs']:
  path=root/name;item={'path':name,'present':path.is_file()}
  if path.is_file():
   item.update(ref(path))
   if path.suffix=='.json':
    d=json.loads(path.read_bytes())
    if isinstance(d,dict):
     item['recorded_postures']={key:d[key] for key in ['task_result','semantic_ready','source_fidelity','review_status','owner_review_disposition','whole_definition_translation','whole_definition_proof','full_project_completion','authority_effect'] if key in d}
     if 'payload' in d and isinstance(d['payload'],dict):
      item['payload_postures']={key:d['payload'][key] for key in ['semantic_status','source_fidelity','source'] if key in d['payload']}
  observations.append(item);outputs[name]=item
 present=all(x['present'] for x in observations);kind=unit['kind']
 counts[kind]['units']+=1;counts[kind]['all_outputs_present']+=int(present)
 counts[kind]['at_least_one_output_missing']+=int(not present)
 row={'unit_id':unit['id'],'parent_task':unit['parent_task'],'kind':kind,'purpose':unit['purpose'],
      'original_task_acceptance':tasks[unit['parent_task']]['acceptance'],
      'original_ordered_rules':unit['ordered_rules'],'original_pre_execution_check':unit['pre_execution_check'],
      'original_validation':unit['validation'],'original_closeout':unit['closeout'],
      'original_dependencies':unit['depends_on_tasks'],'original_execution_condition':unit['execution_condition'],
      'output_observations':observations,'criterion_acceptance_revalidated_by_this_inventory':False,
      'evidence_classification':'planned-output-presence-only' if present else 'missing-planned-output'}
 if unit.get('definition_id'):
  row['definition_id']=unit['definition_id'];row['version_ref']=unit['version_ref']
  candidate=drafts.get(unit['definition_id'])
  if candidate:
   assert candidate['source']['version_ref']==unit['version_ref']
   row['existing_partial_T_observation']=candidate
 units.append(row)
t_ids={u['definition_id'] for u in units if u['kind']=='definition-T' and all(x['present'] for x in u['output_observations'])}
missing_ids={u['definition_id'] for u in units if u['kind']=='definition-T' and not all(x['present'] for x in u['output_observations'])}
assert t_ids==set(drafts) and missing_ids==set(inventory['missing_current_drafts'])
assert len(t_ids)==108 and len(missing_ids)==75
for item in inputs:
 assert hashlib.sha256((root/item['path']).read_bytes()).hexdigest()==item['sha256']
for item in outputs.values():
 if item['present']:assert hashlib.sha256((root/item['path']).read_bytes()).hexdigest()==item['sha256']
summary={k:dict(v) for k,v in counts.items()}
present=sum(v['all_outputs_present'] for v in summary.values())
report={'schema_version':'original-formalization-scope-interim-accounting/v1-candidate','inputs':inputs,
        'original_scope':{'identities':183,'admitted_versions':189,'captured_source_files':201,'tasks':121,'planning_edges':511,'work_units':797,'frontiers':36},
        'original_completion_criterion':plan['completion'],'unit_requirements_and_observations':units,
        'kind_summary':summary,'units_with_all_planned_outputs_present':present,
        'units_with_missing_planned_outputs':797-present,
        'whole_translation_acceptances':inventory['source_owner_accepted_whole_translations'],
        'whole_definition_proofs':inventory['whole_definition_proofs'],
        'existing_inventory_aggregate_counts':inventory['counts'],
        'global_consistency_proven':False,'semantic_ready':False,'authority_effect':'none','goal_status':'active',
        'claim_ceiling':'Exact original requirements and current planned-output observations. No acceptance inferred from presence. Absence at planned paths is not an exhaustive search of alternative evidence. Existing finite models, source-query obligations and the separate relational-checker scope are not substituted for original O/E/R/J criteria.'}
with (out/'original-scope-requirements.json').open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
table=['| Original work kind | Units | All planned outputs present | Some planned output absent |',
       '|---|---:|---:|---:|']
for k,v in summary.items():table.append(f"| {k} | {v['units']} | {v['all_outputs_present']} | {v['at_least_one_output_missing']} |")
text="""# Original formalization scope: interim requirements and evidence review

The original scope remains 183 identities, 189 admitted versions, 201 captured source files, 121 tasks, 511 planning edges, 797 work units and 36 execution frontiers. This review reads the original requirements and checks exact planned output paths. It does not mark the episode complete or accept candidate semantics.

Every original work unit is recorded in [the requirements matrix](original-scope-requirements.json), retaining its task acceptance criterion, ordered rules, pre-execution check, validation command or review criterion, closeout, dependencies and execution condition. Existing output bytes are bound by SHA-256 and checked again before reporting.

## Current planned-path observations

"""+'\n'.join(table)+f"""

There are {present} work units with all planned outputs present and {797-present} with a planned output missing. These are presence counts, not acceptance counts. The earlier 138-unit presence observation is historical; this current observation must not rewrite its earlier receipt.

The 108 planned T outputs match the exact 108 partial-draft identities in Project's completed producer inventory. The remaining 75 identities also match that inventory exactly. Native finite model/source/profile evidence can support these partial interpretations without accepting full source fidelity or a shared theory.

All 183 planned O outputs, all 183 planned E outputs and all 14 planned family-closure receipts are absent. Their original criteria are stronger than file creation or isolated declaration controls. Source-query-obligation files, per-definition countermodels and dependency inventories remain relevant bounded evidence, with their own exact scope. They do not automatically satisfy the neighbour/class/alignment matrix, complete selected theory, required proof strengths or reviewed cross-family maps.

## T, O, E, R and J requirements

T requires an exact source-bound interpretation, complete clause map, typed signature, assumptions, explicit dependencies, required or exempt populations, intuition and realistic examples and counterexamples. Current source-qualified typed drafts retain pending denotations, deferred clauses and explicit unresolved targets. Their existence does not establish accepted whole translations.

O requires each Definition's complete requirement set from the sealed neighbour/class/alignment matrix and canonical theory IR. Exact prerequisite clauses, query direction and required strength must be bound. Missing, weak or substituted obligations remain visible; alias, subtype and coupling checks follow their reviewed classes. No isolated nonentailment query can stand in for an omitted required relationship.

E requires compilation of the exact selected SCC and dependency theory, satisfiability and joint inhabitation before distinction queries, and model or proof replay under the selected profile. Every required statement needs an actual result or an explicitly unresolved outcome. A witness must satisfy the entire included closure. Bounds, assumptions, cross-family premises and evidence strength remain explicit.

R requires exact source clauses, proposed interpretation, dependency assumptions, realistic examples and actual evidence for an attributable correspondence review. Its original rule allows an actual owner decision or an explicit pending state. That alternative does not waive the required review artifact, exact reviewed bytes or presentation contract. Agent preparation and logical evidence cannot supply a human source owner's acceptance.

The one owner-review work unit with all planned outputs is A10.1. Its current receipt records a candidate-agent self-review and a PASS for the explicit pending-state alternative. Source-owner principals, decisions, role bindings and selections remain pending. This is a prepared review packet, not acceptance of all Definitions. All 183 per-definition R outputs remain absent at their planned paths.

J requires the actual dependency SCCs, the whole included closure, explicit reviewed cross-family symbols, every required result and every fidelity status. A family is not assumed dependency-closed. The original acceptance requires one scoped satisfiable inhabited closure or an explicit unresolved outcome, with missing dependency reviews retained. One selected finite witness per partial draft does not establish a single common interpretation.

An explicit pending or unresolved record may satisfy an original recording criterion when that criterion permits it. It cannot establish a stronger semantic assertion. The eventual completion audit must distinguish completed evidence records, accepted source fidelity and proven consistency; neither fabricated acceptance nor omitted required records can satisfy the goal.

## Formalization aspects the final review must explain

The original model separates artifact classification, definitional form, statement role, signature shape and logic requirements. A Definition about Axiom does not assert an axiom; an investigated Hypothesis does not become an adopted premise. Classification remains per clause, with mixed forms and unresolved choices.

Explain the exact source selectors, admission overlays and precedence decisions before explaining the proposed denotations. Preserve primitive, abbreviation, genus/differentia, enumeration, implicit, constructive, inductive and operational requirements. Scope-qualified sorts, functions and predicates need accepted common-carrier maps for cross-definition comparisons; nominally disjoint sorts do not prove intended semantic difference.

Explain truth semantics independently from information and execution status. A classical structure assigns domains and denotations. Missing evidence, absent values, unsupported logic and timeouts are separate from mathematical falsity. Total functions, nonempty domains and requested predicate populations have separate obligations.

Explain theory assembly, selected assumptions, scope and dependency closure. A property to prove cannot be added as its own premise. T satisfiability and one joint T-and-I witness must precede relationship conclusions. Family-local success does not establish whole-theory consistency, and the execution DAG does not resolve semantic cycles.

Explain proof strength precisely: structure checks, checked witnesses, exhaustive bounded results, solver results, independently checked proofs and mechanized theorems under audited assumptions. Required strength follows the obligation. Inductive, temporal, normative and empirical requirements need supported semantic extensions or explicit unresolved outcomes; naming a static predicate does not establish those semantics.

Explain actual carrier observations, qualified profile hypotheses, unresolved source-to-consumer maps, owner review and reproducible evidence. Source identity, interpretation fidelity, runtime compliance, admission and instance authority remain distinct. The final aspect review must cover every required source, artifact and gate at its own scope.

## Alternative formalization evidence and its limits

A separate relational-checker v5 package has its own successor plan: seven extensions, 41 relations, 550 endpoint pairs and 263 inherited semantic obligations. Its current README and completion review describe incomplete work and retain bounded earlier results. Their document bytes are bound in this review; their theorem commands were not replayed here.

Those records are useful evidence of another formalization surface. They are not evidence that this 183-identity Definition plan is complete. Importing them would require exact requirement correspondence, accepted semantic maps and adequate current proof coverage. No verdict, gate or owner assessment from that separate scope is transferred here.

Absence at the original planned paths is not proof that no alternate evidence exists anywhere. This is an interim requirements inventory, not the final exhaustive acceptance audit. The latter must inspect candidate, implementation, proof and validation trees against each original requirement.

## Continuation

Project's existing full-delivery jobs continue independently. Four fresh commands have passed; dependency and inventory replays precede the queued review, seal and separate audit. Capability Instance native authoring still requires the actual audited boundary.

Complete the remaining typed definitions with their positive source meaning, then discharge or explicitly account for original O/E/R/J requirements at their specified strength. Preserve all original requirements and existing sealed bytes. Source-owner accepted whole translations and whole-definition proofs remain zero in the current inventory. Semantic readiness is false and the original goal remains active.
"""
with (out/'ORIGINAL-SCOPE-REVIEW.md').open('x') as f:f.write(text)
print(json.dumps({'result':'Original-scope interim requirements accounting completed','work_units':797,'planned_outputs_present_units':present,'missing_planned_output_units':797-present,'review_words':len(text.split()),'semantic_ready':False,'goal_status':'active'}))

