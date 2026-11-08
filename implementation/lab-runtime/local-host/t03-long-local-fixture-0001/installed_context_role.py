"""Exact installed Context role over the original isolated 0004 payload.

The original host-source preflight captured a mutable system liblzma in 2026.
This successor verifies every installed payload and its original selection instead.
No work, import of repository runtime, or native child occurs on import.
"""
import hashlib,json,os,stat,subprocess
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
INSTALL=Path('/home/vlad_/.local/share/cyberalchemy-lab/native-install/t22-0001')
BASE={'path':'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json','sha256':'2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'}
NATIVE_SHA='fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'
ENV={'PATH':'/usr/bin:/bin','LC_ALL':'C','PYTHONDONTWRITEBYTECODE':'1','PYTHONNOUSERSITE':'1'}
POLICY={'loader':'lib/abi/ld-linux-x86-64.so.2','library_path':'lib/abi','loader_cache':False,'environment':ENV,'timeout_seconds':30,'role':'original-context-native-reader'}
SUPPORT={'checked_io':{'path':'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/checked_io.py','sha256':'cf9871b52b91842efed22f10484a2d9084ca7aeee59f91d2e9b6277f2f35fd12'},'stage_io':{'path':'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/stage_io.py','sha256':'d16ec83b02a052b975dfba3d96cf848d32f0f9f2d706fe83fab375cdfda112ec'},'closure':{'path':'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/closure.py','sha256':'cae6610064a8f105e6e7ee9bbd5a5a0e07af239b6b43221d7e8b011f0e261a0a'}}
MODULES={'dependencies':{'path':'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/closure_hardened_0003.py','sha256':'00d785f95d675a9acdf644324e21653e09e8b889226d4092576fef937d600715'},'control':{'path':'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/installed-proof-performance-preparation-0001/control.py','sha256':'a212cf5352ce7994e6a041ccc69f8f5924f01b2be2e9067c066e082ee9a9a5dd'}}
FIELDS={'schema_version','authority_effect','dependency_selection_binding','installation','installation_receipt_binding','module_bindings','role_code_binding','native_role','execution_policy'}
def need(v,s):
    if not v:raise ValueError(s)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(value):return(json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def parse(raw):
    def pairs(rows):
        out={}
        for k,v in rows:need(k not in out,'duplicate Context role key');out[k]=v
        return out
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:need(False,'nonfinite Context role'))
def relative(value):
    p=Path(value);need(type(value)is str and not p.is_absolute()and p.as_posix()==value and '..'not in p.parts and '\\'not in value,'canonical Context role input required');return ROOT/p
def validate(value):
    need(type(value)is dict and set(value)==FIELDS and value['schema_version']=='lab-selected-context-native-role/v1-candidate'and value['authority_effect']=='none','closed explicit Context role selection required')
    need(value['dependency_selection_binding']==BASE and value['execution_policy']==POLICY,'original whole720/ABI and fixed Context policy required')
    anchor=value['installation'];need(type(anchor)is dict and set(anchor)=={'path','identity'}and anchor['path']==str(INSTALL)and type(anchor['identity'])is list and len(anchor['identity'])==4 and anchor['identity'][2:]==[os.getuid(),0o700],'selected0004 owned identity required')
    need(value['native_role']=={'destination':'bin/lab-context-native-reader','sha256':NATIVE_SHA},'fb847 Context executable role required; ontology executable forbidden')
    need(value['module_bindings']==MODULES,'exact dependency/control module bindings required')
    for binding in [value['role_code_binding'],*value['module_bindings'].values()]:
        need(type(binding)is dict and set(binding)=={'path','sha256'}and type(binding['sha256'])is str and len(binding['sha256'])==64,'closed independently pinned Context role input required');relative(binding['path'])
    receipt=value['installation_receipt_binding']
    need(type(receipt)is dict and set(receipt)=={'path','sha256'}and type(receipt['sha256'])is str and len(receipt['sha256'])==64,
         'closed clean installation receipt binding required')
    need(value['installation_receipt_binding']['path']==str(INSTALL/'installation.json'),
         'exact clean successor installation receipt required')
    need(relative(value['role_code_binding']['path'])==Path(__file__),'true Context role origin required')
    return value
