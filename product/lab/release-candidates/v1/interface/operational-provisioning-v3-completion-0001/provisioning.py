"""T34 versioned constrained locator and provisioning intent controller.

No governing RoleAssignment is constructed. Operational execution requires a
separate T28 adapter; this module only executes independently selected candidate
rehearsals and mandatory original-engine preflight.
"""
import fcntl
from contextlib import contextmanager
import tempfile
import sys
import capture_io
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import secrets
import stat
import subprocess
import time
import traceback
import uuid
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

ROOT = Path(__file__).resolve().parents[6]
ORIGINAL = ROOT/'product/lab/release-candidates/v1/interface/custody-correction-v4'

def require(value, message):
    if not value: raise ValueError(message)

def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()

def sha(raw): return hashlib.sha256(raw).hexdigest()

def parse(raw):
    def pairs(rows):
        result={}
        for key,value in rows:
            require(key not in result, 'duplicate JSON key'); result[key]=value
        return result
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda _:require(False,'nonfinite JSON'))

def identity(st): return [st.st_dev,st.st_ino,st.st_uid,stat.S_IMODE(st.st_mode)]

def preimage(st):return [*identity(st),st.st_size,st.st_mtime_ns,st.st_ctime_ns]

class Directory:
    """Walk absolute locators with openat/O_NOFOLLOW; retain the selected inode."""
    def __init__(self, path, selected):
        self.path=Path(path); self.selected=selected
        require(self.path.is_absolute() and str(self.path)==os.path.normpath(str(self.path)), 'canonical absolute locator required')
        require(not self.path.is_relative_to(ROOT), 'private or staging locator inside repository')
        fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY)
        try:
            for part in self.path.parts[1:]:
                new=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);os.close(fd);fd=new
            require(identity(os.fstat(fd))==selected and selected[2:]==[os.getuid(),0o700], 'directory custody differs')
            self.fd=fd
        except BaseException: os.close(fd);raise
    def guard(self):
        require(identity(os.fstat(self.fd))==self.selected,'retained directory changed')
        other=Directory(self.path,self.selected)
        os.close(other.fd)
    def close(self): os.close(self.fd)
    def names(self): self.guard();return set(os.listdir(self.fd))
    def absent(self,name):
        require('/' not in name and name not in {'.','..'},'flat locator required')
        try: os.stat(name,dir_fd=self.fd,follow_symlinks=False)
        except FileNotFoundError: return
        raise ValueError('selected absent preimage is occupied: '+name)
    def read(self,name,pin=None,limit=65536):
        require('/' not in name and name not in {'.','..'},'flat locator required');self.guard()
        fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=self.fd)
        try:
            before=os.fstat(fd)
            require(stat.S_ISREG(before.st_mode) and before.st_uid==os.getuid() and stat.S_IMODE(before.st_mode)==0o600 and before.st_size<=limit,'protected file mode/type/size/UID differs')
            require(pin is None or identity(before)==pin['identity'],'protected file preimage differs')
            raw=b''
            while True:
                chunk=os.read(fd,limit+1-len(raw))
                if not chunk:break
                raw+=chunk;require(len(raw)<=limit,'protected file too large')
            after=os.fstat(fd)
            require(preimage(before)==preimage(after)==preimage(os.stat(name,dir_fd=self.fd,follow_symlinks=False)),'protected file changed during read')
            require(pin is None or sha(raw)==pin['sha256'],'protected file digest differs')
        finally:os.close(fd)
        self.guard();return raw
    def create(self,name,raw):
        self.guard();self.absent(name)
        fd=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=self.fd)
        try:
            os.fchmod(fd,0o600)
            with os.fdopen(fd,'wb',closefd=False) as out:out.write(raw);out.flush();os.fsync(fd)
        finally:os.close(fd)
        os.fsync(self.fd);self.guard()

PLAN_FIELDS=set('schema_version purpose operator_ref principal_ref scope_ref store_id target_parent target_parent_identity target_name target_preimage custody_path custody_identity policy_pin key_pin public_key policy_ref channel_state channel_state_identity source_bindings engine_pins base_repository_head categories effects rollback'.split())

