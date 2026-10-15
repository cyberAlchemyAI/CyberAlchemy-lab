"""Independent ordinary public closure controls. No Lab/runtime/native imports."""
from pathlib import Path
import ast,copy,hashlib,json,os,sys,types
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');HERE=Path(__file__).absolute().parent
INSTALL=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
assert Path(sys.executable)==INSTALL/'bin/python'
sha=lambda raw:hashlib.sha256(raw).hexdigest();checks=[]
def check(name,value):
 if not value:raise AssertionError(name)
 checks.append(name)
fd_start=len(os.listdir('/proc/self/fd'))
pins={'HANDOFF.json':'a92f4214027e0e31f98d79cfee685f9a9e5f5f1841e57ef9f9aa9c76c08d5176','source-manifest.json':'ec2433ff1eae82c7e3589df215f5c178a8c5bb52f2f8b478b65e45a1cf4d2cbd','source-selection.json':'7482b7f02bc2f7e7d373aea753f2fe10df79749c7950003804ed0d2f303a0587','build.py':'4cb37b74eebc31c45a574fc0a8cbdca750d08cb47cf606fe928661f290f2410c'}
for name,pin in pins.items():check('Root independently held pin '+name,sha((HERE/name).read_bytes())==pin)
raw=(HERE/'build.py').read_bytes();tree=ast.parse(raw)
check('Only ordinary metadata imports',all(n.names[0].name in ['argparse','ast','copy','hashlib','json','os','stat']for n in tree.body if isinstance(n,ast.Import)))
module=types.ModuleType('_T03_independent_public_margin_closure_0001');module.__file__=str(HERE/'build.py');exec(compile(raw,str(HERE/'build.py'),'exec',dont_inherit=True),module.__dict__)
parse=module.parse;mf=parse((HERE/'source-manifest.json').read_bytes());selection=parse((HERE/'source-selection.json').read_bytes());B=selection['bindings'];held={}
def capture(row):
 raw,record=module.capture(row)
 if row['path']in held:check('Duplicate declared byte binding agrees '+row['path'],held[row['path']]==record)
 held[row['path']]=record;return raw
for row in mf['files']:capture(row)
check('Active MF483 true unique paths',len(mf['files'])==483 and len({r['path']for r in mf['files']})==483)
inputs={name:parse(capture(row))for name,row in B.items()if not row['path'].endswith('.py')}
original=inputs['original_margin_manifest']['files'];mapping=parse((HERE/'declaration-map.json').read_bytes());refs=parse((HERE/'source_refs.json').read_bytes());api=parse((HERE/'current-api-expectations.json').read_bytes())['files']
regenerated=module.declaration_map(original,selection['historical_replacements'])
check('Exact original294 declaration mapping regenerated',regenerated==mapping['rows'] and len(original)==294)
check('294 references neither dropped nor relabelled',len(refs['all294_original_declaration_refs'])==294)
by_path={r['path']:r for r in mf['files']}
for i,(old,mapped,ref)in enumerate(zip(original,mapping['rows'],refs['all294_original_declaration_refs']),1):
 check('Original declaration identity '+str(i),mapped['position']==i and mapped['original_declaration']==old and ref['declaration_position']==i and ref['original_byte_binding']==old)
 physical=mapped['physical_binding'];check('True retained physical binding '+str(i),by_path[physical['path']]==physical and ref['actual_retained_physical_binding']==physical)
 check('Exact selected same bytes and complete size '+str(i),physical['sha256']==old['sha256'] and physical['size_bytes']==old['size_bytes'])
check('290 physical files !=294 declarations',{r['physical_binding']['path']for r in mapping['rows']}=={r['path']for r in original if r['path']not in {q['original_declaration']['path']for q in selection['historical_replacements']}})
for item in selection['historical_replacements']:
 old=item['original_declaration'];retained=item['retained_binding'];proof=item['Root_reviewed_preserved_preimage']
 check('Independent historical snapshot bytes '+old['path'],capture(retained)==capture(proof))
 check('No old origin alias/current hash reinterpretation '+old['path'],retained['path']!=old['path'] and by_path[old['path']]['sha256']!=old['sha256'])
