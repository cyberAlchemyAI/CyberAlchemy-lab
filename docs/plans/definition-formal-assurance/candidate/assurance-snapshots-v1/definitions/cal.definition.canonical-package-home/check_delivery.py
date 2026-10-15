"""Separate exact CanonicalPackageHome full delivery preservation and claim-boundary audit."""
import json
import build_candidate as b
import finalize

def main():
 context,core,packet,counts,inventory,graph,profile,source,prior=finalize.audit();receipt=finalize.load('receipt.json');manifest=finalize.load('delivery-manifest.json');b.unchanged(receipt['inputs']+receipt['outputs']+manifest['files']);assert receipt['task_result']=='PARTIAL-DRAFT-VERIFIED' and receipt['source_fidelity']=='pending' and receipt['semantic_ready'] is False and receipt['mechanized_proof'] is False and receipt['whole_definition_translation']=='pending' and len(list((b.BASE/'definitions').glob('*/t.json')))==88 and receipt['retained_failed_native_attempt_refs']==[] and len(receipt['retained_prior_preparation_failure_refs'])==2 and receipt['retained_failed_typed_stage_preparation_refs']==[] and receipt['validation']['retained_preparation_failures']==2 and receipt['retained_failed_native_profile_attempt_refs']==[] and len(receipt['cross_definition_review_findings'])==5 and receipt['validation']['accepted_CanonicalPackageHome_carrier_or_consumer_maps']==0
 current=sorted([b.ref(q) for folder in [b.BASE,b.IMPL] for q in folder.rglob('*') if q.is_file() and '__pycache__' not in q.parts and q.suffix!='.pyc' and q!=b.UNIT/'delivery-manifest.json'],key=lambda x:x['path']);assert current==manifest['files'],'Current file set differs from seal'
 print(json.dumps({'result':'PASS-for-preservation-and-partial-claim-boundary','candidate_files':len(manifest['files']),'prior_candidate_files_preserved':7715,'source_files_current':201,'partial_drafts':88,'missing_current_drafts':95,'unresolved_consumer_findings':5,'source_owner_accepted_whole_translations':0,'whole_definition_proofs':0,'semantic_ready':False,'goal_status':'active','next_definition_priority':finalize.NEXT},indent=2))
if __name__=='__main__':main()
