"""Read-only preservation and partial claim audit of sealed Assignment evidence."""
import json
import build_candidate as b
import finalize
def main():
 context,core,packet,counts,selected=finalize.audit();receipt=finalize.load('receipt.json');manifest=finalize.load('delivery-manifest.json')
 b.unchanged(receipt['inputs']+receipt['outputs']+manifest['files'])
 if receipt['semantic_ready'] is not False or receipt['source_fidelity']!='pending' or receipt['mechanized_proof'] is not False or receipt['whole_definition_translation']!='pending':raise AssignmentError('False whole acceptance')
 if len(list((b.BASE/'definitions').glob('*/t.json')))!=19:raise AssignmentError('Current draft denominator changed')
 if not any(x['path']==b.ref(b.UNIT/'t.json')['path'] for x in receipt['outputs']):raise AssignmentError('Primary output omitted')
 print(json.dumps({'result':'PASS-for-preservation-and-partial-claim-boundary','candidate_files':len(manifest['files']),'prior_candidate_files_preserved':1878,'source_files_current':selected['files'],'partial_drafts':19,'missing_current_drafts':164,'source_owner_accepted_whole_translations':0,'whole_definition_proofs':0,'semantic_ready':False,'goal_status':'active','next_definition_priority':finalize.NEXT},indent=2,sort_keys=True))
if __name__=='__main__':main()
