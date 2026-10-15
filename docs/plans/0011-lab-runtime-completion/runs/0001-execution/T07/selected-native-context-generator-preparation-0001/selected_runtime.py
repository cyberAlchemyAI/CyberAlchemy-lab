"""True-origin native adapter factory; v1 NativeReadStore is never aliased."""
import hashlib,importlib,importlib.util,json,sys,uuid
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE=Path(__file__).absolute().parent
LEGACY=ROOT/'implementation/lab-context/candidates/v1'
DEP=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001'

def need(value,why):
    if not value:raise ValueError(why)
def closed(value,fields):need(type(value)is dict and set(value)==set(fields),'closed selected-native fields required')
def exact(row):
    closed(row,('path','sha256'));p=ROOT/row['path']
    need(not Path(row['path']).is_absolute() and '..' not in p.parts and p.is_relative_to(ROOT),'selected source origin differs')
    need(not any(q.is_symlink() for q in (p,*p.parents)) and p.is_file(),'selected native source alias')
    raw=p.read_bytes();need(hashlib.sha256(raw).hexdigest()==row['sha256'],'selected native source bytes changed')
    return raw
def actual_module(name,row,package=False):
    raw=exact(row);path=ROOT/row['path'];spec=importlib.util.spec_from_file_location(name,path,submodule_search_locations=[str(path.parent)] if package else None)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    exec(compile(raw,str(path),'exec',dont_inherit=True),module.__dict__);return module

class SelectedRuntime:
    def __init__(self,manifest):
        source=json.loads(exact(manifest['source_closure_binding']))
        need(source['runtime_bindings']==manifest['runtime_bindings'],'reviewed runtime selection differs')
        self.manifest=manifest;self.bindings=source['runtime_bindings'];self._seal=json.dumps(manifest,sort_keys=True)
        bindings=self.bindings
        closed(bindings,('native_module','launch_package','launch_module','custody_module','launch_schema','launch_selection','dependency_module','dependency_selection'))
        for row in bindings.values():exact(row)
        need(str(LEGACY) in sys.path and str(DEP) in sys.path,'trusted selected bootstrap paths required')
        # Original modules retain their real names/files, class algorithms and guards.
        self.original=importlib.import_module('native_reader')
        need(Path(self.original.__file__)==ROOT/bindings['native_module']['path'],'unselected original native module cached')
        self.dependencies=importlib.import_module('closure_hardened_0003')
        need(Path(self.dependencies.__file__)==ROOT/bindings['dependency_module']['path'],'unselected dependency module cached')
        prefix='_cal_C08_selected_native_bridge_'+uuid.uuid4().hex
        actual_module(prefix,bindings['launch_package'],package=True)
        self.launch_module=actual_module(prefix+'.native_launch',bindings['launch_module'])
        self.custody_module=actual_module(prefix+'.protected_bridge',bindings['custody_module'])
        self.launch=self.launch_module.SelectedNativeLaunch(exact(bindings['launch_selection']),bindings['launch_selection']['sha256'],ROOT,self.dependencies,bindings['dependency_module'])
        need(self.launch.native_row['sha256']==manifest['native_executable_sha256'],'selected native differs from generator manifest')
        need(self.launch.value['dependency_selection_binding']==bindings['dependency_selection'],'selected dependency closure differs')
    def guard(self):
        need(json.dumps(self.manifest,sort_keys=True)==self._seal,'selected generator runtime mutated')
        for row in self.bindings.values():exact(row)
        self.launch.guard()
    def store(self,semantic_directory,governance_directory,request,executable,pins):
        self.guard()
        need(Path(executable)==self.launch.native,'caller native locator differs from selected installed native')
        original_pins=self.original.NativePins(**pins) if type(pins)is dict else pins
        need(type(original_pins)is self.original.NativePins,'exact original NativePins required')
        return self.launch_module.SelectedNativeReadStore(self.original,self.bindings['native_module'],ROOT,self.launch,
                    semantic_directory,governance_directory,request,executable,original_pins)
    def require_store(self,store):
        need(type(store)is self.launch_module.SelectedNativeReadStore and store.launch is self.launch
             and store.original is self.original,'exact explicitly selected native read adapter required')
        self.guard()
