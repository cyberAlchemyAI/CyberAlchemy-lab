"""Exact candidate reconstruction in a separate, signed, atomic successor genesis.

This is a candidate branch format, not a legacy Store or a global admission.
Old signatures stay in the old branch. New record bytes are reconstruction
postimages, with original committed transaction/selector provenance.
"""
from __future__ import annotations

import copy
import ctypes
import fcntl
import os
import re
import stat
from dataclasses import asdict, dataclass
from pathlib import Path
from datetime import datetime, timezone

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey, Ed25519PrivateKey
from jsonschema import Draft202012Validator

from .common import RuntimeFault, byte_digest, digest, encoded, load, loads, pointer, require
from .profiles import Selection, select
from .sources import capture, freshness, validate_schema, verify_snapshot
from .store import VerifiedLegacyReadStore

CURRENT = {'admitted-current', 'local-admitted-current'}
SCHEMA = Path(__file__).resolve().parents[1] / 'schemas/branch-transition.schema.json'


def _closed(value, keys):
    require(isinstance(value, dict) and set(value) == set(keys), 'transition envelope fields differ')


def _date(value):
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
        require(result.tzinfo is not None, 'timezone required')
        return result.astimezone(timezone.utc)
    except (TypeError, ValueError, AttributeError) as exc:
        raise RuntimeFault('invalid transition timestamp') from exc


@dataclass(frozen=True)
class LocalPolicy:
    """Trusted adapter inputs. Never derive operational permission from call JSON."""
    owner_ref: str
    public_key: str
    branch_id: str
    destination: str
    scope_ref: str
    expires_at: str
    effect: str = 'reconstruct-exact-candidate-genesis'

    def core(self):
        value = asdict(self)
        require(self.effect == 'reconstruct-exact-candidate-genesis', 'unsupported transition authority')
        require(all(isinstance(v, str) and v for v in value.values()), 'empty transition policy')
        require(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:-]{0,127}', self.branch_id), 'invalid branch identity')
        require(len(bytes.fromhex(self.public_key)) == 32, 'invalid transition public key')
        require(str(Path(self.destination).resolve()) == self.destination, 'destination must be canonical absolute path')
        _date(self.expires_at)
        return value


@dataclass(frozen=True)
class BranchPins:
    """External replay pins, handed out by the reviewed apply result."""
    branch_id: str
    plan_digest: str
    baseline_snapshot_digest: str
    profile_sha256: str
    policy_sha256: str
    head_digest: str


def _file_bytes(path):
    path = Path(path)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as handle:
        require(stat.S_ISREG(os.fstat(handle.fileno()).st_mode), 'transition material must be regular file')
        return handle.read()


def committed_files(parent, data):
    names = ['config.json', 'baseline.json', 'HEAD.json'] + [
        f'transactions/{i:010d}.json' for i in range(data['head']['sequence'] + 1)]
    return {name: byte_digest(_file_bytes(parent.path / name)) for name in names}


def _target_index(data, bindings):
    result = {}
    for tx in data['transactions'][1:]:
        for index, target in enumerate(tx['proposal']['targets']):
            version = target['version_ref']
            result[version] = {'target': target, 'provenance': {
                'transaction_path': f"transactions/{tx['sequence']:010d}.json",
                'transaction_sha256': bindings[f"transactions/{tx['sequence']:010d}.json"],
                'transaction_digest': tx['digest'], 'selector': f'/proposal/targets/{index}/record',
                'old_decision_ref': target['decision_ref'], 'signatures_copied': False,
                'record_byte_semantics': 'new-reconstructed-postimage; not original precommit artifact bytes'}}
    return result


def _contract(snapshot, ref):
    require(ref in snapshot['contracts'], 'unknown new carrier: ' + ref)
    c = snapshot['contracts'][ref]
    require(c['lifecycle_state'] == 'admitted-current', 'new carrier must be admitted-current')
    return c


def _record_identity(record, category, carrier, c, identity_bindings):
    if category == 'artifact-type':
        require(record['artifact_type_ref'].rsplit('/', 1)[0], 'missing artifact type identity')
        return record['artifact_type_ref'].rsplit('/', 1)[0]
    selector = c['artifact'].get('instance_contract', {}).get('identity_field')
    if selector:
        selector = '/' + selector if not selector.startswith('/') else selector
    else:
        rows = [r for r in identity_bindings['carriers'] if r['carrier_ref'] == carrier]
        require(len(rows) == 1, 'missing exact carrier identity selector')
        row = rows[0]
        require(row['schema_path'] == c['schema_path'] and row['schema_sha256'] == c['schema_sha256']
                and row.get('schema_selector') == c.get('schema_selector'), 'identity binding differs from current contract')
        selector = row['identity_selector']
    ident = pointer(record, selector)
    require(isinstance(ident, str) and ident, 'missing exact record identity')
    return ident


