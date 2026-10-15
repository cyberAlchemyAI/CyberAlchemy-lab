"""Preparation code/metadata controls only. No staging/capture main or runtime."""
import ast,copy,hashlib,json,sys,types,uuid
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');OUT=Path(__file__).absolute().parent
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution';CAP=RUN/'T07/api17-task-local-capture-0003';API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v17'
CPIN='fe7cf43fbd239b88d5b524ff62c3729e96afb5d44cb2fac2c4ba41208e94e665';SPIN='05556b7b82b8480eb248de9b81772b2ede44733a814f1db8af9bcb506e92c5c8'
def sha(raw):return hashlib.sha256(raw).hexdigest()
sources={}
def exact(path,pin=None):
 raw=path.read_bytes();assert pin is None or sha(raw)==pin,str(path)
 row={'path':str(path.relative_to(ROOT)),'sha256':sha(raw),'size_bytes':len(raw)}
 assert sources.get(row['path'],row)==row;sources[row['path']]=row;return raw
def load(path,pin=None):return json.loads(exact(path,pin))
cap_raw=exact(CAP/'capture.py',CPIN);selector_raw=exact(RUN/'T02/prepare-current-selectors-0002.py',SPIN)
C=types.ModuleType('_T07_independent_preparation_'+uuid.uuid4().hex);C.__file__=str(CAP/'capture.py');sys.modules[C.__name__]=C
exec(compile(cap_raw,C.__file__,'exec'),C.__dict__)
cases=[]
def passed(name):cases.append({'case':name,'result':'PASS'})
def refuses(name,callback):
 try:callback()
 except (AssertionError,KeyError,ValueError,TypeError,OSError):passed(name);return
 raise AssertionError('accepted invalid case '+name)
F=ROOT/'product/lab/release-candidates/v1/interface/current-session-fixtures-v1-completion-0001/instances'
legacy_path=F/'legacy-diagnostic-0001/runtime/runtime-selection.json';current_path=F/'diagnostic-0004/runtime/runtime-selection.json'
legacy=load(legacy_path,'2bcd884a27bde0942195b0db76a9453337e91fe6e1a52c05afda272d70de147f');current=load(current_path,'d8a8b87f45702558ad9bf8df580fb5b554d2cd04f72dbaa35a39216e4f2785b9')
for label,path,d in [('legacy',legacy_path,legacy),('Source8',current_path,current)]:
 roles=C.family_roles(d,str(path.relative_to(ROOT)));assert set(roles)=={'source','reader','mapped','context'};passed('actual '+label+' closed descriptor role selection')
 for case,change in [('extra descriptor field',lambda v:v.update(unselected=True)),('wrong version',lambda v:v.update(schema_version='unknown')),('foreign instance syntax',lambda v:v.update(instance='same_name'))]:
  invalid=copy.deepcopy(d);change(invalid);refuses(label+' '+case+' refuses',lambda:C.family_roles(invalid,str(path.relative_to(ROOT))))
 invalid=copy.deepcopy(d)
 if label=='legacy':invalid['bindings']['unselected']={'path':'other','sha256':'0'*64}
 else:invalid['source_binding']['unselected']=True
 refuses(label+' open role binding refuses',lambda:C.family_roles(invalid,str(path.relative_to(ROOT))))
 invalid=copy.deepcopy(d)
 row=invalid['bindings']['source'] if label=='legacy' else invalid['source_binding'];row['path']=row['path'].replace('/source/','/reader/')
 refuses(label+' role moved outside selected origin refuses',lambda:C.family_roles(invalid,str(path.relative_to(ROOT))))
for alias in ['../other','a/../other','a//other','/absolute/other','a\\other','./other','a/./other','.','']:
 refuses('family alias '+repr(alias)+' refuses',lambda:C.closed_family_binding({'path':alias,'sha256':'0'*64}))
for pin in [None,'x'*64,'A'*64,'0'*63]:
 refuses('malformed independent family pin '+repr(pin)+' refuses',lambda:C.closed_family_binding({'path':'a/b.json','sha256':pin}))

