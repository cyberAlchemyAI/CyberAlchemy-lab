"""Close prepared full CRB state only after actual seal and separate audit zero."""
from pathlib import Path
import hashlib,json
root=Path.cwd();prepared=Path(__file__).resolve().parent;unit=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.capability-realization-binding'
def load(path):return json.loads(path.read_bytes())
def ref(path):return {'path':str(path.relative_to(root)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
for stem in ['full-delivery-seal','full-delivery-audit']:
 result=load(prepared/(stem+'-command-result.json'));assert result['exit_code']==0 and not(prepared/result['stderr']).read_bytes()
manifest,receipt=load(unit/'delivery-manifest.json'),load(unit/'receipt.json');assert manifest['prior_seal_files']==10287 and manifest['validation']==receipt['validation']
for binding in manifest['files']+receipt['inputs']+receipt['outputs']:assert ref(root/binding['path'])==binding,binding['path']
inventory=load(unit/'current-inventory.json');assert inventory['partial_drafts']==110 and len(inventory['missing_current_drafts'])==73
fresh=load(unit/'fresh-command-results.json');assert len(fresh)==6 and all(x['exit_code']==0 and not(unit/x['stderr']).read_bytes() for x in fresh)
state_path=prepared/'current-state.json';previous=state_path.read_bytes()
with (prepared/'current-state-before-full-closeout.json').open('xb') as f:f.write(previous)
state=json.loads(previous);state.update({'completed_boundary':'Exact CRB typed stage,consumer/profile/reuse,qualified reachable graph,whole110 independent-witness inventory,sixfreshchecks,fullreview,fullseal andseparateactualfullaudit allcompleted zero.','full_delivery_sealed':True,'full_delivery_seal_exit_code':0,'full_delivery_separate_audit_exit_code':0,'candidate_files':len(manifest['files']),'current_whole_inventory_refresh_complete':True,'native_partial_drafts':110,'without_native_T':73,'current_inventory_counts':inventory['counts'],'joint_declared_graph':inventory['joint_declared_graph'],'reachable_graph':{'nodes':147,'edges':2677,'selected_existing_packets':107,'missing_counterpart_packets':40,'unclassified_cycles':1},'fresh_full_checks':[{'check':x['check'],'actual_exit_code':x['exit_code']} for x in fresh],'full_review_words':len((unit/'DELIVERY-REVIEW.md').read_text().split()),'full_review_aspects':13,'active_jobs':[],'source_fidelity':'pending','semantic_ready':False,'source_owner_accepted_whole_translations':0,'whole_definition_proofs':0,'goal_status':'active','next_action':'Execute F08-T.cal.definition.coordination-context fromexact C18source,definitions/types/logic first. Preserve original T/O/E/R/J andfinalepisode reviewrequirements;no actualauthority,fidelity orwholeproof inferred.'})
for path in [unit/'delivery-manifest.json',unit/'receipt.json',unit/'DELIVERY-REVIEW.md',unit/'current-inventory.json',unit/'current-dependency-graph.json',unit/'fresh-command-results.json',prepared/'full-delivery-seal-command-result.json',prepared/'full-delivery-audit-command-result.json',prepared/'current-state-before-full-closeout.json']:state['refs'].append(ref(path))
for binding in state['refs']:assert ref(root/binding['path'])==binding,binding['path']
state_path.write_text(json.dumps(state,indent=2,sort_keys=True)+'\n')
print(json.dumps({'result':'CRB-full-candidate-state-closed-after-actual-separateaudit0','candidate_files':len(manifest['files']),'partial_drafts':110,'withoutT':73,'semantic_ready':False,'goal_status':'active'},indent=2))
