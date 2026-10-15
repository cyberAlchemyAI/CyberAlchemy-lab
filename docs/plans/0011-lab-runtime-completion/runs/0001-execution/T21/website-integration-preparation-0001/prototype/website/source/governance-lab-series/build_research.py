from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone
import argparse

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description='Explicitly refresh the captured repository sources.')
parser.add_argument('--repository', type=Path, required=True, help='Repository checkout to capture; not used by the normal website build')
REPO = parser.parse_args().repository.resolve()
OUT = ROOT / 'research'
OUT.mkdir(exist_ok=True)
sources = {}
issues = []

def read(path):
    return json.loads((REPO / path).read_text(encoding='utf-8'))

def capture(path, selector='/', expected=None, role='catalog source'):
    p = REPO / path
    raw = p.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    dest = OUT / 'sources' / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(raw)
    item = sources.setdefault(path, {'repository_path': str(p), 'snapshot_path': 'research/sources/' + path,
                                    'sha256': digest, 'selectors': [], 'roles': []})
    if selector not in item['selectors']:
        item['selectors'].append(selector)
    if role not in item['roles']:
        item['roles'].append(role)
    if expected and digest != expected.removeprefix('sha256:'):
        issues.append({'path': path, 'issue': 'digest differs from registry binding',
                       'expected': expected, 'observed': digest})
    return item['snapshot_path']

definitions_registry = 'authority/definitions/registry.json'
dr = read(definitions_registry)
capture(definitions_registry, '/entries; /current_lookup', role='effective definition selection')
by_definition = {e['definition_id'] + '@' + e['version']: e for e in dr['entries']}
definitions = []
for identity, ref in sorted(dr['current_lookup'].items()):
    e = by_definition[ref]
    d = read(e['path'])
    source = capture(e['path'], '/voices/scientific_formal', e['sha256'], 'normative definition')
    formal = d['voices']['scientific_formal']
    plain = d['voices'].get('plain_language', {})
    definitions.append({'identity': identity, 'ref': ref, 'term': e['term'], 'version': e['version'],
        'effective_status': e['lifecycle_state'], 'decision_ref': e['admission_decision_ref'],
        'source': source, 'repository_path': e['path'], 'sha256': e['sha256'],
        'normative_statement': formal['normative_statement'], 'formal_expression': formal.get('formal_expression'),
        'boundary_conditions': formal.get('boundary_conditions', []),
        'plain_explanation': plain.get('explanation', ''), 'scope': d.get('scope')})

base = 'authority/admissions/governance-transaction-surface/v1/registries/'
ar = read(base + 'artifact-type-registry.json')
capture(base + 'artifact-type-registry.json', '/admitted_contracts; /current_by_identity; /inventory', role='effective contract selection')
contracts = []
current_refs = set(ar['current_by_identity'].values())
for e in ar['admitted_contracts']:
    if e['artifact_type_ref'] not in current_refs:
        continue
    a = read(e['artifact_path'])
    schema = read(e['schema_path'])
    selected_schema = schema
    if e.get('schema_selector'):
        for token in e['schema_selector'].removeprefix('#/').split('/'):
            selected_schema = selected_schema[token.replace('~1', '/').replace('~0', '~')]
    x = dict(e)
    x['source'] = capture(e['artifact_path'], '/', e['artifact_sha256'], 'admitted type contract')
    x['schema_source'] = capture(e['schema_path'], e.get('schema_selector') or '/', e['schema_sha256'], 'admitted schema binding')
    x['schema_top_level_required'] = selected_schema.get('required', [])
    x['schema_top_level_properties'] = list(selected_schema.get('properties', {}))
    x['schema_top_level_additional_properties'] = selected_schema.get('additionalProperties', 'unspecified')
    x['schema_note'] = 'Top level of the selected schema; follow the exact schema and its references for full constraints.'
    x['descriptor_effective_states'] = sorted({d['effective_state'] for d in ar['descriptors'] if d['artifact_type_ref'] == e['artifact_type_ref']})
    contracts.append(x)
contracts.sort(key=lambda x: x['artifact_type_ref'])