# Optimized descriptor support: inert in-memory metadata clone only, no actual
# pending family descriptor is fabricated or consumed by a runtime.
name='inert-review-only';new_family=str((RUN/'T02/optimized-family-preparation-0002/instances'/name).relative_to(ROOT))
old_family=str(current_path.parents[1].relative_to(ROOT))
synthetic=json.loads(json.dumps(current).replace(old_family,new_family));synthetic['instance']=name;synthetic['public_source_name']='completion-current-participation:'+name
synthetic['optimized_capture_selection_binding']={'path':'docs/inert-review-selection.json','sha256':'0'*64};synthetic['original_frozen_family_unchanged']=True
assert set(C.family_roles(synthetic,new_family+'/runtime/runtime-selection.json'))=={'source','reader','mapped','context'}
passed('explicit optimized descriptor shape accepts inert metadata only')
invalid=copy.deepcopy(synthetic);invalid['original_frozen_family_unchanged']=False
refuses('optimized predecessor identity claim refuses',lambda:C.family_roles(invalid,new_family+'/runtime/runtime-selection.json'))

# Original source/profile literal tables and saved API capture2 metadata.
parent=API.parent/'api-integration-v16'
source=load(parent/'source-manifest.json','8ac40a51e23b8e528178807792b8ae477aa9c46cd50d92a5b1522c82945413c7')
profile=load(parent/'contract-profile.json','8cc29da16d3881d8816cdc45c55358d9229fcaf226d1b9a757402ebc8675d18c')
assert len(source['files'])==24497 and len(profile['files'])==24496
profile_paths={r['path']for r in profile['files']};assert [r for r in source['files']if r['path']in profile_paths]==profile['files']
absent=load(RUN/'T07/accounting-0001/unavailable-original-inputs.json','4408c5433d41119a92660f86f856d6847be24171ddb1dab368e22c63ee294e7a')
unavailable={r['binding']['path']:r['binding']for r in absent['rows']};parent_by_path={r['path']:r for r in source['files']}
assert len(parent_by_path)==24497 and len(unavailable)==25 and all(parent_by_path[p]==r for p,r in unavailable.items())
retained=[r for r in source['files']if r['path']not in unavailable];assert len(retained)==24472
passed('full24497 source/full24496 profile rows and order retained; exact25 missing bindings stay provenance only')
prepins={'source-manifest.json':'a909f378b8a1c5f6f02fe6bcbafa56da7f2fe873a3865ab7853b443d57b249f2','contract-profile.json':'f5b411e7b59b9b50ac46dd7372aad086001dcabd214bf8eb639f8ab826886429','SCHEMA-EXECUTION-DEPENDENCIES.json':'c93c4cdecd3028d56a26c306c4ef4d144b90e72402bff9b616f8103a375db5f8','INPUT-ACCOUNTING.json':'0c023fa312e4ec974a1fd2e8de3347e071142ed82a7ad7f857c9d8e729bc9242'}
for fn,pin in prepins.items():assert exact(CAP/'preimage'/fn,pin)==exact(API/fn,pin)
assert exact(CAP/'capture-preparation-preimage-0003.py','e9c7fbe8ff32a4475ec95144b9261502c7bfd94ab428ae69c83ee3a28a9db9e5')
passed('four saved preimages equal unchanged API capture2 exact bytes; prior capture-code preimage exact')

# Evaluate the original nested add function in a pure metadata frame, with its
# actual source body and only new own inert files. Never execute capture.main.
tree=ast.parse(cap_raw);main=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='main');add_node=next(n for n in main.body if isinstance(n,ast.FunctionDef)and n.name=='add')
frame={**C.__dict__,'parent_by_path':parent_by_path,'unavailable':unavailable,'additions':{},'classes':{},'reasons':{}}
exec(compile(ast.Module(body=[add_node],type_ignores=[]),str(CAP/'capture.py'),'exec'),frame);add=frame['add']
missing=next(iter(unavailable.values()));refuses('actual add refuses required unavailable parent body',lambda:add(missing,'successor-family','owned pure test'))
changed=dict(source['files'][0]);changed['sha256']='0'*64
refuses('actual add refuses changed original parent row',lambda:add(changed,'successor-family','owned pure test'))
missing={'path':str((OUT/'never-created-input.json').relative_to(ROOT)),'sha256':'0'*64}
refuses('actual add refuses absent successor input body',lambda:add(missing,'successor-code','owned pure test'))
inert=OUT/'owned-inert-input.json';inert.write_bytes(b'{"review_owned":true}\n');binding={'path':str(inert.relative_to(ROOT)),'sha256':sha(inert.read_bytes())}
add(binding,'successor-code','owned pure test');wrong={**binding,'sha256':'0'*64}
refuses('actual add refuses conflicting successor digest',lambda:add(wrong,'successor-code','owned pure test'))

