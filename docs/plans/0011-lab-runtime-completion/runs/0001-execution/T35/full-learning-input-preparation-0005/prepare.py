"""Closed Root input preparation after freeze; never import/start Lab runtime."""
import argparse,ast,hashlib,json,os,re,stat,sys
from pathlib import Path
HERE=Path(__file__).absolute().parent
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
API='product/lab/release-candidates/v1/interface/api-integration-v17'
DRIVER='docs/plans/0011-lab-runtime-completion/runs/0001-execution/T35/full-learning-driver-0005'
MODULES=('service','workspace','auth','protocol','guard','session_attachment','current_context_sessions','handlers','lesson_assessment','application_journal','observed_margin','margin_capture','margin_kernel','margin_seal')
HELPERS=('margin_capture','margin_kernel','margin_seal','observed_margin')
ORIGINALS={
 'provider_binding':('product/lab/release-candidates/v1/interface/source8-session-runtime-v1-action-0148/provider.py','44152bf9496a98453be56c0eb7e302ea86b9fc7887c3cbcf5c9a0e69b7c4bf11'),
 'caller_boundary_binding':('docs/plans/0011-lab-runtime-completion/runs/0001-execution/T04/revision-0002/caller_adapter.py','b2b171a48754ffcff9cda8dbac889b06bd0b2e0d32d3c75ad49c4d63aeaab7f8'),
 'application_method_binding':('product/lab/release-candidates/v1/interface/lesson-application-v4-completion-0001/preparation.py','3a318632b5fc06fa15c855cf7f4833df6f4d547a8cedd5f99497fc09b3af0af6'),
 'assessment_method_binding':('product/lab/release-candidates/v1/interface/lesson-assessment-v2-action-0148/preparation.py','8f373dd9b123452cf4a46eece997c7bc7c5d46666583e5f4afa1b070836bd30e')}
FIELDS={'schema_version','authority_effect','status','family_generation','family_instance','source_name','producer_root','runtime_selection_binding','source_pin','source_package_pin','final_source_binding','final_profile_binding','driver_binding','selection_schema_binding','api_bootstrap_bindings','lifecycle_bindings','helper_bindings','composition_binding','provider_binding','caller_boundary_binding','application_method_binding','assessment_method_binding','software_inventory_binding','software_input_selection_binding','postselector_current_context_binding','selector_merge_review_binding','dependency_selection_binding','dependency_installation','instrumentation_binding','expected_monitor_tool','protected_control','selection_output_leaf','selection_output_root_identity','preparer_binding','family_closure_preview_binding','family_closure_acceptance_binding','measurement','measurement_schema_binding'}
def need(value,reason):
 if not value:raise ValueError(reason)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(value):return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def parse(raw):
 def pairs(rows):
  out={}
  for key,value in rows:need(key not in out,'duplicate JSON key');out[key]=value
  return out
 def constant(value):raise ValueError('nonfinite JSON')
 return json.loads(raw,object_pairs_hook=pairs,parse_constant=constant)
def relative(value):
 need(type(value) is str and value and '\\' not in value and '\0' not in value,'canonical relative path required')
 p=Path(value);need(not p.is_absolute() and p.as_posix()==value and '..' not in p.parts and value!='.','canonical relative path required');return value
def closed(value,fields):need(type(value) is dict and set(value)==set(fields),'closed independent input required')
def binding(value):
 closed(value,('path','sha256'));relative(value['path']);need(type(value['sha256']) is str and re.fullmatch('[a-f0-9]{64}',value['sha256']) is not None,'independent exact digest required');return value
