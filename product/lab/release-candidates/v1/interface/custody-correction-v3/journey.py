"""Actual scoped correction with original byte custody and independent grants."""
import argparse,base64,copy,hashlib,json,sqlite3,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def raw_json(v):return (' \r\n'+json.dumps(v,indent=4,ensure_ascii=True).replace('\n','\r\n')+'\r\n\t').encode('utf-8')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-sha256',required=True);args=ap.parse_args()
    if sha(HERE/'source-manifest.json')!=args.source_sha256:raise RuntimeError('source pin differs')
    manifest=json.loads((HERE/'source-manifest.json').read_bytes())
    def guard():
        for row in manifest['files']:
            if sha(ROOT/row['path'])!=row['sha256']:raise RuntimeError('source changed '+row['path'])
    guard();sys.path.insert(0,str(HERE))
    from episode import DOMAIN,EnginePins,engine,parse,project_setup,correction_proposal,verify_result
    from reader_adapter import source_record
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    pins=EnginePins(**parse((HERE/'pins.json').read_bytes()));checks=[]
    def need(value,name):
        if not value:raise AssertionError(name)
        checks.append(name)
    with tempfile.TemporaryDirectory(prefix='cal-R03-custody-correction-journey-') as temporary,engine(pins) as handle:
        owned=Path(temporary);store,key=handle.create_owned(owned,'custody-correction-journey',selected_project_scope=True,correction_domains=[DOMAIN]);setup=project_setup(handle,store,key)
        before=store.replay(require_current=True);plain=correction_proposal(handle,before,'original-byte-corrections')
        originals={t['version_ref']:raw_json(t['record']) for t in plain['targets']};proposal=handle.custody.with_originals(plain,originals,{},exact_schema_bytes=True)
        need(proposal['schema_version']=='lab-runtime-reviewed-original-json-proposal/v2-candidate','distinct composed proposal')
        post,cores=handle.operations.prepare(before['projection'],proposal,before['head']['transaction_digest'],before['config'])
        need(len(cores)==10 and all(c['domain_scope_ref']==DOMAIN for c in cores),'ten independent original scoped cores')
        need(all(c['target_digest']==handle.common.digest(t) for c,t in zip(cores,proposal['targets'])),'raw bytes enter actual full core digests')
        for target in proposal['targets']:
            need(post['subjects'][target['version_ref']]['source']['sha256']==handle.common.byte_digest(originals[target['version_ref']]),'prepublication exact original header '+target['version_ref'])
        # Raw content grants no domains, members, changed values, qualifier or endpoint use.
        rejected=[]
        def rejection(p,config=None):
            try:handle.operations.prepare(before['projection'],p,before['head']['transaction_digest'],config or before['config'])
            except Exception as error:return str(error)
            raise AssertionError('unreviewed composed input accepted')
        for label,change in [('removed-profile',lambda p:p.pop('correction_profile_binding')),('wrong-profile',lambda p:p['correction_profile_binding'].update(sha256='0'*64)),('unreviewed-member',lambda p:p['targets'][0]['reference_correction_binding'].update(sha256='0'*64)),('raw-without-correction',lambda p:p['targets'][0].update(reference_correction_binding=None)),('family-smuggling',lambda p:p.update(schema_version='lab-runtime-original-json-proposal/v1-candidate'))]:
            p=copy.deepcopy(proposal);change(p);rejected.append({'case':label,'reason':rejection(p)});checks.append('reject '+label)
        config=copy.deepcopy(before['config']);config['authorized_domain_scope_refs']=['scope:other'];rejected.append({'case':'wrong-domain-grant','reason':rejection(proposal,config)});checks.append('reject wrong domain grant')
        approval=store.authorize(proposal,key);need(approval['schema_version']=='lab-runtime-approval/v2-candidate','scoped approval family retained')
        need(approval['configuration_digest']==handle.common.digest(before['config']) and approval['authorized_domain_scope_refs']==[DOMAIN],'signature binds unchanged exact config and domains')
        signed={k:v for k,v in approval.items() if k!='signature'};Ed25519PublicKey.from_public_bytes(bytes.fromhex(before['config']['public_key'])).verify(bytes.fromhex(approval['signature']),handle.common.encoded(signed));checks.append('actual exact fixture signature')
        changed=copy.deepcopy(proposal);t=changed['targets'][0];t['content']=handle.custody.content_entry(originals[t['version_ref']]+b' ')
        changed_post,changed_cores=handle.operations.prepare(before['projection'],changed,before['head']['transaction_digest'],before['config'])
        try:handle.store_module.verify_approval(approval,changed,changed_cores,before['config'])
        except Exception as error:rejected.append({'case':'changed-encoding-old-signature','reason':str(error)});checks.append('reject changed raw encoding under old signature')
        else:raise AssertionError('old signature accepted a changed original')
        applied=store.apply(proposal,approval);retry=store.apply(proposal,approval);need(retry['idempotent'] and retry['transaction_digest']==applied['transaction_digest'],'exact historical retry')
        after=store.replay(require_current=True);rows=verify_result(handle,before,after,proposal)
        need(after['transactions'][-1]['schema_version']=='lab-runtime-reviewed-original-json-transaction/v2-candidate','closed composed transaction family')
        originals_files={p.relative_to(store.path).as_posix():p.read_bytes() for p in store.path.rglob('*.json')};view=type('View',(),{'handle':handle,'data':after,'originals':originals_files})()
        read_rows=[]
        for target in proposal['targets']:
            raw=handle.custody.original_bytes(store,target['version_ref'],after['head']['transaction_digest']);need(raw==originals[target['version_ref']],'actual canonical original '+target['version_ref'])
            report,bridge=source_record(view,after['projection']['subjects'][target['version_ref']]);need(bridge==raw and report['parsed_record_matches'],'captured source reader original '+target['version_ref'])
            read_rows.append({'version_ref':target['version_ref'],'original_base64':base64.b64encode(raw).decode(),'source_binding':after['projection']['subjects'][target['version_ref']]['source'],'reader_report':report})
        path=owned/'cache.sqlite';cache=handle.custody.build_content_cache(store,path,after['head']['transaction_digest'])
        with sqlite3.connect(path) as db:
            got=dict(db.execute('SELECT version_ref,raw FROM contents WHERE role=?',('authored-target',)).fetchall())
            need(all(got[k]==v for k,v in originals.items()),'actual exact BLOBs for all ten correction originals')
        path.unlink();need(not path.exists(),'cache deleted before cold source reads')
        # A fresh process imports only the frozen runtime and replays the same existing owned fixture.
        runtime=HERE/'runtime';first=proposal['targets'][0]['version_ref']
        code="import sys,base64;sys.path.insert(0,sys.argv[1]);from lab_runtime.store import Store;from lab_runtime.custody import original_bytes;s=Store(sys.argv[2],sys.argv[3]);print(base64.b64encode(original_bytes(s,sys.argv[4],sys.argv[5])).decode())"
        command=[sys.executable,'-c',code,str(runtime),str(store.path),str(ROOT),first,after['head']['transaction_digest']];cold=subprocess.run(command,capture_output=True,text=True)
        need(cold.returncode==0 and base64.b64decode(cold.stdout)==originals[first],'actual cold original read after cache deletion')
        tx=after['transactions'][-1]
        report={'schema_version':'lab-custody-correction-journey/v1-candidate','result':'PASS','authority_effect':'none','actual_owner_outcome':None,'checks':len(checks),'check_names':checks,'source_sha256':args.source_sha256,'fixture_configuration':before['config'],'original_proposal':proposal,'review_cores':cores,'fixture_approval':approval,'application':applied,'retry':retry,'applied_corrections':rows,'original_read_rows':read_rows,'rejections':rejected,'cache_report':cache,'cold_read_command':command,'cold_read_exit_code':cold.returncode,'cold_original_base64':cold.stdout.strip(),'transaction_structural_digest':tx['digest'],'transaction_byte_sha256':sha(store.path/'transactions/0000000002.json'),'transaction_original_base64':base64.b64encode((store.path/'transactions/0000000002.json').read_bytes()).decode(),'private_keys_exported':False,'private_memory_exported':False,'repository_admissions_applied':0,'task_complete':False,'goal_complete':False,'claim_ceiling':'Actual owned ten-member scoped correction with original bytes and exact retained source/authority contracts; public API and full package/semantic/privacy/review integration remain pending.'}
    need(not owned.exists(),'owned store and signer removed');report['owned_root']={'path':str(owned),'removed':True};guard()
    p=HERE/'receipts/0001/journey.json';p.parent.mkdir(parents=True,exist_ok=True);p.open('x').write(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps({'result':'PASS','checks':len(checks),'applied_corrections':10,'receipt':str(p.relative_to(ROOT)),'sha256':sha(p)}),flush=True)
if __name__=='__main__':main()
