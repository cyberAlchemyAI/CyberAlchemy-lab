"""Source-bound public metadata graph, never protected Artifact qualification.

Original table occurrences are preserved, including repetitions and unresolved
members. Only explicitly selected document bodies are read. A table reference
does not supply permission to follow it or prove its current physical bytes.
"""
import ast
import hashlib
import json
from lab_contracts.codec import canonical, closed, need, parse, sha
from .anchors import legacy_json


ROLE_RULES = {
    'historical-proof': ('evidence', {'/files', '/complete_source_bindings',
        '/complete_profile_bindings', '/schema_execution_bindings'}),
    'historical-host-declaration': ('host-custody', {'/external_execution_dependency_bindings',
        '/host_native_binding', '/host_ABI_library_bindings', '/offline_environment_wheel_bindings'}),
    'historical-public-payload': ('evidence', {'/public_payload_file_bindings'}),
    'historical-protected-metadata': ('host-custody', {'/protected_dependencies'}),
    'current-source-declaration': ('execution', {'/files'}),
    'current-profile-declaration': ('execution', {'/files'}),
    'current-external-host-declaration': ('host-custody', {'/external_execution_dependency_bindings'}),
    'current-contribution-evidence': ('evidence', {'/final_contribution_bindings'}),
    'current-schema-execution': ('execution', {'/files'}),
}


def pointer(value, selector):
    need(type(selector) is str and selector.startswith('/'), 'PUBLIC_SELECTOR')
    for raw in selector[1:].split('/'):
        part = raw.replace('~1', '/').replace('~0', '~')
        need('~' not in raw.replace('~1', '').replace('~0', ''), 'PUBLIC_SELECTOR_ESCAPE')
        if type(value) is list:
            need(part.isdigit() and str(int(part)) == part and int(part) < len(value), 'PUBLIC_SELECTOR_INDEX')
            value = value[int(part)]
        else:
            need(type(value) is dict and part in value, 'PUBLIC_SELECTOR_MISSING')
            value = value[part]
    return value


def policy_inputs(policy):
    """Inventory only; caller must anchor policy bytes before trusting this list."""
    bindings = [policy['history_binding']]
    bindings.extend(p['binding'] for p in policy['provenance'])
    bindings.extend(d['binding'] for d in policy['documents'])
    unique = {}
    for b in bindings:
        key = b['root_id'], b['relative_path']
        need(key not in unique or unique[key] == b, 'PUBLIC_POLICY_BINDING_CONFLICT')
        unique[key] = b
    return list(unique.values())


def projection_digest(projection):
    """Bounded incremental encoding of a projection, not a new original identity."""
    h = hashlib.sha256()
    encoder = json.JSONEncoder(sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)
    for fragment in encoder.iterencode(projection):
        h.update(fragment.encode('utf-8'))
    return h.hexdigest()


def verify_subset_rows(source_rows, declared_rows):
    """Preserve the source protocol's complete row equality, not a digest join."""
    declared = {}
    for row in declared_rows:
        path = row['path']
        need(path not in declared or declared[path] == row, 'PUBLIC_CONFLICTING_DECLARED_PATH')
        declared[path] = row
    source = {}
    for row in source_rows:
        path = row['path']
        need(path not in source or source[path] == row, 'PUBLIC_CONFLICTING_SOURCE_PATH')
        source[path] = row
        need(declared.get(path) == row, 'PUBLIC_EXECUTION_OUTSIDE_PROFILE')


