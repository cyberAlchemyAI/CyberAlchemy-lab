"""Trace authored Governed Model uses through the available partial Definition counterpart."""
import json
import build_candidate as b
import dependencies as d


def main():
    packet = json.loads((b.UNIT / 'correspondence.json').read_bytes())
    counterpart_path = b.BASE / 'definitions/cal.definition.definition/correspondence.json'
    counterpart = json.loads(counterpart_path.read_bytes())
    snapshot = b.snapshot()
    selection = {'snapshot_ref': b.ref(b.BASE / 'current-snapshot.json'),
        'root_source': packet['interpretation']['source'],
        'packet_refs': [b.ref(b.UNIT / 'correspondence.json'), b.ref(counterpart_path)],
        'engine_ref': b.ref(b.IMPL / 'dependencies.py'),
        'required_edges': None, 'cycle_policies': [], 'authority_effect': 'none'}
    graph = d.compile_graph(snapshot, [selection['root_source']], [packet, counterpart], live_root=b.ROOT)
    if (len(graph['nodes']), len(graph['edges']), len(graph['missing_or_quarantined_interpretations'])) != (13, 13, 11):
        raise ValueError('Wrong authored/transitive closure: ' + json.dumps(graph))
    if graph['semantic_ready'] is not False or graph['edge_denominator'] != 'requires-independent-review':
        raise ValueError('Invented semantic readiness or edge denominator')
    if '--write' in b.sys.argv:
        b.put('dependency-selection.json', selection)
        b.put('dependency-graph.json', graph)
    else:
        for name, value in [('dependency-selection.json', selection), ('dependency-graph.json', graph)]:
            if not b.r.same_json(json.loads((b.UNIT / name).read_bytes()), value):
                raise ValueError('Substituted or stale ' + name)
    for reference in [selection['snapshot_ref'], selection['engine_ref'], *selection['packet_refs']]:
        if b.ref(b.ROOT / reference['path']) != reference:
            raise ValueError('Closing input drift')
    print(json.dumps({'result': 'PASS-for-exact-authored-and-transitive-uses',
        'nodes': 13, 'authored_direct_edges': 10, 'transitive_edges_from_Definition': 3,
        'total_edges': 13, 'missing_dependency_packets': graph['missing_or_quarantined_interpretations'],
        'semantic_ready': False, 'edge_denominator': 'requires-independent-review',
        'partial_counterpart_fidelity': 'pending'}, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
