"""Qualification-only original Lab port. Never provisions an existing or production store."""
from __future__ import annotations
import copy
import hashlib
import json
import os
from pathlib import Path
import sys

MODEL = Path(__file__).resolve().parents[1]
REPO = MODEL.parents[2]
NATIVE = REPO / 'implementation/lab-runtime/v2'
sys.path.insert(0, str(NATIVE))
from lab_runtime.cli import example
from lab_runtime.common import RuntimeFault, byte_digest, digest, encoded, load, require
from lab_runtime.operations import prepare
from lab_runtime.sources import freshness, resolve
from lab_runtime.store import Store, approval_core, keygen, verify_approval
from lab_runtime.session import Session
from lab_runtime.graph import query
from creation import draft_from_file, prepare_bundle


def wire(value):
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, int):
        return str(value)
    if isinstance(value, list):
        return [wire(x) for x in value]
    if isinstance(value, dict):
        return {k: wire(v) for k, v in value.items()}
    return value


def current_sources():
    selected = load(MODEL / 'native-source.json')
    for name, expected in selected['files'].items():
        require(byte_digest((REPO / name).read_bytes()) == expected, 'selected native source changed: ' + name)


def write_new(path, value, raw=None):
    raw = encoded(value) if raw is None else raw
    with path.open('xb') as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    return binding(path)


def binding(path):
    raw = path.read_bytes()
    return {'path': path.name, 'sha256': byte_digest(raw), 'bytes': len(raw), 'digest_kind': 'original-file-sha256'}


def guard(home):
    require(home.is_absolute() and home.resolve() == home and not home.is_relative_to(REPO), 'fresh external fixture directory required')
    info = home.stat()
    require(info.st_uid == os.getuid() and not info.st_mode & 0o077, 'private fixture directory required')
    current_sources()


def branch_data(data):
    c, base = data['config'], data['baseline']
    return {'project': data['projection']['state']['payload']['project_ref'], 'store': c['store_id'], 'owner': c['owner_ref'],
            'scope': c['scope_ref'], 'policy': c['policy_ref'], 'challenge': c['challenge_route'],
            'head': {'transaction_digest': data['head']['transaction_digest'], 'sequence': data['head']['sequence']},
            'sources': {'selected_profile': digest(base['profile']), 'observed_profile': digest(load(NATIVE / 'profile.json')),
                        'snapshot': base['snapshot_digest'], 'posture': 'Fresh' if data['freshness']['status'] == 'current' else 'Stale',
                        'checked_files': data['freshness']['checked_count']},
            'allowed_categories': c['allowed_categories'], 'allowed_effects': c['allowed_effects']}


def request_for(home, proposal, approval, *, original=None):
    data = Store(home / 'store', REPO).replay()
    old = next((tx for tx in data['transactions'][1:] if tx['proposal']['proposal_id'] == proposal['proposal_id']), None)
    existing = 'NoExistingProposal' if old is None else ('SameCommittedBytes' if old['proposal'] == proposal and old['approval'] == approval else 'ConflictingCommittedBytes')
    targets_valid, cores = False, []
    try:
        _, cores = prepare(data['projection'], proposal, data['head']['transaction_digest'], data['config'])
        targets_valid = True
    except RuntimeFault:
        if old is not None:
            cores = old['decision_cores']
    exact, signature = False, 'SignatureUnchecked'
    if approval is not None and cores:
        expected = approval_core(proposal, cores, data['config'], approval['approved_at'])
        exact = {k: v for k, v in approval.items() if k != 'signature'} == expected
        try:
            verify_approval(approval, proposal, cores, data['config'])
            signature = 'SignatureVerified'
        except RuntimeFault:
            signature = 'SignatureInvalid'
    p = proposal
    targets = []
    for index, target in enumerate(p['targets']):
        raw_binding = None
        if target['record'] is not None:
            file = home / ('original-user-journey.json' if target['category'] == 'definition' else 'target-' + str(index) + '.json')
            raw_binding = binding(file)
        targets.append({'category': target['category'], 'effect': target['operation'], 'version': target['version_ref'],
                        'carrier': target['carrier_ref'], 'predecessor': target['predecessor_ref'], 'decision': target['decision_ref'],
                        'authored_record': raw_binding, 'contract': target['contract']})
    request = {'branch': branch_data(data), 'proposal': {'proposal_id': p['proposal_id'], 'expected_head': p['expected_head'],
               'source_snapshot': p['source_snapshot_digest'], 'scope': p['scope_ref'], 'policy': p['policy_ref'],
               'challenge': p['challenge_route'], 'original': original or binding(home / 'proposal.json'), 'targets': targets,
               'schemas': [], 'approval': binding(home / 'approval.json') if approval is not None else None},
               'checks': {'chain_verified': True, 'targets_valid': targets_valid, 'exact_approval': exact, 'signature': signature,
                          'leftovers': bool(Store(home / 'store', REPO).leftovers(data['head']))},
               'existing': existing, 'phase': 'ReadyToDispatch'}
    return wire(request)


