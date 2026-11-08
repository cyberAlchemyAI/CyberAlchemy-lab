"""Private first emission of actual native lifecycle bodies; never Session RAM.

This produces private, uncommitted material. Only a separately committed owned
workflow journal may publish its ArtifactRefs as owned-produced-current.
"""
from __future__ import annotations
import base64,copy,hashlib,importlib,importlib.util,json,os,stat,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
CATALOG_SHA='b2709686d7a34ff704ebaa4c7dc78c18281208adfe2daeedf84fc5a0705e6ed8'
def need(ok,reason):
    if not ok:raise ValueError(reason)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def compact(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def instant(text):
    v=datetime.fromisoformat(text.replace('Z','+00:00'));need(v.tzinfo is not None,'UTC instant required');return v
def owned(path,mode):
    path=Path(path);need(path.is_absolute() and not path.is_symlink() and not any(p.is_symlink() for p in path.parents),'unsafe private emitter locator')
    s=path.stat();need(s.st_uid==os.getuid() and stat.S_IMODE(s.st_mode)==mode,'private emitter owner/mode differs');return path
def read_private(path):
    path=owned(path,0o600);fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    try:
        s=os.fstat(fd);need(stat.S_ISREG(s.st_mode) and s.st_uid==os.getuid() and stat.S_IMODE(s.st_mode)==0o600
                            and s.st_nlink==1 and s.st_size<=16*1024*1024,'bounded private emitter file required')
        with os.fdopen(fd,'rb',closefd=False) as stream:raw=stream.read(16*1024*1024+1)
        need(len(raw)==s.st_size,'private emitter input changed');return raw
    finally:os.close(fd)
def write_new(path,raw):
    fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
    fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
def carrier_validator():
    name='_t31_native_first_emitter_store'
    if name not in sys.modules:
        s=importlib.util.spec_from_file_location(name,HERE/'output_store.py');m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m)
    m=sys.modules[name];need(m.CATALOG_SHA==CATALOG_SHA,'original first-emitter carrier catalog differs');return m.original_carriers()