def identity(st):return (st.st_dev,st.st_ino,st.st_uid,stat.S_IMODE(st.st_mode))
def stamp(st):return (*identity(st),st.st_nlink,st.st_size,st.st_mtime_ns,st.st_ctime_ns)
def exact(row):
 binding(row);path=ROOT/row['path'];fds=[];links=[]
 try:
  parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC);fds.append(parent)
  for part in path.parts[1:-1]:
   child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent);fds.append(child);links.append((parent,part,child,identity(os.fstat(child))));parent=child
  fd=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=parent);fds.append(fd);before=os.fstat(fd)
  need(stat.S_ISREG(before.st_mode) and before.st_size<=32*1024*1024,'bounded public selected input required');parts=[];count=0
  while block:=os.read(fd,1024*1024):
   count+=len(block);need(count<=before.st_size,'selected input grew');parts.append(block)
  raw=b''.join(parts);need(count==before.st_size and sha(raw)==row['sha256'] and stamp(before)==stamp(os.fstat(fd))==stamp(os.stat(path.name,dir_fd=parent,follow_symlinks=False)),'selected input bytes/attachment differ')
  for parent,name,fd,selected in links:need(identity(os.stat(name,dir_fd=parent,follow_symlinks=False))==identity(os.fstat(fd))==selected,'selected ancestor detached')
  return raw
 finally:
  for fd in reversed(fds):os.close(fd)

def measurement_check(value,expected_tool):
 closed(value,('schema_version','collection_mode','monitoring_reservation','cProfile_enabled','authority_effect'))
 need(value['schema_version']=='lab-full-learning-measurement-selection/v1-candidate' and value['collection_mode']=='phase-only'
  and value['cProfile_enabled'] is False and value['authority_effect']=='none','explicit phase-only/default-unprofiled measurement required')
 reservation=value['monitoring_reservation'];closed(reservation,('tool_id','tool_name'))
 need(type(reservation['tool_id']) is int and reservation['tool_id'] in (4,5) and type(expected_tool) is int
  and reservation['tool_id']==expected_tool and reservation['tool_name']=='cal-full-learning-measurement-v2','independent measurement/instrumentation reservation differs')
 return value

def driver_support_bindings(raw):
 """Expected helper digests come only from independently selected driver bytes."""
 tree=ast.parse(raw);output=[]
 for constant,leaf in [('_CAPTURE_PIN','capture.py'),('_OBSERVE_PIN','observe.py')]:
  values=[node.value for node in tree.body if isinstance(node,ast.Assign) and any(isinstance(target,ast.Name) and target.id==constant for target in node.targets)]
  need(len(values)==1 and isinstance(values[0],ast.Constant) and type(values[0].value) is str and re.fullmatch('[a-f0-9]{64}',values[0].value) is not None,'independent driver helper declaration absent or ambiguous')
  output.append({'path':DRIVER+'/'+leaf,'sha256':values[0].value})
 return output