def seed(home, case):
    require(not any(home.iterdir()), 'fixture directory must be empty')
    keygen(home / 'owner.pem', home / 'owner.pub')
    store = Store(home / 'store', REPO)
    store.initialize(load(NATIVE / 'profile.json'), 'alch-fixture-' + str(case['id']), 'role:definition-owner', (home / 'owner.pub').read_text().strip())
    proposal = example(store, 'alch-model-' + str(case['id']))
    raw = (REPO / 'authority/definitions/candidates/0017-user-journey/definitions/user-journey/v1/definition.json').read_bytes()
    require(byte_digest(raw) == '693045f6c86f0faa8b168d072e473bbb48f1e75cb71d440fc559c7440f147fe7', 'User Journey original changed')
    write_new(home / 'original-user-journey.json', None, raw=raw)
    write_new(home / 'target-0.json', proposal['targets'][0]['record'])
    data = store.replay(require_current=True)
    project = data['projection']['state']['payload']['project_ref']
    record = draft_from_file(data, home / 'target-0.json', kind='record', project=project, scope='work',
                             work='work:creation-fixture', carrier=proposal['targets'][0]['carrier_ref'],
                             version=proposal['targets'][0]['version_ref'], decision=proposal['targets'][0]['decision_ref'])
    definition = draft_from_file(data, home / 'original-user-journey.json', kind='definition', project=project,
                                 scope='project', work=None, carrier='cal.artifact-type.definition/v2', version=None,
                                 decision='decision:alch-model-definition:' + str(case['id']))
    proposal = prepare_bundle(data, [record, definition], proposal['proposal_id'])
    creations = {draft['kind']: {'request': draft['request'], 'draft': draft['draft']} for draft in [record, definition]}
    write_new(home / 'proposal.json', proposal)
    review = store.review(proposal)
    approval = store.authorize(proposal, home / 'owner.pem')
    write_new(home / 'approval.json', approval)
    request = request_for(home, proposal, approval)
    spec = {'fixture_only': True, 'id': str(case['id']), 'mode': case.get('mode', 'normal'), 'request': request,
            'proposal_sha256': binding(home / 'proposal.json')['sha256'], 'approval_sha256': binding(home / 'approval.json')['sha256']}
    write_new(home / 'fixture.json', spec)
    return {'request': request, 'review': review, 'original_definition': binding(home / 'original-user-journey.json'),
            'baseline_cursor': 7, 'fixture_only': True, 'creations': wire(creations)}


def selected(home, ticket=None):
    spec = load(home / 'fixture.json')
    require(spec['fixture_only'] is True, 'fixture marker required')
    proposal, approval = load(home / 'proposal.json'), load(home / 'approval.json')
    require(binding(home / 'proposal.json')['sha256'] == spec['proposal_sha256'] and binding(home / 'approval.json')['sha256'] == spec['approval_sha256'], 'fixture bytes changed')
    if ticket is not None:
        require(ticket['id'] == spec['id'] and ticket['request'] == spec['request'], 'native ticket differs from frozen fixture selection')
    return spec, Store(home / 'store', REPO), proposal, approval


