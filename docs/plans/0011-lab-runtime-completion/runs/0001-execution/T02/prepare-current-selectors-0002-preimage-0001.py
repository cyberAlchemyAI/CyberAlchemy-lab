"""Stage four exact current-family selector postimages; never edit API17."""
import argparse,ast,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).absolute().parents[6]
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v17'
OLD_FAMILY='product/lab/release-candidates/v1/interface/current-session-fixtures-v1-completion-0001/instances/diagnostic-0004'
OLD_CONTEXT_PIN='6f1fb3fcd9f487b76f5e1708a7bda1b157a4bbbb42bfef1e3baae9f350410071'
OLD_MAPPING_PIN='6be0b93a1fd58aa9c4f86a90125afd7563d1b6a17c33612d83c82ba7989522b6'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def binding(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes())}
def exact(path,pin):
 raw=path.read_bytes();assert sha(raw)==pin,str(path)
 return raw
def literal(text,name,value):
 nodes=[n for n in ast.parse(text).body if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id==name]
 assert len(nodes)==1,name
 n=nodes[0].value;assert isinstance(ast.literal_eval(n),str)
 lines=text.splitlines(keepends=True);start=sum(map(len,lines[:n.lineno-1]))+n.col_offset;end=sum(map(len,lines[:n.end_lineno-1]))+n.end_col_offset
 return text[:start]+repr(value)+text[end:]
parser=argparse.ArgumentParser();parser.add_argument('--runtime-selection',required=True);parser.add_argument('--runtime-selection-sha256',required=True)
args=parser.parse_args();p=Path(args.runtime_selection)
assert not p.is_absolute() and p.as_posix()==args.runtime_selection and '..' not in p.parts
descriptor=json.loads(exact(ROOT/p,args.runtime_selection_sha256))
assert descriptor['schema_version']=='lab-current-session-runtime-selection/v1-candidate'
assert descriptor['authority_effect']=='none' and descriptor['actual_owner_outcome'] is None and descriptor['shared_API_qualified'] is False
name=descriptor['instance'];assert re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',name)
assert descriptor['public_source_name']=='completion-current-participation:'+name
selected={}
for key in ['source_binding','source_package_binding','reader_binding','mapper_binding','mapper_package_binding','context_source_binding','context_package_binding','implementation_binding','period_binding']:
 row=descriptor[key];assert set(row)=={'path','sha256'} and re.fullmatch('[a-f0-9]{64}',row['sha256'])
 path=Path(row['path']);assert not path.is_absolute() and path.as_posix()==row['path'] and '..' not in path.parts
 exact(ROOT/path,row['sha256']);selected[key]=row
new_family=str(Path(selected['source_binding']['path']).parents[1]);assert new_family.startswith(str(RUN.relative_to(ROOT))+'/T02/optimized-family-preparation-0001/instances/')
old_manifest=json.loads(exact(API/'source-manifest.json','a909f378b8a1c5f6f02fe6bcbafa56da7f2fe873a3865ab7853b443d57b249f2'))
old_files={row['path']:row for row in old_manifest['files']}
texts={}
for fn in ['source_bridge.py','current_context_sessions.py','authentication.schema.json','machine_auth_scope.py']:
 row=old_files[str((API/fn).relative_to(ROOT))];texts[fn]=exact(API/fn,row['sha256']).decode('utf-8')
source=texts['source_bridge.py']
for key,value in {'CURRENT_SOURCE8_NAME':descriptor['public_source_name'],'CURRENT_SOURCE8_STORE':'completion-current-session-0001-'+name,'CURRENT_SOURCE8_CONTEXT':new_family+'/context','CURRENT_SOURCE8_READER':new_family+'/reader','CURRENT_SOURCE8_SOURCE':new_family+'/source','CURRENT_SOURCE8_DELIVERY_PIN':selected['context_source_binding']['sha256']}.items():source=literal(source,key,value)
assert source.count('_cal_api17_current_source8_diagnostic0004')==1
source=source.replace('_cal_api17_current_source8_diagnostic0004','_cal_api17_current_source8_'+name.replace('-','_'))
texts['source_bridge.py']=source
context=texts['current_context_sessions.py'];context=literal(context,'DELIVERY_PIN',selected['context_source_binding']['sha256']);context=literal(context,'MAPPING_PIN',selected['mapper_package_binding']['sha256'])
assert context.count(OLD_FAMILY+'/reader')==3;context=context.replace(OLD_FAMILY+'/reader',new_family+'/reader');texts['current_context_sessions.py']=context
auth=texts['authentication.schema.json'];old_name='completion-current-participation:diagnostic-0004';assert auth.count(old_name)==4;texts['authentication.schema.json']=auth.replace(old_name,descriptor['public_source_name']);json.loads(texts['authentication.schema.json'])
machine=texts['machine_auth_scope.py'];old_tuple=repr('current-session-fixtures-v1-completion-0001/instances/diagnostic-0004/context')+','+repr(OLD_CONTEXT_PIN)
assert machine.count(old_tuple)==1
new_tuple=repr(str(ROOT/new_family/'context'))+','+repr(selected['context_source_binding']['sha256'])
texts['machine_auth_scope.py']=machine.replace(old_tuple,new_tuple)
out=RUN/'T02'/'current-selector-staging-0002';assert not out.exists();out.mkdir();(out/'preimage').mkdir();(out/'postimages').mkdir();rows=[]
for fn,text in texts.items():
 if fn.endswith('.py'):ast.parse(text)
 target=API/fn;pre=out/'preimage'/fn;post=out/'postimages'/fn
 pre.write_bytes(target.read_bytes());post.write_text(text)
 rows.append({'target':str(target.relative_to(ROOT)),'preimage':binding(pre),'postimage':binding(post)})
ledger={'schema_version':'lab-T02-current-selector-staging/v2-candidate','authority_effect':'none','task_complete':False,'runtime_selection_binding':{'path':args.runtime_selection,'sha256':args.runtime_selection_sha256},'actual_API_modified':False,'rows':rows,'delta':'Only exact independently selected new Source8 name/store/paths/pins/unique module namespace, four closed authentication enum names, and absolute new Context path in current-only Machine runtime map. Legacy selectors, policy/nonce/deadline/budget/class/role/effect guards and all other code remain unchanged. Source/profile import eligibility must be captured independently after Root application.'}
with (out/'patch-ledger.json').open('x') as f:json.dump(ledger,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps({'status':'STAGED-only','rows':len(rows),'ledger':binding(out/'patch-ledger.json')}))
