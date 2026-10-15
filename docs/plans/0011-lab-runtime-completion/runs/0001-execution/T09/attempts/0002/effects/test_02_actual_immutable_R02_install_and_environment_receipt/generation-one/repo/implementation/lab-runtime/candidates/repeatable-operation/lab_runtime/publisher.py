"""Reusable immutable repository publisher with separate owner authority.

The bundle directory rename is the commit point. Managed mirrors/current lookup
are repairable projections and never constitute another owner decision.
"""
from __future__ import annotations
import copy
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import fcntl
import os
from pathlib import Path
import stat

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from jsonschema import Draft202012Validator

from .common import RuntimeFault, byte_digest, digest, encoded, load, loads, require
from .promotion import (RepositoryAuthority, prepare_promotion, public_material, relative,
                        validate_promotion_record)
from .sources import freshness, validate_histories
from .transition import _closed, _date, _file_bytes, _publish

SCHEMA = Path(__file__).resolve().parents[1] / 'schemas/promotion.schema.json'


def verify_generator(review):
    """No mutable current-code substitution for the reviewed executable closure."""
    package = Path(__file__).resolve().parents[1]; repository = package.parents[3]
    actual = {p.relative_to(repository).as_posix() for p in (package / 'lab_runtime').rglob('*.py') if '__pycache__' not in p.parts}
    actual.add((package / 'lab.py').relative_to(repository).as_posix())
    expected = {r['path'] for r in review['generator_binding']['files']}
    require(actual == expected, 'reviewed publication generator closure changed')
    for row in review['generator_binding']['files']:
        require(byte_digest(_file_bytes(repository / row['path'])) == row['sha256'], 'reviewed publication generator bytes changed')


@dataclass(frozen=True)
class PublicationPins:
    review_digest: str
    bundle_sha256: str
    authority_sha256: str


def owner_response(prepared, authority, private_key, *, approved_at=None):
    """One separately scoped signed response covering all independent cores.

    This is a candidate local key adapter. An authenticated conversation adapter
    must bind its real owner message at C09/S02 before actual R08 application;
    no helper fabricates a human response or derives authority from local state.
    """
    review = prepared['review']; require(review['authority'] == authority.core(), 'repository authority differs from review')
    key_path = Path(private_key)
    require(not key_path.is_symlink() and stat.S_IMODE(key_path.stat().st_mode) == 0o600, 'repository approval key must be mode 0600')
    require(not key_path.resolve().is_relative_to(Path(authority.repository_root)), 'private repository approval key must stay outside repository')
    private = serialization.load_pem_private_key(_file_bytes(key_path), password=None)
    require(isinstance(private, Ed25519PrivateKey), 'Ed25519 repository approval key required')
    require(private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw).hex() == authority.public_key, 'independent repository owner key mismatch')
    when = approved_at or datetime.now(timezone.utc).isoformat()
    require(_date(when) <= datetime.now(timezone.utc) < _date(authority.expires_at), 'repository authority expired or response in future')
    core = {'schema_version': 'lab-repository-owner-response/v1-candidate', 'principal_ref': authority.principal_ref,
        'authority_sha256': digest(authority.core()), 'review_digest': digest(review),
        'decision_core_sha256s': review['core_sha256s'], 'selected_outcome': 'admit-exact-independent-repository-effects',
        'approved_at': when, 'authorization_mechanism': 'independent-repository-key-adapter',
        'human_conversation_outcome': None}
    return {**core, 'signature': private.sign(encoded(core)).hex()}


