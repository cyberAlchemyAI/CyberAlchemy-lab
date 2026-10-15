"""Separate ontology execution role; original context720/0004 stays unchanged."""
import copy,hashlib,json,os,re,stat,subprocess
from pathlib import Path

ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
VERSION='lab-ontology-native-execution-selection/v1-candidate'
ONTOLOGY_SHA='57416d01d3479238f9e76a967c0275f1af04466efeb130fc0125bcb94e3a3399'
BASE_PIN='2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'
ENV={'PATH':'/usr/bin:/bin','LC_ALL':'C','PYTHONDONTWRITEBYTECODE':'1','PYTHONNOUSERSITE':'1'}
POLICY={'loader':'lib/abi/ld-linux-x86-64.so.2','library_path':'lib/abi','loader_cache':False,
        'environment':ENV,'timeout_seconds':30,'modes':['seal','append','read']}
FIELDS={'schema_version','authority_effect','base_dependency_selection_binding','base_installation',
        'new_installation','module_bindings','added_inputs','added_elf_graph','ontology_role','execution_policy','installation_receipt_binding'}

def need(ok,why):
    if not ok:raise ValueError(why)
def closed(v,keys):need(type(v)is dict and set(v)==set(keys),'closed ontology execution selection required')
def encoded(v):return (json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def parse(raw):
    need(type(raw)is bytes and len(raw)<=4*1024*1024,'bounded independently selected execution bytes required')
    def pairs(rows):
        out={}
        for k,v in rows:need(k not in out,'duplicate execution selection key');out[k]=v
        return out
    def invalid(_):raise ValueError('nonfinite execution selection')
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=invalid)
def relative(value):
    need(type(value)is str and value and not Path(value).is_absolute() and '..' not in Path(value).parts
         and Path(value).as_posix()==value and '\\' not in value,'canonical relative execution origin required')
    return value
def exact(row,control):
    closed(row,('path','sha256'));path=ROOT/relative(row['path'])
    return control.capture(path,row['sha256'],limit=64*1024*1024)
def module_origin(module,binding,control):
    need(Path(module.__file__)==ROOT/relative(binding['path']),'actual selected execution module origin differs')
    exact(binding,control)
def expected_base(selection):
    value={r['destination']:{'sha256':r['sha256'],'size_bytes':r['size_bytes'],
           'mode':0o755 if r['kind']in{'interpreter','native-executable'}else 0o644}for r in selection['inputs']}
    value.update(selection['wheel_members']);value[POLICY['loader']]['mode']=0o755
    need(len(value)==1010,'whole original1010 installed closure required');return value
def receipt(selection,expected):
    return {'schema_version':'lab-ontology-native-execution-installation/v1-candidate','authority_effect':'none',
            'base_dependency_selection_binding':selection['base_dependency_selection_binding'],'added_inputs':selection['added_inputs'],
            'added_elf_graph':selection['added_elf_graph'],'ontology_role':selection['ontology_role'],
            'execution_policy':selection['execution_policy'],'expected_files_sha256':sha(encoded(expected)),
            'full_original_proof_status':'REFUSED','historical_unavailable_count':25,'runtime_or_owner_qualified':False}

