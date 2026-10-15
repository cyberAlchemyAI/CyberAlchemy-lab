"""Raw original headers, scoped signed revision witnesses and immutable custody."""
import base64,copy,json,unittest
from dataclasses import replace
from unittest.mock import patch
from .base import *
from . import adapter,reader,records
OBSERVATIONS=[]
class OriginalSourceChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manager=reader.open_signed(SOURCE_PIN,PACKAGE_PIN);cls.selected=cls.manager.__enter__();cls.view=cls.selected.view
        cls.product=cls.selected.sources.resolve('product:cyberalchemy-lab')[0];cls.assignment=cls.selected.sources.resolve(records.ASSIGNMENT)[0]
    @classmethod
    def tearDownClass(cls):cls.manager.__exit__(None,None,None)
    def test_01_actual_product_original_revision_witness(self):
        r,body=self.selected.sources.get(self.product.artifact)
        self.assertEqual(r.revision_witness.encoding,self.view.handle.custody.ENCODING)
        self.assertNotEqual(r.original,encoded(body));self.assertNotEqual(r.artifact['version_ref'],r.artifact['identity_ref']+'@'+body['version'])
        OBSERVATIONS.append({'episode':'Actual original-content Product revision witness','artifact':copy.deepcopy(r.artifact),
            'original_base64':base64.b64encode(r.original).decode(),'source_cut':copy.deepcopy(self.selected.source_cut),
            'witness_selector':r.revision_witness.selector,'witness_encoding':r.revision_witness.encoding,
            'enclosing_original_sha256':r.revision_witness.enclosing_sha256,'body_version':body['version'],'actual_owner_outcome':None})
    def test_02_source_cut_pins_actual_executable_profile(self):
        self.assertEqual(self.selected.source_cut['source_profile_sha256'],self.view.handle.manifest['profile_binding']['sha256'])
        self.assertEqual(self.selected.source_cut['commit_sha256'],self.view.data['head']['transaction_digest'])
    def test_03_all_23_authored_target_bytes_are_retained(self):
        count=0
        for tx in self.view.data['transactions'][1:]:
            self.assertEqual(tx['schema_version'],'lab-runtime-original-json-transaction/v2-candidate')
            for t in tx['proposal']['targets']:
                s=self.view.subjects[t['version_ref']];raw=adapter.model.record_bytes(self.view,s)[0]
                self.assertEqual(raw,self.view.handle.custody.decode_content(t['content']));self.assertNotEqual(raw,encoded(t['record']));count+=1
        self.assertEqual(count,23)
    def test_04_inherited_generated_state_encoding_remains_declared(self):
        s=next(s for s in self.view.subjects.values() if s['kind']=='project-state' and s['effective_state']=='local-admitted-current')
        raw,_,encoding,_=adapter.model.record_bytes(self.view,s)
        self.assertEqual(encoding,'inherited-canonical-json-of-selected-original-value');self.assertEqual(raw,encoded(s['record']))
    def test_05_new_source_uses_new_principal_and_profile_identities(self):
        self.assertNotEqual(records.PRINCIPAL,'principal:R03-fresh-reader');self.assertNotEqual(records.PROFILE,'agent-profile:R03-fresh-reader')
        self.assertEqual(self.assignment.artifact['identity_ref'],records.ASSIGNMENT)
    def test_06_absolute_interval_and_original_binding_preserved(self):
        _,m,_=reader.package(SOURCE_PIN,PACKAGE_PIN);p=parse(original(m['period_binding']));old=parse(original(p['inherited_validity_binding']))
        self.assertEqual((p['not_before'],p['expires_at']),(old['not_before'],old['expires_at']))
        self.assertEqual(p['principal_ref'],records.PRINCIPAL)
    def test_07_domain_grant_remains_separate_from_project_scope(self):
        c=self.view.data['config'];self.assertEqual(c['schema_version'],'lab-runtime-store-config/v3-candidate')
        self.assertEqual(c['authorized_domain_scope_refs'],['scope:cyberalchemy-lab-first-agent-episode'])
        self.assertNotEqual(c['scope_ref'],c['authorized_domain_scope_refs'][0])
    def test_08_every_approval_binds_exact_configuration(self):
        for tx in self.view.data['transactions'][1:]:
            self.assertEqual(tx['approval']['configuration_digest'],self.view.handle.common.digest(self.view.data['config']))
            self.assertEqual(tx['approval']['schema_version'],'lab-runtime-approval/v2-candidate')
    def test_09_raw_headers_differ_from_enclosing_transaction_hash(self):
        s=self.view.subjects[self.assignment.artifact['version_ref']];report=self.view.source_record(s)
        self.assertNotEqual(report['original_file_sha256'],s['source']['sha256'])
        self.assertEqual(report['encoding'],self.view.handle.custody.ENCODING)
    def test_10_bridge_rejects_unknown_encoding(self):
        s=copy.deepcopy(self.view.subjects[self.assignment.artifact['version_ref']]);s['source']['encoding']='made-up'
        with self.assertRaises(Exception):adapter.model.record_bytes(self.view,s)
    def test_11_bridge_rejects_wrong_header_hash(self):
        s=copy.deepcopy(self.view.subjects[self.assignment.artifact['version_ref']]);s['source']['sha256']='0'*64
        with self.assertRaises(Exception):adapter.model.record_bytes(self.view,s)
    def test_12_bridge_rejects_wrong_content_reference(self):
        s=copy.deepcopy(self.view.subjects[self.assignment.artifact['version_ref']]);s['source']['content_ref']='other'
        with self.assertRaises(Exception):adapter.model.record_bytes(self.view,s)
    def test_13_bridge_rejects_wrong_store(self):
        s=copy.deepcopy(self.view.subjects[self.assignment.artifact['version_ref']]);s['source']['store_id']='other'
        with self.assertRaises(Exception):adapter.model.record_bytes(self.view,s)
    def test_14_bridge_rejects_wrong_record_selector(self):
        s=copy.deepcopy(self.view.subjects[self.assignment.artifact['version_ref']]);s['source']['record_selector']='/proposal/targets/0/record'
        with self.assertRaises(Exception):adapter.model.record_bytes(self.view,s)
    def witness(self,mutate=None,**changes):
        r=self.product;w=replace(r.revision_witness,**changes)
        if mutate:
            tx=parse(w.enclosing_original);mutate(tx);raw=encoded(tx);w=replace(w,enclosing_original=raw,enclosing_sha256=sha(raw))
        schema=next(s for s in self.selected.schemas if s.carrier_ref==r.artifact['carrier_ref'])
        row=replace(r,revision_witness=w)
        resolver=adapter.eligibility.ExactSources(self.selected.sources.scope_ref,self.selected.source_cut,[row],[schema],lambda:True)
        return resolver.get(row.artifact)
    def test_15_witness_wrong_cut_denied(self):
        with self.assertRaises(ValueError):self.witness(source_cut={})
    def test_16_witness_wrong_artifact_denied(self):
        with self.assertRaises(ValueError):self.witness(artifact_ref={**self.product.artifact,'byte_sha256':'0'*64})
    def test_17_witness_wrong_enclosing_hash_denied(self):
        with self.assertRaises(ValueError):self.witness(enclosing_sha256='0'*64)
    def test_18_witness_unknown_encoding_denied(self):
        with self.assertRaises(ValueError):self.witness(encoding='made-up')
    def test_19_witness_non_target_pointer_denied(self):
        with self.assertRaises(ValueError):self.witness(selector='/other/content/data')
    def test_20_witness_family_smuggling_denied(self):
        with self.assertRaises(ValueError):self.witness(lambda tx:tx.update(schema_version='lab-runtime-transaction/v1'))
    def test_21_witness_wrong_target_version_denied(self):
        with self.assertRaises(ValueError):self.witness(lambda tx:tx['proposal']['targets'][1].update(version_ref='product:other@1'))
    def test_22_witness_wrong_target_scope_denied(self):
        with self.assertRaises(ValueError):self.witness(lambda tx:tx['proposal'].update(scope_ref='project:other'))
    def test_23_witness_closed_content_entry_denied(self):
        with self.assertRaises(ValueError):self.witness(lambda tx:tx['proposal']['targets'][1]['content'].update(extra=True))
    def test_24_witness_changed_raw_encoding_denied(self):
        def change(tx):
            entry=tx['proposal']['targets'][1]['content'];raw=self.product.original+b' ';entry.update(data=base64.b64encode(raw).decode(),size_bytes=len(raw),byte_sha256=sha(raw),content_ref='runtime-content:sha256:'+sha(raw))
        with self.assertRaises(ValueError):self.witness(change)
    def test_25_witness_changed_parsed_record_denied(self):
        with self.assertRaises(ValueError):self.witness(lambda tx:tx['proposal']['targets'][1]['record'].update(name='changed'))
    def test_26_context_body_records_mutation_denied(self):
        row=self.selected.records[0];old=row.artifact['byte_sha256'];row.artifact['byte_sha256']='0'*64
        try:
            with self.assertRaises(ValueError):self.selected.guard()
        finally:row.artifact['byte_sha256']=old
    def test_27_resolver_record_mutation_denied(self):
        ref=self.assignment.artifact['version_ref'];old=self.selected.sources.records[ref]
        self.selected.sources.records[ref]=replace(old,posture='isolated-candidate-current')
        try:
            with self.assertRaises(ValueError):self.selected.guard()
        finally:self.selected.sources.records[ref]=old
    def test_28_resolver_cut_mutation_denied(self):
        old=copy.deepcopy(self.selected.sources.source_cut);self.selected.sources.source_cut['commit_sha256']='0'*64
        try:
            with self.assertRaises(ValueError):self.selected.guard()
        finally:self.selected.sources.source_cut=old
    def test_29_resolver_schema_mutation_denied(self):
        ref=self.assignment.artifact['carrier_ref'];old=self.selected.sources.schemas[ref]
        self.selected.sources.schemas[ref]=replace(old,version_binding_rule='verified-source-revision')
        try:
            with self.assertRaises(ValueError):self.selected.guard()
        finally:self.selected.sources.schemas[ref]=old
    def test_30_projection_mutation_denied(self):
        old=self.view.data['projection']['subjects'][self.assignment.artifact['version_ref']]['effective_state']
        self.view.data['projection']['subjects'][self.assignment.artifact['version_ref']]['effective_state']='admitted-current'
        try:
            with self.assertRaises(ValueError):self.selected.guard()
        finally:self.view.data['projection']['subjects'][self.assignment.artifact['version_ref']]['effective_state']=old
    def test_31_original_transaction_mutation_denied(self):
        name='transactions/0000000002.json';old=self.view.originals[name];self.view.originals[name]=old+b' '
        try:
            with self.assertRaises(ValueError):self.selected.guard()
        finally:self.view.originals[name]=old
    def test_32_no_private_body_no_liveness_no_public_export(self):
        for r in self.selected.records:adapter.eligibility.no_private_memory(parse(r.original),blank_session_policy=r.artifact['carrier_ref']=='cal.artifact-type.agent-session/v1')
        _,m,_=reader.package(SOURCE_PIN,PACKAGE_PIN);self.assertFalse(m['public_package_export_allowed'])
        report=self.selected.closure_report();self.assertFalse(report['fresh_Session_participation_established'])
        self.assertFalse(report['context_or_ontology_views_generated'])
