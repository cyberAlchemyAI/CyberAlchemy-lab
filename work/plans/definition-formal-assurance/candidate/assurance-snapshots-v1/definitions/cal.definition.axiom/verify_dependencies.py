"""Bind and replay only authored Axiom semantic uses, preserving four missing dependency packets."""
import json
import build_candidate as b
import dependencies as d

def main():
 packet=json.loads((b.UNIT/'correspondence.json').read_bytes());snapshot=b.snapshot();selection={'snapshot_ref':b.ref(b.BASE/'current-snapshot.json'),'root_source':packet['interpretation']['source'],'packet_ref':b.ref(b.UNIT/'correspondence.json'),'engine_ref':b.ref(b.IMPL/'dependencies.py'),'required_edges':None,'cycle_policies':[],'authority_effect':'none'}
 expected=d.compile_graph(snapshot,[selection['root_source']],[packet],live_root=b.ROOT)
 if len(expected['nodes'])!=5 or len(expected['edges'])!=4 or len(expected['missing_or_quarantined_interpretations'])!=4 or expected['semantic_ready'] is not False or expected['edge_denominator']!='requires-independent-review':raise ValueError('Wrong source-bound closure or invented readiness')
 if '--write' in b.sys.argv:b.put('dependency-selection.json',selection);b.put('dependency-graph.json',expected)
 else:
  for name,value in [('dependency-selection.json',selection),('dependency-graph.json',expected)]:
   if not b.r.same_json(json.loads((b.UNIT/name).read_bytes()),value):raise ValueError('Stale or substituted '+name)
 for key in ['snapshot_ref','packet_ref','engine_ref']:
  if b.ref(b.ROOT/selection[key]['path'])!=selection[key]:raise ValueError('Closing dependency-input drift')
 print(json.dumps({'result':'PASS-for-exact-authored-uses','nodes':5,'authored_edges':4,'missing_dependency_packets':expected['missing_or_quarantined_interpretations'],'semantic_ready':False,'edge_denominator':'requires-independent-review'},indent=2,sort_keys=True))
if __name__=='__main__':main()