# Actual current selector transform statements run in memory. Prefix selection
# is supplied as the already independently pinned construction metadata value;
# this is a pure transform control, not a final descriptor/family qualification.
st=ast.parse(selector_raw);functions=[n for n in st.body if isinstance(n,ast.FunctionDef)]
ns={'ast':ast,'json':json,'hashlib':hashlib,'Path':Path,'ROOT':ROOT,'RUN':RUN,'API':API,'OLD_FAMILY':old_family,'OLD_CONTEXT_PIN':'6f1fb3fcd9f487b76f5e1708a7bda1b157a4bbbb42bfef1e3baae9f350410071'}
exec(compile(ast.Module(body=functions,type_ignores=[]),str(RUN/'T02/prepare-current-selectors-0002.py'),'exec'),ns)
old_manifest=load(CAP/'preimage/source-manifest.json',prepins['source-manifest.json']);old_rows={r['path']:r for r in old_manifest['files']}
texts={fn:exact(API/fn,old_rows[str((API/fn).relative_to(ROOT))]['sha256']).decode()for fn in ['source_bridge.py','current_context_sessions.py','authentication.schema.json','machine_auth_scope.py']}
original_texts=dict(texts);native_store='completion-optimized-source8-0002-'+name
ns.update(texts=texts,descriptor=synthetic,name=name,new_family=new_family,selected={k:synthetic[k]for k in ['context_source_binding','mapper_package_binding']},native_store=native_store)
start=next(i for i,n in enumerate(st.body)if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id=='source')
stop=next(i for i,n in enumerate(st.body)if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id=='out')
exec(compile(ast.Module(body=st.body[start:stop],type_ignores=[]),str(RUN/'T02/prepare-current-selectors-0002.py'),'exec'),ns)
assert set(texts)==set(original_texts)
source_ast=ast.parse(texts['source_bridge.py']);old_ast=ast.parse(original_texts['source_bridge.py'])
constants={n.targets[0].id:ast.literal_eval(n.value)for n in source_ast.body if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id.startswith('CURRENT_')}
assert constants['CURRENT_SOURCE8_STORE']==native_store and constants['CURRENT_SOURCE8_NAME']==synthetic['public_source_name']
for n in source_ast.body:
 if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id.startswith('CURRENT_SOURCE8_'):
  old=next(x for x in old_ast.body if isinstance(x,ast.Assign)and isinstance(x.targets[0],ast.Name)and x.targets[0].id==n.targets[0].id);n.value=old.value
 if isinstance(n,ast.FunctionDef)and n.name=='current_session_fixture_delivery':n.body=next(x.body for x in old_ast.body if isinstance(x,ast.FunctionDef)and x.name==n.name)
assert ast.dump(source_ast)==ast.dump(old_ast)
assert ast.dump(ast.parse(texts['current_context_sessions.py'].replace(new_family,old_family)))==ast.dump(ast.parse(original_texts['current_context_sessions.py']))
assert json.loads(texts['authentication.schema.json'].replace(synthetic['public_source_name'],current['public_source_name']))==json.loads(original_texts['authentication.schema.json'])
machine=ast.parse(texts['machine_auth_scope.py']);old_machine=ast.parse(original_texts['machine_auth_scope.py'])
mapping=next(n for n in machine.body if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id=='RUNTIMES');values=ast.literal_eval(mapping.value)
assert values['current_context_sessions.py']==(str(ROOT/new_family/'context'),synthetic['context_source_binding']['sha256'])
assert API.parent/values['current_context_sessions.py'][0]==ROOT/new_family/'context'
mapping.value=next(n.value for n in old_machine.body if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id=='RUNTIMES')
assert ast.dump(machine)==ast.dump(old_machine)
passed('actual four in-memory selector transforms preserve every unrelated legacy selector/guard/callback and use absolute new Context origin')
assert '_cal_api17_current_source8_'+name.replace('-','_') in texts['source_bridge.py']
assert all(ast.dump(n)==ast.dump(next(o for o in old_ast.body if isinstance(o,ast.Assign)and isinstance(o.targets[0],ast.Name)and o.targets[0].id==n.targets[0].id))for n in source_ast.body if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id.startswith('CURRENT_LEGACY_'))
passed('new unique Source8 namespace and all legacy constants preserved')
assert any(isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id=='native_store'and ast.dump(n.value)==ast.dump(ast.parse("construction['prefix']",mode='eval').body)for n in st.body)
passed('current05556 selector independently takes actual construction prefix; earlier prefix inference is historical resolved code')

