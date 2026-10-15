"""Owned candidate coordination journal with exact replay and recovery.

The one committed transaction contains original next-run bytes and its event.
The head is a recoverable pointer. A pending claim is never redispatched.
This store does not apply repository admission or export Agent short memory.
"""
import base64
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import tempfile
from .kernel import encoded,require,digest

def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(path):
    require(path.is_file() and not path.is_symlink() and not any(p.is_symlink() for p in path.parents),'unsafe workflow journal file')
    return path.read_bytes()
def sync(path):
    fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:os.fsync(fd)
    finally:os.close(fd)
def write_new(path,raw):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
    sync(path.parent)
def replace_owned(path,raw):
    require(not path.is_symlink(),'unsafe workflow head')
    fd,name=tempfile.mkstemp(prefix='.workflow-head-',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
        os.replace(name,path);sync(path.parent)
    finally:
        if Path(name).exists():Path(name).unlink()

class Indeterminate(ValueError):pass

class Journal:
    @classmethod
    def initialize(cls,root,run_raw,scope_ref,principal_ref):
        root=Path(root)
        require(root.is_absolute() and root.is_relative_to(Path('/tmp')) and not root.exists()
            and not any(p.is_symlink() for p in root.parents),'fresh owned workflow store required')
        run=json.loads(run_raw);require(run['schema_version']=='lab-workflow-run/v1-candidate'
            and run['authority_effect']=='none' and run['actor']['principal_ref']==principal_ref,'exact initial candidate run required')
        root.mkdir(mode=0o700)
        for name in ('claims','transactions'):(root/name).mkdir(mode=0o700)
        config={'schema_version':'lab-owned-workflow-journal/v1-candidate','scope_ref':scope_ref,
            'principal_ref':principal_ref,'run_ref':run['run_ref'],'genesis_sha256':sha(run_raw),'authority_effect':'none'}
        write_new(root/'config.json',encoded(config));write_new(root/'genesis.json',run_raw)
        write_new(root/'HEAD.json',encoded({'sequence':0,'transaction_sha256':None,'run_sha256':sha(run_raw)}))
        write_new(root/'.writer.lock',b'')
        return cls(root,sha(encoded(config)))
    def __init__(self,root,config_sha256):
        self.root=Path(root);self.config_sha256=config_sha256
        require(self.root.is_absolute() and self.root.is_relative_to(Path('/tmp'))
            and self.root.stat().st_uid==os.getuid() and self.root.stat().st_mode&0o777==0o700,'owned workflow root/mode required')
        raw=read(self.root/'config.json');require(sha(raw)==config_sha256,'workflow journal configuration differs')
        self.config=json.loads(raw);require(self.config['authority_effect']=='none','workflow journal grants no admission')
        self.replay()
    @contextmanager
    def locked(self):
        fd=os.open(self.root/'.writer.lock',os.O_RDWR|os.O_NOFOLLOW)
        try:fcntl.flock(fd,fcntl.LOCK_EX);yield
        finally:fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
    def replay(self):
        require(sha(read(self.root/'config.json'))==self.config_sha256,'workflow configuration changed')
        head=json.loads(read(self.root/'HEAD.json'));raw=read(self.root/'genesis.json')
        require(sha(raw)==self.config['genesis_sha256'],'workflow genesis original differs')
        prior=None
        for sequence in range(1,head['sequence']+1):
            txraw=read(self.root/'transactions'/f'{sequence:08d}.json');tx=json.loads(txraw)
            require(tx['sequence']==sequence and tx['predecessor_transaction_sha256']==prior
                and tx['before_run_sha256']==sha(raw) and tx['authority_effect']=='none','workflow transaction replay chain differs')
            raw=base64.b64decode(tx['next_run_original_base64'],validate=True)
            require(sha(raw)==tx['next_run_sha256'],'workflow next-run original hash differs')
            claimraw=read(self.root/'claims'/(tx['namespace']+'.json'));claim=json.loads(claimraw)
            require(sha(claimraw)==tx['claim_sha256'] and claim['fingerprint']==tx['fingerprint'],
                'workflow committed claim differs')
            require(digest({'request_binding':claim['request_binding'],'plan':claim['plan']})==claim['fingerprint']
                and tx['event']==claim['plan']['event'] and json.loads(raw)==claim['plan']['next_run'],
                'workflow effect differs from exact original planned claim')
            body=json.loads(raw)
            require(body['state']==tx['event']['to_state'] and body['run_ref']==self.config['run_ref']
                and body['authority_effect']=='none','workflow committed run/event differs')
            prior=sha(txraw)
        require(head['transaction_sha256']==prior and head['run_sha256']==sha(raw),'workflow head differs from replay')
        return head,raw
    def namespace(self,key):
        return digest({'principal_ref':self.config['principal_ref'],'scope_ref':self.config['scope_ref'],
            'run_ref':self.config['run_ref'],'operation':'workflow.transition','idempotency_key':key})
    def lookup(self,key,fingerprint):
        ns=self.namespace(key);path=self.root/'claims'/(ns+'.json')
        if not path.exists():return None
        claimraw=read(path);claim=json.loads(claimraw)
        require(claim['fingerprint']==fingerprint,'workflow idempotency key conflicts with different exact inputs')
        head,_=self.replay();sequence=claim['sequence'];txpath=self.root/'transactions'/f'{sequence:08d}.json'
        if not txpath.exists() or head['sequence']<sequence:raise Indeterminate('pending workflow claim requires observation/recovery; never redispatch')
        tx=json.loads(read(txpath));require(tx['namespace']==ns and tx['claim_sha256']==sha(claimraw),'workflow result belongs to another claim')
        return tx
    def apply(self,plan,*,request_binding,host_guard,crash_at=None):
        require(type(host_guard) is not type(None),'actual host authority/source guard required')
        host_guard()
        require(plan['schema_version']=='lab-workflow-transition-plan/v1-candidate'
            and plan['authority_effect']=='none' and plan['actual_apply_completed'] is False
            and plan['work_satisfaction_asserted'] is False,'exact private transition plan required')
        event=plan['event'];key=event['idempotency_key'];fingerprint=digest({'request_binding':request_binding,'plan':plan})
        with self.locked():
            host_guard();existing=self.lookup(key,fingerprint)
            if existing is not None:return existing
            head,current=self.replay();require(sha(current)==plan['expected_before_sha256'],'workflow run preimage changed')
            for path in (self.root/'claims').glob('*.json'):
                prior=json.loads(read(path))
                if prior['sequence']>head['sequence']:
                    raise Indeterminate('another pending workflow claim requires observation; no concurrent transition is dispatched')
            next_run=plan['next_run'];require(next_run['actor']['principal_ref']==self.config['principal_ref']
                and next_run['run_ref']==self.config['run_ref'] and digest(next_run)==plan['next_run_structural_sha256'],
                'workflow next-run identity/body differs')
            sequence=head['sequence']+1;ns=self.namespace(key)
            claim={'sequence':sequence,'namespace':ns,'fingerprint':fingerprint,'request_binding':request_binding,
                'before_run_sha256':sha(current),'plan':plan,'authority_effect':'none'}
            claimraw=encoded(claim);write_new(self.root/'claims'/(ns+'.json'),claimraw)
            if crash_at=='after-claim':raise Indeterminate('interrupted after workflow claim')
            host_guard()
            tx={'schema_version':'lab-candidate-workflow-transaction/v1-candidate','sequence':sequence,
                'predecessor_transaction_sha256':head['transaction_sha256'],'namespace':ns,'fingerprint':fingerprint,
                'claim_sha256':sha(claimraw),'before_run_sha256':sha(current),'event':event,
                'next_run_original_base64':base64.b64encode(encoded(next_run)).decode(),'next_run_sha256':sha(encoded(next_run)),
                'output_artifact_refs':[],'canonical_admissions':0,'authority_effect':'none'}
            txraw=encoded(tx);write_new(self.root/'transactions'/f'{sequence:08d}.json',txraw)
            if crash_at=='after-transaction':raise Indeterminate('interrupted after immutable workflow transaction')
            host_guard();replace_owned(self.root/'HEAD.json',encoded({'sequence':sequence,'transaction_sha256':sha(txraw),'run_sha256':tx['next_run_sha256']}))
            self.replay();host_guard();return tx
    def recover(self,key,fingerprint,*,host_guard):
        """Observe an existing exact transaction; no transition is dispatched."""
        host_guard()
        with self.locked():
            ns=self.namespace(key);claimraw=read(self.root/'claims'/(ns+'.json'));claim=json.loads(claimraw)
            require(claim['fingerprint']==fingerprint,'workflow recovery fingerprint differs')
            head,current=self.replay();sequence=claim['sequence'];path=self.root/'transactions'/f'{sequence:08d}.json'
            require(path.exists(),'no observed immutable workflow effect; pending claim cannot be retried')
            raw=read(path);tx=json.loads(raw)
            require(tx['namespace']==ns and tx['claim_sha256']==sha(claimraw) and tx['fingerprint']==fingerprint,
                'workflow recovery original claim/effect differs')
            require(digest({'request_binding':claim['request_binding'],'plan':claim['plan']})==fingerprint
                and tx['event']==claim['plan']['event'],'workflow recovery observed effect differs from exact plan')
            if head['sequence']<sequence:
                require(sequence==head['sequence']+1 and tx['predecessor_transaction_sha256']==head['transaction_sha256']
                    and tx['before_run_sha256']==sha(current),'workflow recovery preimage differs')
                observed=base64.b64decode(tx['next_run_original_base64'],validate=True)
                require(sha(observed)==tx['next_run_sha256'] and json.loads(observed)==claim['plan']['next_run'],
                    'workflow recovery observed bytes differ')
                host_guard();replace_owned(self.root/'HEAD.json',encoded({'sequence':sequence,'transaction_sha256':sha(raw),'run_sha256':sha(observed)}))
            self.replay();host_guard();return tx
