"""Exact declared public headers over original catalog; hypothetical proposals."""
import copy
import unittest
from . import adapter as A, predecessor_binding as V
from .test_catalog_binding import CatalogBindingTests

PROFILE = A.HERE.parent / 'api-v45/catalog-representations.json'
PROFILE_SHA = '435a78f4b974d0f5ad1679940c779be256cad349ee18d98c0d1b3ae99a3b0cfc'


class PredecessorBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): CatalogBindingTests.setUpClass()

    def setUp(self):
        self.b = CatalogBindingTests(); self.b.setUp(); self.f = self.b.f
        self.profile_raw = PROFILE.read_bytes()
        self.profile_pin = PROFILE_SHA
        profile = A.parse(self.profile_raw)
        self.rows = {r['represented_contract_ref']: r for r in profile['rows']}
        for t in self.f.proposal['targets']:
            p = t['predecessor']; prior = self.f.projection['subjects'][p['version_ref']]
            if prior['category'] == 'artifact-type':
                row = self.rows[p['version_ref']]
                p.update(identity_ref=row['identity_ref'], carrier_ref=row['meta_carrier_ref'], byte_sha256=row['byte_sha256'])
            else:
                matches = [ref for ref, contract in self.f.projection['contracts'].items()
                           if contract['lifecycle_state'] in ('admitted-current', 'local-admitted-current')
                           and contract['semantic_kind'] == 'relation-kind'
                           and contract['instance_discriminator']['value'] == prior['record']['schema_version']]
                self.assertEqual(len(matches), 1)
                p['carrier_ref'] = matches[0]

    def source_bytes(self, binding): return (A.ROOT / binding['ref']).read_bytes()

    def bind(self, **changes):
        args = dict(projection=self.f.projection, baseline=self.b.baseline, config=self.f.config,
            representation_profile_bytes=self.profile_raw, expected_profile_sha256=self.profile_pin,
            read_source_material=self.source_bytes)
        args.update(changes)
        return V.bind_public_predecessors(self.f.proposal, **args)

    def check(self, **changes):
        args = dict(independently_selected_representation_profile_bytes=self.profile_raw,
            expected_representation_profile_sha256=self.profile_pin, read_source_material=self.source_bytes)
        args.update(changes)
        return self.b.check(**args)

    def change_profile(self, edit):
        value = A.parse(self.profile_raw); edit(value)
        self.profile_raw = self.f.C.encoded(value); self.profile_pin = A.sha(self.profile_raw)

    def test_01_explicit_public_and_physical_headers_stay_separate(self):
        result = self.bind()
        self.assertEqual(result['result'], 'PASS')
        self.assertEqual(len(result['predecessors']), 4)
        for ref, row in result['predecessors'].items():
            self.assertEqual(row['runtime_predecessor_ref'], ref)
            self.assertIsNone(row['physical_carrier_ref'])
            self.assertIsNotNone(row['public_header']['carrier_ref'])
            self.assertEqual(row['original_predecessor_metadata'], self.f.projection['subjects'][ref])
        self.assertFalse(result['scope_grant_supplied'])

    def test_02_original_complete_postimage_passes_without_source_changes(self):
        before = self.f.C.encoded(self.f.projection)
        result = self.check()
        self.assertEqual(result['result'], 'PASS')
        self.assertEqual(len(result['public_predecessor_binding']['predecessors']), 4)
        self.assertEqual(result['actual_transactions_written'], 0)
        self.assertEqual(before, self.f.C.encoded(self.f.projection))

    def test_03_profile_pin_required(self):
        with self.assertRaisesRegex(A.WireFault, 'profile pin'): self.bind(expected_profile_sha256='0' * 64)

    def test_04_public_carrier_axis_cannot_be_guessed(self):
        self.f.proposal['targets'][0]['predecessor']['carrier_ref'] = 'cal.artifact-type.artifact-type/v3'
        with self.assertRaisesRegex(A.WireFault, 'public predecessor representation'): self.bind()

    def test_05_public_byte_axis_required(self):
        self.f.proposal['targets'][0]['predecessor']['byte_sha256'] = '0' * 64
        with self.assertRaisesRegex(A.WireFault, 'public predecessor representation'): self.bind()

    def test_06_transaction_scope_is_not_semantic_scope_grant(self):
        self.f.proposal['targets'][0]['predecessor']['scope_ref'] = 'project:other'
        with self.assertRaisesRegex(A.WireFault, 'public predecessor representation'): self.bind()

    def test_07_complete_unique_profile_inventory_required(self):
        self.change_profile(lambda value: value['rows'].append(copy.deepcopy(value['rows'][0])))
        with self.assertRaisesRegex(A.WireFault, 'unique representation inventory'): self.bind()

    def test_08_original_raw_bytes_required(self):
        with self.assertRaisesRegex(A.WireFault, 'file bytes differ'):
            self.bind(read_source_material=lambda b: b'{}')

    def test_09_profile_source_binding_cannot_shadow_original(self):
        ref = self.f.proposal['targets'][0]['predecessor']['version_ref']
        self.change_profile(lambda value: next(r for r in value['rows'] if r['represented_contract_ref'] == ref)['source_binding'].update(sha256='0' * 64))
        with self.assertRaisesRegex(A.WireFault, 'representation source binding'): self.bind()

    def test_10_profile_selected_body_bytes_required(self):
        ref = self.f.proposal['targets'][0]['predecessor']['version_ref']
        self.change_profile(lambda value: next(r for r in value['rows'] if r['represented_contract_ref'] == ref).update(size_bytes=0))
        with self.assertRaisesRegex(A.WireFault, 'representation body bytes'): self.bind()

    def test_11_duplicate_predecessors_refused(self):
        self.f.proposal['targets'].append(copy.deepcopy(self.f.proposal['targets'][0]))
        with self.assertRaisesRegex(A.WireFault, 'duplicate predecessor'): self.bind()

    def test_12_partial_adapter_inputs_refused(self):
        with self.assertRaisesRegex(A.WireFault, 'representation inputs must be complete'):
            self.check(read_source_material=None)
