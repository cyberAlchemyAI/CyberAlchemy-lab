"""Independent private policy, nonce authentication, owned byte custody and locks."""
import base64,os,secrets,stat,fcntl,copy
from contextlib import contextmanager
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from .dependencies import *
class Refusal(ValueError):
 def __init__(self,code,message):self.code=code;self.message=message;super().__init__(message)
def need(v,code,message):
 if not v:raise Refusal(code,message)
def private(path,mode=0o600):
 path=Path(path);s=path.lstat();need(stat.S_ISREG(s.st_mode) and s.st_uid==os.getuid() and s.st_mode&0o777==mode,'integrity-failed','Independent owned private file permissions differ.')
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
 try:
  actual=os.fstat(fd);need((actual.st_dev,actual.st_ino)==(s.st_dev,s.st_ino),'integrity-failed','Owned input changed while opening.')
  need(actual.st_size<=16*1024*1024,'budget-exceeded','Owned original exceeds material bound.')
  with os.fdopen(fd,'rb',closefd=False) as stream:raw=stream.read(16*1024*1024+1)
 finally:os.close(fd)
 return raw
def directory(path):
 path=Path(path);s=path.lstat();need(stat.S_ISDIR(s.st_mode) and s.st_uid==os.getuid() and s.st_mode&0o777==0o700,'integrity-failed','Owned directory boundary differs.')
 return {'device':s.st_dev,'inode':s.st_ino}
def put(path,raw):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
 C.fsync_dir(path.parent)
def save(path,value):
 stage=path.with_name(path.name+'.governance-staging');put(stage,encoded(value));os.replace(stage,path);C.fsync_dir(path.parent)
POLICY_FIELDS={'schema_version','root_identity','principal_ref','reader_public_key_hex','scope_refs','not_before','expires_at','revoked','allowed_operations','max_calls','max_request_bytes','max_response_bytes','max_actions','store_identity','store_config_sha256','materials','review_selection','capability_selection','development_authorization_binding','authority_scope','authority_effect','actual_owner_outcome','claim_ceiling'}
def privacy(value):
 try:W.privacy(value)
 except Exception as error:raise Refusal('unauthorized','Private credential, key or Session memory material is outside this candidate/public boundary.') from error
 protected={'api_key','client_secret','private_key_hex','private_key_pem','raw_private_key','session_ram','ram_memory','runtime_memory','memory_dump','working_memory','short_term_memory'}
 if isinstance(value,dict):
  for key,item in value.items():
   need(not (key.lower() in protected and item not in (None,False,'',[],{})),'unauthorized','Private credential or runtime memory material is outside this candidate/public boundary.');privacy(item)
 elif isinstance(value,list):
  for item in value:privacy(item)
