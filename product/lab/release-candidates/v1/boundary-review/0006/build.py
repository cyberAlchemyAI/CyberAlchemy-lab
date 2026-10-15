"""Exact API12 payload/disposition proposal; all original proof rows retained."""
import argparse,collections,datetime,hashlib,importlib.util,json,os,re,stat,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5];RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction';API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v12'
API_SOURCE='5c7f5c69d5795f5a5c0cb8b67c52a47621f8eab746c6afd70d42f06177ddc6ae';API_PROFILE='2ae21af91f8366247cbd3ff77292d307519663fd020bac20cb410fd2d76db56a';NATIVE=Path('/tmp/cal-R03-mapped-native-build-0002/target/debug/lab-context-native-reader');NATIVE_SHA='fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'
R02PATH=ROOT/'product/lab/release-candidates/v1/packaging/R02/successors/0001'
sys.path.insert(0,str(R02PATH));import common as C
spec=importlib.util.spec_from_file_location('_R06_0006_original_installer',R02PATH/'installer.py');R02=importlib.util.module_from_spec(spec);spec.loader.exec_module(R02)
spec=importlib.util.spec_from_file_location('_R06_0006_original_inspector',HERE.parent/'0002/review.py');R=importlib.util.module_from_spec(spec);spec.loader.exec_module(R)
def bind(p):return {'path':str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p),'sha256':C.sha(C.read(p))}
def load(p):return C.parse(C.read(p))
def put(p,v):C.emit(p,v);p.chmod(0o600)
def check_api_controls():
 assert bind(API/'source-manifest.json')['sha256']==API_SOURCE and bind(API/'contract-profile.json')['sha256']==API_PROFILE
 return load(API/'source-manifest.json'),load(API/'contract-profile.json'),load(API/'SCHEMA-EXECUTION-DEPENDENCIES.json')
def frozen(pin):
 assert bind(HERE/'source-manifest.json')['sha256']==pin
 m=load(HERE/'source-manifest.json')
 for row in m['files']:assert bind(ROOT/row['path'])==row,row['path']
 check_api_controls();return m

def freeze():
 assert not (HERE/'source-manifest.json').exists();a,p,s=check_api_controls();full={r['path']:r for r in a['files']}
 for row in p['files']+s['files']:assert full[row['path']]==row
 controls=[API/'source-manifest.json',API/'contract-profile.json',API/'SCHEMA-EXECUTION-DEPENDENCIES.json',API/'integration-members.json',HERE/'build.py',HERE/'check.py',HERE/'disposition.schema.json',HERE/'README.md',RUN/'authorization.json',RUN/'ARE-payload-and-pilot-intake-boundary-0181.json',RUN/'installation-release-R06-api10-audit-0148.json',RUN/'installation-release-R06-api10-remediation-0148.json',HERE.parent/'0003/inventory.json',HERE.parent/'0004/format-resolution.json',HERE.parent/'0005/session-exclusions.json',HERE.parent/'0002/review.py',R02PATH/'common.py',R02PATH/'installer.py',ROOT/'implementation/lab-ontology/candidates/v1/migration/source-selection.json']
 context=RUN/'context-R06-api12-selection-0172.json';put(context,{'schema_version':'lab-bounded-context/v1-candidate','task':'R06 exact API12 candidate payload and protected dependency disposition proposal','source_bindings':[bind(x) for x in controls],'constraints':['All original proof rows retained; all original95 plus17new API10 findings explicitly reconciled.','Public proposal is code/schema/package bytes only; protected history/test state/caches/logs are separate.','Source metadata or body classification is not proof of persisted working RAM or credential leakage.','Original R02 methods only; native byte archival/owned scratch restore is not executable installation or source locator remediation.','No publication, activation, canonical admission, owner approval, whole API qualification or final R06 completion.'],'authority_effect':'none','actual_owner_outcome':None})
 for q in controls+[context]:full[bind(q)['path']]=bind(q)
 for row in full.values():assert bind(ROOT/row['path'])==row,row['path']
 put(HERE/'source-manifest.json',{'schema_version':'lab-R06-API12-payload-proposal-source/v1-candidate','files':[full[k] for k in sorted(full)],'api_source_binding':bind(API/'source-manifest.json'),'api_profile_binding':bind(API/'contract-profile.json'),'schema_execution_binding':bind(API/'SCHEMA-EXECUTION-DEPENDENCIES.json'),'context_binding':bind(context),'original_proof_rows_retained':True,'frozen_before_observations':True,'authority_effect':'none','actual_owner_outcome':None})
 print(json.dumps({'result':'FROZEN','source_binding':bind(HERE/'source-manifest.json'),'files':len(full)}),flush=True)

