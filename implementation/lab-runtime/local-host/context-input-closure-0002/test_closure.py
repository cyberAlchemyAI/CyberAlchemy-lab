"""Causal public-only Context input closure checks; no role import or private body."""
import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import resolve as C

class ClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expected=C.plan()

    def test_exact_frozen_row_resolution_and_public_bytes(self):
        result=C.verify_frozen()
        self.assertEqual(result['historical_rows'],1804)
        self.assertEqual(result['public_preimages'],836)
        self.assertEqual(result['api_bridge'],'REPROJECT_REQUIRED')

    def test_every_historical_row_has_one_disposition(self):
        rows=self.expected['historical_rows']
        self.assertEqual(len(rows),1804)
        self.assertEqual(len({r['path'] for r in rows}),1804)
        self.assertEqual(sum(self.expected['counts'].values()),1804)
        self.assertEqual(self.expected['counts']['EXCLUDE_PROTECTED_ARCHIVE'],6)
        self.assertEqual(self.expected['counts']['EXCLUDE_OLD_FAMILY_REPROJECT_FRESH'],318)
        self.assertEqual(self.expected['counts']['REPROJECT_API_SAME_FAMILY'],5)
        self.assertEqual(self.expected['counts']['EXCLUDE_LEGACY_API_IMPORT'],3)
        self.assertEqual(self.expected['counts']['ALLOW_PUBLIC_PREIMAGE'],824)
        self.assertEqual(self.expected['counts']['EXCLUDE_DIRECT_CONTEXT_INPUT'],648)

    def test_protected_and_legacy_paths_cannot_enter_allowlist(self):
        selected={r['path'] for r in self.expected['public_preimages']}
        rows=self.expected['historical_rows']
        for r in rows:
            if r['disposition'] in ('EXCLUDE_PROTECTED_ARCHIVE',
                                   'EXCLUDE_OLD_FAMILY_REPROJECT_FRESH',
                                   'EXCLUDE_LEGACY_API_IMPORT'):
                self.assertNotIn(r['path'],selected)
        self.assertNotIn('product/lab/release-candidates/v1/interface/inspection/lab_operator.py',selected)

    def test_frozen_mutation_refused_before_target_read(self):
        changed=copy.deepcopy(self.expected)
        changed['historical_rows'][0]['disposition']='EXCLUDE_PROTECTED_ARCHIVE'
        with mock.patch.object(C,'verify_public_preimages',side_effect=AssertionError('target opened')):
            with self.assertRaisesRegex(C.Refused,'frozen row-level closure differs'):
                C.verify_plan(changed,self.expected)

    def test_deleted_schema_binding_refused_at_selector(self):
        old=C.read_exact
        def short_inputs(path,pin):
            raw=old(path,pin)
            if Path(path)==C.REPO/C.API_INPUTS:
                value=json.loads(raw);value['files'].pop()
                return json.dumps(value).encode()
            return raw
        with mock.patch.object(C,'read_exact',side_effect=short_inputs):
            with self.assertRaisesRegex(C.Refused,'API resource selector differs'):
                C.plan()

    def test_protected_archive_selector_injection_refused(self):
        old=C.read_exact
        archive=next(r for r in self.expected['historical_rows']
                     if r['disposition']=='EXCLUDE_PROTECTED_ARCHIVE')
        def substituted(path,pin):
            raw=old(path,pin)
            if Path(path)==C.REPO/C.API_INPUTS:
                value=json.loads(raw)
                value['files'][0]={'path':archive['path'],'sha256':archive['historical_sha256']}
                return json.dumps(value).encode()
            return raw
        with mock.patch.object(C,'read_exact',side_effect=substituted):
            with self.assertRaisesRegex(C.Refused,'unsafe or protected dependency path'):
                C.plan()

    def test_api_registry_and_bridge_requirements_are_explicit(self):
        self.assertEqual(self.expected['api_registry_target_count'],144)
        self.assertEqual({k:len(v) for k,v in self.expected['selected_globs'].items()},
                         {'original_api_schemas':5,'local_api_schemas':4,'registry_schemas':80})
        bridge=self.expected['api_bridge']
        self.assertEqual(bridge['status'],'REPROJECT_REQUIRED_BEFORE_IMPORT')
        self.assertEqual(bridge['old_inspection_and_correction_imports'],'EXCLUDED')
        self.assertEqual(len(bridge['required_reprojection']),5)
        self.assertNotIn('_R03_immutable_operator_reader',sys.modules)

    def test_host_and_image_environment_distinct(self):
        runtime=self.expected['runtime']
        self.assertEqual(runtime['host_observed']['jsonschema'],'4.19.2')
        self.assertEqual(runtime['selected_image_probe']['versions']['jsonschema'],'4.23.0')
        self.assertEqual(runtime['selected_image_probe']['versions']['cryptography'],'46.0.5')
        self.assertEqual(runtime['container_environment'],'VERSION_TRIPLET_MATCHES_EXPECTED')
        self.assertEqual(runtime['host_environment'],'MISMATCH_JSONSCHEMA')

    def test_exact_external_command_receipt_and_duplicate_argv_refusal(self):
        receipt=json.loads(C.read_exact(C.IMAGE_RECEIPT,C.IMAGE_RECEIPT_SHA))
        self.assertEqual(C.validate_image_receipt(receipt)['python'],'3.14.4')
        altered=copy.deepcopy(receipt)
        pos=altered['run']['argv'].index('-c')
        altered['run']['argv'][pos:pos]=['python3','-B']
        with self.assertRaisesRegex(C.Refused,'external Docker command/result mismatch'):
            C.validate_image_receipt(altered)

    def test_receipt_output_exit_image_and_absence_mismatch_refused(self):
        receipt=json.loads(C.read_exact(C.IMAGE_RECEIPT,C.IMAGE_RECEIPT_SHA))
        mutations=(('run','stdout_sha256','0'*64),
                   ('run','os_exit_code',1),
                   ('after_container_inspect','os_exit_code',0),
                   ('image_inspect','stdout_sha256','0'*64))
        for section,key,value in mutations:
            altered=copy.deepcopy(receipt)
            altered[section][key]=value
            with self.subTest(section=section,key=key):
                with self.assertRaises(C.Refused):
                    C.validate_image_receipt(altered)
        altered=copy.deepcopy(receipt)
        altered['image_id']='sha256:'+'0'*64
        with self.assertRaises(C.Refused):
            C.validate_image_receipt(altered)

    def staged_family(self,tmp):
        family=Path(tmp)/'family'
        source=family/'snapshot'/C.SOURCE_REL
        reader=family/'reader'
        (source/'packages/0001').mkdir(parents=True)
        reader.mkdir(parents=True)
        selection=json.loads(C.read_exact(C.INTEGRATION,C.INTEGRATION_SHA))
        files=((selection['source']['source_manifest_path'],source/'source-manifest.json',
                selection['source']['source_manifest_sha256']),
               (selection['source']['package_manifest_path'],source/'packages/0001/manifest.json',
                selection['source']['package_manifest_sha256']),
               (selection['reader']['source_manifest_path'],reader/'source-manifest.json',
                selection['reader']['source_manifest_sha256']),
               (selection['reader']['reader_code_path'],reader/'reader.py',
                selection['reader']['reader_code_sha256']))
        for origin,target,pin in files:
            target.write_bytes(C.read_exact(Path(origin),pin))
        return family

    def test_synthetic_same_family_reader_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            family=self.staged_family(tmp)
            raw,proof=C.project_reader_binding(family)
            value=json.loads(raw)
            self.assertEqual(value['entrypoint_ref'],str(family/'reader/reader.py')+'#SelectedReader.open_signed')
            self.assertEqual(proof['binding_sha256'],C.sha(raw))
            self.assertFalse(proof['private_archive_body_read'])

    def test_changed_reader_manifest_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            family=self.staged_family(tmp)
            path=family/'reader/source-manifest.json'
            path.write_bytes(path.read_bytes()+b' ')
            with self.assertRaisesRegex(C.Refused,'digest differs'):
                C.project_reader_binding(family)

    def test_reader_family_outside_tmp_refused_before_read(self):
        with mock.patch.object(C,'read_exact',side_effect=AssertionError('read after bad family')):
            with self.assertRaisesRegex(C.Refused,'external family root'):
                C.project_reader_binding(Path('/var/unsafe-family'))

    def test_no_effect_or_final_manifest(self):
        for fn in (C.final_context_manifest,C.launch_context):
            with self.assertRaises(C.Refused):
                fn()

if __name__=='__main__':
    unittest.main()
