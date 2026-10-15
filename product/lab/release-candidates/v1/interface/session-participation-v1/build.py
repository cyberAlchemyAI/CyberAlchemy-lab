"""Materialize real sources and apply exact proposals only in a fresh owned store."""
from dataclasses import asdict
import base64
import copy
from datetime import datetime, timezone, timedelta
import tempfile
import time
from base import *
import records


def proposal(data, identity, targets):
    c = data['config']
    return {'schema_version': 'lab-runtime-proposal/v1', 'proposal_id': identity,
        'expected_head': data['head']['transaction_digest'], 'source_snapshot_digest': c['source_snapshot_digest'],
        'scope_ref': c['scope_ref'], 'policy_ref': c['policy_ref'], 'challenge_route': c['challenge_route'],
        'schemas': {}, 'targets': targets}


def archive(store, pins):
    data = store.replay(require_current=True)
    names = ['config.json', 'baseline.json', 'HEAD.json'] + [f'transactions/{i:010d}.json' for i in range(data['head']['sequence'] + 1)]
    files = {name: {'sha256': sha((store.path / name).read_bytes()),
        'base64_original_bytes': base64.b64encode((store.path / name).read_bytes()).decode()} for name in names}
    return {'schema_version': 'lab-owned-participation-archive/v1-candidate', 'engine_pins': asdict(pins),
        'config_sha256': files['config.json']['sha256'], 'baseline_snapshot_digest': data['baseline']['snapshot_digest'],
        'expected_head': data['head']['transaction_digest'], 'files': files, 'private_keys_exported': False,
        'historical_provenance_protection': 'private-original-custody-not-public-package',
        'Session_memory_rehydrated': False, 'authority_effect': 'none', 'actual_owner_outcome': None}


