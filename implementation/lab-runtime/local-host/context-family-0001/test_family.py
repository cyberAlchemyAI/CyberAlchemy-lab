"""Causal, public-only Context family projection tests."""
import copy
import json
import unittest
from pathlib import Path
from unittest import mock
import family as F

class FamilyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=F.predecessor()
        cls.plan,cls.projections=F.construct()

    def test_reviewed_family_and_real_mapper_package(self):
        family=F.selected_family()
        self.assertEqual(family['sibling_names'],[F.SOURCE,F.READER,F.MAPPER])
        self.assertEqual(family['mapper_package_files_including_manifest'],55)
        self.assertEqual(family['mapper_package_manifest_sha256'],F.MAPPER_PACKAGE_SHA)

    def test_reviewed_mapper_source_native_public_schema_join(self):
        result=F.mapper_source_schema_join(self.rows)
        self.assertEqual(result['signed_source_schema_provenance_public_joins'],21)
        self.assertEqual((result['mapped_rows'],result['native_nodes'],result['native_relations']),
                         (25,15,10))
        self.assertFalse(result['archive_body_read'])

    def test_source_schema_provenance_mismatch_refused(self):
        original=F.exact
        def altered(path,pin):
            raw=original(path,pin)
            if Path(path).name=='mapping.json' and Path(path).parent.name=='0001':
                value=json.loads(raw)
                value['source_closure']['schema_provenance'][0]['schema_binding']['sha256']='0'*64
                return F.encoded(value)
            return raw
        with mock.patch.object(F,'exact',side_effect=altered):
            with self.assertRaisesRegex(F.Refused,'signed Source schema provenance'):
                F.mapper_source_schema_join(self.rows)

    def test_no_protected_archive_body_opened(self):
        original=F.exact
        opened=[]
        def observed(path,pin):
            opened.append(str(path))
            return original(path,pin)
        with mock.patch.object(F,'exact',side_effect=observed):
            F.construct()
        self.assertFalse(any(x.endswith('branch.snapshot') for x in opened))

    def test_public_and_schema_closure(self):
        result=F.verify_public_and_schema(self.rows,self.projections)
        self.assertEqual(result,{'public_preimages_rechecked':831,'api_schema_input_bindings':790,
                                 'profile_file_bindings':30,'registry_targets':144})
        self.assertEqual(len(self.plan['projected_api']),5)
        self.assertEqual(len(self.plan['unchanged_public_preimages']),831)
        partition=self.plan['staged_public_partition']
        self.assertEqual(len(partition['already_in_selected_family']),319)
        self.assertEqual(len(partition['copy_exact_public_from_checkout']),512)
        self.assertEqual(len(partition['overlay_projected_api']),5)

    def test_generated_files_equal_pure_projection(self):
        self.assertEqual((F.HERE/'selection.json').read_bytes(),F.encoded(self.plan))
        for name,raw in self.projections.items():
            self.assertEqual((F.HERE/'generated/api-v25'/name).read_bytes(),raw)

    def test_obsolete_context_import_sites_are_pinned_and_held(self):
        gaps=F.context_import_gaps()
        self.assertEqual(len(gaps['pinned_role_preimages']),6)
        self.assertIn('mapper_sibling',gaps['exact_obsolete_sites'])
        self.assertIn('old_auth',gaps['exact_obsolete_sites'])
        self.assertEqual(gaps['actual_import'],'REFUSED')

    def test_bridge_selects_same_loaded_mapper_without_old_import(self):
        bridge=self.projections['source_bridge.py']
        self.assertIn(b'mapper.reader.adapter.source',bridge)
        self.assertIn(b'docker-mapped-20261020-0001',bridge)
        self.assertNotIn(b'inspection/lab_operator.py',bridge)
        self.assertNotIn(b'corrections-v1/loader.py',bridge)
        self.assertNotIn(b'custody_delivery()',bridge)

    def test_profile_rebinds_bridge_and_selection(self):
        profile=json.loads(self.projections['contract-profile.json'])
        bindings={x['path']:x['sha256'] for x in profile['files']}
        for name in ('source_bridge.py','source-selection.json','protocol.py'):
            self.assertEqual(bindings[F.rel(F.API,name)],F.sha(self.projections[name]))

    def test_wrong_mapper_layout_refused(self):
        with mock.patch.object(F,'MAPPER','mapped'):
            with self.assertRaises(F.Refused):F.selected_family()

    def test_mapper_package_digest_mutation_refused(self):
        with mock.patch.object(F,'MAPPER_PACKAGE_SHA','0'*64):
            with self.assertRaisesRegex(F.Refused,'metadata digest differs'):
                F.selected_family()

    def test_profile_old_bridge_injection_refused(self):
        projected=dict(self.projections)
        profile=json.loads(projected['contract-profile.json'])
        for item in profile['files']:
            if item['path']==F.rel(F.API,'source_bridge.py'):
                item['sha256']=self.rows['api_bridge']['old_source_bridge_sha256']
        projected['contract-profile.json']=F.encoded(profile)
        with self.assertRaisesRegex(F.Refused,'projected API profile escapes'):
            F.verify_public_and_schema(self.rows,projected)

    def test_protected_archive_and_effect_refused(self):
        self.assertEqual(self.plan['source_private_archive'],'UNOPENED_AND_UNCOPIED')
        self.assertEqual(self.plan['staged_runtime_import'],'NOT_RUN')
        for fn in (F.final_manifest,F.launch):
            with self.assertRaises(F.Refused):fn()

if __name__=='__main__':unittest.main()
