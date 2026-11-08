"""Private diagnostic configuration from independently installed bindings."""
import hashlib,importlib,importlib.util,json,os,stat,sys,tempfile,uuid
from pathlib import Path

def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(value):return(json.dumps(value,indent=2,sort_keys=True)+'\n').encode()
def need(value,message):
 if not value:raise ValueError(message)
def prepare(runtime):
 provider=runtime.provider;root=runtime.root;api=runtime.api
 provider.require_runtime_ready();provider.guard()
 package=provider.current().package;rows={row['path']:row for row in package['members']}
 def stable(name):
  row=rows.get(name);need(row is not None,'margin input absent from selected public package: '+name)
  need(sha((root/name).read_bytes())==row['sha256'],'selected public margin bytes differ')
  return {'path':name,'sha256':row['sha256']}
 prefix='implementation/lab-runtime/local-host/t03-installed-learning-caller-0001/'
 software=stable(prefix+'margin-software.json');instrumentation=stable(prefix+'margin-instrumentation.json')
 config={'schema_version':'lab-protected-observed-margin-runtime/v1-candidate','authority_effect':'none','mode':'diagnostic-measurement','api_directory':api.relative_to(root).as_posix(),'api_source_binding':runtime.api_binding,'profile_binding':runtime.profile_binding,'software_binding':software,'period_binding':provider.binding('family.period'),'dependency_selection_binding':provider.value('native.dependency_selection'),'dependency_installation':provider.value('native.root'),'instrumentation_binding':instrumentation,'policy_binding':None,'load_binding':None}
 # The selected capture contract requires a flat owned /tmp root. Keep its
 # exact pointer in persistent evidence and retain it on indeterminate failure.
 folder=Path(tempfile.mkdtemp(prefix='cal-T03-margin-',dir='/tmp'));folder.chmod(0o700);raw=encoded(config)
 fd=os.open(folder/'configuration.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
 state=folder.stat();control={'root':str(folder),'identity':(state.st_dev,state.st_ino,state.st_uid,stat.S_IMODE(state.st_mode)),'configuration_binding':{'path':'configuration.json','sha256':sha(raw)}}
 fd=os.open(runtime.evidence/'diagnostic-margin-control.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb') as stream:stream.write(encoded(control));stream.flush();os.fsync(stream.fileno())
 return control

def compose(runtime,host,parent,attachment,control):
 margin=runtime.load('observed_margin');modules={name:runtime.load(name) for name in margin.MODULES}
 helpers=[]
 for name in ('margin_capture','margin_kernel','margin_seal','observed_margin'):
  module=modules[name];path=runtime.api/(name+'.py');raw=path.read_bytes()
  helpers.append((name,module,str(path),sha(raw),raw))
 path=runtime.root/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T03/observed-margin-adapter-0003/postimages/composition.py'
 name='_t03_installed_margin_'+uuid.uuid4().hex;spec=importlib.util.spec_from_file_location(name,path);composition=importlib.util.module_from_spec(spec);sys.modules[name]=composition;spec.loader.exec_module(composition)
 return composition.compose(host,parent,modules,attachment,control_root=Path(control['root']),root_identity=control['identity'],selection_binding=control['configuration_binding'],helper_capture=tuple(helpers))
