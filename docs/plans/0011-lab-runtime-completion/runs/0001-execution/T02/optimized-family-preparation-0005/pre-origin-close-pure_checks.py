"""Owned normal metadata/AST proof; never stage/preview/construct a family."""
import ast,hashlib,json,os,types
from pathlib import Path
import jsonschema
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
HERE=RUN/'T02/optimized-family-preparation-0005';RECIPE4=RUN/'T02/optimized-family-preparation-0004'
checks=[]
def need(name,value):
    if not value:raise AssertionError(name)
    checks.append(name)
def read(path):return json.loads(path.read_bytes())
def sha(raw):return hashlib.sha256(raw).hexdigest()
def binding(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path.read_bytes())}
def funcs(path):return {n.name:n for n in ast.parse(path.read_bytes()).body if isinstance(n,ast.FunctionDef)}
fd_before=len(os.listdir('/proc/self/fd'))
helper_path=HERE/'recipe_inputs_v5.py';raw=helper_path.read_bytes()
need('explicit selected true helper',sha(raw)=='392789f6da9d870f059d7a7cfec2b4127c88ff3970b283cf27c54e3d1c53ae04')
I=types.ModuleType('_cal_T02_v5_author_metadata_only');I.__file__=str(helper_path)
exec(compile(raw,str(helper_path),'exec',dont_inherit=True),I.__dict__)
baseline=I.verify_baseline();need('actual normal exact metadata verifier',True)
parent=read(RECIPE4/'recipe-selection.json');mapping=baseline['declaration_mapping'];technical=baseline['technical_bindings'];forbidden=I.FORBIDDEN_LIVE_API_INPUTS
need('all349 exact declarations conserved',baseline['original_recipe_declarations']==parent['files'] and [x['original_binding'] for x in mapping]==parent['files'] and len(mapping)==349)
need('only6 true snapshot substitutions',sum(x['original_binding']!=x['technical_binding'] for x in mapping)==6 and len(technical)==343)
need('zero live API17 technical preparation paths',not {x['path'] for x in technical}&forbidden)
for pair in baseline['mutable_snapshot_pairs']:
    need('fresh exact snapshot:'+pair['original_binding']['path'],I.sha(I.exact(pair['snapshot_binding']))==pair['original_binding']['sha256']==pair['snapshot_binding']['sha256'])
need('no177-file-tree copy',not (HERE/'preimages').exists() and len(list(HERE.glob('*')))<25)
old=funcs(RECIPE4/'recipe_inputs_v4.py');new=funcs(helper_path)
for name in ['need','sha','parse','exact']:need('original nofollow/helper AST:'+name,ast.dump(old[name],include_attributes=False)==ast.dump(new[name],include_attributes=False))
opt=read(HERE/'optimization-selection.json');oschema=read(HERE/'optimization-selection.schema.json');jsonschema.Draft202012Validator.check_schema(oschema);jsonschema.Draft202012Validator(oschema).validate(opt);need('closed v5 optimization schema',True)
original_opt=read(RECIPE4/'optimization-selection.json');adjusted=dict(original_opt);adjusted['schema_version']='lab-optimized-source8-capture-selection/v5-candidate';need('caller4/eba/4222/five postimages exact',opt==adjusted)
for key,row in opt.items():
    if key.endswith('_binding'):I.exact(row)
need('all explicit optimization binding bytes fresh',True)
for name in ['activation-selection.template.json','pre-source-acceptance.template.json']:
    value=read(HERE/name);need('unresolved nonauthorizing:'+name,value['status']=='unresolved-no-native-execution' and value['authority_effect']=='none' and value['instance']=='optimized-0005' and any(v is None for v in value.values()))
ps=read(HERE/'pre-source-acceptance.schema.json');jsonschema.Draft202012Validator.check_schema(ps)
need('unresolved pre-source schema refusal',bool(list(jsonschema.Draft202012Validator(ps).iter_errors(read(HERE/'pre-source-acceptance.template.json')))))
constructor=funcs(HERE/'construct_optimized_v5.py');original_ctor=funcs(RECIPE4/'construct_optimized_v4.py')
for name in ['cold','reader','mapped','context','capture','snapshot','replace_unselected','package','write','require','environment','binding','parse','sha']:
    old_text=ast.unparse(original_ctor[name]).replace('_v4','_v5')
    need('original complete native/domain/guard AST:'+name,ast.dump(ast.parse(old_text).body[0],include_attributes=False)==ast.dump(constructor[name],include_attributes=False))