def verify_response(response, review, authority, *, live=False):
    _closed(response, ['schema_version', 'principal_ref', 'authority_sha256', 'review_digest',
                       'decision_core_sha256s', 'selected_outcome', 'approved_at', 'authorization_mechanism',
                       'human_conversation_outcome', 'signature'])
    require(response['schema_version'] == 'lab-repository-owner-response/v1-candidate'
        and response['principal_ref'] == authority.principal_ref
        and response['authority_sha256'] == digest(authority.core())
        and response['review_digest'] == digest(review)
        and response['decision_core_sha256s'] == review['core_sha256s']
        and response['selected_outcome'] == 'admit-exact-independent-repository-effects'
        and response['authorization_mechanism'] == 'independent-repository-key-adapter'
        and response['human_conversation_outcome'] is None, 'response does not cover exact independent repository effects')
    when = _date(response['approved_at'])
    require(when < _date(authority.expires_at), 'response outside repository authority interval')
    if live: require(when <= datetime.now(timezone.utc) < _date(authority.expires_at), 'repository authority expired/future response')
    try:
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(authority.public_key)).verify(
            bytes.fromhex(response['signature']), encoded({k:v for k,v in response.items() if k != 'signature'}))
    except (InvalidSignature, ValueError, TypeError) as exc:
        raise RuntimeFault('invalid independent repository owner signature') from exc


def _carrier(context, kind):
    refs = [r for r,c in context['contracts'].items() if c['semantic_kind'] == kind and c['lifecycle_state'] == 'admitted-current']
    require(len(refs) == 1, 'ambiguous current consequence carrier'); return refs[0]


def _record(context, authority, kind, node_id, title):
    r = copy.deepcopy(context['templates'][kind])
    r.update(node_id=node_id, name=title, owner_ref=dict(authority.owner_roles).get('artifact-instance', 'role:repository-owner'),
        scope_ref=authority.scope_ref, evidence_refs=[authority.bundle_path + '/authorization.json'],
        challenge_route=authority.challenge_route, claim_ceiling=authority.claim_ceiling,
        authority_effect='none', lifecycle_state='active', successor_refs=[])
    return r


