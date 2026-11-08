"""Read-only exact sealed-file and partial-claim audit before next-unit creation."""
import json
import build_candidate as b
import finalize
def main():
 context,core,packet,counts,inventory,graph,profile,source,prior=finalize.audit();receipt=finalize.load('receipt.json');manifest=finalize.load('delivery-manifest.json');b.unchanged(receipt['inputs']+receipt['outputs']+manifest['files'])
 if receipt['semantic_ready'] is not False or receipt['source_fidelity']!='pending' or receipt['mechanized_proof'] is not False or receipt['whole_definition_translation']!='pending':raise ValueError('False whole acceptance')
 if len(list((b.BASE/'definitions').glob('*/t.json')))!=72:raise ValueError('Draft denominator changed')
 if not any(x['path']==b.ref(b.UNIT/'t.json')['path'] for x in receipt['outputs']):raise ValueError('Primary output omitted')
 current=sorted([b.ref(q) for folder in [b.BASE,b.IMPL] for q in folder.rglob('*') if q.is_file() and '__pycache__' not in q.parts and q.suffix!='.pyc' and q!=b.UNIT/'delivery-manifest.json'],key=lambda x:x['path'])
 if current!=manifest['files']:raise ValueError('Current files differ from sealed set')
 print(json.dumps({'result':'PASS-for-preservation-and-partial-claim-boundary','candidate_files':len(manifest['files']),'prior_candidate_files_preserved':len(prior['files']),'source_files_current':201,'partial_drafts':72,'missing_current_drafts':111,'source_owner_accepted_whole_translations':0,'whole_definition_proofs':0,'semantic_ready':False,'goal_status':'active','next_definition_priority':finalize.NEXT},indent=2,sort_keys=True))
if __name__=='__main__':main()
