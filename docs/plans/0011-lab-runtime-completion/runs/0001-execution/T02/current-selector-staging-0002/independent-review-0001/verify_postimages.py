"""Exact staged bytes/AST/selection review; no runtime or application."""
import ast,hashlib,json,re,sys
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution';STAGE=RUN/'T02/current-selector-staging-0002';OUT=Path(__file__).absolute().parent;API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v17';FAMILY=RUN/'T02/optimized-family-preparation-0002/instances/optimized-0002'
sources={};checks=[]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def exact(path,pin=None):
 assert path.is_file() and not path.is_symlink() and not any(p.is_symlink()for p in path.parents)
 raw=path.read_bytes();assert pin is None or sha(raw)==pin,str(path)
 row={'path':str(path.relative_to(ROOT)),'sha256':sha(raw),'size_bytes':len(raw)};assert sources.get(row['path'],row)==row;sources[row['path']]=row;return raw
def load(path,pin=None):return json.loads(exact(path,pin))
def binding(row):return exact(ROOT/row['path'],row['sha256'])
def passed(name):checks.append({'case':name,'result':'PASS'})
ledger=load(STAGE/'patch-ledger.json','c63786e305d4e3edacb49bbd72882bec861b278428a43a2379dd3508db2a68cb')
runtime=json.loads(binding(ledger['runtime_selection_binding']));assert ledger['runtime_selection_binding']['sha256']=='6004ecf7533954ee180f87186f46339b4e66a9c816252c40edf6ed2f98ea13bd'
construction=json.loads(binding(ledger['construction_selection_binding']));assert ledger['construction_selection_binding']['sha256']=='dd4d42e28f8e1027cf4876f045ad3b1420ecfe437d69294c19bacec595433993'
acceptance=load(FAMILY.parents[1]/'root-family-acceptance-0001.json');binding(acceptance['final_verification_binding']);binding(acceptance['terminal_binding'])
assert acceptance['result']=='PASS-complete-owned-native-family-only' and acceptance['runtime_selection_binding']==ledger['runtime_selection_binding'] and acceptance['all_actual_phase_exit_codes']==[0]*7
assert acceptance['all_role_and_package_row_occurrences_verified']==6743 and acceptance['whole_learning_or_API_or_owner_qualified']is False
assert runtime['instance']==construction['instance']=='optimized-0002' and runtime['public_source_name']==construction['public_source_name']=='completion-current-participation:optimized-0002'
assert ledger['native_store']==construction['prefix']==acceptance['actual_native_store_id']=='completion-optimized-source8-0002-optimized-0002'
for k in ['source_binding','source_package_binding','reader_binding','mapper_binding','mapper_package_binding','context_source_binding','context_package_binding','implementation_binding','period_binding']:binding(runtime[k])
assert runtime['source_binding']['sha256'].startswith('ff741a6d') and runtime['source_package_binding']['sha256'].startswith('204a8072') and runtime['context_source_binding']['sha256'].startswith('aaea804b') and runtime['mapper_package_binding']['sha256'].startswith('698')
passed('actual6004/dd4/native store and accepted family metadata match exact staged selector inputs')
period=json.loads(binding(runtime['period_binding']));binding(period['original_expired_period_binding'])
assert period['authority_effect']=='none' and period['actual_owner_outcome']is None and period['principal_ref']=='principal:'+ledger['native_store']
passed('actual81b037 fixed period and original expired period preserved without renewal')
expected={'source_bridge.py','current_context_sessions.py','authentication.schema.json','machine_auth_scope.py'}
assert len(ledger['rows'])==4 and {Path(r['target']).name for r in ledger['rows']}==expected
pre={};post={};old_manifest=load(RUN/'T07/api17-task-local-capture-0003/preimage/source-manifest.json','a909f378b8a1c5f6f02fe6bcbafa56da7f2fe873a3865ab7853b443d57b249f2');old_rows={r['path']:r for r in old_manifest['files']}
for row in ledger['rows']:
 name=Path(row['target']).name;assert row['target']==str((API/name).relative_to(ROOT));assert ROOT/row['preimage']['path']==STAGE/'preimage'/name and ROOT/row['postimage']['path']==STAGE/'postimages'/name
 pre[name]=binding(row['preimage']).decode();post[name]=binding(row['postimage']).decode()
 assert row['preimage']['sha256']==old_rows[row['target']]['sha256'] and exact(ROOT/row['target'],row['preimage']['sha256']).decode()==pre[name]
 if name.endswith('.py'):ast.parse(post[name])
