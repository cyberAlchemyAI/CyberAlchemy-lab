"""Private local operator reads from independently selected original signed cuts.

This is the selected CLI journey, not the proposed 34-operation API dispatcher.
No received message grants authority and no operation here signs or applies.
"""
import argparse
import base64
from collections import Counter
from contextlib import contextmanager
import copy
from pathlib import Path
import re
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'coupling'))
from loader import EnginePins, ROOT, sha, parse, encoded, original, require, bind, engine, verify_engine

SELECTION = HERE / 'source-selection.json'
SELECTION_SHA = 'e5dc904cf36e458e94a06cfc25c434f6ad6ec7d8d4f8783d225a5e39858c6008'
PINS = EnginePins('53e2f74c53f123b42d60d3cc3b4c66e75f3fa0c4c9a3142bf3f11e7500bd9677',
    'lab-operator-signed-coupling/v1-candidate',
    '4594cab2172646b1c2157e0a4be37f560088c580de875fd7d269925993fe1f0b',
    'cbfe3d7c5f92d0bc547b836a9d84616b9be26cb399a587aab8800f93fd96ed58')
MAX_ARCHIVE = 64 * 1024 * 1024
MAX_ENTRIES = 1000
CLAIM = 'Exact private isolated signed candidate cut; no final repository admission, implementation satisfaction, human pilot or live runtime outcome.'


def source_selection(name):
    require(sha(SELECTION.read_bytes()) == SELECTION_SHA, 'independent source selection pin differs')
    selection = parse(SELECTION.read_bytes())
    rows = [r for r in selection['sources'] if r['name'] == name]
    require(len(rows) == 1, 'selected source not found')
    return rows[0]


@contextmanager
def replay_source(name, *, source_repo=ROOT):
    """Original-byte signature replay only, with currentness reported separately.

    source_repo is for isolated read-currentness probes; the executable and archive
    are always independently selected at ROOT. A CLI client cannot select it.
    """
    row = source_selection(name)
    require(row['engine_pins'] == PINS.__dict__, 'selected executable pins differ')
    path = ROOT / row['archive_binding']['path']
    require(path.stat().st_size <= MAX_ARCHIVE, 'selected archive exceeds bounded input')
    archive = parse(original(row['archive_binding']))
    expected = parse(original(row['expected_replay_binding']))
    require(archive['engine_pins'] == expected['engine_pins'] == PINS.__dict__, 'archived executable differs')
    require(archive['config_sha256'] == expected['config_sha256'] == row['config_sha256']
        and archive['baseline_snapshot_digest'] == expected['baseline_snapshot_digest'] == row['baseline_snapshot_digest']
        and archive['expected_head'] == expected['expected_head'] == row['expected_head'], 'independent source cut differs')
    require(archive['authority_effect'] == 'none' and archive['actual_owner_outcome'] is None
        and archive['private_key_included'] is archive['Session_memory_included'] is archive['runtime_activation'] is False,
        'archived forbidden state')
    head = parse(base64.b64decode(archive['files']['HEAD.json']['base64_original_bytes'], validate=True))
    require(type(head['sequence']) is int and 0 <= head['sequence'] <= 100, 'inspection transaction budget exceeded')
    names = {'config.json','baseline.json','HEAD.json'} | {f'transactions/{i:010d}.json' for i in range(head['sequence'] + 1)}
    require(set(archive['files']) == names, 'closed original store file set required')
    with tempfile.TemporaryDirectory(prefix='cal-R03-operator-read-') as temp, engine(PINS) as handle:
        store = Path(temp) / 'store'; store.mkdir(); (store / 'transactions').mkdir()
        originals = {}
        for name, binding in archive['files'].items():
            require(set(binding) == {'sha256','base64_original_bytes'}, 'closed archived byte binding required')
            raw = base64.b64decode(binding['base64_original_bytes'], validate=True)
            require(sha(raw) == binding['sha256'], 'archived original bytes differ')
            parse(raw)
            target = store / name
            with target.open('xb') as stream:
                stream.write(raw)
            originals[name] = raw
        require(sha(originals['config.json']) == row['config_sha256'], 'original configuration differs')
        config = parse(originals['config.json'])
        require(config['endpoint_engine_id'] == PINS.engine_id
            and config['endpoint_mapping_binding']['sha256'] == PINS.mapping_sha256
            and config['endpoint_mapping_authority'] == 'isolated-candidate-local-interpretation', 'selected mapping configuration differs')
        data = handle.store_module.Store(store, Path(source_repo)).replay()
        require(data['head']['transaction_digest'] == row['expected_head']
            and data['baseline']['snapshot_digest'] == row['baseline_snapshot_digest']
            and handle.common.digest(data['projection']) == expected['projection_sha256']
            and [handle.common.digest(tx) for tx in data['transactions']] == expected['transaction_sha256s'],
            'signed projection or original transaction parity differs')
        view = Inspection(data, row, originals, handle)
        yield view
        require(all((store / name).read_bytes() == raw for name, raw in originals.items()), 'inspection changed original store bytes')
        require({p.relative_to(store).as_posix() for p in store.rglob('*') if p.is_file()} == names,
            'inspection created store state or Session memory')