def build(packet):
 """Return exact output bytes from explicit Root inputs; performs no writes."""
 closed(packet,FIELDS);need(packet['schema_version']=='lab-T35-final-input-packet/v5-candidate' and packet['authority_effect']=='none'
  and packet['status']=='Root-selected-after-family-selector-merge-and-final-capture' and type(packet['family_generation']) is int and packet['family_generation'] in (4,5),'unresolved/final-stage input refused')
 need(type(packet['family_instance']) is str and packet['family_instance'] and type(packet['source_name']) is str and packet['source_name'],'explicit actual family instance/name required')
 measurement=measurement_check(packet['measurement'],packet['expected_monitor_tool'])
 relative(packet['producer_root']);relative(packet['dependency_installation'])
 for key in FIELDS:
  if key.endswith('_binding'):binding(packet[key])
 need(packet['final_source_binding']['path']==API+'/source-manifest.json' and packet['final_profile_binding']['path']==API+'/contract-profile.json','exact final API source/profile origins required')
 source=parse(exact(packet['final_source_binding']));profile=parse(exact(packet['final_profile_binding']));source_rows={(r['path'],r['sha256']) for r in source['files']};profile_rows={(r['path'],r['sha256']) for r in profile['files']}
 exact(packet['family_closure_preview_binding']);exact(packet['family_closure_acceptance_binding'])
 need(profile_rows==source_rows-{(packet['final_profile_binding']['path'],packet['final_profile_binding']['sha256'])} and (packet['final_profile_binding']['path'],packet['final_profile_binding']['sha256']) in source_rows,'final profile/source tables differ')
 runtime=parse(exact(packet['runtime_selection_binding']))
 need(runtime['schema_version']=='lab-current-session-runtime-selection/v1-candidate' and runtime['instance']==packet['family_instance']
  and runtime['public_source_name']==packet['source_name'] and runtime['authority_effect']=='none' and runtime['actual_owner_outcome'] is None and runtime['shared_API_qualified'] is False,'actual selected candidate family differs')
 for key in ['source_binding','source_package_binding','reader_binding','mapper_binding','mapper_package_binding','context_source_binding','context_package_binding','implementation_binding','period_binding']:exact(runtime[key])
 need(runtime['source_binding']['sha256']==packet['source_pin'] and runtime['source_package_binding']['sha256']==packet['source_package_pin']
  and str(Path(runtime['context_source_binding']['path']).parent)==packet['producer_root'],'independent source/package/producer differs')
 for key,(path,pin) in ORIGINALS.items():need(packet[key]=={'path':path,'sha256':pin},'original provider/caller/method changed');exact(packet[key])
 need(packet['driver_binding']['path']==DRIVER+'/driver.py' and packet['selection_schema_binding']['path']==DRIVER+'/selection.schema.json','exact reviewed true driver5 origins required');driver_raw=exact(packet['driver_binding']);schema=parse(exact(packet['selection_schema_binding']))
 support=driver_support_bindings(driver_raw)
 for row in support:exact(row)
 need(packet['measurement_schema_binding']['path']==DRIVER+'/measurement-selection.schema.json','true independently pinned measurement schema required');measurement_schema=parse(exact(packet['measurement_schema_binding']))
 need(packet['preparer_binding']['path']==str(Path(__file__).relative_to(ROOT)),'true reviewed preparation origin required');exact(packet['preparer_binding'])
 closed(packet['lifecycle_bindings'],('positive','security'))
 for lane in ('positive','security'):need(packet['lifecycle_bindings'][lane]['path']==DRIVER+'/'+lane+'_lifecycle.py','true driver5 lifecycle origin required');exact(packet['lifecycle_bindings'][lane])
 closed(packet['helper_bindings'],HELPERS)
 for leaf in HELPERS:need(packet['helper_bindings'][leaf]['path']==API+'/'+leaf+'.py','true helper API origin required');exact(packet['helper_bindings'][leaf])
 need(packet['composition_binding']['path']=='docs/plans/0011-lab-runtime-completion/runs/0001-execution/T03/observed-margin-adapter-0003/postimages/composition.py','reviewed true margin3 composition required');exact(packet['composition_binding'])
 need(type(packet['api_bootstrap_bindings']) is list and len(packet['api_bootstrap_bindings'])==2 and {r['path'] for r in packet['api_bootstrap_bindings']}=={API+'/__init__.py',API+'/guard.py'},'closed exact original API bootstrap required')
 for row in packet['api_bootstrap_bindings']:exact(row)
 # Require the final inventory from the reviewed actual selector merge, not
 # merely a preselector status string or old software inventory digest.
 inventory=parse(exact(packet['software_inventory_binding']));inventory_inputs=parse(exact(packet['software_input_selection_binding']))
 need(inventory_inputs['schema_version']=='lab-T03-margin-software-inputs/v1-candidate' and inventory_inputs['authority_effect']=='none' and inventory_inputs['status']=='Root-selected-reviewed-software'
  and inventory_inputs['api_directory']==API,'closed reviewed final software inputs required')
 closed(inventory_inputs['module_bindings'],MODULES)
 need(inventory_inputs['merge_review_binding']==packet['selector_merge_review_binding'] and inventory_inputs['module_bindings']['current_context_sessions']==packet['postselector_current_context_binding'],'inventory lacks exact final selector merge correspondence')
 exact(packet['selector_merge_review_binding']);need(packet['postselector_current_context_binding']['path']==API+'/current_context_sessions.py','actual merged selector origin required');exact(packet['postselector_current_context_binding'])
 expected=[]
 for name in MODULES:
  row=inventory_inputs['module_bindings'][name];need(row['path']==API+'/'+name+'.py','inventory module origin differs');exact(row);expected.append(row)
 for key,path in [('policy_schema_binding',API+'/observed-margin-policy.schema.json'),('assessment_method_binding',ORIGINALS['assessment_method_binding'][0])]:
  row=inventory_inputs[key];need(row['path']==path,'inventory schema/method origin differs');exact(row);expected.append(row)
 need(inventory['schema_version']=='lab-T03-observed-margin-software/v1-candidate' and inventory['authority_effect']=='none'
  and sorted(inventory['files'],key=lambda row:row['path'])==sorted(expected,key=lambda row:row['path']),'exact final16 software inventory required')
 # Instrumentation is supplied as an independent observation. No ambient
 # monitor query, free-tool assumption, profile callback or clock patch.
 instrument=parse(exact(packet['instrumentation_binding']));closed(instrument,('schema_version','authority_effect','profile_hook','trace_hook','monitoring_tools'))
 tool=packet['expected_monitor_tool'];need(type(tool) is int and tool in (4,5),'explicit actual reserved monitor observation required')
 need(instrument['schema_version']=='lab-margin-instrumentation-observation/v1-candidate' and instrument['authority_effect']=='none'
  and instrument['profile_hook'] is None and instrument['trace_hook'] is None and type(instrument['monitoring_tools']) is dict and set(instrument['monitoring_tools'])=={str(i) for i in range(6)}
  and instrument['monitoring_tools'][str(tool)]=='cal-full-learning-measurement-v2','instrumentation observation/name/default profiling differs')
 dep=parse(exact(packet['dependency_selection_binding']));need(dep['schema_version']=='lab-runtime-dependency-closure/v2-candidate','exact original dependency closure required')
 need(Path(sys.executable)==ROOT/packet['dependency_installation']/'bin/python','selected dependency interpreter required')
 public=[packet[k] for k in ORIGINALS]+[packet[k] for k in ['driver_binding','selection_schema_binding','composition_binding','software_inventory_binding','instrumentation_binding','postselector_current_context_binding','runtime_selection_binding','software_input_selection_binding','selector_merge_review_binding','dependency_selection_binding','preparer_binding','family_closure_preview_binding','family_closure_acceptance_binding','measurement_schema_binding']]+packet['api_bootstrap_bindings']+list(packet['helper_bindings'].values())+list(packet['lifecycle_bindings'].values())+expected+support
 for row in public:need((row['path'],row['sha256']) in source_rows,'selected software/input absent from final source')
 # Final config is created after freeze and lives outside source rows.
 control=packet['protected_control'];closed(control,('root','identity','configuration_leaf'))
 need(type(control['root']) is str and re.fullmatch('/tmp/cal-T03-margin-[a-zA-Z0-9_-]+',control['root']) is not None,'explicit fresh protected root required')
 need(type(control['identity']) is list and len(control['identity'])==4 and all(type(v) is int for v in control['identity']) and control['identity'][2:]==[os.getuid(),0o700],'independent owned protected root custody required')
 need(type(control['configuration_leaf']) is str and re.fullmatch('config-[0-9]{4}\\.json',control['configuration_leaf']) is not None,'exclusive private config leaf required')
 need(type(packet['selection_output_root_identity']) is list and len(packet['selection_output_root_identity'])==4 and all(type(v) is int for v in packet['selection_output_root_identity']) and packet['selection_output_root_identity'][2:]==[os.getuid(),0o700],'explicit owned selection output root identity required')
 leaf=packet['selection_output_leaf'];need(type(leaf) is str and re.fullmatch('selection-[0-9]{4}\\.json',leaf) is not None,'exclusive own selection output required')
 need(str((HERE/leaf).relative_to(ROOT)) not in {r[0] for r in source_rows},'postfreeze selection output in source table creates cycle')
 config={'schema_version':'lab-protected-observed-margin-runtime/v1-candidate','authority_effect':'none','mode':'diagnostic-measurement','api_directory':API,
  'api_source_binding':packet['final_source_binding'],'profile_binding':packet['final_profile_binding'],'software_binding':packet['software_inventory_binding'],'period_binding':runtime['period_binding'],
  'dependency_selection_binding':packet['dependency_selection_binding'],'dependency_installation':packet['dependency_installation'],'instrumentation_binding':packet['instrumentation_binding'],'policy_binding':None,'load_binding':None}
 config_raw=encoded(config);private_control={'root':control['root'],'identity':control['identity'],'configuration_binding':{'path':control['configuration_leaf'],'sha256':sha(config_raw)}}
 selection={'schema_version':'lab-full-learning-input-selection/v3-candidate','authority_effect':'none','api_path':API,'source_name':runtime['public_source_name'],
  'factory_module':'source_bridge','factory_name':'current_session_fixture_delivery','producer_root':packet['producer_root'],'source_pin':packet['source_pin'],'source_package_pin':packet['source_package_pin'],
  'runtime_selection_binding':packet['runtime_selection_binding'],'period_binding':runtime['period_binding'],'provider_binding':packet['provider_binding'],'caller_boundary_binding':packet['caller_boundary_binding'],
  'api_bootstrap_bindings':packet['api_bootstrap_bindings'],'application_method_binding':packet['application_method_binding'],'assessment_method_binding':packet['assessment_method_binding'],'lifecycle_bindings':packet['lifecycle_bindings'],'measurement':measurement,
  'margin':{'schema_version':'lab-full-learning-private-margin-selection/v1-candidate','authority_effect':'none','mode':'diagnostic-measurement','helper_bindings':packet['helper_bindings'],'composition_binding':packet['composition_binding'],'control':private_control}}
 sys.path.append(str(ROOT/packet['dependency_installation']/'deps'))
 from jsonschema import Draft202012Validator
 Draft202012Validator(measurement_schema).validate(measurement)
 Draft202012Validator(schema).validate(selection)
 return config_raw,encoded(selection)

