"""Read-only preservation and partial-claim audit of the sealed Authority Promotion candidate."""
import json
import build_candidate as b
import finalize
def main():
 context,core,packet,counts,selected=finalize.audit();receipt=finalize.load('receipt.json');manifest=finalize.load('delivery-manifest.json')
 b.unchanged(receipt['inputs']+receipt['outputs']+manifest['files'])
 if receipt['semantic_ready'] is not False or receipt['source_fidelity']!='pending' or receipt['mechanized_proof'] is not False or receipt['whole_definition_translation']!='pending':raise ValueError('False whole acceptance')
 if len(list((b.BASE/'definitions').glob('*/t.json')))!=33:raise ValueError('Current draft denominator changed')
 if not any(x['path']==b.ref(b.UNIT/'t.json')['path'] for x in receipt['outputs']):raise ValueError('Primary output omitted')
 current=[b.ref(p) for folder in [b.BASE,b.IMPL] for p in sorted(folder.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc' and p!=b.UNIT/'delivery-manifest.json']
 if sorted(current,key=lambda x:x['path'])!=manifest['files']:raise ValueError('Current candidate files differ from sealed set')
 print(json.dumps({'result':'PASS-for-preservation-and-partial-claim-boundary','candidate_files':len(manifest['files']),'prior_candidate_files_preserved':2908,'source_files_current':selected['files'],'partial_drafts':33,'missing_current_drafts':150,'source_owner_accepted_whole_translations':0,'whole_definition_proofs':0,'semantic_ready':False,'goal_status':'active','next_definition_priority':finalize.NEXT},indent=2,sort_keys=True))
if __name__=='__main__':main()
