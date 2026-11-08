"""C01 compatibility fixtures derived from the independently accepted codec/schema."""
import argparse,hashlib,json,os,stat,sys
from pathlib import Path
R=Path('/home/vlad_/projects/CyberAlchemy-lab')
S=R/'implementation/lab-runtime/candidates/runtime-completion-0001'
E=R/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U03-01'
OLD=E.parent/'LC-U01-02'
PREFIX=OLD/'python-bytecode-cache-disabled-0002'
DEP=R/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004/deps'
T=Path(__file__).absolute().parent

def read(path,expected=None):
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
 with os.fdopen(fd,'rb') as f:
  before=os.fstat(f.fileno())
  if not stat.S_ISREG(before.st_mode) or before.st_size>64*1024*1024:raise ValueError('input type/bound')
  raw=f.read(64*1024*1024+1);after=os.fstat(f.fileno())
  if (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)!=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns):raise ValueError('input changed')
  if expected is not None and hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('input digest')
  return raw
read(PREFIX,'a5712f1655f68e6f8fe7cacbfb454dc0be0cd1ad8f22f1788fbad7b8adafae29')
if os.environ.get('PYTHONPYCACHEPREFIX')!=str(PREFIX) or not sys.flags.no_site or not sys.dont_write_bytecode:raise ValueError('guarded Python required')
previous=json.loads(read(OLD/'coordinator-dispatch-0002.json','478e5ab1966aabe8c758121d51543b8366d8eb38558da54b9c3405fda2346864'))
selected=[]
for binding in previous['source_bindings']:
 if binding['root_id']=='repository':
  path=R/binding['relative_path']
  if any(path.is_relative_to(base) for base in (S/'contracts',DEP)):
   read(path,binding['sha256']);selected.append(binding)
sys.path[:0]=[str(S/'contracts'),str(DEP)]
from lab_contracts.codec import canonical,parse,Refusal
from lab_contracts.validation import validate


def fixtures():
 base={'kind':'evidence','root_id':'fixture','relative_path':'proof.json','sha256':'a'*64,'size_bytes':10}
 vectors=[]
 def binding(name,updates,expected):
  value=base|updates
  try:validate('ByteBinding',value);admitted=True
  except ValueError:admitted=False
  if admitted!=expected:raise ValueError('fixture differs from selected foundation schema: '+name)
  vectors.append({'name':name,'type':'binding','raw_hex':canonical(value).hex(),'admitted':expected})
 binding('unicode_combining_and_non_bmp',{'root_id':'raiz e\u0301 🧪','relative_path':'fontes/e\u0301/🧪.json'},True)
 binding('precomposed_identity_distinct',{'root_id':'raiz é 🧪','relative_path':'fontes/é/🧪.json'},True)
 binding('escaped_exact_strings',{'root_id':'root\x00\n\t"\\','relative_path':'directory/line\n\t".json'},True)
 binding('root_4096_unicode_scalars',{'root_id':'🧪'*4096},True)
 binding('path_4096_unicode_scalars',{'relative_path':'é'*4096},True)
 binding('root_over_4096',{'root_id':'x'*4097},False)
 binding('path_over_4096',{'relative_path':'x'*4097},False)
 for size in [0,2**53-1,2**53,2**63-1]:binding('size_'+str(size),{'size_bytes':size},True)
 binding('negative_size',{'size_bytes':-1},False)
 for name,path in [('absolute','/x'),('dot','x/./y'),('dotdot','x/../y'),('empty_component','x//y'),('backslash','x\\y'),('nul','x\x00y'),('trailing_slash','x/'),('empty','')]:binding(name,{'relative_path':path},False)
 binding('empty_root',{'root_id':''},False)
 binding('unknown_kind',{'kind':'caller-invented'},False)
 for name,value in [('minimum_i64',-(2**63)),('maximum_i64',2**63-1),('unicode_and_escapes',{'🧪':'e\u0301\n\t\x00"\\','é':'é','e\u0301':'e\u0301'})]:
  raw=canonical(value);vectors.append({'name':name,'type':'canonical','raw_hex':raw.hex(),'admitted':True})
 for name,raw in [('over_i64',b'9223372036854775808'),('under_i64',b'-9223372036854775809'),('negative_zero',b'-0'),('float',b'1.0'),('surrogate',b'"\\ud800"'),('invalid_utf8',b'"\xff"'),('duplicate',b'{"x":1,"x":1}')]:
  try:parse(raw);raise ValueError('foundation unexpectedly admitted '+name)
  except Refusal:pass
  vectors.append({'name':name,'type':'canonical','raw_hex':raw.hex(),'admitted':False})
 # The foundational parser can normalize spelling; durable control records
 # deliberately require the already selected canonical bytes without rewriting.
 vectors.append({'name':'noncanonical_escape_spelling','type':'canonical','raw_hex':b'"\\u00e9"'.hex(),'admitted':False})
 return {'schema_version':'lab-control-c01-compatibility-vectors/v1','foundation_inputs':[b for b in selected if b['relative_path'].endswith(('codec.py','schema_catalog.py','validation.py'))],'vectors':vectors}

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
 raw=canonical(fixtures())+b'\n';path=T/'c01-codec-vectors.json'
 if args.write:
  with path.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
 elif read(path)!=raw:raise ValueError('frozen vectors differ from accepted foundation')
 print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'PASS','checks':len(fixtures()['vectors']),'effect_state':'owned-inert','cleanup':'clean'}))