class GovernanceHost:
 def __init__(self,root,policy_sha256,schemas,source_sha256,profile_sha256,*,integration_profile_binding=None):
  self.root=Path(root);need(self.root.is_absolute() and self.root.is_relative_to('/tmp') and not self.root.is_symlink() and self.root.resolve()==self.root,'unauthorized','Independent isolated owned root required.')
  self.identity=directory(self.root);self.instance_ref='host:owned-governance:'+secrets.token_hex(24);self.policy_pin=policy_sha256;self.schemas=schemas;self.source_pin=source_sha256;self.profile_pin=profile_sha256;self.active_deadline=None
  self.policy_path=self.root/'operator-policy.json';self.policy=self.policy_guard()
  from .publisher import OwnedPublisher
  self.store=OwnedPublisher(self.root/'native-store',ROOT,self)
  self.profile_binding=binding((HERE/'contract-profile.json').relative_to(ROOT).as_posix(),(HERE/'contract-profile.json').read_bytes())
  need(self.profile_binding['sha256']==profile_sha256,'integrity-failed','Independent governance profile pin differs.')
  self.integration_profile_binding=copy.deepcopy(integration_profile_binding)
  if integration_profile_binding is not None:
   need(schemas.profile_binding==integration_profile_binding,'invalid-contract','Constructor-selected integration profile differs from actual shared Schemas profile.')
   path=ROOT/integration_profile_binding['ref'];need(path.is_relative_to(ROOT) and path.resolve()==path,'invalid-contract','Independent integration profile must select exact repository original bytes.')
   raw=path.read_bytes();profile=K.parse(raw)
   need(binding(integration_profile_binding['ref'],raw)==integration_profile_binding and set(OPERATIONS)<=set(profile['implemented_operations']),'invalid-contract','Independent integration profile bytes or declared governance operations differ.')
   original={r['operation']:r for r in K.parse((ROOT/'docs/proposals/0008-lab-api-contracts/api-contracts.json').read_bytes())['operations']}
   need(all(schemas.operations[n]==original[n] for n in OPERATIONS),'invalid-contract','Shared dispatcher changes exact original governance operation contracts.')
   self.profile_binding=copy.deepcopy(integration_profile_binding)
  for name in ('materials','objects','operations'):directory(self.root/name)
  self.lock=self.root/'governance.lock';private(self.lock);self.guard()
 def policy_guard(self):
  need(directory(self.root)==self.identity,'integrity-failed','Owned root identity changed.')
  raw=private(self.policy_path);need(sha(raw)==self.policy_pin,'integrity-failed','Private independently pinned operator policy changed.')
  p=parse(raw);need(set(p)==POLICY_FIELDS and p['schema_version']=='lab-owned-governance-policy/v1-candidate','unauthorized','Closed independently provisioned governance policy required.')
  need(p['root_identity']==self.identity and p['authority_scope']=='operator-local' and p['authority_effect']=='none' and p['actual_owner_outcome'] is None and p['scope_refs'] and len(p['scope_refs'])==1 and p['allowed_operations']==list(OPERATIONS),'unauthorized','Candidate local policy scope differs.')
  need(not p['revoked'],'revoked-authority','Independent operator policy is revoked.')
  need(instant(p['not_before'])<=now()<instant(p['expires_at']),'expired-authority','Independent operator authority is not current.')
  authority=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
  need(p['development_authorization_binding']==binding(authority.relative_to(ROOT).as_posix(),authority.read_bytes()),'unauthorized','Development authorization bytes differ.')
  need(directory(self.root/'native-store')==p['store_identity'] and sha((self.root/'native-store/config.json').read_bytes())==p['store_config_sha256'],'integrity-failed','Independently selected native store changed.')
  return p
 def guard(self):
  guard(self.source_pin);self.schemas.guard();p=self.policy_guard()
  need(sha((HERE/'contract-profile.json').read_bytes())==self.profile_pin,'integrity-failed','Governance profile changed.')
  if self.active_deadline is not None:need(now()<self.active_deadline,'deadline-exceeded','Strictest actual governance deadline expired.')
  need(p==self.policy,'integrity-failed','Independent policy selection changed.')
  if self.integration_profile_binding is not None:
   b=self.integration_profile_binding;need(binding(b['ref'],(ROOT/b['ref']).read_bytes())==b and self.schemas.profile_binding==b,'integrity-failed','Independent shared integration profile bytes or actual schema selection changed.')
  for row in p['materials']:self.material({'ref':row['ref'],'sha256':row['sha256']})
  return p
 def material(self,b):
  rows=[r for r in self.policy['materials'] if r['ref']==b['ref'] and r['sha256']==b['sha256']]
  if len(rows)==1:
   r=rows[0];need(set(r)=={'ref','sha256','filename'} and isinstance(r['sha256'],str) and len(r['sha256'])==64 and all(c in '0123456789abcdef' for c in r['sha256']) and r['filename']==r['sha256'],'integrity-failed','Closed owned material selection differs.')
   raw=private(self.root/'materials'/r['filename'])
  else:
   need(b['ref']=='governance-object:'+b['sha256'],'unresolved-reference','Original is outside independent material selection.')
   raw=private(self.root/'objects'/b['sha256'])
  need(sha(raw)==b['sha256'],'integrity-failed','Original owned bytes changed.');privacy(parse(raw));return raw
 def document(self,b):return parse(self.material(b))
 def object(self,raw):
  privacy(parse(raw))
  b=binding('governance-object:'+sha(raw),raw);p=self.root/'objects'/b['sha256']
  if not p.exists():
   if self.active_deadline is not None:need(now()<self.active_deadline,'deadline-exceeded','Actual deadline expired before candidate object effect.')
   put(p,raw)
  need(private(p)==raw,'integrity-failed','Immutable owned result bytes differ.');return b
 def snapshot(self):
  data=self.store.replay(require_current=True)
  need(data['config']['authority_boundary']=='operator-provisioned-local-store' and data['config']['repository_admission_effect']=='none' and data['config']['scope_ref']==self.policy['scope_refs'][0],'unauthorized','Native publisher is not the independently selected local candidate scope.')
  return data
 def cut(self,data=None):
  d=data or self.snapshot()
  return {'store_ref':d['config']['store_id'],'branch_ref':'branch:owned-governance:'+d['config']['store_id'],'commit_sequence':d['head']['sequence'],'commit_sha256':d['head']['transaction_digest'],'source_profile_sha256':sha((NATIVE/'profile.json').read_bytes()),'streams':[]}
 @contextmanager
 def locked(self):
  private(self.lock);fd=os.open(self.lock,os.O_RDWR|os.O_NOFOLLOW)
  try:fcntl.flock(fd,fcntl.LOCK_EX);yield
  finally:fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