def native_result(home, spec, data, tx=None, outcome=None, explanation='Observed original native Lab operation'):
    receipt = None
    if tx is not None:
        file = home / 'native-receipt.json'
        raw = encoded(tx['consequences']['receipt'])
        if file.exists():
            require(file.read_bytes() == raw, 'immutable native receipt conflict')
        else:
            write_new(file, None, raw=raw)
        receipt = binding(file)
    return wire({'id': int(spec['id']), 'proposal': binding(home / 'proposal.json'), 'outcome': outcome or 'Committed',
                 'transaction_digest': tx['digest'] if tx else None, 'receipt': receipt,
                 'observed_head': data['head']['transaction_digest'], 'sequence': data['head']['sequence'],
                 'semantic_cursor': len(data['projection']['histories']['project-semantic-event-history']['payload']['events']),
                 'governance_cursor': len(data['projection']['histories']['project-governance-event-history']['payload']['events']),
                 'explanation': explanation})


def inspect(home, ticket=None):
    spec, store, proposal, approval = selected(home, ticket)
    try:
        data = store.replay()
    except RuntimeFault:
        return {'kind': 'unknown'}
    tx = next((tx for tx in data['transactions'][1:] if tx['proposal']['proposal_id'] == proposal['proposal_id']), None)
    if tx is not None:
        require(tx['proposal'] == proposal and tx['approval'] == approval, 'native committed bytes conflict')
        return {'kind': 'observed', 'result': native_result(home, spec, data, tx)}
    if (home / 'refused.json').exists():
        return {'kind': 'observed', 'result': native_result(home, spec, data, outcome='Refused', explanation=load(home / 'refused.json')['reason'])}
    if not (home / 'dispatched.json').exists():
        return {'kind': 'not-dispatched'}
    if store.leftovers(data['head']):
        return {'kind': 'unknown'}
    return {'kind': 'observed', 'result': native_result(home, spec, data, outcome='NotDispatched', explanation='Original local chain proves no committed transaction; fresh permission required')}


def apply(home, ticket):
    spec, store, proposal, approval = selected(home, ticket)
    before = inspect(home, ticket)
    if before['kind'] != 'not-dispatched':
        return before
    write_new(home / 'dispatched.json', {'id': spec['id'], 'proposal': binding(home / 'proposal.json')})
    crash_at = {'crash-after-head': 'after-head', 'crash-before-head': 'before-head'}.get(spec['mode'])
    try:
        store.apply(proposal, approval, crash_at=crash_at)
    except Exception as error:
        state = inspect(home, ticket)
        if state['kind'] == 'observed' and state['result']['outcome'] == 'Committed':
            return state
        if store.leftovers(store.replay()['head']):
            return {'kind': 'unknown'}
        if isinstance(error, RuntimeFault):
            write_new(home / 'refused.json', {'reason': str(error)})
            return inspect(home, ticket)
        return {'kind': 'unknown'}
    return inspect(home, ticket)


def negatives(home):
    _, store, original, approval = selected(home)
    cases = []
    for name, mutate in [
        ('head-changed', lambda p, a: p.update(expected_head='0' * 64)),
        ('snapshot-mismatch', lambda p, a: p.update(source_snapshot_digest='0' * 64)),
        ('scope-mismatch', lambda p, a: p.update(scope_ref='scope:other')),
        ('policy-mismatch', lambda p, a: p.update(policy_ref='policy:other')),
        ('challenge-mismatch', lambda p, a: p.update(challenge_route='challenge:other')),
        ('signature-rejected', lambda p, a: a.update(signature='0' * 128)),
        ('targets-invalid', lambda p, a: p['targets'][0]['record'].pop('payload')),
    ]:
        p, a = copy.deepcopy(original), copy.deepcopy(approval)
        mutate(p, a)
        request = request_for(home, p, a)
        allowed, reason = True, None
        try:
            store.apply(p, a)
        except RuntimeFault as error:
            allowed, reason = False, str(error)
        require(not allowed, 'negative native reference unexpectedly committed: ' + name)
        cases.append({'name': name, 'request': request, 'native_allowed': allowed, 'native_reason': reason})
    return {'cases': cases}


