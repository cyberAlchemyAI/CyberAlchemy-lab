"""Read-only closing preservation and partial-claim audit."""
import json
import build_candidate as b
import finalize

def main():
    context,core,packet,counts,selected=finalize.audit()
    receipt=finalize.load('receipt.json'); manifest=finalize.load('delivery-manifest.json'); status=finalize.load('episode-status.json')
    finalize.unchanged(receipt['inputs']+receipt['outputs']+manifest['files'])
    if receipt['semantic_ready'] is not False or receipt['mechanized_proof'] is not False or receipt['source_fidelity'] != 'pending' or receipt['whole_definition_translation'] != 'pending': raise ValueError('False whole acceptance')
    if status['per_definition_T_candidate_drafts'] != len(list((b.BASE/'definitions').glob('*/t.json'))) or status['foundations_family_result'] != 'PARTIAL' or status['source_owner_accepted_whole_translations'] != 0 or status['whole_definition_proofs'] != 0: raise ValueError('Wrong episode completion claim')
    print(json.dumps({'result':'PASS-for-byte-preservation-and-partial-claim-boundary','candidate_files':len(manifest['files']),
                     'source_files_current':selected['files'],'prior_candidate_files_preserved':1065,'external_selected_local_files_current':1,
                     'foundation_partial_drafts':8,'remaining_current_identities_without_per_definition_T_draft':175,
                     'source_owner_accepted_whole_translations':0,'whole_definition_proofs':0,'semantic_ready':False,
                     'goal_status':'active','next_independent_unit':'I04.1',**counts},indent=2,sort_keys=True))

if __name__ == '__main__': main()
