"""Authored Invariant uses plus available partial Axiom and Definition counterpart traces."""
import json
import build_candidate as b
import dependencies as d


def main():
    paths = [b.UNIT / 'correspondence.json', b.BASE / 'definitions/cal.definition.axiom/correspondence.json',
             b.BASE / 'definitions/cal.definition.definition/correspondence.json']
    packets = [json.loads(path.read_bytes()) for path in paths]
    selection = {'authority_effect': 'none', 'snapshot_ref': b.ref(b.BASE / 'current-snapshot.json'),
        'root_source': packets[0]['interpretation']['source'], 'packet_refs': [b.ref(path) for path in paths],
        'engine_ref': b.ref(b.IMPL / 'dependencies.py'), 'required_edges': None, 'cycle_policies': []}
    graph = d.compile_graph(b.snapshot(), [selection['root_source']], packets, live_root=b.ROOT)
    if (len(graph['nodes']), len(graph['edges']), len(graph['missing_or_quarantined_interpretations'])) != (13, 15, 10):
        raise ValueError('Wrong authored/transitive denominator: ' + json.dumps(graph))
    if graph['semantic_ready'] is not False or graph['edge_denominator'] != 'requires-independent-review':
        raise ValueError('Invented closure or reviewed denominator')
    if len(graph['cycle_reviews']) != 1 or graph['cycle_reviews'][0]['disposition'] != 'unresolved-cycle-classification':
        raise ValueError('Mutual Axiom/Invariant references require explicit cycle review')
    if set(graph['cycle_reviews'][0]['members']) != {'cal.definition.invariant@1.0.0-candidate.1', 'cal.definition.axiom@1.0.0-candidate.1'}:
        raise ValueError('Wrong mutual-reference component')
    if '--write' in b.sys.argv:
        b.put('dependency-selection.json', selection); b.put('dependency-graph.json', graph)
    else:
        for name, value in [('dependency-selection.json', selection), ('dependency-graph.json', graph)]:
            if not b.r.same_json(json.loads((b.UNIT / name).read_bytes()), value): raise ValueError('Stale or substituted ' + name)
    for reference in [selection['snapshot_ref'], selection['engine_ref'], *selection['packet_refs']]:
        if b.ref(b.ROOT / reference['path']) != reference: raise ValueError('Closing input drift')
    print(json.dumps({'result': 'PASS-for-exact-authored-and-transitive-uses', 'nodes': 13,
        'authored_direct_edges': 8, 'transitive_edges_from_Axiom_and_Definition': 7, 'total_edges': 15,
        'missing_dependency_packets': graph['missing_or_quarantined_interpretations'],
        'semantic_ready': False, 'edge_denominator': 'requires-independent-review',
        'partial_counterpart_fidelity': 'pending', 'cycle_reviews': graph['cycle_reviews']}, indent=2, sort_keys=True))


if __name__ == '__main__': main()
