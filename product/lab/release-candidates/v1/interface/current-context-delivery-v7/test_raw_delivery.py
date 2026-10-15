"""Raw original bodies, same module/cut identities, lessons and bounded grants."""
from .build import *
from .base import dependency_input_bytes
import unittest
from types import SimpleNamespace
class OriginalDeliveryChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        verify_source(PIN);require(sha((HERE/'packages/0001/manifest.json').read_bytes())==PACKAGE,'independent Context package differs')
        cls.delivery=load(HERE/'packages/0001/delivery.json');cls.proof=load(HERE/'packages/0001/delivery-provenance.json');cls.index=load(HERE/'packages/0001/artifact-index.json')
        cls.manager=reader.open_signed(SOURCE_PIN,SOURCE_PACKAGE);cls.source=cls.manager.__enter__()
    @classmethod
    def tearDownClass(cls):cls.manager.__exit__(None,None,None)
    def test_39_all23raworiginalbodyheaders_preserved_in_delivery(self):
        count=0
        for row in self.proof['source_material_provenance']:
            subject=self.source.view.subjects[row['artifact']['version_ref']];raw,locator,encoding,enclosing=reader.adapter.model.record_bytes(self.source.view,subject)
            self.assertEqual(row['artifact']['byte_sha256'],sha(raw));self.assertEqual(row['selected_original_body_sha256'],sha(raw))
            self.assertEqual(row['selected_body_encoding'],encoding);self.assertEqual(row['original_material']['sha256'],enclosing)
            if encoding==self.source.view.handle.custody.ENCODING:self.assertNotEqual(raw,encoded(subject['record']));count+=1
        self.assertEqual(count,23)
    def test_40_reader_records_eligibility_are_same_selected_mapper_objects(self):
        self.assertIs(reader,MAPPED.reader);self.assertIs(records,MAPPED.records);self.assertIs(EL,reader.adapter.eligibility)
        self.assertIsInstance(self.source.sources,EL.ExactSources)
        self.assertEqual(self.proof['mapped_package_sha256'],MAPPED_PACKAGE)
    def test_41_current_actual_profile_and_product_revision_witness_retained(self):
        self.assertEqual(self.delivery['source_cut']['source_profile_sha256'],self.source.view.handle.manifest['profile_binding']['sha256'])
        product,body=self.source.sources.resolve('product:cyberalchemy-lab')
        self.assertEqual(product.revision_witness.encoding,self.source.view.handle.custody.ENCODING)
        self.assertNotEqual(product.artifact['version_ref'],product.artifact['identity_ref']+'@'+body['version'])
        self.assertIn(product.artifact,self.delivery['included_refs'])
    def test_42_current_API_profile_and_source_implementation_are_exact(self):
        s=API.Schemas(API_PROFILE_PIN);self.assertEqual(s.profile_sha,API_PROFILE_PIN);self.assertEqual(s.profile['implemented_operations'],list(API.SUPPORTED));self.assertEqual(len(API.SUPPORTED),13)
        b=load(HERE/'implementation-binding.json');self.assertEqual(b['entrypoint_ref'],'product/lab/release-candidates/v1/interface/current-source-adapter-v3/reader.py#SelectedReader.open_signed')
        self.assertEqual(b['code_binding']['sha256'],sha((ROOT/b['code_binding']['ref']).read_bytes()))
        body=load(HERE/'protocols/policy.json');self.assertEqual(body['reference'],records.POLICY)
    def test_43_generic_projection_kind_cannot_hide_declared_lesson_carrier(self):
        subject={'version_ref':'operational-lesson:classification-fixture@1','carrier_ref':'cal.artifact-type.operational-lesson/v1','kind':'artifact-instance','effective_state':'local-admitted-current'}
        view=SimpleNamespace(data={'projection':{'contracts':{'cal.artifact-type.operational-lesson/v1':{'semantic_kind':'operational-lesson'}}}},subjects={'fixture':subject})
        self.assertEqual(current_lesson_subjects(view),[subject])
    def test_44_older_and_unresolved_lesson_diagnostics_are_not_falsezero(self):
        current={'version_ref':'operational-lesson:unresolved@1','carrier_ref':None,'kind':'operational-lesson','effective_state':'local-admitted-current'}
        historical={**current,'version_ref':'operational-lesson:old@0','effective_state':'admitted-historical'}
        view=SimpleNamespace(data={'projection':{'contracts':{}}},subjects={'current':current,'old':historical})
        self.assertEqual(current_lesson_subjects(view),[current])
        self.assertEqual(current_lesson_subjects(self.source.view),[])
    def test_45_actual_owned_hostgrant_and_delivery_bounded_to_original_period(self):
        p=load(reader.HERE/'packages/0001/period.json');host=load(HERE/'packages/0001/host-permission-public.json')
        self.assertGreaterEqual(EL.instant(host['not_before']),EL.instant(p['not_before']));self.assertLessEqual(EL.instant(host['expires_at']),EL.instant(p['expires_at']))
        self.assertLessEqual(EL.instant(self.delivery['expires_at']),EL.instant(host['expires_at']))
        result=load(HERE/'packages/0001/build-result.json');self.assertFalse(Path(result['owned_host_root']).exists())
    def test_46_source_and_ontology_metadata_do_not_supply_current_host_permission(self):
        host=load(HERE/'packages/0001/host-permission-public.json');self.assertEqual(host['allowed_operations'],['context.get','session.open'])
        self.assertEqual(host['authority_effect'],'none');self.assertIsNone(host['actual_owner_outcome'])
        native=load(MAPPED.HERE/'packages/0001/mapping.json');self.assertFalse(native['projection_is_host_permission'])
        self.assertTrue(all('private_key' not in b for b in [self.delivery,self.proof,host]))

    def test_47_declared_lifetime_keeps_actual_request_host_and_source_bounds(self):
        policy=load(HERE/'lifetime-policy.json')
        self.assertEqual(policy['maximum_view_lifetime_seconds'],900)
        self.assertEqual(policy['default_request_seconds'],900)
        self.assertEqual(policy['authority_effect'],'none');self.assertIsNone(policy['actual_owner_outcome'])
        request=load(HERE/'packages/0001/request.json');host=load(HERE/'packages/0001/host-permission-public.json')
        period=load(reader.HERE/'packages/0001/period.json');expires=EL.instant(self.delivery['expires_at'])
        self.assertLessEqual(expires,min(EL.instant(request['budget']['deadline']),EL.instant(host['expires_at']),EL.instant(period['expires_at'])))
        row=next(r for r in self.index if r['artifact']['carrier_ref']=='cal.artifact-type.context-view/v1')
        view=load(ROOT/row['original_binding']['path'])
        self.assertLessEqual(expires-EL.instant(view['generated_at']),timedelta(seconds=policy['maximum_view_lifetime_seconds']))
        self.assertEqual(self.delivery['expires_at'],view['expires_at'])

    def test_48_retained_external_dependencies_are_not_domain_originals(self):
        manifest=load(HERE/'source-manifest.json');external=manifest['external_dependency_bindings']
        self.assertEqual(external,[r for r in manifest['files'] if Path(r['path']).is_absolute()])
        self.assertGreater(len(external),0)
        with self.assertRaisesRegex(ValueError,'unsafe source path'):original(external[0])
        with self.assertRaisesRegex(ValueError,'external dependency input not explicitly selected'):
            dependency_input_bytes({'path':'/unselected-external-dependency','sha256':'0'*64},external)
