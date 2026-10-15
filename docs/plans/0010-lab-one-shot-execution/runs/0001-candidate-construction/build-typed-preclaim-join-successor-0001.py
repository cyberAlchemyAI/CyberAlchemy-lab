"""Refuse provably mismatched selected typed identities before durable claim.

The complete original wire/noncollapse/body/schema/core/postimage predicates
remain in the pure preparation. This adds early exact comparisons only.
"""
import ast
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD, NEW = BASE / 'typed-host-composition-v3', BASE / 'typed-host-composition-v4'
PIN = 'f722728cdc57263944e5f7db65dd0b91d3e7f464f15c10297bb517b964db4a20'


def binding(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def emit(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')


def main():
    assert not NEW.exists()
    old = json.loads((OLD / 'source-manifest.json').read_bytes())
    assert binding(OLD / 'source-manifest.json')['sha256'] == PIN
    for row in old['files'] + old['input_bindings']:
        assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256']
    NEW.mkdir()
    for path in OLD.glob('*'):
        if path.is_file() and path.name != 'source-manifest.json':
            (NEW / path.name).write_bytes(path.read_bytes())
    path = NEW / 'selection.py'
    with path.open('a') as stream:
        stream.write('''

def inspection_join(message, proposal, inspection):
    """Compare independently selected identities before any durable claim.

    Structural identity checks are separate from complete current catalog,
    body/schema/core closure and genuine owner semantic judgment.
    """
    require(proposal['proposal_ref'] == inspection['proposal_ref'],
            'typed inspection selects another exact proposal')
    fields = ('scope_ref', 'identity_ref', 'version_ref', 'carrier_ref', 'byte_sha256')
    candidate = message['relation_kind_candidate']
    require(type(candidate) is dict and set(candidate) == set(fields)
            and candidate['carrier_ref'] == 'cal.artifact-type.relation-kind/v2',
            'original exact Relation Kind candidate header required')
    targets = [target for target in proposal['targets'] if target['operation'] != 'withdraw'
               and {field: target['artifact'][field] for field in fields} == candidate]
    require(len(targets) == 1, 'exact selected Relation Kind target missing or ambiguous')
    target = targets[0]
    require(candidate['scope_ref'] == proposal['scope_ref']
            and candidate['identity_ref'] == inspection['relation_kind_ref']
            and candidate['version_ref'] == inspection['successor_version_ref'],
            'typed selected candidate scope, identity or successor differs')
    prior = target['predecessor']
    require(inspection['predecessor_version_ref'] == (None if prior is None else prior['version_ref']),
            'typed selected predecessor revision differs')
    require(message['unique_semantic_question'] == inspection['unique_question']
            and message['axis_ref'] == inspection['axis_ref']
            and message['noncollapse_report_binding'] == inspection['noncollapse_report_binding'],
            'typed selected question, axis or noncollapse evidence differs')
    domains = []
    for pair in inspection['allowed_endpoint_pairs']:
        if pair['qualifier_schema_binding'] not in domains:
            domains.append(pair['qualifier_schema_binding'])
    require(message['qualifier_domain_bindings'] == domains,
            'typed complete ordered qualifier domain selection differs')
    return target
''')
    path = NEW / 'preparation.py'
    text = path.read_text()
    assert text.count('from .selection import require, schema_paths, target_metadata') == 1
    text = text.replace('from .selection import require, schema_paths, target_metadata',
                        'from .selection import require, schema_paths, target_metadata, inspection_join')
    anchor = '        schema_paths(self.routing, proposal)\n        return proposal_raw, proposal, actor\n'
    assert text.count(anchor) == 1
    text = text.replace(anchor, '''        schema_paths(self.routing, proposal)
        inspection = self.P.frame_parse(self.read(self.routing['inspection_binding']))
        inspection_join(message, proposal, inspection)
        return proposal_raw, proposal, actor
''')
    path.write_text(text)
    # Flatten precisely the added import and two preflight statements; every
    # original source, policy, schema, core, postimage and evidence AST remains.
    original, revised = ast.parse((OLD / 'preparation.py').read_bytes()), ast.parse(text)
    imports = next(node for node in revised.body if isinstance(node, ast.ImportFrom) and node.module == 'selection')
    assert imports.names[-1].name == 'inspection_join'
    imports.names.pop()
    preflight = next(node for node in ast.walk(revised) if isinstance(node, ast.FunctionDef) and node.name == 'preflight')
    assert ast.unparse(preflight.body[-2]) == 'inspection_join(message, proposal, inspection)'
    assert ast.unparse(preflight.body[-3]) == "inspection = self.P.frame_parse(self.read(self.routing['inspection_binding']))"
    del preflight.body[-3:-1]
    assert ast.dump(original, include_attributes=False) == ast.dump(revised, include_attributes=False)
    before, after = ast.parse((OLD / 'selection.py').read_bytes()), ast.parse((NEW / 'selection.py').read_bytes())
    assert ast.dump(before, include_attributes=False) == ast.dump(ast.Module(body=after.body[:-1], type_ignores=[]), include_attributes=False)
    assert (OLD / 'test_selection.py').read_bytes() == (NEW / 'test_selection.py').read_bytes()
    path = NEW / 'routing.schema.json'
    document = json.loads(path.read_bytes())
    document['$id'] = 'urn:cyberalchemy-lab:typed-preparation-routing:v4-candidate'
    document['properties']['schema_version']['const'] = 'lab-typed-preparation-routing/v4-candidate'
    path.write_text(json.dumps(document, sort_keys=True, indent=2) + '\n')
    path = NEW / 'DESIGN.md'
    path.write_text(path.read_text() + '\n## Early exact inspection identity join\n\nV4 compares the selected proposal, exact candidate header, successor/predecessor,\nquestion, axis, noncollapse binding and complete ordered qualifier domains before\nthe original dispatcher claims a key. Known identity contradictions cause the\nexisting preclaim invalid-contract outcome. Every original full wire/noncollapse,\nbody/schema/core/postimage and source-exit predicate remains in preparation.\nIncomplete core and postclaim uncertainty handling remain unchanged.\n')
    context = RUN / 'context-R03-typed-preclaim-join-0001.json'
    emit(context, {'schema_version': 'lab-bounded-context/v1-candidate', 'strict_coverage': 'PASS',
        'task': 'R03 exact independent typed inspection identity checks before claim',
        'source_bindings': [binding(OLD / 'source-manifest.json'), binding(RUN / 'API48-typed-binding-join-checks-0001.json'),
                            binding(RUN / 'authorization.json')],
        'write_scope': NEW.relative_to(ROOT).as_posix(),
        'constraints': ['Every original preparation predicate AST and25 selection methods preserved.',
            'Add exact preclaim joins; no catalog/body/core/semantic predicate removed or replaced.',
            'No owner outcome, operational grant, source mutation or full runtime qualification.'],
        'actual_owner_outcome': None, 'authority_effect': 'none', 'task_complete': False})
    static = RUN / 'typed-preclaim-join-static-0001.json'
    emit(static, {'schema_version': 'lab-typed-preclaim-join-static/v1-candidate', 'result': 'PASS',
        'retained_selection_methods': 25, 'every_original_preparation_predicate_AST_unchanged': True,
        'every_other_original_selection_AST_unchanged': True, 'only_preparation_additions': ['inspection_join import',
            'read exact independently selected inspection bytes in preflight', 'inspection_join before original return'],
        'actual_public_calls': 0, 'public_runtime_qualified': False,
        'actual_owner_outcome': None, 'authority_effect': 'none', 'task_complete': False})
    inputs = old['input_bindings'] + [binding(OLD / 'source-manifest.json'), binding(context), binding(static),
                                     binding(Path(__file__).resolve()), binding(RUN / 'API48-typed-binding-join-checks-0001.json')]
    # New regression source is added before the package is sealed by its runner.
    emit(RUN / 'typed-preclaim-join-unsealed-inventory-0001.json', {'schema_version': 'lab-unsealed-candidate-source/v1',
        'parent': old, 'input_bindings': inputs, 'context_binding': binding(context), 'static_binding': binding(static),
        'actual_owner_outcome': None, 'authority_effect': 'none', 'task_complete': False})
    print(json.dumps({'result': 'AUTHORED-UNSEALED', 'retained_original_selection_methods': 25,
                      'original_preparation_predicates_retained': True}), flush=True)


if __name__ == '__main__':
    main()
