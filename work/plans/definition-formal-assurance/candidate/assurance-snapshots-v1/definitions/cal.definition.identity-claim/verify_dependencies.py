"""Select only reachable existing packets; no semantic closure from a draft count."""
import json
import build_candidate as b
import dependencies as d
def main():
 candidates={}
 for p in sorted((b.BASE/'definitions').glob('*/correspondence.json')):
  packet=json.loads(p.read_bytes());candidates[packet['interpretation']['source']['version_ref']]=(p,packet)
 root=json.loads((b.UNIT/'correspondence.json').read_bytes())['interpretation']['source'];todo=[root['version_ref']];seen=set();paths=[];packets=[]
 while todo:
  version=todo.pop(0)
  if version in seen:continue
  seen.add(version)
  if version not in candidates:continue
  p,packet=candidates[version];paths.append(p);packets.append(packet)
  todo += [x['version_ref'] for x in packet['interpretation']['depends_on']]
 selection={'authority_effect':'none','snapshot_ref':b.ref(b.BASE/'current-snapshot.json'),'root_source':root,'packet_refs':[b.ref(p) for p in paths],'engine_ref':b.ref(b.IMPL/'dependencies.py'),'cycle_policies':[],'required_edges':None}
 graph=d.compile_graph(b.snapshot(),[root],packets,live_root=b.ROOT)
 if graph['semantic_ready'] is not False or graph['edge_denominator']!='requires-independent-review' or any(x['disposition']!='unresolved-cycle-classification' for x in graph['cycle_reviews']):raise ValueError('Invented closure or cycle interpretation')
 if '--write' in b.sys.argv:b.put('dependency-selection.json',selection);b.put('dependency-graph.json',graph)
 else:
  for n,x in [('dependency-selection.json',selection),('dependency-graph.json',graph)]:
   if not b.r.same_json(json.loads((b.UNIT/n).read_bytes()),x):raise ValueError('Stale dependency selection/graph')
 b.unchanged([selection['snapshot_ref'],selection['engine_ref'],*selection['packet_refs']])
 print(json.dumps({'result':'PASS-for-exact-authored-and-transitive-uses','nodes':len(graph['nodes']),'edges':len(graph['edges']),'direct_semantic_uses':18,'selected_existing_packets':len(packets),'missing_dependency_packets':graph['missing_or_quarantined_interpretations'],'cycles':graph['cycle_reviews'],'semantic_ready':False,'edge_denominator':graph['edge_denominator']},indent=2,sort_keys=True))
if __name__=='__main__':main()