def facets(subject):
    record = subject['record']; payload = record.get('payload', {})
    return {'admission': subject['effective_state'],
        'authored_lifecycle': record.get('lifecycle_state') or record.get('classification', {}).get('lifecycle_posture_ref'),
        'domain': payload.get('domain_state'), 'implementation': record.get('implementation_status'),
        'runtime_observation': payload.get('runtime_observation'), 'outcome': payload.get('outcome'),
        'inference_rule': 'Only explicitly recorded facets; admission never supplies implementation, liveness or satisfaction.'}


def differences(before, after, path=''):
    """Deterministic structural diff, without pretending to be original byte diff."""
    if before == after:
        return []
    if type(before) is dict and type(after) is dict:
        rows = []
        for key in sorted(set(before) | set(after)):
            pointer = path + '/' + key.replace('~','~0').replace('/','~1')
            if key not in before:
                rows.append({'path': pointer, 'change': 'add', 'after': after[key]})
            elif key not in after:
                rows.append({'path': pointer, 'change': 'remove', 'before': before[key]})
            else:
                rows.extend(differences(before[key], after[key], pointer))
        return rows
    return [{'path': path or '/', 'change': 'replace', 'before': before, 'after': after}]


class Inspection:
    def __init__(self, data, selected, originals, handle):
        self.data = data; self.selected = selected; self.originals = originals; self.handle = handle
        self.subjects = data['projection']['subjects']

    def common(self, command):
        return {'schema_version': 'lab-operator-inspection/v1-candidate', 'command': command,
            'selected_source': self.selected['name'], 'scope_ref': self.data['config']['scope_ref'],
            'source_cut': {'baseline_snapshot_digest': self.data['baseline']['snapshot_digest'],
                'signed_head': self.data['head']['transaction_digest'], 'sequence': self.data['head']['sequence']},
            'source_profile_binding': self.handle.manifest['profile_binding'],
            'source_archive_binding': self.selected['archive_binding'],
            'currentness': self.data['freshness'], 'visibility': 'private-candidate-store-originals',
            'authority_effect': 'none', 'actual_owner_outcome': None, 'claim_ceiling': CLAIM}

    def status(self):
        result = self.common('status')
        result.update(definition_counts=dict(Counter(s['effective_state'] for s in self.subjects.values() if s['category'] == 'definition')),
            subject_count=len(self.subjects), catalog_versions=len(self.data['projection']['contracts']),
            history_cursors={k: len(v['payload']['events']) for k,v in self.data['projection']['histories'].items()},
            repository_runtime_activation='not-observed', local_application_count=len(self.data['transactions']) - 1,
            implemented_cli_commands=['status','definitions','inspect','connections','review','receipt'],
            api_operations_implemented=[], remaining_api_operations=34,
            gaps=['This selected source cut contains admitted Definition revisions; candidate suffixes and candidate directories are not unadmitted evidence.',
                'External/unselected candidate queues are not indexed by this signed source profile.',
                'Authenticated API/stdio and SQLite query parity remain unfinished.',
                'Session continuity and the complete third owner journey are not supplied by this CLI.',
                'Human owner pilot, S02 final envelope and actual R08 outcome are absent.'])
        return result

    def resolve(self, ref):
        if ref in self.subjects:
            return self.subjects[ref]
        rows = [s for s in self.subjects.values() if s['identity'] == ref]
        require(len(rows) != 0, 'artifact not found in selected source cut')
        require(len(rows) == 1, 'ambiguous identity: select one exact version_ref')
        return rows[0]

    def summary(self, subject):
        record = subject['record']
        return {'identity_ref': subject['identity'], 'version_ref': subject['version_ref'],
            'name': record.get('name') or record.get('term') or record.get('title') or subject['identity'],
            'category': subject['category'], 'raw_kind': subject['kind'], 'carrier_ref': subject['carrier_ref'],
            'status_facets': facets(subject), 'source_binding': subject['source'], 'decision_ref': subject.get('decision_ref')}

    def definitions(self, *, state='all', offset=0, limit=50):
        require(type(offset) is int and offset >= 0 and type(limit) is int and 1 <= limit <= MAX_ENTRIES, 'invalid page budget')
        require(state in ('all','admitted-current','admitted-historical','candidate-unadmitted'), 'unknown admission facet')
        rows = sorted((s for s in self.subjects.values() if s['category'] == 'definition'
            and (state == 'all' or s['effective_state'] == state)), key=lambda s:s['version_ref'])
        result = self.common('definitions')
        result.update(selected_admission_state=state, total=len(rows), offset=offset, limit=limit,
            next_offset=offset + limit if offset + limit < len(rows) else None,
            items=[self.summary(s) for s in rows[offset:offset+limit]],
            coverage='Only Definition revisions in the exact signed source profile. Empty candidate-unadmitted selection does not prove the whole repository has no proposals.')
        return result

    def source_record(self, subject):
        binding = subject['source']; path = binding['path']
        if 'store_id' in binding:
            require(binding['store_id'] == self.data['config']['store_id'] and path in self.originals, 'local original source unavailable')
            original_bytes = self.originals[path]
            record = self.handle.common.pointer(parse(original_bytes), binding['selector'])
            require(sha(self.handle.common.encoded(record)) == binding['sha256'], 'embedded canonical record differs')
            return {'encoding': 'inherited-canonical-json-encoding-of-value-selected-from-original-signed-transaction',
                'record_binding': binding, 'original_file_sha256': sha(original_bytes),
                'original_file_is_current': True, 'parsed_record_matches': record == subject['record']}
        require(path in self.data['baseline']['materials']
            and self.data['baseline']['materials'][path] == binding['sha256'], 'source file is not in exact baseline material closure')
        file = ROOT / path
        current = file.is_file() and not file.is_symlink() and sha(file.read_bytes()) == binding['sha256']
        if current:
            value = parse(file.read_bytes())
            record = self.handle.common.pointer(value, binding.get('selector',''))
            require(record == subject['record'], 'original source structure differs from captured record')
        return {'encoding': 'original-repository-file', 'record_binding': binding,
            'original_file_sha256': binding['sha256'], 'original_file_is_current': current,
            'parsed_record_matches': True if current else None,
            'historical_record_basis': 'Verified captured baseline and signed replay; current changed bytes never replace historical content.'}

    def authority(self, subject):
        ref = subject.get('decision_ref')
        local = [s for s in self.subjects.values() if s['identity'] == ref or s['version_ref'] == ref] if ref else []
        bindings = [s['source'] for s in local]
        if ref and not bindings:
            for path, document in self.data['baseline']['documents'].items():
                if isinstance(document, dict) and any(document.get(key) == ref for key in ('decision_id','node_id','decision_ref')):
                    bindings.append({'path': path, 'sha256': self.data['baseline']['materials'][path]})
        return {'selected_decision_ref': ref, 'resolved_evidence_bindings': bindings,
            'resolution_posture': 'resolved-captured-evidence' if bindings else 'reference-only-in-selected-cut',
            'effective_admission': subject['effective_state'],
            'basis': 'Captured admitted source overlay, then independently verified local signed transactions. Authored body labels do not override it.',
            'canonical_effect_from_inspection': False}

    def inspect(self, ref, *, include_body=True):
        subject = self.resolve(ref); result = self.common('inspect')
        result.update(artifact=self.summary(subject), original_source=self.source_record(subject),
            record_structural_sha256=self.handle.common.digest(subject['record']), authority=self.authority(subject),
            gaps=list(subject['record'].get('residue_refs', [])), body=subject['record'] if include_body else None,
            body_included=include_body)
        carrier = subject['carrier_ref'] or subject['record'].get('classification', {}).get('artifact_type_ref')
        contract = self.data['projection']['contracts'].get(carrier)
        result['contract'] = {k: contract.get(k) for k in ('artifact_type_ref','semantic_kind','lifecycle_state','schema_path','schema_sha256','schema_selector','artifact_path','artifact_sha256','semantic_definition_refs','admission_decision_ref')} if contract else None
        result['contract_resolution_basis'] = 'captured-subject-carrier' if subject['carrier_ref'] else 'exact-authored-classification-reference; independently reported carrier posture'
        return result

    def connections(self, ref):
        subject = self.resolve(ref); rows = []
        for entry in sorted(self.subjects.values(), key=lambda s:s['version_ref']):
            if entry['kind'] != 'typed-relation':
                continue
            payload = entry['record'].get('payload', {})
            ends = [payload.get('source', {}), payload.get('target', {})]
            if not any(e.get('version_ref') == subject['version_ref'] for e in ends):
                continue
            error = None
            try:
                self.handle.operations.validate_relation(entry['record'], self.data['projection'], allow_historical=True)
                views = [self.endpoint_view(self.resolve(e['version_ref'])) for e in ends]
            except Exception:
                error = 'Connection is not validated by this selected exact endpoint/type/profile cut.'
                views = []
            rows.append({'connection': self.summary(entry), 'relation_kind_ref': payload.get('relation_kind_ref'),
                'source': ends[0], 'target': ends[1], 'qualifiers': payload.get('qualifiers', {}),
                'validation_posture': 'unresolved' if error else 'validated-selected-cut',
                'endpoint_views': views, 'gap': error,
                'permission_from_connection': False})
        result = self.common('connections'); result.update(artifact=self.summary(subject), connections=rows)
        return result

    def endpoint_view(self, subject):
        represented = self.handle.mapping.subject_kind(subject, self.data['projection'], allow_historical=True)
        mapping = self.handle.mapping.mapping_for(subject.get('carrier_ref'), self.data['projection'])
        contract = self.data['projection']['contracts'].get(subject.get('carrier_ref'))
        return {'version_ref': subject['version_ref'], 'identity_ref': subject['identity'],
            'carrier_kind': contract['semantic_kind'] if contract else subject['kind'],
            'source_projection_kind': subject['kind'], 'represented_endpoint_kind': represented,
            'effective_state': subject['effective_state'], 'carrier_ref': subject.get('carrier_ref'),
            'mapping_binding': self.handle.mapping.binding() if mapping else None,
            'eligibility_role': 'historical-read-only' if subject['effective_state'] in ('admitted-historical','local-admitted-historical') else 'read-existing-exact-connection',
            'raw_subject_rewritten': False, 'action_authority': False}

    def review(self, sequence=None):
        sequence = self.data['head']['sequence'] if sequence is None else sequence
        require(type(sequence) is int and 1 <= sequence <= self.data['head']['sequence'], 'recorded application not found')
        tx = self.data['transactions'][sequence]
        before = self.handle.store_module.Store.initial_projection(self.data['baseline'])
        for prior in self.data['transactions'][1:sequence]:
            before, _ = self.handle.operations.prepare(before, prior['proposal'], prior['previous_digest'], self.data['config'])
        proposal = tx['proposal']; rows = []
        for index, target in enumerate(proposal['targets']):
            predecessor = before['subjects'].get(target['predecessor_ref']) if target.get('predecessor_ref') else None
            rows.append({'target_ref': target['version_ref'], 'operation': target['operation'], 'carrier_ref': target['carrier_ref'],
                'predecessor_ref': target.get('predecessor_ref'), 'before_binding': predecessor['source'] if predecessor else None,
                'after_binding': {'store_id': self.data['config']['store_id'], 'path': f'transactions/{sequence:010d}.json',
                    'selector': f'/proposal/targets/{index}/record', 'sha256': sha(self.handle.common.encoded(target['record']))},
                'status_before_application': 'candidate-unadmitted', 'decision_core': tx['decision_cores'][index],
                'structural_diff': differences(predecessor['record'] if predecessor else None, target['record']),
                'diff_encoding': 'JSON structure; exact original/source-file bindings shown independently.'})
        result = self.common('review')
        result.update(review_posture='recorded-review-before-isolated-local-application', target_count=len(rows), targets=rows,
            proposal_digest=self.handle.common.digest(proposal), proposal_source=self.selected['proposal_binding'],
            recorded_review_binding=self.selected['review_binding'], observed_signature=tx['approval'],
            effects=tx['consequences']['admission_transaction']['payload']['admission_targets'],
            invalidation_conditions=['Different source/profile/HEAD/mapping, target bytes, authority scope or Decision core require a fresh exact review.'],
            final_owner_review=False, decision_prompt='Inspect these exact recorded targets and local effects. This view does not request or generate a final R08 owner response.')
        return result

    def receipt(self, sequence=None):
        sequence = self.data['head']['sequence'] if sequence is None else sequence
        require(type(sequence) is int and 1 <= sequence <= self.data['head']['sequence'], 'recorded receipt not found')
        tx = self.data['transactions'][sequence]; name = f'transactions/{sequence:010d}.json'
        result = self.common('receipt')
        result.update(transaction_file_sha256=sha(self.originals[name]), transaction_digest=tx['digest'],
            approval=tx['approval'], application_receipt=tx['consequences']['receipt'],
            why_path=[{'step': 'captured-source-cut', 'digest': self.data['baseline']['snapshot_digest']},
                {'step': 'original-proposal', 'digest': self.handle.common.digest(tx['proposal'])},
                {'step': 'independent-decision-cores', 'digests': [self.handle.common.digest(c) for c in tx['decision_cores']]},
                {'step': 'verified-local-signature', 'digest': self.handle.common.digest(tx['approval'])},
                {'step': 'deterministic-consequences', 'digest': self.handle.common.digest(tx['consequences'])},
                {'step': 'signed-chain-to-selected-head', 'digest': self.data['head']['transaction_digest']}],
            returned_receipt_is_not_final_repository_admission=True)
        return result