class SelectedOntologyExecutor:
    """Trusted bootstrap capability. Obtaining it never supplies operation authority."""
    def __init__(self,raw,independent_sha256,dependencies,control):
        need(sha(raw)==independent_sha256,'independent ontology execution selection differs')
        self.raw=raw;self.pin=independent_sha256;self.value=parse(raw);closed(self.value,FIELDS)
        v=self.value
        need(v['schema_version']==VERSION and v['authority_effect']=='none' and v['execution_policy']==POLICY,
             'unsupported ontology execution version/policy')
        closed(v['module_bindings'],('dependencies','control'));self.dependencies=dependencies;self.control=control
        module_origin(control,v['module_bindings']['control'],control);module_origin(dependencies,v['module_bindings']['dependencies'],control)
        b=v['base_dependency_selection_binding'];closed(b,('path','sha256'))
        need(b=={'path':'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json','sha256':BASE_PIN},
             'original720 selection cannot be widened or replaced silently')
        self.base,self.base_raw=dependencies.load_selection(ROOT/b['path'],b['sha256'])
        self.expected=expected_base(self.base)
        closed(v['base_installation'],('path','device','inode','uid','mode'))
        closed(v['new_installation'],('path','device','inode','uid','mode'))
        self.base_root=Path(v['base_installation']['path']);self.root=Path(v['new_installation']['path'])
        need(self.base_root==ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
             and self.root!=self.base_root and not self.root.is_relative_to(self.base_root) and not self.base_root.is_relative_to(self.root),
             'new separately owned execution installation required')
        need(type(v['added_inputs'])is list and v['added_inputs'],'explicit added ontology/ABI inputs required')
        seen=set();ontology=[]
        for r in v['added_inputs']:
            closed(r,('source_binding','destination','sha256','size_bytes','mode','kind'))
            name=relative(r['destination']);need(name not in self.expected and name not in seen,'original installed row cannot be overwritten')
            seen.add(name);closed(r['source_binding'],('path','sha256'))
            need(r['source_binding']['sha256']==r['sha256'] and re.fullmatch('[a-f0-9]{64}',r['sha256'])
                 and type(r['size_bytes'])is int and 0<r['size_bytes']<=64*1024*1024,'closed added public byte binding required')
            if r['kind']=='ontology-native-executable':
                need(name=='bin/lab-ontology-native' and r['sha256']==ONTOLOGY_SHA and r['mode']==0o755,'exact original ontology executable role required');ontology.append(r)
            else:need(r['kind']=='host-abi' and name.startswith('lib/abi/') and Path(name).parent.as_posix()=='lib/abi'
                      and r['mode']==0o644,'only explicitly added ABI library supported')
            self.expected[name]={k:r[k]for k in ['sha256','size_bytes','mode']}
        need(len(ontology)==1 and v['ontology_role']=={'destination':'bin/lab-ontology-native','sha256':ONTOLOGY_SHA},'one distinct exact ontology role required')
        need(type(v['added_elf_graph'])is dict and set(v['added_elf_graph'])==seen,'every added ELF needs explicit inspection closure')
        graph={**self.base['elf_graph'],**v['added_elf_graph']}
        for name,info in v['added_elf_graph'].items():
            closed(info,('needed','interpreter'))
            need(type(info['needed'])is list and info['needed']==sorted(set(info['needed'])) and all(type(n)is str and '/'not in n for n in info['needed']),
                 'closed unique declared ELF sonames required')
            need(info['interpreter']in{None,'ld-linux-x86-64.so.2'},'unsupported ontology ELF interpreter')
        for info in graph.values():
            for soname in info['needed']+([info['interpreter']]if info['interpreter']else[]):
                need('lib/abi/'+soname in graph and 'lib/abi/'+soname in self.expected,'missing selected transitive ABI before execution')
        closed(v['installation_receipt_binding'],('path','sha256'))
        need(v['installation_receipt_binding']=={'path':str(self.root/'installation.json'),'sha256':sha(encoded(receipt(v,self.expected)))},
             'complete independently selected extension installation receipt required')
        self._seal=encoded(v)
    @property
    def executable_path(self):return self.root/'bin/lab-ontology-native'
    @property
    def executable_sha256(self):return ONTOLOGY_SHA
    def root_guard(self,field):
        a=self.value[field];path=Path(a['path'])
        need(path.is_absolute() and '..'not in path.parts and path.as_posix()==a['path']
             and not any(p.is_symlink()for p in(path,*path.parents)),'selected native installation path alias')
        s=path.stat();need(stat.S_ISDIR(s.st_mode)and [s.st_dev,s.st_ino,s.st_uid,stat.S_IMODE(s.st_mode)]==[a['device'],a['inode'],a['uid'],a['mode']]
                           and a['uid']==os.getuid()and a['mode']==0o700,'selected native installation root changed')
    def source_guard(self):
        need(sha(self.raw)==self.pin and encoded(self.value)==self._seal,'ontology execution selection mutated')
        need(self.root==Path(self.value['new_installation']['path'])and self.base_root==Path(self.value['base_installation']['path']),
             'selected executable roots mutated')
        module_origin(self.control,self.value['module_bindings']['control'],self.control)
        module_origin(self.dependencies,self.value['module_bindings']['dependencies'],self.control)
        b=self.value['base_dependency_selection_binding'];self.dependencies.preflight(ROOT/b['path'],b['sha256'])
        self.root_guard('base_installation');self.dependencies.verify_installed(self.base_root,self.base)
        for r in self.value['added_inputs']:
            raw=exact(r['source_binding'],self.control);need(len(raw)==r['size_bytes'],'added executable/ABI size differs')
            actual=self.dependencies.BASE.elf(ROOT/r['source_binding']['path'])
            need(actual==self.value['added_elf_graph'][r['destination']],'actual added executable/ABI architecture or graph differs')
    def guard(self):
        self.source_guard();self.root_guard('new_installation')
        self.control.installed(self.root,self.expected)
        b=self.value['installation_receipt_binding'];raw=self.control.capture(b['path'],b['sha256'],limit=4*1024*1024,owner=os.getuid(),mode=0o600)
        need(raw==encoded(receipt(self.value,self.expected)),'whole extension installation receipt bytes differ')
        for r in self.value['added_inputs']:
            need(self.dependencies.BASE.elf(self.root/r['destination'])==self.value['added_elf_graph'][r['destination']],
                 'installed ontology/ABI metadata differs')
        self.root_guard('new_installation')
    def run_native(self,mode,arguments):
        need(mode in {'seal','append','read'} and type(arguments)is list and all(type(v)is str for v in arguments),'exact original ontology argv required')
        need(len(arguments)==(1 if mode=='seal'else 3),'original ontology argv length differs')
        paths=arguments if mode!='read'else arguments[:2]
        need(all(Path(p).is_absolute()and '..'not in Path(p).parts and str(Path(p))==p for p in paths),'canonical original ontology path arguments required')
        if mode=='read':need(re.fullmatch('[0-9]+',arguments[2]),'original semantic cursor must be decimal')
        self.guard()
        try:
            return subprocess.run([str(self.root/POLICY['loader']),'--inhibit-cache','--library-path',str(self.root/POLICY['library_path']),
                                   str(self.executable_path),mode,*arguments],env=dict(ENV),cwd=self.root,
                                  capture_output=True,timeout=30,shell=False)
        finally:self.guard()

