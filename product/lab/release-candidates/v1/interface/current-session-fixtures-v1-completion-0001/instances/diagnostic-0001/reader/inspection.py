"""Exact captured inspection with explicit original content support."""
from collections import Counter
from .base import ROOT,sha,parse,encoded,original,require,original_bridge
MAX_ENTRIES=1000
CLAIM="Exact owned candidate source; no canonical admission, live Agent, Session or public permission."

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
            implemented_cli_commands=[], inspection_methods=['status','definitions','inspect','connections','review','receipt'],
            api_operations_added_by_this_source=0, required_public_api_operations=34,
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
        if binding.get('encoding'):
            report,_=original_bridge.source_record(self,subject)
            return report
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
                'after_binding': self.subjects[target['version_ref']]['source'],
                'status_before_application': 'candidate-unadmitted', 'decision_core': tx['decision_cores'][index],
                'structural_diff': differences(predecessor['record'] if predecessor else None, target['record']),
                'diff_encoding': 'JSON structure; exact original/source-file bindings shown independently.'})
        result = self.common('review')
        result.update(review_posture='recorded-review-before-isolated-local-application', target_count=len(rows), targets=rows,
            proposal_digest=self.handle.common.digest(proposal), proposal_source={'store_id':self.data['config']['store_id'], 'path':f'transactions/{sequence:010d}.json',
                'selector':'/proposal', 'original_file_sha256':sha(self.originals[f'transactions/{sequence:010d}.json'])},
            recorded_review_binding=self.selected['review_binding'] if sequence==self.data['head']['sequence'] else None, observed_signature=tx['approval'],
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
