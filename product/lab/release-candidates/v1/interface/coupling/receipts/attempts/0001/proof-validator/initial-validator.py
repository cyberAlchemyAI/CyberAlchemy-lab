"""Close only the R03 signed coupling subproof, with original evidence retained."""
from collections import Counter
import ast
import base64
import re
import time
from episode import *
from regression import adapted_source

PINS = EnginePins(
    '53e2f74c53f123b42d60d3cc3b4c66e75f3fa0c4c9a3142bf3f11e7500bd9677',
    'lab-operator-signed-coupling/v1-candidate',
    '4594cab2172646b1c2157e0a4be37f560088c580de875fd7d269925993fe1f0b',
    'cbfe3d7c5f92d0bc547b836a9d84616b9be26cb399a587aab8800f93fd96ed58')
RUN = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
ATTEMPT = HERE / 'receipts/attempts/0001'


def main():
    started = time.perf_counter()
    output = HERE / 'receipts/R03-0001.json'
    require(not output.exists(), 'retained proof receipt cannot be overwritten')
    files = {}
    checks = []

    def evidence(path):
        path = Path(path)
        binding = bind(path)
        require(not path.is_symlink(), 'evidence symlink')
        old = files.get(binding['path'])
        require(old is None or old == binding, 'conflicting original evidence epochs')
        files[binding['path']] = binding
        return parse(original(binding)) if path.suffix == '.json' else path.read_bytes()

    def pinned(binding):
        raw = original({k: binding[k] for k in ('path', 'sha256')})
        evidence(ROOT / binding['path'])
        return raw

    def check(name, value):
        require(value, name)
        checks.append({'test': name, 'result': 'PASS'})

    manifest = verify_engine(PINS)
    check('independent executable/profile/mapping closure', manifest['engine_id'] == PINS.engine_id)
    context = evidence(RUN / 'context-R03.json')
    check('original full R03 criteria retained', {o['id'] for o in context['obligations']} == {'U1','U2','U3','U4','U5'})
    for binding in context['source_bindings']:
        raw = pinned(binding)
        if binding['path'].endswith('.json'):
            source = parse(raw)
            for field in ('files', 'source_files', 'source_bindings'):
                for row in source.get(field, []):
                    if isinstance(row, dict) and {'path','sha256'} <= row.keys():
                        pinned(row)
    evidence(RUN / 'CONTEXT-R03.md')
    for binding in parse(original(manifest['parent_binding']))['files']:
        pinned(binding)
    evidence(ROOT / 'implementation/lab-runtime/v2/tests/test_runtime.py')
    raw, edits, parent = adapted_source()
    adaptation = evidence(ATTEMPT / 'full-runtime/adaptation.json')
    check('all original test bodies and assertions retained',
        (ATTEMPT / 'full-runtime/adapted-test-runtime.py').read_text() == raw
        and adaptation['edits'] == edits and adaptation['original_source_binding'] == parent
        and adaptation['assertions_changed'] is False
        and adaptation['adapted_source_sha256'] == sha(raw.encode()))
    regression = parse((ATTEMPT / 'regression.stdout').read_bytes())
    check('all 38 predecessor tests passed', regression['result'] == 'PASS'
        and regression['tests'] == 38 and regression['failures'] == regression['errors'] == 0)
    guardlog = (ATTEMPT / 'guards.stderr').read_text()
    guards = re.findall(r'^(test_\S+) \(([^\n]+)\) \.\.\. ok$', guardlog, re.MULTILINE)
    declared = sum(isinstance(n, ast.FunctionDef) and n.name.startswith('test_')
        for n in ast.walk(ast.parse((HERE / 'test_coupling.py').read_text())))
    check('all 35 coupling guards passed', len(guards) == declared == 35
        and re.search(r'Ran 35 tests in [0-9.]+s\n\nOK\n', guardlog) is not None)
    for name, _ in guards:
        checks.append({'suite': 'coupling-guards', 'test': name, 'result': 'PASS'})
    episodes = []
    totals = Counter()
    for domain, attempt in [('engineering','0001'), ('research','0001'), ('product','0002')]:
        directory = EXAMPLES / 'attempts' / attempt / domain
        result = evidence(directory / 'result.json')
        expected = evidence(directory / 'expected-replay.json')
        witnesses = evidence(directory / 'original-source-witnesses.json')
        proposal = evidence(directory / 'proposal.json')
        approval = evidence(directory / 'approval.json')
        review = evidence(directory / 'review.json')
        application = evidence(directory / 'application.json')
        archive_value = evidence(directory / 'branch.snapshot')
        archive_value = parse(archive_value)
        cold = evidence(ATTEMPT / 'cold' / (domain + '.stdout'))
        cold = parse(cold)
        check(domain + ': actual cold parity', cold['result'] == 'PASS'
            and cold['signed_transaction_replay'] and cold['projection_parity']
            and cold['original_domain_effects_reexecuted'] == 0
            and not cold['keys_restored'] and not cold['Session_memory_restored'])
        check(domain + ': exact independently pinned archive', expected['engine_pins'] == asdict(PINS)
            and expected['source_binding'] == bind(directory / 'branch.snapshot'))
        with tempfile.TemporaryDirectory(prefix='cal-R03-proof-read-') as temp:
            data = restore_archive(directory / 'branch.snapshot', expected['source_binding']['sha256'], Path(temp) / 'store', PINS)
            with engine(PINS) as handle:
                check(domain + ': exact signed projection and transaction parity',
                    handle.common.digest(data['projection']) == expected['projection_sha256']
                    and [handle.common.digest(tx) for tx in data['transactions']] == expected['transaction_sha256s'])
                check(domain + ': single signed application', len(data['transactions']) == 1
                    and data['transactions'][0]['proposal'] == proposal
                    and data['transactions'][0]['approval'] == approval
                    and data['transactions'][0]['digest'] == application['transaction_digest'])
                relation = data['projection']['subjects'][expected['relation_ref']]['record']
                handle.operations.validate_relation(relation, data['projection'])
                rejection = frozen_kind_rejection(handle, data['projection'], relation)
                check(domain + ': frozen mismatch retained and candidate validates', rejection == result['frozen_rejection'])
                views = [handle.mapping.explain(handle.sources.resolve(data['projection']['subjects'], e['version_ref']), data['projection'])
                    for e in (relation['payload']['source'], relation['payload']['target'])]
                check(domain + ': raw and represented axes remain distinct', views == result['endpoint_views'] == expected['endpoint_views']
                    and all(v['raw_subject_rewritten'] is False for v in views)
                    and views[1]['carrier_kind'] == ('product-identity' if domain == 'product' else 'project-identity')
                    and views[1]['represented_endpoint_kind'] == ('product' if domain == 'product' else 'project'))
                check(domain + ': mapping shown before signature', review['endpoint_mapping_binding'] == manifest['mapping_binding']
                    and review['target_count'] == len(proposal['targets']))
                for witness in witnesses['selected_records']:
                    selected = next(t for t in proposal['targets'] if t['version_ref'] == witness['version_ref'])
                    check(domain + ': original target ' + witness['version_ref'],
                        data['projection']['subjects'][witness['version_ref']]['record'] == selected['record']
                        and data['projection']['subjects'][witness['version_ref']]['kind'] == witness['kind'])
                    if witness['source_binding'] is not None:
                        source_raw = pinned(witness['source_binding'])
                        check(domain + ': source structure unchanged ' + witness['version_ref'],
                            parse(source_raw) == selected['record']
                            and handle.common.digest(selected['record']) == witness['original_structural_sha256'])
                effects = data['transactions'][0]['consequences']['admission_transaction']['payload']['admission_targets']
                counts = Counter(e['effect_kind'] for e in effects)
                check(domain + ': exact local effects counted', len(effects) == len(proposal['targets'])
                    and [(e['effect_kind'], e['target_ref']) for e in effects]
                    == [(t['operation'], t['version_ref']) for t in proposal['targets']])
                totals.update(counts)
                tx_bytes = base64.b64decode(archive_value['files']['transactions/0000000001.json']['base64_original_bytes'], validate=True)
                episodes.append({'domain': domain, 'source_binding': expected['source_binding'],
                    'signed_transactions': 1, 'target_effects': len(effects), 'effect_counts': dict(counts),
                    'original_signed_transaction_file_sha256': sha(tx_bytes),
                    'transaction_structural_digest': data['transactions'][0]['digest'],
                    'embedded_record_bindings': result['exact_targets'],
                    'original_source_file_bytes_unchanged': True,
                    'embedded_source_record_structures_unchanged': True,
                    'embedding_serialization': 'Inherited canonical JSON; original standalone source bytes are not embedded verbatim.'})
        check(domain + ': cleanup and external boundaries', result['result'] == 'PASS'
            and result['owned_store_and_key_removed'] and result['fixture_signature_verified']
            and result['idempotent_retry'] and not result['private_key_exported']
            and not result['Session_memory_exported'] and result['actual_owner_outcome'] is None
            and result['original_domain_cases_reexecuted'] == 0
            and not result['canonical_admission'] and not result['runtime_activation'])
        for axis in ('semantic', 'governance'):
            check(domain + ': ' + axis + ' history advances once', result[axis + '_history_before'] == 5
                and result[axis + '_history_after'] == 6)
        if witnesses['case_binding'] is not None:
            pinned(witnesses['case_binding'])
    check('three branches, eight local target effects', dict(totals) == {'admit': 5, 'revise': 3})
    for tree in (HERE, EXAMPLES):
        for path in tree.rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts:
                evidence(path)
    for binding in files.values():
        original(binding)
    verify_engine(PINS)
    receipt = {'schema_version': 'lab-R03-signed-coupling-proof/v1-candidate',
        'task': 'R03', 'result': 'PASS', 'task_complete': False,
        'authority_effect': 'none', 'actual_owner_outcome': None,
        'claim_ceiling': 'Exact signed Project/Product coupling candidate proof only; full operator/API/SQLite, W07 and human value pilot remain incomplete.',
        'verified_obligation_ids': ['U1','U2','U5'], 'checks': checks,
        'tests': 73, 'coupling_guards': 35, 'unchanged_predecessor_tests': 38,
        'cold_episode_replays': 3, 'episodes': episodes, 'signed_transactions': 3,
        'local_target_effects': 8, 'local_admits': 5, 'local_revisions': 3,
        'source_effects_applied_semantics': 'Zero original repository/canonical source effects. The isolated fixture target effects above occurred and are retained.',
        'source_record_bytes_preserved_semantics': 'Original source files unchanged; embedded parsed bodies equal. Inherited canonical JSON serialization differs from standalone file byte encoding.',
        'canonical_effects_applied': 0, 'original_domain_cases_reexecuted': 0,
        'frozen_runtime_changed_files': 0, 'engine_pins': asdict(PINS),
        'preserved_failed_observations': ['Engineering evidence-writing error recovered from original signed archive without another transaction.',
            'First Product fixture failed before proposal/signature; exact top-level product_ref selector corrected in a separately retained successor fixture.'],
        'remaining_obligations': ['U3: Complete operator CLI and authenticated stdio with state facets/currentness, target diff/effects/evidence, deterministic receipts and why-path.',
            'U4: Implement and verify all 34 API operations and required SQLite/query integrations.',
            'W07: Complete separately identified Method/reference and full case integration; no unqualified global merge.',
            'S02/R08: Exact final members, contract reconciliation, actual owner outcome and human value pilot.'],
        'source_drift': [], 'files': sorted(files.values(), key=lambda b: b['path']),
        'duration_seconds': time.perf_counter() - started}
    emit(output, receipt)
    print(json.dumps({'result': 'PASS', 'task': 'R03', 'task_complete': False,
        'tests': 73, 'cold_episode_replays': 3, 'local_target_effects': 8,
        'files': len(files), 'receipt': bind(output), 'authority_effect': 'none'}, sort_keys=True))


if __name__ == '__main__':
    main()
