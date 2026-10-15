"""Record actual full closure, preserving the original unfinished goal."""
from pathlib import Path
import hashlib,json,sys,os
root=Path.cwd();p=Path(__file__).resolve().parent
u=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.intent'
sys.path.insert(0,str(u));import build_candidate as b
def load(path):return json.loads(path.read_bytes())
def ref(path):return {'path':str(path.relative_to(root)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
evidence=[]
for stem in ['full-delivery-seal','full-delivery-audit']:
    record=load(p/(stem+'-command-result.json'));assert record['exit_code']==0 and not(p/record['stderr']).read_bytes()
    evidence.extend(ref(p/name) for name in [stem+'-command-result.json',record['stdout'],record['stderr']])
manifest=load(u/'delivery-manifest.json');receipt=load(u/'receipt.json');typed=load(u/'types-logic-receipt.json');context=load(u/'context.json');inventory=load(u/'current-inventory.json')
b.unchanged(manifest['files']+receipt['inputs']+receipt['outputs']+typed['inputs']+typed['checker_bindings']+context['sources']);b.external_current(context)
assert b.r.verify(b.snapshot(),root)['files']==201
dirty=load(p.parent/'20261012-project/unrelated-tracked-work.json');b.unchanged(dirty['refs']);assert len(dirty['refs'])==30
assert inventory['partial_drafts']==113 and len(inventory['missing_current_drafts'])==70 and len(list((b.BASE/'definitions').glob('*/t.json')))==113
assert receipt['source_fidelity']=='pending' and receipt['semantic_ready'] is False and receipt['task_result']=='PARTIAL-DRAFT-VERIFIED'
assert receipt['validation']['accepted_Intent_carrier_or_consumer_maps']==0 and receipt['validation']['actual_Intent_instance_effects_established'] is False
active=[]
for proc in Path('/proc').glob('[0-9]*'):
    if int(proc.name)==os.getpid():continue
    try:argv=(proc/'cmdline').read_bytes().split(b'\x00')
    except (OSError,PermissionError):continue
    if any(arg.startswith(str(u).encode()+b'/') and arg.endswith(b'.py') for arg in argv):active.append({'pid':int(proc.name),'argv':[a.decode(errors='replace') for a in argv if a]})
assert not active,active
evidence.extend(ref(u/name) for name in ['delivery-manifest.json','receipt.json','DELIVERY-REVIEW.md','work-delivery-dag.json','current-inventory.json','current-dependency-graph.json'])
record={'schema_version':'Intent-full-stage-current-state/v1-candidate','authority_effect':'none','goal_status':'active','current_stage':'full-candidate-delivery-closed','full_delivery_sealed':True,'actual_full_seal_exit':0,'actual_separate_full_audit_exit':0,'active_this_stage_jobs':active,'native_definition_id':'cal.definition.intent','source_selection':context['source_selection'],'current_admission_ref':context['current_admission_ref'],'candidate_files_sealed':len(manifest['files']),'predecessor_files_preserved':10600,'frozen_inputs':17,'frozen_checkers':5,'source_files_current':201,'unrelated_tracked_files_preserved':30,'counts':load(u/'denominator.json'),'validation':receipt['validation'],'current_partial_drafts':113,'current_identities_without_T':70,'current_inventory_counts':inventory['counts'],'joint_graph_summary':{'nodes':len(load(u/'current-dependency-graph.json')['nodes']),'edges':len(load(u/'current-dependency-graph.json')['edges']),'missing_counterparts':len(load(u/'current-dependency-graph.json')['missing_or_quarantined_interpretations']),'unresolved_cycle_classifications':len(load(u/'current-dependency-graph.json')['cycle_reviews'])},'consumer_findings_pending':18,'source_findings_pending':23,'accepted_maps':0,'source_fidelity':'pending','semantic_ready':False,'source_owner_accepted_whole_translations':0,'whole_definition_proofs':0,'retained_Intent_preparation_failures':0,'retained_Intent_consumer_failures':0,'whole_episode_complete':False,'original_scope':{'identities':183,'versions':189,'source_files':201,'tasks':121,'planning_edges':511,'work_units':797,'frontiers':36,'obligations':'T/O/E/R/J and final complete aspect review'},'next_definition_only_after_full_closure':'F08-T.cal.definition.intent-resolution','next_action':'Exact admitted Intent Resolution source preparation, then definitions/types/logic first','this_goal_turn':'progress: full Intent producers, six fresh checks, review, seal and separate audit actual0','evidence':evidence}
with(p/'full-current-state.json').open('x') as f:json.dump(record,f,indent=2);f.write('\n')
print(json.dumps({'result':'PASS-for-actual-Intent-full-closeout','candidate_files_sealed':len(manifest['files']),'partial_drafts':113,'missing_current_drafts':70,'goal_status':'active','semantic_ready':False,'next_definition':record['next_definition_only_after_full_closure']}))
