#!/usr/bin/env python3
"""Read-only structural review of this exact candidate compatibility package.

This is not the product evaluator, a semantic proof or an admission operation.
It writes no receipt, registry, store, profile or authority state.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import re
from jsonschema import Draft202012Validator


STEP = Path(__file__).resolve().parent
ROOT = STEP.parents[5]
PREVIOUS = ROOT / 'define/development/m1-preparation-preview/v1/steps/04-definition-v2-profiles'


def raw(path):
    return Path(path).read_bytes()


def digest(path):
    return hashlib.sha256(raw(path)).hexdigest()


def load(path):
    def pairs(items):
        out = {}
        for key, value in items:
            if key in out:
                raise ValueError('duplicate JSON key: ' + key)
            out[key] = value
        return out

    def invalid(value):
        raise ValueError('non-finite JSON constant: ' + value)

    value = json.loads(raw(path).decode('utf-8', 'strict'), object_pairs_hook=pairs, parse_constant=invalid)

    def finite(item):
        if isinstance(item, float) and not math.isfinite(item):
            raise ValueError('non-finite JSON number')
        if isinstance(item, dict):
            for child in item.values():
                finite(child)
        elif isinstance(item, list):
            for child in item:
                finite(child)

    finite(value)
    return value


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    freeze = load(STEP / 'source-selection.json')
    for row in freeze['files']:
        require(digest(ROOT / row['path']) == row['sha256'], 'changed captured source: ' + row['path'])

    v1_schema = load(ROOT / 'authority/artifact-types/definition/v1/schema.json')
    v1_projection = module(ROOT / 'authority/artifact-types/definition/v1/generator.py', 'selected_v1_projection')
    profile_schema = load(PREVIOUS / 'profile-carriers.schema.json')
    root_schema = load(ROOT / 'authority/artifact-types/artifact-type/v2/schema.json')
    descriptor_projection = module(ROOT / 'tooling/generators/artifact_type_successor.py', 'selected_descriptor_projection')
    delta = load(STEP / 'registration-delta.json')
    definitions = load(STEP / 'semantic-binding-review.json')['needed_meanings']
    for binding in definitions:
        path = ROOT / binding['path']
        require(digest(path) == binding['sha256'], 'changed semantic candidate')
        value = load(path)
        Draft202012Validator(v1_schema).validate(value)
        require(value['schema_digest'] == digest(ROOT / 'authority/artifact-types/definition/v1/schema.json'), 'wrong v1 schema digest')
        require(value['source_direction']['generator_sha256'] == digest(ROOT / 'authority/artifact-types/definition/v1/generator.py'), 'wrong v1 generator digest')
        require(path.with_name('DEFINITION.md').read_text(encoding='utf-8') == v1_projection.render(value), 'semantic projection mismatch')

    for name in ['evaluation', 'lifecycle']:
        value = load(PREVIOUS / (name + '.json'))
        Draft202012Validator(profile_schema).validate(value)
        require(value['schema_digest'] == digest(PREVIOUS / 'profile-carriers.schema.json'), 'wrong profile schema digest')
        require(value['binding_contract_sha256'] == digest(ROOT / value['binding_contract_ref']), 'wrong check-contract digest')
        require(value['source_direction']['generator_sha256'] == digest(PREVIOUS / 'generator.py'), 'wrong profile generator digest')

    for entry in delta['proposed_new_registrations']:
        Draft202012Validator({'$ref': '#/$defs/registeredType', '$defs': root_schema['$defs']}).validate(entry)
        require(entry['schema_sha256'] == digest(ROOT / entry['schema_path']), 'wrong registration schema digest')

    for binding in delta['proposed_descriptor_revisions']:
        path = ROOT / binding['path']
        require(digest(path) == binding['sha256'], 'changed descriptor')
        value = load(path)
        require(value['status'] == 'candidate-unadmitted' and value['authority_effect'] == 'none', 'descriptor claimed adoption')
        require(value['artifact_type_root_binding']['sha256'] == digest(ROOT / value['artifact_type_root_binding']['path']), 'root binding mismatch')
        require(value['source_direction']['shared_generator_sha256'] == digest(ROOT / value['source_direction']['shared_generator_path']), 'descriptor generator mismatch')
        require(path.with_name('ARTIFACT.md').read_text(encoding='utf-8') == descriptor_projection.render_artifact(value), 'descriptor projection mismatch')
        for semantic in value['semantic_definition_bindings']:
            require(semantic['sha256'] == digest(ROOT / semantic['path']), 'semantic binding mismatch')
            require(semantic['admission_posture'] == 'candidate-unadmitted', 'fabricated semantic admission')

    compatibility = load(STEP / 'compatibility.json')
    old = load(ROOT / compatibility['foundation']['predecessor']['path'])
    new = load(ROOT / compatibility['foundation']['proposed_successor']['path'])
    for field in ['normative_statement', 'formal_expression']:
        require(old['voices']['scientific_formal'][field] == new['voices']['scientific_formal'][field], 'foundational meaning changed')
    require(old['scope'] == new['scope'], 'foundational scope changed')
    require(len(compatibility['historical_connections']) == len(old['typed_relations']) == 2, 'historical reference disposition missing')
    require(not new['typed_relations'], 'new global references inferred')
    current_descriptor = load(ROOT / 'authority/artifact-types/definition/v2/artifact.json')
    proposed_descriptor = load(STEP / 'carriers/definition-binding-successor/artifact.json')
    for field in ['instance_contract', 'relation_roles', 'schema_digest']:
        require(current_descriptor[field] == proposed_descriptor[field], 'binding-only descriptor changed shape or relation surface')

    recipe = load(STEP / 'activation-order.json')
    ordered = [node['id'] for node in recipe['nodes']]
    require(len(set(ordered)) == len(ordered), 'duplicate activation node')
    for node in recipe['nodes']:
        require(all(ordered.index(parent) < ordered.index(node['id']) for parent in node['depends_on']), 'activation cycle')
    for path in [STEP / 'REVIEW.md', STEP.parents[1] / 'README.md', STEP.parents[1] / 'DEFINITIONS-INDEX.md']:
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
            require((path.parent / target.split('#')[0]).resolve().exists(), 'broken review link: ' + target)

    print(json.dumps({'scope': 'exact selected candidate structure/bindings/projections only', 'result': 'PASS', 'semantic_candidates': len(definitions), 'carrier_descriptors': len(delta['proposed_descriptor_revisions']), 'historical_dispositions': 2, 'formal_proof': 'not executed', 'owner_acceptance': 'pending', 'runtime_conformance': 'not claimed', 'authority_effect': 'none', 'admissions': 0}, indent=2))


if __name__ == '__main__':
    main()
