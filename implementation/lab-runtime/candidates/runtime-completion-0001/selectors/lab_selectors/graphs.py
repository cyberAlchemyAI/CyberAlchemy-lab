"""Four explicit edge kinds. Historical proof occurrences are not graph edges."""
from lab_contracts.codec import closed, need, canonical, sha, parse

KINDS = frozenset(('semantic', 'execution', 'evidence', 'host-custody'))


def validate_graph(value, expected_rows, *, policy_raw, expected_policy_sha256):
    # This digest comes from a separately selected schema-role policy, never
    # from the proposed graph. The policy binds exact original body selectors,
    # node roles, edge endpoints/kinds and row provenance. Unknown roles refuse.
    need(sha(policy_raw) == expected_policy_sha256, 'EDGE_POLICY_ANCHOR')
    policy = parse(policy_raw, 64 * 1024 * 1024)
    closed(policy, ('schema_version', 'nodes', 'edges', 'roots', 'original_rows_sha256', 'acyclic_kinds'))
    need(policy['schema_version'] == 'lab-completion-edge-policy/v1'
         and policy['original_rows_sha256'] == sha(canonical(expected_rows)), 'EDGE_POLICY_SOURCE')
    need(type(policy['acyclic_kinds']) is list and len(policy['acyclic_kinds']) == len(set(policy['acyclic_kinds']))
         and 'semantic' in policy['acyclic_kinds'] and set(policy['acyclic_kinds']) <= KINDS - {'evidence'},
         'EDGE_CYCLE_POLICY')
    closed(value, ('schema_version', 'nodes', 'edges', 'roots', 'original_rows'))
    need(value['schema_version'] == 'lab-completion-typed-graph/v1', 'GRAPH_VERSION')
    need(value['original_rows'] == expected_rows, 'ORIGINAL_ROWS_CHANGED')
    ids = []
    for node in value['nodes']:
        closed(node, ('id', 'kind', 'original_binding', 'selector'))
        need(type(node['id']) is str and node['id'] and node['kind'] in KINDS, 'NODE_KIND')
        need(type(node['selector']) is str and node['selector'], 'NODE_SELECTOR')
        from lab_contracts.validation import validate
        validate('ByteBinding', node['original_binding'])
        ids.append(node['id'])
    need(len(ids) == len(set(ids)), 'DUPLICATE_NODE')
    nodes = set(ids)
    edges = set()
    adjacency = {n: [] for n in ids}
    for row in value['edges']:
        closed(row, ('from', 'to', 'kind', 'original_row'))
        need(row['kind'] in KINDS and row['from'] in nodes and row['to'] in nodes, 'EDGE_KIND_ENDPOINT')
        need(type(row['original_row']) is int and 0 <= row['original_row'] < len(expected_rows), 'EDGE_PROVENANCE')
        edge = (row['from'], row['to'], row['kind'], row['original_row'])
        need(edge not in edges, 'DUPLICATE_EDGE')
        edges.add(edge)
        adjacency[row['from']].append(row['to'])
    need(type(value['roots']) is list and value['roots'] and
         len(value['roots']) == len(set(value['roots'])) and set(value['roots']) <= nodes, 'GRAPH_ROOTS')
    need(value['nodes'] == policy['nodes'] and value['edges'] == policy['edges']
         and value['roots'] == policy['roots'], 'SCHEMA_ROLE_POLICY_DIFFERS')
    # Reachability includes all declared reference kinds; only explicitly
    # declared dependency graphs undergo their own cycle check. Evidence
    # backreferences cannot accidentally become Artifact dependencies.
    reached = set()
    pending = list(value['roots'])
    while pending:
        node = pending.pop()
        if node not in reached:
            reached.add(node)
            pending.extend(adjacency[node])
    need(reached == nodes, 'DISCONNECTED_GRAPH')
    for kind in policy['acyclic_kinds']:
        subset = {n: [] for n in ids}
        for edge in value['edges']:
            if edge['kind'] == kind:
                subset[edge['from']].append(edge['to'])
        colors = {n: 0 for n in ids}
        stack = [(n, False) for n in ids]
        while stack:
            node, leaving = stack.pop()
            if leaving:
                colors[node] = 2
                continue
            need(colors[node] != 1, 'GRAPH_CYCLE')
            if colors[node] == 2:
                continue
            colors[node] = 1
            stack.append((node, True))
            stack.extend((child, False) for child in reversed(subset[node]))
    return {'nodes': len(ids), 'edges': len(edges), 'original_rows': len(expected_rows),
            'kinds': sorted({e[2] for e in edges}), 'authority_effect': 'none'}


def classify_rows(tables, dispositions, expected_dispositions):
    """One disposition per occurrence; repeated identities remain separate rows."""
    result = []
    need(dispositions == expected_dispositions, 'INDEPENDENT_DISPOSITIONS')
    expected = set()
    for table_index, table in enumerate(tables):
        for row_index, row in enumerate(table['rows']):
            key = (table_index, row_index)
            expected.add(key)
            need(key in dispositions and dispositions[key] in KINDS, 'MISSING_ROW_DISPOSITION')
            result.append({'table_index': table_index, 'row_index': row_index,
                           'kind': dispositions[key], 'row': row})
    need(set(dispositions) == expected, 'EXTRA_ROW_DISPOSITION')
    return result
