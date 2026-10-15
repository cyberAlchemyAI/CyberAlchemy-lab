from __future__ import annotations
import base64,copy,json,sqlite3,subprocess,sys,unittest
from pathlib import Path
import test_runtime as legacy
from lab_runtime.cli import example
from lab_runtime.common import RuntimeFault,atomic,byte_digest,digest,encoded,load,sealed
from lab_runtime.custody import (ENCODING,MAX_CONTENT_BYTES,content_entry,decode_content,equivalent,
    with_originals,original_bytes,content_rows,build_content_cache,parse_original,validate_proposal_content)
from lab_runtime.protocols import SCHEMAS
from lab_runtime.store import Store
PACKAGE=Path('/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/interface/custody-correction-v4/runtime');REPO=Path('/home/vlad_/projects/CyberAlchemy-lab')
OBSERVATIONS=[]

def raw_json(value):
    return (' \r\n'+json.dumps(value,indent=4,ensure_ascii=True,allow_nan=False).replace('\n','\r\n')+'\r\n\t').encode('utf-8')

class CustodyTests(unittest.TestCase):
    setUp=legacy.RuntimeTests.setUp
    commit=legacy.RuntimeTests.commit
    def proposal(self,name='original-work'):
        p=example(self.store,name);p['targets'][0]['record']['name']='Original café 🔬'
        return with_originals(p,{p['targets'][0]['version_ref']:raw_json(p['targets'][0]['record'])},{})
    def head(self):return self.store.replay()['head']['transaction_digest']
    def read(self,p):return original_bytes(self.store,p['targets'][0]['version_ref'],self.head())
    def test_01_exact_review_commit_and_original_retrieval(self):
        p=self.proposal();raw=decode_content(p['targets'][0]['content']);review=self.store.review(p)
        self.assertNotEqual(raw,encoded(p['targets'][0]['record']))
        self.assertEqual(review['decision_cores'][0]['target_digest'],digest(p['targets'][0]))
        approval=self.store.authorize(p,self.key);result=self.store.apply(p,approval)
        self.assertEqual(self.read(p),raw)
        data=self.store.replay();tx=data['transactions'][-1];subject=data['projection']['subjects'][p['targets'][0]['version_ref']]
        self.assertEqual(tx['schema_version'],'lab-runtime-original-json-transaction/v1-candidate')
        self.assertEqual(subject['source']['sha256'],byte_digest(raw));self.assertEqual(subject['source']['encoding'],ENCODING)
        OBSERVATIONS.append({'example':'Reviewed original JSON with CRLF, spaces and Unicode escapes',
            'raw_base64':base64.b64encode(raw).decode(),'original_byte_sha256':byte_digest(raw),
            'inherited_encoded_byte_sha256':byte_digest(encoded(p['targets'][0]['record'])),
            'structural_record_digest':digest(p['targets'][0]['record']),'review':review,
            'fixture_approval':approval,'transaction_digest':result['transaction_digest'],
            'source_binding':subject['source'],'actual_owner_outcome':None,'repository_admission_effect':'none'})
    def test_02_changed_encoding_needs_a_new_signed_review(self):
        p=self.proposal();a=self.store.authorize(p,self.key);changed=copy.deepcopy(p)
        changed['targets'][0]['content']=content_entry(encoded(p['targets'][0]['record']))
        self.assertNotEqual(self.store.review(p)['decision_cores'],self.store.review(changed)['decision_cores'])
        with self.assertRaisesRegex(RuntimeFault,'exact proposal'):self.store.apply(changed,a)
        self.assertEqual(self.store.status()['sequence'],0)
    def test_03_content_header_and_closed_encoding_rejections(self):
        p=self.proposal();entry=p['targets'][0]['content']
        variants=[{'byte_sha256':'0'*64},{'size_bytes':entry['size_bytes']+1},{'content_ref':'wrong'},
            {'encoding':'hex'},{'media_type':'text/plain'},{'semantic_binding':{'algorithm_ref':'invented','value_sha256':'0'*64}},
            {'data':'?'+entry['data'][1:]},{'data':entry['data']+'\n'},{'extra':True}]
        for changes in variants:
            with self.subTest(changes=list(changes)):
                bad=copy.deepcopy(p);bad['targets'][0]['content'].update(changes)
                with self.assertRaises(RuntimeFault):self.store.review(bad)
        self.assertEqual(self.store.status()['sequence'],0)
    def test_04_strict_original_json_parser(self):
        for raw in [b'{"x":1,"x":2}',b'{"x":NaN}',b'{"x":Infinity}',b'{"x":1e999}',
            b'{"x":"\\ud800"}',b'[]',b'\xff',b'\xef\xbb\xbf{}',b'{} trailing']:
            with self.subTest(raw=raw):
                with self.assertRaises(RuntimeFault):content_entry(raw)
    def test_05_parsed_value_equivalence_has_no_numeric_boolean_collapse(self):
        for raw,record in [(b'{"x":true}',{'x':1}),(b'{"x":1}',{'x':1.0}),(b'{"x":2}',{'x':3})]:
            with self.assertRaises(RuntimeFault):equivalent(raw,record)
        equivalent(b' { "x" : "caf\\u00e9" } \r\n',{'x':'café'})
    def test_06_missing_and_unreviewed_originals_fail(self):
        p=self.proposal();bad=copy.deepcopy(p);bad['targets'][0]['content']=None
        with self.assertRaises(RuntimeFault):self.store.review(bad)
        bad=copy.deepcopy(p);del bad['targets'][0]['content']
        with self.assertRaises(RuntimeFault):self.store.review(bad)
        bad=copy.deepcopy(p);bad['targets'][0]['record']['name']='Different'
        with self.assertRaises(RuntimeFault):self.store.review(bad)
    def test_07_cold_process_retrieves_original_bytes(self):
        p=self.proposal();raw=decode_content(p['targets'][0]['content']);self.commit(p)
        code="import sys,base64;sys.path.insert(0,sys.argv[1]);from lab_runtime.store import Store;from lab_runtime.custody import original_bytes;s=Store(sys.argv[2],sys.argv[3]);print(base64.b64encode(original_bytes(s,sys.argv[4],sys.argv[5])).decode())"
        result=subprocess.run([sys.executable,'-c',code,str(PACKAGE),str(self.store.path),str(REPO),p['targets'][0]['version_ref'],self.head()],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(base64.b64decode(result.stdout),raw)
        OBSERVATIONS.append({'episode':'cold-original-read','exit_code':result.returncode,'returned_base64':result.stdout.strip(),'original_byte_sha256':byte_digest(raw)})
    def test_08_disposable_sqlite_blob_parity_and_rebuild(self):
        p=self.proposal();raw=decode_content(p['targets'][0]['content']);self.commit(p);path=self.root/'cache.sqlite'
        report=build_content_cache(self.store,path,self.head())
        with sqlite3.connect(path) as db:
            self.assertEqual(db.execute('SELECT raw,byte_sha256 FROM contents').fetchall(),[(raw,byte_digest(raw))])
        path.unlink();report2=build_content_cache(Store(self.store.path,REPO),path,self.head())
        self.assertEqual(report['file_sha256'],report2['file_sha256']);self.assertEqual(self.read(p),raw)
        OBSERVATIONS.append({'episode':'SQLite-BLOB-canonical-parity-delete-and-cold-rebuild','first':report,'rebuilt':report2,'blob_sha256':byte_digest(raw)})
    def test_09_corrupt_cache_is_never_a_replay_source(self):
        p=self.proposal();raw=decode_content(p['targets'][0]['content']);self.commit(p);path=self.root/'cache.sqlite'
        build_content_cache(self.store,path,self.head())
        with sqlite3.connect(path) as db:db.execute('UPDATE contents SET raw=?',(b'forged',));db.commit()
        self.assertEqual(self.read(p),raw);self.assertEqual(self.store.status()['sequence'],1)
    def test_10_schema_originals_and_new_carrier_preserved(self):
        p=example(self.store,'schema');work=self.store.replay()['projection']['contracts']['cal.artifact-type.work/v1']
        schema=copy.deepcopy(self.store.replay()['projection']['documents'][work['schema_path']]);path='runtime/schemas/custody-work-v1.json';sha=byte_digest(encoded(schema))
        record={'artifact_type_ref':'cal.artifact-type.custody-work/v1','semantic_kind':'work','semantic_definition_refs':work['semantic_definition_refs'],
            'schema_path':path,'schema_selector':None,'schema_sha256':sha,'distinct_validation_purpose':'Exact original schema custody test.'}
        instance=p['targets'][0];instance['carrier_ref']=record['artifact_type_ref'];instance['decision_ref']='decision:local:schema-instance'
        p['schemas']={path:schema};p['targets']=[{'category':'artifact-type','operation':'admit','version_ref':record['artifact_type_ref'],'record':record,
            'carrier_ref':'cal.artifact-type.artifact-type/v3','predecessor_ref':None,'decision_ref':'decision:local:schema',
            'contract':{'semantic_kind':'work','schema_path':path,'schema_sha256':sha,'schema_selector':None,'instance_discriminator':work['instance_discriminator'],
                'identity_field':'node_id','allowed_relation_kinds':work['artifact']['allowed_relation_kinds'],'relation_roles':work['artifact']['relation_roles']}},instance]
        original=raw_json(schema);p=with_originals(p,{t['version_ref']:raw_json(t['record']) for t in p['targets']},{path:original})
        self.commit(p);rows=content_rows(self.store.replay());self.assertEqual(len(rows),3)
        row=next(r for r in rows if r['role']=='schema-input');self.assertEqual(row['raw'],original)
        self.assertNotEqual(row['byte_sha256'],sha)
        self.assertEqual(original_bytes(self.store,record['artifact_type_ref'],self.head()),raw_json(record))
        OBSERVATIONS.append({'episode':'schema-original-versus-inherited-schema-contract-encoding','original_schema_sha256':byte_digest(original),'inherited_contract_sha256':sha,'target_and_schema_rows':len(rows)})
    def test_11_missing_schema_original_or_extra_schema_fails(self):
        p=self.proposal();p['schemas']={'runtime/schemas/extra.json':{'type':'object'}}
        with self.assertRaises(RuntimeFault):self.store.review(p)
        p=self.proposal();p['schema_contents']={'extra':content_entry(b'{}')}
        with self.assertRaises(RuntimeFault):self.store.review(p)
    def test_12_originals_survive_revision_and_withdrawal(self):
        p=self.proposal();oldraw=decode_content(p['targets'][0]['content']);self.commit(p)
        data=self.store.replay();target=copy.deepcopy(p['targets'][0]);target.pop('content');oldver=target['version_ref']
        target.update(operation='revise',version_ref=target['record']['node_id']+'@candidate.2',predecessor_ref=oldver,decision_ref='decision:local:revision')
        target['record']['name']='Revised original';q=example(self.store,'revision');q['targets']=[target]
        newraw=raw_json(target['record']);q=with_originals(q,{target['version_ref']:newraw},{})
        self.commit(q);self.assertEqual(original_bytes(self.store,oldver,self.head()),oldraw);self.assertEqual(self.read(q),newraw)
        w=example(self.store,'withdraw');w['targets']=[{**target,'operation':'withdraw','predecessor_ref':target['version_ref'],'record':None,'contract':None,'decision_ref':'decision:local:withdraw'}]
        w=with_originals(w,{},{});self.commit(w)
        self.assertEqual(original_bytes(self.store,oldver,self.head()),oldraw);self.assertEqual(original_bytes(self.store,target['version_ref'],self.head()),newraw)
    def test_13_withdrawal_cannot_introduce_bytes(self):
        p=self.proposal();self.commit(p);q=example(self.store,'withdraw-bad');target=copy.deepcopy(p['targets'][0]);target.pop('content')
        target.update(operation='withdraw',predecessor_ref=target['version_ref'],record=None,contract=None,decision_ref='decision:local:withdraw-bad')
        q['targets']=[target];q=with_originals(q,{},{});q['targets'][0]['content']=content_entry(b'{}')
        with self.assertRaises(RuntimeFault):self.store.review(q)
        self.assertEqual(self.store.status()['sequence'],1)
    def test_14_mixed_legacy_and_original_transactions(self):
        legacy_p=example(self.store,'legacy-one');self.commit(legacy_p)
        p=self.proposal('original-two');self.commit(p);legacy_q=example(self.store,'legacy-three');self.commit(legacy_q)
        data=self.store.replay();self.assertEqual([t['schema_version'] for t in data['transactions']],['lab-runtime-transaction/v1','lab-runtime-transaction/v1','lab-runtime-original-json-transaction/v1-candidate','lab-runtime-transaction/v1'])
        self.assertEqual(original_bytes(self.store,legacy_p['targets'][0]['version_ref'],self.head()),encoded(legacy_p['targets'][0]['record']))
        self.assertEqual(self.read(p),decode_content(p['targets'][0]['content']))
    def test_15_v2_store_history_and_signatures_are_readable_without_rebase(self):
        path=self.root/'old-v2';code="import sys;sys.path.insert(0,sys.argv[1]);from lab_runtime.store import Store;from lab_runtime.cli import example;from lab_runtime.common import load;from pathlib import Path;s=Store(sys.argv[2],sys.argv[3]);s.initialize(load(Path(sys.argv[1])/'profile.json'),'legacy-custody','principal:isolated-test-fixture',Path(sys.argv[4]).read_text().strip());p=example(s,'old-work');s.apply(p,s.authorize(p,sys.argv[5]))"
        run=subprocess.run([sys.executable,'-c',code,str(REPO/'implementation/lab-runtime/v2'),str(path),str(REPO),str(self.pub),str(self.key)],capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stderr);before={p.name:byte_digest(p.read_bytes()) for p in (path/'transactions').iterdir()}
        old=Store(path,REPO);data=old.replay();self.assertEqual(data['head']['sequence'],1)
        self.assertEqual(original_bytes(old,data['transactions'][-1]['proposal']['targets'][0]['version_ref'],data['head']['transaction_digest']),encoded(data['transactions'][-1]['proposal']['targets'][0]['record']))
        with self.assertRaisesRegex(RuntimeFault,'stale repository sources'):old.replay(require_current=True)
        self.assertEqual(before,{p.name:byte_digest(p.read_bytes()) for p in (path/'transactions').iterdir()})
        OBSERVATIONS.append({'episode':'frozen-v2-committed-history-read-only-compatibility','original_transaction_hashes':before,'source_successor_write_blocked':True})
    def test_16_exact_retry_and_changed_original_conflict(self):
        p=self.proposal();a=self.store.authorize(p,self.key);first=self.store.apply(p,a);retry=self.store.apply(p,a)
        self.assertTrue(retry['idempotent']);self.assertEqual(first['transaction_digest'],retry['transaction_digest'])
        bad=copy.deepcopy(p);bad['targets'][0]['content']=content_entry(encoded(p['targets'][0]['record']))
        with self.assertRaisesRegex(RuntimeFault,'reused'):self.store.apply(bad,a)
    def crash_probe(self,stage):
        p=self.proposal();raw=decode_content(p['targets'][0]['content']);a=self.store.authorize(p,self.key)
        pf=self.root/'proposal.json';af=self.root/'approval.json';atomic(pf,encoded(p));atomic(af,encoded(a))
        code="import sys;sys.path.insert(0,sys.argv[1]);from lab_runtime.store import Store;from lab_runtime.common import load;Store(sys.argv[2],sys.argv[3]).apply(load(sys.argv[4]),load(sys.argv[5]),crash_at=sys.argv[6])"
        run=subprocess.run([sys.executable,'-c',code,str(PACKAGE),str(self.store.path),str(REPO),str(pf),str(af),stage],capture_output=True,text=True)
        self.assertEqual(run.returncode,86,run.stderr);data=self.store.replay();committed=stage=='after-head'
        self.assertEqual(data['head']['sequence'],1 if committed else 0)
        if committed:self.assertEqual(self.read(p),raw)
        else:
            with self.assertRaises(RuntimeFault):original_bytes(self.store,p['targets'][0]['version_ref'],self.head())
        report=self.store.recover(self.head());result=self.store.apply(p,a)
        self.assertEqual(result['idempotent'],committed);self.assertEqual(self.read(p),raw)
        OBSERVATIONS.append({'episode':'original-byte-crash-recovery','crash_stage':stage,'actual_child_exit_code':run.returncode,'recovery':report,'exact_original_sha256':byte_digest(self.read(p)),'idempotent_after_recovery':result['idempotent']})
    def test_17_crash_after_pending(self):self.crash_probe('after-pending')
    def test_18_crash_before_head(self):self.crash_probe('before-head')
    def test_19_crash_after_head(self):self.crash_probe('after-head')
    def test_20_resealed_content_tamper_does_not_bypass_signature(self):
        p=self.proposal();self.commit(p);path=self.store.path/'transactions/0000000001.json';tx=load(path)
        tx['proposal']['targets'][0]['content']=content_entry(encoded(p['targets'][0]['record']))
        changed=sealed({k:v for k,v in tx.items() if k!='digest'});atomic(path,encoded(changed));head=load(self.store.path/'HEAD.json');head['transaction_digest']=changed['digest'];atomic(self.store.path/'HEAD.json',encoded(sealed({k:v for k,v in head.items() if k!='digest'})))
        with self.assertRaisesRegex(RuntimeFault,'exact proposal'):self.store.replay()
    def test_21_protocol_schema_exports_are_exact(self):
        for name,schema in SCHEMAS.items():self.assertEqual(load(PACKAGE/'schemas'/f'{name}.schema.json'),schema,name)
    def test_22_material_and_size_bounds(self):
        with self.assertRaises(RuntimeFault):content_entry(b' '*MAX_CONTENT_BYTES+b'{}')
        p=self.proposal();p['targets']*=65
        with self.assertRaisesRegex(RuntimeFault,'count'):validate_proposal_content(p)
    def test_23_noncanonical_base64_pad_bits_rejected(self):
        entry=content_entry(b'{"x":12}')
        # Eight bytes end in a one-pad quartet: mutate only the unused pad bits.
        alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
        index=alphabet.index(entry['data'][-2]);entry['data']=entry['data'][:-2]+alphabet[index+1]+'='
        with self.assertRaisesRegex(RuntimeFault,'noncanonical base64'):decode_content(entry)
    def test_24_wrong_cut_and_unknown_exact_revision(self):
        p=self.proposal();self.commit(p)
        with self.assertRaises(RuntimeFault):original_bytes(self.store,p['targets'][0]['version_ref'],'0'*64)
        with self.assertRaises(RuntimeFault):original_bytes(self.store,p['targets'][0]['record']['node_id'],self.head())
        with self.assertRaises(RuntimeFault):build_content_cache(self.store,self.root/'wrong.sqlite','0'*64)
        self.assertFalse((self.root/'wrong.sqlite').exists())
    def test_25_existing_cache_path_is_preserved(self):
        p=self.proposal();self.commit(p);path=self.root/'occupied.sqlite';path.write_bytes(b'existing')
        with self.assertRaises(FileExistsError):build_content_cache(self.store,path,self.head())
        self.assertEqual(path.read_bytes(),b'existing')
    def test_26_original_baseline_whole_file_read(self):
        data=self.store.replay();subject=next(s for s in data['projection']['subjects'].values() if s['kind']=='work' and not s['source'].get('selector'))
        raw=original_bytes(self.store,subject['version_ref'],self.head());self.assertEqual(byte_digest(raw),subject['source']['sha256'])
    def test_27_duplicate_targets_are_atomic_rejection(self):
        p=self.proposal();p['targets'].append(copy.deepcopy(p['targets'][0]))
        with self.assertRaises(RuntimeFault):self.store.review(p)
        self.assertEqual(self.store.status()['sequence'],0)
    def test_28_multi_target_originals_share_one_commit(self):
        p=example(self.store,'multi-one');q=example(self.store,'multi-two');p['targets']+=q['targets'];p=with_originals(p,{t['version_ref']:raw_json(t['record']) for t in p['targets']},{})
        self.assertEqual(len(self.store.review(p)['decision_cores']),2);self.commit(p);self.assertEqual(self.store.status()['sequence'],1)
        for t in p['targets']:self.assertEqual(original_bytes(self.store,t['version_ref'],self.head()),decode_content(t['content']))