rr = read(base + 'relation-kind-registry.json')
capture(base + 'relation-kind-registry.json', '/entries', role='effective relation-kind selection')
relations = []
for e in rr['entries']:
    d = read(e['instance_path'])
    x = dict(e)
    x['source'] = capture(e['instance_path'], '/payload', e['instance_sha256'], 'closed relation contract')
    x.update(d['payload'])
    relations.append(x)
relations.sort(key=lambda x: x['relation_kind_id'])
endpoint_file = base + 'endpoint-inventory.json'
endpoints = read(endpoint_file)
capture(endpoint_file, '/entries; /counts', role='closed endpoint inventory')

chapters = [
    {'id': 1, 'title': 'Authority begins with meaning', 'obligation': 'Explain semantic, structural, relational, rule and actor authority without merging provenance or confidence.', 'paths': [
        'authority/governance/candidates/0001-three-lens-module/MODULE.md',
        'authority/governance/README.md']},
    {'id': 2, 'title': 'Following the evidence', 'obligation': 'Trace origin, integrity, observation, measurement, finding and evidence support without inherited authority.', 'paths': [
        'authority/operational-foundations/candidates/0001-cyberalchemy-lab-foundation/FOUNDATION.md']},
    {'id': 3, 'title': 'Changing a governed system', 'obligation': 'Explain independent lifecycle tracks, exact decisions, atomic admission, separate histories and challenge disposition.', 'paths': [
        'docs/decisions/0074-governance-transaction-surface-admission/DECISION.md',
        'authority/project-state-transitions/current.json',
        'implementation/lab-runtime/v1/lab_runtime/store.py',
        'implementation/lab-runtime/v1/lab_runtime/governance.py']},
    {'id': 4, 'title': 'What the Lab organizes', 'obligation': 'Explain the complete purpose, product, coordination, craft, implementation and context families.', 'paths': [
        'authority/ontology-integration/candidates/0003-definition-complete-runtime-integration/MODEL.md',
        'authority/artifact-types/coordination-context/v2/schema.json']},
    {'id': 5, 'title': 'How the records fit together', 'obligation': 'Separate definitions, representation contracts, instances, typed coupling and ontology projections; describe formal assurance accurately.', 'paths': [
        'authority/ontology-integration/candidates/0003-definition-complete-runtime-integration/integrated-model.json',
        'authority/artifact-types/candidates/0012-definition-complete-carrier-materialization/noncarrier-realizations.json',
        'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/source-and-formalization-coverage.json']},
    {'id': 6, 'title': 'An agent’s working session', 'obligation': 'Distinguish accountability, assignment, capability, delegation and ephemeral machine memory; trace fresh context and effects.', 'paths': [
        'implementation/lab-runtime/v1/README.md',
        'implementation/lab-runtime/v1/lab_runtime/session.py']},
    {'id': 7, 'title': 'How experience becomes useful', 'obligation': 'Connect research, experimentation, classification, failure, reflection, lessons, applications and outcomes.', 'paths': [
        'authority/ontology-integration/candidates/0003-definition-complete-runtime-integration/integrated-model.json']},
    {'id': 8, 'title': 'What is operational today', 'obligation': 'Separate exact admissions, implementation, historical execution, candidate successor, roadmap and release readiness.', 'paths': [
        'README.md', 'docs/ROADMAP.md',
        'implementation/lab-runtime/ADMISSION.md',
        'docs/decisions/0075-lab-operational-runtime-v1-admission/DECISION.md',
        'implementation/lab-runtime/v2/REVIEW.md',
        'implementation/lab-runtime/v2/profile.json',
        'implementation/lab-runtime/v2/receipts/validation.json',
        'ontology-lifecycle/README.md',
        'ontology-lifecycle/runtime/src/lib.rs',
        'implementation/bindings/ontology-product-event-runtime/v2/README.md',
        'implementation/bindings/ontology-product-event-runtime/v4/README.md']},
]
for ch in chapters:
    ch['sources'] = [capture(p, '/', role='essay source inspection') for p in ch['paths']]
lookup = read('authority/project-state-transitions/current.json')
for key in ['current_project_state', 'admission_bundle']:
    capture(lookup[key]['path'], '/', lookup[key]['sha256'], 'current D75 authority record')

