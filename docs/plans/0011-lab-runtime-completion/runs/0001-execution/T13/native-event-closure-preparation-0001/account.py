"""Public intent accounting only. No event, Decision, stable core or effect writer."""
import argparse
import hashlib
import json
import os
import stat
from pathlib import Path

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE = Path(__file__).absolute().parent
BLOCKERS = (
    'T10-grounded-representation-and-native-scope-route-unresolved',
    'T11-current-accountable-owner-role-scope-interval-unresolved',
    'T13-no-selected-original-adoption-response-envelope-validation-rule',
    'T13-current-native-archive-and-per-stream-predecessor-validation-pending',
    'R08-actual-exact-positive-owner-response-and-Decision-absent',
    'A01-accepted-append-authority-absent',
)

def need(value, message):
    if not value:
        raise ValueError(message)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def parse(raw):
    def pairs(items):
        out = {}
        for key, value in items:
            need(key not in out, 'duplicate JSON key')
            out[key] = value
        return out
    return json.loads(raw, object_pairs_hook=pairs,
        parse_constant=lambda _: need(False, 'nonfinite JSON'))

def capture(row):
    """Exact selected public bytes, held no-follow descriptors and attachments."""
    need(type(row) is dict and set(row) <= {'path', 'sha256', 'size_bytes', 'selection'}
         and {'path', 'sha256'} <= set(row), 'closed public input binding')
    p = Path(row['path'])
    need(not p.is_absolute() and p.as_posix() == row['path'] and '..' not in p.parts
         and p.name not in {'native.snapshot', 'branch.snapshot'} and '\\' not in row['path'],
         'canonical public locator; private native archive bodies excluded')
    p = ROOT / p
    handles = [os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)]
    links = []
    try:
        parent = handles[-1]
        for name in p.parts[1:-1]:
            child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            handles.append(child); links.append((parent, name, child, os.fstat(child)))
            parent = child
        leaf = os.open(p.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        handles.append(leaf); before = os.fstat(leaf)
        need(stat.S_ISREG(before.st_mode) and before.st_size <= 32 * 1024 * 1024, 'bounded regular public input')
        blocks = []; size = 0
        while block := os.read(leaf, 1024 * 1024):
            size += len(block); need(size <= 32 * 1024 * 1024, 'input grew'); blocks.append(block)
        raw = b''.join(blocks)
        def stamp(s):
            return (s.st_dev, s.st_ino, s.st_mode, s.st_uid, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        need(stamp(before) == stamp(os.fstat(leaf)) == stamp(os.stat(p.name, dir_fd=parent, follow_symlinks=False))
             and sha(raw) == row['sha256'] and len(raw) == row.get('size_bytes', len(raw)), 'input bytes or attachment changed')
        for anchor, name, held, old in reversed(links):
            attached = os.stat(name, dir_fd=anchor, follow_symlinks=False); actual = os.fstat(held)
            identity = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_uid)
            need(identity(old) == identity(attached) == identity(actual), 'public ancestor detached')
        return raw
    finally:
        for handle in reversed(handles):
            os.close(handle)

def analyze(selection):
    need(type(selection) is dict and set(selection) == {
        'schema_version', 'authority_effect', 'task_complete', 'original_preparation_binding',
        'final_selection_binding', 'files', 'expected_intent_count',
        'native_archive_body_read_or_copy_allowed', 'real_owner_response_allowed',
        'private_body_export_allowed', 'shared_or_native_changes_allowed'}, 'closed selected packet')
    need(selection['schema_version'] == 'lab-T13-native-event-proof-inputs/v1-candidate'
         and selection['authority_effect'] == 'none' and selection['task_complete'] is False
         and selection['expected_intent_count'] == 88
         and all(selection[k] is False for k in ['native_archive_body_read_or_copy_allowed',
             'real_owner_response_allowed', 'private_body_export_allowed', 'shared_or_native_changes_allowed']),
         'public preparation only')
    files = {r['path']: r for r in selection['files']}
    need(len(files) == len(selection['files']), 'duplicate public selection')
    # Metadata body files are hashed only. They are never parsed, copied or emitted.
    for row in files.values():
        capture(row)
    for row in [selection['original_preparation_binding'], selection['final_selection_binding']]:
        need(files.get(row['path'], {}).get('sha256') == row['sha256'], 'independent selector absent')
    preparation = parse(capture(selection['original_preparation_binding']))
    final = parse(capture(selection['final_selection_binding']))
    members = [r for r in preparation['members'] if r['member_class'] == 'representation-adoption-intent']
    need(len(members) == 88 and len({r['member_ref'] for r in members}) == 88, 'all88 ordered unique original members')
    final_members = {r['member_ref']: r for r in final['members'] if r['member_class'] == 'representation-adoption-intent'}
    need(set(final_members) == {r['member_ref'] for r in members}, 'final original event accounting differs')
    rows = []; semantic_cursors = set(); predecessor_cursors = set()
    for member in members:
        need(member['postimage_binding'] == member['targets'][0]
             and all(member[k] is None for k in ['actual_answering_principal_ref', 'actual_owner_outcome', 'selected_outcome'])
             and member['current_owner_authority_verified'] is False and member['authority_effect'] == 'none',
             'original preparation invents owner or consequence')
        intent = parse(capture(member['postimage_binding']))
        need(intent['schema_version'] == 'lab-O06-representation-adoption-intent/v1-candidate'
             and intent['actual_owner_outcome'] is None and intent['authority_effect'] == 'none'
             and intent['owner_outcome_required'] is True and intent['verified_owner_required'] is True
             and intent['consequence_rule']['provenance_requires_actual_owner_Decision_binding'] is True
             and intent['consequence_rule']['append_new_governance_event_after_exact_R08_member_acceptance'] is True,
             'original actual owner/append condition weakened')
        need(intent['semantic_tuple'] == member['scope']['exact_semantic_tuple']
             and intent['predecessor_governance_tuple'] == member['scope']['exact_predecessor_governance_tuple']
             and intent['metadata_record_binding'] == member['targets'][1]
             and final_members[member['member_ref']]['original_target_bindings'] == member['targets'],
             'original exact tuple/carrier/scope accounting changed')
        for target in member['targets']:
            need(files.get(target['path'], {}).get('sha256') == target['sha256'], 'original public target missing')
        semantic_cursors.add(intent['semantic_tuple']['semantic_cursor'])
        predecessor_cursors.add(intent['predecessor_governance_tuple']['governance_cursor'])
        rows.append({
            'member_ref': member['member_ref'], 'intent_binding': member['postimage_binding'],
            'intent_byte_sha256': member['postimage_binding']['sha256'],
            'subject_carrier_version_ref': intent['subject_carrier_version_ref'],
            'metadata_record_binding': intent['metadata_record_binding'],
            'archive_binding_declared_only_not_opened': intent['archive_binding'],
            'semantic_tuple': intent['semantic_tuple'],
            'predecessor_governance_tuple': intent['predecessor_governance_tuple'],
            'original_scope': member['scope'], 'original_dependencies': member['dependencies'],
            'original_proposed_owner_roles': member['proposed_owner_roles'],
            'original_requested_axes': member['requested_axes'], 'original_exclusions': member['exclusions'],
            'original_consequence_rule': intent['consequence_rule'],
            'actual_owner_Decision_binding': None, 'actual_owner_response': None,
            'native_event_bytes': None, 'native_event_digest': None, 'stable_unsigned_core': None,
            'status': 'explicitly-blocked-before-native-materialization',
            'blockers': list(BLOCKERS), 'T10_dependency_complete': False, 'T11_dependency_complete': False,
            'single_checkpoint_ready': False, 'authority_effect': 'none',
        })
    need(semantic_cursors == predecessor_cursors == set(range(1, 89)), 'original full1..88 semantic/governance coverage')
    for row in files.values():
        capture(row)
    return {'schema_version': 'lab-T13-all88-native-event-accounting/v1-candidate',
        'authority_effect': 'none', 'task_complete': False, 'actual_materialized_events': 0,
        'explicitly_blocked_intents': 88, 'original_preparation_binding': selection['original_preparation_binding'],
        'final_selection_binding': selection['final_selection_binding'], 'rows': rows,
        'original_private_archive_read_or_copy': False, 'original_metadata_bodies_exported': False,
        'actual_Decision_or_response_or_key_created': False, 'native_calls_or_effects': 0,
        'scope': 'All88 original O06 members retained; T10/T11 and complete36task/73edge goal remain open.'}

def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--selection-sha256', required=True)
    args = parser.parse_args()
    raw = capture({'path': (HERE / 'input-selection.json').relative_to(ROOT).as_posix(), 'sha256': args.selection_sha256})
    value = analyze(parse(raw))
    raw = (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()
    handles = [os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)]; links = []
    try:
        parent = handles[-1]
        for name in HERE.parts[1:]:
            child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            handles.append(child); links.append((parent, name, child, os.fstat(child))); parent = child
        root_info = os.fstat(parent)
        need(root_info.st_uid == os.getuid() and stat.S_IMODE(root_info.st_mode) == 0o700, 'owned preparation output root')
        fd = os.open('ACCOUNTING-88.json', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=parent)
        try:
            offset = 0
            while offset < len(raw):
                offset += os.write(fd, raw[offset:])
            os.fsync(fd)
        finally:
            os.close(fd)
        for anchor, name, held, old in reversed(links):
            actual = os.stat(name, dir_fd=anchor, follow_symlinks=False)
            need((actual.st_dev, actual.st_ino) == (old.st_dev, old.st_ino), 'owned output root detached')
    finally:
        for handle in reversed(handles):
            os.close(handle)
    print(json.dumps({'result': 'PREPARED-all88-explicitly-blocked', 'accounting_sha256': sha(raw),
        'events_created': 0, 'Decisions_created': 0, 'native_calls': 0, 'task_complete': False}))

if __name__ == '__main__':
    main()
