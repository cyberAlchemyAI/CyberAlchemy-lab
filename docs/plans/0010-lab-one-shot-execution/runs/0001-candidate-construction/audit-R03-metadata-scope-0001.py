"""Independent original-source API/SQL audit with separately owned nonce grants."""
import argparse,ast,base64,hashlib,importlib.util,json,os,sys,tempfile
from datetime import datetime,timezone
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
SELECTED=ROOT/'product/lab/release-candidates/v1/interface/api-v23';SOURCE=HERE/'metadata-scope-audit-source-0001.json'
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
    predecessor=SELECTED.parent/'api-v22'
    for name in ['test_preparation.py','test_preparation_corrected.py','run_session_checks.py','test_custody_sessions.py','test_custody_api.py']:
        need(methods(SELECTED/name)==methods(predecessor/name),'all129 original method ASTs unchanged '+name)
    need(len(methods(SELECTED/'test_guarded_reads.py'))==17,'seventeen additional guard methods retained')
    spec=importlib.util.spec_from_file_location('_cal_api_v23_independent_audit',SELECTED/'__init__.py',submodule_search_locations=[str(SELECTED)]);module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    def imported(n):return __import__(spec.name+'.'+n,fromlist=['*'])
    G=imported('guard');G.verify(m['api_source_binding']['sha256']);P=imported('protocol');F=imported('metadata_fixture');S=imported('service');M=imported('artifact_model');Q=imported('projection');Refresh=imported('projection_refresh');GR=imported('guarded_reads');D=P.source.custody_delivery()
    schemas=P.Schemas(m['api_profile_binding']['sha256']);need(len(schemas.operations)==34 and len(P.SUPPORTED)==12,'full original34contract catalog retained')
    need(D.reader is D.MAPPED.reader and D.EL is D.reader.adapter.eligibility,'same original-source reader and eligibility class objects')
    artifacts=[];public=[];roots=[]
    with P.source.replay_source('custody-participation') as view:
        source_cut=imported('handlers').cut(view);need(source_cut==view.custody_signed_sources.source_cut and source_cut['source_profile_sha256']==view.handle.manifest['profile_binding']['sha256'],'actual original signed cut and selected engine profile')
        with GR.model_read_batch(view):
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
            declarations=[subject for subject in view.subjects.values() if subject['category']=='relation-kind']
            need(len(declarations)==41,'all41original catalog RelationKind declarations retained')
            for declaration in declarations:
                h=M.artifact_ref(view,declaration);raw,locator,encoding,enclosing=M.record_bytes(view,declaration)
                need(h['carrier_ref']=='cal.artifact-type.relation-kind/v2' and sha(raw)==h['byte_sha256']==declaration['source']['sha256'] and enclosing==h['byte_sha256'] and encoding=='original-file-bytes','exact explicit declaration metatype original body '+h['version_ref'])
            definitions=[s for s in view.subjects.values() if s['category']=='definition']
            need(len(definitions)==189,'all189original Definition declarations retained')
            for declaration in definitions:
                h=M.artifact_ref(view,declaration);raw,locator,encoding,enclosing=M.record_bytes(view,declaration);b=declaration['source']
                expected=view.handle.common.encoded(declaration['record']) if b.get('selector') else P.source.original({'path':b['path'],'sha256':b['sha256']})
                need(raw==expected and sha(raw)==h['byte_sha256'] and h['carrier_ref']==declaration['record']['classification']['artifact_type_ref'],'explicit Definition classification and original declared byte encoding '+h['version_ref'])
                need(enclosing==b['sha256'] and encoding==('inherited-canonical-json-of-selected-original-value' if b.get('selector') else 'original-file-bytes'),'Definition enclosing/selected-value distinction '+h['version_ref'])
            for declaration in [definitions[0],declarations[0]]:
                b=declaration['source'];saved=b.get('encoding');b['encoding']='unknown-catalog-encoding'
                try:
                    for operation in [M.artifact_ref,M.record_bytes]:
                        rejected=False
                        try:operation(view,declaration)
                        except Exception:rejected=True
                        need(rejected,'unknown catalog encoding refused '+operation.__name__+':'+declaration['version_ref'])
                finally:
                    if saved is None:b.pop('encoding',None)
                    else:b['encoding']=saved
            need(len(M.references(view))==len(view.subjects),'all original subjects remain indexed after catalog/instance distinction')
            connections,gaps=M.connections(view,schemas);owned=[r for r in connections if r['version_ref'].startswith('typed-relation:R03-original-reader:')]
            need(len(owned)==10,'all10current declared original-source connections')
        materials,metadata,targets=F.materials(view)
        need(len(targets)==42,'all42independent owner targets selected')
        original_period_path=D.reader.HERE/'packages/0001/period.json';original_period=original_period_path.read_bytes()
        with tempfile.TemporaryDirectory(prefix='cal-R03-metadata-independent-audit-') as temporary:
            root=Path(temporary);root.chmod(0o700);roots.append(str(root))
            key,path,policy_pin=F.provision(root,materials,metadata)
            channel=imported('auth').ReaderChannel(path,policy_pin,schemas);proof_raw=F.proof(key,channel.challenge);auth=channel.authenticate(proof_raw)
            policy_raw=path.read_bytes();policy=json.loads(policy_raw);proof=json.loads(proof_raw)
            Ed25519PublicKey.from_public_bytes(base64.b64decode(policy['reader_public_key'],validate=True)).verify(base64.b64decode(proof['signature'],validate=True),P.compact(proof['challenge']))
            need(proof['challenge']['policy_sha256']==sha(policy_raw) and auth['context']['authentication_evidence_binding']['sha256']==sha(proof_raw),'independent fresh metadata nonce signature binds exact policy/proof bytes')
            need(policy['schema_version']=='lab-local-metadata-candidate-policy/v1-candidate' and policy['purpose']=='durable-metadata-and-exact-candidate-preparation','explicit different metadata policy/purpose')
            need(policy['allowed_operations']==list(P.METADATA_SUPPORTED) and len(policy['allowed_operations'])==8 and policy['session_control'] is None,'eight metadata operations with no Session host')
            need(policy['principal_ref']!=D.records.PRINCIPAL and policy['principal_ref']!='principal:R03-fresh-reader','fresh metadata Principal does not impersonate historical reader')
            need(imported('auth').instant(policy['expires_at'])>imported('auth').now()>imported('auth').instant(json.loads(original_period)['expires_at']),'new metadata permission after original absolute Assignment expiry')
            service=S.Service(view,channel,schemas);observations=[]
            try:
                need(service.sessions is None and all(auth['context'][k] is None for k in ['agent_instance_ref','assignment_ref','session_ref']),'metadata produces no current Agent/Assignment/Session')
                prepare_call=F.candidate(service,targets,key='audit:all42-prepare');prepared=service.call(P.compact(prepare_call));need(prepared['kind']=='result' and schemas.valid('api-reply',prepared),'actual independent public42prepare reply')
                domain=prepared['message'];need(len(domain['stable_core_bindings'])==42 and domain['posture']=='blocked','all42real cores prepared with unresolved admission authority')
                need(domain['stable_core_bindings']==[t['decision_core_binding'] for t in targets],'prepared42cores preserve exact caller-and-host selected independent bytes')
                report=json.loads(service.vault.object_read(domain['validation_report_binding']));need(report['result']!='fail','actual prepared validation report passes construction')
                scope_check=next(c for c in report['checks'] if c['check_ref']=='check:declared-domain-scope-preparation');need(scope_check['result']=='pass','actual declared domain profile check passes')
                # Resolve actual recorded scope evidence through the exact private vault.
                evidence=scope_check['evidence_bindings'];need(len(evidence)==1,'exact recorded scope check evidence')
                check_record=json.loads(service.vault.object_read(evidence[0]));scope_evidence=json.loads(service.vault.object_read(check_record['details']['scope_evidence_binding']))
                need(scope_evidence['target_count']==42 and len(scope_evidence['hypotheses'])==21 and scope_evidence['source_projection_unchanged'] and not scope_evidence['runtime_admission_authorized'],'all21domain hypotheses retained with no runtime authority')
                need(all(h['configuration_status']=='hypothetical-unprovisioned' and h['actual_runtime_grant'] is False for h in scope_evidence['hypotheses']),'scope configuration simulations never grant operational permission')
                need({v for h in scope_evidence['hypotheses'] for v in h['version_refs']}=={t['artifact']['version_ref'] for t in targets},'exact42target/21scope evidence closure')
                for hypothesis in scope_evidence['hypotheses']:
                    config=dict(view.data['config']);config['scope_ref']=hypothesis['domain_scope_ref']
                    need(sha(view.handle.common.encoded(config))==hypothesis['configuration_sha256'],'hypothetical configuration differs only in declared scope '+hypothesis['domain_scope_ref'])
                observations.append({'call':prepare_call,'reply':prepared,'actual_validation_report':report})
                for target in targets:
                    raw=materials[target['content']['content_ref']];core_raw=materials[target['decision_core_binding']['ref']]
                    need(sha(raw)==target['artifact']['byte_sha256'] and sha(core_raw)==target['decision_core_binding']['sha256'],'independent owner body/core bytes '+target['artifact']['version_ref'])
                    body=json.loads(raw);core=json.loads(core_raw)
                    member=next(x for x in load(SELECTED.parent/'owner-core-preparation-v1/artifacts/manifest.json')['members'] if x['version_ref']==target['artifact']['version_ref'])
                    need(core==load(ROOT/member['independent_core_binding']['path']),'actual prepared core equals separately frozen kernel core '+target['artifact']['version_ref'])
                validate_call=F.candidate(service,targets,operation='change.validate',key='audit:all42-validate');validated=service.call(P.compact(validate_call))
                need(validated['kind']=='result' and validated['message']['result']!='fail','independent public42validation succeeds')
                observations.append({'call':validate_call,'reply':validated})
                for op in ['context.get','session.open','session.close','session.inspect']:
                    call=F.call(channel.context,'lab.status',source_cut);call['operation']=op;reply=service.call(P.compact(call));need(reply['code']=='unsupported-operation' and not reply['effect_may_have_started'],'metadata denies original Agent operation '+op)
                query=F.call(channel.context,'lab.status',source_cut);status=service.call(P.compact(query));need(status['kind']=='result' and status['message']['source_cut']==source_cut,'actual independent metadata source status')
                generation=Q.Generation(view,source_cut,schemas)
                try:
                    need(generation.metadata[2]==view.handle.manifest['profile_binding']['sha256'] and generation.db.execute('PRAGMA foreign_key_check').fetchall()==[],'complete SQL selected source profile and foreign keys')
                    with GR.model_read_batch(view):
                        for row in artifacts:
                            h=row['artifact'];raw=M.record_bytes(view,view.subjects[h['version_ref']])[0]
                            need(generation.db.execute('SELECT content FROM content_cache WHERE byte_sha256=?',(h['byte_sha256'],)).fetchone()[0]==raw,'full SQL actual original body BLOB '+h['version_ref'])
                    need(generation.db.execute('SELECT count(*) FROM artifact_revision').fetchone()[0]==len(view.subjects),'full SQL all original source revisions')
                    generation.verify();checks.append('full SQL exact DDL/rows/metadata/fileSHA/pointer/privacy/integrity guard')
                finally:generation.close()
                public.append({'owned_root':str(root),'public_policy':policy,'public_policy_original_sha256':sha(policy_raw),'signed_nonce_proof':proof,'authentication_context':auth['context'],'actual_public_observations':observations,'authority_effect':'none','actual_owner_outcome':None})
            finally:service.close();key=None
        need(not root.exists(),'owned independent metadata key/policy/workspace removed')
        need(original_period_path.read_bytes()==original_period,'expired original Assignment never renewed or modified')
        view.custody_signed_sources.guard();checks.append('final independent original signed source guard')
    G.verify(m['api_source_binding']['sha256'])
    for row in m['files']:need(bind(ROOT/row['path'])==row,'unchanged final audit input '+row['path'])
    audit={'schema_version':'lab-original-source-API-independent-observation/v1-candidate','result':'PASS','checks':len(checks),'check_names':checks,'source_binding':bind(SOURCE),'selected_API_source_binding':m['api_source_binding'],'selected_API_profile_binding':m['api_profile_binding'],'parent_files_retained':len(parent['files']),'original_byte_observations':artifacts,'actual_owned_nonce_and_candidate_observations':public,'owned_host_roots_removed':roots,'full_SQL_original_byte_BLOBs_independently_verified':True,'observed_at':datetime.now(timezone.utc).isoformat(),'actual_public_API_operations':12,'original_operations':34,'authority_effect':'none','actual_owner_outcome':None,'task_complete':False,'goal_complete':False,'full_suite_qualification':False,'claim_ceiling':'Independent metadata source/API/SQL/nonce and42owner-core construction observations only. Current Agent episode, public review, remaining22APIs, all46criteria and S02/R08 still required.'}
    audit_path=HERE/'metadata-scope-independent-observations-0001.json';put(audit_path,audit)
    print(json.dumps({'result':'PASS','checks':len(checks),'source_files':len(rows),'observation_binding':bind(audit_path),'full_suite_qualification':False}),flush=True)
if __name__=='__main__':main()
