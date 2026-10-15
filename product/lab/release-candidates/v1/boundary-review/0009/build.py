"""Parametric final-family payload/dispositions; protected original proof closure retained."""
import argparse,collections,datetime,hashlib,importlib.util,json,os,re,stat,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5];RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction';API=None
API_SOURCE=None;API_PROFILE=None;NATIVE=Path('/tmp/cal-R03-mapped-native-build-0002/target/debug/lab-context-native-reader');NATIVE_SHA='fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'
R02PATH=ROOT/'product/lab/release-candidates/v1/packaging/R02/successors/0001'
sys.path.insert(0,str(R02PATH));import common as C
spec=importlib.util.spec_from_file_location('_R06_0008_original_installer',R02PATH/'installer.py');R02=importlib.util.module_from_spec(spec);spec.loader.exec_module(R02)
spec=importlib.util.spec_from_file_location('_R06_0008_original_inspector',HERE.parent/'0002/review.py');R=importlib.util.module_from_spec(spec);spec.loader.exec_module(R)
def bind(p):return {'path':str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p),'sha256':C.sha(C.read(p))}
def load(p):return C.parse(C.read(p))
def put(p,v):C.emit(p,v);p.chmod(0o600)

BASE=ROOT/'product/lab/release-candidates/v1/interface'
SELECTION=HERE/'final-family-selection.json'
CONTEXT=RUN/'context-R06-final-family-0241.json'
PREVIOUS_PIN='2834e8ddbb61607abb04e49b27428d8399634a290dc56581e2ef2164a38069a9'

def require(v,why):
 if not v:raise ValueError(why)

def exact(row):
 require(set(row)=={'path','sha256'},'closed original file binding required')
 require(bind(ROOT/row['path'])==row,'immutable input changed: '+row['path'])
 return row

def protected_code(path):
 q=Path(path);parts=q.parts;lower=path.lower();name=q.name.lower()
 return (any(p in ('tests','fixtures','receipts','runs','__pycache__','.git','.local','.env','secrets','credentials','archives','journal') or p.startswith('.env.') for p in parts)
  or any(v in lower for v in ('fixture','qualification','qualifier','reader-policy','host-permission','private-grant'))
  or name.startswith(('test_','checks','check','freeze','qualify','run_','build_','reconcile','restore-runtime'))
  or name in ('build.py','produce.py','producer.py','provision.py','source-manifest.json','contract-profile.json','SCHEMA-EXECUTION-DEPENDENCIES.json','SOURCE-BASELINE.json')
  or path.endswith('/source8-session-runtime-v1-action-0148/provider.py')
  or q.suffix.lower() in ('.pem','.key','.pyc','.db','.sqlite','.sqlite3','.p12','.pfx','.log','.stdout'))

def public_selection(selection_row,source,profile,execution):
 exact(selection_row);value=load(ROOT/selection_row['path'])
 require(set(value)=={'schema_version','api_source_binding','api_profile_binding','files','authority_effect','actual_owner_outcome'},'closed explicit public proposal selection required')
 require(value['schema_version']=='lab-R06-final-public-selection/v1-candidate' and value['authority_effect']=='none' and value['actual_owner_outcome'] is None,'public proposal grants no authority')
 require(value['api_source_binding']==bind(API/'source-manifest.json') and value['api_profile_binding']==bind(API/'contract-profile.json'),'public selection names another frozen family')
 require(value['files'],'empty public proposal selection')
 source_rows={r['path']:r for r in source['files']};active={r['path'] for r in execution['files']};schemas={r['path'] for r in load(API/'schema-inputs.json')['files']};names=[]
 for item in value['files']:
  require(set(item)=={'binding','kind','reasons'} and isinstance(item['reasons'],list) and item['reasons'] and all(type(x) is str and x for x in item['reasons']),'explicit public reason required')
  row=exact(item['binding']);path=row['path'];C.relative(path);require(source_rows.get(path)==row,'public input outside complete final source')
  require(not protected_code(path),'construction/test/fixture/private evidence cannot enter public payload: '+path)
  kind=item['kind'];q=Path(path)
  require(kind in ('runtime-code','schema','runtime-resource','offline-package'),'unknown public input kind')
  package=path.startswith('product/lab/release-candidates/v1/packaging/R02/packages/') and any('/'+v+'/' in path for v in ('0002','0003'))
  require((kind=='runtime-code' and q.suffix=='.py' and path in active)
   or (kind=='schema' and (q.name.endswith('.schema.json') or path in schemas))
   or (kind=='runtime-resource' and q.suffix=='.json' and path in active)
   or (kind=='offline-package' and (package or q.suffix=='.whl' and path in active)), 'public kind/path has no actual runtime/schema/package witness: '+path)
  raw=C.read(ROOT/path);require(not R.scan(raw,path),'public input has private/Session field finding');C.privacy(raw);names.append(path)
 require(names==sorted(set(names)),'public selection paths must be sorted and unique')
 return value