def source_guard(plan):
    rows=plan['source_bindings'];require(rows and len({r['path'] for r in rows})==len(rows),'independent exact source closure required')
    for row in rows:
        require(set(row)=={'path','sha256'},'closed source binding required')
        path=ROOT/row['path']
        require(not Path(row['path']).is_absolute() and '..' not in Path(row['path']).parts and path.is_relative_to(ROOT),'unsafe selected source locator')
        capture_io.capture(path,row['sha256'])
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    require(head==plan['base_repository_head'],'repository base HEAD changed')

class Controller:
    def __init__(self,plan,independent_plan_sha):
        require(sha(encoded(plan))==independent_plan_sha,'independent plan pin differs')
        require(set(plan)==PLAN_FIELDS and plan['schema_version']=='lab-operational-provisioning-plan/v1-candidate','closed versioned plan required')
        require(plan['purpose'] in {'owned-candidate-rehearsal','prospective-operation'},'unknown purpose')
        require(plan['principal_ref'].startswith('principal:') and plan['operator_ref'].startswith('role:'),'explicit principal/operator required')
        require(plan['purpose']!='owned-candidate-rehearsal' or plan['operator_ref'].startswith('role:candidate-'),'technical rehearsal operator must remain candidate-labelled')
        require(plan['scope_ref']=='scope:lab-runtime-local:'+plan['store_id'] and plan['store_id'].replace('-','').isalnum(),'exact executable scope required')
        require(plan['categories']==['artifact-instance'] and plan['effects']==['admit'],'unsupported executable effects')
        require(plan['target_preimage']=='absent' and plan['target_name'] not in {'','.', '..'} and '/' not in plan['target_name'],'new target preimage required')
        require(plan['rollback']=={'selection':'retain-all-prior-state','delete_prior':False,'reuse_prior_permissions':False},'rollback retention required')
        require(len({plan['target_parent'],plan['custody_path'],plan['channel_state']})==3,'separate target/custody/channel roots required')
        self.plan=parse(encoded(plan));self.pin=independent_plan_sha
        self.target=Directory(plan['target_parent'],plan['target_parent_identity'])
        try:
            self.custody=Directory(plan['custody_path'],plan['custody_identity'])
            self.state=Directory(plan['channel_state'],plan['channel_state_identity'])
            self.ensure_lock()
            self.guard()
        except BaseException:
            self.target.close()
            for name in ['custody','state']:
                if hasattr(self,name):getattr(self,name).close()
            raise
    def close(self):
        for name in ['target','custody','state']:getattr(self,name).close()
    def guard(self):
        require(sha(encoded(self.plan))==self.pin,'plan changed in memory');source_guard(self.plan)
        for directory in [self.target,self.custody,self.state]:directory.guard()
        require(self.custody.names()=={'candidate.pem','policy.json'},'unknown or revoked custody entry')
        self.custody.read('candidate.pem',self.plan['key_pin'])
        self.custody.read('policy.json',self.plan['policy_pin'])
        policy=parse(self.custody.read('policy.json',self.plan['policy_pin']))
        expected={'schema_version':'lab-durable-channel-policy/v1-candidate','authority_effect':'none','purpose':'owned-candidate-rehearsal','principal_ref':self.plan['principal_ref'],'operator_ref':self.plan['operator_ref'],'scope_ref':self.plan['scope_ref'],'public_key':self.plan['public_key'],'policy_ref':self.plan['policy_ref'],'plan_source_sha256':sha(encoded(self.plan['source_bindings']))}
        require(set(policy)==set(expected)|{'not_before','expires_at','revoked'},'closed channel policy required')
        require(all(policy[k]==v for k,v in expected.items()),'policy selection differs')
        now=time.time();require(type(policy['revoked']) is bool and not policy['revoked'] and type(policy['not_before']) in {int,float} and type(policy['expires_at']) in {int,float} and policy['not_before']<=now<policy['expires_at'],'policy expired/not current/revoked')
        for name in self.state.names():
            if name=='controller-lock':
                require(self.state.read(name)==b'lab-T34-controller-lock/v2-candidate\n','foreign controller lock')
                require(identity(os.stat(name,dir_fd=self.state.fd,follow_symlinks=False))==self.lock_identity,'controller lock attachment changed')
                if hasattr(self,'active_lock'):
                    require(identity(os.fstat(self.active_lock))==self.lock_identity,'active controller lock changed')
                continue
            require('-' in name,'unknown channel state entry');kind,identifier=name.split('-',1)
            require(kind in {'challenge','consumed','intent','result'} and identifier.isalnum(),'unknown channel state entry')
            value=parse(self.state.read(name))
            if kind=='challenge':
                require(set(value)==set('schema_version host_instance_ref connection_ref nonce plan_sha256 policy_sha256 expires_at authority_effect'.split()) and value['schema_version']=='lab-durable-channel-challenge/v1-candidate' and value['plan_sha256']==self.pin and sha(encoded(value))==identifier,'unrecognized challenge evidence')
            elif kind=='consumed':
                require(value=={'challenge_sha256':identifier,'plan_sha256':self.pin,'authority_effect':'none'} and 'challenge-'+identifier in self.state.names(),'unrecognized consumption evidence')
            elif kind=='intent':
                require(value=={'schema_version':'lab-provisioning-intent/v1-candidate','plan_sha256':self.pin,'operation_id':identifier,'principal_ref':self.plan['principal_ref'],'scope_ref':self.plan['scope_ref'],'authority_effect':'none','target_preimage':'absent','store_created':False},'unrecognized provisioning intent')
            else:
                require('intent-'+identifier in self.state.names() and value.get('intent_sha256')==sha(self.state.read('intent-'+identifier)) and value.get('authority_effect')=='none' and type(value.get('store_created')) is bool and value.get('status') in {'original-preflight-refused','original-candidate-genesis-committed'},'unrecognized provisioning result')
        committed=[parse(self.state.read(name)) for name in self.state.names() if name.startswith('result-') and parse(self.state.read(name)).get('status')=='original-candidate-genesis-committed']
        require(not committed or self.plan['target_name'] in self.target.names(),'recorded committed target is missing')
        if self.plan['target_name'] in self.target.names():
            require(len(committed)==1,'target exists without exact durable completed construction evidence; retain uncertain state')
            self.verify_target(committed[0]['store_pins'])
        return policy
    def verify_target(self,pins):
        target=Directory(self.target.path/self.plan['target_name'],pins['identity'])
        try:
            require(target.names()=={'config.json','baseline.json','HEAD.json','transactions'},'unexpected store residue')
            for name in ['config.json','baseline.json','HEAD.json']:
                target.read(name,pins['files'][name],128*1024*1024)
            tx=Directory(target.path/'transactions',pins['transactions_identity'])
            try:
                require(tx.names()=={'0000000000.json'},'unexpected genesis transaction closure')
                tx.read('0000000000.json',pins['files']['transactions/0000000000.json'])
            finally:tx.close()
            require(parse(target.read('HEAD.json'))['transaction_digest']==pins['expected_head'],'independent genesis HEAD differs')
        finally:target.close()
    def ensure_lock(self):
        if 'controller-lock' not in self.state.names():
            try: self.state.create('controller-lock',b'lab-T34-controller-lock/v2-candidate\n')
            except (FileExistsError,ValueError):
                require('controller-lock' in self.state.names(),'controller lock publication failed')
        require(self.state.read('controller-lock')==b'lab-T34-controller-lock/v2-candidate\n','foreign controller lock')
        self.lock_identity=identity(os.stat('controller-lock',dir_fd=self.state.fd,follow_symlinks=False))
    @contextmanager
    def locked(self):
        self.state.guard()
        fd=os.open('controller-lock',os.O_RDWR|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=self.state.fd)
        try:
            before=os.fstat(fd)
            require(stat.S_ISREG(before.st_mode) and before.st_uid==os.getuid() and stat.S_IMODE(before.st_mode)==0o600,'unsafe controller lock')
            try: fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError: raise ValueError('controller operation already in progress')
            require(identity(before)==self.lock_identity==identity(os.stat('controller-lock',dir_fd=self.state.fd,follow_symlinks=False)),'controller lock detached')
            self.active_lock=fd
            self.state.guard()
            yield
            require(identity(before)==identity(os.fstat(fd))==identity(os.stat('controller-lock',dir_fd=self.state.fd,follow_symlinks=False)),'controller lock changed during operation')
            self.state.guard()
        finally:
            if getattr(self,'active_lock',None)==fd:del self.active_lock
            os.close(fd)
    def original_engine(self):
        from engine_capture import selected_engine
        return selected_engine(self.plan)
    @contextmanager
    def captured_target(self,pins=None):
        # Open the child relative to the retained selected parent, never a
        # replacement absolute parent. Directory objects also recheck ancestry.
        self.target.guard()
        child=os.open(self.plan['target_name'],os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=self.target.fd)
        tx=None
        try:
            selected=identity(os.fstat(child)); tx=os.open('transactions',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=child)
            tx_selected=identity(os.fstat(tx))
            require(selected[2:]==tx_selected[2:]==[os.getuid(),0o700],'store directory custody differs')
            require(set(os.listdir(child))=={'config.json','baseline.json','HEAD.json','transactions'} and set(os.listdir(tx))=={'0000000000.json'},'store closure differs')
            raw={}; files={}
            for name in ['config.json','baseline.json','HEAD.json','transactions/0000000000.json']:
                parent,leaf=(tx,'0000000000.json') if '/' in name else (child,name)
                fd=os.open(leaf,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=parent)
                try:
                    before=os.fstat(fd);require(stat.S_ISREG(before.st_mode) and before.st_uid==os.getuid() and stat.S_IMODE(before.st_mode)==0o600 and before.st_size<=128*1024*1024,'store file custody differs')
                    blocks=[];total=0
                    while block:=os.read(fd,1024*1024):
                        blocks.append(block);total+=len(block);require(total<=128*1024*1024,'store file exceeds bound')
                    raw[name]=b''.join(blocks)
                    require(preimage(before)==preimage(os.fstat(fd))==preimage(os.stat(leaf,dir_fd=parent,follow_symlinks=False)),'store file changed while captured')
                    files[name]={'identity':identity(before),'sha256':sha(raw[name])}
                finally:os.close(fd)
            baseline=parse(raw['baseline.json']);head=parse(raw['HEAD.json'])
            actual={'identity':selected,'transactions_identity':tx_selected,'files':files,'baseline_snapshot_digest':baseline['snapshot_digest'],'expected_head':head['transaction_digest']}
            require(pins is None or pins==actual,'independent captured store pin differs')
            self.target.guard();require(selected==identity(os.stat(self.plan['target_name'],dir_fd=self.target.fd,follow_symlinks=False)),'store root detached')
            with tempfile.TemporaryDirectory(prefix='cal-T34-exact-replay-') as staging:
                snapshot=Path(staging)/'store';snapshot.mkdir(mode=0o700);(snapshot/'transactions').mkdir(mode=0o700)
                for name,blob in raw.items():
                    fd=os.open(snapshot/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
                    with os.fdopen(fd,'wb') as out:out.write(blob)
                yield actual,snapshot
                for name,d in files.items():
                    parent,leaf=(tx,'0000000000.json') if '/' in name else (child,name)
                    fd=os.open(leaf,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=parent)
                    try:
                        before=os.fstat(fd);require(identity(before)==d['identity'] and stat.S_ISREG(before.st_mode),'store file detached after replay')
                        h=hashlib.sha256();total=0
                        while block:=os.read(fd,1024*1024):
                            total+=len(block);require(total<=128*1024*1024,'store file too large after replay');h.update(block)
                        require(preimage(before)==preimage(os.fstat(fd))==preimage(os.stat(leaf,dir_fd=parent,follow_symlinks=False)) and h.hexdigest()==d['sha256'],'store bytes changed during snapshot replay')
                    finally:os.close(fd)
                self.target.guard();require(selected==identity(os.stat(self.plan['target_name'],dir_fd=self.target.fd,follow_symlinks=False)) and tx_selected==identity(os.stat('transactions',dir_fd=child,follow_symlinks=False)),'store directories detached after replay')
        finally:
            if tx is not None:os.close(tx)
            os.close(child)
    def channel(self):return Channel(self)
    def preflight_original(self):
        self.guard()
        loader,selected=self.original_engine();pins=loader.EnginePins(**self.plan['engine_pins'])
        with selected as engine:
            profile=loader.parse(loader.original(engine.manifest['profile_binding']))
            # Full original physical capture: no replaced locator, reduced profile,
            # synthetic baseline, source-proof suppression or selected-row fallback.
            result=engine.sources.capture(ROOT,profile)
            engine.guard()
        self.guard();return {'snapshot_digest':result['snapshot_digest'],'profile_sha256':pins.profile_sha256}
    def reconcile(self,operation_id,independent_result_sha=None):
        with self.locked(): return self._reconcile(operation_id,independent_result_sha)
    def _reconcile(self,operation_id,independent_result_sha=None):
        self.guard();require(operation_id.isalnum(),'operation identifier required')
        intent=parse(self.state.read('intent-'+operation_id));require(intent['plan_sha256']==self.pin,'intent belongs to another selection')
        if 'result-'+operation_id not in self.state.names():return {'status':'uncertain-retain-no-redispatch','intent_sha256':sha(encoded(intent)),'store_created':False}
        result=parse(self.state.read('result-'+operation_id));require(result['intent_sha256']==sha(encoded(intent)),'result does not bind intent')
        require(independent_result_sha is not None and sha(encoded(result))==independent_result_sha,'independent durable result pin required for completed reconciliation')
        if result['store_created']:
            loader,selected=self.original_engine()
            with selected as engine:
                pins=result['store_pins']
                with self.captured_target(pins) as (_,snapshot):
                    engine.replay_owned(snapshot,pins['files']['config.json']['sha256'],pins['baseline_snapshot_digest'],pins['expected_head'])
                engine.guard()
            self.guard()
        return result
    def rehearsal(self,channel,operation_id):
        with self.locked(): return self._rehearsal(channel,operation_id)
    def _rehearsal(self,channel,operation_id):
        require(self.plan['purpose']=='owned-candidate-rehearsal','T28 governing authority adapter is not implemented/selected')
        channel.guard();require(operation_id.isalnum(),'operation identifier required')
        self.target.absent(self.plan['target_name'])
        intent={'schema_version':'lab-provisioning-intent/v1-candidate','plan_sha256':self.pin,'operation_id':operation_id,'principal_ref':self.plan['principal_ref'],'scope_ref':self.plan['scope_ref'],'authority_effect':'none','target_preimage':'absent','store_created':False}
        self.state.create('intent-'+operation_id,encoded(intent));channel.guard()
        try:
            original=self.preflight_original()
            channel.guard();loader,selected=self.original_engine()
            # The original Store owns its real genesis HEAD commit point. If it
            # or our post-check is interrupted, retain exact intent and target;
            # this successor never automatically redispatches initialization.
            with selected as engine:
                profile=loader.parse(loader.original(engine.manifest['profile_binding']))
                target=self.target.path/self.plan['target_name'];self.target.absent(self.plan['target_name'])
                old_mask=os.umask(0o077)
                try:
                    store=engine.store_module.Store(target,ROOT)
                    self.target.guard();self.target.absent(self.plan['target_name'])
                    # Explicit constrained locator adapter: the original Store
                    # constructor resolves its initial path; bind subsequent
                    # original writes to the independently retained parent inode.
                    store.path=Path('/proc/self/fd')/str(self.target.fd)/self.plan['target_name']
                    store.initialize(profile,self.plan['store_id'],self.plan['operator_ref'],self.plan['public_key'],self.plan['categories'],self.plan['effects'])
                finally:os.umask(old_mask)
                with self.captured_target() as (pins,snapshot):
                    replay=engine.replay_owned(snapshot,pins['files']['config.json']['sha256'],pins['baseline_snapshot_digest'],pins['expected_head'])
                source_guard(self.plan);require(self.custody.names()=={'candidate.pem','policy.json'},'custody revoked during construction');self.custody.read('policy.json',self.plan['policy_pin']);self.custody.read('candidate.pem',self.plan['key_pin']);self.target.guard();self.state.guard();engine.guard()
                require(time.time()<channel.challenge['expires_at'],'channel expired during construction')
                result={'status':'original-candidate-genesis-committed','original':original,'store_pins':pins,'replay_freshness':replay['freshness']['status']}
        except Exception as error:
            require(self.plan['target_name'] not in self.target.names(),'construction uncertain after target effect; retain intent/target without result or redispatch')
            result={'status':'original-preflight-refused','error_type':type(error).__name__,'error':str(error),'source_frames':[{'file':f.filename,'line':f.lineno,'function':f.name} for f in traceback.extract_tb(error.__traceback__)]}
        result.update(intent_sha256=sha(encoded(intent)),authority_effect='none',store_created=result['status']=='original-candidate-genesis-committed')
        # Full guard recognizes the target only after the exact durable result.
        # Check protected authority and provenance before publishing that record.
        require(sha(encoded(self.plan))==self.pin,'plan changed during construction');source_guard(self.plan);require(self.custody.names()=={'candidate.pem','policy.json'},'custody revoked before durable result');self.custody.read('policy.json',self.plan['policy_pin']);self.custody.read('candidate.pem',self.plan['key_pin']);self.target.guard();self.state.guard()
        require(time.time()<channel.challenge['expires_at'],'channel expired before durable result')
        require(identity(os.stat('controller-lock',dir_fd=self.state.fd,follow_symlinks=False))==self.lock_identity==identity(os.fstat(self.active_lock)),'controller lock replaced before durable result')
        self.state.create('result-'+operation_id,encoded(result));channel.guard();return result

class Channel:
    def __init__(self,controller):
        self.controller=controller;policy=controller.guard();self.used=False;self.authenticated=False;self.closed=False
        self.challenge={'schema_version':'lab-durable-channel-challenge/v1-candidate','host_instance_ref':uuid.uuid4().hex,'connection_ref':uuid.uuid4().hex,'nonce':secrets.token_hex(32),'plan_sha256':controller.pin,'policy_sha256':controller.plan['policy_pin']['sha256'],'expires_at':min(policy['expires_at'],time.time()+120),'authority_effect':'none'}
        self.id=sha(encoded(self.challenge));controller.state.create('challenge-'+self.id,encoded(self.challenge));controller.guard()
    def authenticate(self,proof):
        require(not self.closed and not self.used,'challenge consumed/closed');self.used=True
        self.controller.guard()
        require(set(proof)=={'challenge','signature'} and proof['challenge']==self.challenge,'wrong fresh challenge')
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(self.controller.plan['public_key'])).verify(bytes.fromhex(proof['signature']),encoded(self.challenge))
        require(time.time()<self.challenge['expires_at'],'challenge expired')
        # Atomic, durable one-use marker prevents two authenticators/restart
        # replay. Failed proofs also consume this in-memory challenge.
        self.controller.state.create('consumed-'+self.id,encoded({'challenge_sha256':self.id,'plan_sha256':self.controller.pin,'authority_effect':'none'}))
        self.controller.guard();self.authenticated=True
        return {'principal_ref':self.controller.plan['principal_ref'],'role_assignment_bindings':[],'authority_effect':'none','origin':'verified-task-local-candidate-adapter','private_credentials_in_context':False,'session_restored':False}
    def guard(self):
        require(not self.closed and self.authenticated and time.time()<self.challenge['expires_at'],'channel unauthenticated/closed/expired');self.controller.guard()
        require(parse(self.controller.state.read('challenge-'+self.id))==self.challenge,'challenge evidence changed')
        require(parse(self.controller.state.read('consumed-'+self.id))=={'challenge_sha256':self.id,'plan_sha256':self.controller.pin,'authority_effect':'none'},'consumption evidence changed')
    def close(self):self.closed=True;self.authenticated=False;self.challenge=None
