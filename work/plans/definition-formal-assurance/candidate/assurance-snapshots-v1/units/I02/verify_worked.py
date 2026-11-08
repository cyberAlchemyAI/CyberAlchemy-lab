"""Freshly regenerate every selected worked revision and compare exact retained output."""
import json
import build_worked as b

def main():
 summary=json.loads((b.UNIT/'worked-summary.json').read_bytes());cases={}
 for name in ['unchanged','counterfactual','retirement']:
  row=summary[name]
  for key in ['selection_ref','output_ref']:
   if b.ref(b.ROOT/row[key]['path'])!=row[key]:raise ValueError('Changed worked input/output')
  fresh=b.d.analyze_selected(b.ROOT,row['selection_ref']);stored=json.loads((b.ROOT/row['output_ref']['path']).read_bytes())
  if not b.d.equal(fresh,stored) or fresh['status']!='candidate-revision-generated' or fresh['semantic_ready'] is not False:raise ValueError('Worked revision not exactly regenerated')
  cases[name]={'result':'PASS-for-exact-regeneration','derived_change':fresh['result']['derived_change'],'logical_requirements':len(fresh['result']['proposal_required_set']['logical_manifest']['obligations']),'whole_definition_proofs':0}
 source=b.d.i.live_recheck(b.d.i.read_epoch(b.ROOT,b.ref(b.BASE/'units/I01/current-epoch.json')),b.ROOT)
 print(json.dumps({'result':'PASS-for-fresh-selected-revision-regeneration','cases':cases,'source_files_current':source['source_files'],'authority_effect':'none','semantic_ready':False,'owner_fidelity':'pending','goal_status':'active'},indent=2,sort_keys=True))
if __name__=='__main__':main()