def render_bundle(prepared, response, authority):
    """Deterministic actual carrier postimages; stable cores exclude these hashes."""
    review = prepared['review']; verify_response(response, review, authority); verify_generator(review)
    validate = list(Draft202012Validator(load(SCHEMA)).iter_errors(review))
    require(not validate, 'invalid promotion review: ' + '; '.join(e.message for e in validate[:3]))
    files = dict(prepared['materials'])
    require(review['material_sha256s'] == {p:byte_digest(raw) for p,raw in files.items()}, 'reviewed material closure changed')
    context = loads(files['validation/context.json']); identities = loads(files['validation/identities.json'])
    root = authority.bundle_path; token = authority.bundle_id
    db = 'decision-bundle:' + token; cp = 'decision-checkpoint:' + token
    boundary = 'authority-boundary:' + token; txid = 'admission-transaction:' + token
    receipt_ref = root + '/receipts/application.json'; auth_path = root + '/authorization.json'
    cores = review['independent_cores']; core_refs = [c['decision_ref'] for c in cores]
    records, decisions, scopes = {}, [], []
    for i,c in enumerate(cores):
        files[f'decision-cores/{i:04d}.json'] = encoded(c)
        dsid = 'decision-scope:' + token + ':' + str(i)
        d = _record(context, authority, 'decision', c['decision_ref'], 'Exact repository ' + c['effect_kind'])
        d.update(owner_ref=c['owner_ref'])
        d['payload'].update(decision_maker_ref=authority.principal_ref, declared_effect_refs=[c['effect_kind']],
            evidence_basis_refs=[auth_path], selected_outcome=c['selected_outcome'], subject_refs=[c['target_ref']])
        d['relation_refs'] = [{'relation_kind_ref': 'relation.member-of', 'direction': 'source', 'counterpart_kind': 'decision-bundle', 'counterpart_ref': db}]
        scope = _record(context, authority, 'decision-scope', dsid, 'Exact independent repository Decision scope')
        scope.update(owner_ref=c['owner_ref']); scope['payload'].update(permitted_effects=[c['effect_kind']],
            subject_kind_refs=[review['targets'][i]['kind']], subject_refs=[c['target_ref']],
            excluded_effects=['runtime-activation', 'service-start', 'external-publication', 'deployment'])
        scope['relation_refs'] = [{'relation_kind_ref': 'relation.scopes-authority-over', 'direction': 'target', 'counterpart_kind': 'authority-boundary', 'counterpart_ref': boundary}]
        records[f'instances/governance/decision-{i:04d}.json'] = d
        records[f'instances/governance/decision-scope-{i:04d}.json'] = scope
        decisions.append(d); scopes.append(scope)
    b = _record(context, authority, 'authority-boundary', boundary, 'Independently authorized repository boundary')
    b['payload'].update(accountable_principal_ref=authority.principal_ref, owner_role_ref='role:repository-owner',
        authority_scope_ref=authority.scope_ref, allowed_effect_kinds=[c['effect_kind'] for c in cores],
        challenge_route_ref=authority.challenge_route, effective_period='exact-review:' + digest(review))
    b['relation_refs'] = [{'relation_kind_ref': 'relation.scopes-authority-over', 'direction': 'source', 'counterpart_kind': 'decision-scope', 'counterpart_ref': s['node_id']} for s in scopes]
    records['instances/governance/authority-boundary.json'] = b
    bundle = _record(context, authority, 'decision-bundle', db, 'One response covering independent repository Decisions')
    bundle['payload'].update(bundle_digest=digest(cores), checkpoint_ref=cp, all_targets_materialized=True,
        ordered_decisions=[{'decision_ref': c['decision_ref'], 'decision_core_sha256': byte_digest(encoded(c)),
            'owner_ref': c['owner_ref'], 'scope_ref': scopes[i]['node_id'], 'effect_kind': c['effect_kind'],
            'selected_outcome': c['selected_outcome'], 'target_refs': [c['target_ref']],
            'target_digests': [{'target_ref': c['target_ref'], 'sha256': c['target_sha256']}]} for i,c in enumerate(cores)])
    bundle['relation_refs'] = [{'relation_kind_ref': 'relation.member-of', 'direction': 'target', 'counterpart_kind': 'decision', 'counterpart_ref': d['node_id']} for d in decisions]
    records['instances/governance/decision-bundle.json'] = bundle
    checkpoint = _record(context, authority, 'decision-checkpoint', cp, 'Resolved exact repository owner response')
    checkpoint['payload'].update(decision_bundle_ref=db, workflow_instance_ref='repository-promotion:' + token,
        workflow_profile_ref='candidate-profile:exact-repository-publication/v1', resolved_preference_ref=None,
        opened_at=response['approved_at'], closed_at=response['approved_at'])
    records['instances/governance/decision-checkpoint.json'] = checkpoint
    old_state = context['state']; stateid = 'project-state:' + token
    state = _record(context, authority, 'project-state', stateid, 'Project State after exact repository transaction')
    state['payload'].update(cursor='repository-admission:' + token,
        decision_refs=list(dict.fromkeys(old_state['payload']['decision_refs'] + core_refs)),
        artifact_refs=list(dict.fromkeys(old_state['payload']['artifact_refs'] + [root + '/' + t['record_path'] for t in review['targets']])),
        state_digest='sha256:' + digest({'predecessor': old_state['payload']['state_digest'], 'review': digest(review), 'cores': review['core_sha256s']}))
    state['relation_refs'] = [{'relation_kind_ref': 'relation.member-of', 'direction': 'source', 'counterpart_kind': 'project', 'counterpart_ref': state['payload']['project_ref']},
        {'relation_kind_ref': 'relation.successor-of', 'direction': 'source', 'counterpart_kind': 'project-state', 'counterpart_ref': old_state['node_id']},
        {'relation_kind_ref': 'relation.materializes-consequence', 'direction': 'target', 'counterpart_kind': 'admission-transaction', 'counterpart_ref': txid}]
    records['instances/project-state.json'] = state
    history = copy.deepcopy(context['histories'])
    sem = history['project-semantic-event-history']['payload']; gov = history['project-governance-event-history']['payload']
    cursor = len(sem['events']) + 1; g_cursor = len(gov['events']) + 1
    event = {'event_id': 'project-semantic-event:' + token, 'cursor': cursor,
        'previous_event_digest': sem['events'][-1]['event_digest'], 'change_kind': 'exact-repository-promotion',
        'predecessor_state_ref': old_state['node_id'], 'predecessor_state_digest': old_state['payload']['state_digest'],
        'resulting_state_ref': stateid, 'resulting_state_digest': state['payload']['state_digest'],
        'material_refs': [{'path': root + '/' + t['record_path'], 'sha256': t['record_sha256']} for t in review['targets']],
        'record_ref': root + '/review.json', 'semantic_summary': 'Exact independently reviewed repository target effects; no runtime activation.'}
    event['event_digest'] = digest(event)
    governance_event = {'event_id': 'project-governance-event:' + token, 'governance_cursor': g_cursor,
        'previous_event_digest': gov['events'][-1]['event_digest'],
        'semantic_event_ref': {'semantic_event_id': event['event_id'], 'semantic_event_digest': event['event_digest'], 'semantic_cursor': cursor},
        'decision_ref': db, 'authorization_ref': auth_path, 'authorization_sha256': byte_digest(encoded(response)),
        'policy_ref': authority.policy_ref, 'challenge_contract_ref': authority.challenge_route,
        'upstream_governance_evidence_refs': core_refs, 'record_ref': root + '/review.json',
        'governance_summary': 'One separate exact repository owner response for independent stable cores.'}
    governance_event['event_digest'] = digest(governance_event)
    for kind, e, watermark in [('project-semantic-event-history', event, 'latest_cursor'), ('project-governance-event-history', governance_event, 'latest_governance_cursor')]:
        files['prior/' + kind + '.json'] = encoded(context['histories'][kind])
        h = history[kind]; h.update(owner_ref='role:repository-owner', scope_ref=authority.scope_ref, evidence_refs=[auth_path], claim_ceiling=authority.claim_ceiling)
        h['payload']['events'].append(e); h['payload'][watermark] = len(h['payload']['events'])
        h['payload']['chain_digest'] = digest([x['event_digest'] for x in h['payload']['events']])
        h['relation_refs'] = [{'relation_kind_ref': 'relation.materializes-consequence', 'direction': 'target', 'counterpart_kind': 'admission-transaction', 'counterpart_ref': txid}]
        records['instances/' + kind + '.json'] = h
    files['prior/project-state.json'] = encoded(old_state); validate_histories(history)
    index = {'schema_version': 'lab-selected-repository-target-index/v1-candidate', 'authority_effect': 'none',
        'coverage': 'selected authored targets only; not complete repository catalog', 'replay_source': False,
        'entries': [{'version_ref': t['version_ref'], 'identity_ref': t['identity'], 'category': t['category'],
            'semantic_kind': t['kind'], 'carrier_type_ref': t['carrier_ref'], 'decision_ref': t['decision_ref'],
            'path': root + '/' + t['record_path'], 'sha256': t['record_sha256'],
            'predecessor_ref': t['predecessor_ref'], 'lifecycle_state': 'withdrawn' if t['operation'] == 'withdraw' else 'admitted-current'} for t in review['targets']]}
    files['instance-index.json'] = encoded(index)
    generated = _record(context, authority, 'generated-output', 'generated-output:' + token, 'Selected target index')
    generated['payload'].update(generator_ref='generator-package:' + digest(review['generator_binding']),
        input_refs=[t['version_ref'] for t in review['targets']], output_digest='sha256:' + byte_digest(files['instance-index.json']),
        reproducibility_receipt_ref=receipt_ref)
    generated['relation_refs'] = [{'relation_kind_ref': 'relation.materializes-consequence', 'direction': 'target', 'counterpart_kind': 'admission-transaction', 'counterpart_ref': txid}]
    records['instances/generated-output.json'] = generated
    transaction = _record(context, authority, 'admission-transaction', txid, 'Exact repository Admission Transaction')
    transaction['payload'].update(project_ref=state['payload']['project_ref'], decision_bundle_ref=db,
        decision_core_refs=[{'decision_ref': c['decision_ref'], 'decision_core_sha256': byte_digest(encoded(c)), 'selected_outcome': c['selected_outcome']} for c in cores],
        review_bundle_digest=digest(review), resolved_bundle_digest=digest(cores), authorization_evidence_ref=auth_path,
        authorization_evidence_sha256=byte_digest(encoded(response)), input_state_ref=old_state['node_id'], input_state_sha256=byte_digest(encoded(old_state)),
        admission_targets=[{'target_ref': c['target_ref'], 'target_sha256': c['target_sha256'], 'effect_kind': c['effect_kind']} for c in cores],
        deterministic_consequences=[{'consequence_kind': r['kind'], 'consequence_ref': r['node_id'], 'output_sha256': byte_digest(encoded(r)), 'declared_input_ref': db} for r in [state, *history.values(), generated]],
        application_state='applied', application_receipt_ref=receipt_ref, rollback_ref='repository-recovery:immutable-bundle:' + token,
        runtime_activations=0, external_effect_refs=[])
    transaction['relation_refs'] = [{'relation_kind_ref': 'relation.governed-by', 'direction': 'source', 'counterpart_kind': 'policy', 'counterpart_ref': authority.policy_ref}]
    records['instances/governance/admission-transaction.json'] = transaction
    # Stage all generated subjects before validating exact-version connections.
    subjects = copy.deepcopy(context['subjects'])
    old_state_entry = next(e for e in subjects.values() if e['identity'] == old_state['node_id'])
    def entry(record, path):
        version = record['node_id'] + '@repository.' + token
        return version, {'identity': record['node_id'], 'version_ref': version, 'category': 'typed-relation' if record['kind'] == 'typed-relation' else 'artifact-instance',
            'kind': record['kind'], 'carrier_ref': _carrier(context, record['kind']), 'effective_state': 'admitted-current',
            'record': record, 'decision_ref': core_refs, 'source': {'path': root + '/' + path, 'sha256': byte_digest(encoded(record))}}
    for path, r in records.items():
        if r['kind'] in ['project-state', 'project-semantic-event-history', 'project-governance-event-history']:
            for old in subjects.values():
                if old['identity'] == r['node_id'] or (r['kind'] == 'project-state' and old['kind'] == 'project-state'):
                    old['effective_state'] = 'admitted-historical'
        v,e = entry(r, path); subjects[v] = e
    project = next(e for e in subjects.values() if e['identity'] == state['payload']['project_ref'])
    def endpoint(record):
        e = next(e for e in subjects.values() if e['record'] is record)
        return {'ref': e['identity'], 'kind': e['kind'], 'version_ref': e['version_ref']}
    connections = [(endpoint(state), {'ref': old_state_entry['identity'], 'kind': old_state_entry['kind'], 'version_ref': old_state_entry['version_ref']}, 'relation.successor-of', {'succession_effect': 'continues-and-supersedes-current-state'}),
        (endpoint(state), {'ref': project['identity'], 'kind': project['kind'], 'version_ref': project['version_ref']}, 'relation.member-of', {'membership_role': 'durable-project-state'})]
    for result in [state, *history.values(), generated]:
        connections.append((endpoint(transaction), endpoint(result), 'relation.materializes-consequence', {
            'consequence_role': result['kind'], 'output_digest': 'sha256:' + byte_digest(encoded(result)), 'application_receipt_ref': receipt_ref}))
    for i,(source, target, predicate, qualifiers) in enumerate(connections):
        r = _record(context, authority, 'typed-relation', 'typed-relation:' + token + ':' + str(i), 'Deterministic ' + predicate)
        r['schema_version'] = context['contracts'][_carrier(context, 'typed-relation')]['instance_discriminator']['value']
        r['payload'].update(relation_kind_ref=predicate, source=source, target=target, qualifiers=qualifiers,
            relation_lifecycle_state='active', relation_evidence_refs=[auth_path])
        records[f'instances/typed-relations/{i:04d}.json'] = r
        v,e = entry(r, f'instances/typed-relations/{i:04d}.json'); subjects[v] = e
    for path, record in records.items():
        carrier = _carrier(context, record['kind']); category = 'typed-relation' if record['kind'] == 'typed-relation' else 'artifact-instance'
        validate_promotion_record(record, category, carrier, context, identities, subjects)
        files[path] = encoded(record)
    for t in review['targets']:
        validate_promotion_record(loads(files[t['record_path']]), t['category'], t['carrier_ref'], context, identities, subjects)
    receipt = {'schema_version': 'lab-repository-publication-receipt/v1-candidate', 'bundle_id': token,
        'review_digest': digest(review), 'authorization_sha256': byte_digest(encoded(response)),
        'decision_core_sha256s': review['core_sha256s'], 'semantic_cursor': cursor, 'governance_cursor': g_cursor,
        'outputs': [{'path': p, 'sha256': byte_digest(raw)} for p,raw in sorted(files.items()) if p.startswith(('targets/', 'instances/'))],
        'runtime_activations': 0, 'external_effects': 0, 'commit_point': 'atomic-no-replace-immutable-bundle-directory'}
    files['receipts/application.json'] = encoded(receipt)
    files['review.json'] = encoded(review); files['authorization.json'] = encoded(response)
    manifest = {'schema_version': 'lab-immutable-repository-bundle/v1-candidate', 'bundle_id': token,
        'review_digest': digest(review), 'authority_sha256': digest(authority.core()),
        'current_project_state_ref': stateid, 'current_project_state_sha256': byte_digest(files['instances/project-state.json']),
        'decision_refs': core_refs, 'decision_checkpoint_ref': cp, 'runtime_activations': 0, 'external_effect_refs': [],
        'files': {p:byte_digest(raw) for p,raw in sorted(files.items())}}
    files['bundle.json'] = encoded(manifest)
    return files, manifest