def _validate(record, category, carrier, snapshot, identity_bindings, subjects):
    c = _contract(snapshot, carrier)
    expected_category = {'artifact-type': 'artifact-type', 'definition': 'definition',
                         'relation-kind': 'relation-kind', 'typed-relation': 'typed-relation'}.get(c['semantic_kind'], 'artifact-instance')
    require(category == expected_category, 'category/new carrier mismatch')
    discriminator = c.get('instance_discriminator')
    if discriminator and not (category == 'artifact-type' and carrier == 'cal.artifact-type.artifact-type/v3'):
        require(pointer(record, discriminator['path']) == discriminator['value'], 'new carrier discriminator mismatch')
    selector = c.get('schema_selector')
    if category == 'artifact-type' and carrier == 'cal.artifact-type.artifact-type/v3':
        selector = '#/properties/registered_types/items'
    validate_schema(record, c['schema_path'], selector, snapshot['documents'])
    ident = _record_identity(record, category, carrier, c, identity_bindings)
    # Semantic extension records remain candidate-only. Their bytes are checked,
    # but they cannot extend global registries or make new connections available.
    for relation in record.get('relation_refs', []):
        if not isinstance(relation, dict) or 'relation_kind_ref' not in relation:
            continue
        ref = relation['relation_kind_ref']
        require(ref in snapshot['relation_contracts'], 'unknown embedded relation kind')
        rc = snapshot['relation_contracts'][ref]['payload']
        pair = {'source_kind': c['semantic_kind'], 'target_kind': relation['counterpart_kind']}
        if relation['direction'] == 'target':
            pair = {'source_kind': pair['target_kind'], 'target_kind': pair['source_kind']}
        require(pair in rc['allowed_endpoint_pairs'], 'undeclared embedded ordered pair')
    if category == 'typed-relation':
        payload = record['payload']
        ref = payload['relation_kind_ref']
        require(ref in snapshot['relation_contracts'], 'unknown relation kind under new cut')
        rc = snapshot['relation_contracts'][ref]['payload']
        require({'source_kind': payload['source']['kind'], 'target_kind': payload['target']['kind']}
                in rc['allowed_endpoint_pairs'], 'undeclared exact ordered pair')
        for e in [payload['source'], payload['target']]:
            require(e['version_ref'] in subjects, 'exact endpoint outside successor closure')
            entry = subjects[e['version_ref']]
            require(entry['identity'] == e['ref'] and entry['kind'] == e['kind'], 'endpoint identity/kind mismatch')
            require(entry['effective_state'] in CURRENT | {'admitted-historical', 'local-admitted-historical', 'candidate-reconstructed'}, 'unadmitted/withdrawn endpoint')
        qc = rc['qualifier_contract']
        errors = list(Draft202012Validator({'type': 'object', 'additionalProperties': False,
                  'properties': qc['properties'], 'required': qc['required_axes']}).iter_errors(payload['qualifiers']))
        require(not errors, 'invalid relation qualifiers under new cut')
    return ident, c['semantic_kind']