passed('all4 actual preimage/postimage digests and exact target paths verified; actual API remains preimage bytes')

new_family=str(FAMILY.relative_to(ROOT));old_family='product/lab/release-candidates/v1/interface/current-session-fixtures-v1-completion-0001/instances/diagnostic-0004'
st=ast.parse(exact(RUN/'T02/prepare-current-selectors-0002.py','05556b7b82b8480eb248de9b81772b2ede44733a814f1db8af9bcb506e92c5c8'))
functions=[n for n in st.body if isinstance(n,ast.FunctionDef)]
frame={'ast':ast,'json':json,'hashlib':hashlib,'Path':Path,'ROOT':ROOT,'RUN':RUN,'API':API,'OLD_FAMILY':old_family,'OLD_CONTEXT_PIN':'6f1fb3fcd9f487b76f5e1708a7bda1b157a4bbbb42bfef1e3baae9f350410071','texts':dict(pre),'descriptor':runtime,'name':runtime['instance'],'new_family':new_family,'native_store':construction['prefix'],'selected':runtime}
exec(compile(ast.Module(body=functions,type_ignores=[]),str(RUN/'T02/prepare-current-selectors-0002.py'),'exec'),frame)
start=next(i for i,n in enumerate(st.body)if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id=='source');stop=next(i for i,n in enumerate(st.body)if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id=='out')
exec(compile(ast.Module(body=st.body[start:stop],type_ignores=[]),str(RUN/'T02/prepare-current-selectors-0002.py'),'exec'),frame)
assert frame['texts']==post
passed('actual4 postimage byte strings exactly reproduce reviewed05556 transform statements from real descriptor/construction metadata')

source=ast.parse(post['source_bridge.py']);old_source=ast.parse(pre['source_bridge.py'])
def constants(tree,prefix):return {n.targets[0].id:ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id.startswith(prefix)}
wanted={'CURRENT_SOURCE8_NAME':runtime['public_source_name'],'CURRENT_SOURCE8_STORE':construction['prefix'],'CURRENT_SOURCE8_CONTEXT':new_family+'/context','CURRENT_SOURCE8_READER':new_family+'/reader','CURRENT_SOURCE8_SOURCE':new_family+'/source','CURRENT_SOURCE8_DELIVERY_PIN':runtime['context_source_binding']['sha256']}
assert constants(source,'CURRENT_SOURCE8_')==wanted
assert constants(source,'CURRENT_LEGACY_')==constants(old_source,'CURRENT_LEGACY_')
for n in source.body:
 if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id in wanted:n.value=next(o.value for o in old_source.body if isinstance(o,ast.Assign)and isinstance(o.targets[0],ast.Name)and o.targets[0].id==n.targets[0].id)
 if isinstance(n,ast.FunctionDef)and n.name=='current_session_fixture_delivery':
  assert ast.unparse(n)=='def current_session_fixture_delivery():\n    return _current_delivery(\'_cal_api17_current_source8_optimized_0002\', ROOT / CURRENT_SOURCE8_CONTEXT, CURRENT_SOURCE8_DELIVERY_PIN)'
  n.body=next(o.body for o in old_source.body if isinstance(o,ast.FunctionDef)and o.name==n.name)
assert ast.dump(source)==ast.dump(old_source)
passed('six actual Source8 constants and unique namespace exact; every other Source bridge callback/legacy selector unchanged')
context=ast.parse(post['current_context_sessions.py']);old_context=ast.parse(pre['current_context_sessions.py'])
assert constants(context,'DELIVERY_PIN')=={'DELIVERY_PIN':runtime['context_source_binding']['sha256']} and constants(context,'MAPPING_PIN')=={'MAPPING_PIN':runtime['mapper_package_binding']['sha256']}
renames=0
for n in ast.walk(context):
 if isinstance(n,ast.Constant)and isinstance(n.value,str)and new_family+'/reader' in n.value:n.value=n.value.replace(new_family+'/reader',old_family+'/reader');renames+=1
assert renames==3
for n in context.body:
 if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id in ['DELIVERY_PIN','MAPPING_PIN']:n.value=next(o.value for o in old_context.body if isinstance(o,ast.Assign)and isinstance(o.targets[0],ast.Name)and o.targets[0].id==n.targets[0].id)
