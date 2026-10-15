"""Semantic Primitive closure retains exact available counterparts and mutual semantic references."""
import json
import build_candidate as b
import dependencies as d


def main():
    paths = [b.UNIT / 'correspondence.json'] + [b.BASE / 'definitions' / identity / 'correspondence.json'
        for identity in ['cal.definition.axiom', 'cal.definition.definition', 'cal.definition.hypothesis', 'cal.definition.invariant', 'cal.definition.premise', 'cal.definition.schema']]
    packets = [json.loads(path.read_bytes()) for path in paths]
    selection = {'authority_effect': 'none', 'snapshot_ref': b.ref(b.BASE / 'current-snapshot.json'),
        'root_source': packets[0]['interpretation']['source'], 'packet_refs': [b.ref(path) for path in paths],
        'engine_ref': b.ref(b.IMPL / 'dependencies.py'), 'required_edges': None, 'cycle_policies': []}
    graph = d.compile_graph(b.snapshot(), [selection['root_source']], packets, live_root=b.ROOT)
    if (len(graph['nodes']), len(graph['edges']), len(graph['missing_or_quarantined_interpretations'])) != (29, 49, 22):
        raise ValueError('Wrong authored/transitive denominator: ' + json.dumps(graph))
    if graph['semantic_ready'] is not False or graph['edge_denominator'] != 'requires-independent-review':
        raise ValueError('Invented semantic closure or independently reviewed denominator')
    if len(graph['cycle_reviews']) != 2 or any(x['disposition'] != 'unresolved-cycle-classification' for x in graph['cycle_reviews']):
        raise ValueError('Two mutual-reference components require cycle review')
    expected = {frozenset(identity + '@1.0.0-candidate.1' for identity in group) for group in [['cal.definition.premise','cal.definition.axiom','cal.definition.hypothesis','cal.definition.invariant'],['cal.definition.schema','cal.definition.semantic-primitive']]}
    if {frozenset(x['members']) for x in graph['cycle_reviews']} != expected: raise ValueError('Wrong mutual-reference components')
    if '--write' in b.sys.argv:
        b.put('dependency-selection.json', selection); b.put('dependency-graph.json', graph)
    else:
        for name, value in [('dependency-selection.json', selection), ('dependency-graph.json', graph)]:
            if not b.r.same_json(json.loads((b.UNIT / name).read_bytes()), value): raise ValueError('Stale/substituted ' + name)
    for ref in [selection['snapshot_ref'], selection['engine_ref'], *selection['packet_refs']]:
        if b.ref(b.ROOT / ref['path']) != ref: raise ValueError('Closing dependency-input drift')
    print(json.dumps({'result': 'PASS-for-exact-authored-and-transitive-uses', 'nodes': len(graph['nodes']),
        'authored_direct_edges': 8, 'transitive_edges_from_available_counterparts': 41, 'total_edges': len(graph['edges']),
        'missing_dependency_packets': graph['missing_or_quarantined_interpretations'], 'semantic_ready': False,
        'edge_denominator': 'requires-independent-review', 'partial_counterpart_fidelity': 'pending',
        'cycle_reviews': graph['cycle_reviews']}, indent=2, sort_keys=True))


if __name__ == '__main__': main()
