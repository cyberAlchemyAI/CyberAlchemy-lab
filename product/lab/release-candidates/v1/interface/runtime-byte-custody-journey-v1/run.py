"""Actual isolated custody journey with public signature evidence, no keys export."""
import argparse,base64,hashlib,json,sqlite3,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)}
def guard(m):
    for row in m['files']:
        if sha(ROOT/row['path'])!=row['sha256']:raise RuntimeError('frozen journey source differs '+row['path'])
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-sha256',required=True);args=ap.parse_args()
    if sha(HERE/'source-manifest.json')!=args.source_sha256:raise RuntimeError('source pin differs')
    m=json.loads((HERE/'source-manifest.json').read_bytes());guard(m)
    runtime=ROOT/m['runtime_root'];sys.path.insert(0,str(runtime))
    from lab_runtime.common import RuntimeFault,byte_digest,digest,encoded,load
    from lab_runtime.store import Store,keygen
    from lab_runtime.cli import example
    from lab_runtime.custody import with_originals,decode_content,original_bytes,build_content_cache
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    with tempfile.TemporaryDirectory(prefix='cal-R03-original-byte-journey-') as temporary:
        root=Path(temporary);key=root/'fixture.pem';pub=root/'fixture.pub';keygen(key,pub)
        store=Store(root/'store',ROOT);store.initialize(load(runtime/'profile.json'),'original-byte-journey','principal:isolated-byte-custody-fixture',pub.read_text().strip())
        p=example(store,'original-byte-work');p['targets'][0]['record']['name']='Review the café experiment 🔬'
        raw=('\t\r\n'+json.dumps(p['targets'][0]['record'],indent=4,ensure_ascii=True).replace('\n','\r\n')+'\r\n ').encode('utf-8')
        p=with_originals(p,{p['targets'][0]['version_ref']:raw},{})
        initial=store.replay();review=store.review(p);approval=store.authorize(p,key)
        public_key=pub.read_text().strip();signed={k:v for k,v in approval.items() if k!='signature'}
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_key)).verify(bytes.fromhex(approval['signature']),encoded(signed))
        core=review['decision_cores'][0]
        assert core['target_digest']==digest(p['targets'][0]) and approval['proposal_digest']==digest(p)
        changed=json.loads(json.dumps(p));changed['targets'][0]['content']['data']=base64.b64encode(raw+b' ').decode();changed['targets'][0]['content']['size_bytes']+=1;changed['targets'][0]['content']['byte_sha256']=byte_digest(raw+b' ');changed['targets'][0]['content']['content_ref']='runtime-content:sha256:'+byte_digest(raw+b' ')
        try:store.apply(changed,approval)
        except RuntimeFault as exc:changed_error=str(exc)
        else:raise RuntimeError('modified original used an old signature')
        assert store.status()['sequence']==0
        first=store.apply(p,approval);retry=store.apply(p,approval);assert retry['idempotent'] and retry['transaction_digest']==first['transaction_digest']
        data=store.replay();assert original_bytes(store,p['targets'][0]['version_ref'],data['head']['transaction_digest'])==raw
        cache=root/'cache.sqlite';cache_report=build_content_cache(store,cache,data['head']['transaction_digest'])
        with sqlite3.connect(cache) as db:
            cache_raw,cache_sha=db.execute('SELECT raw,byte_sha256 FROM contents').fetchone();assert cache_raw==raw and cache_sha==byte_digest(raw)
        cache.unlink()
        code="import sys,base64;sys.path.insert(0,sys.argv[1]);from lab_runtime.store import Store;from lab_runtime.custody import original_bytes;s=Store(sys.argv[2],sys.argv[3]);print(base64.b64encode(original_bytes(s,sys.argv[4],sys.argv[5])).decode())"
        argv=[sys.executable,'-c',code,str(runtime),str(store.path),str(ROOT),p['targets'][0]['version_ref'],data['head']['transaction_digest']]
        cold=subprocess.run(argv,capture_output=True,text=True);assert cold.returncode==0,cold.stderr;assert base64.b64decode(cold.stdout)==raw
        txpath=store.path/'transactions/0000000001.json';txraw=txpath.read_bytes()
        report={'schema_version':'lab-original-byte-custody-journey/v1-candidate','result':'PASS','authority_effect':'none','actual_owner_outcome':None,
            'source_manifest_binding':bind(HERE/'source-manifest.json'),'runtime_source_binding':m['runtime_source_binding'],
            'fixture_public_key':public_key,'fixture_configuration':data['config'],'input_head':initial['head'],'proposal':p,'review':review,'fixture_approval':approval,
            'application_result':first,'exact_retry_result':retry,'changed_original_rejection':changed_error,
            'original_content_base64':base64.b64encode(raw).decode(),'original_byte_sha256':byte_digest(raw),
            'inherited_encoded_byte_sha256':byte_digest(encoded(p['targets'][0]['record'])),'structural_record_digest':digest(p['targets'][0]['record']),
            'original_signed_transaction_base64':base64.b64encode(txraw).decode(),'original_signed_transaction_byte_sha256':byte_digest(txraw),
            'source_binding':data['projection']['subjects'][p['targets'][0]['version_ref']]['source'],'output_head':data['head'],
            'cache_report':cache_report,'cache_deleted_before_cold_read':True,'cold_read_command':argv,'cold_read_exit_code':cold.returncode,'cold_original_base64':cold.stdout.strip(),
            'local_fixture_transactions':1,'repository_admissions_applied':0,'private_keys_exported':False,'private_memory_exported':False,
            'task_complete':False,'goal_complete':False,'claim_ceiling':'One owned signed JSON custody journey, externally verifiable fixture signature and exact original bytes. No actual owner decision or integrated admission/export API.'}
    assert not root.exists();report['owned_root']={'path':str(root),'removed':True};guard(m)
    path=HERE/'receipts/0001/result.json';path.parent.mkdir(parents=True,exist_ok=True);path.open('x').write(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'result':'PASS','result_binding':bind(path),'original_byte_sha256':report['original_byte_sha256'],'owned_root_removed':True}),flush=True)
if __name__=='__main__':main()