class SelectedContextExecutor:
    def __init__(self,raw,pin,dependencies,control):
        need(sha(raw)==pin,'independent Context role selection SHA differs')
        self.raw=raw;self.pin=pin;self.value=validate(parse(raw));self.seal=encoded(self.value)
        self.dependencies=dependencies;self.control=control;self.root=INSTALL
        self.modules={key:(module,tuple((name,item,item.__code__,item.__globals__,item.__defaults__,item.__kwdefaults__)for name,item in vars(module).items()if hasattr(item,'__code__')))for key,module in [('checked_io',dependencies.BASE.IO),('stage_io',dependencies.BASE.S),('closure',dependencies.BASE),('dependencies',dependencies),('control',control)]}
        self._module_guard()
    @property
    def executable_path(self):return INSTALL/'bin/lab-context-native-reader'
    @property
    def executable_sha256(self):return NATIVE_SHA
    def _module_guard(self):
        for key,(module,functions)in self.modules.items():
            b=SUPPORT[key]if key in SUPPORT else self.value['module_bindings'][key];need(Path(module.__file__)==relative(b['path']),'true Context dependency module origin differs')
            self.control.capture(relative(b['path']),b['sha256'])
            need(all(vars(module).get(name) is fn and fn.__code__ is code and fn.__globals__ is globals_selected and fn.__defaults__ is defaults and fn.__kwdefaults__ is kwdefaults for name,fn,code,globals_selected,defaults,kwdefaults in functions),'captured Context dependency callback changed')
        b=self.value['role_code_binding'];self.control.capture(relative(b['path']),b['sha256'])
    def guard(self):
        need(sha(self.raw)==self.pin and encoded(self.value)==self.seal and self.root==INSTALL,'Context role selection mutated');validate(self.value);self._module_guard()
        # The installed 0004 payload is hash-closed; host source ABI bytes may drift.
        selected,_=self.dependencies.load_selection(ROOT/BASE['path'],BASE['sha256'])
        need(len(selected['inputs'])==720 and len(selected['elf_graph'])==77,'whole original720/77 ELF context closure required')
        fd=self.control.directory(INSTALL,self.value['installation']['identity'])
        try:
            expected=self.dependencies.verify_installed(INSTALL,selected)
            need(len(expected)==1010,'all original1010 installed payloads required')
            self.control.installed(INSTALL,expected)
            b=self.value['installation_receipt_binding'];self.control.capture(INSTALL/'installation.json',b['sha256'],limit=4*1024*1024,owner=os.getuid(),mode=0o600)
            self.control.capture(self.executable_path,NATIVE_SHA,mode=0o755)
            need(self.dependencies.BASE.elf(self.executable_path)==selected['elf_graph']['bin/lab-context-native-reader'],'selected actual Context ELF graph differs')
        finally:os.close(fd)
        self._module_guard()
    def run_native(self,arguments):
        need(type(arguments)is list and all(type(v)is str for v in arguments),'exact Context argument list required')
        if len(arguments)==2 and arguments[0]=='seal-fixture':paths=arguments[1:]
        else:need(len(arguments)==3,'original Context reader argument form required');paths=arguments
        need(all(Path(v).is_absolute()and Path(v).as_posix()==v and '..'not in Path(v).parts for v in paths),'canonical original Context paths required')
        self.guard()
        try:return subprocess.run([str(INSTALL/POLICY['loader']),'--inhibit-cache','--library-path',str(INSTALL/POLICY['library_path']),str(self.executable_path),*arguments],env=dict(ENV),cwd=INSTALL,capture_output=True,timeout=30,shell=False)
        finally:self.guard()
