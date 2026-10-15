"""Actual exact-schema identity, immutability and cold custody checks."""
import base64,copy,json,sqlite3,subprocess,sys,unittest
import test_runtime as legacy
from lab_runtime.cli import example
from lab_runtime.common import RuntimeFault,byte_digest,encoded
from lab_runtime.custody import content_entry,content_rows,with_originals,schema_original_bytes,build_content_cache

OBSERVATIONS=[]
def raw_json(value):
    return (' \r\n'+json.dumps(value,indent=4,ensure_ascii=True).replace('\n','\r\n')+'\r\n\t').encode()

class ExactSchemaTests(unittest.TestCase):
    setUp=legacy.RuntimeTests.setUp
    commit=legacy.RuntimeTests.commit
    def head(self):return self.store.replay()['head']['transaction_digest']
    def proposal(self,name='exact-schema',*,captured_baseline=False):
        p=example(self.store,name);projection=self.store.replay()['projection']
        work=projection['contracts']['cal.artifact-type.work/v1']
        schema=copy.deepcopy(projection['documents'][work['schema_path']])
        path=work['schema_path'] if captured_baseline else 'runtime/schemas/exact-work~candidate.json'
        raw=schema_original_bytes(self.store,path,self.head()) if captured_baseline else raw_json(schema)
        sha=byte_digest(raw)
        record={'artifact_type_ref':'cal.artifact-type.exact-work/v1','semantic_kind':'work',
            'semantic_definition_refs':work['semantic_definition_refs'],'schema_path':path,
            'schema_selector':None,'schema_sha256':sha,'distinct_validation_purpose':'Exact original schema byte identity.'}
        instance=p['targets'][0];instance['carrier_ref']=record['artifact_type_ref']
        registration={'category':'artifact-type','operation':'admit','version_ref':record['artifact_type_ref'],
            'record':record,'carrier_ref':'cal.artifact-type.artifact-type/v3','predecessor_ref':None,
            'decision_ref':'decision:local:exact-schema',
            'contract':{'semantic_kind':'work','schema_path':path,'schema_sha256':sha,'schema_selector':None,
                'instance_discriminator':work['instance_discriminator'],'identity_field':'node_id',
                'allowed_relation_kinds':work['artifact']['allowed_relation_kinds'],'relation_roles':work['artifact']['relation_roles']}}
        p['targets']=[registration,instance];p['schemas']={} if captured_baseline else {path:schema}
        p=with_originals(p,{t['version_ref']:raw_json(t['record']) for t in p['targets']},
            {} if captured_baseline else {path:raw},exact_schema_bytes=True)
        return p,path,raw
    def reuse(self,name,path,raw,*,exact=True):
        p=example(self.store,name);p['targets'][0]['carrier_ref']='cal.artifact-type.exact-work/v1'
        p['schemas']={path:self.store.replay()['projection']['documents'][path]}
        return with_originals(p,{t['version_ref']:raw_json(t['record']) for t in p['targets']},{path:raw},exact_schema_bytes=exact)
    def test_01_descriptor_contract_and_replayed_source_bind_exact_original(self):
        p,path,raw=self.proposal();review=self.store.review(p);self.commit(p);data=self.store.replay()
        self.assertNotEqual(byte_digest(raw),byte_digest(encoded(p['schemas'][path])))
        contract=data['projection']['contracts']['cal.artifact-type.exact-work/v1']
        self.assertEqual(contract['schema_sha256'],byte_digest(raw))
        self.assertEqual(contract['artifact']['schema_sha256'],byte_digest(raw))
        binding=data['projection']['schema_content_bindings'][path]
        self.assertEqual(binding['byte_sha256'],byte_digest(raw))
        self.assertEqual(binding['path'],'transactions/0000000001.json')
        self.assertIn('~0',binding['selector']);self.assertIn('~1',binding['selector'])
        self.assertEqual(schema_original_bytes(self.store,path,self.head()),raw)
        OBSERVATIONS.append({'example':'Exact schema original with CRLF, indentation and escaped Unicode',
            'original_schema_base64':base64.b64encode(raw).decode(),'schema_path':path,
            'original_schema_sha256':byte_digest(raw),'inherited_encoded_schema_sha256':byte_digest(encoded(p['schemas'][path])),
            'descriptor':p['targets'][0]['record'],'contract':contract,'schema_source_binding':binding,
            'review':review,'transaction_family':data['transactions'][-1]['schema_version']})
    def test_02_inherited_encoding_digest_is_rejected_as_original(self):
        p,path,raw=self.proposal();wrong=byte_digest(encoded(p['schemas'][path]))
        p['targets'][0]['record']['schema_sha256']=wrong;p['targets'][0]['contract']['schema_sha256']=wrong
        p['targets'][0]['content']=content_entry(raw_json(p['targets'][0]['record']))
        with self.assertRaisesRegex(RuntimeFault,'schema digest mismatch'):self.store.review(p)
        self.assertEqual(self.store.status()['sequence'],0)
    def test_03_same_schema_path_with_changed_whitespace_is_rejected(self):
        p,path,raw=self.proposal();self.commit(p);q=self.reuse('changed-whitespace',path,raw+b' ')
        with self.assertRaisesRegex(RuntimeFault,'immutable schema original bytes conflict'):self.store.review(q)
        self.assertEqual(self.store.status()['sequence'],1)
    def test_04_same_original_reuse_keeps_first_source_identity(self):
        p,path,raw=self.proposal();self.commit(p)
        binding=copy.deepcopy(self.store.replay()['projection']['schema_content_bindings'][path])
        self.commit(self.reuse('same-original-reuse',path,raw))
        self.assertEqual(self.store.replay()['projection']['schema_content_bindings'][path],binding)
        self.assertEqual(schema_original_bytes(self.store,path,self.head()),raw)
    def test_05_legacy_family_cannot_overwrite_exact_schema_identity(self):
        p,path,raw=self.proposal();self.commit(p)
        q=self.reuse('legacy-collision',path,raw,exact=False)
        with self.assertRaisesRegex(RuntimeFault,'immutable schema original bytes conflict'):self.store.review(q)
    def test_06_raw_schema_change_invalidates_fixture_signature(self):
        p,path,raw=self.proposal();a=self.store.authorize(p,self.key);changed=copy.deepcopy(p)
        changed['schema_contents'][path]=content_entry(raw+b' ')
        sha=byte_digest(raw+b' ');changed['targets'][0]['record']['schema_sha256']=sha
        changed['targets'][0]['contract']['schema_sha256']=sha
        changed['targets'][0]['content']=content_entry(raw_json(changed['targets'][0]['record']))
        with self.assertRaisesRegex(RuntimeFault,'exact proposal'):self.store.apply(changed,a)
        self.assertEqual(self.store.status()['sequence'],0)
    def test_07_actual_schema_blob_parity_deletion_and_rebuild(self):
        p,path,raw=self.proposal();self.commit(p);cache=self.root/'schema-cache.sqlite'
        first=build_content_cache(self.store,cache,self.head())
        with sqlite3.connect(cache) as db:
            self.assertEqual(db.execute("SELECT raw,byte_sha256 FROM contents WHERE role='schema-input'").fetchall(),[(raw,byte_digest(raw))])
        cache.unlink();second=build_content_cache(self.store,cache,self.head())
        self.assertEqual(first['file_sha256'],second['file_sha256'])
        cache.unlink();self.assertEqual(schema_original_bytes(self.store,path,self.head()),raw)
        OBSERVATIONS.append({'episode':'Exact schema BLOB cache deletion and rebuild','first':first,'rebuilt':second})
    def test_08_actual_cold_process_schema_retrieval(self):
        p,path,raw=self.proposal();self.commit(p)
        code="import sys,base64;sys.path.insert(0,sys.argv[1]);from lab_runtime.store import Store;from lab_runtime.custody import schema_original_bytes;s=Store(sys.argv[2],sys.argv[3]);print(base64.b64encode(schema_original_bytes(s,sys.argv[4],sys.argv[5])).decode())"
        run=subprocess.run([sys.executable,'-c',code,str(legacy.PACKAGE),str(self.store.path),str(legacy.REPO),path,self.head()],capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stderr);self.assertEqual(base64.b64decode(run.stdout),raw)
        OBSERVATIONS.append({'episode':'Actual cold exact schema retrieval','exit_code':run.returncode,'returned_base64':run.stdout.strip()})
    def test_09_baseline_file_bytes_and_descriptor_identity_are_preserved(self):
        p,path,raw=self.proposal(captured_baseline=True)
        before=self.store.replay();known=before['projection']['contracts']['cal.artifact-type.work/v1']['schema_sha256']
        self.assertEqual(byte_digest(raw),known);self.commit(p)
        self.assertEqual(self.store.replay()['projection']['contracts']['cal.artifact-type.exact-work/v1']['schema_sha256'],known)
        self.assertEqual(schema_original_bytes(self.store,path,self.head()),raw)
    def test_10_wrong_cut_and_missing_schema_are_rejected(self):
        p,path,raw=self.proposal();self.commit(p)
        with self.assertRaises(RuntimeFault):schema_original_bytes(self.store,path,'0'*64)
        with self.assertRaises(RuntimeFault):schema_original_bytes(self.store,'runtime/schemas/absent.json',self.head())
    def test_11_unreviewed_or_missing_schema_content_is_rejected(self):
        p,path,raw=self.proposal();bad=copy.deepcopy(p);bad['schema_contents']={}
        with self.assertRaises(RuntimeFault):self.store.review(bad)
        bad=copy.deepcopy(p);bad['schema_contents'][path]['byte_sha256']='0'*64
        with self.assertRaises(RuntimeFault):self.store.review(bad)
        self.assertEqual(self.store.status()['sequence'],0)
    def test_12_legacy_raw_family_keeps_original_schema_and_prior_contract_encoding(self):
        p,path,raw=self.proposal();sha=byte_digest(encoded(p['schemas'][path]))
        p['schema_version']='lab-runtime-original-json-proposal/v1-candidate'
        p['targets'][0]['record']['schema_sha256']=sha;p['targets'][0]['contract']['schema_sha256']=sha
        p['targets'][0]['content']=content_entry(raw_json(p['targets'][0]['record']))
        self.commit(p);data=self.store.replay()
        self.assertNotIn(path,data['projection'].get('schema_content_bindings',{}))
        self.assertEqual(data['projection']['contracts']['cal.artifact-type.exact-work/v1']['schema_sha256'],sha)
        self.assertEqual(schema_original_bytes(self.store,path,self.head()),raw)
        self.assertEqual(next(r for r in content_rows(data) if r['role']=='schema-input')['raw'],raw)
