"""JSON/AST/explicit public metadata controls; never import or execute capture.py."""
import ast,copy,hashlib,json,os
from pathlib import Path
import jsonschema
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/api17-task-local-capture-0004'
checks=[]
def check(name,condition):
    if not condition:raise AssertionError(name)
    checks.append(name)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(path):return json.loads(path.read_bytes())
def held(row):
    path=ROOT/row['path'];check('held:'+row['path'],path.is_file() and not path.is_symlink() and not any(p.is_symlink() for p in path.parents) and sha(path.read_bytes())==row['sha256'])
def dump(node):return ast.dump(node,include_attributes=False)
initial_fds=len(os.listdir('/proc/self/fd'))
old=(HERE/'capture-preimage.py').read_bytes();new=(HERE/'capture.py').read_bytes()
check('capture3 exact writer preimage',sha(old)=='fe7cf43fbd239b88d5b524ff62c3729e96afb5d44cb2fac2c4ba41208e94e665')
oldast=ast.parse(old);tree=ast.parse(new)
functions={node.name:node for node in tree.body if isinstance(node,ast.FunctionDef)}
originals={node.name:node for node in oldast.body if isinstance(node,ast.FunctionDef)}
for name in ['sha','load','logical','bind','closed_family_binding','family_roles']:check('original full helper AST:'+name,dump(functions[name])==dump(originals[name]))
check('stdlib imports only',all(node.module is None or node.module in {'pathlib'} for node in tree.body if isinstance(node,ast.ImportFrom)) and {item.name for node in tree.body if isinstance(node,ast.Import) for item in node.names}<={'ast','argparse','os','copy','hashlib','json','re'})
selection=read(HERE/'component-selection-draft.json');schema=read(HERE/'selection.schema.json')
validator=jsonschema.Draft202012Validator(schema);validator.check_schema(schema);validator.validate(selection)
check('draft closed schema valid',True)
for field in ['inputs','final_root_packet_binding','final_peer_review_binding']:check('unresolved:'+field,selection[field] is None)
activated=copy.deepcopy(selection);activated['status']='closed-for-Root-capture'
check('draft cannot activate under JSON schema',bool(list(validator.iter_errors(activated))))
for field,value in [('extra','open'),('task_complete',True),('authority_effect','admitted')]:
    invalid=copy.deepcopy(selection);invalid[field]=value
    check('closed invalid:'+field,bool(list(validator.iter_errors(invalid))))
for name in ['root-input-packet.schema.json','root-peer-wrapper.schema.json']:
    jsonschema.Draft202012Validator.check_schema(read(HERE/name));check('schema valid:'+name,True)
held(selection['writer_binding']);held(selection['lineage_binding']);held(selection['known_overlay_receipt_binding']);held(selection['known_margin_receipt_binding'])
lineage=read(HERE/'lineage.json')
for item in lineage['capture3_artifacts']:
    held(item['original_binding']);held(item['retained_binding']);check('retained raw capture3 pair:'+item['original_binding']['path'],item['original_binding']['sha256']==item['retained_binding']['sha256'])
for name,item in lineage['predecessor_metadata'].items():
    held(item['original_binding']);held(item['snapshot_binding']);check('predecessor identical:'+name,item['original_binding']['sha256']==item['snapshot_binding']['sha256'])