class NativeFirstEmitter:
    def __init__(self,*,api_directory,source_sha256,profile_sha256,control_path,control_sha256,adapter_sha256):
        self.api=Path(api_directory);need(self.api.parent==ROOT/'product/lab/release-candidates/v1/interface' and self.api.is_dir(),'selected native API directory required')
        need(sha(Path(__file__).read_bytes())==adapter_sha256,'independent first-emitter code pin differs')
        self.adapter_sha=adapter_sha256;self.source_sha=source_sha256;self.profile_sha=profile_sha256
        self.control_path=Path(control_path);need(not self.control_path.is_relative_to(ROOT),'private first-emitter grant required')
        self.control_sha=control_sha256
        sys.path.insert(0,str(self.api.parent));package=self.api.name
        self.P=importlib.import_module(package+'.protocol');self.G=importlib.import_module(package+'.guard')
        self.S=importlib.import_module(package+'.service');self.A=importlib.import_module(package+'.auth')
        self.C=importlib.import_module(package+'.current_legacy_context_sessions')
        self.carriers=carrier_validator();self.completed=False
    def control(self):
        need(sha(Path(__file__).read_bytes())==self.adapter_sha,'first-emitter code changed')
        raw=read_private(self.control_path);need(sha(raw)==self.control_sha,'first-emitter grant changed or revoked');p=json.loads(raw)
        fields={'schema_version','principal_ref','scope_ref','source_cut','session_ref','opening_result_sha256','producer_policy_sha256','output_root','not_before','expires_at','revoked','permitted_effects','authority_effect','actual_owner_outcome'}
        need(type(p) is dict and set(p)==fields and p['schema_version']=='lab-private-native-first-emitter-grant/v1-fixture'
             and p['permitted_effects']==['emit-formal-lifecycle-output'] and p['authority_effect']=='none'
             and p['actual_owner_outcome'] is None and p['revoked'] is False,'closed scoped fixture first-emitter grant required')
        need(instant(p['not_before'])<=self.A.now()<instant(p['expires_at']),'first-emitter grant expired/not started');return p
    def live(self,host,opening):
        p=self.control();manifest=self.G.verify(self.source_sha)
        need(manifest['profile_binding']['sha256']==self.profile_sha,'selected native manifest/profile differs')
        need(type(host) is self.S.Service,'exact selected native Service type required')
        need(type(host.channel) is self.A.ReaderChannel,'exact selected native ReaderChannel type required')
        expected={'ref':manifest['profile_binding']['path'],'sha256':manifest['profile_binding']['sha256']}
        need(type(host.schemas) is self.P.Schemas and host.schemas.profile_binding==expected,
             'exact selected native protocol profile binding differs')
        host.schemas.guard()
        context=host.channel.guard();host.vault.guard();resource=host.sessions.live.get(p['session_ref'])
        need(type(resource) is self.C.LiveReader and not resource.closed and resource.source is host.sessions.source
             and resource.bridge is host.sessions.bridge and resource.source is host.handlers.view.custody_signed_sources,
             'actual selected native Session resource unavailable')
        resource.guard();row=host.sessions.selected(p['session_ref'])
        need(row['posture']=='active' and row['source_cut']==p['source_cut']==opening['source_cut']
             and context['principal_ref']==row['principal_ref']==p['principal_ref']
             and host.channel.policy['scope_refs']==[p['scope_ref']]
             and host.channel.expected_sha==p['producer_policy_sha256']
             and p['opening_result_sha256']==sha(self.P.compact(opening)),
             'first emission actual Actor/cut/grant/opening differs')
        raw=host.vault.object_read(row['result_object_binding'])
        need(self.P.frame_parse(raw)==opening and row['agent_instance_ref']==opening['agent_instance_ref']==resource.agent['node_id']
             and resource.session['node_id']==p['session_ref'] and resource.agent==row['agent_record'],
             'first emission original native result/resource differs')
        need(not resource.closed and host.sessions.live.get(p['session_ref']) is resource
             and resource.source is host.sessions.source and resource.bridge is host.sessions.bridge
             and self.A.now()<min(resource.expires,instant(p['expires_at'])) and instant(p['expires_at'])<=resource.expires,
             'actual Session/grant expired before emission')
        return resource,p
    def emit(self,host,opening):
        need(not self.completed,'first-emitter invocation never redispatches');resource,p=self.live(host,opening)
        output=Path(p['output_root']);owned(output,0o700)
        need(not output.is_relative_to(ROOT) and not any(output.iterdir()),'fresh external private output custody required')
        proof=host.sessions.delivery(opening['context_delivery_binding'])
        delivery=self.P.frame_parse(host.vault.object_read(proof['delivery_object_binding']))
        bodies=[]
        for kind in ('context-view','ontology-view'):
            header=delivery[kind.replace('-','_')];raw=host.vault.object_read({'ref':'workspace-object:'+host.vault.manifest['workspace_ref']+':'+header['byte_sha256'],'sha256':header['byte_sha256']})
            bodies.append((header,raw,'exact-existing-native-Vault-bytes'))
        # Formal reference arrays belong to the original lifecycle schema.
        # The separate resource.memory field is deliberately never accessed.
        body=copy.deepcopy(resource.session);memory=body['payload']['session_memory']
        need(memory=={'selected_input_refs':[body['payload']['context_view_ref'],body['payload']['ontology_view_ref']],
                     'working_record_refs':[],'unresolved_questions':[],'expires_with_session':True},
             'formal lifecycle body was changed from its actual native opening')
        raw=self.P.compact(body);header={'scope_ref':body['scope_ref'],'identity_ref':body['node_id'],
          'version_ref':body['node_id']+'@ephemeral.1','carrier_ref':'cal.artifact-type.agent-session/v1','byte_sha256':sha(raw)}
        bodies.append((header,raw,'first-explicit-encoding-of-exact-native-formal-Session-body'))
        # Exact Source originals and actual generated ContextRequest are private
        # inputs for a later scoped coordination capsule, never source renewals.
        M=importlib.import_module(self.api.name+'.artifact_model');source_inputs=[]
        with M.model_read_batch(host.handlers.view):
            for name,identity in [('intent',self.C.R.INTENT),('work',self.C.R.WORK),('goal',self.C.R.GOAL),
                                  ('coordination-context',self.C.R.COORDINATION),('agent-assignment',self.C.R.ASSIGNMENT)]:
                selected=[s for s in host.handlers.view.subjects.values() if s['identity']==identity
                          and s['effective_state'] in ('admitted-current','local-admitted-current')]
                need(len(selected)==1,'exact native Source coordination input unavailable')
                header=M.artifact_ref(host.handlers.view,selected[0]);raw,locator,encoding,enclosing=M.record_bytes(host.handlers.view,selected[0])
                need(sha(raw)==header['byte_sha256'],'native Source original/header differs')
                source_inputs.append((name,header,raw,{'posture':selected[0]['effective_state'],'semantic_kind':name,
                  'source_locator':locator,'encoding':encoding,'enclosing_source_sha256':enclosing}))
        requests=[v for v in proof['generated_objects'] if v['artifact']['carrier_ref']=='cal.artifact-type.context-request/v1']
        need(len(requests)==1,'one actual native generated ContextRequest required')
        request=requests[0];request_raw=host.vault.object_read(request['object_binding'])
        need(sha(request_raw)==request['artifact']['byte_sha256'],'actual ContextRequest original/header differs')
        host.sessions.schema_record(self.P.frame_parse(request_raw))
        source_inputs.append(('context-request',request['artifact'],request_raw,{'posture':'produced-uncommitted',
                              'semantic_kind':'context-request','encoding':'exact-existing-native-Vault-bytes'}))
        for header,raw,basis in bodies:self.carriers.output(header,raw,scope_ref=p['scope_ref'])
        rows=[];self.completed=True
        try:
            for header,raw,basis in bodies:
                self.live(host,opening);path=output/(header['byte_sha256']+'.json');write_new(path,raw);self.live(host,opening)
                rows.append({'artifact':header,'path':path.name,'sha256':sha(raw),'encoding_basis':basis})
            coordination_rows=[]
            for kind,header,raw,origin in source_inputs:
                self.live(host,opening);name='input-'+kind+'.json';write_new(output/name,raw);self.live(host,opening)
                coordination_rows.append({'artifact':header,'path':name,'sha256':sha(raw),'origin':origin,
                                          'private_original_base64':base64.b64encode(raw).decode()})
            self.live(host,opening)
            receipt={'schema_version':'lab-observed-native-first-emitter/v1-candidate','outputs':rows,'coordination_inputs':coordination_rows,
              'api_source_binding':{'path':(self.api/'source-manifest.json').relative_to(ROOT).as_posix(),'sha256':self.source_sha},
              'api_profile_sha256':self.profile_sha,'adapter_sha256':self.adapter_sha,'control_sha256':self.control_sha,
              'opening_result_sha256':p['opening_result_sha256'],'source_cut':p['source_cut'],'principal_ref':p['principal_ref'],
              'scope_ref':p['scope_ref'],'session_ref':p['session_ref'],'observed_at':self.A.now().isoformat(),
              'actual_RAM_memory_accessed':False,'actual_RAM_memory_persisted':False,'WorkflowRun_committed':False,
              'authority_effect':'none','actual_owner_outcome':None}
            raw=compact(receipt);write_new(output/'emission.json',raw)
            try:self.live(host,opening)
            except BaseException:
                need(read_private(output/'emission.json')==raw,'first-emitter marker changed');(output/'emission.json').unlink()
                fd=os.open(output,os.O_RDONLY|os.O_DIRECTORY)
                try:os.fsync(fd)
                finally:os.close(fd)
                raise
            return {'receipt':receipt,'receipt_sha256':sha(raw),'output_root':str(output),'posture':'produced-uncommitted'}
        except BaseException:raise

def retained(output_root,expected_receipt_sha256):
    """Distinct later private reader; observations grant no live Session capability."""
    root=owned(Path(output_root),0o700);raw=read_private(root/'emission.json');need(sha(raw)==expected_receipt_sha256,'retained first-emitter receipt differs')
    receipt=json.loads(raw);carriers=carrier_validator();result=[]
    for row in receipt['outputs']:
        need(row['path']==row['artifact']['byte_sha256']+'.json','retained output locator differs')
        raw=read_private(root/row['path']);need(sha(raw)==row['sha256'],'retained formal bytes differ')
        carriers.output(row['artifact'],raw,scope_ref=receipt['scope_ref']);result.append((row['artifact'],raw))
    need(len(result)==3,'complete retained original agent-context output closure required');return result
