"""Owned candidate lifecycle metadata. Cooperating callers, host/SQLite assumptions."""
from pathlib import Path
import contextlib,fcntl,json,os,sqlite3,uuid
from ..p03.context import C,require,binding,check
from ..execution.extension_runtime import Client,schema_validate
from . import lifecycle_adapter as adapter
H=Path(__file__).resolve().parent
class Conflict(ValueError):pass
class Store:
 def __init__(self,path):
  self.path=Path(path).resolve();require(self.path.is_relative_to(H) and self.path!=H,'store outside owned lifecycle scope');self.db=self.path/'lifecycle.sqlite3'
 @classmethod
 def create(cls,path,head,context,epoch=0):
  self=cls(path);self.path.mkdir(parents=True,exist_ok=False)
  initial={'store':uuid.uuid4().hex,'context':context,'epoch':epoch,'head':head,'generation':0,'history':[head],'evidence':[]}
  with self._connection() as db:
   db.execute('CREATE TABLE state (singleton INTEGER PRIMARY KEY CHECK(singleton=1), generation INTEGER NOT NULL, value TEXT NOT NULL)')
   db.execute('CREATE TABLE history (generation INTEGER PRIMARY KEY, record TEXT NOT NULL)')
   db.execute('INSERT INTO state VALUES (1,0,?)',(json.dumps(initial,sort_keys=True),));db.commit()
  return self
 def _connection(self):
  db=sqlite3.connect(self.db,timeout=30);db.execute('PRAGMA journal_mode=DELETE');db.execute('PRAGMA synchronous=FULL');return db
 @contextlib.contextmanager
 def _lock(self):
  with (self.path/'cooperating.lock').open('a+b') as lock:
   fcntl.flock(lock,fcntl.LOCK_EX)
   try:yield
   finally:fcntl.flock(lock,fcntl.LOCK_UN)
 def snapshot(self):
  with self._connection() as db:
   row=db.execute('SELECT generation,value FROM state WHERE singleton=1').fetchone();require(row is not None,'missing lifecycle head');state=C.decode(row[1].encode());require(row[0]==state['generation'],'generation metadata drift');return state
 @staticmethod
 def _durable(path,raw):
  fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  with os.fdopen(fd,'wb') as file:file.write(raw);file.flush();os.fsync(file.fileno())
 def commit(self,client,answer):
  require(type(client) is Client and client.extension=='E04' and answer.get('extension')=='E04','exact lifecycle qualifier required')
  require(answer.get('status')=='fresh-extension-candidate' and answer['value']['value']['eligible'],'checked eligibility is required')
  request=C.decode(check(answer['value']['request']).read_bytes());p=adapter.normalize(request,None)
  require(adapter.result(p)==answer['value']['value'],'checked transition result mismatch')
  def fresh():require(client.live_event(answer),'fresh owned lifecycle event required')
  return self._transaction(request,p,answer['completion'],fresh_guard=fresh)
 def _transaction(self,request,prepared,completion,crash_at=None,fresh_guard=None):
  # Private storage primitive used only after the public gate. Crash controls call
  # it in isolated child stores to measure SQLite durability, not proof freshness.
  require(prepared['eligible'],'ineligible lifecycle request');check(completion)
  with self._lock():
   db=self._connection()
   try:
    db.execute('BEGIN IMMEDIATE');row=db.execute('SELECT generation,value FROM state WHERE singleton=1').fetchone();current=C.decode(row[1].encode())
    if current!=request['before'] or row[0]!=request['before']['generation']:raise Conflict('head/generation conflict; qualify against the current exact head')
    if fresh_guard is not None:fresh_guard()
    folder=self.path/'artifacts'/uuid.uuid4().hex;folder.mkdir(parents=True)
    self._durable(folder/'request.json',json.dumps(request,sort_keys=True,ensure_ascii=False).encode())
    self._durable(folder/'completion-reference.json',json.dumps(completion,sort_keys=True).encode())
    dirfd=os.open(folder,os.O_RDONLY|os.O_DIRECTORY);os.fsync(dirfd);os.close(dirfd)
    parentfd=os.open(folder.parent,os.O_RDONLY|os.O_DIRECTORY);os.fsync(parentfd);os.close(parentfd)
    storefd=os.open(self.path,os.O_RDONLY|os.O_DIRECTORY);os.fsync(storefd);os.close(storefd)
    record={'before':request['before'],'after':prepared['after'],'input':binding(folder/'request.json'),'completion_reference':binding(folder/'completion-reference.json'),'completion':completion,'freshness':'checked-before-transaction; recovery-never-reissues','authority_effect':'none'}
    nxt=prepared['after'];db.execute('INSERT INTO history VALUES (?,?)',(nxt['generation'],json.dumps(record,sort_keys=True)))
    changed=db.execute('UPDATE state SET generation=?,value=? WHERE singleton=1 AND generation=?',(nxt['generation'],json.dumps(nxt,sort_keys=True),current['generation'])).rowcount
    require(changed==1,'transaction generation conflict')
    if crash_at=='before-commit':os._exit(91)
    db.commit()
    if crash_at=='after-commit':os._exit(92)
    return {'status':'candidate-lifecycle-committed','state':nxt,'record':record,'authority_effect':'none','application_authorized':False}
   finally:db.close()
 def recover(self):
  with self._lock():
   with self._connection() as db:
    state=self.snapshot();rows=db.execute('SELECT generation,record FROM history ORDER BY generation').fetchall();require(len(rows)==state['generation'],'history count mismatch')
    prior=None;records=[]
    for gen,raw in rows:
     r=C.decode(raw.encode());request=C.decode(check(r['input']).read_bytes());schema_validate(adapter.SCHEMA,request);require(C.decode(check(r['completion_reference']).read_bytes())==r['completion'],'completion reference mismatch');packet=C.decode(check(r['completion']).read_bytes());require(C.identity(request)==packet['request_identity'],'history completion request mismatch');p=adapter.normalize(request,None)
     require(p['eligible'] and p['after']==r['after'] and request['before']==r['before'] and gen==r['after']['generation'],'history transition mismatch')
     require(prior is None or prior==r['before'],'history fork');prior=r['after'];records.append(r)
    require(prior is None or prior==state,'head/history divergence')
    return {'status':'recorded-committed-state','state':state,'records':records,'fresh_event':False,'authority_effect':'none','application_authorized':False}
