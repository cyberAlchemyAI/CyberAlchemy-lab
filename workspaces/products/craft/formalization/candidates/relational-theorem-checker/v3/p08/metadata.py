"""Transactional authoritative heads and checked mirrors for mediated stores.

Metadata-only probes never claim theorem qualification. Public fresh publication
is composed by shadow.py; this module does not accept saved ready flags.
"""
from pathlib import Path
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
import sqlite3
import time
import uuid
from jsonschema import Draft202012Validator
from ..p03.context import BASE,ROOT,C,check,binding,require
from ..p07.runs import inspect_record

HERE=Path(__file__).resolve().parent
class Reconciliation(RuntimeError):pass
class Exhausted(RuntimeError):pass
class Cancelled(RuntimeError):pass

def encoded(value):return (json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)+'\n').encode()
def validate(name,value):
    Draft202012Validator(C.decode((HERE/(name+'.schema.json')).read_bytes())).validate(value);return value
def fsync_directory(path):
    fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
def immutable(path,value):
    path=Path(path);require(path.resolve().is_relative_to(HERE),'immutable write outside P08')
    raw=encoded(value);require(len(raw)<=4194304,'metadata file byte ceiling')
    with path.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
    os.chmod(path,0o400);fsync_directory(path.parent);return binding(path)
def planned(path,value):
    require(Path(path).resolve().is_relative_to(HERE),'planned path outside P08')
    return {'path':str(Path(path).resolve().relative_to(ROOT)),'sha256':hashlib.sha256(encoded(value)).hexdigest()}