def verify_bundle(path, pins, authority):
    """Fresh cold verify from external pins and exact deterministic recomputation."""
    path = Path(path); require(path.is_dir() and not path.is_symlink(), 'immutable publication root missing/symlink')
    files = {}
    for p in path.rglob('*'):
        require(not p.is_symlink(), 'immutable bundle symlink forbidden')
        if p.is_file(): files[p.relative_to(path).as_posix()] = _file_bytes(p)
    require('bundle.json' in files, 'incomplete immutable bundle')
    require(byte_digest(files['bundle.json']) == pins.bundle_sha256, 'independent immutable bundle pin mismatch')
    manifest = loads(files['bundle.json']); review = loads(files['review.json'])
    require(digest(review) == pins.review_digest == manifest['review_digest'], 'independent review pin mismatch')
    require(digest(authority.core()) == pins.authority_sha256 == manifest['authority_sha256'], 'independent repository authority pin mismatch')
    require(set(files) == set(manifest['files']) | {'bundle.json'}, 'immutable bundle file closure mismatch')
    for name, sha in manifest['files'].items(): require(byte_digest(files[name]) == sha, 'immutable original bytes changed: ' + name)
    require(review['authority'] == authority.core(), 'stored authority differs from trusted context')
    selected = {p:files[p] for p in review['material_sha256s']}
    expected, _ = render_bundle({'review': review, 'materials': selected}, loads(files['authorization.json']), authority)
    require(expected == files, 'generated immutable consequences differ from exact reviewed inputs')
    require({p:byte_digest(_file_bytes(path / p)) for p in files} == {p:byte_digest(raw) for p,raw in files.items()}, 'immutable bytes changed during verification')
    return {'manifest': manifest, 'review': review, 'files': files, 'pins': asdict(pins), 'cold_verified': True}


