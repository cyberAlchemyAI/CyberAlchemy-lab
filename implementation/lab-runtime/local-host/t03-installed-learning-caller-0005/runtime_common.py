"""Caller-owned observations over the selected installed common API."""
import copy,hashlib,importlib,importlib.util,json,os,stat,sys,tempfile,time,uuid
from datetime import datetime,timedelta,timezone
from pathlib import Path

def need(value,message):
 if not value:raise ValueError(message)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def load_file(path):
 name='_t03_owned_caller_'+uuid.uuid4().hex;spec=importlib.util.spec_from_file_location(name,path)
 module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module
def write(path,value):
 raw=value if type(value)is bytes else (json.dumps(value,sort_keys=True,indent=2)+'\n').encode()
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
 return {'path':str(path),'sha256':sha(raw)}

class Runtime:
 def __init__(self,evidence):
  self.provider=sys.modules.get('cal_installed_runtime_selection_v1')
  need(self.provider is not None,'selected installed launcher must activate the provider first')
  self.provider.require_runtime_ready();self.provider.guard();self.root=self.provider.root()
  self.evidence=Path(evidence)
  need(self.evidence.is_absolute() and not self.evidence.exists() and '..'not in self.evidence.parts,'fresh absolute private evidence root required')
  need(self.evidence.parent.is_dir() and not any(p.is_symlink() for p in self.evidence.parents),'unlinked evidence parent required')
  self.evidence.mkdir(mode=0o700);need(self.evidence.stat().st_uid==os.getuid() and stat.S_IMODE(self.evidence.stat().st_mode)==0o700,'owned private evidence root required')
  self.driver_bindings=[{'path':str(path),'sha256':sha(path.read_bytes())} for path in sorted(Path(__file__).resolve().parent.glob('*.py'))]
  write(self.evidence/'CALLER-SELECTION.json',{'caller_bindings':self.driver_bindings,'selected_by_public_runtime_package':False,'authority_effect':'none'})
  self.api_binding=self.provider.binding('api.source');self.profile_binding=self.provider.binding('api.profile')
  self.api=self.root/self.api_binding['path'];self.api=self.api.parent
  self.name='_t03_installed_'+uuid.uuid4().hex
  spec=importlib.util.spec_from_file_location(self.name,self.api/'__init__.py',submodule_search_locations=[str(self.api)])
  package=importlib.util.module_from_spec(spec);sys.modules[self.name]=package;spec.loader.exec_module(package)
  self.load=lambda leaf:importlib.import_module(self.name+'.'+leaf)
  self.P,self.F,self.S,self.H,self.A,self.MT,self.I=[self.load(x) for x in ('protocol','fixtures','service','handlers','auth','machine_transport','integration_dispatch')]
  self.load('guard').verify(self.api_binding['sha256']);self.schemas=self.P.Schemas(self.profile_binding['sha256']);self.schemas.guard()
  self.D=self.load('current_legacy_context_sessions').D;self.helpers=load_file(Path(__file__).with_name('provider.py'));self.M=self.helpers.modules(self.name)
  self.surfaces={};self.pairs=[];self.sequence=0
  lifetime=self.D.load(self.D.HERE/'lifetime-policy.json')
  need(lifetime['default_request_seconds']==lifetime['maximum_view_lifetime_seconds']==3600,'explicit new3600 fixture required')
  assessment=self.load('current_lesson_assessment').selected
  need(assessment.CEILING=='Exact recorded application outcome only; no general or causal effectiveness inferred.' and assessment.METHOD=='recorded-application-outcome/v1-candidate','selected recorded-outcome contract differs before expensive Source/Session startup')
  software_name='implementation/lab-runtime/local-host/t03-installed-learning-caller-0001/margin-software.json'
  software_row=[row for row in self.provider.current().package['members'] if row['path']==software_name]
  need(len(software_row)==1,'independently packaged software selection required before Source startup')
  raw=(self.root/software_name).read_bytes();need(sha(raw)==software_row[0]['sha256'],'software selection bytes differ')
  selected_source=json.loads((self.api/'source-manifest.json').read_bytes());selected_files={row['path']:row['sha256'] for row in selected_source['files']}
  for row in json.loads(raw)['files']:
   need(selected_files.get(row['path'])==row['sha256'] and sha((self.root/row['path']).read_bytes())==row['sha256'],'static software/profile input mismatch before Source or Session startup')
  self.event({'phase':'selected-installed-API','api_source_binding':self.api_binding,'profile_binding':self.profile_binding,'family_source_binding':self.provider.binding('family.source'),'actual_fixture_budget_seconds':3600})
 def event(self,value):
  fd=os.open(self.evidence/'events.jsonl',os.O_WRONLY|os.O_APPEND|os.O_CREAT|os.O_NOFOLLOW,0o600)
  with os.fdopen(fd,'w') as stream:stream.write(json.dumps({'at_utc':datetime.now(timezone.utc).isoformat(),**value},sort_keys=True)+'\n');stream.flush();os.fsync(stream.fileno())
 def stage(self,label,work):
  self.event({'phase':label,'state':'starting'});at=time.monotonic()
  try:result=work()
  except BaseException as error:self.event({'phase':label,'state':'failed','exception_class':type(error).__name__,'message':str(error)[:500],'elapsed_seconds':round(time.monotonic()-at,3)});raise
  self.event({'phase':label,'state':'passed','elapsed_seconds':round(time.monotonic()-at,3)});return result
 def workspace(self,label):
  need(type(label)is str and label.replace('-','').isalnum(),'closed private workspace label required')
  # Selected auth and Vault contracts require /tmp. mkdtemp has no automatic
  # destructor: actual journals and inputs remain until explicit retention-aware
  # cleanup, including after indeterminate execution or process failure.
  path=Path(tempfile.mkdtemp(prefix='cal-T03-retained-'+label+'-',dir='/tmp'));path.chmod(0o700);st=path.stat()
  write(self.evidence/(label+'-workspace.json'),{'root':str(path),'identity':[st.st_dev,st.st_ino,st.st_uid,stat.S_IMODE(st.st_mode)],'retained_on_failure':True,'automatic_deletion':False,'authority_effect':'none'})
  return path
 def journal(self,service):
  return {str(p.relative_to(service.vault.root)):sha(p.read_bytes()) for p in sorted((service.vault.root/'journal').rglob('*')) if p.is_file()}
 def vault_snapshot(self,service):
  result={}
  for path in sorted(service.vault.root.rglob('*')):
   need(not path.is_symlink(),'unexpected link in owned Vault observation')
   if path.is_file():
    st=path.stat();result[str(path.relative_to(service.vault.root))]={'sha256':sha(path.read_bytes()),'identity':[st.st_dev,st.st_ino,st.st_uid,stat.S_IMODE(st.st_mode),st.st_size,st.st_mtime_ns,st.st_ctime_ns]}
  return result
 def guard_caller(self):
  need(all(not Path(row['path']).is_symlink() and sha(Path(row['path']).read_bytes())==row['sha256'] for row in self.driver_bindings),'caller bytes changed during actual execution')
  self.provider.guard();return True
 def source_count(self,selected):
  count=len(selected.view.subjects)
  need(count==len(selected.view.data['projection']['subjects'])==619,'actual selected Source inventory differs from fresh26-record fixture')
  self.actual_subject_count=count
  self.event({'phase':'actual-signed-Source-subject-count','subject_count':count,'source_cut':selected.source_cut,'family_source_binding':self.provider.binding('family.source')})
  return count
 def closed_permission_negatives(self,parent):
  need(not parent.sessions.live,'permission negatives require actual closed parent Sessions')
  channel=parent.channel;original=channel.path.read_bytes();before=self.vault_snapshot(parent);changed=self.P.frame_parse(original);changed['revoked']=True;refused=False
  try:
   channel.path.write_bytes(self.P.compact(changed))
   try:channel.termination_guard()
   except ValueError as error:refused='revoked or changed' in str(error)
  finally:channel.path.write_bytes(original)
  need(refused and channel.path.read_bytes()==original,'changed-to-revoked selected grant was accepted')
  expired=self.P.frame_parse(original);expired['expires_at']=(self.A.now()-timedelta(seconds=1)).isoformat();raw=self.P.compact(expired);path=channel.path.parent/'expired-policy.json';write(path,raw);expiry_refused=False
  try:self.A.ReaderChannel(path,sha(raw),self.schemas)
  except ValueError as error:expiry_refused='reader policy expired' in str(error)
  need(expiry_refused,'actual-clock expired Reader policy was accepted')
  need(before==self.vault_snapshot(parent),'closed permission negatives changed owned Vault')
  result={'changed_to_revoked_selected_grant_refused':True,'actual_clock_expired_grant_refused':True,'whole_Vault_unchanged':True,'closed_parent_not_resurrected':True,'authority_effect':'none'}
  write(self.evidence/'PERMISSION-NEGATIVES.json',result);self.event({'phase':'same-cut-permission-negatives',**result});return result
 def call(self,service,operation,message,key=None,*,pair=True):
  request=self.helpers.call(self.M,service,operation,message,key=key,seconds=3600)
  surface=self.surfaces.get(id(service))
  if surface is None:surface=self.I.IntegrationService(service);self.surfaces[id(service)]=surface
  need(surface.base is service and surface.schemas is self.schemas,'common dispatcher must share the exact base and schema object')
  row=self.schemas.operations[operation]
  def validate_request(value):
   need(self.schemas.valid('api-call',value) and self.schemas.protocol_valid(row['request_schema']['resource_uri'],value['message']),'causal case must reach the actual valid request/domain schema')
  def validate_reply(value,raw):
   need(self.schemas.valid('api-reply',value) and value['request_binding']['sha256']==sha(raw) and value['contract_profile_binding']==self.schemas.profile_binding,'actual reply schema, request bytes or selected profile differs')
   need(self.schemas.protocol_valid(row['result_schema' if value['kind']=='result' else 'error_schema']['resource_uri'],value['message']),'actual result/error domain schema differs')
  validate_request(request)
  if pair and operation not in self.pairs:
   negative=copy.deepcopy(request);negative['call_id']='call:T03-negative:'+uuid.uuid4().hex
   actor=negative['message'].get('actor')
   if type(actor)is dict:actor['principal_ref']='principal:T03-foreign';cause='foreign-Actor'
   else:negative['caller_context_ref']='context:T03-foreign:'+uuid.uuid4().hex;cause='foreign-opaque-context'
   validate_request(negative);before=self.vault_snapshot(service);negative_raw=self.P.compact(negative);bad=surface.call(negative_raw)
   self.sequence+=1
   write(self.evidence/(str(self.sequence).zfill(3)+'-'+operation.replace('.','-')+'-negative-request.json'),negative_raw)
   write(self.evidence/(str(self.sequence).zfill(3)+'-'+operation.replace('.','-')+'-negative-reply.json'),self.P.compact(bad))
   validate_reply(bad,negative_raw)
   need(self.schemas.valid('api-reply',bad) and bad['kind']=='error' and bad['message']['code']=='unauthorized','causal common-dispatch negative did not refuse')
   need(before==self.vault_snapshot(service),'causal negative changed owned Vault')
   self.event({'phase':'common-dispatch-negative','operation':operation,'cause':cause,'journal_unchanged':True,'whole_Vault_unchanged':True,'request_sha256':sha(negative_raw),'reply_sha256':sha(self.P.compact(bad)),'request_and_domain_schema_valid':True,'request_SHA_and_profile_bound':True})
   self.pairs.append(operation)
  raw=self.P.compact(request);reply=surface.call(raw);self.sequence+=1
  write(self.evidence/(str(self.sequence).zfill(3)+'-'+operation.replace('.','-')+'-request.json'),raw)
  write(self.evidence/(str(self.sequence).zfill(3)+'-'+operation.replace('.','-')+'-reply.json'),self.P.compact(reply))
  self.event({'phase':'common-dispatch-call','operation':operation,'kind':reply.get('kind'),'code':reply.get('message',{}).get('code') if type(reply.get('message'))is dict else None,'request_sha256':sha(raw),'reply_sha256':sha(self.P.compact(reply))})
  validate_reply(reply,raw)
  need(reply.get('kind')=='result',operation+' refused; private workspace and exact reply retained')
  return reply['message']
 def capture_formal_session(self,host,sid):
  resource=host.sessions.live[sid]
  # These are the actual protocol Artifact bodies. session_memory here holds
  # selected view references only; no LiveReader.memory notes are accessed.
  body=copy.deepcopy(resource.session)
  need(set(body['payload']['session_memory'])=={'selected_input_refs','working_record_refs','unresolved_questions','expires_with_session'},'unexpected formal Session memory shape')
  need(body['payload']['session_memory']['working_record_refs']==[] and body['payload']['session_memory']['unresolved_questions']==[],'formal metadata must not include working notes')
  return write(self.evidence/'formal-session.json',{'session_ref':sid,'formal_session_body':body,'agent_record':copy.deepcopy(resource.agent),'classification_record':copy.deepcopy(resource.classification),'owned_custody_row':host.sessions.selected(sid),'source_cut':copy.deepcopy(resource.source.source_cut),'api_source_binding':self.api_binding,'family_source_binding':self.provider.binding('family.source'),'short_memory_exported':False,'authority_effect':'none'})
 def inspect_operation(self,service,operation,key,label):
  """Retain the actual pending/completed journal before resource cleanup."""
  try:
   request=self.F.call(service.channel.context,'operation.inspect',None,lookup={'operation':operation,'idempotency_key':key})
   surface=self.surfaces.get(id(service))
   if surface is None:surface=self.I.IntegrationService(service);self.surfaces[id(service)]=surface
   reply=surface.call(self.P.compact(request))
   write(self.evidence/(label+'-inspect-request.json'),self.P.compact(request))
   write(self.evidence/(label+'-inspect-reply.json'),self.P.compact(reply))
   write(self.evidence/(label+'-retained-journal.json'),{'operation':operation,'idempotency_key':key,'workspace_root':str(service.vault.root),'workspace_binding':service.vault.control_binding,'journal_files':self.journal(service),'workspace_retained':True,'authority_effect':'none'})
   self.event({'phase':'operation.inspect-retained','operation':operation,'reply_kind':reply.get('kind'),'workspace_retained':True})
   return reply
  except BaseException as error:
   write(self.evidence/(label+'-inspect-failure.json'),{'exception_class':type(error).__name__,'message':str(error),'workspace_root':str(service.vault.root),'journal_files':self.journal(service),'workspace_retained':True})
   self.event({'phase':'operation.inspect-retained','operation':operation,'inspection_refused':True,'workspace_retained':True})
   return {'kind':'inspection-refused','exception_class':type(error).__name__}