def classify(data, snapshot, selections, identity_bindings, bindings):
    """Pure review classifier. Only prepare/apply supply independently verified data."""
    require(isinstance(selections, list) and 0 < len(selections) <= 1000, 'invalid selected result count')
    index = _target_index(data, bindings)
    rows, records, touched, identities = [], {}, set(), set()
    subjects = copy.deepcopy(snapshot['subjects'])
    for selected in selections:
        _closed(selected, ['version_ref', 'new_carrier_ref', 'disposition', 'reason'])
        version = selected['version_ref']
        require(isinstance(version, str) and version not in touched, 'duplicate selected revision')
        touched.add(version)
        require(selected['disposition'] in ['carry', 'exclude'] and isinstance(selected['reason'], str)
                and selected['reason'].strip(), 'explicit carry/exclusion reason required')
        require(version in index and version in data['projection']['subjects'], 'selection is not a committed local result')
        old = data['projection']['subjects'][version]
        target = index[version]['target']
        record = target['record']
        row = {**selected, 'identity': old['identity'], 'category': target['category'],
               'predecessor_ref': target['predecessor_ref'], 'kind': old['kind'],
               'record_sha256': byte_digest(encoded(record)), 'provenance': index[version]['provenance'],
               'classification': 'excluded', 'diagnostics': []}
        if selected['disposition'] == 'exclude':
            rows.append(row)
            continue
        if old['identity'] in identities:
            raise RuntimeFault('multiple selected current revisions for one identity')
        identities.add(old['identity'])
        row['classification'] = 'eligible'
        if target['operation'] == 'withdraw' or old['effective_state'] != 'local-admitted-current':
            row['classification'] = 'conflicting'; row['diagnostics'].append('selected result is withdrawn or historical')
        elif version in snapshot['subjects']:
            row['classification'] = 'already-promoted' if snapshot['subjects'][version]['record'] == record else 'conflicting'
            row['diagnostics'].append('revision already present in new baseline')
        elif any(e['identity'] == old['identity'] and e['effective_state'] in CURRENT for e in snapshot['subjects'].values()):
            # A successor may replace only the exact original predecessor; no
            # silent identity overwrite or synthetic revision identity is allowed.
            predecessor = target['predecessor_ref']
            current = [e for e in snapshot['subjects'].values() if e['identity'] == old['identity'] and e['effective_state'] in CURRENT]
            if len(current) != 1 or current[0]['version_ref'] != predecessor or predecessor not in data['projection']['subjects'] or current[0]['record'] != data['projection']['subjects'][predecessor]['record']:
                row['classification'] = 'conflicting'; row['diagnostics'].append('identity collision or changed predecessor')
        if row['classification'] == 'eligible':
            try:
                c = _contract(snapshot, selected['new_carrier_ref'])
                ident = _record_identity(record, target['category'], selected['new_carrier_ref'], c, identity_bindings)
                require(ident == old['identity'], 'new carrier changes exact identity')
                require(version == record['artifact_type_ref'] if target['category'] == 'artifact-type'
                        else version.startswith(ident + '@'), 'revision identity mismatch')
                subjects[version] = {**old, 'carrier_ref': selected['new_carrier_ref'], 'kind': c['semantic_kind'],
                                     'effective_state': 'candidate-reconstructed'}
                row['kind'] = c['semantic_kind']
                records[version] = copy.deepcopy(record)
            except (RuntimeFault, KeyError, TypeError) as exc:
                row['classification'] = 'conflicting'; row['diagnostics'].append(str(exc))
        rows.append(row)
    # Validate all selected endpoints together, then propagate dependent failures.
    for _ in range(len(rows) + 1):
        changed = False
        for row in rows:
            if row['classification'] != 'eligible':
                continue
            try:
                _validate(records[row['version_ref']], row['category'], row['new_carrier_ref'], snapshot, identity_bindings, subjects)
            except Exception as exc:
                row['classification'] = 'conflicting'; row['diagnostics'].append('new contract validation: ' + str(exc))
                records.pop(row['version_ref'], None); subjects.pop(row['version_ref'], None); changed = True
        if not changed:
            break
    return rows, records


def _selection_again(selection):
    require(isinstance(selection, Selection), 'independent selection required')
    c = selection.controls
    return select(selection.repo, profile_path=c['profile']['path'], profile_sha256=c['profile']['sha256'],
                  policy_path=c['policy']['path'], executable_manifest_path=c['executable_manifest']['path'],
                  review_path=c['selection_review']['path'], review_sha256=c['selection_review']['sha256'])


