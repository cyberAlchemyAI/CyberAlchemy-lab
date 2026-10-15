"""T33 candidate: verify independent host attestations; never create an approval.

The coordinator supplies TrustContext and Selection from independent trusted
sources. Neither object is accepted from the ingress request. See CONTRACT.md.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


VERSION = 'lab-authentic-owner-ingress/v1-candidate'
ADMIT = 'admit-exact-independent-repository-effects'
OUTCOMES = {ADMIT, 'reject-exact-review', 'revise-exact-review'}


class Refusal(ValueError):
    pass


def require(condition, reason):
    if not condition:
        raise Refusal(reason)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode('utf-8')


def digest(value):
    return sha256(encoded(value)).hexdigest()


def legacy_core_digest(value):
    # Original promotion hashes exact pretty-printed material bytes, whereas
    # review/authority and new signed evidence use compact semantic digests.
    return sha256((json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False,
                             allow_nan=False) + '\n').encode('utf-8')).hexdigest()


def parse(raw):
    require(type(raw) is bytes and len(raw) <= 1024 * 1024, 'bounded ingress bytes required')
    def pairs(items):
        value = {}
        for key, item in items:
            require(key not in value, 'duplicate JSON key')
            value[key] = item
        return value
    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda _: require(False, 'nonfinite JSON'))
    except (UnicodeDecodeError, ValueError) as exc:
        raise Refusal('invalid ingress JSON') from exc


def closed(value, fields):
    require(type(value) is dict and set(value) == set(fields), 'closed fields required')


def text(value):
    require(type(value) is str and bool(value.strip()), 'nonempty text required')
    return value


def pin(value):
    require(type(value) is str and re.fullmatch('[0-9a-f]{64}', value), 'SHA256 pin required')
    return value


def timestamp(value):
    require(type(value) is str and re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ', value),
            'UTC timestamp required')
    try:
        return datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise Refusal('invalid timestamp') from exc


@dataclass(frozen=True)
class TrustContext:
    """Installed out of band; fixture contexts can never authorize publication."""
    host_issuer: str
    host_public_key: str
    role_issuer: str
    role_public_key: str
    mechanism_ref: str
    governing_registry_ref: str
    usage: str  # 'technical-fixture' or independently installed 'actual-owner'


@dataclass(frozen=True)
class Selection:
    """Independent coordinator selection, never derived from response fields."""
    review_sha256: str
    authority_proof_sha256: str
    presentation_sha256: str
    message_sha256: str
    registry_cursor: str
    principal_ref: str
    scope_ref: str


def signed(envelope, issuer, public_key):
    closed(envelope, ('issuer_ref', 'payload', 'signature'))
    require(envelope['issuer_ref'] == issuer, 'unselected issuer')
    try:
        require(re.fullmatch('[0-9a-f]{64}', public_key) is not None, 'invalid trust key')
        require(type(envelope['signature']) is str and
                re.fullmatch('[0-9a-f]{128}', envelope['signature']), 'invalid signature encoding')
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_key)).verify(
            bytes.fromhex(envelope['signature']), encoded({
                'issuer_ref': envelope['issuer_ref'], 'payload': envelope['payload']}))
    except (InvalidSignature, TypeError, ValueError) as exc:
        raise Refusal('issuer signature verification failed') from exc
    return envelope['payload']


def verify(response, review, selection, trust):
    """Verify exact authentic response; returns evidence, not a publication effect.

    Always uses actual wall time. Rejected/revised dispositions are verified but
    cannot pass verify_for_publication. Missing actual host inputs fail closed.
    """
    require(type(trust) is TrustContext and type(selection) is Selection,
            'independent installed context and selection required')
    require(trust.usage in ('technical-fixture', 'actual-owner'), 'unselected trust usage')
    for field in ('host_issuer', 'role_issuer', 'mechanism_ref', 'governing_registry_ref'):
        text(getattr(trust, field))
    require(trust.host_issuer != trust.role_issuer and
            trust.host_public_key != trust.role_public_key, 'independent role issuer required')
    for field in ('review_sha256', 'authority_proof_sha256', 'presentation_sha256', 'message_sha256'):
        pin(getattr(selection, field))
    for field in ('registry_cursor', 'principal_ref', 'scope_ref'):
        text(getattr(selection, field))
    closed(response, ('schema_version', 'authority_proof', 'presentation', 'message'))
    require(response['schema_version'] == VERSION, 'fixture key adapter is not actual owner ingress')
    require(digest(review) == selection.review_sha256, 'independently selected review changed')
    for field, expected in (('authority_proof', selection.authority_proof_sha256),
                            ('presentation', selection.presentation_sha256),
                            ('message', selection.message_sha256)):
        require(digest(response[field]) == expected, 'independently selected evidence changed: ' + field)
    authority = review['authority']
    require(review['authority_sha256'] == digest(authority), 'review authority digest mismatch')
    require(authority['principal_ref'] == selection.principal_ref and
            authority['scope_ref'] == selection.scope_ref, 'review principal/scope mismatch')
    cores = review['independent_cores']
    core_pins = [legacy_core_digest(core) for core in cores]
    require(bool(cores) and review['core_sha256s'] == core_pins and
            len(set(core_pins)) == len(core_pins), 'complete unique member cores required')
    require(len(review['targets']) == len(cores), 'target/member cardinality mismatch')
    roles = authority['owner_roles']
    require(type(roles) is dict and bool(roles), 'governing owner roles missing')
    for target, core in zip(review['targets'], cores):
        require(target['category'] in roles and core['owner_ref'] == roles[target['category']]
                and core['target_ref'] == target['version_ref'], 'member governing role/target mismatch')
    role = signed(response['authority_proof'], trust.role_issuer, trust.role_public_key)
    closed(role, ('schema_version', 'registry_ref', 'registry_cursor', 'principal_ref', 'scope_ref',
                  'governing_roles', 'authority_sha256', 'source_evidence', 'valid_from', 'valid_until',
                  'resolution', 'permitted_effect'))
    require(role['schema_version'] == 'lab-governing-owner-evidence/v1-candidate' and
            role['registry_ref'] == trust.governing_registry_ref and
            role['registry_cursor'] == selection.registry_cursor and
            role['principal_ref'] == selection.principal_ref and
            role['scope_ref'] == selection.scope_ref and role['governing_roles'] == roles and
            role['authority_sha256'] == digest(authority) and
            role['resolution'] == 'independently-resolved-current-governing-authority' and
            role['permitted_effect'] == 'one-exact-immutable-repository-bundle',
            'current independently selected governing authority required')
    require(type(role['source_evidence']) is list and bool(role['source_evidence']),
            'governing authority source provenance absent')
    refs = []
    for row in role['source_evidence']:
        closed(row, ('ref', 'sha256')); refs.append(text(row['ref'])); pin(row['sha256'])
    require(len(set(refs)) == len(refs), 'duplicate role evidence')
    now = datetime.now(timezone.utc)
    start, end = timestamp(role['valid_from']), timestamp(role['valid_until'])
    require(start <= now < end and now < timestamp(authority['expires_at']), 'expired/current authority absent')
    presentation = signed(response['presentation'], trust.host_issuer, trust.host_public_key)
    closed(presentation, ('schema_version', 'mechanism_ref', 'presentation_id', 'conversation_id',
                          'principal_ref', 'review_sha256', 'authority_sha256', 'bundle_id', 'bundle_path',
                          'decision_core_sha256s', 'displayed_material_sha256', 'presented_at'))
    require(presentation['schema_version'] == 'lab-host-review-presentation/v1-candidate' and
            presentation['mechanism_ref'] == trust.mechanism_ref and
            presentation['principal_ref'] == selection.principal_ref and
            presentation['review_sha256'] == selection.review_sha256 and
            presentation['authority_sha256'] == digest(authority) and
            presentation['bundle_id'] == review['bundle_id'] and
            presentation['bundle_path'] == review['bundle_path'] and
            presentation['decision_core_sha256s'] == core_pins,
            'host did not present this exact review to selected owner')
    pin(presentation['displayed_material_sha256'])
    text(presentation['presentation_id']); text(presentation['conversation_id'])
    message = signed(response['message'], trust.host_issuer, trust.host_public_key)
    closed(message, ('schema_version', 'mechanism_ref', 'message_id', 'conversation_id', 'principal_ref',
                     'interaction_kind', 'content', 'content_sha256', 'presentation_sha256',
                     'review_sha256', 'authority_proof_sha256', 'selected_outcome', 'recorded_at'))
    require(message['schema_version'] == 'lab-host-owner-message/v1-candidate' and
            message['mechanism_ref'] == trust.mechanism_ref and
            message['interaction_kind'] == 'human-explicit-review-disposition' and
            message['principal_ref'] == selection.principal_ref and
            message['conversation_id'] == presentation['conversation_id'] and
            message['presentation_sha256'] == selection.presentation_sha256 and
            message['review_sha256'] == selection.review_sha256 and
            message['authority_proof_sha256'] == selection.authority_proof_sha256 and
            message['selected_outcome'] in OUTCOMES,
            'explicit independently attested human disposition absent')
    text(message['message_id']); text(message['content'])
    require(message['content_sha256'] == sha256(message['content'].encode('utf-8')).hexdigest(),
            'actual message content digest mismatch')
    shown, spoken = timestamp(presentation['presented_at']), timestamp(message['recorded_at'])
    require(start <= shown <= spoken <= now and spoken < end, 'message/presentation outside authority period')
    return {'schema_version': VERSION, 'authority_effect': 'none', 'usage': trust.usage,
            'review_sha256': selection.review_sha256, 'authority_sha256': digest(authority),
            'message_sha256': selection.message_sha256, 'message_id': message['message_id'],
            'host_issuer': trust.host_issuer, 'mechanism_ref': trust.mechanism_ref,
            'conversation_id': message['conversation_id'], 'selected_outcome': message['selected_outcome'],
            'bundle_id': review['bundle_id'], 'bundle_path': review['bundle_path'],
            'decision_core_sha256s': core_pins}


def verify_for_publication(response, review, selection, trust):
    """A mandatory new-commit gate; the original publisher is not wired to this yet."""
    result = verify(response, review, selection, trust)
    require(result['selected_outcome'] == ADMIT, 'actual positive owner disposition absent')
    require(trust.usage == 'actual-owner', 'technical fixtures cannot authorize actual R08')
    return result


def ingest(raw, review, selection, trust):
    return verify(parse(raw), review, selection, trust)


class ReplayJournal:
    """Owned persistent reservation per host event, before any new publication.

    Reserve only after verification. Crashes fail closed. Existing committed
    bundles use independently pinned publisher repair, without a new reservation.
    Root must be a coordinator-owned private directory outside request control.
    """
    def __init__(self, root):
        self.root = Path(root)
        require(self.root.is_dir() and not self.root.is_symlink(), 'owned replay root required')
        require((self.root.stat().st_mode & 0o777) == 0o700, 'private replay root required')

    def reserve(self, response, review, selection, trust, *, rehearsal=False):
        result = verify(response, review, selection, trust) if rehearsal else verify_for_publication(
            response, review, selection, trust)
        require(not rehearsal or trust.usage == 'technical-fixture', 'rehearsal only accepts fixture trust')
        event = digest({key: result[key] for key in ('host_issuer', 'mechanism_ref',
                                                    'conversation_id', 'message_id')})
        destination = self.root / (event + '.json')
        try:
            fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        except FileExistsError as exc:
            raise Refusal('host message replay or prior reservation') from exc
        with os.fdopen(fd, 'wb') as handle:
            handle.write(encoded(result)); handle.flush(); os.fsync(handle.fileno())
        directory = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
        return result
