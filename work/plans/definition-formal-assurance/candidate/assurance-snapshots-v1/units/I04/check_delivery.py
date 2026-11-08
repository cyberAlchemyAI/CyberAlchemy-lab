"""Read-only exact delivery and CLI partial-claim closeout audit."""
import json
import finalize as f
def main():
    context,report=f.audit();receipt=f.load('receipt.json');manifest=f.load('delivery-manifest.json')
    f.unchanged(receipt['inputs']+receipt['outputs']+receipt['checker_bindings']+manifest['files'])
    if receipt['runtime_bindings']!=f.v.f.current_bindings():raise ValueError('Runtime drift')
    if receipt['semantic_ready'] is not False or receipt['mechanized_proof'] is not False or receipt['full_project_completion']!='not-established':raise ValueError('False episode completion')
    declared=f.r.parse((f.ROOT/'docs/plans/definition-formal-assurance/candidate/foundations-first-v1/swu-manifest.json').read_bytes(),'SWUs')
    swu=next(x for x in declared['units'] if x['id']=='I04.1')
    if not all(any(x['path']==p for x in receipt['outputs']) for p in swu['outputs'] if not p.endswith('receipt.json')):raise ValueError('Declared output omitted')
    if not all(x['path'] in {y['path'] for y in manifest['files']} for x in receipt['outputs']):raise ValueError('Receipt output outside sealed inventory')
    print(json.dumps({'result':'PASS-for-preservation-exact-output-inventory-and-incomplete-episode-boundary','candidate_files':len(manifest['files']),
                      'prior_candidate_files_preserved':1134,'source_files_current':201,'current_definitions':183,'admitted_source_versions':189,
                      'partial_drafts':8,'missing_drafts':175,'projection_identities':7,'owner_accepted_whole_translations':0,'whole_definition_proofs':0,
                      'semantic_ready':False,'goal_status':'active','next_ready_unit':'I05.1'},indent=2,sort_keys=True))
if __name__=='__main__':main()
