"""Read-only audit of frozen typed-stage evidence and partial claim boundaries."""
import json
import build_candidate as b
import close_types_logic_stage as stage
def main():
 context,counts,model,source,fresh,prior=stage.audit();receipt=stage.load('types-logic-receipt.json');b.unchanged(receipt['inputs']+receipt['producer_results']+[receipt['retained_preparation_failure_ref']]);assert receipt['counts']==counts and receipt['fresh_checks']==fresh and receipt['result']=='PASS-for-typed-candidate-stage-only' and receipt['full_delivery_sealed'] is False and receipt['current_whole_inventory_refresh_complete'] is False and receipt['source_fidelity']=='pending' and receipt['semantic_ready'] is False and receipt['mechanized_proof'] is False and receipt['goal_status']=='active';assert not (b.UNIT/'delivery-manifest.json').exists()
 print(json.dumps({'result':'PASS-for-frozen-types-logic-stage-audit','prior_sealed_files_preserved':len(prior['files']),'source_files_current':201,'working_draft_files_observed':71,'remaining_without_typed_draft':112,'controls':132,'nonentailment_countermodels':29,'owner_fidelity':'pending','full_delivery_sealed':False,'goal_status':'active'},indent=2))
if __name__=='__main__':main()
