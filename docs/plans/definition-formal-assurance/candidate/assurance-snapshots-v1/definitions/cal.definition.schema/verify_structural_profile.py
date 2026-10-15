"""Finite structural inspection examples: no subject execution or population effects."""
import copy
import json
import build_candidate as b
import verifier as v


class ProfileFault(ValueError):
    def __init__(self, code): self.code = code; super().__init__(code)
def exact(value, keys, code):
    if not isinstance(value, dict) or set(value) != set(keys): raise ProfileFault(code)
def name(value):
    if not isinstance(value, str) or not value: raise ProfileFault('invalid-name')
def rows(value, limit, code):
    if not isinstance(value, list) or len(value) > limit: raise ProfileFault(code)
def path_signature(path, relations):
    rows(path, 8, 'invalid-path')
    if not path or any(r not in relations for r in path): raise ProfileFault('invalid-path')
    first = relations[path[0]]; end = first['target_kind']
    for relation in path[1:]:
        row = relations[relation]
        if row['source_kind'] != end: raise ProfileFault('ill-typed-path')
        end = row['target_kind']
    return first['source_kind'], end
def decode_profile(profile):
    b.c.bounded_tree(profile); exact(profile, ['profile', 'schema_level', 'subject_level', 'kinds', 'relations', 'connection_rules'], 'malformed-profile')
    if profile['profile'] != 'candidate:finite-structure-inspection/v1': raise ProfileFault('unsupported-profile')
    name(profile['schema_level']); name(profile['subject_level'])
    if profile['schema_level'] == profile['subject_level']: raise ProfileFault('same-relative-level')
    kinds, relations = {}, {}
    rows(profile['kinds'], 8, 'kind-limit'); rows(profile['relations'], 8, 'relation-limit'); rows(profile['connection_rules'], 8, 'rule-limit')
    for kind in profile['kinds']:
        exact(kind, ['id', 'constraints'], 'malformed-kind'); name(kind['id'])
        if kind['id'] in kinds: raise ProfileFault('duplicate-kind')
        rows(kind['constraints'], 8, 'constraint-limit'); kinds[kind['id']] = kind
        for constraint in kind['constraints']:
            if not isinstance(constraint, dict): raise ProfileFault('malformed-constraint')
            op = constraint.get('op')
            if op == 'field-type':
                exact(constraint, ['op', 'field', 'type'], 'malformed-constraint')
                if constraint['type'] not in ['integer', 'string', 'boolean']: raise ProfileFault('unsupported-field-type')
            elif op == 'integer-min':
                exact(constraint, ['op', 'field', 'minimum'], 'malformed-constraint')
                if type(constraint['minimum']) is not int: raise ProfileFault('invalid-integer-minimum')
            else: raise ProfileFault('unsupported-local-operator')
            name(constraint['field'])
    for relation in profile['relations']:
        exact(relation, ['id', 'source_kind', 'target_kind'], 'malformed-relation'); name(relation['id'])
        if relation['id'] in relations: raise ProfileFault('duplicate-relation')
        if relation['source_kind'] not in kinds or relation['target_kind'] not in kinds: raise ProfileFault('undeclared-endpoint-kind')
        relations[relation['id']] = relation
    for rule in profile['connection_rules']:
        if not isinstance(rule, dict): raise ProfileFault('malformed-rule')
        op = rule.get('op')
        if op == 'endpoint-type': exact(rule, ['op', 'relation'], 'malformed-rule')
        elif op == 'multiplicity':
            exact(rule, ['op', 'relation', 'at', 'minimum', 'maximum'], 'malformed-rule')
            if rule['at'] not in ['source', 'target'] or type(rule['minimum']) is not int or type(rule['maximum']) is not int or not 0 <= rule['minimum'] <= rule['maximum'] <= 8:
                raise ProfileFault('invalid-multiplicity')
        elif op == 'path-equality':
            exact(rule, ['op', 'left', 'right'], 'malformed-rule')
            if path_signature(rule['left'], relations) != path_signature(rule['right'], relations): raise ProfileFault('ill-typed-path-equation')
        else: raise ProfileFault('unsupported-connection-operator')
        if op != 'path-equality' and rule['relation'] not in relations: raise ProfileFault('undeclared-rule-relation')
    return kinds, relations
def compose_path(path, tables):
    pairs = set(tables[path[0]])
    for relation in path[1:]: pairs = {(a, z) for a, middle in pairs for left, z in tables[relation] if middle == left}
    return pairs
