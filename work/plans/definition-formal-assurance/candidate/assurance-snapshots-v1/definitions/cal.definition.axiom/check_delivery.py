"""Read-only audit of the sealed partial Axiom draft and preserved earlier candidate delivery."""
import json
import build_candidate as b

def main():
 receipt=json.loads((b.UNIT/'receipt.json').read_bytes());manifest=json.loads((b.UNIT/'delivery-manifest.json').read_bytes());prior=json.loads((b.BASE/'units/I03/delivery-manifest.json').read_bytes())
 for reference in receipt['inputs']+receipt['outputs']+manifest['files']+prior['files']:
  if b.ref(b.ROOT/reference['path'])!=reference:raise ValueError('Changed bound bytes: '+reference['path'])
 source=b.r.verify(b.snapshot(),b.ROOT)
 if receipt['whole_definition_translation']!='pending' or receipt['source_fidelity']!='pending' or receipt['semantic_ready'] is not False or receipt['mechanized_proof'] is not False or receipt['validation']['model_controls']!=22 or source['files']!=201:raise ValueError('False acceptance or wrong denominator')
 print(json.dumps({'result':'PASS-for-byte-preservation-and-partial-claim-boundary','candidate_files':len(manifest['files']),'prior_candidate_files_preserved':len(prior['files']),'source_files_current':source['files'],'model_controls':22,'whole_translation':'pending','source_fidelity':'pending','semantic_ready':False,'goal_status':'active','next_independent_unit':'F01-T.cal.definition.definition'},indent=2,sort_keys=True))
if __name__=='__main__':main()