def provision(executor):
    """Root-coordinated new installation only, held nofollow directories/exclusive leaves."""
    need(type(executor)is SelectedOntologyExecutor,'exact selected ontology executor required')
    executor.source_guard();executor.root_guard('new_installation')
    root=executor.root;handles=[];links=[];directories={};created=[]
    ident=lambda s:(s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode)
    def attached():
        executor.root_guard('new_installation')
        for parent,name,child,selected in links:
            need(ident(os.stat(name,dir_fd=parent,follow_symlinks=False))==ident(os.fstat(child))==selected,
                 'new installation ancestor detached')
    def write(parent,name,raw,mode):
        attached();fd=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,mode,dir_fd=parent)
        try:
            os.fchmod(fd,mode);before=os.fstat(fd);offset=0
            while offset<len(raw):
                size=os.write(fd,raw[offset:]);need(size>0,'new installation write stalled');offset+=size
            os.fsync(fd);after=os.stat(name,dir_fd=parent,follow_symlinks=False)
            need(ident(after)==ident(before)==ident(os.fstat(fd))and after.st_size==len(raw),'new installation leaf detached')
            attached();os.fsync(parent)
        finally:os.close(fd)
    try:
        parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC);handles.append(parent)
        for part in root.parts[1:]:
            child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent);handles.append(child)
            links.append((parent,part,child,ident(os.fstat(child))));parent=child
        rootfd=parent;directories[()]=rootfd;attached()
        need(os.listdir(rootfd)==[],'new installation must be empty before provisioning')
        for name,row in sorted(executor.expected.items()):
            parts=Path(name).parts;parent=rootfd;prefix=()
            for part in parts[:-1]:
                key=prefix+(part,)
                if key not in directories:
                    attached();os.mkdir(part,0o700,dir_fd=parent)
                    child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent);handles.append(child)
                    st=os.fstat(child);need(st.st_uid==os.getuid()and stat.S_IMODE(st.st_mode)==0o700,'new private payload directory differs')
                    links.append((parent,part,child,ident(st)));directories[key]=child
                parent=directories[key];prefix=key
            added=next((r for r in executor.value['added_inputs']if r['destination']==name),None)
            source=ROOT/added['source_binding']['path']if added else executor.base_root/name
            raw=executor.control.capture(source,row['sha256'],limit=row['size_bytes'],size=row['size_bytes'])
            write(parent,parts[-1],raw,row['mode']);created.append(name)
        write(rootfd,'installation.json',encoded(receipt(executor.value,executor.expected)),0o600)
        executor.guard();attached()
        return {'result':'STAGED-new-ontology-native-installation','files':len(created),'authority_effect':'none','runtime_qualified':False}
    finally:
        for fd in reversed(handles):os.close(fd)


def prepare_selection(added_sources,base_anchor,new_anchor,module_bindings,dependencies,control):
    """Root-only actual-byte/ELF discovery from explicit inputs; no installation."""
    module_origin(control,module_bindings['control'],control);module_origin(dependencies,module_bindings['dependencies'],control)
    base_binding={'path':'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json','sha256':BASE_PIN}
    dependencies.preflight(ROOT/base_binding['path'],BASE_PIN)
    base,_=dependencies.load_selection(ROOT/base_binding['path'],BASE_PIN);expected=expected_base(base)
    added=[];graph={}
    for source in added_sources:
        closed(source,('source_binding','destination','kind'))
        raw=exact(source['source_binding'],control)
        row={**copy.deepcopy(source),'sha256':source['source_binding']['sha256'],'size_bytes':len(raw),
             'mode':0o755 if source['kind']=='ontology-native-executable'else 0o644}
        need(row['destination']not in expected,'original execution rows cannot be replaced')
        added.append(row);expected[row['destination']]={k:row[k]for k in ['sha256','size_bytes','mode']}
        info=dependencies.BASE.elf(ROOT/source['source_binding']['path']);need(info is not None,'added source must be an inspected supported ELF')
        graph[row['destination']]=info
    value={'schema_version':VERSION,'authority_effect':'none','base_dependency_selection_binding':base_binding,
           'base_installation':copy.deepcopy(base_anchor),'new_installation':copy.deepcopy(new_anchor),'module_bindings':copy.deepcopy(module_bindings),
           'added_inputs':added,'added_elf_graph':graph,'ontology_role':{'destination':'bin/lab-ontology-native','sha256':ONTOLOGY_SHA},
           'execution_policy':copy.deepcopy(POLICY),'installation_receipt_binding':None}
    value['installation_receipt_binding']={'path':str(Path(new_anchor['path'])/'installation.json'),'sha256':sha(encoded(receipt(value,expected)))}
    raw=encoded(value);selected=SelectedOntologyExecutor(raw,sha(raw),dependencies,control)
    selected.source_guard();return raw
