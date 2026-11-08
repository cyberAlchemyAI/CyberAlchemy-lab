"""Rebuild the maintained current-fixture suite over portable API74 code.

Original predecessor tests stay immutable. Nine disclosed successor assertions
retain original-source identity/security invariants for the28-target dataset.
"""
import argparse,ast,hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
BASE=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v74-portable-inputs-0001'
LOGICAL=BASE.parent/'api-integration-v75-current-fixtures-0001';POST=HERE/'api75-production-postimages-0001'
sha=lambda raw:hashlib.sha256(raw).hexdigest()
def need(v,m):
 if not v:raise ValueError(m)
def methods(root):
 result={}
 for file in [*root.glob('test_*.py'),*root.glob('run_*checks.py')]:
  for cls in ast.parse(file.read_text()).body:
   if isinstance(cls,ast.ClassDef):
    for node in cls.body:
     if isinstance(node,ast.FunctionDef) and node.name.startswith('test_'):result[file.name+':'+cls.name+'.'+node.name]=ast.dump(node,include_attributes=False)
 return result

def rebuild(destination):
 destination=Path(destination);need(destination.is_absolute() and not destination.exists(),'fresh code rebuild destination required')
 prep=json.loads((HERE/'API74-CODE-PREPARATION-0002.json').read_bytes())
 for row in prep['files']:need(sha((ROOT/row['path']).read_bytes())==row['sha256'],'portableAPI74 input changed')
 shutil.copytree(BASE,destination)
 pins=json.loads((POST/'PINS.json').read_bytes())
 for row in pins['files']:
  raw=(POST/row['name']).read_bytes();need(sha(raw)==row['sha256'],'selected maintained production postimage changed');(destination/row['name']).write_bytes(raw)
 metadata_origin=HERE/'metadata-reader-origin-successor-0001'
 metadata_pins=json.loads((metadata_origin/'PINS.json').read_bytes())
 for row in metadata_pins['files']:
  raw=(metadata_origin/row['name']).read_bytes();need(sha(raw)==row['sha256'],'selected metadata reader origin successor changed');(destination/row['name']).write_bytes(raw)
 profile_post=HERE/'api75-profile-binding-postimages-0001'
 for row in json.loads((profile_post/'PINS.json').read_bytes())['files']:
  raw=(profile_post/row['name']).read_bytes();need(sha(raw)==row['sha256'],'selected strict profile-binding postimage changed');(destination/row['name']).write_bytes(raw)
 owned_post=HERE/'api75-owned-workflow-postimages-0001'
 owned_pins=json.loads((owned_post/'DELTA-PINS.json').read_bytes())
 for name,pin in owned_pins['postimages'].items():
  raw=(owned_post/name).read_bytes();need(sha(raw)==pin,'selected owned workflow postimage changed');(destination/name).write_bytes(raw)
 identity_post=ROOT/'implementation/lab-runtime/local-host/t31-public-owned-transition-0001/api73-reference-overlay-0003'
 identity_pins=json.loads((identity_post/'IDENTITY-DELTA-PINS.json').read_bytes())
 for name in ('owned_workflow_transition.py','owned_workflow_semantics.py'):
  raw=(identity_post/name).read_bytes();need(sha(raw)==identity_pins['files'][name],'selected original-schema identity postimage changed');(destination/name).write_bytes(raw)
 auth_post=HERE/'api75-owned-auth-postimages-0001';auth_pins=json.loads((auth_post/'DELTA-PINS.json').read_bytes());raw=(auth_post/'auth.py').read_bytes();need(sha(raw)==auth_pins['postimage_auth_sha256'],'selected owned workflow auth postimage changed');(destination/'auth.py').write_bytes(raw)
 for source,name,pin in (
  (ROOT/'implementation/lab-runtime/local-host/t17-current-ontology-0001/postimages-0002/ontology_projection.py','ontology_projection.py','97fb7a85e58e2fbcc050089023beec6d697bee2249915440bad48287201fba88'),
  (ROOT/'implementation/lab-runtime/local-host/t31-current-ontology-capture-0001/postimages-0001/workflow_ontology_outputs.py','workflow_ontology_outputs.py','3c4daa9660888bb478d12ab9e1a931148eee327bb57a3b3cc880a9548561e416')):
  raw=source.read_bytes();need(sha(raw)==pin,'selected current ontology postimage changed');(destination/name).write_bytes(raw)
 origin_post=HERE/'api75-current-origin-postimages-0001'
 for row in json.loads((origin_post/'PINS.json').read_bytes())['files']:
  raw=(origin_post/row['name']).read_bytes();need(sha(raw)==row['sha256'],'selected current family origin postimage changed');(destination/row['name']).write_bytes(raw)
 root_post=HERE/'api75-root-portability-postimages-0001'
 for row in json.loads((root_post/'PINS.json').read_bytes())['files']:
  raw=(root_post/row['name']).read_bytes();need(sha(raw)==row['sha256'],'selected provider ROOT postimage changed');(destination/row['name']).write_bytes(raw)
 delivery_post=HERE/'api75-delivery-selection-postimages-0001'
 for row in json.loads((delivery_post/'PINS.json').read_bytes())['files']:
  raw=(delivery_post/row['name']).read_bytes();need(sha(raw)==row['sha256'],'selected exact view delivery postimage changed');(destination/row['name']).write_bytes(raw)
 for source,name,pin in (
  (ROOT/'implementation/lab-runtime/local-host/t03-portable-session-external-0002/session_source_freshness.py','session_source_freshness.py','e785cac6101b8680b58ce17ceacbb5e61d151d6c0e8a5a3152a447ccc31a85b2'),
  (ROOT/'implementation/lab-runtime/local-host/t22-retained-origin-resolution-0001/postimages-0001/fixture_resolution_handler.py','fixture_resolution_handler.py','f3a756e7ec65b1741e88eb61cf68e7502165935909cf44862c2bdf25e8004f8e')):
  raw=source.read_bytes();need(sha(raw)==pin,'selected final portable handler postimage changed');(destination/name).write_bytes(raw)
 effect_post=ROOT/'implementation/lab-runtime/local-host/t03-portable-effect-external-0001'
 for name,pin in (
  ('machine_transport.py','8a4c4af82ec7bb2bb1339e0160962217d0ca380015e4ec67ec3e4edd9a236a99'),
  ('derived_effects.py','c40a26a4526891392ca24a18e8b805c1dc1a786bd3c35274af53883dbf866e12')):
  raw=(effect_post/name).read_bytes();need(sha(raw)==pin,'reviewed exact Machine/Derived external propagation postimage changed');(destination/name).write_bytes(raw)
 flat_post=HERE/'api75-flat-current-evidence-postimages-0003'
 raw=(flat_post/'guard.py').read_bytes();need(sha(raw)=='0b5fdb9365b17799e692605f5818a469d1788f4cd4851d146167522636213eea','reviewed exact seven-row Source allowlist changed');(destination/'guard.py').write_bytes(raw)
 release_post=HERE/'api75-release-evidence-path-postimages-0001/installation_release.py'
 raw=release_post.read_bytes();need(sha(raw)=='e08388166d7e1edd75d9256266b8c2fb6b88d6b768cf3eeb9bca78bfecfecc69','reviewed exact installed release reference path fix changed');(destination/'installation_release.py').write_bytes(raw)
 ontology_post=ROOT/'implementation/lab-runtime/local-host/t31-current-ontology-capture-0001/native-kind-postimages-0001/ontology_projection.py'
 raw=ontology_post.read_bytes();need(sha(raw)=='605021e7bfe39fa867407404de48285660bd6a251b7f1ce4f1183658746c047e','reviewed exact native node/relation vocabulary changed');(destination/'ontology_projection.py').write_bytes(raw)
 for name in ('classification_fixture.py','failure_fixture.py','challenge_fixture.py','review_fixture.py','metadata_fixture.py','workflow_fixture.py'):
  file=destination/name;text=file.read_text();prefix='source' if name=='metadata_fixture.py' else 'P.source';needle="source_name='custody-participation'";need(text.count(needle)==1,'fixture policy seam differs');file.write_text(text.replace(needle,'source_name='+prefix+'.CURRENT_LEGACY_NAME'))
 for name in ('package_fixture.py','package_export_fixture.py'):
  file=destination/name;text=file.read_text();need(text.count('source.custody_delivery()')==1,'package record selector seam differs');file.write_text(text.replace('source.custody_delivery()','source.current_legacy_delivery()'))
 for file in destination.glob('test_*.py'):
  text=file.read_text().replace("P.source.replay_source('custody-participation')","P.source.replay_source(P.source.CURRENT_LEGACY_NAME)").replace("source.replay_source('custody-participation')","source.replay_source(source.CURRENT_LEGACY_NAME)").replace('source.custody_delivery()','source.current_legacy_delivery()')
  if file.name=='test_custody_api.py':text=text.replace('self.assertIs(source.legacy_delivery(),D)','self.assertIs(source.current_legacy_delivery(),D)').replace('self.assertEqual(len(subjects),23)','self.assertEqual(len(subjects),28)')
  if file.name in ('test_challenge_api.py','test_preparation_corrected.py'):
   text=text.replace("P.source.CURRENT_LEGACY_NAME!='completion-legacy:legacy-local-4636eca980a5d94d'","P.source.CURRENT_LEGACY_NAME!=P.source.PORTABLE.value('identity.source_name')").replace("cls.view.legacy_signed_sources.source_cut['store_ref']!='completion-legacy-local-4636eca980a5d94d'","cls.view.legacy_signed_sources.source_cut['store_ref']!=P.source.CURRENT_LEGACY_STORE").replace("view.legacy_signed_sources.source_cut['store_ref']!='completion-legacy-local-4636eca980a5d94d'","view.legacy_signed_sources.source_cut['store_ref']!=source.CURRENT_LEGACY_STORE")
  if file.name=='test_metadata_scope.py':
   text=text.replace('self.assertEqual(len(self.view.subjects),582)','self.assertEqual(len(self.view.subjects),619)').replace('wrong=source.inspection(data,self.view.selected,self.view.originals,self.view.handle)','wrong=source.inspection(data,self.view.selected,self.view.originals,self.view.handle,origin_view=self.view)')
  if file.name=='test_guarded_reads.py':
   text=text.replace('from . import artifact_model as M','from . import artifact_model as M\nfrom . import guarded_reads as maintained_guarded_reads').replace("patch.object(source, 'custody_delivery', wraps=source.custody_delivery)","patch.object(maintained_guarded_reads, 'legacy_view_guard', wraps=maintained_guarded_reads.legacy_view_guard)")
  file.write_text(text)
 import importlib.util
 schema_patch=HERE/'auth_schema_current_names.py';spec=importlib.util.spec_from_file_location('_cal_current_source_schema_constructor',schema_patch);helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
 schema,source_name_delta=helper.apply(json.loads((BASE/'authentication.schema.json').read_bytes()))
 budget_spec=importlib.util.spec_from_file_location('_cal_current_source_budget_constructor',HERE/'auth_schema_current_budget_0001.py');budget_helper=importlib.util.module_from_spec(budget_spec);budget_spec.loader.exec_module(budget_helper);schema,budget_delta=budget_helper.apply(schema)
 (destination/'authentication.schema.json').write_text(json.dumps(schema,sort_keys=True,indent=2)+'\n')
 for file in destination.rglob('*.py'):compile(file.read_bytes(),str(file),'exec',dont_inherit=True)
 before,after=methods(BASE),methods(destination)
 need(set(before)==set(after) and len(before)==345,'maintained inherited test inventory differs')
 changed=sorted(name for name in before if before[name]!=after[name]);need(changed==['test_custody_api.py:OriginalAPI.test_01_same_original_reader_objects','test_custody_api.py:OriginalAPI.test_03_all23original_bytes_and_headers','test_guarded_reads.py:GuardedReads.test_batch_full_delivery_preflight_at_both_boundaries','test_guarded_reads.py:GuardedReads.test_batch_nested_same_view_retains_outer_guards','test_guarded_reads.py:GuardedReads.test_outside_batch_full_preflight_is_retained','test_metadata_scope.py:MetadataScopes.test_00_current_metadata_after_original_Assignment_expiry','test_metadata_scope.py:MetadataScopes.test_06_original_reader_Principal_cannot_be_impersonated','test_metadata_scope.py:MetadataScopes.test_19_original_period_and_signed_source_unchanged','test_metadata_scope.py:MetadataScopes.test_21_changed_prefix_projection_refused'],'undisclosed maintained assertion change')
 files=[{'path':str((LOGICAL/file.relative_to(destination)).relative_to(ROOT)),'sha256':sha(file.read_bytes())} for file in sorted(destination.rglob('*')) if file.is_file()]
 return {'schema_version':'lab-maintained-current-fixture-code-stage/v1','status':'CODE-REBUILT-NOT-RUN','files':files,'inherited_case_count':345,'unchanged_method_asts':336,'reviewed_successor_assertions':changed,'source_profile_generated_per_install':True,'authority_effect':'none'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('destination',type=Path);p.add_argument('--report',type=Path,required=True);a=p.parse_args();report=rebuild(a.destination);a.report.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n');print(json.dumps({'status':report['status'],'files':len(report['files']),'maintained_cases':345},sort_keys=True))