ctor=(HERE/'construct_optimized_v5.py').read_text();builder=(HERE/'build_family_optimized_v5.py').read_text();stager=(HERE/'stage_optimized_family_v5.py').read_text();runtime=(HERE/'stage_runtime_optimized_v5.py').read_text()
need('24h/1800/900 clocks unchanged','timedelta(hours=24)' in builder and '"reader_grant_max_seconds": 1800' in builder and '"session_max_seconds": 900' in builder and 'timedelta(hours=24)' in ctor)
need('new exclusive instance/prefix everywhere',"instance=='optimized-0005'" in raw.decode() and 'completion-optimized-source8-0005-' in builder and 'completion-optimized-source8-0005-optimized-0005' in runtime)
need('all new actual filenames and loaders',all('recipe_inputs_v5.py' in text and "392789f6da9d870f059d7a7cfec2b4127c88ff3970b283cf27c54e3d1c53ae04" in text for text in [builder,stager,ctor,runtime]) and 'build_family_optimized_v5.py' in stager and '_cal_owned_optimized_family_stager_v5' in stager)
need('explicit true RECIPE4 dependency',all('RECIPE4=ROOT/' in text for text in [builder,stager,ctor,runtime,raw.decode()]))
need('all original declaration mapping persisted in actual construction',"selection['optimized_recipe_declaration_mapping']=baseline['declaration_mapping']" in stager and "selection['mutable_API_preparation_snapshot_pairs']=baseline['mutable_snapshot_pairs']" in stager)
need('all4 generated metadata and5 mutable selector paths blocked at technical hash boundary', all(name in ctor for name in ['contract-profile.json','SCHEMA-EXECUTION-DEPENDENCIES.json','INPUT-ACCOUNTING.json','source-manifest.json','source_bridge.py','current_context_sessions.py','authentication.schema.json','machine_auth_scope.py','current_machine_context_scope.py']))
need('constructor add rejects live aliases before fresh existing hash','locator not in FORBIDDEN_LIVE_API_INPUTS' in ctor and 'require(sha(path.read_bytes())==row[\'sha256\']' in ctor)
need('same exact source helper preview and actual',all(any(isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='source_selection' for node in ast.walk(constructor[name])) for name in ['source','preview_source']))
source_text=ast.get_source_segment(ctor,constructor['source']);need('review/equality gate before source snapshot/native load',source_text.index('check_pre_source_review')<source_text.index("snapshot(family,'source'")<source_text.index('B=package('))
need('no preview/acceptance in role technical rows',"binding(family/'source-closure-preview.json')" not in ctor and 'review_binding' not in ast.get_source_segment(ctor,constructor['capture']) and 'review_binding' not in ast.get_source_segment(ctor,constructor['source_selection']))
need('preview outside roles',"path=family/'source-closure-preview.json'" in ctor)
need('every native phase requires actual reviewed construction',"independent actual construction/preview acceptance required before native phases" in ctor and "inputs.check_pre_source_review(review_binding,family)" in ctor)
need('original Source8/period/native/schema/history references retained','original_Source8_period_binding' in ctor and "original_Schemas_code_changed':False" in ctor and "full_original_history_validation_preserved':True" in ctor and "NATIVE_SHA='fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'" in ctor)
need('runtime reads all5 templates via snapshots only',"for pair in baseline['runtime_template_snapshot_pairs']" in runtime and "raw=I.exact(snapshot)" in runtime and "I.exact(row);name=Path(row['path']).name" not in runtime)
need('runtime retains original template identities and true pairs',"descriptor['original_templates']" in runtime and "descriptor['original_template_preimages']" in runtime)
need('runtime all4 role closures prohibit6 live and require6 snapshots',"for key in ['source_binding','reader_binding','mapper_binding','context_source_binding']" in runtime and 'actual full role closure needs all snapshots and zero live mutable API preparation origins' in runtime)
need('all9 native role bindings +5 reports +original phaseorder',"set(value['family_bindings'])==FAMILY_FIELDS" in runtime and "len(value['phase_reports'])==5" in runtime and "phases==['source','cold','reader','mapped','context']" in runtime)
need('no retained old runtime schema or namespace', 'lab-T02-v4-actual-family-inputs' not in runtime and '_cal_api17_current_source8_optimized_0004' not in runtime and '_cal_api17_current_source8_optimized_0005' in runtime)
causal=read(ROOT/baseline['Root_causal_review_binding']['path']);old_source=read(ROOT/causal['actual_source_snapshot']['path']);need('Root actual Source4 evidence exact',sha((ROOT/causal['actual_source_snapshot']['path']).read_bytes())==causal['actual_source_snapshot']['sha256'] and len(old_source['files'])==1642)
projection={}
substitutions={x['original_binding']['path']:x['snapshot_binding'] for x in baseline['mutable_snapshot_pairs']}
for row in old_source['files']:
    mapped=substitutions.get(row['path'],row);need('normal full closure row identity:'+row['path'],projection.get(mapped['path'],mapped)==mapped);projection[mapped['path']]=mapped
need('actual1642 diagnostic projection zero6 live/all6fresh',not set(projection)&forbidden and all(projection.get(x['path'])==x for x in substitutions.values()) and len(projection)==1636)
need('no actual owned family/preview/source created',not (HERE/'instances').exists() and not (HERE/'reports').exists())
need('FD delta zero',len(os.listdir('/proc/self/fd'))==fd_before)
result={'schema_version':'lab-T02-v5-pure-preparation-controls/v1-candidate','result':'PASS','check_count':len(checks),'checks':checks,'FD_delta':0,'actual_metadata_verifier_binding':binding(helper_path),'actual_Source4_metadata_binding':causal['actual_source_snapshot'],'projected_diagnostic_original_rows':1642,'projected_technical_rows':1636,'projection_is_actual_family5_source_manifest':False,'actual_v5_staging_preview_constructor_native_or_lease':False,'original_callbacks_clocks_globals_or_private_state_changed':False,'authority_effect':'none','limitations':['Pure exact metadata verifier, JSON schema and static AST checks only. Projection demonstrates six substitutions on diagnostic1642 rows; actual new staged Source closure must separately be previewed and independently reviewed by Root before native use. No family5 staging, Source/native constructors or timing/calibration proof.']}
with (HERE/'STATIC-CHECKS-final.json').open('x') as f:f.write(json.dumps(result,sort_keys=True,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='checks'}),flush=True)