def write_exclusive(root,selected,leaf,raw):
 """Descriptor anchored new file only; no existing/private body overwrite."""
 need(type(leaf) is str and re.fullmatch('[a-zA-Z0-9][a-zA-Z0-9._-]*',leaf) is not None and type(raw) is bytes,'flat bounded own output required')
 root=Path(root);need(root.is_absolute() and '..' not in root.parts and root.as_posix()==str(root),'canonical output root required');fds=[];links=[];output=None
 try:
  parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC);fds.append(parent)
  for part in root.parts[1:]:
   child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent);fds.append(child);links.append((parent,part,child,identity(os.fstat(child))));parent=child
  need(identity(os.fstat(parent))==tuple(selected) and selected[2:]==[os.getuid(),0o700],'actual owned output root differs')
  for anchor,name,held,expected in links:need(identity(os.stat(name,dir_fd=anchor,follow_symlinks=False))==identity(os.fstat(held))==expected,'output root detached')
  output=os.open(leaf,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=parent);before=identity(os.fstat(output));offset=0
  while offset<len(raw):offset+=os.write(output,raw[offset:])
  os.fsync(output);need(identity(os.stat(leaf,dir_fd=parent,follow_symlinks=False))==identity(os.fstat(output))==before,'new output detached')
  for anchor,name,held,expected in links:need(identity(os.stat(name,dir_fd=anchor,follow_symlinks=False))==identity(os.fstat(held))==expected,'output root detached after write')
  os.fsync(parent)
 finally:
  if output is not None:os.close(output)
  for fd in reversed(fds):os.close(fd)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--packet',required=True);parser.add_argument('--packet-sha256',required=True);args=parser.parse_args()
 packet_binding={'path':args.packet,'sha256':args.packet_sha256};packet=parse(exact(packet_binding));config,selection=build(packet)
 # Re-read every input at commit boundary through build; no trusted body cache.
 need(build(parse(exact(packet_binding)))==(config,selection),'independent packet/input changed before output')
 control=packet['protected_control'];write_exclusive(control['root'],control['identity'],control['configuration_leaf'],config)
 # A later failure preserves the uncertain original config; no automatic retry.
 write_exclusive(HERE,packet['selection_output_root_identity'],packet['selection_output_leaf'],selection)
 print(json.dumps({'result':'PREPARED-Root-diagnostic-inputs-only','selection_binding':{'path':str((HERE/packet['selection_output_leaf']).relative_to(ROOT)),'sha256':sha(selection)},
  'private_configuration_binding':{'path':control['configuration_leaf'],'sha256':sha(config)},'runtime_started':False,'empirical_margin_qualified':False,'task_complete':False,'authority_effect':'none'}))
if __name__=='__main__':main()