def observations(home):
    spec, store, proposal, approval = selected(home)
    data = store.replay()
    graph = query(data, depth=1, max_nodes=20, max_edges=30)
    stale_data = copy.deepcopy(data)
    stale_data['freshness']['status'] = 'stale'
    stale = query(stale_data, depth=1, max_nodes=20, max_edges=30)
    clock = [100.0]
    session = Session(store, proposal['targets'][0]['version_ref'], ttl=10, clock=lambda: clock[0])
    session.note('Ephemeral qualification note')
    clock[0] = 110.0
    expired = False
    try:
        session.context()
    except RuntimeFault:
        expired = session.closed and not session.memory
    tx = data['transactions'][1]
    repeated = store.apply(proposal, approval)
    subject = resolve(data['projection']['subjects'], proposal['targets'][1]['version_ref'])
    return wire({'branch': branch_data(data), 'repeat_request': request_for(home, proposal, approval), 'native_repeat': repeated['idempotent'],
                 'sequence': data['head']['sequence'], 'cursor': len(data['projection']['histories']['project-semantic-event-history']['payload']['events']),
                 'native_stale_confirmed_connections': len(stale['connections']), 'native_query_nodes': len(graph['nodes']),
                 'native_session_expired_and_erased': expired,
                 'subject': {'project': branch_data(data)['project'], 'identity_ref': subject['identity'], 'version': subject['version_ref'],
                             'standing': 'LocalCurrent', 'source': binding(home / 'original-user-journey.json'),
                             'candidate_payload': subject['record'].get('status') == 'candidate'},
                 'native_receipt': tx['consequences']['receipt'], 'definition_original_sha256': binding(home / 'original-user-journey.json')['sha256']})


