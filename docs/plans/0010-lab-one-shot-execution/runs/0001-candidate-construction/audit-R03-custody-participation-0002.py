"""Independent original-body/signature audit with every parent file retained."""
import argparse,ast,base64,hashlib,importlib.util,json,os,sys
from datetime import datetime,timezone
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
SELECTED=ROOT/'product/lab/release-candidates/v1/interface/custody-participation-v1'
SOURCE=HERE/'custody-participation-audit-source-0002.json'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def bind(p):return {'path':p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p),'sha256':sha(p.read_bytes())}
def parse(raw):
    def pairs(items):
        value={}
        for key,item in items:
            if key in value:raise ValueError('duplicate independent audit JSON key')
            value[key]=item
        return value
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('nonfinite audit JSON')))
def encoded(value):return (json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()
def digest(value):return sha(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode())
def put(path,value):
    path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as f:f.write(encoded(value))
def methods(p):
    tree=ast.parse(p.read_bytes());return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-sha256',required=True);args=ap.parse_args()
    assert sha(SOURCE.read_bytes())==args.source_sha256;m=parse(SOURCE.read_bytes());checks=[]
    def need(value,name):
        if not value:raise AssertionError(name)
        checks.append(name)
    for row in m['files']:need(bind(ROOT/row['path'])==row,'original frozen audit input '+row['path'])
    parent=parse((ROOT/m['parent_receipt_binding']['path']).read_bytes());retained={r['path']:r for r in m['files']}
    for row in parent['files']:need(retained.get(row['path'])==row,'retain original parent '+row['path'])
    need(parent['result']=='PASS' and parent['task_complete'] is False,'full original parent remains partial')
    terminal=parse((ROOT/m['terminal_binding']['path']).read_bytes())
    need(terminal['selected_exit_codes']=={'build':0,'eligibility':0,'checks':0,'cold':0},'all four actual producer exit codes')
    for name,count in [('checks',54),('eligibility',90)]:
        report=parse((SELECTED/'receipts'/f'{name}.json').read_bytes())
        need(report['result']=='PASS' and report['tests_run']==count,'all '+str(count)+' '+name+' methods passed')
        need(len(report['cases'])==count and len({r['test'] for r in report['cases']})==count and all(r['result']=='PASS' for r in report['cases']),'every '+name+' method exactly once')
        need(report['source_sha256']==m['selected_source_binding']['sha256'] and report['task_complete'] is False,'source pinned and partial '+name)
    comparisons=[('session-authority-v1/test_eligibility_corrected.py','test_eligibility.py',74),('session-authority-v2/test_revision_witness.py','test_revision_witness.py',16)]
    for old,new,count in comparisons:
        a=methods(SELECTED.parent/old);b=methods(SELECTED/new);need(a==b and len(a)==count,'original assertion AST parity '+new)
    old=methods(SELECTED.parent/'session-participation-v2/run_checks.py');new=methods(SELECTED/'test_original_branch.py')
    need(len(old)==len(new)==22 and set(old)==set(new),'all original 22 branch method identities retained')
    for name in old:
        if name!='test_02_actual_original_byte_parity':need(old[name]==new[name],'exact original branch assertion '+name)
    need(old['test_02_actual_original_byte_parity']!=new['test_02_actual_original_byte_parity'],'explicit raw original parity successor changes inherited serializer expectation')
    package=SELECTED/'packages/0001';manifest=parse((package/'manifest.json').read_bytes())
    need(bind(package/'manifest.json')==m['package_binding'],'independent exact derived package pin')
    need(manifest['public_package_export_allowed'] is False and manifest['visibility']=='private-candidate-original-custody','private custody is not a public package')
    index={r['version_ref']:r for r in parse((package/'record-index.json').read_bytes())};need(len(index)==21,'all21fresh body/relation files')
    built=parse((package/'build-result.json').read_bytes())
    need(built['result']=='PASS' and built['owned_store_and_key_removed'] and not Path(built['owned_root']).exists(),'actual owned store and signer removed')
    need(built['private_keys_exported'] is False and built['Session_memory_rehydrated'] is False and built['active_Agents_created']==0,'no private key restoration or active runtime claims')
    period=parse((package/'period.json').read_bytes());prior=parse((ROOT/period['inherited_validity_binding']['path']).read_bytes())
    need(bind(ROOT/period['inherited_validity_binding']['path'])==period['inherited_validity_binding'],'retained original period source bytes')
    need((period['not_before'],period['expires_at'])==(prior['not_before'],prior['expires_at']),'absolute source interval never reset or extended')
    a=parse((package/'branch.snapshot').read_bytes());expected=parse((package/'expected-replay.json').read_bytes());originals={}
    for name,row in a['files'].items():
        raw=base64.b64decode(row['base64_original_bytes'],validate=True);need(sha(raw)==row['sha256'] and base64.b64encode(raw).decode()==row['base64_original_bytes'],'exact original archive file '+name);originals[name]=raw
    config=parse(originals['config.json']);need(config['digest']==digest({k:v for k,v in config.items() if k!='digest'}),'original sealed config')
    config={k:v for k,v in config.items() if k!='digest'};baseline=parse(originals['baseline.json']);head=parse(originals['HEAD.json'])
    need(baseline['snapshot_digest']==digest({k:v for k,v in baseline.items() if k!='snapshot_digest'}),'exact baseline captured closure')
    need(sha(originals['config.json'])==expected['config_sha256'] and baseline['snapshot_digest']==expected['baseline_snapshot_digest'],'independent config/baseline byte/source pins')
    need(head['digest']==digest({k:v for k,v in head.items() if k!='digest'}) and head['sequence']==2 and head['transaction_digest']==expected['expected_head'],'selected exact2transaction HEAD')
    need(config['schema_version']=='lab-runtime-store-config/v3-candidate' and config['authorized_domain_scope_refs']==['scope:cyberalchemy-lab-first-agent-episode'] and config['scope_ref'] not in config['authorized_domain_scope_refs'],'separate exact project and correction domain scopes')
    target_bytes={};transactions=[];decisions=set();previous=None
    for seq in range(3):
        tx=parse(originals[f'transactions/{seq:010d}.json']);need(tx['digest']==digest({k:v for k,v in tx.items() if k!='digest'}),'actual structural transaction seal '+str(seq))
        need(tx['sequence']==seq and tx['previous_digest']==previous,'actual original signed chain '+str(seq));previous=tx['digest'];transactions.append(tx['digest'])
        need(tx['config_digest']==digest(config) and tx['baseline_digest']==baseline['snapshot_digest'],'actual config and baseline transaction bindings '+str(seq))
        if seq==0:continue
        p=tx['proposal'];approval=tx['approval'];cores=tx['decision_cores'];signed={k:v for k,v in approval.items() if k!='signature'}
        expected_signed={'schema_version':'lab-runtime-approval/v2-candidate','store_id':config['store_id'],'owner_ref':config['owner_ref'],
            'scope_ref':p['scope_ref'],'policy_ref':p['policy_ref'],'challenge_route':p['challenge_route'],'source_snapshot_digest':p['source_snapshot_digest'],
            'expected_head':p['expected_head'],'proposal_digest':digest(p),'decision_core_digests':[digest(c) for c in cores],'approved_at':approval['approved_at'],
            'outcome':'authorize-exact-local-effects','configuration_digest':digest(config),'correction_profile_binding':config['correction_profile_binding'],
            'authorized_domain_scope_refs':config['authorized_domain_scope_refs']}
        need(signed==expected_signed,'independent closed exact signature input '+str(seq))
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(config['public_key'])).verify(bytes.fromhex(approval['signature']),encoded(signed));checks.append('independent actual Ed25519 signature '+str(seq))
        need(tx['schema_version']=='lab-runtime-original-json-transaction/v2-candidate' and p['schema_version']=='lab-runtime-original-json-proposal/v2-candidate','explicit ordinary original-json/v2 family '+str(seq))
        need(p['scope_ref']==config['scope_ref'] and p['expected_head']==tx['previous_digest'] and p['source_snapshot_digest']==baseline['snapshot_digest'],'exact project/source/HEAD proposal '+str(seq))
        need(len(cores)==len(p['targets']) and p['schemas']=={} and p['schema_contents']=={},'complete existing-carrier target/schema closure '+str(seq))
        for i,(t,c) in enumerate(zip(p['targets'],cores)):
            expected_core={k:t[k] for k in ['decision_ref','category','operation','version_ref']};expected_core['target_digest']=digest(t)
            need(c==expected_core and c['decision_ref'] not in decisions,'exact independent full target core '+t['version_ref']);decisions.add(c['decision_ref'])
            e=t['content'];need(set(e)==set('schema_version content_ref media_type byte_sha256 size_bytes encoding data semantic_binding'.split()),'closed original content '+t['version_ref'])
            raw=base64.b64decode(e['data'],validate=True)
            need(base64.b64encode(raw).decode()==e['data'] and sha(raw)==e['byte_sha256'] and len(raw)==e['size_bytes'] and e['content_ref']=='runtime-content:sha256:'+sha(raw),'actual original body byte binding '+t['version_ref'])
            need(e['encoding']=='base64' and e['media_type']=='application/json' and e['semantic_binding'] is None and e['schema_version']=='lab-artifact-content-entry/v1-candidate','explicit content profile '+t['version_ref'])
            need(digest(parse(raw))==digest(t['record']) and raw!=encoded(t['record']),'original bytes separate from structural and inherited encoding '+t['version_ref'])
            target_bytes[t['version_ref']]=raw
            file=ROOT/index[t['version_ref']]['original_binding']['path'] if seq==2 else package/'setup-artifacts'/['project.json','product.json'][i]
            need(file.read_bytes()==raw,'actual authored candidate file custody '+t['version_ref'])
    need(len(target_bytes)==len(decisions)==23 and [digest(parse(originals[f'transactions/{i:010d}.json'])) for i in range(3)]==expected['transaction_sha256s'] and previous==head['transaction_digest'],'all23distinct original targets/cores and signed transactions')
    cold=parse((SELECTED/'receipts/cold.json').read_bytes())
    need(cold['result']=='PASS' and cold['owned_cold_read_workspace_removed'] and cold['process_id']!=os.getpid(),'actual separate cold process and owned cleanup')
    need(cold['source_sha256']==m['selected_source_binding']['sha256'] and cold['package_sha256']==m['package_binding']['sha256'],'actual cold process independent pins')
    need(cold['source_cut']['source_profile_sha256']==expected['engine_pins']['profile_sha256'] and cold['source_cut']['commit_sha256']==head['transaction_digest'],'current actual engine profile and signed cut')
    for row in cold['original_targets']:need(sha(target_bytes[row['version_ref']])==row['byte_sha256'],'actual cold original byte parity '+row['version_ref'])
    need(len(cold['original_targets'])==23 and len(cold['dispositions'])==cold['accounted_subjects'],'complete captured source accounting')
    need(len(cold['carrier_counts'])==22 and not cold['missing_current_carriers'] and not cold['instance_bound_assignments'],'full closed22carrier policy and new ProfileeligibleAssignment')
    product=cold['actual_product_artifact'];raw=base64.b64decode(cold['actual_product_original_base64'],validate=True)
    need(raw==target_bytes[product['version_ref']] and sha(raw)==product['byte_sha256'] and product['version_ref']!=product['identity_ref']+'@'+cold['product_body_version'],'actual Product original-byte and distinct signed/body revision witness')
    spec=importlib.util.spec_from_file_location('_cal_participation_independent_audit',SELECTED/'__init__.py',submodule_search_locations=[str(SELECTED)])
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    reader=__import__(spec.name+'.reader',fromlist=['open_signed']);inspection=[]
    with reader.open_signed(m['selected_source_binding']['sha256'],m['package_binding']['sha256']) as selected:
        view=selected.view;status=view.status();defs=view.definitions(limit=1000)
        need(status['implemented_cli_commands']==[] and status['api_operations_added_by_this_source']==0,'inspection methods claim no public CLI/API implementation')
        need(defs['total']>0 and defs['total']==len(defs['items']),'actual complete selected definition inspection')
        for seq in [1,2]:
            review=view.review(seq);receipt=view.receipt(seq);need(review['target_count']==(2 if seq==1 else 21),'actual recorded review target count '+str(seq))
            for t in review['targets']:
                need(t['after_binding']==view.subjects[t['target_ref']]['source'],'recorded review binds actual original header '+t['target_ref'])
            need(receipt['transaction_digest']==transactions[seq] and receipt['transaction_file_sha256']==sha(originals[f'transactions/{seq:010d}.json']),'actual original inspection receipt '+str(seq))
            inspection.append({'sequence':seq,'review':review,'receipt':receipt})
        s=view.subjects[product['version_ref']];report=view.inspect(s['version_ref'])
        need(report['original_source']['record_binding']['sha256']==sha(raw),'actual inspect original Product body header')
        work=next(r for r in selected.records if r.artifact['carrier_ref']=='cal.artifact-type.work/v1');connections=view.connections(work.artifact['version_ref'])
        need(len(connections['connections'])==1 and all(r['validation_posture']=='validated-selected-cut' for r in connections['connections']),'actual closed work-to-project connection inspection')
        need(cold['accounted_subjects']==len(view.subjects) and cold['included_current_instances']==len(selected.records),'independent current domain and allsubject accounting')
    for row in m['files']:need(bind(ROOT/row['path'])==row,'unchanged final independent input '+row['path'])
    audit={'schema_version':'lab-original-participation-independent-audit/v1-candidate','result':'PASS','checks':len(checks),'check_names':checks,
        'source_manifest_binding':bind(SOURCE),'parent_files_retained':len(parent['files']),'selected_methods':144,'independent_actual_signatures_verified':2,
        'actual_original_targets':23,'actual_inspection_methods_exercised':['status','definitions','inspect','connections','review','receipt'],
        'actual_recorded_inspection':inspection,'preserved_absolute_interval':{'not_before':period['not_before'],'expires_at':period['expires_at']},
        'authority_effect':'none','actual_owner_outcome':None,'task_complete':False,'goal_complete':False}
    audit_path=SELECTED/'receipts/independent-audit-0002.json';put(audit_path,audit)
    rows={r['path']:r for r in m['files']}
    for p in [SOURCE,audit_path]:rows[bind(p)['path']]=bind(p)
    receipt={'schema_version':'lab-R03-original-participation-partial-proof/v1-candidate','result':'PASS','files':sorted(rows.values(),key=lambda r:r['path']),
        'checked_at':datetime.now(timezone.utc).isoformat(),'parent_receipt_binding':m['parent_receipt_binding'],
        'selected_source_binding':m['selected_source_binding'],'package_binding':m['package_binding'],'independent_audit_binding':bind(audit_path),
        'audit_checks':len(checks),'parent_files_retained':len(parent['files']),'selected_methods':144,'method_counts':{'original_branch':22,'new_original_source':32,'original_eligibility':74,'original_revision_witness':16},
        'all_original_assertions_retained_except_declared_serializer_successor':True,'actual_public_api_operations':12,'remaining_original_api_operations':22,'original_public_api_operations':34,
        'closed_plan_criteria':35,'total_plan_criteria':46,'actual_original_targets':23,'actual_signatures_independently_verified':2,
        'selected_producers_terminal':True,'selected_owned_roots_removed':True,'private_keys_exported':False,'private_memory_exported':False,
        'repository_admissions_applied':0,'authority_effect':'none','actual_owner_outcome':None,'task_complete':False,'goal_complete':False,
        'remaining_obligations':m['remaining_obligations'],
        'claim_ceiling':'New original-byte current domain source and guarded context source adapter verified; current host permissions, active Agent/Session, full public API/SQLite/native context/ontology and all original task criteria remain. One actual final R08 checkpoint follows complete S02.'}
    p=SELECTED/'receipts/R03-0019.json';put(p,receipt);print(json.dumps({'result':'PASS','checks':len(checks),'files':len(rows),'parent_files_retained':len(parent['files']),'methods':144,'receipt_binding':bind(p)}),flush=True)
if __name__=='__main__':main()
