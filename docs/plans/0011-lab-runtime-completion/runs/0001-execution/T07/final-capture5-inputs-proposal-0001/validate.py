"""Pure proposal validation; does not import/call capture or Lab/runtime code."""
import argparse,ast,hashlib,json,os,stat,sys
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');HERE=Path(__file__).absolute().parent
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
CAP4=RUN/'T07/api17-task-local-capture-0004';CAP5=RUN/'T07/api17-task-local-capture-0005'
INSTALL=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v17'
GENERATED={'source-manifest.json','contract-profile.json','SCHEMA-EXECUTION-DEPENDENCIES.json','INPUT-ACCOUNTING.json'}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def capture(row):
 path=ROOT/row['path'];assert path.is_absolute() and '..' not in path.parts
 held=[os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)]
 try:
  for part in path.parts[1:-1]:held.append(os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=held[-1]))
  held.append(os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=held[-1]));before=os.fstat(held[-1]);assert stat.S_ISREG(before.st_mode)
  chunks=[]
  while block:=os.read(held[-1],1024*1024):chunks.append(block)
  raw=b''.join(chunks);stamp=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
  assert sha(raw)==row['sha256'] and stamp(before)==stamp(os.fstat(held[-1]))
  for i,part in enumerate(path.parts[1:]):
   a=os.stat(part,dir_fd=held[i],follow_symlinks=False);b=os.fstat(held[i+1]);assert (a.st_dev,a.st_ino,a.st_mode,a.st_uid,a.st_gid)==(b.st_dev,b.st_ino,b.st_mode,b.st_uid,b.st_gid)
  return raw,{'path':row['path'],'sha256':row['sha256'],'size_bytes':len(raw),'device':before.st_dev,'inode':before.st_ino,'mode':stat.S_IMODE(before.st_mode)}
 finally:
  for fd in reversed(held):os.close(fd)
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--inputs-sha256',required=True);args=parser.parse_args();assert Path(sys.executable)==INSTALL/'bin/python'
 selected={};entry={};bodies={};checks=[];fdstart=len(os.listdir('/proc/self/fd'))
 def check(name,value):assert value,name;checks.append(name)
 def read(row):
  row={'path':row['path'],'sha256':row['sha256']};name=row['path']
  if name in selected:assert selected[name]==row;return bodies[name]
  raw,record=capture(row);selected[name]=row;entry[name]=record;bodies[name]=raw;return raw
 def load(row):return json.loads(read(row))
 def own(name):
  path=HERE/name;return {'path':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes())}
 provenance=load(own('initial-provenance-selection.json'));inputs=load({'path':str((HERE/'proposed-inputs.json').relative_to(ROOT)),'sha256':args.inputs_sha256})
 sys.path.insert(0,str(INSTALL/'deps'));from jsonschema import Draft202012Validator
 schema=load(provenance['capture5_schema']);input_schema={'$defs':schema['$defs'],'$ref':'#/$defs/inputs'};Draft202012Validator(input_schema).validate(inputs);check('exact actual closed input schema',True)
 draft=load(own('proposed-selection.json'));Draft202012Validator(schema).validate(draft);check('selection remains genuine null nonactivating draft',draft['status']=='draft-refuses-activation' and draft['inputs'] is None and draft['final_root_packet_binding'] is None and draft['final_peer_review_binding'] is None)
 packet=load(own('proposed-root-packet.json'));peer=load(own('proposed-peer-wrapper.json'))
 for name,value,binding in [('Root-status',packet,provenance['Root_packet_schema']),('peer',peer,provenance['Root_peer_schema'])]:
  errors=list(Draft202012Validator(load(binding)).iter_errors(value));check('unresolved template cannot pass activation schema:'+name,bool(errors))
 check('Rootpacket closed inputs exact and Rootstatus unresolved',packet['inputs']==inputs and packet['status'] is None)
 lineage=load(provenance['capture4_lineage']);prior=load(provenance['predecessor_metadata']['source-manifest.json']);profile=load(provenance['predecessor_metadata']['contract-profile.json']);account=load(provenance['predecessor_metadata']['INPUT-ACCOUNTING.json']);old_schema=load(provenance['predecessor_metadata']['SCHEMA-EXECUTION-DEPENDENCIES.json'])
 original_binding={'path':'product/lab/release-candidates/v1/interface/api-integration-v16/source-manifest.json','sha256':'8ac40a51e23b8e528178807792b8ae477aa9c46cd50d92a5b1522c82945413c7'}
 original=load(original_binding);old_original_profile=load({'path':'product/lab/release-candidates/v1/interface/api-integration-v16/contract-profile.json','sha256':'8cc29da16d3881d8816cdc45c55358d9229fcaf226d1b9a757402ebc8675d18c'})
 absent=load({'path':str((RUN/'T07/accounting-0001/unavailable-original-inputs.json').relative_to(ROOT)),'sha256':'4408c5433d41119a92660f86f856d6847be24171ddb1dab368e22c63ee294e7a'})
 unavailable={r['binding']['path'] for r in absent['rows']};originalnames={r['path'] for r in original['files']};oldrows={r['path']:r for r in prior['files']}
 check('full27400/27399/3418/24497/24496/25 retained as exact metadata',tuple(map(len,[prior['files'],profile['files'],old_schema['files'],original['files'],old_original_profile['files'],unavailable]))==(27400,27399,3418,24497,24496,25))
 check('all2928 original addition classifications and reasons retained',len(account['additions'])==2928 and all(set(r)=={'binding','classification','selection_reason'} for r in account['additions']))
 check('all25 REFUSED historical positions retained',lineage['historical_physical_closure']=='REFUSED' and {r['binding']['path'] for r in account['consumption'] if r['status']=='historical-metadata-only'}==unavailable)
 replacements={r['preimage_binding']['path']:r for r in inputs['replacement_bindings']}
 check('seven additive same-origin exact predecessor replacements',len(replacements)==7 and all(r['preimage_binding']['path']==r['postimage_binding']['path'] and oldrows.get(p)==r['preimage_binding'] and p not in originalnames and Path(p).name not in GENERATED and r['preimage_binding']!=r['postimage_binding'] for p,r in replacements.items()))
 static={r['path']:r for r in original['files'] if r['path'] not in unavailable}
 for item in account['additions']:
  row=item['binding'];p=row['path']
  if p.startswith(str(API.relative_to(ROOT))+'/') and Path(p).name in GENERATED:continue
  static[p]=replacements.get(p,{}).get('postimage_binding',row)
 def add(row,verify=True):
  row={'path':row['path'],'sha256':row['sha256']};p=row['path']
  assert p not in unavailable and (p not in static or static[p]==row),'conflicting source declaration:'+p
  assert not(p.startswith(str(API.relative_to(ROOT))+'/') and Path(p).name in GENERATED),'generated input cycle'
  static[p]=row
  if verify:read(row)
 for row in inputs['api_expected_files']+inputs['helper_expected_files']+inputs['direct_inputs']+packet['merged_receipt_bindings']:add(row)
 actual={str(p.relative_to(ROOT)) for p in API.rglob('*') if p.is_file() and '__pycache__' not in p.parts and 'receipts' not in p.parts and p.name not in GENERATED}
 check('all165 API membership exact no ambient hash discovery',actual=={r['path'] for r in inputs['api_expected_files']} and len(actual)==165)
 helpers=[]
 for folder in inputs['helper_roots']:
  root=ROOT/folder;assert not root.is_symlink();helpers.extend(str(p.relative_to(ROOT)) for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
 check('exact7 helper membership in3 disjoint roots',len(helpers)==7 and len(set(helpers))==7 and len(inputs['helper_roots'])==3 and set(helpers)=={r['path'] for r in inputs['helper_expected_files']})
 component_counts=[]
 for component in inputs['component_manifests']:
  manifest=load(component);add(component);check('explicit original component base:'+component['path'],component['base']=='.')
  for row in manifest['files']:add(row)
  component_counts.append({'binding':{k:component[k] for k in ['path','sha256']},'rows':len(manifest['files'])})
 check('new483 closure active, old294 only raw historical metadata',len(component_counts)==19 and any(r['binding']==provenance['margin_closure_manifest'] and r['rows']==483 for r in component_counts) and not any('observed-margin-adapter-0003/source-manifest.json' in r['binding']['path'] for r in component_counts))
 family=inputs['active_family'];descriptor=load(family['descriptor_binding']);add(family['descriptor_binding']);selection=load(family['actual_family_selection_binding']);add(family['actual_family_selection_binding'])
 check('exact nine actual family bindings and descriptor shape',len(family['family_bindings'])==9 and family['family_bindings']==selection['family_bindings'] and family['descriptor_keys']==sorted(descriptor) and all(descriptor[k]==v for k,v in family['family_bindings'].items()))
 for row in family['family_bindings'].values():add(row)
 phases=[]
 for row in family['phase_report_bindings']:
  report=load(row);add(row);phases.append(report['phase']);check('actual completed native phase:'+report['phase'],report['result']=='PASS' and report['error'] is None and report['instance']=='optimized-0005')
 check('five exact selected ordered phase reports',phases==['source','cold','reader','mapped','context'] and family['phase_report_bindings']==selection['phase_reports'])
 acceptance=load(family['pre_source_acceptance_binding']);add(family['pre_source_acceptance_binding'])
 for key in ['construction_binding','preview_binding','independent_review_binding']:add(acceptance[key])
 preview=load(acceptance['preview_binding']);check('actual Source exactly independently reviewed preview',load(family['family_bindings']['source_binding'])==preview['source_manifest_value'])
 baseline=load(next(r for r in inputs['direct_inputs'] if r['path'].endswith('optimized-family-preparation-0005/preparation-baseline.json')));snapshots=[r['snapshot_binding'] for r in baseline['mutable_snapshot_pairs']]
 forbidden={'product/lab/release-candidates/v1/interface/api-integration-v17/'+n for n in ['source-manifest.json','contract-profile.json','SCHEMA-EXECUTION-DEPENDENCIES.json','INPUT-ACCOUNTING.json','source_bridge.py','current_context_sessions.py','authentication.schema.json','machine_auth_scope.py','current_machine_context_scope.py']}
 for key in ['source_binding','reader_binding','mapper_binding','context_source_binding']:
  manifest=load(family['family_bindings'][key]);check('full role retains6snapshots/excludes9:'+key,all(r in manifest['files'] for r in snapshots) and not({r['path'] for r in manifest['files']}&forbidden))
  for row in manifest['files']:add(row)
 check('all349 original mapping retained in native construction',len(load(acceptance['construction_binding'])['optimized_recipe_declaration_mapping'])==349)
 for key in ['previous_runtime_selection_binding','optimized_capture_selection_binding']:add(descriptor[key])
 for row in descriptor['runtime_postimages']:add(row)
 check('five exact true historical template pairs',family['template_preimages']==descriptor['original_template_preimages'] and len(family['template_preimages'])==5)
 for item in family['template_preimages']:add(item['snapshot_binding'])
 software=load(inputs['public_software_manifest_binding']);add(inputs['public_software_manifest_binding'])
 for row in software['files']:add(row)
 public=load(own('T35-public-required-bindings.json'))
 def flatten(value):
  if type(value)is dict:
   if set(value)=={'path','sha256'}:yield value
   else:
    for child in value.values():yield from flatten(child)
  elif type(value)is list:
   for child in value:yield from flatten(child)
 publicrows={r['path']:r for r in flatten(public)}
 for row in publicrows.values():check('preparer public input present in proposed Source:'+row['path'],static.get(row['path'])==row)
 for row in old_schema['files']:
  required=replacements.get(row['path'],{}).get('postimage_binding',row);assert static.get(row['path'])==required,'required original schema input omitted'
 check('all3418 original schema rows conserved with exact declared replacements',True)
 check('all27400 predecessor paths conserved except2 derived outputs awaiting Root',set(oldrows)-{str((API/n).relative_to(ROOT)) for n in ['contract-profile.json','SCHEMA-EXECUTION-DEPENDENCIES.json']}<=set(static))
 check('profile binding-only updates empty; historical fields unchanged',inputs['profile_updates']==[])
 check('margin peer actual PASS included',any(r['sha256']=='1f1f34ce1146b4e497e97eba3f944a9227190f9ef420d3c3312cc7d0c6fa5d43' for r in inputs['direct_inputs']))
 exit_rows={name:capture(row)[1] for name,row in selected.items()};check('full captured public input entry exit identity equal',entry==exit_rows);check('FD delta0',len(os.listdir('/proc/self/fd'))==fdstart)
 report={'schema_version':'lab-capture5-owned-input-proposal-validation/v1','result':'PASS-PROPOSAL-ONLY','checks':checks,'check_count':len(checks),'entry':list(entry.values()),'exit':list(exit_rows.values()),'component_counts':component_counts,'FD_delta':0,'static_source_input_rows_without_future_generated_outputs':len(static),'T35_public_required_unique_inputs':len(publicrows),'private_final_packet_or_config_created':False,'all_original_parent_bodies_freshly_guarded':False,'limits':'Metadata conservation and selected public component/family input byte audit only; actual capture still must freshly reread every original/current required byte and publish metadata under Root control.','Root_review_or_capture_runtime_native_or_lease_executed':False,'authority_effect':'none','task_complete':False}
 with (HERE/'VALIDATION.json').open('x') as f:f.write(json.dumps(report,sort_keys=True,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k not in ['checks','entry','exit','component_counts']}))
if __name__=='__main__':main()
