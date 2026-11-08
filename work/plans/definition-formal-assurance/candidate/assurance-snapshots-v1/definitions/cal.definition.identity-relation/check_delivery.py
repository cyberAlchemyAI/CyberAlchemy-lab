"""Read-only full-byte preservation and partial-claim audit."""
import json
import build_candidate as b
import finalize
def main():
 context,core,packet,counts,selected=finalize.audit();receipt=finalize.load('receipt.json');manifest=finalize.load('delivery-manifest.json')
 b.unchanged(receipt['inputs']+receipt['outputs']+manifest['files'])
 if receipt['semantic_ready'] is not False or receipt['source_fidelity']!='pending' or receipt['mechanized_proof'] is not False or receipt['whole_definition_translation']!='pending':raise ValueError('False whole acceptance')
 if len(list((b.BASE/'definitions').glob('*/t.json')))!=13:raise ValueError('Current draft denominator changed')
 if not any(x['path']==b.ref(b.UNIT/'t.json')['path'] for x in receipt['outputs']):raise ValueError('Primary output omitted')
 print(json.dumps({'result':'PASS-for-preservation-and-partial-claim-boundary','candidate_files':len(manifest['files']),'prior_candidate_files_preserved':1474,'source_files_current':selected['files'],'partial_drafts':13,'missing_current_drafts':170,'source_owner_accepted_whole_translations':0,'whole_definition_proofs':0,'semantic_ready':False,'goal_status':'active','next_definition_priority':'F07-T.cal.definition.typed-coupling-invariant'},indent=2,sort_keys=True))
if __name__=='__main__':main()
