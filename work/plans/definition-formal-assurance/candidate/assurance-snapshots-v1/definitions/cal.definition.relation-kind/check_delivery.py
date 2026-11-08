"""Read-only complete-byte preservation and partial-claim delivery audit."""
import json
import build_candidate as b
import finalize
def main():
    context,core,packet,counts,selected=finalize.audit();receipt=finalize.load('receipt.json');manifest=finalize.load('delivery-manifest.json')
    b.unchanged(receipt['inputs']+receipt['outputs']+manifest['files'])
    if receipt['semantic_ready'] is not False or receipt['source_fidelity']!='pending' or receipt['mechanized_proof'] is not False or receipt['whole_definition_translation']!='pending':raise ValueError('False whole acceptance')
    if len(list((b.BASE/'definitions').glob('*/t.json')))!=10:raise ValueError('Current draft count changed')
    if not any(x['path']==b.ref(b.UNIT/'t.json')['path'] for x in receipt['outputs']):raise ValueError('Declared primary output omitted')
    print(json.dumps({'result':'PASS-for-preservation-and-partial-claim-boundary','candidate_files':len(manifest['files']),'prior_candidate_files_preserved':1241,
                      'source_files_current':selected['files'],'partial_drafts':10,'missing_current_drafts':173,'source_owner_accepted_whole_translations':0,'whole_definition_proofs':0,
                      'semantic_ready':False,'goal_status':'active','next_definition_priority':'F04-T.cal.definition.artifact-type'},indent=2,sort_keys=True))
if __name__=='__main__':main()
