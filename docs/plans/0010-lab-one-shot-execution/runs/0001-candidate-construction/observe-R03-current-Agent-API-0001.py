"""Development observation of actual new Session under frozen candidate controls.

Seven preflight controls must pass. Full146/134 qualification is expressly
pending. This script proves only the actual observed lifecycle and disposal.
"""
import argparse,base64,hashlib,importlib.util,json,os,sys,tempfile,uuid
from pathlib import Path
from datetime import datetime,timezone
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v29'
SOURCE=RUN/'current-Agent-development-observation-source-0001.json'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def bind(p):return {'path':p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p),'sha256':sha(p.read_bytes())}
def load(p):return json.loads(p.read_bytes())
def encoded(v):return (json.dumps(v,indent=2,sort_keys=True,ensure_ascii=False)+'\n').encode()
def put(p,v):
    p.parent.mkdir(mode=0o700,exist_ok=True);fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as f:f.write(encoded(v))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-sha256',required=True);a=ap.parse_args()
    assert sha(SOURCE.read_bytes())==a.source_sha256;frozen=load(SOURCE);checks=[];observations=[]
    def need(v,label):
        if not v:raise AssertionError(label)
        checks.append(label)
    def guard():
        for r in frozen['files']:need(bind(ROOT/r['path'])==r,'exact audit input '+r['path'])
    guard()
    for name,count in [('current-controls.json',7)]:
        report=load(API/'receipts'/name)
        need(report['result']=='PASS' and report['tests_run']==report['expected_tests']==count,'full completed regression '+name)
        need(all(c['result']=='PASS' for c in report['cases']),'every recorded regression case '+name)
    name='_cal_current_Agent_development_observation'
    spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)]);pkg=importlib.util.module_from_spec(spec);sys.modules[name]=pkg;spec.loader.exec_module(pkg)
    def imported(n):return __import__(name+'.'+n,fromlist=['*'])
    P,F,S,A,H,W,G=[imported(n) for n in ['protocol','example_fixture','service','auth','handlers','workspace','guard']]
    C=imported('custody_context_sessions');D=C.D;R=C.R;GR=imported('guarded_reads');M=imported('artifact_model')
    G.verify(frozen['api_source_binding']['sha256']);schemas=P.Schemas(frozen['api_profile_binding']['sha256'])
    need(len(P.SUPPORTED)==13 and len(schemas.operations)==34,'exact13handlers and34declaredoperations')
    with P.source.replay_source('custody-participation') as view:
        selected=view.custody_signed_sources;cut=H.cut(view);before=P.compact(view.data)
        need(D.reader is D.MAPPED.reader and D.EL is D.reader.adapter.eligibility,'shared real reader/mapper/eligibility objects')
        period_path=D.reader.HERE/'packages/0001/period.json';period_raw=period_path.read_bytes();period=load(period_path)
        old=period['original_expired_period_binding'];oldraw=P.source.original(old)
        need(period['principal_ref']==R.PRINCIPAL=='principal:R03-current-episode-0002','exact distinct new accountable Principal')
        need(load(ROOT/old['path'])['expires_at']=='2026-10-10T02:45:14.443492+00:00' and A.now()>A.instant(load(ROOT/old['path'])['expires_at']),'old source period remains expired')
        raw_bodies=0
        with GR.model_read_batch(view):
            for subject in view.subjects.values():
                if subject['source'].get('encoding')!=view.handle.custody.ENCODING:continue
                raw=M.record_bytes(view,subject)[0];header=M.artifact_ref(view,subject)
                tx=json.loads(view.originals[subject['source']['path']]);target=view.handle.common.pointer(tx,subject['source']['record_selector'].removesuffix('/record'))
                original=base64.b64decode(target['content']['data'],validate=True)
                need(raw==original and sha(raw)==header['byte_sha256'],'actual original raw body '+header['version_ref']);raw_bodies+=1
        need(raw_bodies==23,'all23original bodies survive actual API model')
        materials,metadata,target=F.materials_for(view)
        with tempfile.TemporaryDirectory(prefix='cal-R03-current-Agent-independent-audit-') as tmp:
            root=Path(tmp);root.chmod(0o700)
            key,path,pin=F.provision(root,'custody-participation',materials,metadata,principal=R.PRINCIPAL,projection_control=imported('projection_refresh').control(view))
            channel=A.ReaderChannel(path,pin,schemas);proof_raw=F.proof(key,channel.challenge);authenticated=channel.authenticate(proof_raw);policy=load(path);proof=json.loads(proof_raw)
            Ed25519PublicKey.from_public_bytes(base64.b64decode(policy['reader_public_key'],validate=True)).verify(base64.b64decode(proof['signature'],validate=True),P.compact(proof['challenge']))
            checks.append('independently verified actual Ed25519 nonce signature')
            need(proof['challenge']['policy_sha256']==pin==sha(path.read_bytes()) and authenticated['context']['authentication_evidence_binding']['sha256']==sha(proof_raw),'independent host/proof byte bindings')
            need(A.instant(period['not_before'])<=A.now()<A.instant(policy['expires_at'])<=A.instant(period['expires_at']),'new independently current host window bounded by fixed episode')
            need(channel.context['role_assignment_bindings']==[] and channel.context['authority_scope']=='operator-local','no owner role fabricated')
            service=S.Service(view,channel,schemas)
            def call(value,expected='result'):
                raw=P.compact(value);reply=service.call(raw)
                need(schemas.valid('api-reply',reply) and reply['kind']==expected,'actual typed API '+value['operation'])
                need(reply['request_binding']['sha256']==sha(raw),'exact actual request bytes '+value['operation'])
                W.privacy(reply);D.EL.no_private_memory(reply)
                observations.append({'call':value,'reply':reply})
                return reply['message']
            try:
                q=D.query(selected,service.sessions.bridge);q['budget'].update(max_input_bytes=65536,max_output_bytes=1048576)
                req=F.call(channel.context,'lab.status',cut);req.update(operation='context.get',message=q)
                delivered=call(req);need(delivered['posture']=='ready' and delivered['scope_enforced'] and A.instant(delivered['expires_at'])>A.now(),'actual fresh ready scoped Context delivery')
                ref=lambda i:selected.sources.resolve(i+'@'+R.VERSION)[0].artifact
                opening=F.call(channel.context,'lab.status',cut);opening['operation']='session.open';opening['idempotency_key']='audit-open:'+uuid.uuid4().hex
                actor=opening['message']['actor'];budget=opening['message']['budget'];budget['max_actions']=1
                opening['message']={'schema_version':'lab-agent-session-open/v1-candidate','request_ref':'request:current-Agent-independent:'+uuid.uuid4().hex,'actor':actor,'assignment':ref(R.ASSIGNMENT),'profile':ref(R.PROFILE),'implementation':ref(R.IMPLEMENTATION),'capabilities':[ref(R.CAPABILITY)],'context_delivery_binding':P.binding('context-delivery:'+delivered['context_view']['version_ref'],P.compact(delivered)),'authority_envelope_binding':C.stable_policy(channel),'source_cut':cut,'budget':budget,'memory_policy':{'persistence_allowed':False,'expires_with_session':True},'authority_effect':'none'}
                opened=call(opening);need(opened['posture']=='active' and opened['memory_persistence_allowed'] is False and opened['durable_continuity_source']=='project-state-via-context-and-ontology-views','actual ephemeral Agent Session and Project State continuity')
                sid=opened['session_ref'];resource=service.sessions.live[sid];resource.guard()
                note=b'audit-private-RAM-only-'+uuid.uuid4().hex.encode();resource.note(note);held=resource.memory[0]
                need(bytes(held)==note,'actual short memory exists in RAM')
                def inspect_call():
                    v=F.call(channel.context,'lab.status',cut);budget=v['message']['budget'];actor=v['message']['actor'];v.update(operation='session.inspect',message={'schema_version':'lab-session-inspect-request/v1-candidate','request_ref':'request:independent-session-inspect:'+uuid.uuid4().hex,'actor':actor,'session_ref':sid,'budget':budget,'authority_effect':'none'});return v
                active=call(inspect_call());need(active['posture']=='active' and active['short_memory_in_response'] is False,'actual active inspection excludes memory')
                history=service.sessions.selected(sid)
                need(history['principal_ref']==R.PRINCIPAL and history['scope_ref']==selected.sources.scope_ref and history['source_cut']==cut and history['short_memory_persisted'] is False,'durable audit metadata exact scope/source excludes short memory')
                need(resource.session['payload']['context_view_ref']==delivered['context_view']['version_ref'] and resource.session['payload']['ontology_view_ref']==delivered['ontology_view']['version_ref'],'actual Session consumes both actual Project State/Ontology views')
                need(len(history['connection_records'])==7,'all7actual typed Session connections')
                for obj in history['connection_records']:
                    body=obj['record'];payload=body['payload'];need(payload['source']['version_ref']==obj['source_artifact']['version_ref'] and payload['target']['version_ref']==obj['target_artifact']['version_ref'],'actual typed Session exact endpoint versions')
                    need(obj['authority_effect']=='none' and obj['posture']=='candidate-ephemeral-connection','typed connection does not admit or grant authority')
                close=F.call(channel.context,'lab.status',cut);close.update(operation='session.close',idempotency_key='audit-close:'+uuid.uuid4().hex,message={'schema_version':'lab-agent-session-close/v1-candidate','request_ref':'request:current-Agent-independent-close:'+uuid.uuid4().hex,'session_ref':sid,'agent_instance_ref':opened['agent_instance_ref'],'expected_session_binding':active['last_receipt_binding'],'requested_at':A.now().isoformat(),'reason':'completed','eligible_audit_bindings':[],'authority_effect':'none'})
                closed=call(close);need(closed['discarded_memory'] and closed['agent_identity_reuse_allowed'] is False,'actual closed receipt forbids identity/memory reuse')
                need(resource.closed and resource.memory==[] and bytes(held)==b'\0'*len(held) and resource.delivery is None and sid not in service.sessions.live,'actual retained RAM buffer zeroed and live resource removed')
                need(call(inspect_call())['posture']=='closed','actual durable closed inspection')
                retry=dict(opening);retry['call_id']='call:independent-retry:'+uuid.uuid4().hex;historical=call(retry)
                need(historical==opened and sid not in service.sessions.live and resource.closed,'exact idempotent opening retry remains historical and cannot restore RAM')
                for p in (root/'workspace').rglob('*'):
                    if p.is_file():need(note not in p.read_bytes(),'private RAM bytes never persisted '+p.relative_to(root).as_posix())
                for v in observations:need(note not in P.compact(v),'private RAM absent from recorded calls/replies')
            finally:service.close();key=None
        need(not root.exists(),'owned private host/key/workspace root removed')
        need(period_path.read_bytes()==period_raw and P.source.original(old)==oldraw and P.compact(view.data)==before,'fixed new/expired periods and actual signed Project State unchanged')
        selected.guard()
    guard()
    out=API/'receipts/current-Agent-development-observation.json'
    v={'schema_version':'lab-current-Agent-development-observation/v1-candidate','result':'PASS','checks_including_input_file_hashes':len(checks),'check_names':checks,'source_binding':bind(SOURCE),'actual_Actor_Session_created_and_closed':True,'whole_API_qualification':False,'full146_and134_qualification':False,'current_Agent_qualified':False,'raw_source_bodies':23,'private_root_removed':True,'new_source_and_original_expired_period_unchanged':True,'actual_nonce_signature_verified':True,'actual_memory_zeroed':True,'saved_retry_restores_memory':False,'public_operations':13,'original_public_operations':34,'remaining_public_operations':21,'current_owner_authority_verified':False,'repository_admissions_applied':0,'authority_effect':'none','actual_owner_outcome':None,'task_complete':False,'goal_complete':False}
    put(out,v);put(API/'receipts/current-Agent-development-wire.json',{'observations':observations,'authority_effect':'none','actual_owner_outcome':None})
    print(json.dumps({'result':'PASS','checks_including_hashes':len(checks),'audit_binding':bind(out)}),flush=True)
if __name__=='__main__':main()
