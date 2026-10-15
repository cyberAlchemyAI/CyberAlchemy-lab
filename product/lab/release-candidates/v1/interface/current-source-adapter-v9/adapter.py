"""Actual signed API branch to exact, current domain participation sources."""
from contextlib import contextmanager
import copy
import importlib.util
import importlib.metadata
from pathlib import Path
import platform
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
from . import base as source,model,eligibility
from .base import cut

# Explicit domain-carrier policy. Directories and JSON names do not supply kinds.
CARRIERS = {
    'principal/v1': ('principal', 'node_id'),
    'principal-reference/v1': ('principal-reference', 'node_id'),
    'project-identity/v1': ('project-identity', 'project_id'),
    'product-identity/v2': ('product-identity', 'product_id'),
    'goal/v1': ('goal', 'goal_id'),
    'intent/v1': ('intent', 'node_id'),
    'intent-resolution/v1': ('intent-resolution', 'node_id'),
    'work/v1': ('work', 'node_id'),
    'coordination-context/v2': ('coordination-context', 'coordination_context_id'),
    'agent-assignment/v1': ('agent-assignment', 'node_id'),
    'agent-profile/v1': ('agent-profile', 'node_id'),
    'agent-capability/v1': ('agent-capability', 'node_id'),
    'implementation/v1': ('implementation', 'node_id'),
    'policy/v2': ('policy', 'node_id'),
    'agent-instance/v1': ('agent-instance', 'node_id'),
    'agent-session/v1': ('agent-session', 'node_id'),
    'context/v1': ('context', 'node_id'),
    'context-request/v1': ('context-request', 'node_id'),
    'context-view/v1': ('context-view', 'node_id'),
    'ontology/v1': ('ontology', 'node_id'),
    'ontology-cut/v1': ('ontology-cut', 'node_id'),
    'ontology-view/v1': ('ontology-view', 'node_id'),
    'project-state/v2': ('project-state', 'node_id'),
    'agent-action/v1': ('agent-action', 'node_id'),
    'operational-observation/v1': ('operational-observation', 'node_id'),
    'agent-reflection/v1': ('agent-reflection', 'node_id'),
    'operational-lesson/v1': ('operational-lesson', 'node_id'),
    'challenge-contract/v1': ('challenge-contract', 'node_id'),
    'challenge-event/v1': ('challenge-event', 'node_id'),
    'evidence-set/v1': ('evidence-set', 'node_id'),
    'decision/v2': ('decision', 'node_id'),
    'effect/v1': ('effect', 'node_id'),
    'decision-scope/v2': ('decision-scope', 'node_id'),
    'authority-boundary/v1': ('authority-boundary', 'node_id'),
}
CARRIERS = {'cal.artifact-type.' + k: v for k, v in CARRIERS.items()}
CURRENT = {'admitted-current', 'local-admitted-current'}
EXCLUDED_CATEGORIES = {'artifact-type', 'relation-kind', 'definition'}