def prepare_transition(parent, selection, selections, identity_binding_path, identity_binding_sha256, policy):
    require(isinstance(parent, VerifiedLegacyReadStore), 'independent old-store verifier required')
    policy_core = policy.core()
    data = parent.verify_full()
    bindings = committed_files(parent, data)
    require(policy.branch_id != data['config']['store_id'], 'successor must have a separate branch identity')
    dest = Path(policy.destination)
    require(not dest.is_relative_to(parent.path) and not parent.path.is_relative_to(dest), 'old/new branch overlap')
    for repo in [parent.repository, parent.executable_repo, selection.repo]:
        if dest.is_relative_to(repo):
            require(dest.is_relative_to(repo / '.local'), 'runtime branch must live outside tracked repository paths')
    snapshot = capture(_selection_again(selection))
    raw = _file_bytes(identity_binding_path)
    require(byte_digest(raw) == identity_binding_sha256, 'exact identity mapping pin mismatch')
    identity_bindings = loads(raw)
    rows, records = classify(data, snapshot, selections, identity_bindings, bindings)
    require(committed_files(parent, data) == bindings, 'old committed bytes changed during planning')
    plan = {'schema_version': 'lab-branch-transition/v1-candidate', 'authority_effect': 'none',
        'branch_id': policy.branch_id, 'destination': policy.destination, 'policy': policy_core,
        'policy_sha256': digest(policy_core), 'parent': {'store_id': data['config']['store_id'],
            'head': data['head']['transaction_digest'], 'baseline_snapshot_digest': parent.pins.baseline_snapshot_digest,
            'config_sha256': parent.pins.config_sha256, 'committed_files': bindings,
            'verification': 'independent pinned full replay; no copied transactions or signatures'},
        'new_baseline': {'snapshot_digest': snapshot['snapshot_digest'], 'profile_sha256': snapshot['source_profile_sha256'],
            'source_cut': snapshot['expected_cut'], 'identity_bindings_sha256': identity_binding_sha256},
        'selections': copy.deepcopy(selections), 'classifications': rows,
        'record_postimages': {v: byte_digest(encoded(r)) for v, r in records.items()},
        'effects': {'reconstructed_count': len(records), 'global_admissions': 0, 'global_registry_changes': 0,
                    'candidate_posture': 'candidate-reconstructed', 'external_effects': 0},
        'applicable': all(r['classification'] in ['eligible', 'excluded'] for r in rows)}
    errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(plan))
    require(not errors, 'invalid transition plan: ' + '; '.join(e.message for e in errors[:3]))
    return {'plan': plan, 'baseline': snapshot, 'records': records, 'identity_binding_bytes': raw,
            'parent_path': str(parent.path)}


def authorize_transition(prepared, policy, private_key, *, approved_at=None):
    plan = prepared['plan']
    require(plan['policy'] == policy.core() and plan['applicable'], 'plan is not authorizable')
    private_key = Path(private_key)
    require(not private_key.is_symlink() and stat.S_IMODE(private_key.stat().st_mode) == 0o600, 'private key must be mode 0600 regular file')
    for root in [Path(policy.destination), Path(prepared['parent_path']), Path(__file__).resolve().parents[5]]:
        require(not private_key.resolve().is_relative_to(root), 'private key must be outside repository and successor branch')
    private = serialization.load_pem_private_key(_file_bytes(private_key), password=None)
    require(isinstance(private, Ed25519PrivateKey), 'Ed25519 approval key required')
    public = private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw).hex()
    require(public == policy.public_key, 'approval key differs from trusted adapter')
    when = approved_at or datetime.now(timezone.utc).isoformat()
    require(_date(when) <= datetime.now(timezone.utc) and _date(when) < _date(policy.expires_at), 'approval outside policy interval')
    core = {'schema_version': 'lab-branch-transition-approval/v1-candidate', 'plan_digest': digest(plan),
            'policy_sha256': digest(policy.core()), 'approved_at': when, 'outcome': policy.effect}
    return {**core, 'signature': private.sign(encoded(core)).hex()}


def _approval(approval, plan, policy, *, enforce_expiry=False):
    _closed(approval, ['schema_version', 'plan_digest', 'policy_sha256', 'approved_at', 'outcome', 'signature'])
    require(approval['schema_version'] == 'lab-branch-transition-approval/v1-candidate'
            and approval['plan_digest'] == digest(plan) and approval['policy_sha256'] == digest(policy.core())
            and approval['outcome'] == policy.effect and plan['policy'] == policy.core(), 'approval binds different exact effects')
    when = _date(approval['approved_at'])
    require(when < _date(policy.expires_at), 'approval outside policy interval')
    if enforce_expiry:
        require(when <= datetime.now(timezone.utc) < _date(policy.expires_at), 'transition policy expired or future approval')
    try:
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(policy.public_key)).verify(
            bytes.fromhex(approval['signature']), encoded({k:v for k,v in approval.items() if k != 'signature'}))
    except (InvalidSignature, ValueError, TypeError) as exc:
        raise RuntimeFault('invalid transition approval signature') from exc


def _pins(plan, head):
    return BranchPins(plan['branch_id'], digest(plan), plan['new_baseline']['snapshot_digest'],
        plan['new_baseline']['profile_sha256'], plan['policy_sha256'], digest(head))


