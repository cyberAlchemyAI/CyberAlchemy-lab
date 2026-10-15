"""Exact artifact bodies, selective disclosure and canonical/SQLite parity guards."""
from contextlib import ExitStack
import copy
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from fixtures import *
from service import *
import artifact_model as model
from projection import Generation,row_digest


class ArtifactGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stack=ExitStack();cls.root=Path(cls.stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-R03-readers-unit-')))
        cls.key,cls.policy,cls.pin=provision(cls.root);cls.schemas=Schemas()
        cls.view=cls.stack.enter_context(source.replay_source('engineering'))
        cls.definition=next(s for s in cls.view.subjects.values() if s['category']=='definition')
        cls.work=next(s for s in cls.view.subjects.values() if s['kind']=='evidence-set' and 'store_id' in s['source'])
    @classmethod
    def tearDownClass(cls):cls.stack.close()
    def setUp(self):
        self.channel=ReaderChannel(self.policy,self.pin,self.schemas);self.channel.authenticate(proof(self.key,self.channel.challenge))
        self.service=Service(self.view,self.channel,self.schemas)
    def tearDown(self):self.service.close()
    def invoke(self,operation,selected=None,**values):
        c=call(self.channel.context,operation,selected or cut(self.view),**values)
        return self.service.call(compact(c)),c
    def inspect(self,subject=None,**values):
        values.setdefault('artifact',model.artifact_ref(self.view,subject or self.definition))
        return self.invoke('artifact.inspect',**values)[0]
    def query(self,**values):return self.invoke('artifact.query',**values)[0]
    def assert_error(self,result,code):
        self.assertEqual(result['kind'],'error');self.assertEqual(result['message']['code'],code)
    def test_original_file_body_byte_identity(self):
        r=self.inspect();self.assertEqual(r['kind'],'result');m=r['message'];e=m['envelope']
        original=source.original(self.definition['source'])
        self.assertEqual(e['content']['byte_sha256'],source.sha(original));self.assertEqual(e['content']['size_bytes'],len(original))
        self.assertEqual(e['decoded_artifact']['body'],source.parse(original));self.assertTrue(self.schemas.valid('api-reply',r))
    def test_embedded_signed_body_exact_encoding(self):
        r=self.inspect(self.work);self.assertEqual(r['kind'],'result');e=r['message']['envelope']
        self.assertEqual(e['content']['byte_sha256'],source.sha(self.view.handle.common.encoded(self.work['record'])))
        self.assertIn('inherited-canonical',e['claim_ceiling']);self.assertIn('store:',e['source_locator'])
    def test_body_omission_does_not_disclose_body(self):
        r=self.inspect(include=['lifecycle']);m=r['message'];self.assertIsNone(m['envelope']);self.assertIsNone(m['contract_binding'])
        for k in ['authority_bindings','provenance_bindings','evidence_bindings','connections','gaps']:self.assertEqual(m[k],[])
    def test_body_only_does_not_disclose_excluded_authority(self):
        r=self.inspect(include=['body']);self.assertEqual(r['kind'],'result')
        self.assertEqual(r['message']['authority_bindings'],[]);self.assertEqual(r['message']['envelope']['effective_admission_basis'],[])
    def test_each_selected_section_is_independent(self):
        for section,key in [('contract','contract_binding'),('authority','authority_bindings'),('provenance','provenance_bindings'),('evidence','evidence_bindings'),('gaps','gaps'),('relations','connections')]:
            r=self.inspect(include=[section]);self.assertEqual(r['kind'],'result');m=r['message']
            self.assertEqual(m['included_sections'],[section]);self.assertIsNone(m['envelope'])
            if section!='contract':self.assertIsNone(m['contract_binding'])
            for excluded in ['authority_bindings','provenance_bindings','evidence_bindings','connections','gaps']:
                if excluded!=key:self.assertEqual(m[excluded],[])
    def test_admission_is_independent_of_runtime_outcome(self):
        f=self.inspect()['message']['status_facets'];self.assertEqual(f['admission'],self.definition['effective_state'])
        self.assertIsNone(f['runtime_observation']);self.assertIsNone(f['outcome'])
    def test_header_identity_mismatch_rejected(self):
        h=model.artifact_ref(self.view,self.definition);h['identity_ref']='identity:forged';self.assert_error(self.inspect(artifact=h),'invalid-contract')
    def test_header_carrier_mismatch_rejected(self):
        h=model.artifact_ref(self.view,self.definition);h['carrier_ref']='cal.artifact-type.work/v1';self.assert_error(self.inspect(artifact=h),'invalid-contract')
    def test_header_byte_mismatch_rejected(self):
        h=model.artifact_ref(self.view,self.definition);h['byte_sha256']='0'*64;self.assert_error(self.inspect(artifact=h),'invalid-contract')
    def test_header_scope_mismatch_rejected(self):
        h=model.artifact_ref(self.view,self.definition);h['scope_ref']='scope:foreign';self.assert_error(self.inspect(artifact=h),'unauthorized')
    def test_exact_unknown_revision_not_found(self):
        h=model.artifact_ref(self.view,self.definition);h['version_ref']='missing@1';self.assert_error(self.inspect(artifact=h),'not-found')
    def test_descriptor_schema_gap_not_faked_as_valid_body(self):
        descriptor=next(s for s in self.view.subjects.values() if s['version_ref']=='cal.artifact-type.work/v1')
        self.assert_error(self.inspect(descriptor),'invalid-contract')
        metadata=self.inspect(descriptor,include=['contract','gaps']);self.assertEqual(metadata['kind'],'result');self.assertTrue(metadata['message']['gaps'])
    def test_query_canonical_exact_independent_registry_definitions(self):
        r=self.query(limit=1000);self.assertEqual(r['kind'],'result');m=r['message']
        registry=self.view.data['baseline']['documents']['authority/definitions/registry.json']
        expected={row['definition_id']+'@'+row['version'] for row in registry['entries']}
        self.assertEqual({h['version_ref'] for h in m['results']},expected);self.assertEqual(len(expected),189)
        self.assertEqual(m['query_basis'],'canonical');self.assertIsNone(m['projection_generation']);self.assertEqual(m['freshness'],'current')
    def test_query_projection_full_inventory_parity(self):
        carriers=list(self.view.data['projection']['contracts'])
        a=self.query(carrier_refs=carriers,limit=1000);b=self.query(carrier_refs=carriers,limit=1000,query_basis='projection')
        self.assertEqual(a['kind'],b['kind']);self.assertEqual(b['kind'],'result');self.assertEqual(a['message']['results'],b['message']['results'])
        self.assertEqual(len(b['message']['results']),508);self.assertEqual(b['message']['query_basis'],'projection');self.assertIsNotNone(b['message']['projection_generation'])
    def test_query_historical_prefix_excludes_later_local_revisions(self):
        selected=cut(self.service.handlers.available_views[0]);r,_=self.invoke('artifact.query',selected,
            carrier_refs=['cal.artifact-type.evidence-set/v1'],freshness_requirement='exact-historical',limit=1000,query_basis='projection')
        self.assertEqual(r['kind'],'result');self.assertEqual(r['message']['freshness'],'historical')
        self.assertNotIn(self.work['version_ref'],{h['version_ref'] for h in r['message']['results']})
        self.assertEqual(r['message']['source_cut'],selected)
    def test_current_query_cannot_use_historical_prefix(self):
        selected=cut(self.service.handlers.available_views[0]);r,_=self.invoke('artifact.query',selected);self.assert_error(r,'stale-cut')
    def test_exact_historical_requirement_not_current_alias(self):self.assert_error(self.query(freshness_requirement='exact-historical'),'invalid-contract')
    def test_allow_stale_must_be_explicit(self):
        with patch.object(self.service.handlers,'current',return_value=False):
            self.assert_error(self.query(),'stale-cut');r=self.query(freshness_requirement='allow-stale',query_basis='projection')
            self.assertEqual(r['kind'],'result');self.assertEqual(r['message']['freshness'],'stale')
    def test_stale_cut_is_not_unknown_prefix_permission(self):
        selected=cut(self.view);selected['commit_sha256']='0'*64
        r,_=self.invoke('artifact.query',selected,freshness_requirement='allow-stale');self.assert_error(r,'stale-cut')
    def test_query_scope_not_authorized(self):self.assert_error(self.query(scope_refs=['scope:foreign']),'unauthorized')
    def test_query_depth_host_ceiling(self):self.assert_error(self.query(max_depth=5),'budget-exceeded')
    def test_query_limit_host_ceiling(self):self.assert_error(self.query(limit=1001),'budget-exceeded')
    def test_query_selector_host_ceiling(self):self.assert_error(self.query(identity_refs=['identity:'+str(i) for i in range(101)]),'budget-exceeded')
    def test_query_sql_parameters_do_not_execute(self):
        r=self.query(query_basis='projection',identity_refs=["x'); DROP TABLE artifact_revision; --"])
        self.assertEqual(r['kind'],'result');self.assertEqual(r['message']['results'],[])
        generation=next(iter(self.service.handlers.generations.values()));generation.verify()
        self.assertEqual(generation.db.execute('SELECT count(*) FROM artifact_revision').fetchone()[0],508)
    def test_query_identity_and_exact_version_filters(self):
        for value in [self.definition['identity'],self.definition['version_ref']]:
            r=self.query(identity_refs=[value]);self.assertEqual(r['kind'],'result');self.assertIn(self.definition['version_ref'],{x['version_ref'] for x in r['message']['results']})
    def test_query_cursor_paging_is_exact(self):
        a=self.query(limit=3,query_basis='projection');cursor=a['message']['next_page_cursor'];b=self.query(limit=3,query_basis='projection',page_cursor=cursor)
        self.assertEqual(b['kind'],'result');self.assertFalse({r['version_ref'] for r in a['message']['results']}&{r['version_ref'] for r in b['message']['results']})
        self.assertEqual(a['message']['projection_generation'],b['message']['projection_generation'])
    def test_query_cursor_selector_change_rejected(self):
        cursor=self.query(limit=3)['message']['next_page_cursor'];self.assert_error(self.query(limit=4,page_cursor=cursor),'invalid-cursor')
    def test_query_cursor_generation_change_rejected(self):
        cursor=self.query(limit=3,query_basis='projection')['message']['next_page_cursor']
        self.assert_error(self.query(limit=3,query_basis='canonical',page_cursor=cursor),'invalid-cursor')
    def test_query_cursor_cross_operation_rejected(self):
        c=self.invoke('catalog.get')[0]['message']['next_page_cursor'];self.assert_error(self.query(page_cursor=c),'invalid-cursor')
    def test_query_unknown_cursor_rejected(self):self.assert_error(self.query(page_cursor='cursor:unknown'),'invalid-cursor')
    def test_project_membership_traversal_preserves_raw_endpoints(self):
        values={'carrier_refs':['cal.artifact-type.evidence-set/v1'],'identity_refs':[self.work['version_ref']],
            'relation_kind_refs':['relation.member-of'],'max_depth':1,'limit':1000}
        a=self.query(**values);b=self.query(query_basis='projection',**values)
        self.assertEqual(a['kind'],b['kind']);self.assertEqual(b['kind'],'result');self.assertEqual(a['message']['results'],b['message']['results'])
        self.assertEqual(a['message']['connections'],b['message']['connections']);self.assertTrue(b['message']['connections'])
        self.assertTrue(any(c['target']['semantic_kind']=='project' and c['target']['artifact']['carrier_ref']=='cal.artifact-type.project-identity/v1' for c in b['message']['connections']))
    def test_zero_depth_no_connections(self):
        r=self.query(carrier_refs=['cal.artifact-type.evidence-set/v1'],identity_refs=[self.work['version_ref']],max_depth=0)
        self.assertEqual(r['message']['connections'],[])
    def test_relation_filter_controls_traversal(self):
        r=self.query(carrier_refs=['cal.artifact-type.evidence-set/v1'],identity_refs=[self.work['version_ref']],relation_kind_refs=['relation.tests-hypothesis'],max_depth=1)
        self.assertEqual(r['message']['connections'],[])
    def test_sql_corruption_not_authority(self):
        self.query(query_basis='projection');g=next(iter(self.service.handlers.generations.values()))
        with sqlite3.connect(g.path) as db:db.execute('UPDATE artifact_revision SET admission_posture=?',('fake-owner-admission',))
        self.assert_error(self.query(query_basis='projection'),'integrity-failed')
    def test_prefer_projection_explicit_canonical_fallback(self):
        self.query(query_basis='projection');g=next(iter(self.service.handlers.generations.values()))
        g.path.write_bytes(b'corrupt disposable projection')
        r=self.query(query_basis='prefer-projection');self.assertEqual(r['kind'],'result');self.assertEqual(r['message']['query_basis'],'canonical')
        self.assertIsNone(r['message']['projection_generation']);self.assertTrue(any('fell back' in gap['reason'] for gap in r['message']['gaps']))
    def test_sql_self_claimed_ready_digest_is_insufficient(self):
        self.query(query_basis='projection');g=next(iter(self.service.handlers.generations.values()))
        with sqlite3.connect(g.path) as db:
            db.execute('UPDATE stream_watermark SET cursor=cursor+1');db.execute('UPDATE projection_generation SET derived_rows_sha256=?',(row_digest(db),))
        self.assert_error(self.query(query_basis='projection'),'integrity-failed')
    def test_foreign_keys_and_integrity_checked(self):
        self.query(query_basis='projection');g=next(iter(self.service.handlers.generations.values()))
        self.assertEqual(g.db.execute('PRAGMA foreign_keys').fetchone(),(1,));self.assertEqual(g.db.execute('PRAGMA foreign_key_check').fetchall(),[])
        self.assertEqual(g.db.execute('PRAGMA integrity_check').fetchall(),[('ok',)])
    def test_generation_does_not_claim_ontology_or_owner_facts(self):
        self.query(query_basis='projection');g=next(iter(self.service.handlers.generations.values()))
        for table in ['authority_fact_projection','ontology_representation_link']:
            self.assertEqual(g.db.execute('SELECT count(*) FROM '+table).fetchone()[0],0)
        self.assertEqual(g.metadata[-2:],(0,'none'))
    def test_contract_identity_selectors_preserve_legacy_fields(self):
        self.query(query_basis='projection');g=next(iter(self.service.handlers.generations.values()))
        selectors=dict(g.db.execute('SELECT carrier_version_ref,identity_selector FROM contract_binding_projection'))
        self.assertEqual(selectors['cal.artifact-type.definition/v1'],'/definition_id')
        self.assertEqual(selectors['cal.artifact-type.artifact-type/v2'],'/artifact_type_id')
        self.assertEqual(selectors['cal.artifact-type.owner-registry/v1'],'/record_id')
        self.assertEqual(selectors['cal.artifact-type.work/v1'],'/node_id')
    def test_signature_lookup_key_and_subject_identity_stay_distinct(self):
        r=self.query(carrier_refs=['cal.artifact-type.evidence-set/v1'],identity_refs=[self.work['version_ref']],
            relation_kind_refs=['relation.member-of'],max_depth=1,query_basis='projection')
        self.assertEqual(r['kind'],'result');self.assertTrue(r['message']['connections']);g=next(iter(self.service.handlers.generations.values()))
        versions=[row[0] for row in g.db.execute('SELECT relation_kind_version_ref FROM typed_relation_projection')]
        signature,bind=model.signature(self.view,'relation.member-of')
        matched=next(s for s in self.view.subjects.values() if s['category']=='relation-kind' and s['record']==signature and s['source']['sha256']==bind['sha256'])
        self.assertIn(matched['version_ref'],versions);self.assertNotEqual(matched['identity'],'relation.member-of')
    def test_ambiguous_current_heads_remain_gaps(self):
        r=self.query(query_basis='projection');g=next(iter(self.service.handlers.generations.values()))
        counts=g.db.execute('SELECT identity_ref,count(*) FROM artifact_revision WHERE admission_posture IN (?,?) GROUP BY identity_ref HAVING count(*)>1',('admitted-current','local-admitted-current')).fetchall()
        self.assertTrue(counts)
        for identity,_ in counts:self.assertEqual(g.db.execute('SELECT count(*) FROM artifact_head WHERE identity_ref=?',(identity,)).fetchone()[0],0)
        self.assertTrue(any('unique artifact head' in gap['reason'] for gap in r['message']['gaps']))
    def test_generation_deleted_at_context_close(self):
        self.query(query_basis='projection');g=next(iter(self.service.handlers.generations.values()));path=g.path
        self.service.close();self.assertFalse(path.exists());self.assertIsNone(self.channel.context);self.assertEqual(self.service.handlers.generations,{})
    def test_rebuild_preserves_rows_without_reusing_old_generation(self):
        self.query(query_basis='projection');g=next(iter(self.service.handlers.generations.values()));rows=g.query(call(self.channel.context,'artifact.query',cut(self.view))['message'])[0]
        other=Generation(self.view,cut(self.view),self.schemas)
        try:
            self.assertNotEqual(other.ref,g.ref);self.assertEqual(rows,other.query(call(self.channel.context,'artifact.query',cut(self.view))['message'])[0])
            self.assertEqual(other.catalog_sha,g.catalog_sha);self.assertEqual(other.cut,g.cut)
        finally:other.close()


if __name__=='__main__':unittest.main()