prior=read(ROOT/lineage['capture3_selection_binding']['path']);overlay=read(ROOT/selection['known_overlay_receipt_binding']['path'])
rows={row['path']:row for row in prior['api_expected_files']};rows.update({row['path']:row for row in overlay['actual_target_bindings']})
check('known165 from independently pinned160 and8overlay',len(rows)==165 and selection['known_api_expected_files']==[rows[path] for path in sorted(rows)])
for row in selection['known_api_expected_files']:held(row)
source=read(HERE/'preimage/source-manifest.json');profile=read(HERE/'preimage/contract-profile.json');inventory=read(HERE/'preimage/INPUT-ACCOUNTING.json');required=read(HERE/'preimage/SCHEMA-EXECUTION-DEPENDENCIES.json')
check('all current row counts retained',len(source['files'])==27400 and len(profile['files'])==27399 and len(required['files'])==3418 and len(inventory['additions'])==2928)
check('accounting exact original closed field set',set(inventory)=={'schema_version','source_sha256','profile_sha256','unavailable_sha256','additions','consumption','authority_effect','claim_ceiling'})
check('historical25 explicit no pruning',len([x for x in inventory['consumption'] if x['status']=='historical-metadata-only'])==25 and lineage['historical_physical_closure']=='REFUSED')
main=functions['main'];activate=functions['activate'];publish=functions['publish'];family=functions['new_family']
main_text=ast.get_source_segment(new.decode(),main);activate_text=ast.get_source_segment(new.decode(),activate);publish_text=ast.get_source_segment(new.decode(),publish);family_text=ast.get_source_segment(new.decode(),family)
check('readiness gates before construction and publication',main_text.index('activate(selection)')<main_text.index('prior_source=')<main_text.index('publish(outputs,lineage,result)'))
check('draft status exact refusal guard',"selection['status']=='closed-for-Root-capture'" in activate_text and 'capture4 draft refuses activation' in activate_text)
check('external Root packet and peer bind same input declaration',"packet[key]==selection[key]" in activate_text and "peer['reviewed_root_packet_binding']==selection['final_root_packet_binding']" in activate_text)
check('full prior additions seed and source path conservation',"for item in prior_inventory['additions']:" in main_text and "set(prior_rows)<=set(row['path'] for row in current)" in main_text)
check('all3418 schema paths conserve',"len(schema_rows)==3418" in main_text and "set(row['path'] for row in schema['files'])<=set(schema_rows)" in main_text)
check('every original nonabsent row fresh checked',"for row in retained:selected(row)" in main_text)
check('full final current reread uncached',"for row in current:" in main_text and "selected(row)" in main_text[main_text.index('for row in current:'):])
check('original hash/period/source guards unchanged',"load(PARENT/'source-manifest.json',SOURCE_SHA)" in main_text and "load(PARENT/'contract-profile.json',PROFILE_SHA)" in main_text and "original_signed_history_schema_callbacks_changed'] is False" in main_text)
check('no expected ambient helper sweep',"actual_helpers.extend(logical(p)" in main_text and "set(actual_helpers)==set(expected_helpers)" in main_text and 'add_file(' not in main_text)
check('nine exact native role paths and five phase reports',"set(bindings)==set(ROLE_TARGETS)" in family_text and "len(family['phase_reports'])==5" in family_text and "phases==['source','cold','reader','mapped','context']" in family_text)
check('old selector bytes only preserved snapshots',"value['template_preimages']" in family_text and "add(snapshot" in family_text and "add(original" not in family_text)
check('corrected stager and driver4 required',"T02/runtime-stager-correction-0001/source-manifest.json" in main_text and "520cd80314fbbd952e0484517af6782f3358e6a804658e6753e59c939b6e6d5b" in main_text)
check('fresh postselector software0002 required',"software-0002.json" in main_text and "preselector software0001 is ineligible" in main_text)
check('original domain metadata preserved with only binding updates',"key.endswith(('_binding','_bindings'))" in main_text and "not key.startswith(('historical_','original_'))" in main_text)
check('generated metadata cycle refuses external additions',"selected output metadata dependency cycle forbidden" in main_text)
check('no overwrite paths and owned temp cleanup',"not (HERE/'capture-result.json').exists()" in publish_text and "open('xb')" in publish_text and "(st.st_dev,st.st_ino)==identity:path.unlink()" in publish_text)
check('source publishes last',"['SCHEMA-EXECUTION-DEPENDENCIES.json','contract-profile.json','INPUT-ACCOUNTING.json','source-manifest.json']" in publish_text)
check('unoptimized assertion contract enforced',"if not __debug__:raise RuntimeError" in main_text)
check('selected JSON duplicate and nonfinite keys refused','duplicate selected JSON key' in new.decode() and 'parse_constant=invalid' in new.decode())
check('no real capture output or metadata temp exists',not (HERE/'capture-result.json').exists() and all(not (ROOT/'product/lab/release-candidates/v1/interface/api-integration-v17'/(name+'.capture-0004-new')).exists() for name in lineage['predecessor_metadata']))
check('FD delta zero',len(os.listdir('/proc/self/fd'))==initial_fds)
result={'schema_version':'lab-T07-capture4-static-controls/v1-candidate','result':'PASS','checks':checks,'check_count':len(checks),'selected_writer':selection['writer_binding'],'selected_draft':{'path':(HERE/'component-selection-draft.json').relative_to(ROOT).as_posix(),'sha256':sha((HERE/'component-selection-draft.json').read_bytes())},'capture_runtime_imported_or_executed':False,'actual_native_constructor_or_lease':False,'shared_write':False,'FD_delta':0,'authority_effect':'none','limitations':['Only JSON schema, exact metadata/public code hashes and AST inspected. No future packet or family exists. No capture, callback changes, native/Lab constructors, lease, private inputs or empirical timing.']}
with (HERE/'STATIC-CHECKS.json').open('x') as handle:handle.write(json.dumps(result,sort_keys=True,indent=2)+'\n')
print(json.dumps(result),flush=True)
