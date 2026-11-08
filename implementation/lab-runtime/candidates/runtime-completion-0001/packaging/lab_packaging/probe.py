"""Bounded real cold loading of the installed public dependency closure."""
import json,time
from lab_contracts.codec import need,sha
from lab_selectors.authority import bounded_transport
from environment.requirements import VERSIONS
from .selection import SENTINEL

def python_command(tree,code,args=()):
    root=tree.path
    return [str(root/'lib/abi/ld-linux-x86-64.so.2'),'--inhibit-cache','--library-path',str(root/'lib/abi'),
        str(root/'bin/python'),'-I','-X','utf8','-B','-S','-X','pycache_prefix='+str(root/'bytecode-disabled'),'-c',code,*map(str,args)]

CODE=r'''
import sys
if not (sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode and sys.flags.utf8_mode):raise RuntimeError('FLAGS')
import os,json,sqlite3,importlib.metadata,hashlib,bz2,lzma,ssl,ctypes,asyncio,uuid,resource,fcntl,zipfile,subprocess
from pathlib import Path
root=Path(sys.argv[1]);manifest=json.loads((root/'payload-manifest.json').read_bytes());members=manifest['members']
if sys.pycache_prefix!=str(root/'bytecode-disabled') or not Path(sys.pycache_prefix).is_file():raise RuntimeError('CACHE_POLICY')
sys.path.insert(0,str(root/'deps'))
allowed=[str(root/'deps'),str(root/'lib/python314.zip'),str(root/'lib/python3.14'),str(root/'lib/python3.14/lib-dynload')]
if sys.path!=allowed:raise RuntimeError('PATH_POLICY')
import jsonschema,cryptography,cffi,rpds,referencing,attr
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
k=Ed25519PrivateKey.from_private_bytes(bytes(range(32)));message=b'owned inert dependency probe';k.public_key().verify(k.sign(message),message)
jsonschema.Draft202012Validator({'type':'integer'}).validate(7)
db=sqlite3.connect(':memory:');db.execute('CREATE TABLE p(v INTEGER,t TEXT)');db.execute('INSERT INTO p VALUES(?,?)',(7,'Laboratório 研究'))
if db.execute('SELECT * FROM p').fetchone()!=(7,'Laboratório 研究'):raise RuntimeError('SQLITE')
db.close()
if bz2.decompress(bz2.compress(message))!=message or lzma.decompress(lzma.compress(message))!=message:raise RuntimeError('COMPRESSION')
modules={}
def selected(path):
    p=Path(path)
    if not p.is_relative_to(root):raise RuntimeError('EXTERNAL_ORIGIN')
    rel=p.relative_to(root).as_posix()
    if rel not in members or hashlib.sha256(p.read_bytes()).hexdigest()!=members[rel]['sha256']:raise RuntimeError('UNSELECTED_ORIGIN')
    return rel
for name,value in list(sys.modules.items()):
    path=getattr(value,'__file__',None)
    if path and not path.startswith('<'):modules[name]=selected(path)
maps=sorted({selected(line.split()[-1]) for line in Path('/proc/self/maps').read_text().splitlines() if len(line.split())>=6 and line.split()[-1].startswith('/')})
required=['bin/python','lib/abi/ld-linux-x86-64.so.2','lib/abi/libsqlite3.so.0']
if not set(required).issubset(maps):raise RuntimeError('MAPPING_REQUIRED')
native=subprocess.run([str(root/'lib/abi/ld-linux-x86-64.so.2'),'--inhibit-cache','--library-path',str(root/'lib/abi'),str(root/'bin/lab-context-native-reader')],env={'LC_ALL':'C','LANG':'C'},stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=10,close_fds=True)
if native.returncode!=1 or native.stdout!=b'' or native.stderr!=b'usage: lab-context-native-reader semantic-dir governance-dir request.json\n':raise RuntimeError('NATIVE_USAGE')
print(json.dumps({'python_version':sys.version.split()[0],'sqlite_version':sqlite3.sqlite_version,
 'versions':{n:importlib.metadata.version(n) for n in json.loads(sys.argv[2])},'module_origins':modules,'mapped_origins':maps,
 'bytecode_policy':'isolated-command-line-regular-file-prefix','native_usage_exit':native.returncode,
 'sqlite_roundtrip':True,'signature_fixture':True,'schema_validation':True,'compression_roundtrips':True},sort_keys=True))
'''

def cold_probe(tree,expected):
    tree.verify(expected)
    need(expected['bytecode-disabled']['sha256']==sha(SENTINEL),'INSTALLED_CACHE_SENTINEL')
    argv=python_command(tree,CODE,[tree.path,json.dumps(list(VERSIONS))])
    started=time.time_ns();clock=time.monotonic_ns()
    raw=bounded_transport(argv,{'LC_ALL':'C','LANG':'C'},str(tree.path),b'',60000,65536)
    ended=time.time_ns();elapsed=time.monotonic_ns()-clock
    value=json.loads(raw)
    need(value['versions']==VERSIONS and value['python_version']=='3.14.4' and value['sqlite_version']=='3.46.1','COLD_VERSION')
    tree.verify(expected)
    return {'result':'PASS','observation':value,'argv':argv,'environment':{'LC_ALL':'C','LANG':'C'},
        'actual_transport_exit_code':0,'started_utc_ns':started,'ended_utc_ns':ended,'elapsed_ns':elapsed,
        'source_rebuild_reproduced':False,'native_semantic_qualified':False,'protected_startup_qualified':False,
        'actual_host_custody_qualified':False,'authority_effect':'none'}