expected=module.current_api(inputs['capture3_retained_selection'],inputs['margin_application_receipt'],inputs['selector_application_receipt'])
check('Exact independently rebuilt current165 expectations',api==expected and len(api)==165)
old160={r['path']:r for r in inputs['capture3_retained_selection']['api_expected_files']};margin8={r['path']:r for r in inputs['margin_application_receipt']['actual_target_bindings']};selector4={r['target']:r['actual']for r in inputs['selector_application_receipt']['rows']if r['changed']}
check('12 actual reviewed postimages with5 new leaves',len(margin8)==8 and len(selector4)==4 and len(set(margin8)|set(selector4))==12 and len(set(margin8)-set(old160))==5)
for row in api:check('Actual current API pin '+row['path'],all(by_path[row['path']].get(k)==v for k,v in row.items()) and sha(capture(row))==row['sha256'])
software=inputs['current_software_inventory']['files'];check('Current exact software16 selected',len(software)==16 and len({r['path']for r in software})==16)
for row in software:check('Current software pin '+row['path'],by_path[row['path']]['sha256']==row['sha256']and sha(capture(row))==row['sha256'])
check('Current165 excludes generatedAPI MF/profile capture cycle',not any(r['path'].endswith('/'+leaf)for r in api for leaf in ['source-manifest.json','profile.json','schema-inventory.json','schema-dependency-inventory.json']))
check('Unchanged original guard65ba',by_path[module.API+'guard.py']['sha256']=='65ba71adb3b885f6fedc268be29f982f1f03139265f00a7e9ed08ff19b6adeb3')
check('Active MF has no own MF/HH self digest',all(r['path']not in {str((HERE/'source-manifest.json').relative_to(ROOT)),str((HERE/'HANDOFF.json').relative_to(ROOT))}for r in mf['files']))
for name in ['driver4_code','margin_composition']:
 text=capture(B[name]);constants=[n.value for n in ast.walk(ast.parse(text))if isinstance(n,ast.Constant)and isinstance(n.value,str)]
 check('No raw original294 runtime table selection '+name,not any(B['original_margin_manifest']['path']in s for s in constants))
for case in ['drop-original','drop-substitution','wrong-old','fake-retained','old-live-alias']:
 rows=copy.deepcopy(original);replacements=copy.deepcopy(selection['historical_replacements'])
 if case=='drop-original':rows.pop()
 elif case=='drop-substitution':replacements.pop()
 elif case=='wrong-old':replacements[0]['original_declaration']['sha256']='0'*64
 elif case=='fake-retained':replacements[0]['retained_binding']['sha256']='0'*64
 else:replacements[0]['retained_binding']['path']=replacements[0]['original_declaration']['path']
 try:module.declaration_map(rows,replacements)
 except ValueError:check('Pure mapping refusal '+case,True)
 else:raise AssertionError(case)
for path,record in held.items():check('Held public entry exit unchanged '+path,module.capture({'path':path,'sha256':record['sha256'],'size_bytes':record['size_bytes']})[1]==record)
check('FD delta zero',len(os.listdir('/proc/self/fd'))==fd_start)
report={'schema_version':'lab-T03-margin-final-closure-independent-controls/v1','authority_effect':'none','result':'PASS-pure-public-closure-controls','check_count':len(checks),'checks':checks,'independent_pins':pins,'actual_interpreter':str(sys.executable),'MF_rows':483,'held_public_files':len(held),'original_declarations':294,'historical_unique_physical':290,'historical_substitutions':4,'current_API_expectations':165,'current_software_bindings':16,'FD_delta':0,'native_API_guard_or_runtime_or_lease_or_private_effects':False,'original_callback_or_shared_or_frozen_mutations':False,'full_T03_or_goal_complete':False}
with (HERE/'independent-controls-0001.json').open('x')as f:f.write(json.dumps(report,sort_keys=True,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items()if k not in ['checks','independent_pins']}))
