"""Owned inert package/control tests; no Lab constructors or runtime lease."""
import hashlib,importlib.util,json,os,shutil,sys,tempfile,types,uuid
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
MARGIN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T03/observed-margin-adapter-0003/postimages'
I=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def require(value,reason):
 if not value:raise AssertionError(reason)
def check():
 D=load('_T35_margin_loader_driver_'+uuid.uuid4().hex,HERE/'driver.py');cases=[];baseline=len(list(Path('/proc/self/fd').iterdir()))
 fixture=HERE/'owned_fixture_api';require(fixture.is_dir(),'explicit owned public fixture API required')
 def binding(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes())}
 def scenario(mode='diagnostic-measurement',fault=None):
  selected_api=HERE/'owned_fixture_api_failure' if fault=='helper-failure' else fixture
  name='_T35_own_margin_api_'+uuid.uuid4().hex;package=types.ModuleType(name);package.__file__=str(selected_api/'__init__.py');package.__path__=[str(selected_api)];package.__package__=name;sys.modules[name]=package
  tmp=Path(tempfile.mkdtemp(prefix='cal-T03-margin-driver-inert-'));tmp.chmod(0o700)
  rootstat=tmp.stat();ident=[rootstat.st_dev,rootstat.st_ino,rootstat.st_uid,0o700]
  config={field:None for field in ['schema_version','authority_effect','mode','api_directory','api_source_binding','profile_binding','software_binding','period_binding','dependency_selection_binding','dependency_installation','instrumentation_binding','policy_binding','load_binding']}
  config.update(schema_version='lab-protected-observed-margin-runtime/v1-candidate',authority_effect='none',mode=mode,api_directory=str(selected_api.relative_to(ROOT)),dependency_installation='inert-installation')
  for key in ['api_source_binding','profile_binding','software_binding','period_binding','dependency_selection_binding','instrumentation_binding']:config[key]={'path':'inert-config.json','sha256':'1'*64}
  config['api_source_binding']={'path':str((selected_api/'source-manifest.json').relative_to(ROOT)),'sha256':'1'*64};config['profile_binding']['sha256']='2'*64
  raw=json.dumps(config,sort_keys=True).encode();private=tmp/'config.json';private.write_bytes(raw);private.chmod(0o600)
  chosen={'schema_version':'lab-full-learning-private-margin-selection/v1-candidate','authority_effect':'none','mode':mode,'helper_bindings':{leaf:binding(selected_api/(leaf+'.py')) for leaf in D.MARGIN_HELPERS},'composition_binding':binding(MARGIN/'composition.py'),'control':{'root':str(tmp),'identity':ident,'configuration_binding':{'path':'config.json','sha256':sha(raw)}}}
  selection={'api_path':str(selected_api.relative_to(ROOT)),'margin':chosen}
  if fault=='preexisting-module':sys.modules[name+'.margin_kernel']=types.ModuleType(name+'.margin_kernel')
  if fault=='preexisting-attribute':package.margin_kernel=types.ModuleType(name+'.margin_kernel')
  if fault=='wrong-pin':chosen['helper_bindings']['margin_kernel']['sha256']='3'*64
  if fault=='wrong-origin':chosen['helper_bindings']['margin_kernel']=binding(MARGIN/'api/margin_kernel.py')
  if fault=='wrong-root':chosen['control']['identity'][1]+=1
  if fault=='wrong-mode':chosen['mode']='enforce-observed-margin'
  try:return D.prepare_margin(name,selection,'1'*64,'2'*64),name,package,selection,tmp
  except BaseException:
   # Every own registration is absent after failed config/compile; preexisting
   # collision residue is intentionally preserved by the loader.
   for leaf in D.MARGIN_HELPERS:
    if not (fault=='preexisting-module' and leaf=='margin_kernel'):require(name+'.'+leaf not in sys.modules,'own helper registry leaked on refusal')
    if not (fault=='preexisting-attribute' and leaf=='margin_kernel'):require(leaf not in vars(package),'own package attribute leaked on refusal')
   for key in list(sys.modules):
    if key==name or key.startswith(name+'.'):sys.modules.pop(key)
   shutil.rmtree(tmp);raise
 prepared,name,package,selection,tmp=scenario()
 try:
  require(tuple(prepared['modules'])==D.MARGIN_HELPERS and len(prepared['capture'])==4,'dependency order or captures differ')
  for leaf,module,path,pin,raw in prepared['capture']:
   require(path==module.__file__==str(fixture/(leaf+'.py')) and sha(raw)==pin and module.__package__==name,'captured true-origin tuple differs')
   if leaf=='observed_margin':require(module.C is prepared['modules']['margin_capture'] and module.K is prepared['modules']['margin_kernel'] and module.L is prepared['modules']['margin_seal'],'relative helper imports not selected captured modules')
  cases.append('actual four captured helper buffers compiled in selected package/dependency order with exact true origins')
  require(len(D.MARGIN_MODULES)==14 and set(prepared['modules'])<=set(D.MARGIN_MODULES),'14 private module contract differs');cases.append('exact14 private margin module contract retains separate original lifecycle M')
 finally:
  for key in list(sys.modules):
   if key==name or key.startswith(name+'.'):sys.modules.pop(key)
  sys.modules.pop(prepared['composition'].__name__);shutil.rmtree(tmp)
 for fault in ['preexisting-module','preexisting-attribute','wrong-pin','wrong-origin','wrong-root','wrong-mode','helper-failure']:
  try:scenario(fault=fault)
  except (ValueError,OSError):cases.append('private startup '+fault+' refuses without overwriting foreign namespace or own registration leak')
  else:raise AssertionError(fault+' accepted')
 try:scenario(mode='enforce-observed-margin')
 except ValueError:cases.append('explicit enforcement with unknown policy/load refuses before any Lab episode')
 else:raise AssertionError('unknown enforcement accepted')
 try:D.margin_shape({'schema_version':'unresolved'})
 except ValueError:cases.append('unknown/missing private margin selection has no activation fallback')
 else:raise AssertionError('unresolved accepted')
 # Static dataflow: hook composes both children using exact private14 mapping,
 # loaded buffers, external root/config and held tuple, with no API ingress.
 source=(HERE/'driver.py').read_text()
 require(source.index('prepared_margin=prepare_margin(')<source.index('episode=Episode('),'private preparation after episode constructor')
 require('helper.MARGIN_COMPOSITION=self.compose_margin' in source and 'helper_capture=prepared[\'capture\']' in source,'actual lifecycle hook missing')
 require("for key in MARGIN_MODULES" in source and 'control_root=Path(control[\'root\'])' in source,'private module/config dataflow differs')
 cases.append('actual staged lifecycle hook and private capture/control dataflow installed before constructors')
 # Actual selected observer tool/name must equal independently bound record;
 # failure closes only the new observer before any Lab episode executes.
 prepared,name,package,selection,tmp=scenario()
 try:
  spec={'schema_version':'lab-margin-instrumentation-observation/v1-candidate','authority_effect':'none','profile_hook':None,'trace_hook':None,'monitoring_tools':{str(i):sys.monitoring.get_tool(i) for i in range(6)}}
  expected_tool=next(i for i in [5,4] if sys.monitoring.get_tool(i) is None);spec['monitoring_tools'][str(expected_tool)]='cal-full-learning-measurement-v2'
  actual_file=fixture/'instrumentation-owned-valid.json';require(actual_file.read_bytes()==json.dumps(spec,sort_keys=True).encode(),'independently selected own instrumentation record differs')
  prepared['instrumentation_binding']=binding(actual_file)
  args=types.SimpleNamespace(profile_load=False,source_name='OWNED-INERT',source='1'*64,profile='2'*64);events=[];record=types.SimpleNamespace(emit=events.append)
  episode=D.Episode(args,selection,record,name,None,'positive',{},prepared)
  require(episode.observer.tool==expected_tool,'actual observer selected unexpected owned tool');episode.observer.close();cases.append('actual independent instrumentation tool/name/default profile binding matches before episode run')
  prepared['instrumentation_binding']=binding(fixture/'instrumentation-owned-mismatch.json')
  try:D.Episode(args,selection,record,name,None,'positive',{},prepared)
  except ValueError:pass
  else:raise AssertionError('unknown or mismatched actual instrumentation permitted')
  require(sys.monitoring.get_tool(expected_tool) is None,'instrument mismatch leaked observer');cases.append('instrumentation mismatch refuses and disposes observer before any Lab constructor')
 finally:
  for key in list(sys.modules):
   if key==name or key.startswith(name+'.'):sys.modules.pop(key)
  sys.modules.pop(prepared['composition'].__name__);shutil.rmtree(tmp)

 require(baseline==len(list(Path('/proc/self/fd').iterdir())),'private capture FD leak');cases.append('all private input capture descriptors released')
 sys.path.append(str(I/'deps'));from jsonschema import Draft202012Validator
 validator=Draft202012Validator(json.loads((HERE/'selection.schema.json').read_bytes()));require(not validator.is_valid(json.loads((HERE/'UNRESOLVED-INPUT-SELECTION.json').read_bytes())),'unresolved template became runnable')
 cases.append('closed schema rejects null finalfamily/profile/config template')
 return {'result':'PASS-owned-private-loader-controls','checks':cases,'checks_count':len(cases),'FD_delta':0,'actual_Lab_constructor_native_lease_or_original_callback_change':False,'authority_effect':'none','task_complete':False}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
