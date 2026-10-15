"""Complete the machine review; leave actual human assessment explicitly pending."""
from pathlib import Path
import sys,re,collections
sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'execution'));import support as s
sys.path.insert(0,str(BASE/'s13'));import audit_successor as audit
HERE=Path(__file__).resolve().parent
inventory=s.ROOT/'docs/plans/relational-theorem-checker/reviews/2026-10-09/implementation-analysis/definition-inventory.json'
s.context('S14',[(BASE/'s13/review-packet.md','concrete meaning/diagnostic/use assessment packet'),(BASE/'s13/pilot-report.json','actual scoped pilot results'),(inventory,'176 retained declarations and 17 successor concept requirements'),(BASE/'s01/requirements.json','independent source obligations and inherited unsupported'),(BASE/'s18/source-map.json','all 41 selected/deferred source meanings'),(BASE/'s10/qualification-audit.json','fresh exact trust qualification'),(BASE/'s11/stage-measurements.json','observed full and scoped performance'),(BASE/'s12/task-acceptance.json','optional reference fallback resolution'),(BASE/'s09/resource-exhaustion-audit.json','actual resource failure retained previous snapshot'),(s.ROOT/'docs/plans/relational-theorem-checker/PLAN-SOURCE.json','original R06/G4 remain pending')],[{'decision':'Finish current machine/evidence review before requesting human assessment','basis':'Concrete reviewable outcome; user authorized implementation but has not assessed the resulting meanings/diagnostics/use'},{'decision':'Keep S14 pending until actual feedback is recorded; no invented feedback or v1 human-gate discharge','basis':'S14 first acceptance criterion explicitly requires real human feedback'}])
plan=s.read(s.PLAN);accepted=[t for t in plan['tasks'] if t['status']=='accepted']
s.require(len(accepted)==17,'machine task inventory incomplete')
optional=s.task('S12');s.require(optional['status']=='not-needed','optional branch unresolved')
receipts=[s.check(t['receipt']) for t in accepted]
for p in receipts:s.audit_receipt(p)
closure=audit.binding_closure(receipts+[s.check(optional['receipt']),inventory,BASE/'s09/resource-exhaustion-audit.json'])
s.write(HERE/'final-source-closure.json',closure)
defs=s.read(inventory);formal=defs['formal_definitions']
for d in formal:
 p=s.check(d['source']);s.require(d['definition_excerpt'] in p.read_text(),'retained declaration changed '+d['id'])
concepts=[]
for d in defs['proposed_definitions']:
 refs=d['task_refs'];s.require(all(s.task(t)['status']=='accepted' for t in refs),'concept task not accepted '+d['name'])
 concepts.append({**d,'implementation_status':'scoped machine qualification accepted','evidence':[s.task(t)['receipt'] for t in refs],'external_truth_proved':False,'human_meaning_assessment':'pending'})
source=s.read(BASE/'s18/source-map.json');s.require(len(source['relations'])==41,'relation inventory incomplete')
requirements=s.read(BASE/'s01/requirements.json')
old=s.read(s.ROOT/'docs/plans/relational-theorem-checker/PLAN-SOURCE.json')
gates=[{'id':t['id'],'status':t['status']} for t in old['tasks'] if t['id'] in ['R06','G4']]
s.require(len(gates)==2 and all(t['status']!='accepted' for t in gates),'original human gates changed')
report={'schema':'relational.v2-final-requirement-audit/v1','machine_result':'pass','task_inventory':[{'id':t['id'],'status':t['status'],'receipt':t.get('receipt')} for t in plan['tasks']],'retained_declarations':{'count':len(formal),'inventory':s.binding(inventory),'result':'all exact excerpts and source byte bindings current; retained meanings unchanged'},'successor_concepts':concepts,'relations':source['relations'],'requirement_inventory':s.binding(BASE/'s01/requirements.json'),'inherited_unsupported':requirements['inherited_unsupported'],'interpretation_note':'Original unsupported rows remain original v1 claims. Selected v2 fragments have separate accepted task/proof evidence; this review does not discharge external truth or deferred semantics.','current_source_closure':s.binding(HERE/'final-source-closure.json'),'original_human_gates':gates,'human_feedback':None,'authority_effect':'none'}
s.write(HERE/'requirement-audit.json',report)
final={'schema':'relational.v2-final-review/v1','machine_result':'pass','completed_required_machine_tasks':17,'optional_tasks_resolved':{'S12':'not-needed; qualified reference selected'},'whole_plan_complete':False,'remaining_task':'S14 actual semantic/diagnostic/bounded-use feedback','reviewed_packet':s.binding(BASE/'s13/review-packet.md'),'feedback_template':s.binding(BASE/'s13/feedback-template.md'),'requirements':s.binding(HERE/'requirement-audit.json'),'human_feedback':None,'use_qualification':'pending human review','original_human_gates':gates,'deployment_or_publication_authorized_by_review':False,'authority_effect':'none'}
s.write(HERE/'final-review.json',final)
(HERE/'bounded-use-recommendation.md').write_text('''# Bounded-use review

Machine qualification passes for the selected candidate profile. Seventeen required machine tasks are accepted; optional S12 is resolved by retaining the qualified reference. The actual pilot includes exact target/scope/kind observations, recursive fresh predicates, wrong-scope absence in a complete finite closure, potential versus active norms, expiry, and two independently registered shadow successors.

Use qualification remains pending actual human feedback on [the worked packet](../s13/review-packet.md). S14 requires an assessment of intended meanings, useful diagnostics, and suitability for bounded local shadow use. Implementation authorization and author review do not supply that assessment. No feedback has been fabricated.

The candidate remains limited to finite selected profiles, supplied external truth, a tested decoder/source boundary, same pinned kernel replay, resource ceilings, and cooperative local writers. Deferred relation meanings remain explicit. The resource failure and unchanged-before-state evidence are [recorded separately](../s09/resource-exhaustion-audit.json); the same-statement proof splitting completed the demonstrated two-edit case without broadening the budget guarantee.

The [final requirement audit](requirement-audit.json) verifies all 176 retained declarations, 17 successor concepts, 41 relation source entries, accepted task artifacts and relevant transitive proof/source byte bindings. Historical task captures, deliberate stale-input tests, removed temporary host state and dynamic navigation snapshots are explicitly classified as nonqualification metadata. External governance documents are byte-bound input leaves. Original R06/G4 remain pending because this successor packet does not itself assess their original review artifacts. This review has no deployment, publication or live authority effect.
''')
# Validate local Markdown references in the worked final review material.
for p in [BASE/'s13/review-packet.md',HERE/'bounded-use-recommendation.md']:
 for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  if not target.startswith(('http:','https:','#')):s.require((p.parent/target).resolve().is_file(),'broken review link '+target)
s.write(HERE/'machine-review-controls.json',{'result':'pass','controls':['all required machine task receipts and optional resolution current','all relevant proof/source bindings current; historical/navigation/hostile metadata separately classified','176 exact retained declaration excerpts unchanged','17 proposed concept task dispositions verified','41 source relations preserved with selected/deferred ceilings','worked/final review local links resolve','actual human response absent and explicitly pending','original R06/G4 still pending'],'reviewed_outputs':[s.binding(HERE/f) for f in ['final-review.json','bounded-use-recommendation.md','requirement-audit.json']],'authority_effect':'none'})
s.sync();print('S14 machine review ready; actual human semantic/diagnostic/use feedback remains pending.')