def replay_successor(path, pins, policy):
    """Cold verified reconstruction. Ignores no files and trusts no stored pins."""
    path = Path(path)
    require(not path.is_symlink() and path.is_dir(), 'successor root symlink/missing')
    raw_files = {}
    for p in path.rglob('*'):
        require(not p.is_symlink(), 'successor symlink forbidden')
        if p.is_file():
            raw_files[p.relative_to(path).as_posix()] = _file_bytes(p)
    require('HEAD.json' in raw_files, 'incomplete genesis: no committed HEAD')
    head = loads(raw_files['HEAD.json'])
    _closed(head, ['schema_version', 'branch_id', 'plan_digest', 'files'])
    require(head['schema_version'] == 'lab-successor-genesis-head/v1-candidate' and digest(head) == pins.head_digest, 'independent HEAD pin mismatch')
    require(set(raw_files) == set(head['files']) | {'HEAD.json'}, 'successor file closure mismatch')
    for name, sha in head['files'].items():
        require(byte_digest(raw_files[name]) == sha, 'successor original bytes changed: ' + name)
    plan = loads(raw_files['plan.json'])
    require(plan['branch_id'] == pins.branch_id == policy.branch_id == head['branch_id']
            and digest(plan) == pins.plan_digest == head['plan_digest'], 'independent plan/branch pin mismatch')
    require(digest(policy.core()) == pins.policy_sha256 == plan['policy_sha256'], 'independent policy pin mismatch')
    _approval(loads(raw_files['approval.json']), plan, policy)
    require(plan['applicable'], 'conflicting/duplicate transition cannot have a genesis')
    snapshot = loads(raw_files['baseline.json'])
    require(snapshot['snapshot_digest'] == pins.baseline_snapshot_digest == plan['new_baseline']['snapshot_digest'], 'independent new baseline pin mismatch')
    verify_snapshot(snapshot, expected_profile_sha256=pins.profile_sha256)
    raw_bindings = raw_files['identity-bindings.json']
    require(byte_digest(raw_bindings) == plan['new_baseline']['identity_bindings_sha256'], 'identity mapping bytes changed')
    identities = loads(raw_bindings)
    records, subjects = {}, copy.deepcopy(snapshot['subjects'])
    rows = [r for r in plan['classifications'] if r['classification'] == 'eligible']
    require({r['version_ref'] for r in rows} == set(plan['record_postimages']), 'selected postimage closure mismatch')
    for row in rows:
        version = row['version_ref']; sha = plan['record_postimages'][version]
        raw = raw_files['records/' + sha + '.json']
        require(sha == row['record_sha256'] and byte_digest(raw) == sha, 'reconstructed record byte mismatch')
        record = loads(raw)
        require(encoded(record) == raw, 'record is not exact reconstructed postimage encoding')
        c = _contract(snapshot, row['new_carrier_ref'])
        ident = _record_identity(record, row['category'], row['new_carrier_ref'], c, identities)
        require(ident == row['identity'] and version not in snapshot['subjects'], 'reconstruction identity conflict')
        records[version] = record
        subjects[version] = {'identity': ident, 'version_ref': version, 'kind': c['semantic_kind'],
            'category': row['category'], 'carrier_ref': row['new_carrier_ref'], 'record': record,
            'effective_state': 'candidate-reconstructed', 'decision_ref': None,
            'source': {'path': 'records/' + sha + '.json', 'sha256': sha}, 'provenance': row['provenance']}
    for row in rows:
        _validate(records[row['version_ref']], row['category'], row['new_carrier_ref'], snapshot, identities, subjects)
    require({name: byte_digest(_file_bytes(path / name)) for name in raw_files} == {name: byte_digest(raw) for name, raw in raw_files.items()}, 'successor bytes changed during replay')
    return {'branch_id': pins.branch_id, 'records': records, 'subjects': subjects,
            'plan': plan, 'head': head, 'baseline': snapshot, 'authority_effect': 'none', 'cold_replay': True}


def _fsync(fd):
    os.fsync(fd)


