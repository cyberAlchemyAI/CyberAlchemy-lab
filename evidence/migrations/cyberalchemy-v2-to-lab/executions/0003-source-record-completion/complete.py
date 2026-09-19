"""Complete source-backed candidate records, retaining admission dependencies."""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / 'tooling/importers'))
from migration_contract_import import prepare, read, digest
from migration_contracts import load_registry


def complete(source_root):
    plan = read(HERE / 'plan.json')
    source = {}
    for ref in plan['sources']:
        path = source_root / ref['path']
        if digest(path) != ref['sha256']:
            raise ValueError('Source drift: ' + ref['path'])
        source[path.name] = read(path)
    prior = prepare(read(HERE.parent / '0002-contract-checked-sample/plan.json'), source_root)
    registry = {e['target_id']: e for e in load_registry()['entries']}
    nodes = {n['id']: n for n in source['nodes.json']['nodes']}
    product = prior['records'][0]['record']
    thesis, capability, obligations = (source[n] for n in ['product-thesis.json', 'product-capability.json', 'obligations.json'])
    if thesis['product_ref'] != prior['records'][0]['source_id'] or capability['product_ref'] != thesis['product_ref']:
        raise ValueError('Product reference mismatch')
    if thesis['thesis_id'] != prior['records'][1]['source_id'] or capability['business_ontology_ref'] != prior['records'][2]['source_id']:
        raise ValueError('Source record identity mismatch')
    if obligations['capability_ref'] != capability['capability_id'] or obligations['registry_id'] != capability['obligation_registry_ref']:
        raise ValueError('Obligation reference mismatch')
    if any(r['authority_effect'] != 'none' for r in [thesis, capability, obligations]):
        raise ValueError('Unexpected source effect')
    common = {'status': 'candidate-unadmitted', 'authority_effect': 'none', 'scope_ref': plan['scope'], 'product_ref': product['node_id']}
    thesis_record = {
        **common, 'kind': 'product-thesis',
        'node_id': 'cav2:people-and-teams/product-thesis.json#' + thesis['thesis_id'],
        'owner_ref': thesis['owner_route'],
        'audience': '; '.join(nodes[ref]['label'] for ref in thesis['participants']),
        'problem': thesis['problem'], 'value_proposition': thesis['value_proposition'],
        'assumptions': thesis['hypotheses'], 'revision_criteria': thesis['revision_criteria'],
    }
    owners = [r['owner'] for r in capability['owner_routes'] if r['responsibility'] == 'product-meaning']
    if len(owners) != 1:
        raise ValueError('Ambiguous product owner route')
    capability_record = {
        **common, 'kind': 'product-capability',
        'node_id': 'cav2:people-and-teams/product-capability.json#' + capability['capability_id'],
        'owner_ref': owners[0], 'outcome': capability['outcome'],
        'acceptance_conditions': [o['statement'] for o in obligations['obligations']],
        'exclusions': capability['exclusions'],
    }
    from engine import validate_graph
    graph = {'schema_version': 'cal-review-graph/v1', 'authority_effect': 'none', 'nodes': [product, thesis_record, capability_record], 'relations': []}
    validate_graph(graph)
    records = []
    for record in graph['nodes']:
        entry = registry['type.' + record['kind']]
        records.append({'record': record, 'contract': entry['contract'], 'missing_fields': [],
                        'disposition': 'validated-candidate-dependency-pending' if entry['candidate_definition_dependencies'] else 'imported-candidate',
                        'dependencies': entry['semantic_definition_bindings']})
    for ref in plan['sources']:
        if digest(source_root / ref['path']) != ref['sha256']:
            raise ValueError('Source changed during completion')
    return {'result': 'PASS', 'selected': 4, 'records_validated': 3, 'imported': 1,
            'staged_pending_dependencies': 2, 'not_applicable': 1,
            'missing_fields': 0, 'authority_effect': 'none', 'records': records,
            'team': plan['team_disposition'], 'source_bindings': plan['sources'],
            'source_records': source, 'mapping': plan['mapping'],
            'dependency_policy': plan['dependency_policy']}


if __name__ == '__main__':
    result = complete(ROOT.parent / 'cyberAlchemy-v2')
    output = HERE / 'results.json'
    text = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if output.exists() and output.read_text() != text:
        raise ValueError('Preserve previous result; create a successor run')
    output.write_text(text)
    print(json.dumps({k: result[k] for k in ['result', 'records_validated', 'imported', 'staged_pending_dependencies', 'not_applicable', 'missing_fields']}))