def build(pin):
    verify_source(pin);out = HERE / 'packages/0001'
    require(not out.exists(), 'refuse participation package overwrite');out.mkdir(parents=True, mode=0o700)
    started = time.monotonic();pins = selected_pins()
    with tempfile.TemporaryDirectory(prefix='cal-R03-fresh-participation-') as temp, loader.engine(pins) as handle:
        owned = Path(temp);store, key = handle.create_owned(owned, 'R03-fresh-participation-0001', selected_project_scope=True)
        try:
            before = store.replay(require_current=True)
            project = [s for s in before['projection']['subjects'].values() if s['identity'] == before['config']['scope_ref'] and s['effective_state'] == 'admitted-current']
            require(len(project) == 1, 'unique source Project unavailable');old = project[0]
            project_body = copy.deepcopy(old['record'])
            new_version = old['identity'] + '@' + project_body['version']
            require(new_version != old['version_ref'], 'selected Project setup must correct only the explicit revision reference')
            setup_target = {'category': 'artifact-instance', 'operation': 'revise', 'version_ref': new_version,
                'carrier_ref': old['carrier_ref'], 'record': project_body, 'predecessor_ref': old['version_ref'],
                'decision_ref': 'decision:R03-fresh-participation:project-source-setup', 'contract': None}
            setup = proposal(before, 'R03-fresh-project-source-setup', [setup_target])
            emit(out / 'project-setup-proposal.json', setup)
            setup_approval = store.authorize(setup, key);emit(out / 'project-setup-approval.json', setup_approval)
            setup_application = store.apply(setup, setup_approval);emit(out / 'project-setup-application.json', setup_application)
            before = store.replay(require_current=True)
            items = records.targets(before['projection'], before['config']['scope_ref'])
            require(len(items) == 19, 'complete ten sources/nine Typed Relations required')
            index = []
            for i, target in enumerate(items):
                raw = encoded(target['record']);path = out / ('artifacts/' + str(i).zfill(2) + '.json')
                emit(path, None, raw=raw)
                require(raw == handle.common.encoded(target['record']), 'incoming original source bytes differ from legacy declared transaction encoding')
                index.append({'kind': target['record'].get('kind', before['projection']['contracts'][target['carrier_ref']]['semantic_kind']),
                    'version_ref': target['version_ref'], 'carrier_ref': target['carrier_ref'], 'original_binding': binding(path),
                    'encoding': 'original-file-equals-declared-inherited-transaction-encoding'})
            emit(out / 'record-index.json', index)
            p = proposal(before, 'R03-fresh-reader-participation', items);emit(out / 'proposal.json', p)
            post, cores = handle.operations.prepare(before['projection'], p, before['head']['transaction_digest'], before['config'])
            require(before['projection'] != post and len(cores) == 19, 'pure prepare must stage nineteen independent cores')
            review = store.review(p);emit(out / 'review.json', review)
            approval = store.authorize(p, key);emit(out / 'approval.json', approval)
            applied = store.apply(p, approval);emit(out / 'application.json', applied)
            retry = store.apply(p, approval);emit(out / 'retry.json', retry)
            require(retry['idempotent'] and retry['transaction_digest'] == applied['transaction_digest'], 'exact retry must not redispatch')
            after = store.replay(require_current=True)
            for target, row in zip(items, index):
                s = after['projection']['subjects'][target['version_ref']]
                require(s['effective_state'] == 'local-admitted-current' and s['record'] == target['record'], 'actual source postimage differs')
                require(s['source']['sha256'] == row['original_binding']['sha256'], 'actual signed record identity lost original bytes')
                if target['category'] == 'typed-relation': handle.operations.validate_relation(s['record'], after['projection'])
            a = after['projection']['subjects'][records.ASSIGNMENT + '@' + records.VERSION]['record']['payload']
            require(a['eligible_agent_ref'] == records.PROFILE + '@' + records.VERSION, 'fresh Assignment incorrectly binds an old instance')
            state = after['projection']['state']
            require(state['payload']['project_ref'] == after['config']['scope_ref'], 'generated Project State scope differs')
            expected = {'schema_version': 'lab-owned-participation-expected-replay/v1-candidate',
                'engine_pins': asdict(pins), 'projection_sha256': handle.common.digest(after['projection']),
                'transaction_sha256s': [handle.common.digest(t) for t in after['transactions']],
                'config_sha256': sha((store.path / 'config.json').read_bytes()), 'baseline_snapshot_digest': after['baseline']['snapshot_digest'],
                'expected_head': after['head']['transaction_digest'], 'selected_source_record_index': index,
                'current_Project_State_ref': state['node_id'], 'authority_effect': 'none', 'actual_owner_outcome': None}
            emit(out / 'expected-replay.json', expected)
            stamp = datetime.now(timezone.utc)
            emit(out / 'period.json', {'schema_version': 'lab-owned-absolute-participation-period/v1-candidate',
                'period_ref': records.PERIOD, 'not_before': stamp.isoformat(), 'expires_at': (stamp + timedelta(hours=24)).isoformat(),
                'principal_ref': records.PRINCIPAL, 'assignment_version_ref': records.ASSIGNMENT + '@' + records.VERSION,
                'authority_effect': 'none', 'actual_owner_outcome': None,
                'claim_ceiling': 'Actual bounded construction period only; independent current host permission remains required.'})
            verify_source(pin);outcome = {'result': 'PASS', 'authored_current_artifacts': 10, 'authored_current_typed_relations': 9,
                'independent_participation_decision_cores': 19, 'signed_transactions': 2, 'fresh_Profile_eligible_Assignment': True,
                'private_keys_exported': False, 'Session_memory_rehydrated': False, 'active_Agents_created': 0,
                'public_API_operations_added': 0, 'canonical_effects_applied': 0, 'source_effects_applied': 0,
                'authority_effect': 'none', 'actual_owner_outcome': None, 'human_pilot_outcome': None,
                'signature_basis': 'Independently generated controlled development signer for this owned candidate store; no human/canonical owner response.',
                'duration_seconds': time.monotonic() - started}
        except Exception as error:
            emit(out / 'failure.json', {'result': 'FAIL', 'error_class': type(error).__name__, 'reason': str(error),
                'authority_effect': 'none', 'actual_owner_outcome': None})
            raise
        finally:
            emit(out / 'branch.snapshot', archive(store, pins))
    require(not owned.exists(), 'owned source store/key remain')
    outcome['owned_store_and_key_removed'] = True;emit(out / 'build-result.json', outcome)
    files = [binding(p) for p in sorted(out.rglob('*')) if p.is_file()]
    manifest = {'schema_version': 'lab-owned-participation-package/v1-candidate', 'files': files,
        'source_manifest_binding': binding(HERE / 'source-manifest.json'), 'archive_binding': binding(out / 'branch.snapshot'),
        'expected_replay_binding': binding(out / 'expected-replay.json'), 'period_binding': binding(out / 'period.json'),
        'visibility': 'private-candidate-original-custody', 'public_package_export_allowed': False,
        'authority_effect': 'none', 'actual_owner_outcome': None}
    emit(out / 'manifest.json', manifest)
    print(json.dumps({'result': 'PASS', 'package_binding': binding(out / 'manifest.json'), 'records': 19}), flush=True)


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser();p.add_argument('--source-sha256', required=True);a = p.parse_args();build(a.source_sha256)
