"""Separate read-only full audit and exact candidate file-set equality."""
import json
import build_candidate as b
import finalize
context,core,counts,inventory,graph,qualified,source,prior=finalize.audit();receipt,manifest=finalize.load('receipt.json'),finalize.load('delivery-manifest.json')
b.unchanged(receipt['inputs']+receipt['outputs']+manifest['files']+receipt['retained_failed_preparation_refs']+receipt['retained_successful_preparation_refs']+receipt['retained_failed_consumer_comparison_refs'])
assert receipt['task_result']=='PARTIAL-DRAFT-VERIFIED' and receipt['source_fidelity']=='pending' and receipt['semantic_ready'] is receipt['mechanized_proof'] is False and receipt['whole_definition_translation']=='pending' and receipt['whole_definition_proof'] is None
assert receipt['validation']['accepted_Implementation_carrier_or_consumer_maps']==0 and receipt['validation']['actual_Implementation_instance_effects_established'] is False and len(receipt['cross_definition_review_findings'])==17 and len(receipt['retained_failed_preparation_refs'])==14 and len(receipt['retained_failed_consumer_comparison_refs'])==5
assert manifest['validation']==receipt['validation'] and manifest['prior_seal_files']==len(prior['files'])==10497
current=sorted([b.ref(path) for folder in [b.BASE,b.IMPL] for path in folder.rglob('*') if path.is_file() and '__pycache__' not in path.parts and path.suffix!='.pyc' and path!=b.UNIT/'delivery-manifest.json'],key=lambda row:row['path']);assert current==manifest['files'],'Candidate file set differs from full seal'
print(json.dumps({'result':'PASS-for-Implementation-full-candidate-preservation-and-claim-boundary','candidate_files':len(current),'prior_candidate_files_preserved':10497,'partial_drafts':112,'missing_current_drafts':71,'accepted_maps':0,'whole_definition_proofs':0,'semantic_ready':False,'next_definition_priority':finalize.NEXT,'goal_status':'active'},indent=2))