def proposal(pin):
 frozen(pin);a,p,s=check_api_controls();profile={r['path'] for r in p['files']};runtime={r['path'] for r in s['files']};schema={r['path'] for r in load(API/'schema-inputs.json')['files']}
 audit=load(RUN/'installation-release-R06-api10-audit-0148.json');prior={r['path']:r for r in audit['rows']};assert len(prior)==112
 old=load(HERE.parent/'0003/inventory.json');oldflag={r['path'] for r in old['rows'] if r['disposition']!='unselected-final-release-source'};assert len(oldflag)==95 and len(set(prior)-oldflag)==17
 original_proposals={r['path']:r for r in load(HERE.parent/'0005/session-exclusions.json')['exclusion_proposals']+load(HERE.parent/'0004/format-resolution.json')['TOML_observations']+load(HERE.parent/'0004/format-resolution.json')['diagnostic_exclusions']}
 migrations=load(ROOT/'implementation/lab-ontology/candidates/v1/migration/source-selection.json');nonexport={r['source_binding']['path']:r for r in migrations['items'] if not r['public_body_export_allowed']};assert len([r for r in migrations['items'] if not r['public_body_export_allowed']])==140
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
  elif package or path in schema or q.suffix=='.whl' and path in runtime or in_core and q.suffix in ('.py','.schema.json','.md') or path in runtime and q.suffix=='.py' or path.startswith('implementation/lab-runtime/') and q.suffix=='.py' or path.startswith('implementation/lab-context/candidates/v1/native/') and q.suffix in ('.rs','.toml','.lock'):
   disposition='candidate-public-code-schema-package';reason='Exact selected implementation/schema/package source proposal; unchanged scanner completed without private-field finding.'
   C.relative(path);C.privacy(raw);public[path]=raw
  else:disposition='protected-verification-history';reason='Full original history/dependency row retained; not selected as public implementation payload.'
  category[disposition]+=1
  rows.append({**row,'size_bytes':len(raw),'mode':oct(stat.S_IMODE(q.stat().st_mode)),'profile_verification_input':path in profile,'schema_execution_input':path in runtime,'original_schema_input':path in schema,'selected_core_member':in_core,'disposition':disposition,'reason':reason,'public_payload_proposed':path in public,'public_body_export_allowed':False,'private_field_findings':findings,'inspection_refusal_class':refusal})
  if index%4000==0:print(json.dumps({'source_rows_inspected':index,'public_proposed':len(public),'new_findings':len(new_findings)}),flush=True)
 assert len(reconciled)==112 and set(prior)=={r['path'] for r in reconciled}
 snapshot=HERE/'public-payload.snapshot';exported=R02.export_files(public,snapshot,R02.OwnedScope(str(HERE)));snapshot.chmod(0o600)
 assert C.payload(C.read(snapshot))==public
 put(HERE/'prior-exclusions.json',{'schema_version':'lab-R06-API12-prior-exclusion-reconciliation/v1-candidate','api_source_binding':bind(API/'source-manifest.json'),'api_profile_binding':bind(API/'contract-profile.json'),'original95':95,'additional17':17,'exact_rows_reconciled':112,'rows':sorted(reconciled,key=lambda v:v['path']),'prior_findings_and_classifications_retained':True,'authority_effect':'none','actual_owner_outcome':None})
 put(HERE/'dependency-dispositions.json',{'schema_version':'lab-R06-API12-dependency-dispositions/v1-candidate','api_source_binding':bind(API/'source-manifest.json'),'api_profile_binding':bind(API/'contract-profile.json'),'schema_execution_binding':bind(API/'SCHEMA-EXECUTION-DEPENDENCIES.json'),'rows':rows,'files_accounted':len(rows),'disposition_counts':dict(category),'new_field_or_format_findings':new_findings,'public_body_export_authorized':False,'source_proof_rows_removed':0,'R06_complete':False,'authority_effect':'none','actual_owner_outcome':None})
 missing=[{'path':r['path'],'sha256':r['sha256'],'disposition':r['disposition']} for r in rows if r['schema_execution_input'] and not r['public_payload_proposed']]
 put(HERE/'payload-selection.json',{'schema_version':'lab-R06-API12-payload-selection/v1-candidate','source_binding':bind(HERE/'source-manifest.json'),'api_source_binding':bind(API/'source-manifest.json'),'api_profile_binding':bind(API/'contract-profile.json'),'payload_binding':bind(snapshot),'payload_files':[{'path':k,'sha256':C.sha(v),'size_bytes':len(v)} for k,v in sorted(public.items())],'payload_members':len(public),'payload_bytes':sum(map(len,public.values())),'protected_dependency_members':len(rows)-len(public),'schema_execution_inputs_outside_public_payload':missing,'original_nonexportable_migration_items':140,'public_body_export_authorized':False,'public_payload_self_contained':False,'complete_runtime_install_qualified':False,'R06_complete':False,'authority_effect':'none','actual_owner_outcome':None})
 assert bind(NATIVE)['sha256']==NATIVE_SHA
 native_descriptor={'schema_version':'lab-R06-native-execution-dependency-retention/v1-candidate','original_binding':bind(NATIVE),'original_mode':oct(stat.S_IMODE(NATIVE.stat().st_mode)),'signed_locator_unchanged':True,'native_execution_qualified':False,'runtime_activations':0,'authority_effect':'none'}
 files={'native/lab-context-native-reader':C.read(NATIVE),'native/dependency.json':C.encoded(native_descriptor)};archive=HERE/'protected-native-dependency.snapshot';archived=R02._archive_files(files,archive,R02.OwnedScope(str(HERE)));archive.chmod(0o600)
 outputs=[]
 for option in ('-l','-d'):
  result=subprocess.run(['/usr/bin/readelf',option,str(NATIVE)],check=True,capture_output=True,text=True)
  outputs.extend(v.strip() for v in result.stdout.splitlines() if 'interpreter:' in v or 'NEEDED' in v or 'RPATH' in v or 'RUNPATH' in v)
 with tempfile.TemporaryDirectory(prefix='cal-R06-native-retention-0172-') as temporary:
  root=Path(temporary);restored=root/'restored';observed=R02.restore(archive,bind(archive)['sha256'],restored,R02.OwnedScope(str(root)));assert R02.tree(restored)==files
  executable=restored/'native/lab-context-native-reader';mode=stat.S_IMODE(executable.stat().st_mode);assert mode==0o600 and not os.access(executable,os.X_OK);before=R02.tree(restored);retry=R02.restore(archive,bind(archive)['sha256'],restored,R02.OwnedScope(str(root)));assert retry['idempotent'] and R02.tree(restored)==before
 put(HERE/'native-remediation.json',{'schema_version':'lab-R06-native-dependency-remediation-preparation/v1-candidate','original_binding':bind(NATIVE),'protected_archive_binding':bind(archive),'archive_observation':archived,'actual_owned_scratch_restore':observed,'actual_exact_retry_observation':retry,'actual_restored_mode':oct(mode),'actual_restored_file_count':len(files),'actual_original_bytes_equal':True,'native_executed':False,'native_executable_install_qualified':False,'signed_tmp_locator_changed':False,'locator_or_ABI_blocker_resolved':False,'readelf_observed_interpreter_and_libraries':outputs,'readelf_tool_binding':bind(Path('/usr/bin/readelf').resolve()),'proposed_final_remediation':['Create a separately authorized signed source-family successor selecting a stable owned native executable locator and exact original/reproducible artifact hash; retain current signed /tmp locator unchanged in predecessor proofs.','Provide explicit executable-mode installation and dependency/host ABI closure for the selected ELF interpreter, libgcc_s.so.1 and libc.so.6; original R02 restore intentionally yields0600.','Qualify actual source readers and complete API against that successor; independently bind public/protected payload dispositions and original source proof inputs.'],'runtime_activations':0,'external_effects':0,'authority_effect':'none','actual_owner_outcome':None})
 put(HERE/'runtime-blockers.json',{'schema_version':'lab-R06-API12-public-packaging-blockers/v1-candidate','blockers':[{'subject':'native-signed-scratch-locator-and-ABI','original_binding':bind(NATIVE),'reason':'Mandatory selected native ELF remains signed to a /tmp path; protected archival does not rebind original source selection. Its interpreter/shared-library ABI and executable mode are absent from original R02 public code installation.'},{'subject':'protected-source-and-profile-proof-inputs','reason':'The public proposal omits protected histories, signed Session archives, original proof controls and test material that remain mandatory full source/profile verification inputs. They require separately protected provisioning, not deletion or public export.'},{'subject':'guard-selected-inputs-outside-public-payload','exact_inputs':missing,'reason':'Conservative schema execution guard still requires these exact nonpublic code/control/proof inputs; the public proposal is not a self-contained runtime replacement.'},{'subject':'final-source-family-and-qualification','reason':'Actual common API12 qualification remains independent and in progress; final R07/S02 family selection and complete release disposition/acceptance/human evidence and R08 owner outcome are not supplied by this proposal.'}],'public_payload_self_contained':False,'original_proof_rows_removed':0,'candidate_preparation_only':True,'R06_complete':False,'authority_effect':'none','actual_owner_outcome':None})
 frozen(pin);print(json.dumps({'result':'PASS-candidate-proposal','source_rows':len(rows),'public_members':len(public),'prior_exclusions':len(reconciled),'guard_inputs_outside_public_payload':len(missing),'new_findings':len(new_findings),'source_proof_rows_removed':0}),flush=True)

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('command',choices=['freeze','proposal']);parser.add_argument('--source-sha256');args=parser.parse_args()
 if args.command=='freeze':freeze()
 else:assert args.source_sha256;proposal(args.source_sha256)