def _write_stage(parent_fd, name, files):
    os.mkdir(name, mode=0o700, dir_fd=parent_fd)
    fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent_fd)
    try:
        os.mkdir('records', mode=0o700, dir_fd=fd)
        rfd = os.open('records', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
        try:
            for path, raw in files.items():
                directory, filename = (rfd, path.split('/')[1]) if path.startswith('records/') else (fd, path)
                out = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=directory)
                with os.fdopen(out, 'wb') as f:
                    f.write(raw); f.flush(); os.fsync(f.fileno())
            _fsync(rfd); _fsync(fd); _fsync(parent_fd)
        finally:
            os.close(rfd)
    finally:
        os.close(fd)


def _publish(parent_fd, stage, destination):
    libc = ctypes.CDLL(None, use_errno=True)
    fn = getattr(libc, 'renameat2', None)
    require(fn is not None, 'atomic no-replace directory publish unavailable')
    fn.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    fn.restype = ctypes.c_int
    rc = fn(parent_fd, os.fsencode(stage), parent_fd, os.fsencode(destination), 1)  # RENAME_NOREPLACE
    if rc:
        error = ctypes.get_errno()
        raise RuntimeFault('no-replace publish rejected: ' + os.strerror(error))
    _fsync(parent_fd)


def apply_transition(parent, selection, prepared, approval, identity_binding_path, policy, *, crash_at=None):
    """Local effect gate: fresh full verification, exact signature, atomic genesis.

    crash_at is an isolated-fixture fault injection hook; it exits the process.
    Existing final branches are cold-verified for idempotent retry. Unknown or
    incomplete stages are retained for explicit investigation, never deleted.
    """
    require(crash_at in [None, 'after-stage', 'before-publish', 'after-publish'], 'unknown crash hook')
    dest = Path(policy.destination)
    # Shared lock prevents this transition racing a cooperating legacy writer.
    lock_fd = os.open(parent.path / '.writer.lock', os.O_RDONLY | os.O_NOFOLLOW)
    try:
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_SH | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeFault('parent branch writer active') from exc
        new = prepare_transition(parent, selection, prepared['plan']['selections'], identity_binding_path,
              prepared['plan']['new_baseline']['identity_bindings_sha256'], policy)
        require(new['plan'] == prepared['plan'] and new['records'] == prepared['records']
                and new['baseline'] == prepared['baseline'], 'stale transition proposal; review a fresh plan')
        plan = new['plan']
        require(plan['applicable'], 'conflicting/duplicate selections block transition')
        _approval(approval, plan, policy, enforce_expiry=True)
        files = {'plan.json': encoded(plan), 'baseline.json': encoded(new['baseline']),
                 'approval.json': encoded(approval), 'identity-bindings.json': new['identity_binding_bytes']}
        files.update({'records/' + byte_digest(encoded(r)) + '.json': encoded(r) for r in new['records'].values()})
        head = {'schema_version': 'lab-successor-genesis-head/v1-candidate', 'branch_id': policy.branch_id,
                'plan_digest': digest(plan), 'files': {name: byte_digest(raw) for name, raw in files.items()}}
        files['HEAD.json'] = encoded(head); pins = _pins(plan, head)
        if os.path.lexists(dest):
            replay_successor(dest, pins, policy)
            return {'idempotent': True, 'recovered': False, 'pins': asdict(pins), 'authority_effect': 'none'}
        require(dest.parent.is_dir() and not dest.parent.is_symlink(), 'destination parent must already exist')
        fd = os.open(dest.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            # Use the opened directory capability, and reject relocated parent paths.
            require(os.path.realpath('/proc/self/fd/' + str(fd)) == str(dest.parent), 'destination parent moved')
            stage = '.' + dest.name + '.transition-' + digest(plan)
            capability = Path('/proc/self/fd/' + str(fd))
            recovered = os.path.lexists(capability / stage)
            if recovered:
                replay_successor(capability / stage, pins, policy)
            else:
                _write_stage(fd, stage, files)
            if crash_at in ['after-stage', 'before-publish']:
                os._exit(75)
            require(freshness(selection.repo, new['baseline'])['status'] == 'current', 'new source cut changed before publish')
            require(committed_files(parent, parent.verify_full()) == plan['parent']['committed_files'], 'old branch changed before publish')
            require(os.path.realpath('/proc/self/fd/' + str(fd)) == str(dest.parent), 'destination parent moved')
            _publish(fd, stage, dest.name)
            if crash_at == 'after-publish':
                os._exit(76)
        finally:
            os.close(fd)
        replay_successor(dest, pins, policy)
        return {'idempotent': False, 'recovered': recovered, 'pins': asdict(pins), 'authority_effect': 'none'}
    finally:
        os.close(lock_fd)