def _directory(root, relative_dir, *, create=False):
    """No symlink components; caller holds repository writer capability."""
    fd = os.dup(root) if isinstance(root, int) else os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in Path(relative_dir).parts:
            require(part not in ['.', '..'], 'invalid directory component')
            if create:
                try: os.mkdir(part, mode=0o700, dir_fd=fd)
                except FileExistsError: pass
                os.fsync(fd)
            new = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd); os.close(fd); fd = new
        return fd
    except BaseException:
        os.close(fd); raise


def _stage(parent_fd, stage, files):
    os.mkdir(stage, mode=0o700, dir_fd=parent_fd)
    root_fd = os.open(stage, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent_fd)
    try:
        for path, raw in files.items():
            relative(path); p = Path(path)
            fd = _directory(root_fd, p.parent, create=True)
            try:
                out = os.open(p.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=fd)
                with os.fdopen(out, 'wb') as f: f.write(raw); f.flush(); os.fsync(f.fileno())
                os.fsync(fd)
            finally: os.close(fd)
        os.fsync(root_fd); os.fsync(parent_fd)
    finally: os.close(root_fd)


def _replace_managed(root, name, raw, before_sha256):
    p = Path(relative(name)); fd = _directory(root, p.parent, create=True)
    try:
        actual_path = Path('/proc/self/fd/' + str(fd)) / p.name
        actual = byte_digest(_file_bytes(actual_path)) if os.path.lexists(actual_path) else None
        after = byte_digest(raw)
        if actual == after: return 'already-current'
        require(actual == before_sha256, 'managed mirror conflict; preserve unrelated bytes: ' + name)
        tmp = '.' + p.name + '.repair-' + after
        try:
            out = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=fd)
            with os.fdopen(out, 'wb') as f: f.write(raw); f.flush(); os.fsync(f.fileno())
        except FileExistsError:
            require(_file_bytes(Path('/proc/self/fd/' + str(fd)) / tmp) == raw, 'unknown interrupted mirror bytes retained')
        # All cooperating publisher writers hold the single repository lock.
        current = byte_digest(_file_bytes(actual_path)) if os.path.lexists(actual_path) else None
        require(current == before_sha256, 'managed mirror changed during repair')
        os.replace(tmp, p.name, src_dir_fd=fd, dst_dir_fd=fd); os.fsync(fd)
        return 'repaired'
    finally: os.close(fd)