class Store:
    @classmethod
    def initialize(cls,root,baseline,*,store_kind='fixture-shadow',seed_evidence=None,seed_gate=None):
        root=Path(root).resolve();require(root.is_relative_to(HERE/'stores'),'store outside P08 owned stores')
        if store_kind=='fixture-shadow':
            require(seed_evidence is not None and seed_gate is not None,'fixture shadow genesis requires independent fresh baseline registration')
            seed_gate()
        require(not root.exists(),'store already exists');root.mkdir(parents=True,mode=0o700)
        for name in ['snapshots','registrations','reviews']: (root/name).mkdir(mode=0o700)
        store_id=uuid.uuid4().hex
        policy={'schema':'relational.shadow-policy/v3','writers':'exclusively-mediated-cooperating-writers',
                'store_kind':store_kind,'scope':'bounded-local-candidate','authority_effect':'none','application_authorized':False}
        validate('policy',policy)
        owner={'schema':'relational.shadow-owner/v3','store_id':store_id,'root':str(root.relative_to(ROOT)),
               'policy':policy,'authority_effect':'none','application_authorized':False}
        validate('owner',owner);owner_ref=immutable(root/'owner.json',owner)
        genesis_tx=uuid.uuid4().hex if seed_evidence is not None else None
        snap={'schema':'relational.shadow-snapshot/v3','store_id':store_id,'transaction_id':genesis_tx,
              'baseline_identity':C.identity(baseline),'baseline':baseline,'authority_effect':'none','application_authorized':False}
        validate('snapshot',snap);snapshot=immutable(root/'snapshots/genesis.json',snap)
        registration=None
        if seed_evidence is not None:
            reg={'schema':'relational.shadow-registration/v3','store_id':store_id,'transaction_id':genesis_tx,
                 'baseline_identity':C.identity(baseline),'snapshot':snapshot,**seed_evidence,
                 'authority_effect':'none','application_authorized':False}
            validate('registration',reg);registration=immutable(root/'registrations/genesis.json',reg)
        head={'schema':'relational.shadow-head/v3','store_id':store_id,'store_kind':store_kind,'generation':0,
              'baseline_identity':C.identity(baseline),'snapshot':snapshot,'registration':registration,'transaction_id':genesis_tx,
              'authority_effect':'none','application_authorized':False}
        validate('head',head)
        db=sqlite3.connect(root/'metadata.db')
        try:
            db.execute('PRAGMA journal_mode=DELETE');db.execute('PRAGMA synchronous=FULL')
            db.executescript('CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL); CREATE TABLE head (id INTEGER PRIMARY KEY CHECK(id=1), generation INTEGER NOT NULL, value TEXT NOT NULL); CREATE TABLE transactions (id TEXT PRIMARY KEY, phase TEXT NOT NULL, generation INTEGER NOT NULL, fresh_run_id TEXT NOT NULL UNIQUE, value TEXT NOT NULL); CREATE UNIQUE INDEX committed_generation ON transactions(generation) WHERE phase="committed";')
            db.executemany('INSERT INTO meta VALUES (?,?)',[('owner',encoded(owner_ref).decode()),('genesis',encoded(head).decode())])
            db.execute('INSERT INTO head VALUES (1,0,?)',(encoded(head).decode(),));db.commit()
        finally:db.close()
        os.chmod(root/'metadata.db',0o600);fsync_directory(root)
        immutable(root/'HEAD.json',head);(root/'LOCK').touch(mode=0o600);fsync_directory(root)
        return cls(root)

    def __init__(self,root):
        self.root=Path(root).resolve();require(self.root.is_relative_to(HERE/'stores') and self.root.is_dir(),'not an owned P08 store')
        for name in ['owner.json','metadata.db','HEAD.json','LOCK','snapshots','registrations','reviews']:
            require(not (self.root/name).is_symlink(),'store symlink forbidden')
        self.owner=validate('owner',C.decode((self.root/'owner.json').read_bytes()))
        require(self.owner['root']==str(self.root.relative_to(ROOT)),'store owner/root mismatch')
        self.id=self.owner['store_id'];self.kind=self.owner['policy']['store_kind']

    @contextmanager
    def lock(self,*,deadline=None,cancel=None):
        fd=os.open(self.root/'LOCK',os.O_RDWR|os.O_NOFOLLOW)
        try:
            while True:
                if cancel is not None and cancel.is_set():raise Cancelled('Cancelled while waiting for the mediated writer.')
                if deadline is not None and time.monotonic()>deadline:raise Exhausted('Publication deadline while waiting for the mediated writer.')
                try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);break
                except BlockingIOError:time.sleep(.02)
            yield
        finally:os.close(fd)

    def connect(self):
        db=sqlite3.connect(self.root/'metadata.db',timeout=.1)
        try:
            db.execute('PRAGMA synchronous=FULL');require(db.execute('PRAGMA journal_mode').fetchone()[0]=='delete','unexpected metadata journal mode')
            require(db.execute('PRAGMA synchronous').fetchone()[0]==2,'FULL synchronization unavailable')
            owner_ref=C.decode(db.execute('SELECT value FROM meta WHERE key="owner"').fetchone()[0].encode())
            require(check(owner_ref)==self.root/'owner.json','owner binding changed')
            return db
        except BaseException:db.close();raise

    def _head(self,db):
        generation,raw=db.execute('SELECT generation,value FROM head WHERE id=1').fetchone()
        head=validate('head',C.decode(raw.encode()))
        require(head['generation']==generation and head['store_id']==self.id and head['store_kind']==self.kind,'authoritative head metadata mismatch')
        return head

    def _transactions(self,db):
        result=[]
        for id,phase,generation,run,raw in db.execute('SELECT id,phase,generation,fresh_run_id,value FROM transactions ORDER BY generation,id'):
            value=validate('transaction',C.decode(raw.encode()))
            require(value['transaction_id']==id and value['phase']==phase and value['after_head']['generation']==generation and value['fresh_run_id']==run,'transaction columns/body mismatch')
            require(value['store_id']==self.id and value['store_kind']==self.kind,'transaction store substitution')
            result.append(value)
        return result

    def _save_tx(self,db,value,*,insert=False):
        validate('transaction',value)
        data=(value['phase'],value['after_head']['generation'],value['fresh_run_id'],encoded(value).decode(),value['transaction_id'])
        if insert:db.execute('INSERT INTO transactions(phase,generation,fresh_run_id,value,id) VALUES (?,?,?,?,?)',data)
        else:require(db.execute('UPDATE transactions SET phase=?,generation=?,fresh_run_id=?,value=? WHERE id=?',data).rowcount==1,'missing transaction')
        db.commit();fsync_directory(self.root)

    def _local(self,ref,folder):
        p=check(ref);require(p.parent==self.root/folder,'artifact not in exact owned store folder');return p

    def _snapshot(self,head):
        p=self._local(head['snapshot'],'snapshots');snap=validate('snapshot',C.decode(p.read_bytes()))
        require(snap['store_id']==self.id and snap['transaction_id']==head['transaction_id'],'snapshot/store/transaction mismatch')
        require(snap['baseline_identity']==head['baseline_identity']==C.identity(snap['baseline']),'snapshot/baseline identity mismatch')
        return snap

    def _registration(self,head):
        p=self._local(head['registration'],'registrations');reg=validate('registration',C.decode(p.read_bytes()))
        require(reg['store_id']==self.id and reg['transaction_id']==head['transaction_id'],'registration store/transaction mismatch')
        require(reg['snapshot']==head['snapshot'] and reg['baseline_identity']==head['baseline_identity'],'registration successor mismatch')
        expected='fresh-independent-successor-registration' if self.kind=='fixture-shadow' else 'io-probe-unqualified'
        require(reg['proof_mode']==expected,'unqualified IO registration cannot enter a theorem-qualified store')
        if self.kind=='fixture-shadow':
            for name in ['request','qualification','completion','owned_run']:check(reg[name])
            request=C.decode(check(reg['request']).read_bytes());C.validate('request',request)
            q=C.decode(check(reg['qualification']).read_bytes());C.validate('result',q)
            completion=C.decode(check(reg['completion']).read_bytes());inspect_record(reg['owned_run'])
            owned=C.decode(check(reg['owned_run']).read_bytes())
            require(completion['result']==reg['qualification']==owned['result'],'registration completion/result/owned binding mismatch')
            require(owned['request_identity']==q['request_identity'] and owned['policy_identity']==C.identity(request['resource_policy']),'registration owned request/policy mismatch')
            require(q['status']=='qualified-candidate' and q['request_identity']==C.identity(request),'registration qualification/request mismatch')
            require(request['proposal']['before']==request['proposal']['after'] and C.identity(request['proposal']['before'])==head['baseline_identity'],'registration is not an independent exact successor check')
            require(reg['required_inventory']==[o['id'] for o in C.required_inventory('register')],'registration inventory changed')
            require(q['manifest']['obligations']==[o['id'] for o in C.required_inventory('rule-only')],'registration superset proof inventory changed')
            require(owned['phase']=='completed','registration owned evidence incomplete')
        return reg

    def _mirror(self,head):
        p=self.root/('HEAD-'+uuid.uuid4().hex+'.tmp')
        with p.open('xb') as f:f.write(encoded(head));f.flush();os.fsync(f.fileno())
        os.chmod(p,0o400);os.replace(p,self.root/'HEAD.json');fsync_directory(self.root)

    def _recover_locked(self,db):
        head=self._head(db);transactions=self._transactions(db)
        genesis=validate('head',C.decode(db.execute('SELECT value FROM meta WHERE key="genesis"').fetchone()[0].encode()))
        self._snapshot(genesis)
        if self.kind=='fixture-shadow':
            require(genesis['registration'] is not None,'unregistered genesis cannot enter candidate shadow')
            self._registration(genesis)
        previous=genesis;events=[]
        for tx in [t for t in transactions if t['phase']=='committed']:
            require(tx['before_head']==previous,'committed generation chain conflict')
            require(tx['after_head']['generation']==previous['generation']+1,'committed generation gap')
            require(tx['after_head']['snapshot']==tx['snapshot'] and tx['after_head']['registration']==tx['registration'],'committed head artifact mismatch')
            self._snapshot(tx['after_head']);self._registration(tx['after_head']);previous=tx['after_head']
            for ref in tx['mapped_checks']:check(ref)
        require(previous==head,'authoritative head/committed journal conflict; preserve potentially committed state')
        active=next((t for t in transactions if t['transaction_id']==head['transaction_id']),None)
        actual=(self.root/'HEAD.json').read_bytes()
        if actual!=encoded(head):
            if active and active['progress']=='metadata-head' and actual==encoded(active['before_head']):
                self._mirror(head);events.append({'kind':'repaired-mirror','detail':'Only the recorded postcommit mirror window was repaired; authoritative head was preserved.'})
            else:raise Reconciliation('HEAD mirror conflict outside the recorded postcommit window; authoritative head preserved.')
        if active and active['progress']!='complete':
            active['progress']='complete';self._save_tx(db,active)
        for tx in transactions:
            if tx['phase']=='reconciliation-required':raise Reconciliation(tx['reason'])
            if tx['phase']!='prepared':continue
            require(head['transaction_id']!=tx['transaction_id'],'prepared journal names potentially committed head')
            # Missing files in an unfinished phase are a known precommit crash.
            # A recorded durable phase whose binding changed is conflicting state.
            completed={'snapshot'} if tx['progress']=='snapshot' else {'snapshot','registration'} if tx['progress']=='registration' else set()
            for field in ['snapshot','registration']:
                p=(ROOT/tx[field]['path']).resolve()
                require(p.parent==self.root/('snapshots' if field=='snapshot' else 'registrations'),'prepared artifact outside owned store')
                if field in completed:self._local(tx[field],'snapshots' if field=='snapshot' else 'registrations')
                elif p.exists() and binding(p)!=tx[field]:
                    # A partial exclusive file before its durable phase marker
                    # is retained as interrupted preparation, never promoted.
                    events.append({'kind':'retained-partial-file','detail':str(p.relative_to(ROOT))})
            tx['phase']='aborted';tx['reason']='Recovered uncommitted preparation; authoritative committed head unchanged.'
            self._save_tx(db,tx);events.append({'kind':'aborted-prepared','detail':tx['transaction_id']})
        return head,events

    def recover(self,*,deadline=None,cancel=None):
        db=None
        try:
            with self.lock(deadline=deadline,cancel=cancel):
                db=self.connect();head,events=self._recover_locked(db)
                return {'schema':'relational.shadow-recovery/v3','status':'head-current','head':head,'events':events,
                        'proof_scope':self.kind,'fresh_qualification':False,'authority_effect':'none','application_authorized':False}
        except (Cancelled,Exhausted):raise
        except Exception as e:
            return {'schema':'relational.shadow-recovery/v3','status':'reconciliation-required','reason':str(e).splitlines()[0][:500],
                    'proof_scope':self.kind,'fresh_qualification':False,'authority_effect':'none','application_authorized':False}
        finally:
            if db:db.close()

    def head(self):
        recovered=self.recover();require(recovered['status']=='head-current',recovered.get('reason','reconciliation required'));return recovered['head']

    def review(self,request,raw,*,mappings=(),reviewer='author-integration-fixture',assessment='reviewed-candidate'):
        require(self.kind=='fixture-shadow','IO store cannot issue an application review')
        C.validate('request',request);head=self.head()
        require(C.identity(request['proposal']['before'])==head['baseline_identity'],'review before differs from head')
        value={'schema':'relational.shadow-review/v3','store_id':self.id,'expected_head':head,
               'request_bytes_sha256':hashlib.sha256(raw).hexdigest(),'request_identity':C.identity(request),
               'proposal_identity':C.identity(request['proposal']),'successor_identity':C.identity(request['proposal']['after']),
               'reviewer':reviewer,'assessment':assessment,'context_identity':C.identity(request['proposal']['before']['context']),
               'mappings_identity':C.identity(list(mappings)),'mapped_contexts':[C.identity(m['baseline']['context']) for m in mappings],
               'authority_effect':'none','application_authorized':False}
        validate('review',value);return immutable(self.root/'reviews'/('review-'+uuid.uuid4().hex+'.json'),value)

    def _publish(self,*,before,after_baseline,registration_evidence,review,proposal_qualification,fresh_run_id,mapped_checks=(),gate=None,fault=None,deadline=None,cancel=None):
        """Internal engine. Fresh publication requires shadow.py's live guard."""
        require(self.kind=='io-probe-unqualified' or gate is not None,'live mediated publication guard missing')
        with self.lock(deadline=deadline,cancel=cancel):
            db=self.connect()
            try:
                head,_=self._recover_locked(db)
                if head!=before:return {'status':'stale-head','head':head,'authority_effect':'none','application_authorized':False}
                if gate:gate()
                txid=uuid.uuid4().hex
                snap={'schema':'relational.shadow-snapshot/v3','store_id':self.id,'transaction_id':txid,
                      'baseline_identity':C.identity(after_baseline),'baseline':after_baseline,'authority_effect':'none','application_authorized':False}
                validate('snapshot',snap);snap_path=self.root/'snapshots'/(txid+'.json');snap_ref=planned(snap_path,snap)
                reg={'schema':'relational.shadow-registration/v3','store_id':self.id,'transaction_id':txid,
                     'baseline_identity':snap['baseline_identity'],'snapshot':snap_ref,**registration_evidence,
                     'authority_effect':'none','application_authorized':False}
                validate('registration',reg);reg_path=self.root/'registrations'/(txid+'.json');reg_ref=planned(reg_path,reg)
                after={**head,'generation':head['generation']+1,'baseline_identity':snap['baseline_identity'],
                       'snapshot':snap_ref,'registration':reg_ref,'transaction_id':txid}
                tx={'schema':'relational.shadow-transaction/v3','store_id':self.id,'transaction_id':txid,'store_kind':self.kind,
                    'phase':'prepared','progress':'journal','before_head':head,'after_head':after,'review':review,
                    'proposal_qualification':proposal_qualification,'registration':reg_ref,'snapshot':snap_ref,
                    'mapped_checks':list(mapped_checks),
                    'fresh_run_id':fresh_run_id,'reason':'','authority_effect':'none','application_authorized':False}
                self._save_tx(db,tx,insert=True)
                if fault:fault('journal')
                require(immutable(snap_path,snap)==snap_ref,'snapshot serialization drift')
                tx['progress']='snapshot';self._save_tx(db,tx)
                if fault:fault('snapshot')
                require(immutable(reg_path,reg)==reg_ref,'registration serialization drift')
                tx['progress']='registration';self._save_tx(db,tx)
                if fault:fault('registration')
                if cancel is not None and cancel.is_set():raise Cancelled('Cancelled after registration; head unchanged.')
                if deadline is not None and time.monotonic()>deadline:raise Exhausted('Publication whole-run deadline before commit; head unchanged.')
                if gate:gate()
                require((self.root/'HEAD.json').read_bytes()==encoded(head),'external mirror edit before commit')
                db.execute('BEGIN IMMEDIATE')
                try:
                    tx['phase']='committed';tx['progress']='metadata-head'
                    require(db.execute('UPDATE head SET generation=?,value=? WHERE id=1 AND generation=? AND value=?',
                                       (after['generation'],encoded(after).decode(),head['generation'],encoded(head).decode())).rowcount==1,'transactional head comparison failed')
                    db.execute('UPDATE transactions SET phase=?,value=? WHERE id=?',('committed',encoded(tx).decode(),txid))
                    db.commit();fsync_directory(self.root)
                except BaseException:db.rollback();raise
                if fault:fault('metadata-head')
                self._mirror(after)
                if fault:fault('mirror')
                tx['progress']='complete';self._save_tx(db,tx)
                return {'status':'applied-candidate-shadow' if self.kind=='fixture-shadow' else 'committed-io-probe',
                        'before':head,'after':after,'transaction':tx,'authority_effect':'none','application_authorized':False}
            finally:db.close()

    def committed_run(self,fresh_run_id):
        """Inspect durable commit after an exception; never infer noncommit from it."""
        with self.lock():
            db=self.connect()
            try:
                rows=[t for t in self._transactions(db) if t['fresh_run_id']==fresh_run_id and t['phase']=='committed']
                require(len(rows)<=1,'duplicate committed fresh run')
                return rows[0] if rows else None
            finally:db.close()

    def probe(self,after_baseline,*,fault=None,cancel=None,deadline=None):
        require(self.kind=='io-probe-unqualified','metadata-only probe forbidden in a theorem-qualified store')
        before=self.head()
        evidence={'proof_mode':'io-probe-unqualified','request':None,'qualification':None,'completion':None,'owned_run':None,
                  'required_inventory':[],'fresh_at_creation':False}
        return self._publish(before=before,after_baseline=after_baseline,registration_evidence=evidence,review=None,
                             proposal_qualification=None,fresh_run_id='io-probe-'+uuid.uuid4().hex,fault=fault,cancel=cancel,deadline=deadline)
