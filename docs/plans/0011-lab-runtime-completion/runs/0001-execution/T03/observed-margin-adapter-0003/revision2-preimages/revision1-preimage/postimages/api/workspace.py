"""Owned exact material vault and durable private operation metadata, no Agent memory."""
from contextlib import contextmanager
import fcntl
import os
from pathlib import Path
import secrets
import re
from jsonschema import Draft202012Validator
from . import source_bridge as source
from . import jcs
HERE=Path(__file__).resolve().parent
MAX_MATERIAL=1024*1024

def safe(path,mode):
    path=Path(path)
    source.require(not path.is_symlink() and not any(p.is_symlink() for p in path.parents),'workspace symlink')
    st=path.stat();source.require(st.st_uid==os.getuid() and st.st_mode&0o777==mode,'workspace custody mode/owner')
    return path

def read_private(path):
    path=safe(path,0o600);source.require(path.is_file() and path.stat().st_size<=MAX_MATERIAL,'bounded regular private file required')
    return path.read_bytes()

def privacy(value):
    if isinstance(value,dict):
        for key,item in value.items():
            source.require(not (key.lower() in ('session_memory','short_memory','private_key','private_credentials','access_token','refresh_token','password','secret') and item not in (None,False,'',[],{})), 'private credential or Session memory material')
            privacy(item)
    elif isinstance(value,list):
        for item in value:privacy(item)
    elif isinstance(value,str):
        source.require(re.search(r'-----BEGIN(?: [A-Z0-9]+)* PRIVATE KEY-----',value) is None,'private key material')

def validate_scope(policy):
    row=policy['workspace'];root=Path(row['root'])
    source.require(root.is_absolute() and root.is_relative_to(Path('/tmp')) and not root.is_relative_to(source.ROOT)
        and root.as_posix()==row['root'] and '..' not in root.parts and root.resolve()==root,'independent owned temporary workspace required')
    safe(root,0o700);source.require(root.is_dir(),'workspace not directory')
    for name in ('inputs','objects','journal'):source.require(safe(root/name,0o700).is_dir(),'workspace directory missing')
    raw=read_private(root/'workspace.json');source.require(source.sha(raw)==row['manifest_sha256'],'workspace manifest differs')
    manifest=source.parse(raw);schema=source.parse((HERE/'workspace.schema.json').read_bytes())
    source.require(Draft202012Validator(schema).is_valid(manifest),'closed workspace manifest required')
    source.require(manifest['principal_ref']==policy['principal_ref'] and manifest['scope_refs']==policy['scope_refs'],'workspace principal/scope differs')
    refs=set();paths=set()
    for item in manifest['materials']:
        ref=item['ref'];relative=item['path'];path=Path(relative)
        source.require(ref not in refs and relative not in paths and path.parts[0]=='inputs'
            and not path.is_absolute() and '..' not in path.parts and path.as_posix()==relative and '\\' not in relative,'unsafe or duplicate workspace material')
        refs.add(ref);paths.add(relative)
        raw=read_private(root/path);source.require(source.sha(raw)==item['sha256'],'workspace material hash differs')
        privacy(source.parse(raw))
    actual={p.relative_to(root/'inputs').as_posix() for p in (root/'inputs').iterdir() if p.is_file()}
    source.require(all(not p.is_symlink() and p.is_file() for p in (root/'inputs').iterdir()) and actual=={str(Path(p).relative_to('inputs')) for p in paths},'closed flat input vault differs')
    allowed={'inputs','objects','journal','workspace.json','.lock'}
    if policy['schema_version']=='lab-local-ontology-projection-policy/v1-candidate':
        allowed.add('ontology');source.require(safe(root/'ontology',0o700).is_dir(),'selected owned ontology directory missing')
    if policy['schema_version']=='lab-local-workflow-transition-policy/v1-candidate':
        allowed.add('workflows');source.require(safe(root/'workflows',0o700).is_dir(),'selected workflow directory missing')
    if policy['schema_version']=='lab-local-export-candidate-policy/v1-candidate':
        allowed.add('exports')
        source.require(safe(root/'exports',0o700).is_dir(),'selected export directory missing')
    if policy['schema_version'] in ('lab-local-package-import-policy/v1-candidate','lab-local-package-export-policy/v1-candidate'):
        allowed.add('packages')
        source.require(safe(root/'packages',0o700).is_dir(),'selected package directory missing')
    source.require(set(p.name for p in root.iterdir())<=allowed,'unselected workspace entry')
    return root,manifest

def atomic(path,raw):
    from .integrated_guard import require_outside
    require_outside()
    """Publish complete bytes with no replacement; fsync file and directory."""
    path=Path(path);temporary=path.parent/('.stage-'+secrets.token_hex(16))
    fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    try:
        with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
        try:os.link(temporary,path,follow_symlinks=False)
        except FileExistsError:
            source.require(read_private(path)==raw,'immutable workspace object conflict')
        directory=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
        try:os.fsync(directory)
        finally:os.close(directory)
    finally:temporary.unlink(missing_ok=True)

