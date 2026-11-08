"""Select only reachable existing packets; no semantic closure from a draft count."""
import json
import build_candidate as b
import dependencies as d
import verifier as v
from static_snapshot_reuse import StaticSnapshotReuse
def dependencies(snapshot,reuse):
 context=json.loads((b.UNIT/'context.json').read_bytes());typed=json.loads((b.UNIT/'types-logic-receipt.json').read_bytes());prior=json.loads((b.BASE/'definitions/cal.definition.implementation/delivery-manifest.json').read_bytes());runtime=v.f.current_bindings()
 b.unchanged(typed['inputs']+typed['checker_bindings']+prior['files']+context['sources']);b.external_current(context)
 assert len(prior['files'])==10600 and len(typed['inputs'])==17 and len(typed['checker_bindings'])==5
 candidates={}
 for p in sorted((b.BASE/'definitions').glob('*/correspondence.json')):
  packet=json.loads(p.read_bytes());version=packet['interpretation']['source']['version_ref']
  if version in candidates:raise ValueError('Ambiguous source-qualified packet '+version)
  candidates[version]=(p,packet)
 root=json.loads((b.UNIT/'correspondence.json').read_bytes())['interpretation']['source'];todo=[root['version_ref']];seen=set();paths=[];packets=[]
 while todo:
  version=todo.pop(0)
  if version in seen:continue
  seen.add(version)
  if version not in candidates:continue
  p,packet=candidates[version];paths.append(p);packets.append(packet)
  todo += [x['version_ref'] for x in packet['interpretation']['depends_on']]
 selection={'authority_effect':'none','snapshot_ref':b.ref(b.BASE/'current-snapshot.json'),'root_source':root,'packet_refs':[b.ref(p) for p in paths],'engine_ref':b.ref(b.IMPL/'dependencies.py'),'static_reuse_implementation_ref':b.ref(b.UNIT/'static_snapshot_reuse.py'),'static_reuse_validation_ref':b.ref(b.UNIT/'static-snapshot-reuse-checks.json'),'cycle_policies':[],'required_edges':None}
 graph=d.compile_graph(snapshot,[root],packets,live_root=b.ROOT)
 reuse.finish();selection['static_snapshot_verification_reuse']=reuse.report()
 if graph['semantic_ready'] is not False or graph['edge_denominator']!='requires-independent-review' or any(x['disposition']!='unresolved-cycle-classification' for x in graph['cycle_reviews']):raise ValueError('Invented closure or cycle interpretation')
 if '--write' in b.sys.argv:b.put('dependency-selection.json',selection);b.put('dependency-graph.json',graph)
 else:
  for n,x in [('dependency-selection.json',selection),('dependency-graph.json',graph)]:
   if not b.r.same_json(json.loads((b.UNIT/n).read_bytes()),x):raise ValueError('Stale dependency selection/graph')
 b.unchanged(typed['inputs']+typed['checker_bindings']+prior['files']+context['sources']);b.external_current(context)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 b.unchanged([selection['snapshot_ref'],selection['engine_ref'],selection['static_reuse_implementation_ref'],selection['static_reuse_validation_ref'],*selection['packet_refs']]);b.r.verify(snapshot,b.ROOT)
 print(json.dumps({'result':'PASS-for-exact-authored-and-transitive-uses','nodes':len(graph['nodes']),'edges':len(graph['edges']),'direct_semantic_uses':len(json.loads((b.UNIT/'t.json').read_bytes())['payload']['depends_on']),'selected_existing_packets':len(packets),'missing_dependency_packet_count':len(graph['missing_or_quarantined_interpretations']),'unclassified_cycle_count':len(graph['cycle_reviews']),'semantic_ready':False,'edge_denominator':graph['edge_denominator']},indent=2,sort_keys=True))
def main():
 snapshot=b.snapshot()
 with StaticSnapshotReuse(b.r,snapshot) as reuse:dependencies(snapshot,reuse)
if __name__=='__main__':main()