def build(reader, expected_policy_binding):
    policy = parse(reader.read(expected_policy_binding), 1024 * 1024)
    closed(policy, ('schema_version', 'history_binding', 'provenance', 'documents', 'tables',
                   'joins', 'subset_constraints', 'semantic_search', 'expected_counts',
                   'authority_effect', 'claim_ceiling'))
    need(policy['schema_version'] == 'lab-completion-public-source-role-policy/v1'
         and policy['authority_effect'] == 'none', 'PUBLIC_POLICY_VERSION')
    cache = {}

    def read(b):
        key = canonical(b)
        if key not in cache:
            cache[key] = reader.read(b)
        return cache[key]

    history = legacy_json(read(policy['history_binding']))
    need(len(history['tables']) == 17 and sum(r['occurrences'] for r in history['tables']) == 172533,
         'PUBLIC_ORIGINAL_HISTORY_CLOSURE')
    provenance_ids = set()
    for source in policy['provenance']:
        closed(source, ('id', 'binding', 'selector', 'role'))
        need(source['id'] not in provenance_ids, 'PUBLIC_PROVENANCE_DUPLICATE')
        provenance_ids.add(source['id'])
        raw = read(source['binding'])
        if source['selector'].startswith('python:'):
            names = source['selector'][7:].split('.')
            body = ast.parse(raw).body
            for name in names:
                matches = [n for n in body if isinstance(n, (ast.ClassDef, ast.FunctionDef)) and n.name == name]
                need(len(matches) == 1, 'PUBLIC_PROVENANCE_SYMBOL')
                body = matches[0].body
        elif source['selector'].startswith('text:'):
            need(source['selector'][5:] in raw.decode('utf-8'), 'PUBLIC_PROVENANCE_TEXT')
        else:
            pointer(legacy_json(raw), source['selector'])
    documents = {}
    document_specs = {}
    for d in policy['documents']:
        closed(d, ('id', 'binding', 'schema_selector', 'schema_identity', 'scope'))
        need(d['id'] not in documents, 'PUBLIC_DOCUMENT_DUPLICATE')
        value = legacy_json(read(d['binding']))
        need(pointer(value, d['schema_selector']) == d['schema_identity'], 'PUBLIC_DOCUMENT_SCHEMA')
        need(d['scope'] in ('historical-metadata', 'current-metadata', 'public-schema'), 'PUBLIC_DOCUMENT_SCOPE')
        documents[d['id']], document_specs[d['id']] = value, d
    tables, occurrence_nodes, occurrence_edges = [], [], []
    seen = set()
    historical = []
    kind_counts = {'semantic': 0, 'execution': 0, 'evidence': 0, 'host-custody': 0}
    for t in policy['tables']:
        closed(t, ('id', 'document_id', 'selector', 'row_count', 'role', 'kind', 'provenance_ids'))
        need(t['id'] not in seen and t['document_id'] in documents, 'PUBLIC_TABLE_IDENTITY')
        seen.add(t['id'])
        need(t['role'] in ROLE_RULES, 'PUBLIC_TABLE_ROLE')
        kind, selectors = ROLE_RULES[t['role']]
        need(t['kind'] == kind and t['selector'] in selectors, 'PUBLIC_TABLE_ROLE_KIND')
        need(t['provenance_ids'] and set(t['provenance_ids']) <= provenance_ids, 'PUBLIC_TABLE_PROVENANCE')
        spec = document_specs[t['document_id']]
        is_history = t['role'].startswith('historical-')
        need(spec['scope'] == ('historical-metadata' if is_history else 'current-metadata'), 'PUBLIC_TABLE_SCOPE')
        rows = pointer(documents[t['document_id']], t['selector'])
        if t['selector'] == '/host_native_binding':
            rows = [rows]
        need(type(rows) is list and all(type(r) is dict for r in rows)
             and type(t['row_count']) is int and len(rows) == t['row_count'], 'PUBLIC_TABLE_CARDINALITY')
        if t['role'] == 'historical-protected-metadata':
            need(all(r.get('public_body_export_allowed') is False for r in rows), 'PUBLIC_PROTECTED_EXPORT')
        if is_history:
            historical.append({'document': spec['binding']['relative_path'],
                               'row_selector': t['selector'], 'occurrences': len(rows)})
            need(history['document_pins'].get(spec['binding']['relative_path']) == spec['binding']['sha256'],
                 'PUBLIC_HISTORY_DOCUMENT_PIN')
        tables.append({**t, 'document_binding': spec['binding'], 'rows': rows})
        for index, row in enumerate(rows):
            need(type(row.get('path')) is str and type(row.get('sha256')) is str
                 and len(row['sha256']) == 64 and all(c in '0123456789abcdef' for c in row['sha256']),
                 'PUBLIC_ORIGINAL_REFERENCE_SHAPE')
            node_id = f"{t['id']}:{index}"
            original_selector = t['selector'] if t['selector'] == '/host_native_binding' else f"{t['selector']}/{index}"
            occurrence_nodes.append({'id': node_id, 'table_id': t['id'], 'row_index': index,
                                     'original_selector': original_selector, 'kind': kind,
                                     'member_status': 'metadata-retained-body-unverified'})
            occurrence_edges.append({'from': t['document_id'], 'to': node_id,
                                     'kind': kind, 'role': t['role']})
            kind_counts[kind] += 1
    need(historical == history['tables'], 'PUBLIC_HISTORY_ORDER_OR_OMISSION')
    current_roles = [t['role'] for t in tables if not t['role'].startswith('historical-')]
    need(len(current_roles) == 5 and set(current_roles) ==
         {role for role in ROLE_RULES if role.startswith('current-')},
         'PUBLIC_CURRENT_TABLE_CLOSURE')
    actual = {'historical_tables': len(historical), 'historical_occurrences': 172533,
              'all_tables': len(tables), 'all_occurrences': len(occurrence_nodes)}
    need(actual == policy['expected_counts'], 'PUBLIC_COMPLETE_ACCOUNTING')
    by_table = {t['id']: t for t in tables}
    for constraint in policy['subset_constraints']:
        closed(constraint, ('source_table', 'declared_table'))
        source, target = by_table[constraint['source_table']], by_table[constraint['declared_table']]
        verify_subset_rows(source['rows'], target['rows'])
    verified_joins = []
    for join in policy['joins']:
        closed(join, ('from', 'selector', 'to', 'kind', 'role', 'provenance_ids'))
        need(join['from'] in documents and join['to'] in documents
             and join['kind'] in ('execution', 'evidence'), 'PUBLIC_JOIN_SCOPE')
        need(set(join['provenance_ids']) <= provenance_ids and join['provenance_ids'], 'PUBLIC_JOIN_PROVENANCE')
        target = document_specs[join['to']]['binding']
        need(pointer(documents[join['from']], join['selector']) ==
             {'path': target['relative_path'], 'sha256': target['sha256']}, 'PUBLIC_DECLARED_JOIN')
        verified_joins.append(join)
    semantic = policy['semantic_search']
    closed(semantic, ('schema_document_id', 'public_payload_table', 'declaration_selectors',
                     'selected_instance_bindings', 'disposition', 'reason'))
    need(semantic['selected_instance_bindings'] == [] and semantic['disposition'] == 'unresolved-gated',
         'PUBLIC_SEMANTIC_INSTANCE_UNSELECTED')
    schema_id = semantic['schema_document_id']
    schema = documents[schema_id]
    schema_binding = document_specs[schema_id]['binding']
    payload = by_table[semantic['public_payload_table']]['rows']
    need(any(r['path'] == schema_binding['relative_path'] and r['sha256'] == schema_binding['sha256']
             and r['size_bytes'] == schema_binding['size_bytes'] for r in payload), 'PUBLIC_SCHEMA_EXPORT_SELECTION')
    declarations = [{'selector': s, 'original': pointer(schema, s)} for s in semantic['declaration_selectors']]
    # Internal JSON Schema references are execution/schema links. They never
    # become claims about an instantiated Artifact's authority or semantic edge.
    schema_links = []
    def refs(value, path=''):
        if type(value) is dict:
            for key, child in value.items():
                at = path + '/' + key.replace('~', '~0').replace('/', '~1')
                if key == '$ref':
                    need(type(child) is str and child.startswith('#/'), 'PUBLIC_SCHEMA_EXTERNAL_REF_UNSELECTED')
                    pointer(schema, child[1:])
                    schema_links.append({'from': schema_id, 'source_selector': at,
                                         'to': schema_id, 'target_selector': child[1:],
                                         'kind': 'execution', 'role': 'json-schema-reference'})
                else:
                    refs(child, at)
        elif type(value) is list:
            for index, child in enumerate(value):
                refs(child, path + '/' + str(index))
    refs(schema)
    return {'schema_version': 'lab-completion-public-source-projection/v1',
            'policy_binding': expected_policy_binding, 'documents': policy['documents'],
            'tables': tables, 'graph': {'occurrence_nodes': occurrence_nodes,
            'occurrence_edges': occurrence_edges, 'verified_document_joins': verified_joins,
            'verified_schema_links': schema_links, 'semantic_artifact_edges': []},
            'counts': actual, 'occurrence_kind_counts': kind_counts,
            'semantic_resolution': {**semantic, 'verified_schema_declarations': declarations},
            'member_byte_resolution': {'status': 'unresolved-gated', 'members_read': 0,
                'reason': 'Reference metadata does not authorize member reads or verify current bytes, ABI, custody or semantic authority.'},
            'read_bindings': policy_inputs(policy), 'authority_effect': 'none',
            'runtime_eligible': False, 'claim_ceiling': policy['claim_ceiling']}
