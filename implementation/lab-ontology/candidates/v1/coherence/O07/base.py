"""Pinned original-byte inputs, candidate write roots and before-effect checks."""
import base64,copy,hashlib,importlib.util,json,re,sys
from pathlib import Path,PurePosixPath
HERE=Path(__file__).resolve().parent
ONTOLOGY=HERE.parents[1]
ROOT=ONTOLOGY.parents[3]
RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
CONTEXT={'path':str((RUN/'context-O07.json').relative_to(ROOT)),'sha256':'3f59d0390ffc05f2843c511e6d5a733866146fcdb536f21178a2f59f30a39040'}
ORIGINAL=ONTOLOGY/'migration/candidate/0001'
PREPARED=ONTOLOGY/'review/O06/packages/0001'
QUERY=ONTOLOGY/'queries/successors/0009'
QUERY_PIN={'path':str((QUERY/'packages/0001/selection.json').relative_to(ROOT)),'sha256':'5dce634a00ac7ff99f4319332d36ca77ee2c5850244d016b4bf778b705db9cf3'}
COVERAGE=ONTOLOGY/'coverage/coherence/0001'
RECEIPTS=['implementation/lab-ontology/candidates/v1/review/O06/receipts/0001.json','implementation/lab-workflows/candidates/v1/episodes/W09/receipts/0001.json',
 'implementation/lab-ontology/candidates/v1/receipts/query-coverage.json','implementation/lab-ontology/candidates/v1/receipts/O05/0001.json',
 'implementation/lab-continuity/candidates/v1/receipts/C13/0002.json','implementation/lab-ontology/candidates/v1/receipts/O02/0004.json']
OLD_RESULTS={'historical-d73-slice':ONTOLOGY/'coverage/questions/0017-historical/result.json','d75-selected-source':ONTOLOGY/'coverage/questions/0015-D75/result.json',
 'O05-source-interpretation':ONTOLOGY/'coverage/questions/0014-native/result.json'}
def require(v,msg):
 if not v:raise ValueError(msg)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(v):return (json.dumps(v,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()
def parse(raw):
 def pairs(rows):
  v={}
  for k,x in rows:require(k not in v,'duplicate JSON field');v[k]=x
  return v
 return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('nonfinite JSON')))
def binding(p):
 p=Path(p);return {'path':p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else p.as_posix(),'sha256':sha(p.read_bytes())}
def bound(b,external=False):
 require(type(b) is dict and set(b)=={'path','sha256'},'closed file binding required')
 name=b['path'];require(type(name) is str and '\\' not in name and re.fullmatch('[0-9a-f]{64}',b['sha256']),'invalid selected binding')
 relative=PurePosixPath(name);require(relative.as_posix()==name and '..' not in relative.parts and (not relative.is_absolute() or external),'unsafe selected path')
 p=Path(name) if relative.is_absolute() else ROOT/name
 require(p.is_file() and not p.is_symlink() and not any(x.is_symlink() for x in p.parents),'missing or unsafe original file')
 require(external or p.resolve().is_relative_to(ROOT),'original path escaped repository')
 raw=p.read_bytes();require(sha(raw)==b['sha256'],'original bytes changed: '+name);return raw
def original(b,external=False):return parse(bound(b,external))
def load(p):return parse(Path(p).read_bytes())
def emit(p,v):
 p=Path(p);require(p.resolve().is_relative_to(HERE) or p.resolve().is_relative_to(COVERAGE) or p==ONTOLOGY/'receipts/coherence-closure.json','outside candidate write scope')
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(encoded(v))
def module(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def source_guard(manifest_pin):
 require(binding(HERE/'manifest.json')['sha256']==manifest_pin,'independent coherence manifest differs')
 value=load(HERE/'manifest.json');require(value['authority_effect']=='none' and value['actual_owner_outcome'] is None,'candidate source closure required')
 for b in value['files']:bound(b,external=True)
 expected={b['path'] for b in value['files'] if str(HERE.relative_to(ROOT))+'/' in b['path'] and Path(b['path']).parent==HERE.relative_to(ROOT)}
 actual={binding(p)['path'] for p in HERE.iterdir() if p.is_file() and p.name!='manifest.json'}
 require(actual==expected,'coherence control file closure changed')
 ctx=original(CONTEXT);require(ctx['strict_coverage']=='PASS','strict context coverage required')
 for b in ctx['source_bindings']:bound(b)
 exe=ctx['execution_locator_binding'];bound(exe,external=True);return ctx