def binding(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': source.sha(path.read_bytes())}


def verify_package(expected_sha256):
    return source.verify_source(expected_sha256)


class SignedSources:
    """Construction requires the host's verified reader, never a public message."""
    def __init__(self, view, package_pin, *, selection_reader=None):
        verify_package(package_pin)
        self.view = view
        source.require(callable(selection_reader), "independent source selection reader required")
        self.selection_reader = selection_reader
        self.package_pin = package_pin
        self.closed = False
        self._trusted_records=None;self._trusted_sources=None;self._trusted_schemas=None;self._trusted_source_schemas=None
        self.selected = copy.deepcopy(view.selected)
        self.source_cut = copy.deepcopy(cut(view))
        self.original_bindings = {k: source.sha(v) for k, v in view.originals.items()}
        self.projection_digest = view.handle.common.digest(view.data['projection'])
        self.configuration_digest = view.handle.common.digest(view.data['config'])
        self.baseline_digest = view.handle.common.digest(view.data['baseline'])
        self.records = []
        self.schemas = []
        self.dispositions = []
        self.schema_provenance = []
        self.guard()
        contracts = view.data['projection']['contracts']
        for carrier, (kind, identity_field) in CARRIERS.items():
            contract = contracts.get(carrier)
            if contract is None or contract['lifecycle_state'] != 'admitted-current':
                continue
            source.require(contract['semantic_kind'] == kind, 'selected carrier semantic kind differs')
            source.require(contract['schema_selector'] is None, 'schema fragment requires an explicit successor adapter')
            path = contract['schema_path']
            source.require(view.data['baseline']['materials'].get(path) == contract['schema_sha256'], 'schema is not in exact captured material closure')
            raw = source.original({'path': path, 'sha256': contract['schema_sha256']})
            schema = source.parse(raw)
            source.require(identity_field in schema.get('properties', {}), 'declared carrier identity field unavailable')
            rule = 'verified-source-revision' if carrier == 'cal.artifact-type.product-identity/v2' else 'body-version-equals-reference'
            item = eligibility.SchemaSpec(carrier, kind, identity_field, raw, source.sha(raw), rule)
            item.validator()
            self.schemas.append(item)
            self.schema_provenance.append({'carrier_ref': carrier, 'schema_binding': {'ref': path, 'sha256': source.sha(raw)}})
        schemas = {row.carrier_ref: row for row in self.schemas}
        for subject in sorted(view.subjects.values(), key=lambda row: row['version_ref']):
            if subject['category'] in EXCLUDED_CATEGORIES or subject['carrier_ref'] not in CARRIERS:
                self.dispositions.append({'version_ref': subject['version_ref'], 'disposition': 'excluded-carrier-or-catalog', 'reason': 'Outside explicit current domain-instance policy.'})
                continue
            if subject['effective_state'] not in CURRENT:
                self.dispositions.append({'version_ref': subject['version_ref'], 'disposition': 'excluded-historical', 'reason': 'Historical metadata is not current participation.'})
                continue
            carrier = subject['carrier_ref']
            if carrier not in schemas:
                self.dispositions.append({'version_ref': subject['version_ref'], 'disposition': 'excluded-schema', 'reason': 'Current carrier contract unavailable.'})
                continue
            raw, locator, encoding, enclosing_digest = model.record_bytes(view, subject)
            ref = model.artifact_ref(view, subject)
            item = schemas[carrier]
            body = eligibility.parse(raw)
            valid = item.validator().is_valid(body) and body.get(item.identity_field) == ref['identity_ref']
            if not valid:
                self.dispositions.append({'version_ref': subject['version_ref'], 'disposition': 'excluded-body-contract', 'reason': 'Exact captured body does not conform to selected domain carrier.'})
                continue
            try:
                eligibility.no_private_memory(body, blank_session_policy=item.semantic_kind == 'agent-session')
            except eligibility.EligibilityFault:
                self.dispositions.append({'version_ref': subject['version_ref'], 'disposition': 'excluded-private-body', 'reason': 'Protected memory or credential contents cannot enter context.'})
                continue
            witness = None
            if item.version_binding_rule == 'verified-source-revision':
                b = subject['source']
                enclosing = view.originals[b['path']] if 'store_id' in b else source.original({'path': b['path'], 'sha256': b['sha256']})
                witness = eligibility.SignedRevisionWitness(copy.deepcopy(self.source_cut), copy.deepcopy(ref), enclosing, enclosing_digest, b.get('selector', ''), encoding)
            self.records.append(eligibility.SourceRecord(ref, raw, subject['effective_state'], locator, witness))
            self.dispositions.append({'version_ref': subject['version_ref'], 'disposition': 'included-current-original',
                'artifact': ref, 'source_locator': locator, 'encoding': encoding, 'enclosing_source_sha256': enclosing_digest, 'version_binding_rule': item.version_binding_rule,
                'original_body_version': body.get('version')})
        source.require(len(self.dispositions) == len(view.subjects), 'subject accounting incomplete')
        self.sources = eligibility.ExactSources(view.data['config']['scope_ref'], self.source_cut,
            self.records, self.schemas, self.guard)
        source.require(self.sources.validate_current_records()==len(self.records),
            'complete selected record construction validation required')
        self._trusted_records=self.record_stamp(self.records)
        self._trusted_sources=self.record_stamp(self.sources.records.values())
        self._trusted_schemas=self.schema_stamp(self.schemas)
        self._trusted_source_schemas=self.schema_stamp(self.sources.schemas.values())
        self.guard()

    @staticmethod
    def record_stamp(rows):
        def witness(w):
            if w is None:return None
            return {'source_cut':w.source_cut,'artifact_ref':w.artifact_ref,'enclosing_sha256':w.enclosing_sha256,
                'actual_enclosing_sha256':source.sha(w.enclosing_original),'selector':w.selector,'encoding':w.encoding}
        return source.encoded([{'artifact':r.artifact,'raw_sha256':source.sha(r.original),'posture':r.posture,
            'source_ref':r.source_ref,'witness':witness(r.revision_witness)} for r in rows])
    @staticmethod
    def schema_stamp(rows):
        return source.encoded([{'carrier':s.carrier_ref,'kind':s.semantic_kind,'identity_field':s.identity_field,
            'raw_sha256':source.sha(s.original_schema),'expected_sha256':s.expected_sha256,'rule':s.version_binding_rule} for s in rows])
    def guard(self):
        source.require(not self.closed, 'closed source adapter cannot serve context')
        if self._trusted_records is not None:
            source.require(self.record_stamp(self.records)==self._trusted_records
                and self.record_stamp(self.sources.records.values())==self._trusted_sources
                and self.schema_stamp(self.schemas)==self._trusted_schemas
                and self.schema_stamp(self.sources.schemas.values())==self._trusted_source_schemas
                and self.sources.scope_ref==self.view.data['config']['scope_ref']
                and self.sources.source_cut==self.source_cut
                and self.sources.current_guard==self.guard
                and set(self.sources.validators)==set(self.sources.schemas)
                and all(source.encoded(v.schema)==source.encoded(source.parse(self.sources.schemas[k].original_schema)) for k,v in self.sources.validators.items()),'captured source records or schemas changed')
        verify_package(self.package_pin)
        self.view.handle.guard()
        source.require(self.selection_reader(self.selected['name']) == self.selected == self.view.selected, 'independently selected branch changed')
        for key in ['archive_binding', 'expected_replay_binding']:
            source.original(self.selected[key])
        source.require(self.source_cut == cut(self.view), 'captured signed source cut changed')
        source.require(self.configuration_digest == self.view.handle.common.digest(self.view.data['config']), 'captured configuration changed')
        source.require(self.baseline_digest == self.view.handle.common.digest(self.view.data['baseline']), 'captured baseline changed')
        source.require(self.projection_digest == self.view.handle.common.digest(self.view.data['projection'])
            and self.view.subjects == self.view.data['projection']['subjects'], 'captured signed projection changed')
        source.require(self.original_bindings == {k: source.sha(v) for k, v in self.view.originals.items()}, 'original signed transaction byte closure changed')
        source.require(self.view.handle.sources.freshness(ROOT, self.view.data['baseline'])['status'] == 'current', 'selected baseline material bytes are stale')
        return True

    def closure_report(self):
        self.guard()
        counts = {carrier: sum(row.artifact['carrier_ref'] == carrier for row in self.records) for carrier in CARRIERS}
        missing = [carrier for carrier in ['cal.artifact-type.goal/v1', 'cal.artifact-type.coordination-context/v2',
            'cal.artifact-type.project-state/v2'] if counts[carrier] == 0]
        old_instances = []
        profile_refs = {value for row in self.records if row.artifact['carrier_ref'] == 'cal.artifact-type.agent-profile/v1'
            for value in [row.artifact['identity_ref'], row.artifact['version_ref']]}
        for row in self.records:
            if row.artifact['carrier_ref'] == 'cal.artifact-type.agent-assignment/v1':
                eligible = eligibility.parse(row.original)['payload']['eligible_agent_ref']
                if eligible not in profile_refs: old_instances.append({'assignment': row.artifact, 'eligible_ref': eligible})
        return {'schema_version': 'lab-same-cut-participation-closure/v1-candidate', 'source_name': self.selected['name'],
            'source_cut': copy.deepcopy(self.source_cut), 'archive_binding': self.selected['archive_binding'],
            'included_current_instances': len(self.records), 'accounted_subjects': len(self.dispositions),
            'carrier_counts': counts, 'missing_current_carriers': missing, 'instance_bound_assignments': old_instances,
            'schema_provenance': copy.deepcopy(self.schema_provenance), 'dispositions': copy.deepcopy(self.dispositions),
            'native_domain_mapping_supplied': False, 'context_or_ontology_views_generated': False,
            'fresh_Session_participation_established': False, 'authority_effect': 'none', 'actual_owner_outcome': None,
            'claim_ceiling': 'Exact current API branch domain-source bridge and closure diagnostic only; missing carriers and old instance-bound participation are not repaired or authorized by this report.'}

    def close(self):
        self.closed = True