def configure(value):
 global API,API_SOURCE,API_PROFILE
 require(set(value)=={'schema_version','api_directory','api_source_binding','api_profile_binding','schema_execution_binding','public_selection_binding','authority_effect','actual_owner_outcome'},'closed final family selection required')
 require(value['schema_version']=='lab-R06-final-family-selection/v1-candidate' and value['authority_effect']=='none' and value['actual_owner_outcome'] is None,'candidate family selector grants no authority')
 API=(ROOT/value['api_directory']).resolve();require(API.parent==BASE and API.name.startswith('api-integration-'),'selected final API origin differs')
 require(value['api_source_binding']['path']==str((API/'source-manifest.json').relative_to(ROOT)) and value['api_profile_binding']['path']==str((API/'contract-profile.json').relative_to(ROOT)) and value['schema_execution_binding']['path']==str((API/'SCHEMA-EXECUTION-DEPENDENCIES.json').relative_to(ROOT)),'final controls outside actual API directory')
 API_SOURCE=value['api_source_binding']['sha256'];API_PROFILE=value['api_profile_binding']['sha256']
 for key in ('api_source_binding','api_profile_binding','schema_execution_binding','public_selection_binding'):exact(value[key])
 return value

def check_api_controls():
 require(API is not None,'final family has not been explicitly selected')
 require(bind(API/'source-manifest.json')['sha256']==API_SOURCE and bind(API/'contract-profile.json')['sha256']==API_PROFILE,'independent final API pins differ')
 spec=importlib.util.spec_from_file_location('_R06_exact_final_API_guard',API/'guard.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 a=module.verify(API_SOURCE);p=load(API/'contract-profile.json');s=load(API/'SCHEMA-EXECUTION-DEPENDENCIES.json');full={r['path']:r for r in a['files']}
 for row in p['files']+s['files']:require(full.get(row['path'])==row,'profile/execution row outside exact full source')
 return a,p,s

def frozen(pin):
 require(bind(HERE/'source-manifest.json')['sha256']==pin,'independent boundary source pin differs')
 m=load(HERE/'source-manifest.json');configure(load(SELECTION))
 require(m['final_family_selection_binding']==bind(SELECTION),'frozen final family selector changed')
 for row in m['files']:exact(row)
 a,p,s=check_api_controls();public_selection(load(SELECTION)['public_selection_binding'],a,p,s)
 return m

def freeze(args):
 require(not (HERE/'source-manifest.json').exists() and not SELECTION.exists(),'refuse frozen boundary overwrite')
 api=Path(args.api_directory).resolve();require(api.parent==BASE and api.name.startswith('api-integration-'),'final API origin differs')
 value={'schema_version':'lab-R06-final-family-selection/v1-candidate','api_directory':str(api.relative_to(ROOT)),
  'api_source_binding':{'path':str((api/'source-manifest.json').relative_to(ROOT)),'sha256':args.api_source_sha256},
  'api_profile_binding':{'path':str((api/'contract-profile.json').relative_to(ROOT)),'sha256':args.api_profile_sha256},
  'schema_execution_binding':bind(api/'SCHEMA-EXECUTION-DEPENDENCIES.json'),
  'public_selection_binding':{'path':str(Path(args.public_selection).resolve().relative_to(ROOT)),'sha256':args.public_selection_sha256},'authority_effect':'none','actual_owner_outcome':None}
 configure(value);a,p,s=check_api_controls();public_selection(value['public_selection_binding'],a,p,s)
 require(load(RUN/'R06-api12-selection-terminal-0173.json')['conformance_actual_exit_code']==143,'original actual143 changed')
 require(load(HERE.parent/'0007/receipts/terminal-verification-0001.json')['result']=='PASS-independent-read-only-closure','original independent terminal proof differs')
 recovery=load(RUN/'runtime-recovery-0209.json');require(recovery['result']=='PASS' and recovery['native_binding']==bind(NATIVE) and recovery['native_mode']=='0o755' and recovery['old_private_keys_or_sessions_restored'] is False,'actual0209 host recovery proof differs')
 previous=load(HERE.parent/'0007/source-manifest.json');require(bind(HERE.parent/'0007/source-manifest.json')['sha256']==PREVIOUS_PIN,'original0007 source differs')
 full={r['path']:r for r in a['files']}
 for row in previous['files']:
  require(full.get(row['path'],row)==row,'conflicting original proof input');exact(row);full[row['path']]=row
 controls=[HERE.parent/'0007/source-manifest.json',HERE.parent/'0007/build.py',HERE.parent/'0007/check.py',HERE.parent/'0007/receipts/proof-0001.json',HERE.parent/'0007/receipts/conformance-0001.json',HERE.parent/'0007/terminal-verify.py',HERE.parent/'0007/receipts/terminal-verification-0001.json',
  RUN/'R06-api12-selection-terminal-0173.json',RUN/'runtime-recovery-0209.json',RUN/'restore-runtime-0209.py',RUN/'ARE-runtime-recovery-0209.json',
  ROOT/'product/lab/release-candidates/v1/release-scope.json',ROOT/'product/lab/release-candidates/v1/packaging/R02/packages/0003/selection.json',API/'source-manifest.json',API/'contract-profile.json',API/'SCHEMA-EXECUTION-DEPENDENCIES.json',API/'integration-members.json',
  HERE/'build.py',HERE/'check.py',HERE/'disposition.schema.json',HERE/'README.md',CONTEXT,RUN/'authorization.json',RUN/'ARE-final-R06-boundary-0241.json',
  RUN/'installation-release-R06-api10-audit-0148.json',RUN/'installation-release-R06-api10-remediation-0148.json',HERE.parent/'0003/inventory.json',HERE.parent/'0004/format-resolution.json',HERE.parent/'0005/session-exclusions.json',HERE.parent/'0002/review.py',R02PATH/'common.py',R02PATH/'installer.py',ROOT/'implementation/lab-ontology/candidates/v1/migration/source-selection.json',ROOT/value['public_selection_binding']['path']]
 put(SELECTION,value)
 for path in controls+[SELECTION]:full[bind(path)['path']]=bind(path)
 for row in full.values():exact(row)
 put(HERE/'source-manifest.json',{'schema_version':'lab-R06-final-family-payload-source/v1-candidate','files':[full[k] for k in sorted(full)],'api_source_binding':bind(API/'source-manifest.json'),'api_profile_binding':bind(API/'contract-profile.json'),'schema_execution_binding':bind(API/'SCHEMA-EXECUTION-DEPENDENCIES.json'),'final_family_selection_binding':bind(SELECTION),'context_binding':bind(CONTEXT),'original0007_source_binding':bind(HERE.parent/'0007/source-manifest.json'),'original_proof_rows_retained':True,'frozen_before_observations':True,'authority_effect':'none','actual_owner_outcome':None})
 print(json.dumps({'result':'FROZEN-UNQUALIFIED','source_binding':bind(HERE/'source-manifest.json'),'files':len(full)}),flush=True)
def proposal(pin):
 frozen(pin);a,p,s=check_api_controls();public_choice=public_selection(load(SELECTION)['public_selection_binding'],a,p,s);chosen={i['binding']['path']:i for i in public_choice['files']};profile={r['path'] for r in p['files']};runtime={r['path'] for r in s['files']};schema={r['path'] for r in load(API/'schema-inputs.json')['files']}
 audit=load(RUN/'installation-release-R06-api10-audit-0148.json');prior={r['path']:r for r in audit['rows']};assert len(prior)==112
 old=load(HERE.parent/'0003/inventory.json');oldflag={r['path'] for r in old['rows'] if r['disposition']!='unselected-final-release-source'};assert len(oldflag)==95 and len(set(prior)-oldflag)==17
 original_proposals={r['path']:r for r in load(HERE.parent/'0005/session-exclusions.json')['exclusion_proposals']+load(HERE.parent/'0004/format-resolution.json')['TOML_observations']+load(HERE.parent/'0004/format-resolution.json')['diagnostic_exclusions']}
 migrations=load(ROOT/'implementation/lab-ontology/candidates/v1/migration/source-selection.json');migration_items=[r for r in migrations['items'] if not r['public_body_export_allowed']];assert len(migration_items)==140
 nonexport={str(Path(migrations['root_bindings'][r['source_binding']['root_ref']]['material_root'])/r['source_binding']['path']):r for r in migration_items if r['source_binding'] is not None}
 branches=load(API/'integration-members.json')['members'];core=[API.relative_to(ROOT).as_posix()+'/']+[str(API.parent.relative_to(ROOT))+'/'+m['directory']+'/' for m in branches.values()]
 rows=[];public={};new_findings=[];external=[];reconciled=[];category=collections.Counter()
 for index,row in enumerate(a['files']):
  path=row['path'];q=ROOT/path;raw=C.read(q);assert C.sha(raw)==row['sha256'];findings=[];refusal=None
  try:findings=R.scan(raw,path)
  except (ValueError,UnicodeError,RecursionError) as error:refusal=type(error).__name__
  name=q.name;parts=q.parts;in_core=any(path.startswith(root) for root in core);fixture=('qualification-workspace' in parts or any(v in parts for v in ('tests','fixtures')) or name.startswith(('test_','checks','freeze','qualify','run_session_checks','build_')) or 'fixture' in name)
  package=path.startswith('product/lab/release-candidates/v1/packaging/R02/packages/') and ('/0002/' in path or '/0003/' in path)
  risky=any(v in parts for v in ('.env','.local','__pycache__','.git','secrets','credentials')) or q.suffix.lower() in ('.pem','.key','.pyc','.db','.sqlite','.sqlite3','.p12','.pfx')
  if path in prior:
   assert row['sha256']==prior[path]['sha256'];disposition='protected-prior-exclusion';reason='Exact original95 or additional17 audit finding retained; prior classification unchanged.'
   reconciled.append({'path':path,'sha256':row['sha256'],'prior_group':'original95' if path in oldflag else 'additional17','prior_audit_row':prior[path],'prior_disposition_proposal':original_proposals.get(path),'proposed_disposition':disposition,'public_body_export_allowed':False})
  elif path in nonexport:disposition='protected-nonexportable-migration';reason='Original nonexportable import contract retained independently of public/private classification.'
  elif Path(path).is_absolute():disposition='protected-external-proof-dependency';reason='Retained external original proof input; not a public payload path.';external.append(row)
  elif risky:disposition='protected-cache-or-credential-path';reason='Runtime/cache/credential path excluded; no credential value inferred.'
  elif findings or refusal:disposition='protected-new-field-or-format-finding';reason='Fresh nested inspector finding/refusal requires exact disposition before public selection.';new_findings.append({'path':path,'sha256':row['sha256'],'findings':findings,'refusal_class':refusal})
  elif '/journal/' in path or 'reader-policy' in name or 'qualification-workspace' in parts or fixture:disposition='protected-test-or-operation-evidence';reason='Captured test/policy/journal/fixture material remains separately protected evidence.'
  elif q.suffix=='.snapshot' and not package:disposition='protected-source-history';reason='Original signed history/body archive remains protected; never a public code payload.'
  elif '/receipts/' in path or '/history/' in path or q.suffix in ('.log','.stdout') or name in ('source-manifest.json','contract-profile.json','SCHEMA-EXECUTION-DEPENDENCIES.json','SOURCE-BASELINE.json'):disposition='protected-verification-history';reason='Exact validation/control/provenance evidence is retained outside proposed public bodies.'
  elif protected_code(path):disposition='protected-construction-or-fixture-code';reason='Explicit construction/test/fixture/qualifier helper remains protected even when it is an active runtime dependency.'
  elif path in chosen:
   disposition='candidate-public-code-schema-package';reason='Explicit final public selection: '+ '; '.join(chosen[path]['reasons'])
   C.relative(path);C.privacy(raw);public[path]=raw
  elif path.endswith('/genuine-work-history-v1-0208/provider.py'):disposition='protected-runtime-history-reader';reason='Actual production history selection/read/validate_policy/open_history/inspect_view code; exact protected host dependency pending explicit public selection, not a grant-construction helper.'
  else:disposition='protected-verification-history';reason='Full original history/dependency row retained; not selected as public implementation payload.'
  category[disposition]+=1
  rows.append({**row,'size_bytes':len(raw),'mode':oct(stat.S_IMODE(q.stat().st_mode)),'profile_verification_input':path in profile,'schema_execution_input':path in runtime,'original_schema_input':path in schema,'selected_core_member':in_core,'disposition':disposition,'reason':reason,'public_payload_proposed':path in public,'public_body_export_allowed':False,'private_field_findings':findings,'inspection_refusal_class':refusal})
  if index%4000==0:print(json.dumps({'source_rows_inspected':index,'public_proposed':len(public),'new_findings':len(new_findings)}),flush=True)
 assert set(public)==set(chosen),'public selection included a protected finding/archive/migration row'
 assert len(reconciled)==112 and set(prior)=={r['path'] for r in reconciled}
 snapshot=HERE/'public-payload.snapshot';exported=R02.export_files(public,snapshot,R02.OwnedScope(str(HERE)));snapshot.chmod(0o600)
 assert C.payload(C.read(snapshot))==public
 put(HERE/'migration-dispositions.json',{'schema_version':'lab-R06-original-migration-dispositions/v1-candidate','source_selection_binding':bind(ROOT/'implementation/lab-ontology/candidates/v1/migration/source-selection.json'),'original_items':migration_items,'items_accounted':140,'unmaterialized_binding_records':sum(r['source_binding'] is None for r in migration_items),'original_visibility_counts':dict(collections.Counter(r['privacy'] for r in migration_items)),'all_original_classifications_and_bindings_retained':True,'public_body_export_authorized':False,'authority_effect':'none','actual_owner_outcome':None})
 put(HERE/'prior-failed-boundary.json',{'schema_version':'lab-R06-retained-failed-boundary/v1-candidate','source_binding':bind(HERE.parent/'0006/source-manifest.json'),'terminal_binding':bind(RUN/'R06-api12-selection-terminal-0172.json'),'log_binding':bind(RUN/'R06-api12-selection-0172.log'),'originals_changed':False,'authority_effect':'none','actual_owner_outcome':None})
 put(HERE/'prior-exclusions.json',{'schema_version':'lab-R06-final-family-prior-exclusion-reconciliation/v1-candidate','api_source_binding':bind(API/'source-manifest.json'),'api_profile_binding':bind(API/'contract-profile.json'),'original95':95,'additional17':17,'exact_rows_reconciled':112,'rows':sorted(reconciled,key=lambda v:v['path']),'prior_findings_and_classifications_retained':True,'authority_effect':'none','actual_owner_outcome':None})
 put(HERE/'dependency-dispositions.json',{'schema_version':'lab-R06-final-family-dependency-dispositions/v1-candidate','api_source_binding':bind(API/'source-manifest.json'),'api_profile_binding':bind(API/'contract-profile.json'),'schema_execution_binding':bind(API/'SCHEMA-EXECUTION-DEPENDENCIES.json'),'rows':rows,'files_accounted':len(rows),'disposition_counts':dict(category),'new_field_or_format_findings':new_findings,'public_body_export_authorized':False,'source_proof_rows_removed':0,'R06_complete':False,'authority_effect':'none','actual_owner_outcome':None})
 missing=[{'path':r['path'],'sha256':r['sha256'],'disposition':r['disposition']} for r in rows if r['schema_execution_input'] and not r['public_payload_proposed']]
 put(HERE/'payload-selection.json',{'schema_version':'lab-R06-final-family-payload-selection/v1-candidate','source_binding':bind(HERE/'source-manifest.json'),'api_source_binding':bind(API/'source-manifest.json'),'api_profile_binding':bind(API/'contract-profile.json'),'public_selection_binding':load(SELECTION)['public_selection_binding'],'payload_binding':bind(snapshot),'payload_files':[{'path':k,'sha256':C.sha(v),'size_bytes':len(v)} for k,v in sorted(public.items())],'payload_members':len(public),'payload_bytes':sum(map(len,public.values())),'protected_dependency_members':len(rows)-len(public),'schema_execution_inputs_outside_public_payload':missing,'original_nonexportable_migration_items':140,'public_body_export_authorized':False,'public_payload_self_contained':False,'portable_runtime_required_by_selected_scope':False,'selected_environment':'local-Linux-repository','host_provided_original_dependencies_required':True,'complete_runtime_install_qualified':False,'R06_complete':False,'authority_effect':'none','actual_owner_outcome':None})
 assert bind(NATIVE)['sha256']==NATIVE_SHA
 native_descriptor={'schema_version':'lab-R06-native-execution-dependency-retention/v1-candidate','original_binding':bind(NATIVE),'original_mode':oct(stat.S_IMODE(NATIVE.stat().st_mode)),'signed_locator_unchanged':True,'native_execution_qualified':False,'runtime_activations':0,'authority_effect':'none'}
 files={'native/lab-context-native-reader':C.read(NATIVE),'native/dependency.json':C.encoded(native_descriptor)};archive=HERE/'protected-native-dependency.snapshot';archived=R02._archive_files(files,archive,R02.OwnedScope(str(HERE)));archive.chmod(0o600)
 outputs=[]
 for option in ('-l','-d'):
  result=subprocess.run(['/usr/bin/readelf',option,str(NATIVE)],check=True,capture_output=True,text=True)
  outputs.extend(v.strip() for v in result.stdout.splitlines() if 'interpreter:' in v or 'NEEDED' in v or 'RPATH' in v or 'RUNPATH' in v)
 with tempfile.TemporaryDirectory(prefix='cal-R06-native-retention-0241-') as temporary:
  root=Path(temporary);restored=root/'restored';observed=R02.restore(archive,bind(archive)['sha256'],restored,R02.OwnedScope(str(root)));assert R02.tree(restored)==files
  executable=restored/'native/lab-context-native-reader';mode=stat.S_IMODE(executable.stat().st_mode);assert mode==0o600 and not os.access(executable,os.X_OK);before=R02.tree(restored);retry=R02.restore(archive,bind(archive)['sha256'],restored,R02.OwnedScope(str(root)));assert retry['idempotent'] and R02.tree(restored)==before
 put(HERE/'native-remediation.json',{'schema_version':'lab-R06-native-dependency-remediation-preparation/v1-candidate','original_binding':bind(NATIVE),'protected_archive_binding':bind(archive),'archive_observation':archived,'actual_owned_scratch_restore':observed,'actual_exact_retry_observation':retry,'actual_restored_mode':oct(mode),'actual_restored_file_count':len(files),'actual_original_bytes_equal':True,'host_recovery_proof_binding':bind(RUN/'runtime-recovery-0209.json'),'native_executed':False,'native_executable_install_qualified':False,'signed_tmp_locator_changed':False,'portable_locator_or_ABI_remediation_performed':False,'portable_runtime_required_by_selected_scope':False,'host_provided_native_binding':bind(NATIVE),'host_provided_native_mode':oct(stat.S_IMODE(NATIVE.stat().st_mode)),'selected_environment':C.environment(),'expected_R02_environment':load(ROOT/'product/lab/release-candidates/v1/packaging/R02/packages/0003/selection.json')['environment'],'host_ABI_library_bindings':[bind(Path(n).resolve()) for n in ('/lib64/ld-linux-x86-64.so.2','/lib/x86_64-linux-gnu/libgcc_s.so.1','/lib/x86_64-linux-gnu/libc.so.6')],'selected_local_host_dependency_satisfied':stat.S_IMODE(NATIVE.stat().st_mode)==0o755 and C.environment()==load(ROOT/'product/lab/release-candidates/v1/packaging/R02/packages/0003/selection.json')['environment'],'readelf_observed_interpreter_and_libraries':outputs,'readelf_tool_binding':bind(Path('/usr/bin/readelf').resolve()),'optional_out_of_scope_portable_remediation':['Create a separately authorized signed source-family successor selecting a stable owned native executable locator and exact original/reproducible artifact hash; retain current signed /tmp locator unchanged in predecessor proofs.','Provide explicit executable-mode installation and dependency/host ABI closure for the selected ELF interpreter, libgcc_s.so.1 and libc.so.6; original R02 restore intentionally yields0600.','Qualify actual source readers and complete API against that successor; independently bind public/protected payload dispositions and original source proof inputs.'],'runtime_activations':0,'external_effects':0,'authority_effect':'none','actual_owner_outcome':None})
 put(HERE/'runtime-blockers.json',{'schema_version':'lab-R06-final-family-local-dependency-scenario-accounting/v1-candidate','selected_environment':'local-Linux-repository','release_scope_binding':bind(ROOT/'product/lab/release-candidates/v1/release-scope.json'),'portable_runtime_or_deployment_required':False,'host_provided_dependencies':[{'kind':'native-ELF','binding':bind(NATIVE),'mode':oct(stat.S_IMODE(NATIVE.stat().st_mode)),'required_for_selected_local_reader':True,'available_at_exact_hash':True,'provided_by':'selected-local-host','archive_restore_mode':'0o600','archive_is_executable_install':False},{'kind':'repository-source-and-profile-verification-inputs','api_source_binding':bind(API/'source-manifest.json'),'api_profile_binding':bind(API/'contract-profile.json'),'all_selected_original_bytes_verified':True,'required_protected_rows':[{'path':r['path'],'sha256':r['sha256'],'disposition':r['disposition']} for r in rows if not r['public_payload_proposed']]}],'schema_execution_inputs_outside_public_payload':missing,'selected_local_dependency_availability_blockers':[],'declared_scenario_obligations':[{'scenario':'fresh-install-upgrade-replay-rollback-and-export-in-selected-local-environment','status':'separate-actual-R02-and-common-API-qualification-required','rationale':'All original repository/host dependencies remain supplied at exact hashes; this disposition proposal neither executes nor replaces those qualified scenarios.'},{'scenario':'restore-native-archive-as-executable','status':'not-selected-not-qualified','rationale':'Original R02 recovery yields0600; the selected native executable remains the intact host-provided0755 artifact. No claim that archival recovery executes it.'}],'remaining_blockers':[{'subject':'final-exact-release-family-and-evidence','reason':'This accounts exact candidate final-family bytes, not yet the final R07/S02 release-family/evidence selection. Actual common API qualification and final candidate release selection remain independent.'}],'public_payload_self_contained':False,'self_containment_is_not_selected_acceptance_requirement':True,'original_proof_rows_removed':0,'candidate_preparation_only':True,'R06_complete':False,'authority_effect':'none','actual_owner_outcome':None})
 frozen(pin);print(json.dumps({'result':'PASS-candidate-proposal','source_rows':len(rows),'public_members':len(public),'prior_exclusions':len(reconciled),'guard_inputs_outside_public_payload':len(missing),'new_findings':len(new_findings),'source_proof_rows_removed':0}),flush=True)


if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('command',choices=['freeze','proposal']);parser.add_argument('--source-sha256');parser.add_argument('--api-directory');parser.add_argument('--api-source-sha256');parser.add_argument('--api-profile-sha256');parser.add_argument('--public-selection');parser.add_argument('--public-selection-sha256');args=parser.parse_args()
 if args.command=='freeze':
  require(all((args.api_directory,args.api_source_sha256,args.api_profile_sha256,args.public_selection,args.public_selection_sha256)),'explicit finalAPI/source/profile/public-selection pins required before freeze');freeze(args)
 else:require(args.source_sha256,'independent boundary source pin required');proposal(args.source_sha256)