def inspect(profile, subject):
    kinds, relations = decode_profile(profile); b.c.bounded_tree(subject)
    exact(subject, ['level', 'nodes', 'edges'], 'malformed-subject'); name(subject['level'])
    rows(subject['nodes'], 8, 'node-limit'); rows(subject['edges'], 64, 'edge-limit')
    nodes, local_results, connection_results = {}, [], []
    for node in subject['nodes']:
        exact(node, ['id', 'kind', 'fields'], 'malformed-node'); name(node['id'])
        if node['id'] in nodes: raise ProfileFault('duplicate-node')
        if node['kind'] not in kinds or not isinstance(node['fields'], dict): raise ProfileFault('unknown-kind-or-malformed-fields')
        nodes[node['id']] = node
        for constraint in kinds[node['kind']]['constraints']:
            field = constraint['field']; value = node['fields'].get(field)
            if constraint['op'] == 'field-type':
                kind = {'integer': int, 'string': str, 'boolean': bool}[constraint['type']]
                truth = field in node['fields'] and type(value) is kind
            else: truth = field in node['fields'] and type(value) is int and value >= constraint['minimum']
            local_results.append({'node': node['id'], 'constraint': constraint, 'pass': truth})
    tables = {r: set() for r in relations}
    for edge in subject['edges']:
        exact(edge, ['relation', 'source', 'target'], 'malformed-edge')
        if edge['relation'] not in relations or edge['source'] not in nodes or edge['target'] not in nodes: raise ProfileFault('undeclared-relation-or-dangling-edge')
        pair = (edge['source'], edge['target']); table = tables[edge['relation']]
        if pair in table: raise ProfileFault('duplicate-edge')
        table.add(pair); signature = relations[edge['relation']]
        connection_results.append({'check': 'declared-endpoint-typing', 'edge': edge,
            'pass': nodes[pair[0]]['kind'] == signature['source_kind'] and nodes[pair[1]]['kind'] == signature['target_kind']})
    for rule in profile['connection_rules']:
        op = rule['op']
        if op == 'path-equality': truth = compose_path(rule['left'], tables) == compose_path(rule['right'], tables)
        elif op == 'endpoint-type':
            relation = relations[rule['relation']]
            truth = all(nodes[a]['kind'] == relation['source_kind'] and nodes[z]['kind'] == relation['target_kind'] for a, z in tables[rule['relation']])
        else:
            relation = relations[rule['relation']]; source = rule['at'] == 'source'; position = 0 if source else 1
            selected_kind = relation['source_kind' if source else 'target_kind']
            truth = all(rule['minimum'] <= sum(pair[position] == identity for pair in tables[rule['relation']]) <= rule['maximum']
                for identity, node in nodes.items() if node['kind'] == selected_kind)
        connection_results.append({'check': op, 'rule': rule, 'pass': truth})
    C = all(x['pass'] for x in local_results); N = all(x['pass'] for x in connection_results); level = subject['level'] == profile['subject_level']
    return {'local_constraints_pass': C, 'connection_rules_pass': N, 'level_matches': level, 'conforms': C and N and level,
        'local_results': local_results, 'connection_results': connection_results, 'occupants_supplied': len(nodes), 'edges_supplied': len(subject['edges']),
        'subject_executed': False, 'occupants_added': 0, 'authority_effect': 'none'}
def base_profile():
    return {'profile': 'candidate:finite-structure-inspection/v1', 'schema_level': 'meta', 'subject_level': 'data',
        'kinds': [{'id': k, 'constraints': [{'op': 'field-type', 'field': 'value', 'type': 'integer'}, {'op': 'integer-min', 'field': 'value', 'minimum': 0}]} for k in ['A', 'B']],
        'relations': [{'id': 'r', 'source_kind': 'A', 'target_kind': 'B'}],
        'connection_rules': [{'op': 'endpoint-type', 'relation': 'r'}, {'op': 'multiplicity', 'relation': 'r', 'at': 'source', 'minimum': 1, 'maximum': 1}]}
def base_subject():
    return {'level': 'data', 'nodes': [{'id': 'a', 'kind': 'A', 'fields': {'value': 0}}, {'id': 'b', 'kind': 'B', 'fields': {'value': 0}}],
        'edges': [{'relation': 'r', 'source': 'a', 'target': 'b'}]}
