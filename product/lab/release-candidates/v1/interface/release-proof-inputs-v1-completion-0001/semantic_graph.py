"""Independently selected schema/role graph, not a traversal of naked hashes."""
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from .protected_inputs import (Refusal, need, closed, parse, digest, ProtectedReader)

def pointer(value, path):
    need(type(path) is str and (path == '' or path.startswith('/')), 'JSON pointer required')
    for part in path.split('/')[1:]:
        part = part.replace('~1', '/').replace('~0', '~')
        try: value = value[int(part)] if type(value) is list else value[part]
        except (KeyError, IndexError, ValueError, TypeError) as exc:
            raise Refusal('declared selector unresolved: ' + path) from exc
    return value

def reference_slots(schema, prefix=''):
    """Coverage only: name does not decide whether a slot is a graph edge.

    Independently selected field dispositions decide edges. This rejects missing
    classifications for actual declared reference slots, including payload fields.
    Nested relation_refs are covered by original descriptor relation_roles.
    """
    result = set()
    for key, child in schema.get('properties', {}).items():
        path = prefix + '/' + key.replace('~', '~0').replace('/', '~1')
        if key.endswith(('_ref', '_refs')):
            if key != 'relation_refs': result.add(path)
        elif child.get('type') == 'object':
            result.update(reference_slots(child, path))
    return result

def expected_schema_pointer(path):
    result = ''
    for part in path.split('/')[1:]: result += '/properties/' + part
    return result

def refs(value, schema):
    if schema.get('type') == 'string':
        need(type(value) is str, 'declared string reference required'); return [value]
    need(schema.get('type') == 'array' and schema.get('items', {}).get('type') == 'string'
         and type(value) is list and all(type(x) is str for x in value),
         'unsupported reference slot schema')
    return value