def _repair(verified, authority, *, crash_at=None):
    root = Path(authority.repository_root); review = verified['review']; files = verified['files']
    statuses = []
    for i,row in enumerate(review['mirrors']):
        require(row['source'] in files and row['source'] != 'bundle.json', 'managed mirror source outside committed bundle')
        result = _replace_managed(root, row['path'], files[row['source']], row['before_sha256'])
        statuses.append({'path': row['path'], 'result': result})
        if crash_at == 'after-first-mirror' and i == 0: os._exit(77)
    # Current lookup is deliberately last: it cannot expose a partial bundle.
    manifest = verified['manifest']; pointer = {'schema_version': 'cyberalchemy-lab-current-project-state-lookup/v1',
        'authority_effect': 'none', 'replay_source': False, 'projection_policy': 'generated-from-immutable-admission-bundle',
        'admission_bundle': {'path': authority.bundle_path + '/bundle.json', 'sha256': verified['pins']['bundle_sha256']},
        'current_project_state': {'path': authority.bundle_path + '/instances/project-state.json', 'sha256': manifest['current_project_state_sha256']},
        'identity_ref': manifest['current_project_state_ref'], 'decision_ref': manifest['decision_refs'][0]}
    statuses.append({'path': authority.current_pointer_path,
        'result': _replace_managed(root, authority.current_pointer_path, encoded(pointer), review['expected_pointer_sha256'])})
    return statuses


