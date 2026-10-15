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
API = HERE.parent / 'api-v12'
sys.path.insert(0, str(API))
import source_bridge as source
import artifact_model as model
from handlers import cut

spec = importlib.util.spec_from_file_location('_R03_selected_session_eligibility', HERE.parent / 'session-authority-v1/eligibility.py')
eligibility = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = eligibility
spec.loader.exec_module(eligibility)

# Explicit domain-carrier policy. Directories and JSON names do not supply kinds.
CARRIERS = {
    'principal/v1': ('principal', 'node_id'),
    'project-identity/v1': ('project-identity', 'project_id'),
    'product-identity/v2': ('product-identity', 'product_id'),
    'goal/v1': ('goal', 'goal_id'),
    'intent/v1': ('intent', 'node_id'),
    'work/v1': ('work', 'node_id'),
    'coordination-context/v2': ('coordination-context', 'coordination_context_id'),
    'agent-assignment/v1': ('agent-assignment', 'node_id'),
    'agent-profile/v1': ('agent-profile', 'node_id'),
    'agent-capability/v1': ('agent-capability', 'node_id'),
    'implementation/v1': ('implementation', 'node_id'),
    'policy/v1': ('policy', 'node_id'),
    'agent-instance/v1': ('agent-instance', 'node_id'),
    'agent-session/v1': ('agent-session', 'node_id'),
    'context/v1': ('context', 'node_id'),
    'context-request/v1': ('context-request', 'node_id'),
    'context-view/v1': ('context-view', 'node_id'),
    'ontology/v1': ('ontology', 'node_id'),
    'ontology-cut/v1': ('ontology-cut', 'node_id'),
    'ontology-view/v1': ('ontology-view', 'node_id'),
    'project-state/v2': ('project-state', 'node_id'),
}
CARRIERS = {'cal.artifact-type.' + k: v for k, v in CARRIERS.items()}
CURRENT = {'admitted-current', 'local-admitted-current'}
EXCLUDED_CATEGORIES = {'artifact-type', 'relation-kind', 'definition'}


def binding(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': source.sha(path.read_bytes())}


def verify_package(expected_sha256):
    path = HERE / 'source-manifest.json'
    source.require(source.sha(path.read_bytes()) == expected_sha256, 'independently selected adapter package differs')
    manifest = source.parse(path.read_bytes())
    source.require(manifest['authority_effect'] == 'none' and manifest['actual_owner_outcome'] is None, 'adapter source posture cannot supply authority')
    source.require(manifest['environment'] == {'python': platform.python_version(), 'jsonschema': importlib.metadata.version('jsonschema')}, 'selected source adapter environment differs')
    for row in manifest['files']: source.original(row)
    return manifest


class SignedSources:
    """Construction requires the host's verified reader, never a public message."""
    def __init__(self, view, package_pin):
        verify_package(package_pin)
        self.view = view
        self.package_pin = package_pin
        self.closed = False
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
            item = eligibility.SchemaSpec(carrier, kind, identity_field, raw, source.sha(raw))
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
            self.records.append(eligibility.SourceRecord(ref, raw, subject['effective_state'], locator))
            self.dispositions.append({'version_ref': subject['version_ref'], 'disposition': 'included-current-original',
                'artifact': ref, 'source_locator': locator, 'encoding': encoding, 'enclosing_source_sha256': enclosing_digest})
        source.require(len(self.dispositions) == len(view.subjects), 'subject accounting incomplete')
        self.sources = eligibility.ExactSources(view.data['config']['scope_ref'], self.source_cut,
            self.records, self.schemas, self.guard)
        for record in self.records: self.sources.get(record.artifact)
        self.guard()

    def guard(self):
        source.require(not self.closed, 'closed source adapter cannot serve context')
        verify_package(self.package_pin)
        self.view.handle.guard()
        source.require(source.source_selection(self.selected['name']) == self.selected == self.view.selected, 'independently selected branch changed')
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


@contextmanager
def open_signed(source_name, package_pin):
    verify_package(package_pin)
    with source.replay_source(source_name) as view:
        adapter = SignedSources(view, package_pin)
        try:
            yield adapter
            adapter.guard()
        finally:
            adapter.close()
