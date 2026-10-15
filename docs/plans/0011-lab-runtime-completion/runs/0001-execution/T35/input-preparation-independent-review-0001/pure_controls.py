"""Actual preparation expressions only; no writer main, staging or runtime."""
import ast,hashlib,json,re,sys,types
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution';OUT=Path(__file__).absolute().parent;WRITER=RUN/'T35/prepare-full-learning-inputs-0001.py';HERE=RUN/'T35/full-learning-driver-0001';API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v17'
PIN='2934c6de5b0db15899142eb7a82a89ae30428b4c7841e397e11bcbcbd1d8564a'
RPIN='6004ecf7533954ee180f87186f46339b4e66a9c816252c40edf6ed2f98ea13bd';RPATH=RUN/'T02/optimized-family-preparation-0002/instances/optimized-0002/runtime/runtime-selection.json'
sources={};cases=[]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def observed(path,pin=None):
 raw=path.read_bytes();assert pin is None or sha(raw)==pin,str(path)
 row={'path':str(path.relative_to(ROOT)),'sha256':sha(raw),'size_bytes':len(raw)};assert sources.get(row['path'],row)==row;sources[row['path']]=row;return raw
def load(path,pin=None):return json.loads(observed(path,pin))
def passed(name):cases.append({'case':name,'result':'PASS'})
def refuses(name,callback):
 try:callback()
 except (AssertionError,ValueError,OSError,KeyError,TypeError):passed(name);return
 raise AssertionError('expected refusal '+name)
raw=observed(WRITER,PIN);tree=ast.parse(raw);defs=[n for n in tree.body if isinstance(n,ast.FunctionDef)]
frame={'ROOT':ROOT,'RUN':RUN,'API':API,'json':json,'hashlib':hashlib,'re':re,'Path':Path}
exec(compile(ast.Module(body=defs,type_ignores=[]),str(WRITER),'exec'),frame)
runtime=load(RPATH,RPIN);runtime_binding={'path':str(RPATH.relative_to(ROOT)),'sha256':RPIN}
frame['runtime']=runtime;frame['runtime_binding']=runtime_binding
for key in ['source_binding','source_package_binding','reader_binding','mapper_binding','mapper_package_binding','context_source_binding','context_package_binding','implementation_binding','period_binding']:
 body=frame['exact'](runtime[key]);assert body==observed(ROOT/runtime[key]['path'],runtime[key]['sha256'])
passed('all9 actual completed descriptor bindings verify exact public metadata bytes; no acceptance inference')
assert runtime['source_binding']['sha256']=='ff741a6debeeedd890e73014d52c673fd36a3da232e7c39e2e9696c69c59e617'
assert runtime['source_package_binding']['sha256']=='204a8072fd725f62c8e61058a6254d0118c937603e600139efa7cbace1e96f04'
assert runtime['period_binding']['sha256']=='81b03779ecc254e3b86ac534333709282a2d40f7c0f30c8966f3a47be4b532bc'
passed('actual Source/package/period ff741/204a/81b037 pins preserved exactly')
node=next(n for n in tree.body if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id=='source2')
exec(compile(ast.Module(body=[node],type_ignores=[]),str(WRITER),'exec'),frame)
source2raw=observed(RUN/'T07/api17-task-local-capture-0003/preimage/source-manifest.json','a909f378b8a1c5f6f02fe6bcbafa56da7f2fe873a3865ab7853b443d57b249f2')
assert frame['source2']==json.loads(source2raw);frame['source2_rows']={r['path']:r for r in frame['source2']['files']}
manifest=load(HERE/'source-manifest-0003.json','dbccd24d4b621f6f3c4495f686ea42120be36baa81a65a08f73574f5b75c0ed9');assert len(manifest['files'])==55
for row in manifest['files']:observed(ROOT/row['path'],row['sha256'])
frame['driver_rows']={r['path']:r for r in manifest['files']}
passed('immutable source2 a909 and complete55-row driver dbccd manifest independently checked')

