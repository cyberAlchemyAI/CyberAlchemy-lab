"""Separate actual read-only Project full audit and exact file-set equality."""
import json
import build_candidate as b
import finalize
def main():
 context,core,counts,inventory,graph,p,source,prior=finalize.audit();receipt=finalize.load('receipt.json');manifest=finalize.load('delivery-manifest.json');b.unchanged(receipt['inputs']+receipt['outputs']+manifest['files']+receipt['retained_successful_preparation_refs']+receipt['retained_successful_prepared_stage_refs'])
 assert receipt['task_result']=='PARTIAL-DRAFT-VERIFIED' and receipt['source_fidelity']=='pending' and receipt['semantic_ready'] is False and receipt['mechanized_proof'] is False and receipt['whole_definition_translation']=='pending' and receipt['whole_definition_proof'] is None and len(list((b.BASE/'definitions').glob('*/t.json')))==108 and receipt['retained_failed_native_attempt_refs']==receipt['retained_failed_consumer_comparison_refs']==[] and len(receipt['retained_failed_preparation_refs'])==9 and len(receipt['retained_successful_prepared_stage_refs'])==13 and len(receipt['cross_definition_review_findings'])==12 and receipt['validation']['accepted_Project_carrier_or_consumer_maps']==0 and receipt['validation']['actual_Project_activation_established'] is False
 for ref in receipt['external_source_refs']:assert b.r.digest(b.Path(ref['absolute_path']).read_bytes())==ref['sha256']
 assert receipt['validation']['retained_interrupted_full_replays']==1 and len(receipt['retained_interrupted_fresh_capture_refs'])>=20
 b.unchanged(receipt['retained_interrupted_fresh_capture_refs'])
 assert manifest['validation']==receipt['validation'] and manifest['prior_seal_files']==receipt['validation']['prior_candidate_files_preserved']==len(prior['files'])==10076
 current=sorted([b.ref(q) for folder in [b.BASE,b.IMPL] for q in folder.rglob('*') if q.is_file() and '__pycache__' not in q.parts and q.suffix!='.pyc' and q!=b.UNIT/'delivery-manifest.json'],key=lambda x:x['path']);assert current==manifest['files'],'Current files differ from full candidate seal'
 print(json.dumps({'result':'PASS-for-preservation-and-partial-claim-boundary','candidate_files':len(manifest['files']),'prior_candidate_files_preserved':len(prior['files']),'source_files_current':201,'partial_drafts':108,'missing_current_drafts':75,'unresolved_consumer_findings':12,'source_owner_accepted_whole_translations':0,'whole_definition_proofs':0,'actual_Project_activation_established':False,'semantic_ready':False,'goal_status':'active','next_definition_priority':finalize.NEXT},indent=2))
if __name__=='__main__':main()
