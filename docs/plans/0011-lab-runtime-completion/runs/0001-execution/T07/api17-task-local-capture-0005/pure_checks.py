"""Own JSON/AST/public metadata checks only; never import or execute writer."""
import ast,hashlib,json,os
from pathlib import Path
import jsonschema
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution';HERE=RUN/'T07/api17-task-local-capture-0005';CAPTURE4=RUN/'T07/api17-task-local-capture-0004'
checks=[]
def check(name,value):
    if not value:raise AssertionError(name)
    checks.append(name)
def read(path):return json.loads(path.read_bytes())
def sha(raw):return hashlib.sha256(raw).hexdigest()
def binding(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path.read_bytes())}
def held(row):
    path=ROOT/row['path'];check('exact:'+row['path'],path.is_file() and not path.is_symlink() and not any(p.is_symlink() for p in path.parents) and sha(path.read_bytes())==row['sha256'])
fd_before=len(os.listdir('/proc/self/fd'))
old=(CAPTURE4/'capture.py').read_text();new=(HERE/'capture_v5.py').read_text()
oldfuncs={n.name:n for n in ast.parse(old).body if isinstance(n,ast.FunctionDef)};funcs={n.name:n for n in ast.parse(new).body if isinstance(n,ast.FunctionDef)}
for name in ['sha','load','logical','bind','closed_family_binding','family_roles','need','selected','repo_binding','read_selected','unique_rows','encoded','derived']:
    check('original helper AST:'+name,ast.dump(oldfuncs[name],include_attributes=False)==ast.dump(funcs[name],include_attributes=False))
selection=read(HERE/'component-selection-draft.json')
for name in ['selection.schema.json','root-input-packet.schema.json','root-peer-wrapper.schema.json']:
    schema=read(HERE/name);jsonschema.Draft202012Validator.check_schema(schema);check('closed schema valid:'+name,True)
validator=jsonschema.Draft202012Validator(read(HERE/'selection.schema.json'));validator.validate(selection)
check('draft inactive closed null fields',selection['status']=='draft-refuses-activation' and all(selection[k] is None for k in ['inputs','final_root_packet_binding','final_peer_review_binding']))
closed=dict(selection);closed['status']='closed-for-Root-capture';check('null inputs reject activation schema',bool(list(validator.iter_errors(closed))))
held(selection['writer_binding']);held(selection['lineage_binding'])
required=read(HERE/'required-components.json')['bindings']
for row in required.values():held(row)
check('parent capture4 exact inactive FLAG retained',read(ROOT/required['parent_capture4_review']['path'])['result']=='FLAG-current-family4-mutable-input-cycle')
check('new writer true filename',selection['writer_binding']['path']==(HERE/'capture_v5.py').relative_to(ROOT).as_posix() and "HERE/'capture_v5.py'" in new and not (HERE/'capture.py').exists())
check('no historical tree copy',not (HERE/'preimage').exists() and not (HERE/'lineage-preimages').exists())
lineage=read(ROOT/selection['lineage_binding']['path']);check('all25 original artifacts retained by exact references',len(lineage['capture3_artifacts'])==25)
for pair in lineage['capture3_artifacts']:
    held(pair['original_binding']);held(pair['retained_binding']);check('exact25-pair:'+pair['original_binding']['path'],pair['original_binding']['sha256']==pair['retained_binding']['sha256'])
