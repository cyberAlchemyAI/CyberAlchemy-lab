"""Install the approved migration contracts through an additive decision overlay."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BATCH = ROOT / 'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0026-remaining-targets-review-batch'
APPROVAL = ROOT / 'docs/decisions/0051-remaining-83-review-approval/decision.json'
REGISTRY = ROOT / 'authority/decisions/migration-contracts/v1/registry.json'
DECISION_ID = 'CAL-REMAINING-83-CONTRACT-ADMISSION-0052'
SCOPE = 'cyberAlchemy-v2-to-CyberAlchemy-lab-migration'


def read(path):
    return json.loads(path.read_text())


def bind(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def verify(ref):
    if bind(ROOT / ref['path']) != {k: ref[k] for k in ('path', 'sha256')}:
        raise ValueError('Binding drift: ' + ref['path'])


def install(path, value):
    text = json.dumps(value, indent=2, sort_keys=True) + '\n'
    if path.exists() and path.read_text() != text:
        raise ValueError('Refusing to overwrite an existing different decision: ' + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def main():
    approval = read(APPROVAL)
    if approval['status'] != 'approved' or len(approval['targets']) != 83:
        raise ValueError('Expected approval of exactly 83 targets')
    for ref in approval['subject'].values():
        verify(ref)
    manifest = read(BATCH / 'manifest.json')
    for ref in manifest['materials']:
        verify(ref)
    dependencies = read(BATCH / 'dependencies.json')
    for ref in dependencies['definitions'] + dependencies['admitted_definitions']:
        verify(ref)
    entries = []
    for target in approval['targets']:
        verify(target['binding'])
        verify(target['contract'])
        contract = read(ROOT / target['contract']['path'])
        if contract['target_id'] != target['target_id']:
            raise ValueError('Target identity mismatch')
        definitions = contract['semantic_definition_bindings']
        for ref in definitions:
            verify(ref)
        entries.append({
            **target,
            'status': 'admitted-migration-contract',
            'decision_ref': DECISION_ID,
            'scope': SCOPE,
            'semantic_definition_bindings': definitions,
            'candidate_definition_dependencies': [ref for ref in definitions if ref.get('admission_posture') != 'admitted'],
            'carrier_ref': contract.get('carrier_ref'),
            'consumer_activation': 'not-applied',
            'action_authorized': False,
        })
    if len({entry['target_id'] for entry in entries}) != 83:
        raise ValueError('Duplicate targets')
    registry = {
        'schema_version': 'cal-migration-contract-registry/v1',
        'scope': SCOPE,
        'authority_effect': 'exact-contract-admission-within-migration',
        'decision_path': str((HERE / 'decision.json').relative_to(ROOT)),
        'approval': bind(APPROVAL),
        'snapshot': bind(BATCH / 'manifest.json'),
        'dependency_inventory': bind(BATCH / 'dependencies.json'),
        'entries': entries,
        'claim_ceiling': 'Authoritative contract selection for this migration only. Definition and carrier admission are not inferred; consumer activation and domain actions are not granted.',
    }
    install(REGISTRY, registry)
    decision = {
        'schema_version': 'cal-migration-contract-admission-decision/v1',
        'decision_id': DECISION_ID,
        'status': 'owner-admitted-within-migration',
        'authority_effect': '83-exact-migration-contracts-admitted-by-decision-overlay',
        'authorization': {'approval': bind(APPROVAL), 'continuation_verbatim': 'do next', 'resolution_basis': 'Apply registration after approval of the exact reviewed contracts. No repeated approval is required for this scope.'},
        'scope': SCOPE,
        'registry': bind(REGISTRY),
        'family_counts': dict(Counter(e['family'] for e in entries)),
        'transaction_model': 'additive decision overlay; preserve reviewed candidate bytes',
        'dependency_policy': 'Dependencies retain their recorded posture. These contracts are selected for the migration, without promoting candidate Definitions or earlier carriers. Live integration must resolve the dependencies it uses.',
        'consumer_activation': 'not-applied',
        'next_step': 'Connect a bounded migration consumer to this registry and validate its real inputs and dependency requirements before activation.',
    }
    install(HERE / 'decision.json', decision)
    ledger = read(BATCH / 'reconciliation.json')
    by_id = {entry['target_id']: entry for entry in entries}
    changed = 0
    for row in ledger['targets']:
        if row['target_id'] in by_id:
            if row['construction_state'] != 'constructed-candidate':
                raise ValueError('Unexpected predecessor state')
            row['construction_state'] = 'admitted-migration-contract'
            row['admission_decision'] = bind(HERE / 'decision.json')
            row['admission_scope'] = SCOPE
            row['next_action'] = decision['next_step']
            changed += 1
    if changed != 83:
        raise ValueError('Ledger membership mismatch')
    ledger['state_counts'] = dict(Counter(r['construction_state'] for r in ledger['targets']))
    ledger['authority_effect'] = 'migration-contract-admission-reconciliation'
    ledger['claim_ceiling'] = '13 previously admitted targets; 83 contracts admitted within migration scope; 99 constructed candidates. Scoped contract admission does not assert global Definition closure or consumer activation.'
    ledger['inputs'].extend([bind(BATCH / 'reconciliation.json'), bind(HERE / 'decision.json')])
    install(HERE / 'reconciliation.json', ledger)
    print(json.dumps({'result': 'PASS', 'admitted_migration_contracts': changed, 'state_counts': ledger['state_counts']}))


if __name__ == '__main__':
    main()
