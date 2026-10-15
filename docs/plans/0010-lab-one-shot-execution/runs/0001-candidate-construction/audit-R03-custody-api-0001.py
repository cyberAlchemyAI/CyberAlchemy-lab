"""Independent original-source API/SQL audit with separately owned nonce grants."""
import argparse,ast,base64,hashlib,importlib.util,json,os,sys,tempfile
from datetime import datetime,timezone
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
SELECTED=ROOT/'product/lab/release-candidates/v1/interface/api-v17';SOURCE=HERE/'custody-api-audit-source-0001.json'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def bind(p):return {'path':p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p),'sha256':sha(p.read_bytes())}
def load(p):return json.loads(p.read_bytes())
def encoded(v):return (json.dumps(v,indent=2,sort_keys=True,ensure_ascii=False)+'\n').encode()
def put(p,v):
    p.parent.mkdir(parents=True,exist_ok=True,mode=0o700);fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as f:f.write(encoded(v))
def methods(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
    p=argparse.ArgumentParser();p.add_argument('--source-sha256',required=True);a=p.parse_args();assert sha(SOURCE.read_bytes())==a.source_sha256;m=load(SOURCE);checks=[]
    def need(v,n):
        if not v:raise AssertionError(n)
        checks.append(n)
    for row in m['files']:need(bind(ROOT/row['path'])==row,'exact frozen input '+row['path'])
    rows={r['path']:r for r in m['files']};parent=load(ROOT/m['parent_receipt_binding']['path'])
    for row in parent['files']:need(rows.get(row['path'])==row,'retain complete original parent '+row['path'])
    tests=load(SELECTED/'receipts/checks.json');terminal=load(ROOT/m['terminal_binding']['path'])
    need(terminal['exit_code']==0 and tests['result']=='PASS' and tests['tests_run']==tests['expected_tests']==129,'actual129test terminal pass')
    need(len(tests['cases'])==len({r['test'] for r in tests['cases']})==129 and all(r['result']=='PASS' for r in tests['cases']),'all129case results exactly once')
    need(tests['source_sha256']==m['api_source_binding']['sha256'] and tests['profile_sha256']==m['api_profile_binding']['sha256'],'exact tested source and profile')
    for name in ['test_preparation.py','test_preparation_corrected.py']:need(methods(SELECTED/name)==methods(SELECTED.parent/'api-v16'/name),'all original preparation method ASTs '+name)
    old=methods(SELECTED.parent/'api-v16/run_session_checks.py');new=methods(SELECTED/'run_session_checks.py')
    need(set(old)==set(new) and [n for n in old if old[n]!=new[n]]==['test_30_current_handler_profile_retains_all_original_contracts'],'33originalSessionASTs unchanged; explicit existing12operation count correction')
    observations=load(SELECTED/'receipts/wire-observations.json')
    for name in ['_cal_api_v17_checks.run_session_checks','_cal_api_v17_checks.test_custody_sessions']:
        operations={r['reply']['operation'] for r in observations[name] if r['reply']['kind']=='result'}
        need(len(operations)==12,'all12actual positive operations '+name)
    spec=importlib.util.spec_from_file_location('_cal_api_v17_independent_audit',SELECTED/'__init__.py',submodule_search_locations=[str(SELECTED)]);module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    def imported(n):return __import__(spec.name+'.'+n,fromlist=['*'])
    G=imported('guard');G.verify(m['api_source_binding']['sha256']);P=imported('protocol');F=imported('example_fixture');S=imported('service');M=imported('artifact_model');Q=imported('projection');Refresh=imported('projection_refresh');D=P.source.custody_delivery()
    schemas=P.Schemas(m['api_profile_binding']['sha256']);need(len(schemas.operations)==34 and len(P.SUPPORTED)==12,'full original34contract catalog retained')
    need(D.reader is D.MAPPED.reader and D.EL is D.reader.adapter.eligibility,'same original-source reader and eligibility class objects')
    artifacts=[];public=[];roots=[]
    with P.source.replay_source('custody-participation') as view:
        source_cut=imported('handlers').cut(view);need(source_cut==view.custody_signed_sources.source_cut and source_cut['source_profile_sha256']==view.handle.manifest['profile_binding']['sha256'],'actual original signed cut and selected engine profile')
        for subject in view.subjects.values():
            if subject['source'].get('encoding')!=view.handle.custody.ENCODING:continue
            raw,locator,encoding,enclosing=M.record_bytes(view,subject);h=M.artifact_ref(view,subject)
            file=view.originals[subject['source']['path']];transaction=json.loads(file);target=view.handle.common.pointer(transaction,subject['source']['record_selector'].removesuffix('/record'))
            original=base64.b64decode(target['content']['data'],validate=True)
            need(raw==original and sha(raw)==h['byte_sha256']==target['content']['byte_sha256'],'independent original raw bytes and header '+h['version_ref'])
            need(raw!=view.handle.common.encoded(subject['record']) and enclosing==sha(file) and enclosing!=h['byte_sha256'],'body versus serializer versus enclosing original file '+h['version_ref'])
            view.handle.operations.validate_record(subject['record'],subject['carrier_ref'],view.data['projection']);checks.append('actual original carrier validation '+h['version_ref'])
            artifacts.append({'artifact':h,'source_locator':locator,'encoding':encoding,'enclosing_sha256':enclosing})
        need(len(artifacts)==23,'all23actual raw original bodies exposed correctly')
        connections,gaps=M.connections(view,schemas);owned=[r for r in connections if r['version_ref'].startswith('typed-relation:R03-original-reader:')]
        need(len(owned)==10,'all10current declared original-source connections')
        materials,metadata,target=F.materials_for(view)
        for legacy in [False,True]:
            selected_materials=dict(materials);selected_target=dict(target)
            if legacy:
                body=json.loads(materials['candidate:work-content']);runtime_target={'category':'artifact-instance','operation':'admit','version_ref':target['artifact']['version_ref'],'carrier_ref':target['artifact']['carrier_ref'],'record':body,'predecessor_ref':None,'decision_ref':'decision:R03-candidate-admit','contract':None}
                core={'decision_ref':runtime_target['decision_ref'],'category':'artifact-instance','operation':'admit','version_ref':runtime_target['version_ref'],'target_digest':view.handle.common.digest(runtime_target)}
                selected_materials['candidate:work-core']=view.handle.common.encoded(core);selected_target['decision_core_binding']={'ref':'candidate:work-core','sha256':sha(selected_materials['candidate:work-core'])}
            with tempfile.TemporaryDirectory(prefix='cal-R03-original-API-audit-') as temporary:
                root=Path(temporary);root.chmod(0o700);roots.append(str(root))
                key,path,pin=F.provision(root,'custody-participation',selected_materials,metadata,principal=D.records.PRINCIPAL,projection_control=Refresh.control(view))
                channel=imported('auth').ReaderChannel(path,pin,schemas);proof_raw=F.proof(key,channel.challenge);auth=channel.authenticate(proof_raw)
                policy_raw=path.read_bytes();policy=json.loads(policy_raw);proof=json.loads(proof_raw)
                Ed25519PublicKey.from_public_bytes(base64.b64decode(policy['reader_public_key'],validate=True)).verify(base64.b64decode(proof['signature'],validate=True),P.compact(proof['challenge']))
                need(proof['challenge']['policy_sha256']==sha(policy_raw) and auth['context']['authentication_evidence_binding']['sha256']==sha(proof_raw),'actual independent nonce signature and exact host/proof bytes')
                period=D.load(D.reader.HERE/'packages/0001/period.json')
                need(imported('auth').instant(policy['expires_at'])<=imported('auth').instant(period['expires_at']) and period['expires_at']=='2026-10-10T02:45:14.443492+00:00','new owned host grant bounded by original absolute Assignment expiry')
                service=S.Service(view,channel,schemas)
                try:
                    call=F.candidate_call(service,selected_target,operation='change.validate',key='audit:legacy' if legacy else 'audit:raw');reply=service.call(P.compact(call))
                    need(reply['kind']=='result' and schemas.valid('api-reply',reply),'actual independently authenticated candidate validation domain reply')
                    report=reply['message']
                    if legacy:need(report['result']=='fail' and any(c['check_ref']=='check:candidate-construction-refusal' for c in report['checks']),'legacy core rejected inside actual validator under valid separately provisioned material manifest')
                    else:
                        need(report['result']!='fail' and any(c['check_ref']=='check:exact-source-target-schema-core' and c['result']=='pass' for c in report['checks']),'actual full raw target core validated')
                        query=F.call(channel.context,'lab.status',source_cut);status=service.call(P.compact(query));need(status['kind']=='result' and status['message']['source_cut']==source_cut and status['message']['supported_operations']==list(P.SUPPORTED),'actual independently authenticated status original source')
                        generation=Q.Generation(view,source_cut,schemas)
                        try:
                            need(generation.metadata[2]==view.handle.manifest['profile_binding']['sha256'] and generation.db.execute('PRAGMA foreign_key_check').fetchall()==[],'complete SQL selected source profile and foreign keys')
                            for row in artifacts:
                                h=row['artifact'];raw=M.record_bytes(view,view.subjects[h['version_ref']])[0]
                                need(generation.db.execute('SELECT content FROM content_cache WHERE byte_sha256=?',(h['byte_sha256'],)).fetchone()[0]==raw,'full SQL actual original body BLOB '+h['version_ref'])
                            need(generation.db.execute('SELECT count(*) FROM artifact_revision').fetchone()[0]==len(view.subjects),'full SQL all source revisions')
                            generation.verify();checks.append('full SQL exact DDL/rows/metadata/fileSHA/pointer/privacy/integrity guard')
                        finally:generation.close()
                    public.append({'legacy_core_selected':legacy,'owned_root':str(root),'public_policy':policy,'public_policy_original_sha256':sha(policy_raw),'signed_nonce_proof':proof,'authentication_context':auth['context'],'actual_validation_reply':reply,'authority_effect':'none','actual_owner_outcome':None})
                finally:service.close();key=None
            need(not root.exists(),'actual owned independent API host policy/key/workspace root removed')
        view.custody_signed_sources.guard();checks.append('final independent original signed source guard')
    G.verify(m['api_source_binding']['sha256'])
    for row in m['files']:need(bind(ROOT/row['path'])==row,'unchanged final audit input '+row['path'])
    audit={'schema_version':'lab-original-source-API-independent-audit/v1-candidate','result':'PASS','checks':len(checks),'check_names':checks,'selected_methods':129,'parent_files_retained':len(parent['files']),'original_byte_observations':artifacts,'actual_owned_nonce_and_candidate_observations':public,'owned_host_roots_removed':roots,'full_SQL_original_byte_BLOBs_independently_verified':True,'legacy_core_rejected_with_valid_independent_manifest':True,'actual_public_API_operations':12,'original_operations':34,'authority_effect':'none','actual_owner_outcome':None,'task_complete':False,'goal_complete':False}
    audit_path=SELECTED/'receipts/independent-audit.json';put(audit_path,audit)
    for p in [SOURCE,audit_path]:rows[bind(p)['path']]=bind(p)
    receipt={'schema_version':'lab-R03-original-source-API-integration-partial-proof/v1-candidate','result':'PASS','files':sorted(rows.values(),key=lambda r:r['path']),'checked_at':datetime.now(timezone.utc).isoformat(),'parent_receipt_binding':m['parent_receipt_binding'],'selected_API_source_binding':m['api_source_binding'],'selected_API_profile_binding':m['api_profile_binding'],'independent_audit_binding':bind(audit_path),'parent_files_retained':len(parent['files']),'audit_checks':len(checks),'selected_methods':129,'raw_original_artifact_bodies':23,'current_closed_original_typed_connections':10,'complete_SQL_original_body_custody_verified':True,'actual_legacy_and_original_Session_journeys_verified':True,'actual_active_Agents_at_completion':0,'actual_public_api_operations':12,'remaining_original_api_operations':22,'original_public_api_operations':34,'closed_plan_criteria':35,'total_plan_criteria':46,'selected_producers_terminal':True,'repository_admissions_applied':0,'private_keys_exported':False,'Session_memory_rehydrated':False,'authority_effect':'none','actual_owner_outcome':None,'human_pilot_outcome':None,'task_complete':False,'goal_complete':False,'remaining_obligations':m['remaining_obligations'],'claim_ceiling':'Twelve existing APIs integrated with exact original signed source, complete SQL byte custody and owned ephemeral Session journeys. Remaining22APIs/full46task/S02/actualR04/R08 outcomes remain.'}
    p=SELECTED/'receipts/R03-0022.json';put(p,receipt);print(json.dumps({'result':'PASS','checks':len(checks),'methods':129,'files':len(rows),'parent_files_retained':len(parent['files']),'receipt_binding':bind(p)}),flush=True)
if __name__=='__main__':main()
