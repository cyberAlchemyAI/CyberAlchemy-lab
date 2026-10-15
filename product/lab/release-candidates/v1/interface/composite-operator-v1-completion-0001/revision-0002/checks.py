"""Focused controls only: no fake full34 construction or governing authority."""
import base64,copy,importlib.util,io,json,os,subprocess,sys,tempfile,time
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import composite as C
from control import *
from framing import Reader,FrameError,dispatch
HERE=Path(__file__).resolve().parent
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/revision-0002'
T34=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T34/task-session-result.json'
def put(path,raw):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as out:out.write(raw);out.flush();os.fsync(out.fileno())
def pin(path):return {'path':str(path),'identity':ident(path.stat()),'sha256':sha(path.read_bytes())}
def pub(k):return base64.b64encode(k.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)).decode()
def session():
    path=ROOT/'implementation/lab-workflows/candidates/v1/authority/evaluator.py'
    name='_T06_actual_original_session';spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    value=module.SessionLease(ttl=30);need(value.clock is time.time,'original actual UTC clock required');return value
def fixture():
    root=Path(tempfile.mkdtemp(prefix='cal-T06-owned-controls-'));os.chmod(root,0o700)
    for name in ['base','actions','governance']:(root/name).mkdir(mode=0o700)
    keys={n:Ed25519PrivateKey.generate() for n in ['base','actions','governance','source','custody','grant','policy']}
    auth={'path':str(T34.relative_to(ROOT)),'sha256':sha(T34.read_bytes())}
    now=time.time();expires=now+600
    policies={}
    for name in ['base','actions','governance']:
        p={'schema_version':'inert-T06-control-policy-not-an-API-policy','principal_ref':'principal:inert-'+name,'scope_ref':'scope:inert-'+name,'authority_effect':'none','actual_owner_outcome':None,'revoked':False,'expires_at':datetime_text(expires),'max_request_bytes':65536,'max_response_bytes':1048576,'allowed_operations':['inert-observation-only']}
        p['reader_public_key_hex' if name=='governance' else 'reader_public_key' if name=='base' else 'public_key']=keys[name].public_key().public_bytes_raw().hex() if name=='governance' else pub(keys[name]);policies[name]=p
    old={'schema_version':'inert-T06-source-not-schema-qualified','scope_ref':'scope:inert-actions','records':{'role-assignment-placeholder':{'original_b64':'aW5lcnQ=','sha256':sha(b'inert')}},'refs':{'agent-instance':'inert:instance@1','agent-session':'inert:session@1'},'runtime_bindings':{'instance':'old-inert-instance','session':'old-inert-session'},'initial_status':{'runtime_handle_bindings':{'inert:instance@1':'old-inert-instance','inert:session@1':'old-inert-session'},'revoked_refs':[],'periods':{'period:inert':[now-1,expires]},'stopped':False}}
    source_raw=compact(old);grant={'schema_version':'inert-T06-grant-not-authority','principal_ref':policies['actions']['principal_ref'],'scope_ref':policies['actions']['scope_ref'],'source_sha256':sha(source_raw),'not_before':now-1,'expires_at':expires,'max_actions':1,'role_assignment_ref':'inert:unchanged-not-a-grant'}
    policies['actions'].update(source_binding={'ref':'action-source:'+sha(source_raw),'sha256':sha(source_raw)},grant_binding={'ref':'action-grant:'+sha(compact(grant)),'sha256':sha(compact(grant))})
    files={'source.json':source_raw,'source.signature':base64.b64encode(keys['source'].sign(source_raw)),'grant.json':compact(grant),'status.json':compact(old['initial_status']),'ledger-pins.json':b'{}'}
    for name,raw in files.items():put(root/'actions'/name,raw)
    for name,p in policies.items():put(root/name/'operator-policy.json',compact(p))
    (root/'base/workspace').mkdir(mode=0o700);put(root/'base/workspace/workspace.json',b'{}');policies['base']['workspace']={'root':str(root/'base/workspace'),'manifest_sha256':sha(b'{}')};(root/'base/operator-policy.json').write_bytes(compact(policies['base']));(root/'governance/native-store').mkdir(mode=0o700)
    for name in ['config.json','baseline.json','HEAD.json']:put(root/'governance/native-store'/name,b'{}')
    config={'schema_version':'lab-composite-operator-config/v2-candidate','purpose':'owned-candidate-rehearsal','authority_effect':'none','provisioning_binding':auth,'source':{'directory':str(C.API),'source_sha256':'0'*64,'profile_sha256':'0'*64,'members_sha256':'0'*64,'bootstrap_bindings':[]},'dependencies':{'selection':{'path':C.DEPENDENCY_SELECTION,'sha256':C.DEPENDENCY_SHA},'installation':str(C.INSTALL)},'branches':{},'handoff':{'contract':'fresh-session-current-source-handoff/v1-candidate','startup_seconds':2,'issuers':{n:{'public_key':pub(keys[n]),'authorization_binding':auth,'posture':'independently-selected-candidate-technical-issuer'} for n in ['custody','grant','policy']}},'transport':{'max_frames':64,'max_wire_bytes':2097152,'max_frame_bytes':65536,'max_response_bytes':1048576}}
    for n in ['base','actions','governance']:
        names=['workspace/workspace.json'] if n=='base' else sorted(C.ACTION_FILES) if n=='actions' else ['native-store/config.json','native-store/baseline.json','native-store/HEAD.json']
        b={'workspace_root':str(root/n),'root_identity':ident((root/n).stat()),'policy':pin(root/n/'operator-policy.json'),'public_key':pub(keys[n]),'files':{k:pin(root/n/k) for k in names}}
        if n=='actions':b.update(source_public_key=pub(keys['source']),lease_ttl=30)
        if n=='base':b.update(vault={'root':str(root/'base/workspace'),'root_identity':ident((root/'base/workspace').stat())})
        config['branches'][n]=b
    initial={'controls':{'actions':(policies['actions'],files)}}
    return root,config,keys,initial
