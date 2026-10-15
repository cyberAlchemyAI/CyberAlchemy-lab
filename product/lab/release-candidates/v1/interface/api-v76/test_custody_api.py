"""Original-source public API, complete SQL, raw core and stdio checks."""
from .example_fixture import *
from .service import *
from .projection_refresh import control as projection_control
from . import artifact_model as model
from .custody_context_sessions import D,R
from contextlib import ExitStack
import base64,copy,json,os,subprocess,sys,tempfile,unittest
class OriginalAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stack=ExitStack();cls.addClassCleanup(cls.stack.close)
        cls.view=cls.stack.enter_context(source.replay_source('custody-participation'));cls.schemas=Schemas(PROFILE)
        cls.materials,cls.metadata,cls.target=materials_for(cls.view)
    def setUp(self):
        self.stack=ExitStack();self.addCleanup(self.stack.close)
        self.root=Path(self.stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-R03-original-API-check-')));self.root.chmod(0o700)
        self.key,self.policy,self.pin=provision(self.root,'custody-participation',self.materials,self.metadata,principal=R.PRINCIPAL,projection_control=projection_control(self.view))
        self.channel=ReaderChannel(self.policy,self.pin,self.schemas);self.channel.authenticate(proof(self.key,self.channel.challenge))
        self.service=Service(self.view,self.channel,self.schemas);self.addCleanup(self.service.close)
        # The child owns this method's workspace lease; the parent is unused.
        if self._testMethodName=='test_13_actual_stdout_nonce_authenticated_status':self.service.close()
    def success(self,c):
        raw=compact(c);r=self.service.call(raw)
        from .fixture_observation import record
        record(self.id(),self.service,raw,r)
        self.assertTrue(self.schemas.valid('api-reply',r),r);self.assertEqual(r['kind'],'result',r)
        self.assertEqual(r['request_binding']['sha256'],source.sha(raw));return r['message']
    def test_01_same_original_reader_objects(self):
        self.assertIs(source.custody_delivery(),D);self.assertIs(self.service.sessions.source,self.view.custody_signed_sources)
        self.assertIs(D.reader,D.MAPPED.reader);self.assertIs(D.EL,D.reader.adapter.eligibility)
    def test_02_actual_selected_engine_profile_cut(self):
        result=self.success(call(self.channel.context,'lab.status',cut(self.view)))
        self.assertEqual(result['source_cut'],self.view.custody_signed_sources.source_cut)
        self.assertEqual(result['source_cut']['source_profile_sha256'],self.view.handle.manifest['profile_binding']['sha256'])
        self.assertEqual(self.channel.context['source_profile_binding'],result['source_profile_binding'])
    def test_03_all23original_bytes_and_headers(self):
        subjects=[s for s in self.view.subjects.values() if s['source'].get('encoding')==self.view.handle.custody.ENCODING];self.assertEqual(len(subjects),23)
        for s in subjects:
            raw,locator,encoding,enclosing=model.record_bytes(self.view,s);h=model.artifact_ref(self.view,s)
            self.assertEqual(raw,D.reader.adapter.model.record_bytes(self.view,s)[0]);self.assertEqual(source.sha(raw),h['byte_sha256'])
            self.assertEqual(encoding,self.view.handle.custody.ENCODING);self.assertNotEqual(raw,self.view.handle.common.encoded(s['record']));self.assertNotEqual(enclosing,h['byte_sha256'])
            self.assertTrue(locator.endswith('/content/data'))
    def test_04_actual_product_revision_witness(self):
        subject=self.view.subjects['product:cyberalchemy-lab@current-episode-0003.candidate.1'];header=model.artifact_ref(self.view,subject)
        self.assertNotEqual(header['version_ref'].rsplit('@',1)[1],subject['record']['version'])
        result=self.success(call(self.channel.context,'artifact.inspect',cut(self.view),artifact=header,include=['body','contract','authority','provenance','gaps']))
        self.assertEqual(result['envelope']['artifact'],header);self.assertEqual(result['envelope']['decoded_artifact']['body'],subject['record'])
        self.assertEqual(result['envelope']['content']['byte_sha256'],subject['source']['sha256'])
    def test_05_all10declared_source_connections_current(self):
        rows,gaps=model.connections(self.view,self.schemas)
        actual=[r for r in rows if r['version_ref'].startswith('typed-relation:R03-current-episode-0004:')]
        self.assertEqual(len(actual),10)
        for row in actual:
            c=row['connection']
            for endpoint in ['source','target']:
                h=c[endpoint]['artifact'];self.assertEqual(h,model.artifact_ref(self.view,self.view.subjects[h['version_ref']]))
            self.assertIn(c['relation_kind_ref'],self.view.data['projection']['relation_contracts']);self.assertNotEqual(c['signature_sha256'],'0'*64)
    def test_06_complete_SQL_original_body_BLOBs(self):
        from .projection import Generation,DATA_TABLES
        generation=Generation(self.view,cut(self.view),self.schemas);self.addCleanup(generation.close)
        self.assertEqual(generation.db.execute('SELECT count(*) FROM artifact_revision').fetchone()[0],len(self.view.subjects))
        self.assertEqual(generation.metadata[2],self.view.handle.manifest['profile_binding']['sha256'])
        for s in self.view.subjects.values():
            if s['source'].get('encoding')!=self.view.handle.custody.ENCODING:continue
            h=model.artifact_ref(self.view,s);raw=model.record_bytes(self.view,s)[0]
            self.assertEqual(generation.db.execute('SELECT content FROM content_cache WHERE byte_sha256=?',(h['byte_sha256'],)).fetchone()[0],raw)
        self.assertEqual(generation.db.execute('SELECT stream_ref,cursor,head_sha256 FROM stream_watermark ORDER BY stream_ref').fetchall(),[(s['stream_ref'],s['cursor'],s['head_sha256']) for s in sorted(cut(self.view)['streams'],key=lambda s:s['stream_ref'])])
        self.assertEqual(generation.db.execute('PRAGMA integrity_check').fetchall(),[('ok',)]);self.assertEqual(generation.db.execute('PRAGMA foreign_key_check').fetchall(),[])
        self.assertEqual(set(DATA_TABLES),{'stream_watermark','content_cache','artifact_revision','artifact_head','typed_relation_projection','contract_binding_projection','reference_resolution','authority_fact_projection','ontology_representation_link','projection_gap'})
    def test_07_raw_prepare_compares_full_core(self):
        review=self.success(candidate_call(self.service,self.target));self.assertEqual(review['stable_core_bindings'],[self.target['decision_core_binding']])
        report=source.parse(self.service.vault.object_read(review['validation_report_binding']))
        self.assertTrue(any(c['check_ref']=='check:exact-source-target-schema-core' and c['result']=='pass' for c in report['checks']),report)
        self.assertNotEqual(report['result'],'fail');self.assertEqual(review['posture'],'blocked')
    def test_08_legacy_core_cannot_authorize_raw_target(self):
        body=source.parse(self.materials['candidate:work-content']);target={'category':'artifact-instance','operation':'admit','version_ref':self.target['artifact']['version_ref'],'carrier_ref':self.target['artifact']['carrier_ref'],'record':body,'predecessor_ref':None,'decision_ref':'decision:R03-candidate-admit','contract':None}
        old={'decision_ref':target['decision_ref'],'category':target['category'],'operation':target['operation'],'version_ref':target['version_ref'],'target_digest':self.view.handle.common.digest(target)}
        actual=source.parse(self.materials['candidate:work-core']);self.assertNotEqual(actual,old)
        selected=self.target['decision_core_binding'];path=self.service.vault.root/self.service.vault.inputs[selected['ref']]['path'];saved=path.read_bytes();path.write_bytes(self.view.handle.common.encoded(old))
        try:self.assertEqual(self.service.call(compact(candidate_call(self.service,self.target)))['code'],'unauthenticated-channel')
        finally:path.write_bytes(saved)
    def test_09_schema_originals_enter_actual_final_target_shape(self):
        with_bytes=self.view.handle.custody.with_originals({'schema_version':'lab-runtime-proposal/v1','proposal_id':'proposal:byte-shape-proof','expected_head':self.view.data['head']['transaction_digest'],'source_snapshot_digest':self.view.data['config']['source_snapshot_digest'],'scope_ref':self.view.data['config']['scope_ref'],'policy_ref':self.view.data['config']['policy_ref'],'challenge_route':self.view.data['config']['challenge_route'],'schemas':{},'targets':[]},{},{},exact_schema_bytes=True)
        self.assertEqual(with_bytes['schema_version'],'lab-runtime-original-json-proposal/v2-candidate');self.assertEqual(with_bytes['schema_contents'],{})
    def test_10_SQL_and_canonical_queries_have_exact_header_parity(self):
        from .projection import Generation
        generation=Generation(self.view,cut(self.view),self.schemas);self.addCleanup(generation.close)
        c=call(self.channel.context,'artifact.query',cut(self.view),carrier_refs=['cal.artifact-type.work/v1'],identity_refs=[R.WORK],max_depth=1,limit=1000)
        m=c['message'];expected=model.select(model.references(self.view),model.connections(self.view,self.schemas)[0],m);actual=generation.query(m)
        self.assertEqual(sorted(actual[0],key=lambda h:h['version_ref']),sorted(expected[0],key=lambda h:h['version_ref']))
        self.assertEqual(sorted(actual[1],key=lambda h:h['version_ref']),sorted(expected[1],key=lambda h:h['version_ref']))
    def test_11_fixed_original_period_and_owned_host_scope(self):
        p=D.load(D.reader.HERE/'packages/0001/period.json');v=self.channel.policy
        self.assertEqual(p['not_before'],'2026-10-10T21:02:19.890302+00:00')
        self.assertEqual(p['expires_at'],'2026-10-11T21:02:19.890302+00:00');self.assertLessEqual(instant(v['expires_at']),instant(p['expires_at']))
        old=p['original_expired_period_binding'];raw=source.original(old)
        self.assertEqual(source.parse(raw)['expires_at'],'2026-10-10T02:45:14.443492+00:00');self.assertEqual(source.sha(raw),old['sha256'])
        self.assertEqual(v['principal_ref'],R.PRINCIPAL);self.assertEqual(v['session_control']['period_binding']['sha256'],source.sha((D.reader.HERE/'packages/0001/period.json').read_bytes()))
    def test_12_historical_prefix_uses_raw_inspection(self):
        self.assertEqual(len(self.service.handlers.available_views),3)
        v=self.service.handlers.available_views[1];self.assertIsInstance(v,D.reader.Inspection)
        for s in v.subjects.values():
            if s['source'].get('encoding')==v.handle.custody.ENCODING:self.assertEqual(source.sha(model.record_bytes(v,s)[0]),model.artifact_ref(v,s)['byte_sha256'])
    def test_13_actual_stdout_nonce_authenticated_status(self):
        process=subprocess.Popen([sys.executable,str(HERE/'serve.py'),'--source-sha256',source.sha((HERE/'source-manifest.json').read_bytes()),'--policy',str(self.policy),'--policy-sha256',self.pin,'--protocol-profile-sha256',PROFILE],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        try:
            challenge=source.parse(process.stdout.readline());process.stdin.write(proof(self.key,challenge)+b'\n');process.stdin.flush()
            authenticated=source.parse(process.stdout.readline());self.assertEqual(authenticated['schema_version'],'lab-local-reader-authenticated/v1-candidate')
            c=call(authenticated['context'],'lab.status',cut(self.view));process.stdin.write(compact(c)+b'\n');process.stdin.flush()
            result=source.parse(process.stdout.readline());self.assertTrue(self.schemas.valid('api-reply',result),result);self.assertEqual(result['kind'],'result',result)
            self.assertEqual(result['message']['supported_operations'],list(SUPPORTED));self.assertEqual(result['message']['source_cut'],self.view.custody_signed_sources.source_cut)
            process.stdin.close();process.wait(timeout=60);self.assertEqual(process.returncode,0,process.stderr.read())
        finally:
            if process.poll() is None:process.kill();process.wait()
    def test_14_unknown_encoding_is_not_serializer_fallback(self):
        subject=next(s for s in self.view.subjects.values() if s['source'].get('encoding'));saved=subject['source']['encoding'];subject['source']['encoding']='unknown-original-encoding'
        try:
            with self.assertRaises(Exception):model.record_bytes(self.view,subject)
            with self.assertRaises(Exception):model.artifact_ref(self.view,subject)
        finally:subject['source']['encoding']=saved
