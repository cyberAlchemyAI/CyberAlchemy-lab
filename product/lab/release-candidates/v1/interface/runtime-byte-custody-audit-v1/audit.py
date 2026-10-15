"""Independent public signature/byte audit and preserved parent proof closure."""
import argparse,ast,base64,hashlib,json
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
def raw_sha(raw):return hashlib.sha256(raw).hexdigest()
def sha(p):return raw_sha(p.read_bytes())
def parse(raw):
    def pairs(items):
        result={}
        for key,value in items:
            if key in result:raise ValueError('duplicate audit JSON key')
            result[key]=value
        return result
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('nonfinite audit JSON')))
def digest(v):return raw_sha(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode())
def encoded(v):return (json.dumps(v,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-sha256',required=True);args=ap.parse_args()
    assert sha(HERE/'source-manifest.json')==args.source_sha256,'audit source pin differs'
    m=parse((HERE/'source-manifest.json').read_bytes());checks=[]
    def need(condition,name):
        if not condition:raise AssertionError(name)
        checks.append(name)
    for row in m['files']:need(sha(ROOT/row['path'])==row['sha256'],'exact file '+row['path'])
    parent=parse((ROOT/m['parent_receipt_binding']['path']).read_bytes())
    selected={r['path']:r['sha256'] for r in m['files']}
    for row in parent['files']:need(selected.get(row['path'])==row['sha256'],'parent closure '+row['path'])
    suite=parse((ROOT/m['suite_result_binding']['path']).read_bytes());journey=parse((ROOT/m['journey_result_binding']['path']).read_bytes())
    need(suite['result']=='PASS' and suite['all_children_terminal'] and suite['sources_unchanged'],'terminal complete selected suite')
    expected=[];runtime=ROOT/m['runtime_root']
    for module,cls in [('test_runtime','RuntimeTests'),('test_custody','CustodyTests')]:
        tree=ast.parse((runtime/'tests'/f'{module}.py').read_text());definition=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==cls)
        expected += [f'{module}.{cls}.{n.name}' for n in definition.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')]
    need(sorted(expected)==sorted(c['test'] for c in suite['cases']),'every original and new method exactly once')
    need(suite['original_runtime_methods']==38 and suite['custody_methods']==28 and suite['test_methods']==66,'complete 38 plus 28 original method count')
    for case in suite['cases']:
        need(case['result']=='PASS' and case['exit_code']==0,'actual terminal '+case['test'])
        report=parse((ROOT/case['report_binding']['path']).read_bytes())
        need(report['result']=='PASS' and report['tests_run']==1 and report['checks']==[{'test':case['test'],'result':'PASS'}],'exact case '+case['test'])
        need(report['sources_unchanged'] and all(row['removed'] and not Path(row['path']).exists() for row in report['owned_roots']),'owned cleanup '+case['test'])
    need(journey['result']=='PASS' and journey['owned_root']['removed'] and not Path(journey['owned_root']['path']).exists(),'actual direct journey terminal cleanup')
    raw=base64.b64decode(journey['original_content_base64'],validate=True);p=journey['proposal'];target=p['targets'][0];content=target['content']
    need(raw_sha(raw)==journey['original_byte_sha256']==content['byte_sha256'],'reviewed original byte identity')
    need(len(raw)==content['size_bytes'] and base64.b64decode(content['data'],validate=True)==raw,'original entry length and actual bytes')
    need(digest(parse(raw))==digest(target['record'])==journey['structural_record_digest'],'original parsed structural equivalence')
    need(raw!=encoded(target['record']) and raw_sha(encoded(target['record']))==journey['inherited_encoded_byte_sha256'],'different original and inherited byte identities')
    cores=[{'decision_ref':t['decision_ref'],'category':t['category'],'operation':t['operation'],'version_ref':t['version_ref'],'target_digest':digest(t)} for t in p['targets']]
    need(cores==journey['review']['decision_cores'],'exact original-inclusive Decision core')
    approval=journey['fixture_approval'];config=journey['fixture_configuration'];signed={k:v for k,v in approval.items() if k!='signature'}
    need(config['public_key']==journey['fixture_public_key'],'independent retained fixture public key')
    expected_approval={'schema_version':'lab-runtime-approval/v1','store_id':config['store_id'],'owner_ref':config['owner_ref'],'scope_ref':p['scope_ref'],'policy_ref':p['policy_ref'],
        'challenge_route':p['challenge_route'],'source_snapshot_digest':p['source_snapshot_digest'],'expected_head':p['expected_head'],'proposal_digest':digest(p),
        'decision_core_digests':[digest(c) for c in cores],'approved_at':approval['approved_at'],'outcome':'authorize-exact-local-effects'}
    need(signed==expected_approval,'closed exact fixture signature inputs')
    Ed25519PublicKey.from_public_bytes(bytes.fromhex(journey['fixture_public_key'])).verify(bytes.fromhex(approval['signature']),encoded(signed));checks.append('independent Ed25519 exact original-inclusive signature verification')
    txraw=base64.b64decode(journey['original_signed_transaction_base64'],validate=True);tx=parse(txraw)
    need(raw_sha(txraw)==journey['original_signed_transaction_byte_sha256'],'enclosing original transaction byte identity')
    need(digest({k:v for k,v in tx.items() if k!='digest'})==tx['digest'],'actual structural transaction seal')
    need(tx['proposal']==p and tx['approval']==approval and tx['decision_cores']==cores,'committed review signature and original bytes')
    need(tx['schema_version']=='lab-runtime-original-json-transaction/v1-candidate' and p['schema_version']=='lab-runtime-original-json-proposal/v1-candidate','distinct custody protocol identities')
    need(tx['config_digest']==digest(config) and tx['baseline_digest']==config['source_snapshot_digest'],'transaction source configuration bindings')
    need(tx['previous_digest']==journey['input_head']['transaction_digest']==p['expected_head'] and tx['sequence']==1,'original predecessor and exact sequence')
    need(tx['digest']==journey['output_head']['transaction_digest']==journey['application_result']['transaction_digest']==journey['exact_retry_result']['transaction_digest'],'single canonical cut and exact retry')
    need(journey['exact_retry_result']['idempotent'] and bool(journey['changed_original_rejection']),'historical retry and changed original rejection')
    need(journey['source_binding']['sha256']==raw_sha(raw) and journey['source_binding']['encoding']=='base64-original-json/v1-candidate','source header retains original digest')
    need(journey['cold_read_exit_code']==0 and base64.b64decode(journey['cold_original_base64'],validate=True)==raw,'actual cold exact original retrieval')
    need(journey['cache_deleted_before_cold_read'] and journey['cache_report']['source_head']==tx['digest'] and journey['cache_report']['row_count']==1,'disposable cache and independent canonical read')
    need(journey['actual_owner_outcome'] is None and suite['actual_owner_outcome'] is None and journey['repository_admissions_applied']==0,'fixture outcome is not actual owner admission')
    for report in [suite,journey]:need(report['private_keys_exported'] is False and report['private_memory_exported'] is False,'no private key or memory export')
    result={'schema_version':'lab-original-byte-custody-independent-audit/v1-candidate','result':'PASS','authority_effect':'none','actual_owner_outcome':None,
        'source_manifest_binding':bind(HERE/'source-manifest.json'),'checks':len(checks),'check_names':checks,'all_parent_files_retained':len(parent['files']),
        'suite_result_binding':m['suite_result_binding'],'journey_result_binding':m['journey_result_binding'],
        'independent_public_signature_verified':True,'original_runtime_methods':38,'custody_methods':28,'selected_methods':66,
        'original_sha256':raw_sha(raw),'encoded_sha256':raw_sha(encoded(target['record'])),'structural_record_digest':digest(target['record']),
        'task_complete':False,'goal_complete':False,'claim_ceiling':'Independent byte/signature/source evidence for the scoped storage primitive and full original method coverage; no independent reconstruction of missing baseline original files, full API integration, actual admission or whole task completion.'}
    path=HERE/'receipts/0001/result.json';path.parent.mkdir(parents=True,exist_ok=True);path.open('x').write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'result':'PASS','checks':len(checks),'retained_parent_files':len(parent['files']),'result_binding':bind(path)}),flush=True)
if __name__=='__main__':main()
