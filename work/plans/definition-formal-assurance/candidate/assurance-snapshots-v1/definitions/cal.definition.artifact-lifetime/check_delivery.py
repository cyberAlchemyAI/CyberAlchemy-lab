"""Read-only audit of Lifetime's exact sealed candidate set before native Surface creation."""
import json
import build_candidate as b
import finalize
def main():
 context,core,packet,counts,inventory,graph,profile,source,prior=finalize.audit();receipt=finalize.load('receipt.json');manifest=finalize.load('delivery-manifest.json');b.unchanged(receipt['inputs']+receipt['outputs']+manifest['files']);assert receipt['source_fidelity']=='pending' and receipt['semantic_ready'] is False and receipt['mechanized_proof'] is False and receipt['whole_definition_translation']=='pending' and len(list((b.BASE/'definitions').glob('*/t.json')))==83 and any(x['path']==b.ref(b.UNIT/'t.json')['path'] for x in receipt['outputs']) and len(receipt['retained_failed_native_attempt_refs'])==1 and len(receipt['retained_prior_preparation_failure_refs'])==2 and len(receipt['retained_next_source_inspection_failure_refs'])==1
 current=sorted([b.ref(q) for folder in [b.BASE,b.IMPL] for q in folder.rglob('*') if q.is_file() and '__pycache__' not in q.parts and q.suffix!='.pyc' and q!=b.UNIT/'delivery-manifest.json'],key=lambda x:x['path'])
 if current!=manifest['files']:raise ValueError('Current file set differs from seal')
 print(json.dumps({'result':'PASS-for-preservation-and-partial-claim-boundary','candidate_files':len(manifest['files']),'prior_candidate_files_preserved':len(prior['files']),'source_files_current':201,'partial_drafts':83,'missing_current_drafts':100,'retained_author_preflight_failures':1,'retained_next_source_inspection_failures':1,'source_owner_accepted_whole_translations':0,'whole_definition_proofs':0,'semantic_ready':False,'goal_status':'active','next_definition_priority':finalize.NEXT},indent=2,sort_keys=True))
if __name__=='__main__':main()
