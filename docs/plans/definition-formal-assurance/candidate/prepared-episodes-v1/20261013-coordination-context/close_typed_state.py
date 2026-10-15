"""Record actual typed closure and the full-delivery continuation without changing the freeze."""
from pathlib import Path
import hashlib,json,sys
root=Path.cwd();p=Path(__file__).resolve().parent;unit=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.coordination-context';sys.path.insert(0,str(unit));import build_candidate as b
for name in ['typed-stage-freeze','typed-stage-audit']:
 result=json.loads((p/(name+'-command-result.json')).read_bytes());assert result['exit_code']==0 and not(p/result['stderr']).read_bytes()
receipt=json.loads((unit/'types-logic-receipt.json').read_bytes());b.unchanged(receipt['inputs']+receipt['checker_bindings']+receipt['retained_preparation_failure_refs'])
assert receipt['source_fidelity']=='pending' and receipt['full_delivery_sealed'] is receipt['semantic_ready'] is False
context=json.loads((unit/'context.json').read_bytes());b.unchanged(context['sources']+context['retained_successful_preparation_refs']);b.external_current(context)
prior=json.loads((b.BASE/'definitions/cal.definition.capability-realization-binding/delivery-manifest.json').read_bytes());b.unchanged(prior['files']);assert len(prior['files'])==10389
dirty=json.loads((p.parent/'20261012-project/unrelated-tracked-work.json').read_bytes());b.unchanged(dirty['refs']);assert len(dirty['refs'])==30
assert b.r.verify(b.snapshot(),root)['files']==201
active=[]
patterns=['run_prepared.py','run_native.py','run_fresh_types.py','capture_typed_boundary.py','close_types_logic_stage.py','check_types_logic_stage.py','verify_candidate.py','verify_source_checks.py']
for proc in Path('/proc').iterdir():
 if not proc.name.isdigit():continue
 try:argv=(proc/'cmdline').read_bytes().split(b'\0')
 except (FileNotFoundError,PermissionError,ProcessLookupError):continue
 if len(argv)>=3 and any(arg.decode(errors='replace').endswith('/'+name) for arg in argv[1:] for name in patterns) and any(b'20261013-coordination-context' in arg or b'cal.definition.coordination-context' in arg for arg in argv):active.append(int(proc.name))
assert not active,active
evidence=[b.ref(p/name) for name in ['typed-stage-freeze-command-result.json','typed-stage-freeze-stdout.txt','typed-stage-freeze-stderr.txt','typed-stage-audit-command-result.json','typed-stage-audit-stdout.txt','typed-stage-audit-stderr.txt','current-consumer-discovery.json']]+[b.ref(unit/'types-logic-receipt.json')]
state={'schema_version':'CoordinationContext-typed-stage-current-state/v1-candidate','authority_effect':'none','goal_status':'active','previous_goal_turn':'no-progress status restatement; revalidated before executing this typed stage','this_goal_turn':'progress: prepared and native source/build/model checks, independent source checks, three fresh checks, typed freeze and separate audit all actual0','current_stage':'types-and-logic-closed','native_definition_id':'cal.definition.coordination-context','actual_typed_freeze_exit':0,'actual_separate_typed_audit_exit':0,'frozen_inputs':17,'frozen_checkers':5,'controls':198,'nonentailment_queries':32,'source_checks':86,'source_query_obligations':74,'review_words':len((unit/'REVIEW.md').read_text().split()),'review_aspects':13,'source_findings_pending':21,'source_fidelity':'pending','semantic_ready':False,'source_owner_accepted_whole_translations':0,'whole_definition_proofs':0,'full_delivery_sealed':False,'source_files_current':201,'predecessor_files_preserved':10389,'unrelated_tracked_files_preserved':30,'current_partial_drafts_observed':111,'original_scope':{'identities':183,'versions':189,'source_files':201,'tasks':121,'planning_edges':511,'work_units':797,'frontiers':36,'obligations':'T/O/E/R/J and final complete aspect review'},'retained_preparation_failures':2,'evidence':evidence,'active_this_stage_jobs':active,'next_action':'Coordination Context full consumer/profile/reuse/dependency/inventory/fresh-six/review/seal/separate-audit closure','next_definition_only_after_full_closure':context['next_definition_priority'],'consumer_discovery':{'files_read':79,'exact_matching_bindings':45,'accepted_maps':[]},'required_claim_ceiling':'Typed finite candidate evidence only; original episode completion and accepted denotations remain unproven.'}
with (p/'current-state.json').open('x') as f:json.dump(state,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps({key:state[key] for key in ['current_stage','actual_typed_freeze_exit','actual_separate_typed_audit_exit','controls','source_checks','active_this_stage_jobs','full_delivery_sealed','goal_status']},indent=2))
