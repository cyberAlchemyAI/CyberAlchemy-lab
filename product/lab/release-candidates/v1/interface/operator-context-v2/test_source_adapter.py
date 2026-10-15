"""Actual signed-branch source/reference parity and invalidation guards."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import source_adapter as bridge


class SignedSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pin = hashlib.sha256((HERE / 'source-manifest.json').read_bytes()).hexdigest()
        cls.context = bridge.open_signed('reference-corrected', cls.pin)
        cls.adapter = cls.context.__enter__()
        cls.report = cls.adapter.closure_report()

    @classmethod
    def tearDownClass(cls):
        cls.context.__exit__(None, None, None)

    def source(self, carrier):
        return next(row for row in self.adapter.records if row.artifact['carrier_ref'] == 'cal.artifact-type.' + carrier)

    def test_cut_exactly_matches_actual_API_signed_reader(self):
        self.assertEqual(self.report['source_cut'], bridge.cut(self.adapter.view))

    def test_signed_corrected_branch_selection_preserved(self):
        self.assertEqual(self.report['archive_binding']['sha256'], 'f8400d77102576bdbe5cb24a2efa15da04feab7f33e4843f3c9e79aa8a95ff81')

    def test_subject_accounting_is_complete(self):
        self.assertEqual(self.report['accounted_subjects'], len(self.adapter.view.subjects))
        self.assertEqual(len(self.report['dispositions']), len(self.adapter.view.subjects))

    def test_catalog_descriptors_are_not_domain_sources(self):
        included = {row.artifact['version_ref'] for row in self.adapter.records}
        self.assertTrue(all(row['version_ref'] not in included for row in self.adapter.view.subjects.values() if row['category'] in bridge.EXCLUDED_CATEGORIES))

    def test_current_Project_State_is_from_this_branch(self):
        row = self.source('project-state/v2')
        self.assertEqual(row.artifact['identity_ref'], 'project-state:R03-reference-corrections:2')
        self.assertEqual(self.report['carrier_counts']['cal.artifact-type.project-state/v2'], 1)

    def test_C12_state_is_not_substituted(self):
        self.assertFalse(any('c12-source-audit' in row.artifact['identity_ref'] for row in self.adapter.records))

    def test_missing_Goal_is_reported(self):
        self.assertIn('cal.artifact-type.goal/v1', self.report['missing_current_carriers'])

    def test_missing_Coordination_Context_is_reported(self):
        self.assertIn('cal.artifact-type.coordination-context/v2', self.report['missing_current_carriers'])

    def test_Project_State_is_not_reported_missing(self):
        self.assertNotIn('cal.artifact-type.project-state/v2', self.report['missing_current_carriers'])

    def test_old_instance_Assignment_does_not_become_fresh_participation(self):
        rows = self.report['instance_bound_assignments']
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['eligible_ref'], 'agent-instance:first-governed-agent-episode:2026-10-06')
        self.assertFalse(self.report['fresh_Session_participation_established'])

    def test_no_view_or_native_mapping_claim(self):
        self.assertFalse(self.report['context_or_ontology_views_generated'])
        self.assertFalse(self.report['native_domain_mapping_supplied'])

    def test_no_authority_or_owner_outcome(self):
        self.assertEqual(self.report['authority_effect'], 'none')
        self.assertIsNone(self.report['actual_owner_outcome'])

    def test_no_historical_record_enters_current_resolver(self):
        self.assertTrue(all(row.posture in bridge.CURRENT for row in self.adapter.records))

    def test_protected_Session_body_is_excluded(self):
        protected = [row for row in self.report['dispositions'] if row['disposition'] == 'excluded-private-body']
        self.assertTrue(protected)
        self.assertFalse(any(row.artifact['carrier_ref'] == 'cal.artifact-type.agent-session/v1' for row in self.adapter.records))

    def test_exported_diagnostics_contain_no_Session_memory(self):
        self.assertNotIn('session_memory', json.dumps(self.report))
        self.assertNotIn('working_record_refs', json.dumps(self.report))

    def test_original_records_keep_API_headers(self):
        for row in self.adapter.records:
            subject = self.adapter.view.subjects[row.artifact['version_ref']]
            self.assertEqual(row.artifact, bridge.model.artifact_ref(self.adapter.view, subject))

    def test_original_record_bytes_keep_API_encoding(self):
        for row in self.adapter.records:
            subject = self.adapter.view.subjects[row.artifact['version_ref']]
            raw, locator, encoding, enclosing = bridge.model.record_bytes(self.adapter.view, subject)
            self.assertEqual(raw, row.original)
            self.assertEqual(locator, row.source_ref)
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row.artifact['byte_sha256'])

    def test_enclosing_signed_transaction_digest_stays_separate(self):
        rows = [row for row in self.report['dispositions'] if row['disposition'] == 'included-current-original' and row['encoding'] == 'inherited-canonical-json-of-selected-original-value']
        self.assertTrue(rows)
        self.assertTrue(all(row['artifact']['byte_sha256'] != row['enclosing_source_sha256'] for row in rows))

    def test_actual_same_cut_Principal_resolves(self):
        row, body = self.adapter.sources.resolve('principal:repository-owner', 'cal.artifact-type.principal/v1')
        self.assertEqual(body['node_id'], row.artifact['identity_ref'])

    def test_actual_same_cut_Work_resolves(self):
        row = self.source('work/v1')
        found, body = self.adapter.sources.get(row.artifact, 'cal.artifact-type.work/v1')
        self.assertEqual(row, found)

    def test_foreign_scope_reference_is_rejected(self):
        ref = copy.deepcopy(self.source('work/v1').artifact);ref['scope_ref'] = 'project:other'
        with self.assertRaisesRegex(bridge.eligibility.EligibilityFault, 'scope differs'):
            self.adapter.sources.get(ref)

    def test_substituted_byte_reference_is_rejected(self):
        ref = copy.deepcopy(self.source('work/v1').artifact);ref['byte_sha256'] = '0' * 64
        with self.assertRaisesRegex(bridge.eligibility.EligibilityFault, 'unresolved'):
            self.adapter.sources.get(ref)

    def test_wrong_carrier_is_rejected(self):
        with self.assertRaisesRegex(bridge.eligibility.EligibilityFault, 'carrier differs'):
            self.adapter.sources.get(self.source('work/v1').artifact, 'cal.artifact-type.intent/v1')

    def test_missing_Goal_does_not_resolve_by_name(self):
        with self.assertRaisesRegex(bridge.eligibility.EligibilityFault, 'missing or ambiguous'):
            self.adapter.sources.resolve('goal:invented', 'cal.artifact-type.goal/v1')

    def test_projection_mutation_invalidates_guard(self):
        value = self.adapter.view.data['projection'];before = value.get('mutation-test')
        try:
            value['mutation-test'] = True
            with self.assertRaisesRegex(ValueError, 'projection changed'): self.adapter.guard()
        finally:
            if before is None: value.pop('mutation-test', None)
            else: value['mutation-test'] = before

    def test_original_transaction_mutation_invalidates_guard(self):
        originals = self.adapter.view.originals;name = next(k for k in originals if k.startswith('transactions/'));before = originals[name]
        try:
            originals[name] = before + b' '
            with self.assertRaisesRegex(ValueError, 'transaction byte closure changed'): self.adapter.guard()
        finally: originals[name] = before

    def test_original_transaction_omission_invalidates_guard(self):
        originals = self.adapter.view.originals;name = next(k for k in originals if k.startswith('transactions/'));before = originals.pop(name)
        try:
            with self.assertRaisesRegex(ValueError, 'transaction byte closure changed'): self.adapter.guard()
        finally: originals[name] = before

    def test_configuration_mutation_invalidates_guard(self):
        config = self.adapter.view.data['config'];before = config['scope_ref']
        try:
            config['scope_ref'] = 'project:other'
            with self.assertRaises(ValueError): self.adapter.guard()
        finally: config['scope_ref'] = before

    def test_closed_adapter_cannot_serve_sources(self):
        self.adapter.closed = True
        try:
            with self.assertRaisesRegex(ValueError, 'closed source adapter'): self.adapter.sources.get(self.source('work/v1').artifact)
        finally: self.adapter.closed = False

    def test_schema_originals_match_the_captured_contracts(self):
        for schema in self.adapter.schemas:
            contract = self.adapter.view.data['projection']['contracts'][schema.carrier_ref]
            self.assertEqual(schema.expected_sha256, contract['schema_sha256'])

    def test_selected_Artifact_bodies_have_no_normalization(self):
        row = self.source('agent-assignment/v1')
        self.assertEqual(bridge.eligibility.parse(row.original), self.adapter.view.subjects[row.artifact['version_ref']]['record'])

    def test_stable_and_exact_Work_reference_match(self):
        row = self.source('work/v1')
        a, _ = self.adapter.sources.resolve(row.artifact['identity_ref'])
        b, _ = self.adapter.sources.resolve(row.artifact['version_ref'])
        self.assertEqual(a, b)


if __name__ == '__main__': unittest.main(verbosity=2)