def verify_graph(reader, policy_file_id, declared_edges, root_refs):
    need(type(reader) is ProtectedReader, 'actual protected reader required')
    # Original integration must additionally repeat its own current source/Actor
    # guards. This module never overrides them or infers admission from validity.
    with reader.boundary():
        policy_raw = reader.read(policy_file_id, 'semantic-policy')
        policy = parse(policy_raw)
        closed(policy, ('schema_version', 'profiles', 'node_file_ids',
                       'proof_references', 'context_references', 'authority_effect'), 'graph policy')
        need(policy['schema_version'] == 'lab-schema-declared-semantic-graph/v1-candidate'
             and policy['authority_effect'] == 'none', 'graph version/effect differs')
        ids = policy['node_file_ids']
        need(type(ids) is list and ids and len(ids) == len(set(ids)), 'unique complete node selection required')
        need(set(ids) == {i for i, row in reader.files.items() if row['kind'] == 'governed-record'},
             'governed record node omitted or kind spoofed')
        profiles = {}; docs = {}; descriptors = {}
        for profile in policy['profiles']:
            closed(profile, ('kind', 'schema_file_id', 'descriptor_file_id', 'fields'), 'carrier profile')
            kind = profile['kind']; need(kind not in profiles, 'duplicate carrier profile')
            raw = reader.read(profile['schema_file_id'], 'governed-schema'); schema = parse(raw)
            descriptor = parse(reader.read(profile['descriptor_file_id'], 'governed-descriptor'))
            need(descriptor.get('schema_digest') == digest(raw)
                 and descriptor.get('classification', {}).get('semantic_kind') == kind
                 and schema.get('properties', {}).get('kind', {}).get('const') == kind,
                 'actual carrier schema/descriptor/kind binding differs')
            need(descriptor.get('instance_contract', {}).get('identity_field') == 'node_id',
                 'unsupported original identity selector; explicit successor profile required')
            roles = descriptor.get('relation_roles')
            need(type(roles) is list and roles and schema['properties']['relation_refs']['type'] == 'array',
                 'actual declared relation role contract required')
            for role in roles:
                closed(role, ('relation_kind_ref', 'direction', 'counterpart_kinds'), 'original role')
            fields = profile['fields']
            need(type(fields) is list and len({f['instance_pointer'] for f in fields}) == len(fields),
                 'duplicate reference classification')
            need({f['instance_pointer'] for f in fields} == reference_slots(schema),
                 'declared reference slot omitted/added')
            for f in fields:
                closed(f, ('instance_pointer', 'schema_pointer', 'disposition'), 'reference field')
                need(f['schema_pointer'] == expected_schema_pointer(f['instance_pointer']) and
                     f['disposition'] in ('semantic-node', 'verified-proof', 'current-context', 'self-identity'),
                     'undeclared schema selector/disposition')
                slot = pointer(schema, f['schema_pointer'])
                need(slot.get('type') == 'string' or
                     (slot.get('type') == 'array' and slot.get('items', {}).get('type') == 'string'),
                     'unsupported declared reference shape')
            profiles[kind] = profile; docs[kind] = schema; descriptors[kind] = descriptor
        registry = Registry()
        for schema in docs.values():
            need(type(schema.get('$id')) is str, 'independently identified original schema required')
            registry = registry.with_resource(schema['$id'], Resource.from_contents(schema))
        proof = {}
        for row in policy['proof_references']:
            closed(row, ('reference', 'file_id'), 'proof reference')
            need(row['reference'] not in proof and row['file_id'] in reader.files and
                 reader.files[row['file_id']]['kind'] != 'governed-record',
                 'proof reference duplicate/kind spoof')
            reader.read(row['file_id']); proof[row['reference']] = row['file_id']
        contexts = policy['context_references']
        need(type(contexts) is list and all(type(x) is str for x in contexts)
             and len(contexts) == len(set(contexts)), 'closed current context reference set required')
        nodes = {}
        for file_id in ids:
            record = parse(reader.read(file_id, 'governed-record'))
            kind = record.get('kind'); need(kind in profiles, 'unselected carrier profile')
            try:
                Draft202012Validator(docs[kind], registry=registry).validate(record)
            except Exception as exc:
                raise Refusal('actual original record schema refused') from exc
            identity = record['node_id']; need(identity not in nodes, 'duplicate semantic node identity')
            nodes[identity] = record
        need(type(root_refs) is list and root_refs and len(root_refs) == len(set(root_refs))
             and set(root_refs) <= set(nodes), 'unique selected graph roots required')
        actual = set()
        for identity, record in nodes.items():
            for relation in record['relation_refs']:
                matches = [role for role in descriptors[record['kind']]['relation_roles']
                    if role['relation_kind_ref'] == relation['relation_kind_ref'] and
                    role['direction'] == relation['direction'] and
                    relation['counterpart_kind'] in role['counterpart_kinds']]
                need(len(matches) == 1, 'original declared pair/direction differs')
                other = relation['counterpart_ref']
                need(other in nodes and nodes[other]['kind'] == relation['counterpart_kind'],
                     'semantic endpoint absent/wrong kind')
                edge = (identity, other) if relation['direction'] == 'source' else (other, identity)
                actual.add(edge)
            for f in profiles[record['kind']]['fields']:
                for ref in refs(pointer(record, f['instance_pointer']),
                                pointer(docs[record['kind']], f['schema_pointer'])):
                    disposition = f['disposition']
                    if disposition == 'semantic-node':
                        need(ref in nodes, 'schema-declared semantic dependency omitted')
                        actual.add((identity, ref))
                    elif disposition == 'verified-proof':
                        need(ref in proof, 'exact proof reference omitted')
                    elif disposition == 'current-context':
                        need(ref in contexts, 'current-context reference omitted')
                    else:
                        need(ref == identity or ref.startswith(identity + '@'), 'self identity differs')
        need(type(declared_edges) is list, 'explicit declared graph edges required')
        declared = []
        for row in declared_edges:
            closed(row, ('source', 'dependency'), 'semantic edge')
            need(row['source'] in nodes and row['dependency'] in nodes, 'declared edge outside selected nodes')
            declared.append((row['source'], row['dependency']))
        need(len(declared) == len(set(declared)) and set(declared) == actual,
             'declared semantic edges duplicate/omitted/substituted')
        active = set(); done = set(); adjacency = {key: [] for key in nodes}
        for left, right in actual: adjacency[left].append(right)
        def visit(key):
            need(key not in active, 'actual semantic dependency cycle')
            if key in done: return
            active.add(key)
            for child in adjacency[key]: visit(child)
            active.remove(key); done.add(key)
        for key in nodes: visit(key)
        result = {'policy_sha256': digest(policy_raw), 'nodes': len(nodes), 'edges': len(actual),
                  'proof_references': len(proof), 'schema_and_declared_roles_verified': True,
                  'authority_effect': 'none', 'admission_or_owner_authority': False}
    return result