literature = [
    {'title': 'W3C PROV-DM', 'url': 'https://www.w3.org/TR/prov-dm/', 'use': 'Entities, activities and agents provide a useful lineage model; this comparison confers no Lab authority.'},
    {'title': 'NIST SP 800-162, ABAC', 'url': 'https://csrc.nist.gov/pubs/sp/800/162/upd2/final', 'use': 'Subject, object, operation and environmental conditions clarify one part of actor permission.'},
    {'title': 'Saltzer and Schroeder, Basic Principles of Information Protection', 'url': 'https://web.mit.edu/Saltzer/www/publications/protection/Basic.html', 'use': 'Least privilege and fresh access checks inform the explanation of delegation.'},
    {'title': 'W3C SHACL', 'url': 'https://www.w3.org/TR/shacl/', 'use': 'Graph shape validation is a comparison for structural checks, not a claim of SHACL implementation.'},
    {'title': 'Martin Fowler, Event Sourcing', 'url': 'https://martinfowler.com/eaaDev/EventSourcing.html', 'use': 'Event history, replay and derived state; the Lab separately binds governance authority.'},
    {'title': 'Martin Fowler, Bounded Context', 'url': 'https://martinfowler.com/bliki/BoundedContext.html', 'use': 'Scoped models and explicit interrelationships explain the semantic boundary.'},
    {'title': 'Park et al., Generative Agents', 'url': 'https://arxiv.org/abs/2304.03442', 'use': 'Observation, retrieval, reflection and planning demonstrate an external memory architecture in a simulation; no business reliability or Lab conformance claim.'},
    {'title': 'Lean reference, Validating a Lean Proof', 'url': 'https://lean-lang.org/doc/reference/latest/ValidatingProofs/', 'use': 'Proof acceptance and intended theorem meaning are separate assurance questions.'},
    {'title': 'Mensh and Kording, Ten simple rules for structuring papers', 'url': 'https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005619', 'use': 'Editorial method: one central argument per essay, reader context and logical progression.'},
]
catalog = {'schema_version': 'explanatory-lab-catalog/v1', 'authority_effect': 'none',
    'captured_at': datetime.now(timezone.utc).isoformat(), 'project_state_selection': lookup,
    'counts': {'current_definition_identities': len(definitions), 'admitted_definition_versions': len(dr['entries']),
               'current_artifact_type_contract_bindings': len(contracts), 'all_admitted_type_contracts': len(ar['admitted_contracts']),
               'relation_kinds': len(relations), 'named_endpoint_kinds': len(endpoints['entries']),
               'declared_endpoint_pairs': sum(len(x['allowed_endpoint_pairs']) for x in relations)},
    'definitions': definitions, 'artifact_types': contracts, 'relations': relations,
    'endpoints': endpoints['entries'], 'artifact_registry_inventory': ar['inventory'],
    'historical_definition_versions': [e for e in dr['entries'] if e['definition_id']+'@'+e['version'] not in set(dr['current_lookup'].values())],
    'historical_artifact_contracts': [e for e in ar['admitted_contracts'] if e['artifact_type_ref'] not in current_refs]}
manifest = {'schema_version': 'essay-research-context/v1', 'authority_effect': 'none',
    'captured_at': catalog['captured_at'], 'repo': str(REPO), 'scope': 'Current finite semantic and representation catalogs plus selected governance, integration, runtime, roadmap and formal-assurance evidence.',
    'limits': ['No whole-repository ontology completeness claim.', 'No new implementation test execution.',
               'Historical receipts are reported as recorded evidence.', 'Copied candidate labels require the effective admission overlay.',
               'Illustrative business examples are not observed deployments.', 'Essay and snapshots confer no normative authority.'],
    'context_budget': {'mode': 'deep, split by eight obligations', 'extension_reason': 'Complete current reference catalogs require mechanical extraction beyond a single 24-file context pack; narrative inspection remains selected by chapter obligations.'},
    'chapters': chapters, 'literature': literature, 'sources': sorted(sources.values(), key=lambda x:x['repository_path']), 'issues': issues}
(OUT/'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2)+'\n')
(OUT/'context-pack.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({'counts': catalog['counts'], 'captured_sources': len(sources), 'binding_discrepancies': issues}, ensure_ascii=False))