def datetime_text(seconds):
    from datetime import datetime,timezone
    return datetime.fromtimestamp(seconds,timezone.utc).isoformat()
def fresh_materials(root,initial,lease,source_key):
    source=copy.deepcopy(parse(initial['controls']['actions'][1]['source.json']));status=copy.deepcopy(source['initial_status']);fresh={'instance':lease.instance_ref,'session':lease.session_ref}
    source['runtime_bindings']=fresh;handles={source['refs']['agent-instance']:lease.instance_ref,source['refs']['agent-session']:lease.session_ref};source['initial_status']['runtime_handle_bindings']=handles;status['runtime_handle_bindings']=handles
    source_raw=compact(source);grant=copy.deepcopy(parse(initial['controls']['actions'][1]['grant.json']));grant['source_sha256']=sha(source_raw);grant_raw=compact(grant)
    policy=copy.deepcopy(initial['controls']['actions'][0]);policy['source_binding']={'ref':'action-source:'+sha(source_raw),'sha256':sha(source_raw)};policy['grant_binding']={'ref':'action-grant:'+sha(grant_raw),'sha256':sha(grant_raw)}
    materials={'source.json':source_raw,'source.signature':base64.b64encode(source_key.sign(source_raw)),'status.json':compact(status),'grant.json':grant_raw,'ledger-pins.json':initial['controls']['actions'][1]['ledger-pins.json'],'operator-policy.json':compact(policy)}
    for name,raw in materials.items():(root/'actions'/name).write_bytes(raw)
    return {name:pin(root/'actions'/name) for name in materials}
def packet(config,config_sha,lease,pins,keys):
    body={'schema_version':'lab-composite-current-handoff/v1-candidate','configuration_sha256':config_sha,'fresh_lease':{'instance':lease.instance_ref,'session':lease.session_ref},'files':pins}
    authorizations={}
    for kind in ['custody','grant','policy']:
        signed={'schema_version':'lab-composite-current-selection-authorization/v1-candidate','selection_kind':kind,'purpose':'candidate-technical-current-selection','authority_effect':'none','issuer_authorization_binding':config['handoff']['issuers'][kind]['authorization_binding'],'handoff':body}
        authorizations[kind]={'signature_base64':base64.b64encode(keys[kind].sign(compact(signed))).decode()}
    return body|{'authorizations':authorizations}
