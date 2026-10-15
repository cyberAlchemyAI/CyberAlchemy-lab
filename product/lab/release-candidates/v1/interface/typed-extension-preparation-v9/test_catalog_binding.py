"""Distinct hypothetical envelopes with complete catalog byte/predecessor closure."""
import copy
import unittest
from . import adapter as A, catalog_binding as B
from .test_postimage import PostimageTests


class CatalogBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): PostimageTests.setUpClass()

    def setUp(self):
        self.f = PostimageTests(); self.f.setUp()
        self.snapshot = self.f.fixture.snapshot
        # An explicitly hypothetical legacy envelope, retaining the actual D75
        # catalog bytes. It supplies no actual signed-host/currentness evidence.
        self.baseline = copy.deepcopy(self.snapshot)
        for key in ['controls', 'control_bytes', 'executable_materials', 'executable_byte_contents',
                    'selection_scope', 'source_profile', 'source_profile_sha256']:
            self.baseline.pop(key, None)
        self.baseline['snapshot_digest'] = self.f.C.digest({k: v for k, v in self.baseline.items() if k != 'snapshot_digest'})
        self.f.config['source_snapshot_digest'] = self.baseline['snapshot_digest']
        self.f.expected_config_digest = self.f.C.digest(self.f.config)

    def bind(self, **changes):
        f = self.f
        args = dict(baseline=self.baseline, projection=f.projection, config=f.config, head=f.head,
            expected_profile_sha256=f.fixture.profile_sha, expected_baseline_digest=f.C.digest(self.baseline),
            expected_projection_digest=f.C.digest(f.projection), expected_config_digest=f.C.digest(f.config), expected_head=f.head)
        args.update(changes)
        return B.bind_runtime_catalog(f.selection, self.snapshot, **args)

    def check(self, **changes):
        args = dict(independently_selected_catalog_snapshot=self.snapshot,
            independently_selected_runtime_baseline=self.baseline,
            expected_runtime_baseline_digest=self.f.C.digest(self.baseline),
            expected_catalog_profile_sha256=self.f.fixture.profile_sha)
        args.update(changes)
        return self.f.check(**args)

    def test_01_distinct_envelopes_complete_original_backend(self):
        result = self.check()
        binding = result['runtime_catalog_binding']
        self.assertEqual(result['result'], 'PASS')
        self.assertFalse(binding['equal_snapshot_envelope_digests'])
        self.assertFalse(binding['executable_closures_equated'])
        self.assertEqual(binding['current_carrier_count'], 121)
        self.assertEqual(binding['current_relation_kind_count'], 41)
        self.assertTrue(binding['exact_catalog_material_bindings'])
        self.assertEqual(result['actual_transactions_written'], 0)

    def test_02_same_envelope_explicit_complete_binding(self):
        self.baseline = copy.deepcopy(self.snapshot)
        self.f.config['source_snapshot_digest'] = self.baseline['snapshot_digest']
        self.f.expected_config_digest = self.f.C.digest(self.f.config)
        self.assertTrue(self.check()['runtime_catalog_binding']['equal_snapshot_envelope_digests'])

    def test_03_unselected_current_runtime_carrier_refused(self):
        self.f.projection['contracts']['fixture:unselected/v1'] = copy.deepcopy(
            self.f.projection['contracts']['cal.artifact-type.principal/v1'])
        with self.assertRaisesRegex(A.WireFault, 'carrier inventory differs'): self.bind()

    def test_04_missing_current_runtime_carrier_refused(self):
        self.f.projection['contracts'].pop('cal.artifact-type.principal/v1')
        with self.assertRaisesRegex(A.WireFault, 'carrier inventory differs'): self.bind()

    def test_05_unselected_runtime_relation_kind_refused(self):
        self.f.projection['relation_contracts']['relation.hypothetical-unselected'] = {}
        with self.assertRaisesRegex(A.WireFault, 'Relation Kind inventory differs'): self.bind()

    def test_06_missing_runtime_relation_kind_refused(self):
        self.f.projection['relation_contracts'].pop('relation.acts-for')
        with self.assertRaisesRegex(A.WireFault, 'Relation Kind inventory differs'): self.bind()

    def test_07_complete_runtime_relation_body_required(self):
        self.f.projection['relation_contracts']['relation.acts-for']['payload']['allowed_endpoint_pairs'] = []
        with self.assertRaisesRegex(A.WireFault, 'Relation Kind body differs'): self.bind()

    def test_08_full_runtime_schema_required(self):
        c = self.f.projection['contracts']['cal.artifact-type.principal/v1']
        self.f.projection['documents'][c['schema_path']]['properties']['kind']['const'] = 'hypothetical-other'
        with self.assertRaisesRegex(A.WireFault, 'carrier schema differs'): self.bind()

    def test_09_descriptor_original_byte_identity_required(self):
        self.f.projection['contracts']['cal.artifact-type.principal/v1']['artifact_sha256'] = '0' * 64
        with self.assertRaisesRegex(A.WireFault, 'descriptor or schema selection differs'): self.bind()

    def test_10_complete_definition_predecessor_required(self):
        binding = self.bind()
        ref = next(ref for ref in binding['exact_catalog_predecessor_and_definition_refs']
                   if self.f.projection['subjects'][ref]['category'] == 'definition')
        self.f.projection['subjects'][ref]['source']['sha256'] = '0' * 64
        with self.assertRaisesRegex(A.WireFault, 'predecessor/Definition differs'): self.bind()

    def test_11_original_catalog_material_hash_required(self):
        path = self.f.projection['contracts']['cal.artifact-type.principal/v1']['schema_path']
        self.baseline['materials'][path] = '0' * 64
        with self.assertRaisesRegex(A.WireFault, 'catalog material differs'): self.bind()

    def test_12_non_catalog_executable_closures_stay_distinct(self):
        # Distinct closure differences are recorded, without declaring them
        # equivalent, trusting a new executable or replacing any source guard.
        path = 'fixture:hypothetical-extra-executable'
        self.baseline['materials'][path] = '1' * 64
        result = self.bind()
        self.assertIn(path, result['runtime_baseline_additional_materials'])
        self.assertFalse(result['executable_closures_equated'])
        self.assertFalse(result['actual_transport_authenticated'])

    def test_13_independent_runtime_baseline_pin_required(self):
        with self.assertRaisesRegex(A.WireFault, 'baseline/projection/configuration/HEAD'):
            self.bind(expected_baseline_digest='0' * 64)

    def test_14_independent_catalog_snapshot_pin_required(self):
        self.f.selection['snapshot_digest'] = '0' * 64
        with self.assertRaisesRegex(A.WireFault, 'semantic snapshot pin'): self.bind()

    def test_15_partial_binding_inputs_refused(self):
        with self.assertRaisesRegex(A.WireFault, 'binding inputs must be complete'):
            self.check(expected_runtime_baseline_digest=None)

    def test_16_actual_runtime_config_must_select_its_own_baseline(self):
        self.f.config['source_snapshot_digest'] = self.snapshot['snapshot_digest']
        with self.assertRaisesRegex(A.WireFault, 'exact baseline'): self.bind()
