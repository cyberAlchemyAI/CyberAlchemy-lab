"""Final input metadata/byte closure only; no capture/main/native/lease."""
import ast,hashlib,json,os,re,stat,sys,types
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution';HERE=RUN/'T07/api17-task-local-capture-0003';OUT=Path(__file__).absolute().parent;API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v17'
SPIN='b182a70bf823e1e54cef016496e9acf7f573d32264653c0194c61e1bfe2fe661';WPIN='a3a860bf6a31e23cebd0cd750e31c1037919b6ca5cf343106d5f391b4f534417';CPIN='fe7cf43fbd239b88d5b524ff62c3729e96afb5d44cb2fac2c4ba41208e94e665'
verified={};union={};checks=[];failures=[]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def logical(path):
 p=Path(path);return str(p.relative_to(ROOT))if p.is_absolute()and p.is_relative_to(ROOT)else p.as_posix()
def closed(row):
 assert type(row)is dict and set(row)=={'path','sha256'} and re.fullmatch('[a-f0-9]{64}',row['sha256'])
 p=Path(row['path']);assert p.as_posix()==row['path'] and '..'not in p.parts and '\\'not in row['path'] and '\0'not in row['path'] and row['path']not in ['','.']
 return row
def exact(path,pin=None,body=False,fresh=False):
 path=Path(path);path=path if path.is_absolute()else ROOT/path;name=logical(path)
 assert not path.is_symlink() and not any(p.is_symlink()for p in path.parents),name
 if not body and not fresh and name in verified:
  row=verified[name];assert pin is None or row['sha256']==pin,name;return row
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK);before=os.fstat(fd);assert stat.S_ISREG(before.st_mode)
 parts=[];h=hashlib.sha256();size=0
 try:
  while True:
   raw=os.read(fd,1024*1024)
   if not raw:break
   h.update(raw);size+=len(raw)
   if body:parts.append(raw)
  after=os.fstat(fd);attached=os.stat(path,follow_symlinks=False)
  stamp=lambda s:(s.st_dev,s.st_ino,s.st_uid,s.st_mode,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
  assert stamp(before)==stamp(after)==stamp(attached)
 finally:os.close(fd)
 assert not any(p.is_symlink()for p in path.parents)
 row={'path':name,'sha256':h.hexdigest(),'size_bytes':size};assert pin is None or row['sha256']==pin,name
 assert verified.get(name,row)==row,name;verified[name]=row
 return b''.join(parts)if body else row
def load(path,pin=None):return json.loads(exact(path,pin,body=True))
def read_binding(row):closed(row);return load(row['path'],row['sha256'])
def add(row):
 closed(row);r={'path':logical(row['path']),'sha256':row['sha256']};assert union.get(r['path'],r)==r,'conflicting selected byte '+r['path'];union[r['path']]=r;exact(r['path'],r['sha256'])
def passed(name):checks.append({'case':name,'result':'PASS'})
selection=load(HERE/'component-selection.json',SPIN);writer=exact(HERE/'prepare_selection.py',WPIN,body=True);ast.parse(writer)
assert set(selection)=={'schema_version','authority_effect','claim_ceiling','selected_at','task_complete','whole_API_qualified','guard_binding','api_expected_files','helper_expected_files','current_family_selections','component_manifests','direct_inputs','superseded_template_metadata_basis'}
assert selection['authority_effect']=='none' and selection['task_complete']is False and selection['whole_API_qualified']is False
passed('exact final b182 selection/a3a writer and closed nonauthorizing candidate shape')
pre=load(HERE/'preimage/source-manifest.json','a909f378b8a1c5f6f02fe6bcbafa56da7f2fe873a3865ab7853b443d57b249f2');prior={r['path']:r for r in pre['files']}
parent=load(API.parent/'api-integration-v16/source-manifest.json','8ac40a51e23b8e528178807792b8ae477aa9c46cd50d92a5b1522c82945413c7');profile=load(API.parent/'api-integration-v16/contract-profile.json','8cc29da16d3881d8816cdc45c55358d9229fcaf226d1b9a757402ebc8675d18c')
assert len(parent['files'])==24497 and len(profile['files'])==24496
profile_paths={r['path']for r in profile['files']};assert [r for r in parent['files']if r['path']in profile_paths]==profile['files']
absent=load(RUN/'T07/accounting-0001/unavailable-original-inputs.json','4408c5433d41119a92660f86f856d6847be24171ddb1dab368e22c63ee294e7a');unavailable={r['binding']['path']:r['binding']for r in absent['rows']};parents={r['path']:r for r in parent['files']}
assert len(unavailable)==25 and all(parents[p]==r for p,r in unavailable.items());retained=[r for r in parent['files']if r['path']not in unavailable]
passed('all24497/24496 original provenance/order and exact25 unavailable bindings preserved without current physical PASS')
patch=load(RUN/'T02/current-selector-staging-0002/patch-ledger.json','c63786e305d4e3edacb49bbd72882bec861b278428a43a2379dd3508db2a68cb');changes={r['target']:r for r in patch['rows']};assert len(changes)==4
expected={r['path']:closed(r)for r in selection['api_expected_files']};assert len(expected)==len(selection['api_expected_files'])==160
actual={str(p.relative_to(ROOT))for p in API.rglob('*')if p.is_file()and '__pycache__'not in p.parts and 'receipts'not in p.parts and p.name not in ['source-manifest.json','contract-profile.json','SCHEMA-EXECUTION-DEPENDENCIES.json','INPUT-ACCOUNTING.json']}
assert actual==set(expected)
for path,row in expected.items():
 if path in changes:
  c=changes[path];assert row['sha256']==c['postimage']['sha256'];add(c['postimage']);add(c['preimage']);assert c['preimage']['sha256']==prior[path]['sha256'];add(row)
 else:assert row==prior[path];add(row)
passed('complete160 API expectations: exactly4 reviewed postimages,156 independent unchanged a909 predecessor bytes; actual API now exact reviewed postimage')
helpers={r['path']:closed(r)for r in selection['helper_expected_files']};assert len(helpers)==7
actual_helpers=set()
for folder in ['machine-context-scope-v2-completion-0001','lesson-host-composition-v46-completion-0001','lesson-application-v4-completion-0001']:
 for path in(API.parent/folder).rglob('*'):
  if path.is_file()and '__pycache__'not in path.parts:actual_helpers.add(str(path.relative_to(ROOT)))
assert actual_helpers==set(helpers)
for path,row in helpers.items():assert row==prior[path];add(row)
add(selection['guard_binding']);assert selection['guard_binding']['sha256']=='65ba71adb3b885f6fedc268be29f982f1f03139265f00a7e9ed08ff19b6adeb3'
passed('all7 helpers and original guard independently expected, complete and physically unchanged')

capraw=exact(HERE/'capture.py',CPIN,body=True);C=types.ModuleType('_T07_final_selection_shape_review');C.__file__=str(HERE/'capture.py');exec(compile(capraw,C.__file__,'exec'),C.__dict__)
families=[];role_occurrences=0;names=set();paths=set();all_role_rows=[]
for row in selection['current_family_selections']:
 closed(row);assert row['path']not in paths;paths.add(row['path']);runtime=read_binding(row);assert runtime['instance']not in names;names.add(runtime['instance']);roles=C.family_roles(runtime,row['path']);add(row)
 info={'descriptor_binding':row,'instance':runtime['instance'],'role_tables':{},'new_current_execution_candidate':runtime['instance']=='optimized-0002'}
 for role,b in roles.items():
  mf=read_binding(b);assert mf['authority_effect']=='none' and mf['actual_owner_outcome']is None
  info['role_tables'][role]={'binding':b,'rows':len(mf['files'])};add(b)
  for r in mf['files']:
   slim={'path':r['path'],'sha256':r['sha256']};assert logical(slim['path'])not in unavailable;add(slim);all_role_rows.append(slim);role_occurrences+=1
  assert not {logical(r['path'])for r in mf['files']}&set(changes)
 if runtime['instance']=='optimized-0002':current_runtime=runtime
 families.append(info)
assert len(families)==3 and names=={'legacy-diagnostic-0001','diagnostic-0004','optimized-0002'}
passed('three distinct closed real family descriptors and complete12 role tables hash-verified; old families retained without period renewal or changed-API input conflict')

component_occurrences=0;components=[]
for component in selection['component_manifests']:
 assert set(component)=={'base','path','sha256'} and component['base']=='.';mf=read_binding({'path':component['path'],'sha256':component['sha256']});add({'path':component['path'],'sha256':component['sha256']})
 for row in mf['files']:
  p=Path(row['path']);p=p if p.is_absolute()else ROOT/component['base']/p;slim={'path':logical(p),'sha256':row['sha256']};add(slim);component_occurrences+=1
  if 'size_bytes'in row:assert verified[slim['path']]['size_bytes']==row['size_bytes']
 components.append({'manifest_binding':component,'rows':len(mf['files'])})
assert len(components)==7 and component_occurrences==261
passed('seven full components/261 row occurrences exact, including failedV1 provenance and correctedV2 recipe')
direct={r['path']:closed(r)for r in selection['direct_inputs']};assert len(direct)==len(selection['direct_inputs'])==49
for row in direct.values():add(row)
draft=load(HERE/'component-selection-DRAFT.json','7c2bcdb45babf7ef7abf89f68693f276c9e5cc7dd76a2aeba4f12ab2a530280a')
stager=str((RUN/'T02/prepare-current-selectors-0002.py').relative_to(ROOT));old_stager=str((RUN/'T02/prepare-current-selectors-0002-preimage-0001.py').relative_to(ROOT))
for row in draft['direct_inputs']:
 if row['path']==stager:assert direct[old_stager]['sha256']==row['sha256'] and direct[stager]['sha256']=='05556b7b82b8480eb248de9b81772b2ede44733a814f1db8af9bcb506e92c5c8'
 else:assert direct[row['path']]==row
required=['T02/optimized-family-preparation-0002/reports/observer-0001/actual_attempt.py','T02/optimized-family-preparation-0002/reports/observer-0001/authentication_verify.py','T35/prepare-full-learning-inputs-0001.py','T35/full-learning-inputs-0001/selection.json','T03/context-parser-correction-0002/generation.py','T03/context-parser-correction-0002/HANDOFF.json']
for name in required:assert str((RUN/name).relative_to(ROOT))in union,name
assert union[str((RUN/'T03/context-parser-correction-0002/generation.py').relative_to(ROOT))]['sha256']=='4937fc175201cbed0e8a8a67093fb6a02bc617fa3fbf38150d1a109afd01bc05'
passed('all49 direct inputs exact and old draft inputs retained; required V2 observer/helper/current writers/input selection/corrected parser true origins selected')

basis=selection['superseded_template_metadata_basis'];assert set(basis)=={'descriptor_binding','patch_ledger_binding','scope'} and basis['descriptor_binding']==patch['runtime_selection_binding'] and basis['patch_ledger_binding']['sha256']=='c63786e305d4e3edacb49bbd72882bec861b278428a43a2379dd3508db2a68cb'
template_dispositions=[]
for row in current_runtime['original_templates']:
 if row['path']in changes:
  assert row['sha256']==changes[row['path']]['preimage']['sha256'];preimage=changes[row['path']]['preimage'];assert direct[preimage['path']]==preimage
  template_dispositions.append({'original_binding_metadata_only':row,'preserved_physical_preimage_binding':preimage,'current_origin_binding':expected[row['path']],'same_inode_or_current_digest_claimed':False})
 else:add(row);template_dispositions.append({'unchanged_original_binding':row})
passed('superseded template metadata anchored to true retained preimage bytes; no current digest alias or old proof transfer')

# Model capture schema-origin eligibility without executing its mutating main.
schema=load(API.parent/'api-integration-v16/SCHEMA-EXECUTION-DEPENDENCIES.json');schema_rows={r['path']:r for r in schema['files']};assert not set(schema_rows)&set(unavailable)
current_map={r['path']:r for r in retained};current_map.update(union);current_map.update(expected)
for path,row in current_map.items():
 if path.startswith(str(API.relative_to(ROOT))+'/')or(path in union and path.endswith('.py')):schema_rows[path]=row
for path,row in union.items():
 if path.endswith('.py'):assert schema_rows.get(path)==row,path
for name in required:
 path=str((RUN/name).relative_to(ROOT))
 if path.endswith('.py'):assert schema_rows[path]==union[path]
assert all(path not in unavailable for path in schema_rows)
passed('complete new Python true-origin eligibility modeled with all original schema rows retained; no missing historical byte becomes schema execution input')
learning=read_binding(direct[str((RUN/'T35/full-learning-inputs-0001/selection.json').relative_to(ROOT))]);assert learning['runtime_selection_binding']==patch['runtime_selection_binding'] and learning['source_pin']==current_runtime['source_binding']['sha256'] and learning['source_package_pin']==current_runtime['source_package_binding']['sha256'];assert not any(k in learning for k in ['source_sha256','profile_sha256'])
assert str((HERE/'component-selection.json').relative_to(ROOT))not in direct
passed('current learning selection consistent; global source/profile and component-selection digest dependencies remain acyclic')
for path,row in list(verified.items()):exact(path,row['sha256'],fresh=True)
report={'schema_version':'lab-T07-final-selection-independent-controls/v1-candidate','verdict':'PASS-final-input-selection-only','selection_sha256':SPIN,'writer_sha256':WPIN,'capture_code_sha256':CPIN,'checks':checks,'checks_count':len(checks),'unique_physical_inputs_hashed_fresh_entry_exit':len(verified),'original_provenance_rows':{'source':24497,'profile':24496,'unavailable':25,'retained_current':len(retained)},'API_expected_rows':160,'helper_expected_rows':7,'family_descriptors':families,'role_row_occurrences_accounted':role_occurrences,'component_manifests':components,'component_row_occurrences_accounted':component_occurrences,'direct_inputs':49,'template_dispositions':template_dispositions,'source_bindings':list(verified.values()),'audit_scope':'All selected addition/component/family bytes checked per unique path at entry and exit. Original24497/24496 tables inspected as exact immutable metadata; full24472 original present physical-byte guard not rerun. No production verifier cache or old proof transfer.','actual_API_edits_capture_main_runtime_native_or_lease_executed':False,'actual_runtime_or_whole_API_qualified':False,'unsupported_or_missing_selection_eligibility_findings':failures,'authority_effect':'none','task_complete':False}
path=OUT/'controls-result.json';path.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps({'verdict':report['verdict'],'checks':len(checks),'physical_inputs':len(verified),'role_rows':role_occurrences,'component_rows':component_occurrences,'sha256':sha(path.read_bytes())}),flush=True)
