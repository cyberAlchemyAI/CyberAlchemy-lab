#!/usr/bin/env python3
"""Validate and render this candidate; never update the admitted registry."""
from pathlib import Path
import hashlib
import importlib.util
import json
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]


def main():
    path = ROOT / 'definitions/user-journey/v1/definition.json'
    raw = path.read_bytes();body = json.loads(raw)
    schema = REPO / 'authority/artifact-types/definition/v2/schema.json'
    generator = REPO / 'authority/artifact-types/definition/v2/generator.py'
    if hashlib.sha256(schema.read_bytes()).hexdigest() != body['schema_digest']:
        raise ValueError('Definition schema changed')
    if hashlib.sha256(generator.read_bytes()).hexdigest() != body['source_direction']['generator_sha256']:
        raise ValueError('Definition generator changed')
    Draft202012Validator(json.loads(schema.read_bytes())).validate(body)
    spec = importlib.util.spec_from_file_location('_user_journey_generator', generator)
    module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    (path.parent / 'DEFINITION.md').write_text(module.render(body))
    registry = {'schema_version': 'cal.candidate-definition-index/v1', 'authority_effect': 'none',
                'standing': 'candidate-only; not admitted-current lookup', 'entries': [{
                    'definition_id': body['definition_id'], 'version': body['version'], 'term': body['term'],
                    'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(raw).hexdigest(),
                    'lifecycle_posture_ref': body['classification']['lifecycle_posture_ref'], 'admission_decision_ref': None}]}
    (ROOT / 'registry.json').write_text(json.dumps(registry, sort_keys=True, indent=2) + '\n')
    print('User Journey schema, provider pins, generated Markdown and candidate index: PASS')


if __name__ == '__main__':main()
