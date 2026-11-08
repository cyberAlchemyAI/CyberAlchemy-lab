"""Retain whole original tables as metadata, without reading their members."""
from lab_contracts.codec import closed, need, sha
from .anchors import legacy_json


def table(reader, document_binding, selector):
    need(type(selector) is str and selector.startswith('/') and selector.count('/') == 1,
         'TABLE_SELECTOR')
    document = legacy_json(reader.read(document_binding))
    need(type(document) is dict and selector[1:] in document, 'TABLE_MISSING')
    rows = document[selector[1:]]
    if selector == '/host_native_binding':
        rows = [rows]
    need(type(rows) is list and all(type(r) is dict for r in rows), 'TABLE_ROWS')
    # Intentionally do not open any path referenced by these rows.
    return {'document_binding': document_binding, 'selector': selector, 'rows': rows}


def retain(reader, descriptors, expected_descriptors):
    need(descriptors == expected_descriptors, 'INDEPENDENT_TABLE_SELECTION')
    keys = []
    tables = []
    for d in descriptors:
        closed(d, ('document_binding', 'selector', 'row_count', 'classification'))
        need(d['classification'] in ('original-proof-metadata', 'current-execution-metadata',
             'public-payload-metadata', 'protected-dependency-metadata'), 'TABLE_CLASSIFICATION')
        key = (d['document_binding']['sha256'], d['selector'])
        need(key not in keys, 'DUPLICATE_TABLE')
        keys.append(key)
        t = table(reader, d['document_binding'], d['selector'])
        need(type(d['row_count']) is int and len(t['rows']) == d['row_count'], 'TABLE_CARDINALITY')
        if d['classification'] == 'protected-dependency-metadata':
            need(all(r.get('public_body_export_allowed') is False for r in t['rows']),
                 'PROTECTED_EXPORT_COERCION')
        tables.append({**t, 'classification': d['classification']})
    return {'schema_version': 'lab-completion-original-table-inventory/v1',
            'tables': tables, 'occurrences': sum(len(t['rows']) for t in tables),
            'member_bodies_read': 0, 'authority_effect': 'none'}


def compare(original, retained):
    need(original == retained, 'ORDERED_ORIGINAL_TABLE_DRIFT')
    return sum(len(t['rows']) for t in original['tables'])
