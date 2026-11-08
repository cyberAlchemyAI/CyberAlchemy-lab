"""Exact Relation Kind dependencies; missing counterparts and cycles stay open."""
import json
import build_candidate as b
import dependencies as d
def main():
    paths=[b.UNIT/'correspondence.json',*[b.BASE/'definitions'/identity/'correspondence.json' for identity in ['cal.definition.typed-relation','cal.definition.governed-model','cal.definition.definition']]]
    packets=[json.loads(p.read_bytes()) for p in paths]
    selection={'authority_effect':'none','snapshot_ref':b.ref(b.BASE/'current-snapshot.json'),'root_source':packets[0]['interpretation']['source'],
               'packet_refs':[b.ref(p) for p in paths],'engine_ref':b.ref(b.IMPL/'dependencies.py'),'cycle_policies':[],'required_edges':None}
    graph=d.compile_graph(b.snapshot(),[selection['root_source']],packets,live_root=b.ROOT)
    if graph['semantic_ready'] is not False or graph['edge_denominator']!='requires-independent-review' or any(x['disposition']!='unresolved-cycle-classification' for x in graph['cycle_reviews']):raise ValueError('Invented closure or cycle interpretation')
    if '--write' in b.sys.argv:b.put('dependency-selection.json',selection);b.put('dependency-graph.json',graph)
    else:
        for n,x in [('dependency-selection.json',selection),('dependency-graph.json',graph)]:
            if not b.r.same_json(json.loads((b.UNIT/n).read_bytes()),x):raise ValueError('Stale dependency selection/graph')
    b.unchanged([selection['snapshot_ref'],selection['engine_ref'],*selection['packet_refs']])
    print(json.dumps({'result':'PASS-for-exact-authored-and-transitive-uses','nodes':len(graph['nodes']),'edges':len(graph['edges']),
                      'direct_semantic_uses':6,'missing_dependency_packets':graph['missing_or_quarantined_interpretations'],
                      'cycles':graph['cycle_reviews'],'semantic_ready':False,'edge_denominator':graph['edge_denominator']},indent=2,sort_keys=True))
if __name__=='__main__':main()