# Execute only the original selection-dictionary expressions using actual
# independently selected public metadata. No selection file is authored here.
context=next(n for n in tree.body if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id=='context_root')
selection=next(n for n in tree.body if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id=='selection')
exec(compile(ast.Module(body=[context,selection],type_ignores=[]),str(WRITER),'exec'),frame);value=frame['selection']
schema=load(HERE/'selection.schema.json');driver_raw=observed(HERE/'driver.py');driver_tree=ast.parse(driver_raw)
fields=next(n.value for n in driver_tree.body if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id=='SELECTION_FIELDS')
expected_fields=eval(compile(ast.Expression(fields),str(HERE/'driver.py'),'eval'),{})
assert set(value)==expected_fields==set(schema['required'])==set(schema['properties'])
sys.path.insert(0,str(ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004/deps'))
from jsonschema import Draft202012Validator
validator=Draft202012Validator(schema);validator.validate(value)
passed('actual preparation dictionary exactly matches closed driver field contract and JSON Schema')
invalid={**value,'unselected':True};assert list(validator.iter_errors(invalid));passed('open selection field refuses under actual closed schema')
invalid=copy_value=json.loads(json.dumps(value));invalid['lifecycle_bindings']['unselected']=invalid['lifecycle_bindings']['positive'];assert list(validator.iter_errors(invalid));passed('open lifecycle selector refuses under actual closed schema')
family=RPATH.parents[1];assert value['producer_root']==str((family/'context').relative_to(ROOT))
assert value['source_name']==runtime['public_source_name']=='completion-current-participation:optimized-0002'
assert value['factory_module']=='source_bridge' and value['factory_name']=='current_session_fixture_delivery'
assert value['runtime_selection_binding']==runtime_binding and value['period_binding']==runtime['period_binding']
assert value['source_pin']==runtime['source_binding']['sha256'] and value['source_package_pin']==runtime['source_package_binding']['sha256']
passed('actual factory/source/producer/package/period paths and pins satisfy frozen driver comparisons')
assert {r['path']for r in value['api_bootstrap_bindings']}=={str((API/'__init__.py').relative_to(ROOT)),str((API/'guard.py').relative_to(ROOT))}
assert value['api_bootstrap_bindings'][1]['sha256']=='65ba71adb3b885f6fedc268be29f982f1f03139265f00a7e9ed08ff19b6adeb3'
assert value['provider_binding']['path']==str((API.parent/'source8-session-runtime-v1-action-0148/provider.py').relative_to(ROOT)) and value['provider_binding']['sha256']=='44152bf9496a98453be56c0eb7e302ea86b9fc7887c3cbcf5c9a0e69b7c4bf11'
assert value['caller_boundary_binding']['sha256']=='b2b171a48754ffcff9cda8dbac889b06bd0b2e0d32d3c75ad49c4d63aeaab7f8'
assert value['application_method_binding']['sha256']=='3a318632b5fc06fa15c855cf7f4833df6f4d547a8cedd5f99497fc09b3af0af6'
for key in ['provider_binding','caller_boundary_binding','application_method_binding','assessment_method_binding','period_binding']:
 row=value[key];observed(ROOT/row['path'],row['sha256'])
for row in [*value['api_bootstrap_bindings'],*value['lifecycle_bindings'].values()]:observed(ROOT/row['path'],row['sha256'])
assert set(value['lifecycle_bindings'])=={'positive','security'} and all(row['path']==str((HERE/(name+'_lifecycle.py')).relative_to(ROOT))for name,row in value['lifecycle_bindings'].items())
passed('actual original provider/caller/method pins and true two-bootstrap/two-lifecycle origins verified')

# Original reader defect preserved in an owned inert metadata file. Execute its
# actual read expression without authoring main; corrected expression refuses.
oldraw=observed(RUN/'T35/prepare-full-learning-inputs-preimage-0001.py','b85316a2d56784d754749c78622aa00fcedd726b0e3512d7a22f69043dbaddf0')
oldtree=ast.parse(oldraw);oldnode=next(n for n in oldtree.body if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id=='source2')
inert_run=OUT/'inert-public-metadata';target=inert_run/'T07/api17-task-local-capture-0003/preimage/source-manifest.json';target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b'{"files":[],"unselected_marker":true}\n')
inert_frame={**frame,'RUN':inert_run}
exec(compile(ast.Module(body=[oldnode],type_ignores=[]),str(RUN/'T35/prepare-full-learning-inputs-preimage-0001.py'),'exec'),inert_frame);assert inert_frame['source2']['unselected_marker'] is True
refuses('corrected actual read expression rejects unselected predecessor metadata accepted by preserved b853',lambda:exec(compile(ast.Module(body=[node],type_ignores=[]),str(WRITER),'exec'),inert_frame))
for path in ['a//b','a/../b','../b','/absolute/b','./b','a\\b','.']:
 refuses('actual expected binding alias '+repr(path)+' refuses',lambda:frame['exact']({'path':path,'sha256':'0'*64}))
refuses('actual expected binding digest mismatch refuses',lambda:frame['exact']({'path':str(target.relative_to(ROOT)),'sha256':'0'*64}))

# Selection references native family snapshots and code digests only. Global
# API source/profile pins are supplied independently via CLI after capture,
# allowing selection→profile→source→driver without self-dependent digests.
assert not any(k in value for k in ['source_sha256','profile_sha256','API_source_binding','API_profile_binding'])
assert not any(isinstance(n,ast.Name)and n.id in ['source_sha256','profile_sha256']for n in ast.walk(selection))
assert value['source_pin']==runtime['source_binding']['sha256'] and value['source_pin']!='a909f378b8a1c5f6f02fe6bcbafa56da7f2fe873a3865ab7853b443d57b249f2'
passed('no new global source/profile digest cycle or renamed global-source identity')
for path,row in list(sources.items()):observed(ROOT/path,row['sha256'])
report={'schema_version':'lab-T35-input-preparation-independent-controls/v1-candidate','verdict':'PASS-preparation-code-only','checks':cases,'checks_count':len(cases),'writer_binding':{'path':str(WRITER.relative_to(ROOT)),'sha256':PIN},'actual_runtime_descriptor_binding':runtime_binding,'actual_public_metadata_only':True,'sources':list(sources.values()),'all_sources_fresh_entry_exit':True,'selection_constructed_only_in_memory_from_actual_metadata':True,'selection_schema_valid':True,'preparation_main_or_selection_output_authored':False,'Context_bindings_invented':False,'actual_native_family_acceptance_claimed':False,'actual_Lab_Source_Service_Session_or_native_constructed':False,'runtime_lock_acquired':False,'authority_effect':'none','task_complete':False}
path=OUT/'pure-controls-result.json';path.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps({'result':report['verdict'],'checks':len(cases),'sources':len(sources),'sha256':sha(path.read_bytes())}),flush=True)