def creation_checks(home):
    from creation import create_draft, inspect_creation
    import creation
    import subprocess
    spec, store, proposal, approval = selected(home)
    data = store.replay(require_current=True)
    before = (home / 'store/HEAD.json').read_bytes()
    project = data['projection']['state']['payload']['project_ref']
    workspace = home / 'workspace'
    out = workspace / 'authority/definitions/user-journey/v1'
    kwargs = dict(kind='definition', project=project, scope='project', work=None,
                  carrier='cal.artifact-type.definition/v2', version=None,
                  decision='decision:creation-definition:' + spec['id'], proposal_id='creation-definition-' + spec['id'], output=out)
    result = create_draft(store, home / 'original-user-journey.json', **kwargs)
    require((out / 'definition.json').read_bytes() == (home / 'original-user-journey.json').read_bytes(), 'definition original bytes changed')
    unsigned = load(out / 'proposal.json')
    review = store.review(unsigned)
    repeated = create_draft(store, home / 'original-user-journey.json', **kwargs)
    require(repeated['outcome'] == 'replayed', 'creation not idempotent')
    original_record = proposal['targets'][0]
    record_out = workspace / 'work/creation/outputs/records/local-work'
    command = [sys.executable, '-B', str(MODEL / 'create.py'), '--store', str(store.path), 'record',
               '--file', str(home / 'target-0.json'), '--project', project, '--scope', 'work', '--work', 'work:creation',
               '--carrier', original_record['carrier_ref'], '--version-ref', original_record['version_ref'],
               '--decision', 'decision:creation-record:' + spec['id'], '--proposal-id', 'creation-record-' + spec['id'], '--out', str(record_out)]
    cli = subprocess.run(command, capture_output=True, text=True)
    require(cli.returncode == 0, 'creation CLI failed: ' + cli.stdout + cli.stderr)
    cli_result = json.loads(cli.stdout)
    require((record_out / 'record.json').read_bytes() == (home / 'target-0.json').read_bytes(), 'record original bytes changed')
    record_proposal = load(record_out / 'proposal.json')
    store.review(record_proposal)
    # Exact-byte tampering is detected even when the JSON meaning is unchanged.
    original_raw = (record_out / 'record.json').read_bytes()
    (record_out / 'record.json').write_bytes(original_raw + b' ')
    tampered = False
    try:inspect_creation(record_out)
    except RuntimeFault:tampered = True
    (record_out / 'record.json').write_bytes(original_raw)
    require(tampered, 'creation inspection accepted changed original bytes')
    blocked = []
    def refuses(name, source, changes):
        options = {**kwargs, **changes, 'output': workspace / ('blocked-' + name)}
        try:create_draft(store, source, **options)
        except (RuntimeFault, KeyError, ValueError) as error:
            require(not Path(options['output']).exists(), 'refused creation published output')
            blocked.append({'name': name, 'reason': str(error)})
            return
        raise RuntimeFault('creation unexpectedly accepted ' + name)
    bad = copy.deepcopy(load(home / 'original-user-journey.json'))
    del bad['voices']['scientific_formal']
    write_new(home / 'missing-voice.json', bad)
    refuses('missing-required-voice', home / 'missing-voice.json', {})
    refuses('wrong-project', home / 'original-user-journey.json', {'project': 'project:other'})
    refuses('work-scope-without-work', home / 'original-user-journey.json', {'scope': 'work'})
    refuses('project-scope-with-work', home / 'original-user-journey.json', {'work': 'work:other'})
    refuses('definition-through-record-route', home / 'original-user-journey.json', {'kind': 'record', 'version': proposal['targets'][1]['version_ref']})
    bad = copy.deepcopy(load(home / 'original-user-journey.json'))
    bad['schema_digest'] = '0' * 64
    write_new(home / 'wrong-schema-binding.json', bad)
    refuses('schema-binding-mismatch', home / 'wrong-schema-binding.json', {})
    existing = next(entry for entry in data['projection']['subjects'].values() if entry['kind'] == 'work')
    collision = copy.deepcopy(original_record['record'])
    collision['node_id'] = existing['identity']
    write_new(home / 'existing-work.json', collision)
    refuses('existing-identity', home / 'existing-work.json', {'kind': 'record', 'carrier': original_record['carrier_ref'], 'version': existing['identity'] + '@creation-candidate'})
    # Simulate interruption after a body write: preserve the incomplete output,
    # keep native HEAD unchanged, and refuse an implicit overwrite on retry.
    incomplete = workspace / 'incomplete-draft'
    original_writer = creation._write_exclusive
    count = [0]
    def interrupted(path, raw):
        count[0] += 1
        if count[0] == 2:raise OSError('qualification interruption')
        return original_writer(path, raw)
    creation._write_exclusive = interrupted
    unknown = False
    try:create_draft(store, home / 'original-user-journey.json', **{**kwargs, 'output': incomplete})
    except RuntimeFault as error:unknown = 'outcome-unknown' in str(error)
    finally:creation._write_exclusive = original_writer
    require(unknown and (incomplete / 'definition.json').is_file() and not (incomplete / 'creation.json').exists(), 'incomplete creation was not preserved')
    incomplete_before = (incomplete / 'definition.json').read_bytes()
    refused_retry = False
    try:create_draft(store, home / 'original-user-journey.json', **{**kwargs, 'output': incomplete})
    except RuntimeFault as error:refused_retry = 'publication-incomplete' in str(error)
    require(refused_retry and (incomplete / 'definition.json').read_bytes() == incomplete_before, 'incomplete draft overwritten')
    require((home / 'store/HEAD.json').read_bytes() == before and store.replay()['head']['sequence'] == 0, 'draft creation changed native state')
    require('approval' not in unsigned and 'signature' not in unsigned and not (out / 'approval.json').exists(), 'draft created owner authority')
    return {'definition_created': result['outcome'] == 'created', 'definition_original_sha256': binding(out / 'definition.json')['sha256'],
            'record_cli_created': cli_result['outcome'] == 'created', 'unsigned_proposals_reviewable': True,
            'idempotent_creation': repeated['outcome'] == 'replayed', 'exact_byte_tamper_refused': tampered,
            'native_head_unchanged': True, 'native_sequence': 0, 'blocked': blocked,
            'incomplete_publication_preserved': unknown and refused_retry, 'registry_updated': result['receipt']['registry_updated'],
            'approval_required': review['approval_required'], 'new_files': [p.name for p in out.iterdir()]}