def controls():
    rows = []
    def add(name, change, C=True, N=True, error=None, level=True):
        profile, subject = base_profile(), base_subject(); change(profile, subject)
        rows.append({'case_id': name, 'profile': profile, 'subject': subject, 'expected_C': C, 'expected_N': N, 'expected_level': level, 'expected_error': error})
    for C, N in [(False, False), (False, True), (True, False), (True, True)]:
        def vary(p, s, C=C, N=N):
            if not C: s['nodes'][0]['fields']['value'] = -1
            if not N: s['edges'] = []
        add('independent-C-' + str(C).lower() + '-N-' + str(N).lower(), vary, C=C, N=N)
    add('Boolean-is-not-an-integer-occupant-value', lambda p, s: s['nodes'][0]['fields'].update(value=True), C=False)
    add('endpoint-kind-mismatch', lambda p, s: s['edges'][0].update(source='b', target='a'), N=False)
    def no_C(p, s):
        for kind in p['kinds']: kind['constraints'] = []
        for node in s['nodes']: node['fields'] = {}
    add('connection-rules-with-no-local-constraints', no_C)
    def no_N(p, s): p.update(relations=[], connection_rules=[]); s['edges'] = []
    add('local-constraints-with-no-relations-or-connection-rules', no_N)
    add('empty-supplied-graph-passes-vacuously-without-populating-it', lambda p, s: s.update(nodes=[], edges=[]))
    add('wrong-declared-subject-level', lambda p, s: s.update(level='other'), level=False)
    def path(p, s, equal=True):
        p['kinds'].append({'id': 'C', 'constraints': []})
        p['relations'] = [{'id': 'f', 'source_kind': 'A', 'target_kind': 'B'}, {'id': 'g', 'source_kind': 'B', 'target_kind': 'C'}, {'id': 'h', 'source_kind': 'A', 'target_kind': 'C'}]
        p['connection_rules'] = [{'op': 'path-equality', 'left': ['f', 'g'], 'right': ['h']}]
        s['nodes'].append({'id': 'c', 'kind': 'C', 'fields': {}})
        s['edges'] = [{'relation': 'f', 'source': 'a', 'target': 'b'}, {'relation': 'g', 'source': 'b', 'target': 'c'}]
        if equal: s['edges'].append({'relation': 'h', 'source': 'a', 'target': 'c'})
    add('composite-paths-agree', path)
    add('composite-paths-disagree', lambda p, s: path(p, s, False), N=False)
    add('unsupported-local-operation-rejected', lambda p, s: p['kinds'][0]['constraints'][0].update(op='execute-subject'), error='unsupported-local-operator')
    def bad_path(p, s): path(p, s); p['connection_rules'][0]['right'] = ['f']
    add('ill-typed-path-equation-rejected', bad_path, error='ill-typed-path-equation')
    add('duplicate-kind-rejected', lambda p, s: p['kinds'].append(copy.deepcopy(p['kinds'][0])), error='duplicate-kind')
    add('dangling-edge-rejected', lambda p, s: s['edges'][0].update(target='absent'), error='undeclared-relation-or-dangling-edge')
    add('duplicate-edge-rejected', lambda p, s: s['edges'].append(copy.deepcopy(s['edges'][0])), error='duplicate-edge')
    def string_content(p, s):
        p['kinds'] = [{'id': 'A', 'constraints': [{'op': 'field-type', 'field': 'payload', 'type': 'string'}]}]
        p.update(relations=[], connection_rules=[])
        s.update(nodes=[{'id': 'a', 'kind': 'A', 'fields': {'payload': "raise RuntimeError('subject content must remain data')"}}], edges=[])
    add('executable-looking-string-inspected-as-data', string_content)
    return rows