for pair in lineage['predecessor_metadata'].values():held(pair['original_binding']);held(pair['snapshot_binding'])
source=read(CAPTURE4/'preimage/source-manifest.json');profile=read(CAPTURE4/'preimage/contract-profile.json');schema=read(CAPTURE4/'preimage/SCHEMA-EXECUTION-DEPENDENCIES.json');inventory=read(CAPTURE4/'preimage/INPUT-ACCOUNTING.json')
check('27400/27399/3418/2928 exact lineage counts',len(source['files'])==27400 and len(profile['files'])==27399 and len(schema['files'])==3418 and len(inventory['additions'])==2928)
check('25 unavailable dispositions retained',sum(x['status']=='historical-metadata-only' for x in inventory['consumption'])==25 and lineage['historical_physical_closure']=='REFUSED')
parent=read(ROOT/'product/lab/release-candidates/v1/interface/api-integration-v16/source-manifest.json');missing={x['binding']['path'] for x in inventory['consumption'] if x['status']=='historical-metadata-only'};retained=[r for r in parent['files'] if r['path'] not in missing];added=[x['binding'] for x in inventory['additions']]
check('all original row/order and current additions conserved',len(parent['files'])==24497 and len(retained)==24472 and source['files']==retained+added and [x['binding'] for x in inventory['consumption']]==parent['files']+added)
by_path={r['path']:r for r in source['files']};check('all3418 schema and27399 profile rows remain in source',all(by_path.get(r['path'])==r for r in schema['files']+profile['files']))
old_selection=read(CAPTURE4/'component-selection-draft.json');check('all165 externally selected API expectations unchanged',selection['known_api_expected_files']==old_selection['known_api_expected_files'])
baseline=read(ROOT/required['recipe5_baseline']['path']);stager=(ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T02/optimized-family-preparation-0005/stage_runtime_optimized_v5.py').read_text()
check('descriptor emits all5 original identities and snapshot pairs',"descriptor['original_template_preimages']" in stager and len(baseline['runtime_template_snapshot_pairs'])==5)
for pair in baseline['mutable_snapshot_pairs']:held(pair['snapshot_binding'])
check('family5 exact new origin and original9 roles',"T02/optimized-family-preparation-0005/instances/optimized-0005" in new and "set(bindings)==set(ROLE_TARGETS)" in new and "lab-T02-v5-actual-family-inputs/v1-candidate" in new)
check('closed final packet requires family5 readiness',"Root-reviewed-merged-native-family5-ready-for-capture" in new and 'native-family4-ready' not in new)
check('native roles reject9 live and require6 snapshots',"not {logical(row['path']) for row in manifest['files']}&FORBIDDEN_NATIVE_API_INPUTS" in new and "all(row in manifest['files'] for row in snapshots)" in new)
check('349 exact mapping and6 snapshots conserved before roles',"construction['optimized_recipe_declaration_mapping']==baseline['declaration_mapping']" in new and "construction['mutable_API_preparation_snapshot_pairs']==baseline['mutable_snapshot_pairs']" in new)
check('actual Source agrees pre-source reviewed preview',"manifest==preview['source_manifest_value']" in new and "review['preview_binding']==accepted['preview_binding']" in new and "lab-T00-family5-pre-source-closure-acceptance/v1-candidate" in new)
check('all5 emitted descriptor pairs equal baseline originals',"value['template_preimages']==runtime['original_template_preimages']==expected_pairs" in new and "runtime['original_templates']" in new)
check('all current schema/hash/disposition safeguards remain',"len(schema_rows)==3418" in new and "for row in retained:selected(row)" in new and "for row in current:" in new and "original_signed_history_schema_callbacks_changed'] is False" in new and '65ba71adb3b885f6fedc268be29f982f1f03139265f00a7e9ed08ff19b6adeb3' in new)
check('all source/profile scalar provenance preserved',"profile=copy.deepcopy(prior_profile)" in new and "not key.startswith(('historical_','original_'))" in new and "manifest=copy.deepcopy(prior_source)" in new)
check('T35 required manifests and code/record/peer exact',all(required[k]['sha256'] in new for k in ['input_preparer4_manifest','input_preparer4_peer','instrumentation_manifest','instrumentation_actual','instrumentation_peer']))
check('driver4 and software0002 retained exact',"520cd80314fbbd952e0484517af6782f3358e6a804658e6753e59c939b6e6d5b" in new and "48f731601527ce05cf6a771a3c49ab2cbf0e2103adddff992f91ff90c253bf25" in new and "software-0002.json" in new)
check('external acceptance/preview never inserted into native role files','These external coordinator proofs enter only final API capture, never native role files.' in new)
check('publication only new temporary filename and fresh full guard',".capture-0005-new" in new and '.capture-0004-new' not in new and 'selected output metadata dependency cycle forbidden' in new)
check('no new writer import/runtime/capture/outputs',not (HERE/'capture-result.json').exists() and all(not (ROOT/'product/lab/release-candidates/v1/interface/api-integration-v17'/(n+'.capture-0005-new')).exists() for n in lineage['predecessor_metadata']))
check('FD delta zero',len(os.listdir('/proc/self/fd'))==fd_before)
result={'schema_version':'lab-T07-capture5-pure-static-controls/v1-candidate','result':'PASS','check_count':len(checks),'checks':checks,'writer_binding':selection['writer_binding'],'draft_binding':binding(HERE/'component-selection-draft.json'),'FD_delta':0,'writer_imported_or_executed':False,'native_or_Lab_constructor_or_lease_or_callback_change':False,'shared_write':False,'actual_family5_preview_review_or_root_packet_ready':False,'authority_effect':'none','limits':['Metadata/schema/AST plus exact preserved public artifact hashes only. No capture/writer import or Native/Source construction. Root actual Source preview acceptance and final family/selector/software0002/packet/peer remain pending. No original fields pruned; no empirical or whole-API/Session qualification.']}
with (HERE/'STATIC-CHECKS.json').open('x') as f:f.write(json.dumps(result,sort_keys=True,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='checks'}),flush=True)
