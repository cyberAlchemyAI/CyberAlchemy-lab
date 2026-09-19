"""Import a complete Capability as a candidate, with explicit semantic dependencies."""
import importlib.util
import json
from pathlib import Path
import sys
from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / 'tooling/importers'))
from migration_contract_import import digest, read
from migration_contracts import load_registry, REGISTRY


def validate_source(capability, nodes, schema):
    Draft202012Validator({**schema, '$ref': '#/$defs/productCapability'}).validate(capability)
    index = {node['id']: node for node in nodes}
    if len(index) != len(nodes):
        raise ValueError('Duplicate source node identity')
    for field in ['product_ref', 'business_ontology_ref']:
        if capability[field] not in index:
            raise ValueError('Unresolved ' + field)
    for field in ['participant_refs', 'consumer_refs', 'input_contract_refs', 'output_contract_refs', 'context_policy_refs', 'outcome_refs']:
        for ref in capability[field]:
            if ref not in index:
                raise ValueError('Unresolved ' + field + ': ' + ref)
    status_schema = schema['$defs']['lifecyclePosture']['properties']['status']
    Draft202012Validator(status_schema).validate(capability['lifecycle_posture']['status'])
    planned = capability['realization_binding_refs']
    if planned != ['CA2-CAP-BIND-PEOPLE-AND-TEAMS-UNSELECTED']:
        raise ValueError('Realization references require an explicit binding adapter')
    return {'status_vocabulary_selector': '/$defs/lifecyclePosture/properties/status',
            'status_vocabulary': status_schema,
            'concept_references': [ref for ref in capability['participant_refs'] if index[ref]['role'] in ['actor', 'collective_actor']],
            'team_instances_required': 0,
            'realization': {'state': 'not-selected', 'resolved_bindings': [], 'unresolved_source_refs': planned,
                            'treatment': 'Preserved as source residue; no implementation binding is asserted or needed for candidate import.'}}


def prepare(source_root):
    plan = read(HERE / 'plan.json')
    registry = load_registry()
    if plan['mode'] != 'candidate-only' or plan['scope'] != registry['scope'] or plan['registry_sha256'] != digest(ROOT / REGISTRY):
        raise ValueError('Candidate scope or registry mismatch')
    schema_path = source_root / plan['source_schema']['path']
    if digest(schema_path) != plan['source_schema']['sha256']:
        raise ValueError('Source schema drift')
    previous = HERE.parent / '0003-source-record-completion/complete.py'
    spec = importlib.util.spec_from_file_location('source_completion', previous)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    completed = module.complete(source_root)
    source = completed['source_records']
    capability = source['product-capability.json']
    closure = validate_source(capability, source['nodes.json']['nodes'], read(schema_path))
    selected = [entry for entry in completed['records'] if entry['record']['kind'] in ['product', 'product-capability']]
    from engine import validate_graph
    validate_graph({'schema_version': 'cal-review-graph/v1', 'authority_effect': 'none', 'nodes': [entry['record'] for entry in selected], 'relations': []})
    for entry in selected:
        entry['disposition'] = 'imported-candidate'
        entry['operational_use_authorized'] = False
    vocabulary = {**plan['source_schema'], 'selector': closure['status_vocabulary_selector']}
    return {'result': 'PASS', 'mode': 'candidate-only', 'imported': 2, 'team_instances': 0,
            'authority_effect': 'none', 'operational_use_authorized': False,
            'records': selected, 'source_records': source, 'source_bindings': completed['source_bindings'],
            'closure': closure, 'lifecycle_binding': {'source_status': capability['lifecycle_posture']['status'], 'status_vocabulary_ref': vocabulary, 'origin': 'Explicit migration binding to the existing source schema; source bytes unchanged.'},
            'dependency_policy': plan['dependency_policy'],
            'operational_blockers': [ref for entry in selected for ref in entry['dependencies'] if ref.get('admission_posture') != 'admitted'],
            'plan_sha256': digest(HERE / 'plan.json')}


if __name__ == '__main__':
    result = prepare(ROOT.parent / 'cyberAlchemy-v2')
    output = ROOT / '.local/capability-candidate-import-0004'
    if output.exists():
        raise ValueError('Existing import is immutable; choose a successor run')
    output.mkdir(parents=True)
    text = json.dumps(result, indent=2, sort_keys=True) + '\n'
    (output / 'import.json').write_text(text)
    (HERE / 'results.json').write_text(text)
    print(json.dumps({k: result[k] for k in ['result', 'imported', 'team_instances', 'mode', 'operational_use_authorized']}))
