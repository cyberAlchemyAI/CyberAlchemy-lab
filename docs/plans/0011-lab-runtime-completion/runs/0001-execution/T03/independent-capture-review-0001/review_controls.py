import ast,hashlib,importlib.abc,importlib.util,json,os,sys,tempfile,uuid
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T03/pure-source-capture-0001'
OUT=RUN.parent/'independent-capture-review-0001'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def binding(path):
 raw=path.read_bytes();return {'path':path.relative_to(ROOT).as_posix(),'sha256':sha(raw),'size_bytes':len(raw)}
manifest=RUN/'HANDOFF.json';assert sha(manifest.read_bytes())=='06e6e5de689e9188edafa66f1e1da05485c41678e0b46e0a8dab0e6fc835651a';h=json.loads(manifest.read_bytes())
checked=[]
for row in [h['capture'],h['source_manifest'],h['postimage_selection'],h['terminal'],*h['evidence']]:
 assert binding(ROOT/row['path'])==row;checked.append(row)
source=json.loads((ROOT/h['source_manifest']['path']).read_bytes())
for row in source['files']:assert binding(ROOT/row['path'])==row
selection=json.loads((ROOT/h['postimage_selection']['path']).read_bytes())
changed_allowed={'source/base.py':{'original','verify_source'},'reader/reader.py':{'guard'},'mapped/base.py':{'verify_source'},'context/base.py':{'preflight'},'context/generation.py':{'selected_mapping'}}
unchanged_functions=[]
for item in selection['postimages']:
 for field in ['original','postimage']:assert binding(ROOT/item[field]['path'])==item[field]
 assert item['selected_now'] is False
 old=ast.parse((ROOT/item['original']['path']).read_bytes());new=ast.parse((ROOT/item['postimage']['path']).read_bytes())
 suffix='/'.join(item['postimage']['path'].split('/')[-2:]);allowed=changed_allowed[suffix]
 def functions(tree):return {(getattr(node,'name',''),getattr(parent,'name','')):ast.dump(node,include_attributes=False) for parent in [tree,*[x for x in tree.body if isinstance(x,ast.ClassDef)]] for node in parent.body if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))}
 oldf=functions(old);newf=functions(new)
 for key,value in oldf.items():
  if key[0] not in allowed:assert newf[key]==value;unchanged_functions.append(suffix+':'+'.'.join(reversed(key)).strip('.'))
code=ROOT/h['capture']['path'];raw=code.read_bytes();pin=h['capture']['sha256']
class Loader(importlib.abc.SourceLoader):
 selected_source_sha256=pin
 def get_filename(self,name):return str(code)
 def get_data(self,path):assert path==str(code);return raw
 def get_code(self,name):return compile(raw,str(code),'exec',dont_inherit=True)
name='_independent_T03_capture_'+uuid.uuid4().hex
spec=importlib.util.spec_from_file_location(name,code,loader=Loader());K=importlib.util.module_from_spec(spec);sys.modules[name]=K;spec.loader.exec_module(K)
cases=[]
def refused(label,operation):
 n=len(os.listdir('/proc/self/fd'))
 try:operation()
 except (ValueError,OSError):pass
 else:raise AssertionError(label+' accepted')
 assert n==len(os.listdir('/proc/self/fd'));assert not getattr(K._ACTIVE,'value',False);cases.append({'case':label,'result':'PASS-refused'})
with tempfile.TemporaryDirectory(prefix='cal-T03-independent-') as td:
 root=Path(td);os.chmod(root,0o700);(root/'parent').mkdir(mode=0o700)
 for n in ['a','b']:(root/'parent'/n).write_bytes(b'inert independent '+n.encode())
 rows=[{'path':'parent/'+n,'sha256':sha((root/'parent'/n).read_bytes())} for n in ['a','b']]
 assert K.verify_all(root,rows,code_sha256=pin)==2;assert K.capture_one(root,rows[0],code_sha256=pin)==(root/rows[0]['path']).read_bytes();cases.append({'case':'complete fresh owned rows and exact capture','result':'PASS'})
 refused('independent pin required',lambda:K.verify_all(root,rows,code_sha256=None))
 refused('digest change',lambda:K.verify_all(root,[dict(rows[0],sha256='0'*64)],code_sha256=pin))
 refused('duplicate locator',lambda:K.verify_all(root,rows+[rows[0]],code_sha256=pin))
 refused('external absolute locator unselected',lambda:K.verify_all(root,[dict(rows[0],path=str(root/rows[0]['path']))],code_sha256=pin))
 external=dict(rows[0],path=str(root/rows[0]['path']));assert K.verify_all(root,[external],code_sha256=pin,selected_external=[external])==1;cases.append({'case':'explicit selected external row','result':'PASS'})
 # Replace actual own leaf at batch finalcheck, samebytes but new inode.
 observed=False;mid=3;target=K.Batch.check.__code__;calls=0
 def probe(code,offset):
  global calls,observed
  if code is target:
   calls+=1
   if calls==2:
    leaf=root/'parent/a';body=leaf.read_bytes();leaf.rename(root/'parent/a-retained');leaf.write_bytes(body);observed=True
 sys.monitoring.use_tool_id(mid,'independent own T03 finalcheck mutation');sys.monitoring.register_callback(mid,sys.monitoring.events.PY_START,probe);sys.monitoring.set_local_events(mid,target,sys.monitoring.events.PY_START)
 try:refused('actual late samebyte owned leaf replacement',lambda:K.verify_all(root,rows,code_sha256=pin))
 finally:sys.monitoring.set_local_events(mid,target,0);sys.monitoring.register_callback(mid,sys.monitoring.events.PY_START,None);sys.monitoring.free_tool_id(mid)
 assert observed
 for row in [h['capture'],h['source_manifest'],h['postimage_selection'],h['terminal'],*h['evidence']]:assert binding(ROOT/row['path'])==row
report={'schema_version':'lab-T03-independent-pure-capture-controls/v1-candidate','authority_effect':'none','task_complete':False,'original_runtime_callbacks_modified':False,'Lab_constructors_executed':False,'source_rows_rechecked':len(source['files']),'all_original_postimage_preimages_checked':True,'unchanged_AST_functions':unchanged_functions,'independent_cases':cases,'read_only_selections':checked,'result':'PASS-component-only'}
(OUT/'controls-result.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
print(json.dumps({'result':report['result'],'cases':len(cases),'source_rows':len(source['files']),'unchanged_functions':len(unchanged_functions),'output_sha256':sha((OUT/'controls-result.json').read_bytes())}))