assert ast.dump(context)==ast.dump(old_context)
passed('actual Context aa ea delivery/698 mapper pins and three reader paths exact; all original Session/policy/nonce/deadline/budget/class/role/effect code unchanged')
auth=load(STAGE/'postimages/authentication.schema.json');old_auth=load(STAGE/'preimage/authentication.schema.json');assert post['authentication.schema.json'].count(runtime['public_source_name'])==4
assert json.loads(post['authentication.schema.json'].replace(runtime['public_source_name'],'completion-current-participation:diagnostic-0004'))==old_auth
passed('exactly4 authentication enum replacements; complete unrelated schema remains identical')
machine=ast.parse(post['machine_auth_scope.py']);old_machine=ast.parse(pre['machine_auth_scope.py']);values=constants(machine,'RUNTIMES')['RUNTIMES'];old_values=constants(old_machine,'RUNTIMES')['RUNTIMES']
assert values['current_context_sessions.py']==(str(FAMILY/'context'),runtime['context_source_binding']['sha256'])
assert API.parent/values['current_context_sessions.py'][0]==FAMILY/'context'
assert {k:v for k,v in values.items()if k!='current_context_sessions.py'}=={k:v for k,v in old_values.items()if k!='current_context_sessions.py'}
next(n for n in machine.body if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id=='RUNTIMES').value=next(n.value for n in old_machine.body if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id=='RUNTIMES')
assert ast.dump(machine)==ast.dump(old_machine)
passed('absolute current Machine Context tuple matches real producer origin; every original helper/guard callback and other runtime tuple unchanged')

selection_path=RUN/'T35/full-learning-inputs-0001/selection.json';selection=load(selection_path,'d1a1569c7e290d51f6c47cfecb611fa01b58d49599926558de887657b00f53aa');schema=load(RUN/'T35/full-learning-driver-0001/selection.schema.json')
sys.path.insert(0,str(ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004/deps'))
from jsonschema import Draft202012Validator
Draft202012Validator(schema).validate(selection)
assert selection['source_name']==runtime['public_source_name'] and selection['producer_root']==wanted['CURRENT_SOURCE8_CONTEXT'] and selection['source_pin']==runtime['source_binding']['sha256'] and selection['source_package_pin']==runtime['source_package_binding']['sha256'] and selection['period_binding']==runtime['period_binding'] and selection['runtime_selection_binding']==ledger['runtime_selection_binding']
assert selection['factory_module']=='source_bridge' and selection['factory_name']=='current_session_fixture_delivery'
for k in ['provider_binding','caller_boundary_binding','application_method_binding','assessment_method_binding']:binding(selection[k])
for row in [*selection['api_bootstrap_bindings'],*selection['lifecycle_bindings'].values()]:binding(row)
assert not any(k in selection for k in ['source_sha256','profile_sha256','API_source_binding','API_profile_binding'])
passed('actual d1a156 selection schema/pins/producer/factory/bootstrap/lifecycle origins exact and no global source/profile digest cycle')
driver=load(RUN/'T35/full-learning-driver-0001/source-manifest-0003.json','dbccd24d4b621f6f3c4495f686ea42120be36baa81a65a08f73574f5b75c0ed9');rows={r['path']:r for r in driver['files']}
for row in selection['lifecycle_bindings'].values():assert row=={k:rows[row['path']][k]for k in ['path','sha256']}
passed('actual lifecycle bodies remain exactly frozen55-row driver inputs')
for path,row in list(sources.items()):exact(ROOT/path,row['sha256'])
report={'schema_version':'lab-T02-actual-selector-independent-controls/v1-candidate','verdict':'PASS-exact-staged-postimages-and-input-selection','checks':checks,'checks_count':len(checks),'sources':list(sources.values()),'fresh_exact_sources_entry_exit':True,'patch_ledger_sha256':'c63786e305d4e3edacb49bbd72882bec861b278428a43a2379dd3508db2a68cb','input_selection_sha256':'d1a1569c7e290d51f6c47cfecb611fa01b58d49599926558de887657b00f53aa','scope':'four exact staged postimages and actual diagnostic input selection only','actual_API_modified_or_capture_executed':False,'Lab_Source_Service_Session_or_native_constructed':False,'lease_lock_acquired':False,'whole_learning_API_owner_or_release_qualified':False,'authority_effect':'none','task_complete':False}
path=OUT/'controls-result.json';path.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps({'result':report['verdict'],'checks':len(checks),'sources':len(sources),'sha256':sha(path.read_bytes())}),flush=True)