def main(argv=None):
    parser = argparse.ArgumentParser(description='Inspect an exact private signed Lab candidate source cut.')
    parser.add_argument('--source', choices=['engineering','research','product'], default='engineering')
    parser.add_argument('--json', action='store_true', help='Exact structured report; default is readable text.')
    parser.add_argument('--max-output-bytes', type=int, default=1024*1024)
    subs = parser.add_subparsers(dest='command', required=True)
    subs.add_parser('status')
    definitions = subs.add_parser('definitions')
    definitions.add_argument('--state', choices=['all','admitted-current','admitted-historical','candidate-unadmitted'], default='all')
    definitions.add_argument('--offset', type=int, default=0); definitions.add_argument('--limit', type=int, default=50)
    inspect = subs.add_parser('inspect'); inspect.add_argument('ref'); inspect.add_argument('--without-body', action='store_true')
    connections = subs.add_parser('connections'); connections.add_argument('ref')
    for command in ('review','receipt'):
        sub = subs.add_parser(command); sub.add_argument('--sequence', type=int)
    args = parser.parse_args(argv)
    try:
        require(4096 <= args.max_output_bytes <= 4*1024*1024, 'output ceiling outside host budget')
        with replay_source(args.source) as view:
            if args.command == 'definitions':
                result = view.definitions(state=args.state, offset=args.offset, limit=args.limit)
            elif args.command == 'inspect':
                result = view.inspect(args.ref, include_body=not args.without_body)
            elif args.command == 'connections':
                result = view.connections(args.ref)
            elif args.command in ('review','receipt'):
                result = getattr(view,args.command)(args.sequence)
            else:
                result = view.status()
        from render import readable
        raw = encoded(result) if args.json else readable(result).encode('utf-8')
        require(len(raw) <= args.max_output_bytes, 'output budget exceeded; select fewer Definitions or omit body')
        sys.stdout.buffer.write(raw)
        return 0
    except Exception as error:
        # Local CLI diagnostic. No raw archive, body, credential or traceback.
        message = str(error) if isinstance(error,ValueError) else 'Selected signed source could not be verified.'
        sys.stderr.write(message + '\n'); return 2


if __name__ == '__main__':
    raise SystemExit(main())