class GovernanceChannel:
 def __init__(self,host):
  need(type(host) is GovernanceHost,'unauthorized','Actual independently selected governance host required.')
  self.host=host;self.policy=host.policy_guard();self.connection=secrets.token_hex(24);self.context=None;self.used=False;self.closed=False
  self.challenge={'schema_version':'lab-owned-governance-nonce/v1-candidate','nonce':secrets.token_hex(32),'connection_ref':self.connection,'policy_sha256':host.policy_pin,'source_sha256':host.source_pin,'contract_profile_binding':host.profile_binding,'profile_sha256':host.profile_binding['sha256'],'principal_ref':self.policy['principal_ref'],'expires_at':iso(min(now()+__import__('datetime').timedelta(seconds=60),instant(self.policy['expires_at'])))}
 def authenticate(self,proof):
  self.host.guard();raw_proof=proof if isinstance(proof,bytes) else encoded(proof);proof=parse(raw_proof);privacy(proof)
  need(self.host.policy_guard()==self.policy,'unauthorized','Independent governance policy changed before nonce verification.')
  need(not self.used and not self.closed and now()<instant(self.challenge['expires_at']),'unauthorized','Governance nonce is used, closed or expired.');self.used=True
  need(set(proof)=={'challenge','signature_base64'} and proof['challenge']==self.challenge,'unauthorized','Proof selects another independently scoped nonce.')
  Ed25519PublicKey.from_public_bytes(bytes.fromhex(self.policy['reader_public_key_hex'])).verify(base64.b64decode(proof['signature_base64'],validate=True),encoded(self.challenge))
  self.authentication_binding=self.host.object(raw_proof)
  self.context={'schema_version':'lab-trusted-call-context/v1-candidate','context_ref':'context:owned-governance:'+self.connection,'host_instance_ref':self.host.instance_ref,'connection_ref':self.connection,'principal_ref':self.policy['principal_ref'],'authority_scope':'operator-local','scope_refs':copy.deepcopy(self.policy['scope_refs']),'agent_instance_ref':None,'assignment_ref':None,'session_ref':None,'role_assignment_bindings':[],'source_profile_binding':binding((NATIVE/'profile.json').relative_to(ROOT).as_posix(),(NATIVE/'profile.json').read_bytes()),'authentication_evidence_binding':self.authentication_binding,'policy_bindings':[binding('owned-governance-policy:'+self.host.policy_pin,private(self.host.policy_path)),binding((HERE/'source-manifest.json').relative_to(ROOT).as_posix(),(HERE/'source-manifest.json').read_bytes())],'expires_at':self.policy['expires_at'],'limits':{'max_request_bytes':self.policy['max_request_bytes'],'max_response_bytes':self.policy['max_response_bytes'],'max_actions':self.policy['max_actions'],'deadline':self.policy['expires_at']},'origin':'verified-local-adapter','accept_client_supplied_authority_context':False,'private_credentials_in_context':False}
  need(self.host.schemas.valid('trusted-call-context',self.context),'invalid-contract','Actual local nonce-authenticated context violates original trusted-call-context schema.')
  privacy(self.context);self.expected_context=copy.deepcopy(self.context);return copy.deepcopy(self.context)
 def guard(self):
  need(self.context is not None and not self.closed,'unauthorized','Current nonce-authenticated governance channel required.');p=self.host.policy_guard();need(p==self.policy,'integrity-failed','Independent channel policy changed.')
  need(self.context==self.expected_context and self.host.schemas.valid('trusted-call-context',self.context),'unauthorized','Actual nonce-derived trusted context changed or violates its original contract.')
  need(self.host.document(self.authentication_binding)['challenge']==self.challenge,'integrity-failed','Original nonce authentication evidence changed.')
  privacy(self.context);return copy.deepcopy(self.context)
 def actor(self):
  c=self.guard();return {k:c[k] for k in ('principal_ref','agent_instance_ref','assignment_ref','session_ref')}|{'role_assignment_refs':c['role_assignment_bindings']}
 def close(self):self.closed=True