# Complete new Python origins are added to the schema set, while original
# parent schema rows and missing-source refusal remain independently retained.
profile_py={r['path']for r in source['files']if r['path'].endswith('.py')};new_py={p for p in frame['additions']if p.endswith('.py')}
assert "(path in additions and path.endswith('.py'))" in cap_raw.decode()
assert "for row in original['files']+[additions[path]for path in sorted(additions)]" in cap_raw.decode()
assert "'historical_original_physical_closure':'REFUSED'" in cap_raw.decode()
assert "assert set(actual_api)==set(expected_api)" in cap_raw.decode()
assert "runtime['instance'] not in seen_family_names" in cap_raw.decode() and "family['path'] not in seen_family_paths" in cap_raw.decode()
passed('capture code retains full accounting/history order, independently expected complete API set, every added Python origin, and refusal ceilings')
# Additive current helper expectation block: actual complete unchanged seven
# inputs, then malformed/missing/extra/duplicate/alias/digest refusals. No helper
# function or real runtime constructor is ever executed.
prep=load(CAP/'PREPARATION-revision-0005.json');expected=prep['helper_expected_files']
assert len(expected)==7
oldcap=exact(CAP/'capture-preparation-preimage-0004.py','8ef1c32e039d50b93a53ba84a79e0638844f4809aa24a2911e98a528a2ebbc0f')
oldtree=ast.parse(oldcap);oldfunctions={n.name:ast.dump(n)for n in oldtree.body if isinstance(n,ast.FunctionDef)and n.name!='main'}
newfunctions={n.name:ast.dump(n)for n in tree.body if isinstance(n,ast.FunctionDef)and n.name!='main'}
assert oldfunctions==newfunctions
passed('additive helper change preserves every other capture function and exact8ef1 predecessor')
first=next(i for i,n in enumerate(main.body)if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id=='expected_helpers')
last=next(i for i,n in enumerate(main.body)if isinstance(n,ast.Assert)and 'current_family_selections' in ast.unparse(n))
helper_code=compile(ast.Module(body=main.body[first:last],type_ignores=[]),str(CAP/'capture.py'),'exec')
def check_helpers(rows):
 current_frame={**frame,'selection':{'helper_expected_files':rows}}
 exec(helper_code,current_frame)
check_helpers(expected);passed('actual complete helper expectation block accepts all7 independently selected unchanged bytes')
refuses('helper missing expected body row refuses',lambda:check_helpers(expected[:-1]))
refuses('helper duplicate expected origin refuses',lambda:check_helpers(expected+[expected[0]]))
refuses('helper unselected extra expected origin refuses',lambda:check_helpers(expected+[{'path':'unused/extra.py','sha256':'0'*64}]))
aliased=copy.deepcopy(expected);aliased[0]['path']=aliased[0]['path'].replace('/interface/','/interface//')
refuses('helper aliased expected origin refuses',lambda:check_helpers(aliased))
wrong=copy.deepcopy(expected);wrong[0]['sha256']='0'*64
refuses('helper wrong expected digest refuses',lambda:check_helpers(wrong))
for row in expected:exact(ROOT/row['path'],row['sha256'])
passed('all7 helper bodies fresh independently selected; no current code self-capture trust')
for path,row in list(sources.items()):exact(ROOT/path,row['sha256'])
report={'schema_version':'lab-T07-capture3-independent-preparation-controls/v1-candidate','verdict':'PASS-preparation-code-only','checks':cases,'checks_count':len(cases),'source_binding':{'path':str((CAP/'capture.py').relative_to(ROOT)),'sha256':CPIN},'selector_binding':{'path':str((RUN/'T02/prepare-current-selectors-0002.py').relative_to(ROOT)),'sha256':SPIN},'source_rows':24497,'profile_rows':24496,'original_source_profile_common_order_preserved':True,'original_missing_bindings':25,'retained_original_present_rows':24472,'sources':list(sources.values()),'all_selected_source_metadata_fresh_entry_exit':True,'synthetic_descriptor_is_inert_metadata_only':True,'actual_capture_or_selector_main_executed':False,'final_component_selection_or_new_family_descriptor_qualified':False,'actual_Lab_Source_Service_Session_or_native_constructed':False,'runtime_lock_acquired':False,'authority_effect':'none','task_complete':False}
path=OUT/'pure-controls-result-0002.json';path.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps({'result':report['verdict'],'checks':len(cases),'sources':len(sources),'report':str(path),'sha256':sha(path.read_bytes())}),flush=True)