def checks(report_name='focused-evidence-0002.json'):
    cases=[];roots=[]
    def refused(label,fn):
        try:fn()
        except Exception as error:cases.append({'case':label,'result':'PASS-refused','error_type':type(error).__name__})
        else:raise AssertionError(label+' accepted')
    root,config,keys,initial=fixture();roots.append(str(root));C.config_shape(config);config_sha=sha(compact(config));put(root/'initial-config.json',compact(config))
    # Missing credential probes execute preflight itself before source/API load.
    for kind in ['base','actions','governance']:
        policy=root/kind/'operator-policy.json';policy.rename(root/(kind+'-policy-retained.json'))
        refused('missing '+kind+' independent policy before any startup effect',lambda:C.preflight(config,config_sha))
        (root/(kind+'-policy-retained.json')).rename(policy)
    refused('valid private controls cannot fabricate pending API17 software guard',lambda:C.preflight(config,config_sha))
    changed=copy.deepcopy(config);del changed['branches']['governance'];refused('base-only configuration refuses full34 label',lambda:C.config_shape(changed))
    changed=copy.deepcopy(config);changed['purpose']='admitted-operation';refused('no admitted operator mode',lambda:C.config_shape(changed))
    changed=copy.deepcopy(config);changed['handoff']['issuers']['grant']['public_key']=changed['handoff']['issuers']['custody']['public_key'];refused('custody key cannot impersonate independent grant issuer',lambda:C.config_shape(changed))
    lease=session()
    try:
        pins=fresh_materials(root,initial,lease,keys['source']);valid=packet(config,config_sha,lease,pins,keys)
        accepted=C.authorize_handoff(config,config_sha,lease,compact(valid),initial);need(accepted==pins,'inert helper selection mismatch')
        cases.append({'case':'inert handoff helper retains immutable bytes and real fresh lease; no actual API/authority success claimed','result':'PASS-helper-only'})
        bad=copy.deepcopy(valid);del bad['authorizations']['grant'];refused('missing independent grant authorization',lambda:C.authorize_handoff(config,config_sha,lease,compact(bad),initial))
        bad=copy.deepcopy(valid);bad['authorizations']['grant']=bad['authorizations']['custody'];refused('custody signature cannot authorize grant digest change',lambda:C.authorize_handoff(config,config_sha,lease,compact(bad),initial))
        bad=copy.deepcopy(valid);bad['fresh_lease']['session']='old-inert-session';refused('old Session identity handoff',lambda:C.authorize_handoff(config,config_sha,lease,compact(bad),initial))
        second=session()
        try:refused('new process lease rejects prior handoff',lambda:C.authorize_handoff(config,config_sha,second,compact(valid),initial))
        finally:second.close()
        for filename,mutate,label in [('grant.json',lambda d:d.update(expires_at=d['expires_at']+1),'grant expiry extension'),('grant.json',lambda d:d.update(max_actions=2),'grant budget widening'),('operator-policy.json',lambda d:d.update(allowed_operations=['inert-observation-only','admission.apply']),'policy permission widening'),('source.json',lambda d:d['records'].update({'forged-role-assignment':'new bytes'}),'source RoleAssignment/body substitution'),('status.json',lambda d:d.update(stopped=True),'changed current stop state')]:
            path=root/'actions'/filename;original=path.read_bytes();value=parse(original);mutate(value);path.write_bytes(compact(value));badpins=copy.deepcopy(pins);badpins[filename]=pin(path)
            if filename=='source.json':(root/'actions/source.signature').write_bytes(base64.b64encode(keys['source'].sign(path.read_bytes())));badpins['source.signature']=pin(root/'actions/source.signature')
            bad=packet(config,config_sha,lease,badpins,keys);refused(label+' even with three technical signatures',lambda:C.authorize_handoff(config,config_sha,lease,compact(bad),initial));path.write_bytes(original)
            if filename=='source.json':(root/'actions/source.signature').write_bytes(base64.b64encode(keys['source'].sign(original)))
        original=root/'actions/grant.json';original.rename(root/'grant-retained.json');original.symlink_to(root/'grant-retained.json');refused('protected grant symlink',lambda:C.authorize_handoff(config,config_sha,lease,compact(valid),initial));original.unlink();(root/'grant-retained.json').rename(original)
        os.chmod(root/'actions/operator-policy.json',0o644);refused('protected current policy mode',lambda:C.authorize_handoff(config,config_sha,lease,compact(valid),initial));os.chmod(root/'actions/operator-policy.json',0o600)
        lease.close();refused('closed actual lease refuses handoff',lambda:C.authorize_handoff(config,config_sha,lease,compact(valid),initial))
    finally:lease.close()
    # Framing probes deliberately use a transport observer, not a fabricated
    # IntegrationService or mocked original authenticated branch.
    class Observer:
        def __init__(self):self.raw=[]
        def call(self,raw):self.raw.append(raw);return {'byte_sha256':sha(raw)}
    payloads=[b'{ "operation" : "operation.inspect", "message":{"lookup":{"operation":"action.dispatch"}} }\r',b'{"message":{"lookup":{"operation":"admission.apply"}},"operation":"operation.inspect"}',b'{"operation":"catalog.get"}']
    observer=Observer();output=io.BytesIO();reader=Reader(io.BytesIO(b'\n'.join(payloads)+b'\n'),max_frames=10,max_wire_bytes=4096)
    need(dispatch(observer,reader,output,1024,4096)==0 and observer.raw==payloads,'transport changed raw envelope bytes');cases.append({'case':'serialized transport preserves all original raw bytes including CR/whitespace/member order','result':'PASS-transport-observer-only'})
    for label,data,limit,frames,budget in [('partial EOF',b'{}',8,5,32),('oversize line',b'123456789\n',8,5,32),('wire budget',b'{}\n',8,5,2),('frame budget',b'{}\n{}\n',8,1,32)]:
        def run_frame():
            r=Reader(io.BytesIO(data),max_frames=frames,max_wire_bytes=budget)
            while r.receive(limit) is not None:pass
        refused(label,run_frame)
    left,right=os.pipe()
    try:
        with os.fdopen(left,'rb') as stream:refused('real pipe startup deadline with no input',lambda:Reader(stream,max_frames=2,max_wire_bytes=64).receive(32,time.monotonic()+0.02))
    finally:os.close(right)
    from contextlib import ExitStack
    events=[]
    with ExitStack() as owned:
        owned.callback(lambda:events.append('first-owned'));owned.callback(lambda:events.append('last-owned'))
    need(events==['last-owned','first-owned'],'owned shutdown order differs');cases.append({'case':'deterministic reverse owned cleanup contract','result':'PASS-contract-only'})
    # Fresh selected process: missing governance credentials never emits a
    # challenge, loads an API branch, writes a lock or declares full34 ready.
    fresh_root,fresh_config,_,_=fixture();roots.append(str(fresh_root));missing=fresh_root/'governance/operator-policy.json';missing.rename(fresh_root/'governance-policy-retained.json');put(fresh_root/'config.json',compact(fresh_config))
    code='import sys;sys.path[:0]=['+repr(str(C.INSTALL/'deps'))+','+repr(str(HERE))+'];from composite import main;raise SystemExit(main())'
    command=[str(C.INSTALL/'lib/abi/ld-linux-x86-64.so.2'),'--inhibit-cache','--library-path',str(C.INSTALL/'lib/abi'),str(C.INSTALL/'bin/python'),'-I','-X','utf8','-B','-S','-c',code,'--config',str(fresh_root/'config.json'),'--config-sha256',sha(compact(fresh_config))]
    result=subprocess.run(command,input=b'',capture_output=True,env={'PATH':'/usr/bin:/bin','LC_ALL':'C'})
    need(result.returncode==2 and parse(result.stdout)['code']=='startup-or-channel-refused' and b'challenge' not in result.stdout and not list(fresh_root.rglob('*.lock')),'missing credential startup produced effects/readiness');cases.append({'case':'real fresh process missing governance credentials fail before challenge/effects','result':'PASS','returncode':result.returncode})
    report={'schema_version':'lab-T06-focused-development/v1-candidate','result':'PASS','cases':cases,'owned_roots':roots,'actual_full34_construction':False,'actual_Schemas_shared_by_three_branches_tested':False,'genuine_operational_signer_or_grant_authority_proven':False,'inert_fixture_sources_or_grants_used_as_actual_runtime':False,'task_complete':False,'authority_effect':'none','pending':'Exact coordinator API17 candidate source/profile/bootstrap execution selection and independently selected actual branch inputs/full fresh-process three-branch qualification.'}
    output=RUN/report_name;put(output,json.dumps(report,indent=2,sort_keys=True).encode()+b'\n');print(json.dumps({'result':'PASS','cases':len(cases),'report':str(output)}))
if __name__=='__main__':checks()