def verify(write=False):
    context = json.loads((b.UNIT / 'context.json').read_bytes()); b.external_current(context); snap = b.snapshot(); b.r.verify(snap, b.ROOT)
    bindings = [b.ref(path) for path in [b.UNIT / 'verify_structural_profile.py', b.UNIT / 'build_candidate.py', b.IMPL / 'contracts.py', b.IMPL / 'resolver.py']]
    runtime = v.f.current_bindings(); results = []
    for case in controls():
        # Exercise the actual strict decoder rather than accepting only in-memory literals.
        profile = b.r.parse(json.dumps(case['profile']).encode(), 'authored-profile'); subject = b.r.parse(json.dumps(case['subject']).encode(), 'authored-subject')
        before = copy.deepcopy((profile, subject))
        try:
            outcome = inspect(profile, subject)
            if case['expected_error'] is not None or (outcome['local_constraints_pass'], outcome['connection_rules_pass'], outcome['level_matches']) != (case['expected_C'], case['expected_N'], case['expected_level']):
                raise ValueError('Wrong structural outcome: ' + case['case_id'])
            result = {'case_id': case['case_id'], 'profile': profile, 'subject': subject, 'status': 'inspected-authored-finite-structure', 'outcome': outcome}
        except ProfileFault as error:
            if error.code != case['expected_error']: raise
            result = {'case_id': case['case_id'], 'profile': profile, 'subject': subject, 'status': 'rejected-structural-input', 'code': error.code}
        if (profile, subject) != before: raise ValueError('Inspection mutated schema or occupant')
        results.append(result)
    revisions = []
    for name, new_min, value, expected in [('tightening-rejects-previously-valid', 1, 0, [True, False]),
        ('relaxation-retains-selected-valid-example', -1, 0, [True, True]), ('relaxation-admits-previously-invalid', -1, -1, [False, True])]:
        old = base_profile(); new = copy.deepcopy(old); subject = base_subject()
        for kind in new['kinds']: kind['constraints'][1]['minimum'] = new_min
        subject['nodes'][0]['fields']['value'] = value
        before = copy.deepcopy((old, new, subject)); old_result, new_result = inspect(old, subject), inspect(new, subject)
        if [old_result['conforms'], new_result['conforms']] != expected or (old, new, subject) != before: raise ValueError('Wrong finite revision result')
        revisions.append({'case_id': name, 'old_profile': old, 'new_profile': new, 'subject': subject, 'old_result': old_result, 'new_result': new_result,
            'universal_compatibility_proved': False, 'semantic_preservation_proved': False, 'revision_authorized': False})
    schema_path = b.ROOT / 'authority/artifact-types/definition/v1/schema.json'; schema_ref = b.ref(schema_path)
    schema = b.r.parse(b.r.read_bytes(b.ROOT, schema_ref['path']), 'actual-Definition-schema'); b.c.Draft202012Validator.check_schema(schema)
    source = b.source_ref(snap, 'cal.definition.schema'); document = b.co.source_document(snap, source); fixture = copy.deepcopy(document)
    fixture['semantic_owner_ref'] = 'role:unverified-example-owner'
    fixture_errors = list(b.c.Draft202012Validator(schema).iter_errors(fixture))
    fixture_raw = json.dumps(fixture, indent=2, sort_keys=True).encode() + b'\n'
    if fixture_errors or b.r.digest(fixture_raw) == source['sha256']: raise ValueError('Actual schema fixture failed or substituted canonical bytes')
    actual_schema_fixture = {'fixture': fixture, 'schema_ref': schema_ref, 'canonical_source_ref': source,
        'fixture_sha256': b.r.digest(fixture_raw), 'Definition_v1_schema_valid': True, 'matches_current_registered_source_bytes': False,
        'fixture_owner_authenticated': False, 'admission_or_truth_established': False,
        'meaning': 'Authored altered-owner fixture passes actual shape schema but is not the current source bytes and has no authenticated owner/admission evidence.'}
    prior = json.loads((b.BASE / 'definitions/cal.definition.premise/delivery-manifest.json').read_bytes())
    for ref in prior['files'] + context['sources'] + bindings + [schema_ref]:
        if b.ref(b.ROOT / ref['path']) != ref: raise ValueError('Closing source/checker/prior drift')
    b.external_current(context); b.r.verify(snap, b.ROOT)
    if runtime != v.f.current_bindings(): raise ValueError('Runtime drift')
    report = {'schema_version': 'definition-assurance-schema-finite-inspection/v1-candidate',
        'status': 'PASS-for-exact-finite-structural-inspection-controls', 'authority_effect': 'none', 'checker_bindings': bindings,
        'runtime_bindings': runtime, 'selected_actual_schema_ref': schema_ref,
        'results': results, 'structural_controls': len(results), 'rejected_structural_inputs': sum(x['status'] == 'rejected-structural-input' for x in results),
        'C_N_variation_cases': [x['case_id'] for x in results[:4]], 'revision_results': revisions, 'revision_controls': len(revisions),
        'actual_schema_fixture': actual_schema_fixture, 'actual_schema_fixture_checks': 1,
        'source_fidelity': 'pending', 'semantic_ready': False, 'mechanized_proof': False,
        'source_Conforms_to_inspector_embedding_reviewed': False, 'universal_C_N_independence_proved': False,
        'subject_executed': False, 'occupants_added': 0, 'source_or_producer_changed': False,
        'claim_ceiling': 'Actual closed finite candidate profile: at most8 kinds/constraints per kind/relations/rules/nodes/path length and64 edges; fixed field-type/integer-min, endpoint/multiplicity/path-equation operators. Authored controls and selected revision witnesses only. No arbitrary schema-language decidability, canonical C/N independence, universal migration compatibility, source embedding fidelity, subject execution/population, ownership/truth/promotion or whole-definition proof.'}
    if write: b.put('structural-profile-checks.json', report)
    elif not b.r.same_json(report, json.loads((b.UNIT / 'structural-profile-checks.json').read_bytes())): raise ValueError('Fresh finite profile evidence differs')
    return report


def main():
    report = verify('--write' in b.sys.argv)
    print(json.dumps({'result': report['status'], 'structural_controls': report['structural_controls'], 'rejected_structural_inputs': report['rejected_structural_inputs'],
        'C_N_variation_cases': 4, 'revision_controls': report['revision_controls'], 'actual_schema_fixture_checks': 1,
        'source_Conforms_to_inspector_embedding_reviewed': False, 'subject_executed': False, 'occupants_added': 0,
        'universal_compatibility_proved': False, 'semantic_ready': False}, indent=2, sort_keys=True))


if __name__ == '__main__': main()
