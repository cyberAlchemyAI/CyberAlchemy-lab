"""Pure expected-input/value/custody controls, never a Lab runtime constructor."""
import hashlib,importlib.util,json,os,shutil,sys,tempfile,types,uuid
from pathlib import Path
HERE=Path(__file__).absolute().parent;ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');I=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
sys.path.append(str(I/'deps'))
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(v):return (json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def load(path):
 n='_T35_own_input_writer_'+uuid.uuid4().hex;s=importlib.util.spec_from_file_location(n,path);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def check():
 real=load(HERE/'prepare.py');cases=[]
 from jsonschema import Draft202012Validator
 schema=json.loads((HERE/'expected-input-packet.schema.json').read_bytes());Draft202012Validator.check_schema(schema)
 assert not Draft202012Validator(schema).is_valid(json.loads((HERE/'UNRESOLVED-EXPECTED-INPUT-PACKET.json').read_bytes()));cases.append('closed36field independent packet rejects unresolved family5/final capture template')
 start=len(list(Path('/proc/self/fd').iterdir()))
 def refuses(label,fn):
  try:fn()
  except (ValueError,OSError):cases.append(label)
  else:raise AssertionError(label+' accepted')
 refuses('closed unresolved packet refuses before input/public/private output',lambda:real.build({}))
 fixture=Path(tempfile.mkdtemp(prefix='cal-T35-input-packet-inert-'));fixture.chmod(0o700)
 try:
  # Explicit three-locator test adapter: root locator, selected interpreter,
  # dependency imports. All other producer logic/body is exact. True fixture
  # filename and declared delta; no monkeypatch/original callback alias.
  original=(HERE/'prepare.py').read_text();adapted=original.replace("ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')",'ROOT=Path('+repr(str(fixture))+')')
  adapted=adapted.replace("Path(sys.executable)==ROOT/packet['dependency_installation']/'bin/python'","Path(sys.executable)==Path("+repr(str(I/'bin/python'))+")")
  adapted=adapted.replace("str(ROOT/packet['dependency_installation']/'deps')",repr(str(I/'deps')))
  clone=fixture/'prepare-fixture.py';clone.write_text(adapted);F=load(clone)
  def write(name,raw):
   p=fixture/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);return {'path':name,'sha256':sha(raw)}
  def body(name,v):return write(name,encoded(v))
  packets={};packet={key:None for key in F.FIELDS};packet.update(schema_version='lab-T35-final-input-packet/v4-candidate',authority_effect='none',status='Root-selected-after-family-selector-merge-and-final-capture',family_generation=4,family_instance='OWNED-INERT-INSTANCE',source_name='OWNED-INERT-NOT-SOURCE',producer_root='owned-context',source_pin=None,source_package_pin=None,dependency_installation='owned-inert-dependency-locator',expected_monitor_tool=5,selection_output_leaf='selection-0001.json',selection_output_root_identity=[fixture.stat().st_dev,fixture.stat().st_ino,os.getuid(),0o700],protected_control={'root':'/tmp/cal-T03-margin-owned-inert-unused','identity':[1,1,os.getuid(),0o700],'configuration_leaf':'config-0001.json'})
  for key,(path,pin) in F.ORIGINALS.items():packet[key]=write(path,(ROOT/path).read_bytes());assert packet[key]['sha256']==pin
  packet['preparer_binding']={'path':'prepare-fixture.py','sha256':sha(clone.read_bytes())}
  driver=ROOT/F.DRIVER
  packet['driver_binding']=write(F.DRIVER+'/driver.py',(driver/'driver.py').read_bytes());packet['selection_schema_binding']=write(F.DRIVER+'/selection.schema.json',(driver/'selection.schema.json').read_bytes())
  packet['lifecycle_bindings']={lane:write(F.DRIVER+'/'+lane+'_lifecycle.py',(driver/(lane+'_lifecycle.py')).read_bytes()) for lane in ['positive','security']}
  api=F.API;module_rows={n:write(api+'/'+n+'.py',b'# OWNED INERT PUBLIC MODULE DATA; NEVER IMPORTED\n'+n.encode()) for n in F.MODULES}
  packet['helper_bindings']={leaf:module_rows[leaf] for leaf in F.HELPERS};packet['postselector_current_context_binding']=module_rows['current_context_sessions']
  packet['composition_binding']=write('docs/plans/0011-lab-runtime-completion/runs/0001-execution/T03/observed-margin-adapter-0003/postimages/composition.py',b'# OWNED INERT COMPOSITION DATA; NEVER EXECUTED\n')
  packet['api_bootstrap_bindings']=[write(api+'/__init__.py',b'# OWNED INERT BOOTSTRAP DATA\n'),module_rows['guard']]
  selection_runtime={'schema_version':'lab-current-session-runtime-selection/v1-candidate','instance':packet['family_instance'],'public_source_name':packet['source_name'],'authority_effect':'none','actual_owner_outcome':None,'shared_API_qualified':False}
  for key in ['source_binding','source_package_binding','reader_binding','mapper_binding','mapper_package_binding','context_source_binding','context_package_binding','implementation_binding','period_binding']:
   selection_runtime[key]=body(('owned-context/' if key=='context_source_binding' else 'owned-family/')+key+'.json',{'fixture':'OWNED INERT METADATA, NO SIGNATURE/RAM/REAL SOURCE'})
  packet['runtime_selection_binding']=body('owned-family/runtime.json',selection_runtime);packet['source_pin']=selection_runtime['source_binding']['sha256'];packet['source_package_pin']=selection_runtime['source_package_binding']['sha256']
  packet['family_closure_preview_binding']=body('owned-closure-preview.json',{'fixture':'OWNED INERT, NO NATIVE CLOSURE RESULT'})
  packet['family_closure_acceptance_binding']=body('owned-closure-peer.json',{'fixture':'OWNED INERT METADATA, NO APPROVAL'})
  packet['selector_merge_review_binding']=body('owned-selector-review.json',{'fixture':'OWNED INERT CORRESPONDENCE ONLY, NO APPROVAL'})
  inventory_inputs={'schema_version':'lab-T03-margin-software-inputs/v1-candidate','authority_effect':'none','status':'Root-selected-reviewed-software','api_directory':api,'module_bindings':module_rows,'policy_schema_binding':body(api+'/observed-margin-policy.schema.json',{'fixture':'inert schema data'}),'assessment_method_binding':packet['assessment_method_binding'],'merge_review_binding':packet['selector_merge_review_binding']}
  packet['software_input_selection_binding']=body('owned-inventory-inputs.json',inventory_inputs)
  packet['software_inventory_binding']=body('owned-inventory.json',{'schema_version':'lab-T03-observed-margin-software/v1-candidate','authority_effect':'none','files':list(module_rows.values())+[inventory_inputs['policy_schema_binding'],inventory_inputs['assessment_method_binding']]})
  packet['dependency_selection_binding']=body('owned-dependency.json',{'schema_version':'lab-runtime-dependency-closure/v2-candidate'})
  instrument={'schema_version':'lab-margin-instrumentation-observation/v1-candidate','authority_effect':'none','profile_hook':None,'trace_hook':None,'monitoring_tools':{str(i):None for i in range(6)}};instrument['monitoring_tools']['5']='cal-full-learning-measurement-v2';packet['instrumentation_binding']=body('owned-instrument.json',instrument)
  # Final tables mirror only these own constructed public records. Nothing is
  # a native signed family, real cut, actual role/nonce or current source proof.
  all_rows=[{'path':str(p.relative_to(fixture)),'sha256':sha(p.read_bytes())} for p in fixture.rglob('*') if p.is_file()]
  profile=body(api+'/contract-profile.json',{'schema_version':'lab-operator-contract-profile/v4-candidate','files':all_rows});packet['final_profile_binding']=profile
  packet['final_source_binding']=body(api+'/source-manifest.json',{'files':all_rows+[profile],'authority_effect':'none'})
  cfg,selected=F.build(packet);configuration=json.loads(cfg);selection=json.loads(selected)
  assert configuration['mode']=='diagnostic-measurement' and configuration['policy_binding'] is None and configuration['load_binding'] is None
  assert selection['margin']['control']['configuration_binding']['sha256']==sha(cfg) and selection['caller_boundary_binding']==packet['caller_boundary_binding']
  assert selection['period_binding']==selection_runtime['period_binding'] and selection['source_pin']==packet['source_pin'];cases.append('complete driver4 diagnostic values preserve original fields and independent final correspondence')
  assert F.build({**packet,'family_generation':5})==(cfg,selected);cases.append('prospective family5 explicit Root packet allowed without ambient instance or epoch inference')
  assert len(configuration)==13 and len(selection)==18;cases.append('closed original margin config13 and full driver4 selection18 no implicit empirical fields')
  for key,value in [('family_generation',3),('family_instance','OWNED DIFFERENT'),('source_name','OWNED DIFFERENT'),('source_pin','1'*64),('producer_root','different-root'),('expected_monitor_tool',4)]:
   refuses('independent final input mismatch '+key,lambda key=key,value=value:F.build({**packet,key:value}))
  refuses('preselector current context digest refuses despite status',lambda:F.build({**packet,'postselector_current_context_binding':{**packet['postselector_current_context_binding'],'sha256':'1'*64}}))
  refuses('wrong selector review correspondence refuses',lambda:F.build({**packet,'selector_merge_review_binding':packet['instrumentation_binding']}))
  refuses('original caller selector cannot silently change',lambda:F.build({**packet,'caller_boundary_binding':packet['provider_binding']}))
  refuses('source/self output cycle locator refuses',lambda:F.build({**packet,'selection_output_leaf':'prepare-fixture.py'}))
  refuses('extra actor/input policy field refuses',lambda:F.build({**packet,'actor':{}}))
  refuses('null final source/profile refuses',lambda:F.build({**packet,'final_source_binding':None}))
  # Exact public read/closed bytes and solely owned output custody controls.
  original=packet['instrumentation_binding'];refuses('wrong independent input SHA refuses',lambda:F.exact({**original,'sha256':'0'*64}))
  target=fixture/'private-owned';target.mkdir(mode=0o700);st=target.stat();ident=[st.st_dev,st.st_ino,os.getuid(),0o700]
  F.write_exclusive(target,ident,'config-0001.json',b'{"OWNED_INERT":true}\n');assert (target/'config-0001.json').stat().st_mode&0o777==0o600;cases.append('descriptor-held own fresh output exact600 with fsync')
  refuses('existing output preserved no replace',lambda:F.write_exclusive(target,ident,'config-0001.json',b'FOREIGN'))
  refuses('wrong owned output identity before writes',lambda:F.write_exclusive(target,[ident[0],ident[1]+1,*ident[2:]],'config-0002.json',b'INERT'))
  refuses('arbitrary output child path refused',lambda:F.write_exclusive(target,ident,'../foreign.json',b'INERT'))
  assert not (target/'config-0002.json').exists() and (target/'config-0001.json').read_bytes()==b'{"OWNED_INERT":true}\n';cases.append('no unselected output body overwritten')
 finally:shutil.rmtree(fixture)
 assert start==len(list(Path('/proc/self/fd').iterdir()));cases.append('all owned input and output descriptors closed')
 return {'result':'PASS-pure-input-preparation-component','checks':cases,'checks_count':len(cases),'fixture_locator_adaptations':3,'fixture_not_real_Source_native_signature_RAM_lease_or_approval':True,'actual_packet_or_private_runtime_config_created':False,'actual_Lab_runtime_or_guard_executed':False,'FD_delta':0,'task_complete':False,'authority_effect':'none'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
