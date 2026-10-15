"""Exercise unchanged and counterfactual record revisions; never change admitted meanings."""
import hashlib
import json
import sys
from pathlib import Path
UNIT=Path(__file__).resolve().parent;ROOT=UNIT.parents[6];BASE=UNIT.parents[1];IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1';sys.path.insert(0,str(IMPL));import diff as d

def ref(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def put(path,value):
 with path.open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
 return ref(path)
def main():
 context=json.loads((UNIT/'context.json').read_bytes())
 for row in context['sources']:
  if ref(ROOT/row['path'])!=row:raise ValueError('Selected input changed')
 test=json.loads((UNIT/'attempt-003/result.json').read_bytes())
 if test['result']!='PASS':raise ValueError('Actual complete I02 suite required')
 projection=json.loads((BASE/'units/A08/projection.json').read_bytes());theory=json.loads((ROOT/projection['theory_ref']['path']).read_bytes());assumptions=put(UNIT/'selected-formal-assumptions.json',{'authority_effect':'none','assumption_set_id':theory['assumption_set_id'],'assumptions':[]});epoch_ref=ref(BASE/'units/I01/current-epoch.json')
 side={'epoch_ref':epoch_ref,'theory_ref':projection['theory_ref'],'relations_ref':projection['relations_ref'],'populations_ref':projection['populations_ref'],'bindings_ref':projection['endpoint_bindings_ref'],'assumptions_ref':assumptions}
 initial={'schema_version':'definition-assurance-revision-selection/v1-candidate','authority_effect':'none','baseline':side,'proposal':side,'declared_change':'unchanged','claims':[]}
 baseline_ref=put(UNIT/'unchanged-selection.json',initial);baseline=d.analyze_selected(ROOT,baseline_ref)
 if baseline['status']!='candidate-revision-generated' or baseline['result']['derived_change']!='unchanged':raise ValueError('Unchanged current control failed')
 baseline_output=put(UNIT/'unchanged-requirements.json',baseline)
 counter_theory=dict(theory);counter_theory['statements']=theory['statements']+[{'op':'forall','var':'r','sort':'Record','body':{'op':'implies','left':{'op':'pred','name':'Traceable','args':[{'op':'var','name':'r'}]},'right':{'op':'pred','name':'Position','args':[{'op':'var','name':'r'}]}}}]
 counter_ref=put(UNIT/'counterfactual-theory.json',counter_theory);proposal=dict(side);proposal['theory_ref']=counter_ref;selection={'schema_version':initial['schema_version'],'authority_effect':'none','baseline':side,'proposal':proposal,'declared_change':'representation-only','claims':[{'claim_id':'counterfactual-preserve-trace-outside-position','kind':'preservation','targets':['relation:TRACE-Position:left-difference'],'embedding_ref':None}]};selection_ref=put(UNIT/'counterfactual-selection.json',selection);counter=d.analyze_selected(ROOT,selection_ref)
 if counter['status']!='candidate-revision-generated' or counter['result']['derived_change']!='constraint-change' or len(counter['result']['invalidated_current_definitions'])!=7:raise ValueError('Mislabelled actual projection control failed')
 counter_output=put(UNIT/'counterfactual-requirements.json',counter);effective_ref=put(UNIT/'counterfactual-effective-theory.json',counter['result']['effective_proposal_theory'])
 relation_requests=json.loads((ROOT/projection['relations_ref']['path']).read_bytes());removed_ref=put(UNIT/'removed-relation-requests.json',[row for row in relation_requests if row['relation']['relation_id']!='TRACE-Position']);retired_proposal=dict(side);retired_proposal['relations_ref']=removed_ref;retired_selection={**initial,'proposal':retired_proposal,'declared_change':'representation-only'};retired_selection_ref=put(UNIT/'retirement-selection.json',retired_selection);retired=d.analyze_selected(ROOT,retired_selection_ref)
 if retired['status']!='candidate-revision-generated':raise ValueError('Retirement control failed')
 retired_rows=[x for x in retired['result']['requirement_ledger'] if x['category']=='logical' and x['status']=='removed-pending-retirement-review']
 if len(retired_rows)!=2:raise ValueError('Obsolete relation targets were silently lost')
 retired_output=put(UNIT/'retirement-requirements.json',retired)
 summary={'authority_effect':'none','semantic_ready':False,'goal_status':'active','global_current_source_nodes':183,'selected_partial_logical_sources':7,'whole_definition_proofs':0,'owner_fidelity':'pending','formal_assumption_selection':'No additional first-order formulas beyond the exact selected projection T. The source-level hypothetical assumptions, omissions and conditional record denotation remain bound by A07/A08 and are not discharged.','unchanged':{'selection_ref':baseline_ref,'output_ref':baseline_output,'logical_requirements':len(baseline['result']['proposal_required_set']['logical_manifest']['obligations']),'gates':len(baseline['result']['proposal_required_set']['administrative_and_semantic_gates'])},'counterfactual':{'selection_ref':selection_ref,'output_ref':counter_output,'effective_theory_ref':effective_ref,'declared_change':'representation-only','derived_change':'constraint-change','invalidated_selected_sources':7,'logical_requirements':len(counter['result']['proposal_required_set']['logical_manifest']['obligations']),'base_and_change_gates':len(counter['result']['proposal_required_set']['administrative_and_semantic_gates']),'supplemental_gates':len(counter['result']['supplemental_gates']),'extra_theorem_obligations':len(counter['result']['revision_claim_obligations']),'meaning':'Hostile counterfactual: forcing Traceable -> Position conflicts with the requested Traceable-outside-Position witness. This is not a recommended source edit or an accepted revision; I02 records required checks only.'},'retirement':{'selection_ref':retired_selection_ref,'output_ref':retired_output,'removed_prior_logical_targets':[x['requirement_id'] for x in retired_rows],'retirement_disposition':'pending-review; no old proof or requirement silently inherited/waived'},'source_fidelity':'pending','semantic_closure':'not-established','claim_ceiling':'Actual selected-scope obligation regeneration on unchanged and isolated counterfactual files. No checked preservation/conservativity proof, source edit or complete episode.'};put(UNIT/'worked-summary.json',summary);print(json.dumps(summary,indent=2,sort_keys=True))
if __name__=='__main__':main()