def artifact_type_checks(home):
    """Actual draft CLI -> owner admission -> fresh-process record creation, on a disposable branch."""
    from creation import create_draft, inspect_creation, ARTIFACT_TYPE_CARRIER
    import subprocess
    _, store, original, _ = selected(home)
    initial = store.replay(require_current=True)
    project = branch_data(initial)['project']
    work = initial['projection']['contracts']['cal.artifact-type.work/v1']
    schema = copy.deepcopy(initial['projection']['documents'][work['schema_path']])
    # Exercise an explicit custom identity field, not the common node_id fallback.
    schema['properties']['custom_id'] = schema['properties'].pop('node_id')
    schema['required'] = ['custom_id' if x == 'node_id' else x for x in schema['required']]
    schema_path = 'runtime/schemas/registered-work.json'
    type_ref = 'cal.artifact-type.registered-work/v1'
    descriptor = {'artifact_type_ref': type_ref, 'semantic_kind': 'work',
                  'semantic_definition_refs': work['semantic_definition_refs'], 'schema_path': schema_path,
                  'schema_selector': None, 'schema_sha256': byte_digest(encoded(schema)),
                  'distinct_validation_purpose': 'Validate registered Work with an explicit custom instance identity.'}
    contract = {k: descriptor[k] for k in ['semantic_kind', 'schema_path', 'schema_selector', 'schema_sha256']}
    contract.update(instance_discriminator=work['instance_discriminator'], identity_field='custom_id',
                    allowed_relation_kinds=work['artifact']['allowed_relation_kinds'], relation_roles=work['artifact']['relation_roles'])
    for name, value in [('type-source.json', descriptor), ('schema-source.json', schema), ('contract-source.json', contract)]:
        write_new(home / name, value, raw=json.dumps(value, separators=(',', ':')).encode() if name == 'schema-source.json' else None)
    original_schema_sha = binding(home / 'schema-source.json')['sha256']
    require(original_schema_sha != descriptor['schema_sha256'], 'fixture must distinguish original schema bytes from native encoding')
    kwargs = dict(kind='artifact-type', project=project, scope='project', work=None, carrier=ARTIFACT_TYPE_CARRIER,
                  version=None, decision='decision:registered-work:type', proposal_id='register-work-type',
                  output=home / 'draft-type', owner='role:definition-owner',
                  schema_source=home / 'schema-source.json', contract_source=home / 'contract-source.json')
    cli = [sys.executable, '-B', str(MODEL / 'create.py'), '--store', str(store.path), 'artifact-type',
           '--file', str(home / 'type-source.json'), '--schema', str(home / 'schema-source.json'),
           '--contract', str(home / 'contract-source.json'), '--owner', kwargs['owner'], '--project', project,
           '--decision', kwargs['decision'], '--proposal-id', kwargs['proposal_id'], '--out', str(kwargs['output'])]
    def run(command):
        result = subprocess.run(command, capture_output=True, text=True, timeout=120)
        require(result.returncode == 0, 'Artifact Type fixture command failed: ' + result.stdout + result.stderr)
        return json.loads(result.stdout)
    created = run(cli)
    receipt = created['receipt']
    require(created['outcome'] == 'created' and store.replay()['head'] == initial['head'], 'Artifact Type draft mutated native HEAD')
    require(run(cli)['outcome'] == 'replayed', 'Artifact Type draft did not replay')
    p = load(kwargs['output'] / 'proposal.json')
    require(store.review(p)['approval_required'], 'Artifact Type proposal has no owner gate')
    blocked = []
    def refuses(name, file, changes):
        opts = {**kwargs, **changes, 'output': home / ('blocked-type-' + name)}
        try:create_draft(store, file, **opts)
        except (RuntimeFault, KeyError, ValueError) as error:
            require(not opts['output'].exists(), 'rejected type published files')
            blocked.append({'name': name, 'reason': str(error)})
            return
        raise RuntimeFault('unexpectedly accepted type: ' + name)
    def mutated(name, value):
        file = home / (name + '.json');write_new(file, value);return file
    bad = copy.deepcopy(contract);bad['schema_sha256'] = '0' * 64
    refuses('digest', home / 'type-source.json', {'contract_source': mutated('bad-contract-digest', bad)})
    bad = copy.deepcopy(descriptor);bad['schema_path'] = 'runtime/schemas/different.json'
    refuses('descriptor-agreement', mutated('bad-type-descriptor', bad), {})
    bad = copy.deepcopy(descriptor);bad['semantic_definition_refs'] = ['missing-definition@1.0.0']
    refuses('unresolved-definition', mutated('bad-type-definition', bad), {})
    refuses('owner-required', home / 'type-source.json', {'owner': None})
    refuses('project', home / 'type-source.json', {'project': 'project:other'})
    bad = copy.deepcopy(schema);bad['type'] = 'not-a-json-schema-type'
    bad_contract = {**contract, 'schema_sha256': byte_digest(encoded(bad))}
    bad_descriptor = {**descriptor, 'schema_sha256': bad_contract['schema_sha256']}
    refuses('invalid-schema', mutated('invalid-type-schema-descriptor', bad_descriptor),
            {'schema_source': mutated('invalid-type-schema', bad), 'contract_source': mutated('invalid-type-schema-contract', bad_contract)})
    bad = {'$ref': 'https://example.invalid/schema.json'}
    bad_contract = {**contract, 'schema_selector': None, 'schema_sha256': byte_digest(encoded(bad))}
    bad_descriptor = {**descriptor, 'schema_selector': None, 'schema_sha256': bad_contract['schema_sha256']}
    refuses('external-schema', mutated('external-schema-descriptor', bad_descriptor),
            {'schema_source': mutated('external-schema', bad), 'contract_source': mutated('external-schema-contract', bad_contract)})
    for name in ['artifact-type.json', 'schema.json', 'contract.json', 'proposal.json']:
        path = kwargs['output'] / name;raw = path.read_bytes();path.write_bytes(raw + b' ')
        try:
            accepted = True
            try:inspect_creation(kwargs['output'])
            except RuntimeFault:accepted = False
            require(not accepted, 'type draft tampering accepted: ' + name)
        finally:path.write_bytes(raw)
    approval = store.authorize(p, home / 'owner.pem')
    store.apply(p, approval)
    committed = store.replay(require_current=True)
    tx = committed['transactions'][-1]
    require(type_ref in committed['projection']['contracts'], 'type not registered')
    require(run(cli)['outcome'] == 'replayed', 'committed type draft replay failed')
    refuses('existing-type', home / 'type-source.json', {})
    # Delete caller schema inputs: only the verified native transaction is now authoritative.
    (home / 'schema-source.json').unlink()
    body = copy.deepcopy(original['targets'][0]['record'])
    body['custom_id'] = body.pop('node_id') + '-registered'
    write_new(home / 'registered-record-source.json', body)
    record_out = home / 'draft-registered-record'
    record_cli = [sys.executable, '-B', str(MODEL / 'create.py'), '--store', str(store.path), 'record',
                  '--file', str(home / 'registered-record-source.json'), '--project', project, '--scope', 'work', '--work', 'work:registered',
                  '--carrier', type_ref, '--version-ref', body['custom_id'] + '@candidate.1',
                  '--decision', 'decision:registered-work:record', '--proposal-id', 'create-registered-work', '--out', str(record_out)]
    record_result = run(record_cli)
    record_receipt = record_result['receipt']
    material = record_receipt['creation_request']['validation']['carrier_schema']
    require(material['digest_kind'] == 'native-json-sha256' and material['sha256'] == descriptor['schema_sha256'] and
            material['selector'] == descriptor['schema_selector'] and material['provenance_digest'] == tx['digest'], 'committed schema provenance lost')
    require(store.replay()['head'] == committed['head'], 'record draft mutated native HEAD')
    rp = load(record_out / 'proposal.json')
    require(rp['schemas'] == {} and rp['targets'][0]['record'] == body, 'registered record proposal changed body')
    store.apply(rp, store.authorize(rp, home / 'owner.pem'))
    require(run(record_cli)['outcome'] == 'replayed', 'registered record draft replay failed')
    fresh = store.replay(require_current=True)
    require(fresh['head']['sequence'] == 2 and rp['targets'][0]['version_ref'] in fresh['projection']['subjects'], 'registered record admission failed')
    # Native refusals use a genuinely current registered carrier.
    record_blocked = []
    def refuses_record(name, changed):
        file = mutated('bad-record-' + name, changed)
        try:create_draft(store, file, kind='record', project=project, scope='work', work='work:registered', carrier=type_ref,
                         version=changed.get('custom_id', 'missing') + '@candidate.2', decision='decision:bad:' + name,
                         proposal_id='bad-record-' + name, output=home / ('blocked-record-' + name))
        except (RuntimeFault, KeyError, ValueError) as error:
            record_blocked.append({'name': name, 'reason': str(error)});return
        raise RuntimeFault('unexpectedly accepted registered record: ' + name)
    bad = copy.deepcopy(body);bad['custom_id'] += '-wrong-kind';bad['schema_version'] = 'incorrect-discriminator'
    refuses_record('discriminator', bad)
    bad = copy.deepcopy(body);bad['custom_id'] += '-missing';del bad['owner_ref']
    refuses_record('schema-required-field', bad)
    refuses_record('duplicate-identity', body)
    # Explicitly withdrawn carrier cannot be resurrected by its retained schema.
    wp = {**rp, 'proposal_id': 'withdraw-registered-work-type', 'expected_head': fresh['head']['transaction_digest'],
          'targets': [{**p['targets'][0], 'operation': 'withdraw', 'predecessor_ref': type_ref,
                       'record': None, 'contract': None, 'decision_ref': 'decision:registered-work:withdraw'}], 'schemas': {}}
    store.apply(wp, store.authorize(wp, home / 'owner.pem'))
    bad = copy.deepcopy(body);bad['custom_id'] += '-withdrawn'
    refuses_record('withdrawn-carrier', bad)
    return wire({'fixture_only': True, 'type': {'branch': branch_data(initial), 'request': receipt['artifact_type_request'],
                 'draft': receipt['draft'], 'original': binding(kwargs['output'] / 'proposal.json')},
                 'record': {'branch': branch_data(committed), 'request': record_receipt['creation_request'], 'draft': record_receipt['draft']},
                 'type_cli_created': True, 'drafts_preserve_head': True, 'idempotent_before_and_after_admission': True,
                 'exact_originals_retained': all((kwargs['output'] / name).read_bytes() == (home / source).read_bytes()
                     for name, source in [('artifact-type.json', 'type-source.json'), ('contract.json', 'contract-source.json')]),
                 'original_schema_sha256': original_schema_sha, 'all_draft_members_tamper_refused': True, 'blocked': blocked, 'record_blocked': record_blocked,
                 'registered_schema_from_native_transaction': material, 'record_native_sequence': fresh['head']['sequence'],
                 'fresh_process_replay': True, 'type_transaction': tx['digest'], 'authority_effect_of_drafts': 'none'})


def recover(home):
    _, store, _, _ = selected(home)
    data = store.replay()
    before = data['head']['transaction_digest']
    recovered = store.recover(before)
    after = store.replay()
    require(after['head']['transaction_digest'] == before, 'recovery changed committed HEAD')
    return {'recovered': recovered, 'inspection': inspect(home), 'head_preserved': True}


def main():
    command = json.load(sys.stdin)
    home = Path(command['fixture']).absolute()
    guard(home)
    operation = command['operation']
    if operation == 'seed':return seed(home, command)
    if operation == 'inspect':return inspect(home, command.get('ticket'))
    if operation == 'apply':return apply(home, command['ticket'])
    if operation == 'negative-cases':return negatives(home)
    if operation == 'observations':return observations(home)
    if operation == 'recover':return recover(home)
    if operation == 'creation-checks':return creation_checks(home)
    if operation == 'artifact-type-checks':return artifact_type_checks(home)
    raise RuntimeFault('unknown fixture operation')


if __name__ == '__main__':
    print(json.dumps(main(), ensure_ascii=False, separators=(',', ':')))
