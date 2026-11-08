"""Closed byte envelopes and selected Linux environment; no authority inference."""
import base64, ctypes, hashlib, importlib.metadata, json, os, platform, re, sqlite3, stat, sys, zipfile
from pathlib import Path, PurePosixPath
VERSIONS={'attrs':'25.4.0','cffi':'2.0.0','cryptography':'46.0.5','jsonschema':'4.23.0','jsonschema-specifications':'2023.12.1','pycparser':'2.23','referencing':'0.36.2','rpds-py':'0.27.1'}
def need(v,m):
 if not v: raise ValueError(m)
def sha(b): return hashlib.sha256(b).hexdigest()
def encoded(v): return (json.dumps(v,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def parse(b):
 def pairs(rows):
  d={}
  for k,v in rows: need(k not in d,'duplicate JSON field');d[k]=v
  return d
 return json.loads(b,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('nonfinite JSON')))
def load(p): return parse(read(p))
def emit(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(encoded(v));f.flush();os.fsync(f.fileno())
def relative(n):
 need(type(n) is str and n and '\\' not in n and '\x00' not in n,'invalid relative path');p=PurePosixPath(n)
 need(not p.is_absolute() and '..' not in p.parts and p.as_posix()==n,'noncanonical relative path')
 need(not any(x in ('.env','.local','__pycache__') or x.startswith('.env.') for x in p.parts),'private/cache path')
 need(not n.endswith(('.pem','.key','.pyc')),'private/cache suffix');return n

def read(p):
 p=Path(p);need(not p.is_symlink() and not any(x.is_symlink() for x in p.parents),'symlink material')
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb') as f:need(stat.S_ISREG(os.fstat(f.fileno()).st_mode),'regular material required');return f.read()

def environment():
 exe=Path(sys.executable).resolve()
 return {'python_version':platform.python_version(),'implementation':platform.python_implementation(),'machine':platform.machine(),'system':platform.system(),'libc':list(platform.libc_ver()),'sqlite_version':sqlite3.sqlite_version,'interpreter_sha256':sha(exe.read_bytes())}

def environment_guard(expected): need(environment()==expected,'unselected interpreter/SQLite/Linux environment')
def privacy(raw, *, source=False):
 # Schema declarations are not Session state. Actual values and embedded captured
 # source bytes are inspected independently; base64 is never a privacy bypass.
 need(not re.search(rb'-----BEGIN (?:[A-Z ]+)?PRIVATE KEY-----\r?\n',raw),'private key export')
 def walk(v,schema=False):
  if isinstance(v,dict):
   if not schema:
    need(not ({'private_key','private_key_bytes','session_memory','short_memory'} & set(v)),'private/session state export')
   for k,x in v.items():
    if k in ('byte_contents','control_bytes','executable_byte_contents') and isinstance(x,dict):
     for name,data in x.items():
      if k!='control_bytes':relative(name)
      privacy(base64.b64decode(data,validate=True),source=True)
    else:walk(x,schema or ((source or '$schema' in v) and k in ('properties','$defs','definitions')))
  elif isinstance(v,list):
   for x in v:walk(x,schema)
 if raw.lstrip().startswith((b'{',b'[')):walk(parse(raw))

def payload(raw):
 v=parse(raw);need(set(v)=={'schema_version','authority_effect','files','sha256s'},'closed snapshot required')
 need(v['schema_version']=='lab-exact-public-byte-snapshot/v1-candidate' and v['authority_effect']=='none','candidate snapshot required')
 need(set(v['files'])==set(v['sha256s']) and 0<len(v['files'])<=10000,'exact snapshot closure')
 out={}
 for n,b in v['files'].items():
  relative(n);data=base64.b64decode(b,validate=True);need(sha(data)==v['sha256s'][n],'snapshot byte mismatch');need(len(data)<=32*1024**2,'file budget');out[n]=data
 need(sum(map(len,out.values()))<=128*1024**2,'snapshot byte budget');return out

def snapshot(files):return {'schema_version':'lab-exact-public-byte-snapshot/v1-candidate','authority_effect':'none','files':{n:base64.b64encode(b).decode() for n,b in sorted(files.items())},'sha256s':{n:sha(b) for n,b in sorted(files.items())}}

def publish(parent_fd,stage,dest):
 fn=getattr(ctypes.CDLL(None,use_errno=True),'renameat2',None);need(fn is not None,'Linux no-replace publish unavailable')
 fn.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_uint];fn.restype=ctypes.c_int
 need(fn(parent_fd,os.fsencode(stage),parent_fd,os.fsencode(dest),1)==0,'no-replace publish rejected');os.fsync(parent_fd)