def _lock(authority):
    root = Path(authority.repository_root)
    fd = _directory(root, '.local/admission-locks', create=True)
    try: lock = os.open('repository-publisher.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600, dir_fd=fd)
    finally: os.close(fd)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        os.close(lock); raise RuntimeFault('repository publisher writer active') from exc
    return lock


def repair_publication(pins, authority, *, crash_at=None):
    """Cold idempotent projection repair of the same committed signed response.

    Historical expiry cannot erase an already committed transaction. Recovery
    scope comes from the independently resolved adapter, not a new owner response.
    """
    require(crash_at in [None, 'after-first-mirror'], 'unknown recovery fault hook')
    authority.core(); lock = _lock(authority)
    try:
        verified = verify_bundle(Path(authority.repository_root) / authority.bundle_path, pins, authority)
        return {'committed': True, 'new_owner_response_required': False, 'mirrors': _repair(verified, authority, crash_at=crash_at), 'pins': asdict(pins)}
    finally: os.close(lock)


def publish(parent, selection, selections, identity_path, identity_sha256, authority, prepared, response,
            *, extension_packages=None, mirrors=(), crash_at=None):
    """Commit one exact immutable repository bundle, then recoverable mirrors."""
    require(crash_at in [None, 'after-stage', 'after-commit', 'after-first-mirror'], 'unknown publication fault hook')
    authority.core(); root = Path(authority.repository_root); final = root / authority.bundle_path
    lock = _lock(authority); parent_lock = None
    try:
        # A committed bundle has consumed the response. Retry/repair does not
        # rebuild on the now-changed source pointer or issue another approval.
        files, manifest = render_bundle(prepared, response, authority)
        pins = PublicationPins(digest(prepared['review']), byte_digest(files['bundle.json']), digest(authority.core()))
        if os.path.lexists(final):
            verified = verify_bundle(final, pins, authority)
            return {'committed': True, 'idempotent': True, 'mirrors': _repair(verified, authority, crash_at=crash_at), 'pins': asdict(pins)}
        verify_response(response, prepared['review'], authority, live=True)
        parent_lock = os.open(parent.path / '.writer.lock', os.O_RDONLY | os.O_NOFOLLOW)
        try: fcntl.flock(parent_lock, fcntl.LOCK_SH | fcntl.LOCK_NB)
        except BlockingIOError as exc: raise RuntimeFault('local source writer active') from exc
        current = prepare_promotion(parent, selection, selections, identity_path, identity_sha256, authority,
                                    extension_packages=extension_packages, mirrors=mirrors)
        require(current['review'] == prepared['review'] and current['materials'] == prepared['materials'], 'stale repository promotion review')
        require(freshness(root, current['snapshot'])['status'] == 'current', 'repository source cut changed before publication')
        require(all(row['source'] in files for row in prepared['review']['mirrors']), 'mirror source not in exact bundle')
        parent_fd = _directory(root, Path(authority.bundle_path).parent, create=True)
        try:
            name = final.name; stage = '.' + name + '.publisher-' + pins.review_digest
            stage_path = Path('/proc/self/fd/' + str(parent_fd)) / stage
            if os.path.lexists(stage_path): verify_bundle(stage_path, pins, authority)
            else: _stage(parent_fd, stage, files)
            if crash_at == 'after-stage': os._exit(75)
            require(freshness(root, current['snapshot'])['status'] == 'current', 'repository source cut changed before commit')
            verify_response(response, prepared['review'], authority, live=True)
            _publish(parent_fd, stage, name)
            if crash_at == 'after-commit': os._exit(76)
        finally: os.close(parent_fd)
        verified = verify_bundle(final, pins, authority)
        try:
            states = _repair(verified, authority, crash_at=crash_at)
            return {'committed': True, 'idempotent': False, 'mirrors': states, 'pins': asdict(pins), 'new_owner_response_required': False}
        except (RuntimeFault, OSError) as exc:
            return {'committed': True, 'idempotent': False, 'projection_state': 'recovery-required',
                    'error': str(exc), 'pins': asdict(pins), 'new_owner_response_required': False}
    finally:
        if parent_lock is not None: os.close(parent_lock)
        os.close(lock)