class DeadlineBeforeClaim(ValueError):
    """The guarded lock was acquired after the effect deadline; nothing was written."""

class Vault:
    def __init__(self,channel):
        self.channel=channel;self.root,self.manifest=validate_scope(channel.policy)
        self.inputs={b['ref']:b for b in self.manifest['materials']}
    @property
    def control_binding(self):
        return {'ref':'workspace:'+self.manifest['workspace_ref'],'sha256':self.channel.policy['workspace']['manifest_sha256']}
    def guard(self):
        self.channel.guard();root,manifest=validate_scope(self.channel.policy)
        source.require(root==self.root and manifest==self.manifest,'workspace selection changed')
    def material(self,b):
        source.require(set(b)=={'ref','sha256'},'closed material binding')
        if self.channel.policy['schema_version'] in ('lab-local-package-import-policy/v1-candidate','lab-local-package-export-policy/v1-candidate') and b['ref'].startswith('workspace-object:'):
            raw=self.object_read(b);privacy(source.parse(raw));return raw
        selected=self.inputs.get(b['ref']);source.require(selected is not None and selected['sha256']==b['sha256'],'unselected input material')
        raw=read_private(self.root/selected['path']);source.require(source.sha(raw)==b['sha256'],'material changed');privacy(source.parse(raw));return raw
    def object(self,raw):
        source.require(len(raw)<=MAX_MATERIAL,'candidate evidence too large');privacy(source.parse(raw))
        digest=source.sha(raw);atomic(self.root/'objects'/(digest+'.json'),raw)
        return {'ref':'workspace-object:'+self.manifest['workspace_ref']+':'+digest,'sha256':digest}
    def object_read(self,b):
        source.require(b['ref']=='workspace-object:'+self.manifest['workspace_ref']+':'+b['sha256'],'object namespace differs')
        raw=read_private(self.root/'objects'/(b['sha256']+'.json'));source.require(source.sha(raw)==b['sha256'],'evidence object differs');return raw
    @contextmanager
    def lock(self,*,create=True):
        self.guard()
        flags=(os.O_RDWR|os.O_CREAT) if create else os.O_RDONLY
        fd=os.open(self.root/'.lock',flags|os.O_NOFOLLOW,0o600)
        try:
            safe(self.root/'.lock',0o600);fcntl.flock(fd,fcntl.LOCK_EX);self.guard();yield
        finally:fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
    def state(self,ns):
        allocated=self.root/'journal'/(ns+'.allocated.json')
        if not allocated.exists():
            source.require(not (self.root/'journal'/(ns+'.claim.json')).exists() and not (self.root/'journal'/(ns+'.result.json')).exists(),'orphan journal requires reconciliation')
            return None,None
        allocation=source.parse(read_private(allocated));claimpath=self.root/'journal'/(ns+'.claim.json')
        if not claimpath.exists():return allocation,None
        raw=read_private(claimpath);source.require(source.sha(raw)==allocation['claim_sha256'],'operation claim bytes differ')
        claim=source.parse(raw);resultpath=self.root/'journal'/(ns+'.result.json')
        source.require(claim['namespace']==ns,'operation claim namespace differs')
        original=self.object_read(claim['original_call_material_binding'])
        source.require(source.sha(original)==claim['original_call_binding']['sha256']
            and source.parse(original)['operation']==claim['operation'],'original operation wire material differs')
        if not resultpath.exists():return claim,None
        result=source.parse(read_private(resultpath));source.require(set(result)=={'claim_sha256','domain_binding','posture','evidence_bindings'} and result['claim_sha256']==source.sha(raw)
            and result['posture'] in ('completed','failed'),'result/claim closure differs')
        self.object_read(result['domain_binding'])
        for b in result['evidence_bindings']:self.object_read(b)
        return claim,result
    def claim(self,call,raw,context,*,deadline=None):
        ns=jcs.namespace(call['operation'],call['idempotency_key'],context);fp=jcs.fingerprint(call,context)
        with self.lock():
            prior,result=self.state(ns)
            if prior is not None:
                source.require(prior['principal_ref']==context['principal_ref'] and prior['namespace']==ns,'journal owner differs')
                return ns,fp,prior,result,False
            source.require(len(list((self.root/'journal').glob('*.allocated.json')))<self.channel.policy['workspace']['max_actions'],'workspace action budget exhausted')
            if deadline is not None:
                from .auth import now
                if now()>=deadline:raise DeadlineBeforeClaim('Effect deadline expired during guarded journal-lock acquisition')
            if call['operation'] in ('lesson.apply','lesson.assess'):
                from .observed_margin import before_claim,RuntimeBinding,MarginBeforeClaim
                runtime=getattr(self,'observed_margin_runtime',None)
                if type(runtime) is not RuntimeBinding:raise MarginBeforeClaim('closure-missing')
                runtime.check_entry(before_claim)
                before_claim(self,call,context,deadline)
            original=self.object(raw)
            claim={'schema_version':'lab-private-operation-claim/v1-candidate','namespace':ns,'fingerprint':fp,
                'principal_ref':context['principal_ref'],'operation':call['operation'],
                'original_call_binding':{'ref':'call:'+context['connection_ref']+':'+call['call_id'],'sha256':source.sha(raw)},
                'original_call_material_binding':original,
                'authority_effect':'none','actual_owner_outcome':None}
            claimraw=source.encoded(claim)
            allocation={**claim,'claim_sha256':source.sha(claimraw)}
            atomic(self.root/'journal'/(ns+'.allocated.json'),source.encoded(allocation))
            atomic(self.root/'journal'/(ns+'.claim.json'),claimraw)
            return ns,fp,claim,None,True
    def finish(self,ns,domain,evidence,posture='completed'):
        resultbinding=self.object(source.encoded(domain))
        with self.lock():
            claim,old=self.state(ns);source.require(claim is not None and old is None,'operation result already recorded')
            raw=read_private(self.root/'journal'/(ns+'.claim.json'))
            result={'claim_sha256':source.sha(raw),'domain_binding':resultbinding,'posture':posture,'evidence_bindings':evidence}
            atomic(self.root/'journal'/(ns+'.result.json'),source.encoded(result))
        return resultbinding
    def record_pending_evidence(self,ns,evidence):
        # Evidence is an observation, never a completion or permission to retry.
        source.require(type(evidence) is list and 0<len(evidence)<=128,'bounded pending verification evidence required')
        with self.lock():
            claim,result=self.state(ns)
            source.require(claim is not None and result is None
                and claim['principal_ref']==self.channel.context['principal_ref'], 'pending operation owner or state differs')
            for item in evidence:
                source.require(type(item) is dict and set(item)=={'ref','sha256'}
                    and type(item['ref']) is str and type(item['sha256']) is str
                    and re.fullmatch('[0-9a-f]{64}',item['sha256']) is not None,'closed pending evidence binding required')
                self.object_read(item)
            claimraw=read_private(self.root/'journal'/(ns+'.claim.json'))
            row={'schema_version':'lab-private-pending-evidence/v1-candidate',
                 'claim_sha256':source.sha(claimraw),'evidence_bindings':evidence,'authority_effect':'none'}
            atomic(self.root/'journal'/(ns+'.pending-evidence.json'),source.encoded(row))
    def pending_evidence(self,ns):
        with self.lock():
            claim,result=self.state(ns)
            source.require(claim is not None and result is None
                and claim['principal_ref']==self.channel.context['principal_ref'],'pending operation owner or state differs')
            path=self.root/'journal'/(ns+'.pending-evidence.json')
            if not path.exists():return []
            row=source.parse(read_private(path))
            claimraw=read_private(self.root/'journal'/(ns+'.claim.json'))
            source.require(type(row) is dict and set(row)=={'schema_version','claim_sha256','evidence_bindings','authority_effect'}
                and row['schema_version']=='lab-private-pending-evidence/v1-candidate'
                and row['claim_sha256']==source.sha(claimraw) and row['authority_effect']=='none'
                and type(row['evidence_bindings']) is list and 0<len(row['evidence_bindings'])<=128,'pending evidence claim binding differs')
            for item in row['evidence_bindings']:
                source.require(type(item) is dict and set(item)=={'ref','sha256'}
                    and type(item['ref']) is str and type(item['sha256']) is str
                    and re.fullmatch('[0-9a-f]{64}',item['sha256']) is not None,'closed pending evidence binding required')
                self.object_read(item)
            return row['evidence_bindings']
    def lookup(self,lookup,context):
        # An empty journal is a valid read observation. Its first durable lock
        # is created only by claim(), after public preflight succeeds. A later
        # claim rechecks the fingerprint under the exclusive writer lock.
        self.guard()
        if not (self.root/'.lock').exists():
            durable=('.allocated.json','.claim.json','.result.json','.pending-evidence.json')
            source.require(not any(p.name.endswith(durable) for p in (self.root/'journal').iterdir()),
                'durable journal without its lock requires reconciliation')
            self.guard()
            return None,None
        # Never recreate a removed lock while inspecting an existing journal.
        with self.lock(create=False):
            if 'operation' in lookup:
                ns=jcs.namespace(lookup['operation'],lookup['idempotency_key'],context)
                claim,result=self.state(ns)
            else:
                rows=[]
                for path in (self.root/'journal').glob('*.allocated.json'):
                    claim,result=self.state(path.name.removesuffix('.allocated.json'))
                    if claim['principal_ref']==context['principal_ref'] and claim['original_call_binding']==lookup['call_binding']:rows.append((claim,result))
                source.require(len(rows)<=1,'ambiguous operation lookup');claim,result=rows[0] if rows else (None,None)
            if claim is not None:source.require(claim['principal_ref']==context['principal_ref'],'operation owner differs')
            return claim,result
