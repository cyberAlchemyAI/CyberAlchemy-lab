"""Separate read-only Craft Method full candidate audit with exact file-set equality."""
import json
import build_candidate as b
import finalize
def main():
 context,core,counts,inventory,graph,p,source,prior=finalize.audit();receipt=finalize.load('receipt.json');manifest=finalize.load('delivery-manifest.json');b.unchanged(receipt['inputs']+receipt['outputs']+manifest['files']+receipt['retained_failed_preparation_refs']+receipt['retained_successful_preparation_refs']+receipt['retained_failed_consumer_comparison_refs'])
 assert receipt['task_result']=='PARTIAL-DRAFT-VERIFIED' and receipt['source_fidelity']=='pending' and receipt['semantic_ready'] is False and receipt['mechanized_proof'] is False and receipt['whole_definition_translation']=='pending' and receipt['whole_definition_proof'] is None and len(list((b.BASE/'definitions').glob('*/t.json')))==105 and receipt['retained_failed_native_attempt_refs']==[] and len(receipt['retained_failed_preparation_refs'])==10 and len(receipt['retained_failed_consumer_comparison_refs'])==5 and len(receipt['cross_definition_review_findings'])==8 and receipt['validation']['accepted_CraftMethod_carrier_or_consumer_maps']==0
 for ref in receipt['external_source_refs']:assert b.r.digest(b.Path(ref['absolute_path']).read_bytes())==ref['sha256']
 assert manifest['validation']==receipt['validation'] and manifest['prior_seal_files']==receipt['validation']['prior_candidate_files_preserved']==len(prior['files'])==9735
 current=sorted([b.ref(q) for folder in [b.BASE,b.IMPL] for q in folder.rglob('*') if q.is_file() and '__pycache__' not in q.parts and q.suffix!='.pyc' and q!=b.UNIT/'delivery-manifest.json'],key=lambda x:x['path']);assert current==manifest['files'],'Current files differ from full candidate seal'
 print(json.dumps({'result':'PASS-for-preservation-and-partial-claim-boundary','candidate_files':len(manifest['files']),'prior_candidate_files_preserved':len(prior['files']),'source_files_current':201,'partial_drafts':105,'missing_current_drafts':78,'unresolved_consumer_findings':8,'source_owner_accepted_whole_translations':0,'whole_definition_proofs':0,'semantic_ready':False,'goal_status':'active','next_definition_priority':finalize.NEXT},indent=2))
if __name__=='__main__':main()
