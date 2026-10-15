"""Owned nonactivating capture input proposal; no capture writer import/effect."""
import ast,hashlib,json
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
HERE=Path(__file__).absolute().parent
CAP4=RUN/'T07/api17-task-local-capture-0004'
CAP5=RUN/'T07/api17-task-local-capture-0005'
API='product/lab/release-candidates/v1/interface/api-integration-v17/'
def bind(path):return {'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def load(path):return json.loads(path.read_bytes())
def write(name,value):
 with (HERE/name).open('x') as f:f.write(json.dumps(value,sort_keys=True,indent=2)+'\n')
def literal(path,name):
 node=next(n for n in ast.parse(path.read_bytes()).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets));return ast.literal_eval(node.value)
def main():
 selection=load(CAP5/'component-selection-draft.json');required=load(CAP5/'required-components.json')['bindings'];lineage=load(CAP4/'lineage.json')
 predecessor_path=CAP4/'lineage-preimages'/lineage['capture3_selection_binding']['path'];old=load(predecessor_path)
 prior=load(CAP4/'preimage/source-manifest.json');original=load(ROOT/'product/lab/release-candidates/v1/interface/api-integration-v16/source-manifest.json')
 current=load(RUN/'T03/margin-final-capture-closure-0001/current-api-expectations.json')['files']
 oldrows={r['path']:r for r in prior['files']};originalnames={r['path'] for r in original['files']}
 replacements=[]
 for row in current:
  if row['path'] in oldrows and oldrows[row['path']]!=row:
   assert row['path'] not in originalnames
   replacements.append({'preimage_binding':oldrows[row['path']],'postimage_binding':row})
 assert len(replacements)==7
 components={r['path']:r for r in old['component_manifests']}
 manifest_paths=[required[k]['path'] for k in ['recipe5_manifest','parent_capture4_manifest','input_preparer4_manifest','instrumentation_manifest']]
 manifest_paths += [str((RUN/p).relative_to(ROOT)) for p in ['T35/full-learning-driver-0004/source-manifest.json','T03/margin-software-manifest-preparation-0001/source-manifest.json','T03/caller-integration-0004/source-manifest.json','T03/participation-snapshot-reuse-0001/source-manifest.json','T03/integrity-comparison-preparation-0001/source-manifest.json','T03/integrity-hardening-0002/source-manifest.json','T03/margin-final-capture-closure-0001/source-manifest.json','T07/api17-task-local-capture-0005/source-manifest.json']]
 for name in manifest_paths:components[name]={'base':'.',**bind(ROOT/name)}
 assert len(components)==19 and not any(r['path'].endswith('observed-margin-adapter-0003/source-manifest.json') for r in components.values())
 descriptor_path=RUN/'T02/optimized-family-preparation-0005/instances/optimized-0005/runtime/runtime-selection.json';descriptor=load(descriptor_path)
 family_path=ROOT/descriptor['actual_family_selection_binding']['path'];family=load(family_path)
 acceptance_path=RUN/'T00/family5-pre-source-acceptance-0001.json';acceptance=load(acceptance_path)
 active={'descriptor_binding':bind(descriptor_path),'descriptor_keys':sorted(descriptor),'family_bindings':family['family_bindings'],'phase_report_bindings':family['phase_reports'],'actual_family_selection_binding':descriptor['actual_family_selection_binding'],'template_preimages':descriptor['original_template_preimages'],'pre_source_acceptance_binding':bind(acceptance_path)}
 direct={r['path']:r for r in old['direct_inputs']}
 def add(row):
  row={'path':row['path'],'sha256':row['sha256']}
  if row['path'] in direct:assert direct[row['path']]==row
  direct[row['path']]=row
 for row in required.values():add(row)
 extra=['T00/selector-merge-review-0005.json','T02/selector-merge-0005/application-receipt.json','T03/margin-software-manifest-preparation-0001/input-selection-0002.json','T03/margin-software-manifest-preparation-0001/independent-review-0002.json','T03/margin-final-capture-closure-0001/HANDOFF.json','T03/margin-final-capture-closure-0001/independent-review-0001.json','T02/optimized-family-preparation-0005/reports/root-actual-full-family-independent-review-0001.json','T02/optimized-family-preparation-0005/reports/root-selector-overlay-independent-review-0001.json','T35/full-learning-driver-0004/independent-review-0001.json','T35/full-learning-input-preparation-0004/prepare.py','T35/full-learning-input-preparation-0004/expected-input-packet.schema.json','T07/revision-0002/dependency-selection-0002.json','T00/family5-pre-source-acceptance-0001.json']
 for name in extra:add(bind(RUN/name))
 for row in acceptance.values():
  if type(row)is dict and set(row)=={'path','sha256'}:add(row)
 optimization=load(RUN/'T02/optimized-family-preparation-0005/optimization-selection.json')
 for name,row in optimization.items():
  if name.endswith('_binding') and type(row)is dict and {'path','sha256'}<=set(row):add(row)
 driver=RUN/'T35/full-learning-driver-0004';preparer=RUN/'T35/full-learning-input-preparation-0004/prepare.py'
 originals=literal(preparer,'ORIGINALS');public={k:{'path':path,'sha256':pin} for k,(path,pin) in originals.items()}
 public.update({k:bind(path) for k,path in {'driver_binding':driver/'driver.py','selection_schema_binding':driver/'selection.schema.json','composition_binding':RUN/'T03/observed-margin-adapter-0003/postimages/composition.py','software_inventory_binding':RUN/'T03/margin-software-manifest-preparation-0001/software-0002.json','software_input_selection_binding':RUN/'T03/margin-software-manifest-preparation-0001/input-selection-0002.json','selector_merge_review_binding':RUN/'T00/selector-merge-review-0005.json','postselector_current_context_binding':ROOT/(API+'current_context_sessions.py'),'dependency_selection_binding':RUN/'T07/revision-0002/dependency-selection-0002.json','preparer_binding':preparer,'family_closure_preview_binding':ROOT/acceptance['preview_binding']['path'],'family_closure_acceptance_binding':acceptance_path,'instrumentation_binding':RUN/'T35/instrumentation-observation-0001/instrumentation.json','runtime_selection_binding':descriptor_path}.items()})
 public['api_bootstrap_bindings']=[bind(ROOT/(API+n)) for n in ['__init__.py','guard.py']]
 public['helper_bindings']={name:bind(ROOT/(API+name+'.py')) for name in ['margin_capture','margin_kernel','margin_seal','observed_margin']}
 public['lifecycle_bindings']={lane:bind(driver/(lane+'_lifecycle.py')) for lane in ['positive','security']}
 public['expected_software_rows']=load(RUN/'T03/margin-software-manifest-preparation-0001/software-0002.json')['files']
 def flatten(value):
  if type(value)is dict:
   if set(value)=={'path','sha256'}:yield value
   else:
    for child in value.values():yield from flatten(child)
  elif type(value)is list:
   for child in value:yield from flatten(child)
 for row in flatten(public):add(row)
 inputs={'api_expected_files':current,'helper_roots':sorted({str(Path(r['path']).parent) for r in old['helper_expected_files']}),'helper_expected_files':old['helper_expected_files'],'component_manifests':list(components.values()),'direct_inputs':[direct[n] for n in sorted(direct)],'replacement_bindings':replacements,'active_family':active,'public_software_manifest_binding':public['software_inventory_binding'],'guard_binding':old['guard_binding'],'profile_updates':[]}
 merged_names=['T00/margin-merge-receipt-0004.json','T02/composite-merge-preparation-0004/application-receipt.json','T02/selector-merge-0005/application-receipt.json','T00/selector-merge-review-0005.json','T03/margin-software-manifest-preparation-0001/independent-review-0002.json','T03/margin-final-capture-closure-0001/independent-review-0001.json','T02/optimized-family-preparation-0005/root-actual-family-selection-0001.json','T02/optimized-family-preparation-0005/reports/root-actual-full-family-independent-review-0001.json','T02/optimized-family-preparation-0005/reports/root-selector-overlay-independent-review-0001.json','T00/family5-pre-source-acceptance-0001.json']
 packet={'schema_version':'lab-T00-final-capture5-inputs/v1-candidate','status':None,'authority_effect':'none',**{k:selection[k] for k in ['lineage_binding','writer_binding','known_overlay_receipt_binding','known_margin_receipt_binding']},'inputs':inputs,'merged_receipt_bindings':[bind(RUN/n) for n in merged_names]}
 # The genuine selection draft stays nonactivating. Its schema deliberately
 # forbids populated inputs until BOTH independent final bindings exist.
 peer={'schema_version':'lab-T00-capture5-inputs-peer/v1-candidate','result':None,'authority_effect':'none','reviewed_root_packet_binding':None,'review_binding':None,'limitations':['Unresolved template only. No Root review, peer PASS, writer execution or runtime qualification is represented.']}
 write('proposed-inputs.json',inputs);write('proposed-root-packet.json',packet);write('proposed-selection.json',selection);write('proposed-peer-wrapper.json',peer);write('T35-public-required-bindings.json',public)
 write('ASSEMBLY.json',{'schema_version':'lab-owned-capture5-input-proposal-assembly/v1','status':'PROPOSAL-only-not-Root-reviewed','input_binding':bind(HERE/'proposed-inputs.json'),'Root_packet_template':bind(HERE/'proposed-root-packet.json'),'selection_draft':bind(HERE/'proposed-selection.json'),'peer_template':bind(HERE/'proposed-peer-wrapper.json'),'future_selection_assignment':{'inputs':'Copy proposed-inputs after Root review; draft presently remains null as required by actual schema.','status':'Root alone selects closed-for-Root-capture after independent review.','final_root_packet_binding':None,'final_peer_review_binding':None},'components':len(components),'helpers':7,'helper_roots':3,'current_API':165,'same_origin_additive_replacements':7,'original24497_replacements':0,'profile_updates':[],'Root_capture_or_native_or_lease_or_shared_mutation':False,'authority_effect':'none','task_complete':False})
 print(json.dumps({'result':'OWNED-PROPOSAL-assembled','components':len(components),'direct_inputs':len(direct),'replacement_rows':len(replacements),'runtime_or_capture_executed':False}))
if __name__=='__main__':main()
