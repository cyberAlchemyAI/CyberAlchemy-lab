"""Bind all current sources and all eight existing accounted packets; no closure claim."""
import hashlib
import json
import sys
from pathlib import Path
UNIT=Path(__file__).resolve().parent;ROOT=UNIT.parents[6];BASE=UNIT.parents[1];IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1';sys.path.insert(0,str(IMPL));import invalidation as i

def ref(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def put(path,value):
 with path.open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
def main():
 context=json.loads((UNIT/'context.json').read_bytes())
 for row in context['sources']:
  if ref(ROOT/row['path'])!=row:raise ValueError('Changed selected input')
 result=json.loads((UNIT/'attempt-002/result.json').read_bytes())
 if result['result']!='PASS' or result['return_code']!=0:raise ValueError('Actual passing I01 validation required')
 snapshot_ref=ref(BASE/'current-snapshot.json');snapshot=json.loads((ROOT/snapshot_ref['path']).read_bytes());pilot=json.loads((BASE/'pilot-v2/interpretation.json').read_bytes());packets=[ref(BASE/'units/A04/hypothesis-review-packet.json')]+[row['packet_ref'] for row in pilot['source_packets']]
 roots=[i.d.source_ref(row) for row in snapshot['current_entries']]
 selection={'snapshot_ref':snapshot_ref,'roots':roots,'packet_refs':packets,'cycle_policies':[],'required_edges':None,'bindings':[{'definition_id':row['definition_id'],'artifacts':{role:[] for role in i.ROLES}} for row in snapshot['current_entries']]}
 epoch=i.capture_epoch(ROOT,selection);put(UNIT/'current-epoch.json',epoch);plan=i.compare_selected(ROOT,ref(UNIT/'current-epoch.json'),ref(UNIT/'current-epoch.json'));put(UNIT/'baseline-unchanged-plan.json',plan);source=i.live_recheck(epoch,ROOT)
 boundary={'authority_effect':'none','semantic_ready':False,'source_files_rechecked':source['source_files'],'current_source_nodes':len(epoch['nodes']),'existing_source_accounting_packets':len(packets),'missing_or_quarantined_interpretations':len(epoch['coverage']['missing_or_quarantined_interpretations']),'pending_packet_correspondence_or_fidelity':len(epoch['coverage']['pending_correspondence_or_fidelity']),'validated_authored_dependency_edges':len(epoch['graph_projection']['edges']),'edge_denominator':epoch['coverage']['edge_denominator'],'cache_candidates_in_unchanged_baseline':len(plan['unaffected_cache_candidates']),'actual_cached_proofs_reused':0,'owner_accepted_whole_definition_translations':0,'whole_definition_proofs':0,'meaning':'All183 current sources and eight existing accounting packets are byte-bound; missing translations/declared semantic uses/fidelity remain pending. Unchanged baseline is not whole-theory regression or semantic closure.','epoch_ref':ref(UNIT/'current-epoch.json'),'unchanged_plan_ref':ref(UNIT/'baseline-unchanged-plan.json'),'goal_status':'active'};put(UNIT/'current-boundary.json',boundary);print(json.dumps(boundary,indent=2,sort_keys=True))
if __name__=='__main__':main()
