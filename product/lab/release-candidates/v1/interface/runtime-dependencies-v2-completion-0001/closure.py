"""Pinned public CPython/SQLite/ELF closure, isolated from live operator inputs."""
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import stat
import subprocess
import checked_io as IO
import stage_io as S

ROOT=Path(__file__).resolve().parents[6]
V1=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v1-completion-0001'
STDLIB=Path('/usr/lib/python3.14')
ABI=Path('/usr/lib/x86_64-linux-gnu')
READELF=Path('/usr/bin/x86_64-linux-gnu-readelf')
LOADER='ld-linux-x86-64.so.2'
ENV={'PATH':'/usr/bin:/bin','LC_ALL':'C','PYTHONDONTWRITEBYTECODE':'1','PYTHONNOUSERSITE':'1'}
EXECUTION_CONFIG={'locale':'C','python_flags':['-I','-X','utf8','-B','-S'],'loader_cache':False,'ambient_environment_inherited':False}
require=IO.require
sha=IO.digest

def record(path,kind,destination,classification='public-installation-bytes'):
    path=Path(path)
    require(not path.is_symlink(),'source symlink rejected')
    value=path.stat();require(stat.S_ISREG(value.st_mode),'regular source required')
    raw=path.read_bytes()
    row={'path':str(path),'kind':kind,'sha256':sha(raw),'size_bytes':len(raw),'mode':stat.S_IMODE(value.st_mode),'destination':destination,'classification':classification}
    IO.anchored_read(path,expected_sha256=row['sha256'],expected_size=row['size_bytes'],expected_mode=row['mode'])
    return row

def stdlib_files():
    # Never follow sitecustomize or development symlinks out of this public root.
    result=[];excluded=[]
    for directory,subdirs,files in os.walk(STDLIB,followlinks=False):
        subdirs[:]=sorted(n for n in subdirs if n not in {'__pycache__','site-packages','dist-packages','config-3.14-x86_64-linux-gnu'})
        for name in sorted(files):
            path=Path(directory)/name
            if name.endswith('.pyc') or path.is_symlink():
                if path.is_symlink():excluded.append({'path':str(path),'reason':'site customization/development alias is outside execution closure'})
                continue
            result.append(path)
    return sorted(result),excluded

def elf(path):
    if Path(path).read_bytes()[:4]!=b'\x7fELF':return None
    result=subprocess.run([str(READELF),'-h','-d','-l',str(path)],env=ENV,capture_output=True,timeout=10)
    require(result.returncode==0,'ELF inspection failed')
    text=result.stdout.decode('utf-8',errors='strict')
    require(re.search(r'Class:\s+ELF64',text) and re.search(r'Machine:\s+Advanced Micro Devices X86-64',text),'unsupported ELF architecture')
    needed=sorted(re.findall(r'\(NEEDED\).*?\[([^\]]+)\]',text))
    require(len(needed)==len(set(needed)) and all('/' not in n for n in needed),'invalid ELF dependency')
    runpaths=re.findall(r'\((?:RUNPATH|RPATH)\).*?\[([^\]]+)\]',text)
    require(not runpaths,'unsupported embedded ELF search path')
    interpreter=re.findall(r'Requesting program interpreter: ([^\]]+)',text)
    require(not interpreter or interpreter==['/lib64/'+LOADER],'unsupported ELF interpreter')
    return {'needed':needed,'interpreter':LOADER if interpreter else None}

def resolve_soname(name):
    require(name and '/' not in name,'bounded ELF soname required')
    source=ABI/name;target=source.resolve(strict=True)
    require(target.parent==ABI and target.is_file() and not target.is_symlink(),'ELF dependency outside exact system ABI root')
    return target

def build_selection(previous):
    previous=Path(previous).absolute()
    old=IO.parse(previous.read_bytes())
    inputs=[]
    for row in old['inputs']:
        if row['kind']=='host-abi':continue
        if row['kind']=='wheel':
            inputs.append(record(row['path'],'wheel','wheels/'+Path(row['path']).name))
        elif row['kind']=='interpreter':inputs.append(record(V1/'installations/0001/bin/python','interpreter','bin/python'))
        else:inputs.append(record(V1/'installations/0001/bin/lab-context-native-reader','native-executable','bin/lab-context-native-reader'))
        require(inputs[-1]['sha256']==row['sha256'],'retained original execution bytes differ')
    paths,excluded=stdlib_files()
    inputs.extend(record(p,'stdlib','lib/python3.14/'+p.relative_to(STDLIB).as_posix()) for p in paths)
    # Wheel members stay original archive bytes; ELF inspection uses the already
    # pinned v1 extraction and records that extraction as provenance only.
    wheel_members={}
    for row in inputs:
        if row['kind']=='wheel':
            for relative,raw in S.wheel_files(S.selected_bytes(row)).items():
                destination='deps/'+relative
                require(destination not in wheel_members,'wheel output collision')
                wheel_members[destination]={'sha256':sha(raw),'size_bytes':len(raw),'mode':0o644}
    graph={};pending={LOADER};abi_names={};wheel_elf_bindings=[]
    for row in inputs:
        if row['kind']=='wheel':continue
        info=elf(row['path'])
        if info:graph[row['destination']]=info;pending.update(info['needed'])
    for destination,row in sorted(wheel_members.items()):
        original=V1/'installations/0001'/destination
        IO.anchored_read(original,expected_sha256=row['sha256'],expected_size=row['size_bytes'],expected_mode=row['mode'])
        if original.read_bytes()[:4]!=b'\x7fELF':continue
        info=elf(original);graph[destination]=info;pending.update(info['needed'])
        wheel_elf_bindings.append({'path':str(original),'sha256':row['sha256'],'size_bytes':row['size_bytes'],'mode':row['mode'],'destination':destination})
    while pending:
        name=min(pending);pending.remove(name)
        if name in abi_names:continue
        target=resolve_soname(name);destination='lib/abi/'+name
        row=record(target,'host-abi',destination,'host-dependency-public-system-bytes')
        row['soname']=name;inputs.append(row);abi_names[name]=target
        info=elf(target);require(info is not None,'ELF system dependency required')
        graph[destination]=info;pending.update(info['needed'])
    bindings=list(old['original_bindings'])
    for p in [Path(previous),V1/'source-manifest.json',ROOT/'product/lab/release-candidates/v1/interface/api-integration-v16/source-manifest.json']:
        bindings.append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes())})
    return {'schema_version':'lab-runtime-dependency-closure/v2-candidate','authority_effect':'none','actual_owner_outcome':None,
        'environment':old['environment'],'execution_configuration':EXECUTION_CONFIG,'versions':old['versions'],'inputs':inputs,'elf_graph':graph,'wheel_members':wheel_members,'wheel_elf_bindings':wheel_elf_bindings,
        'inspection_tool':record(READELF,'inspection-tool',None),'original_bindings':bindings,'excluded_stdlib_inputs':excluded,
        'original_full_proof':{'source_manifest_sha256':'8ac40a51e23b8e528178807792b8ae477aa9c46cd50d92a5b1522c82945413c7','rows':24497,'retained_original_manifest':True,'rows_elided':False,'private_original_paths_opened':False},
        'excluded_protected_inputs':['private signing keys','Reader grants and custody secrets','live databases','operator state'],
        'supported_scope':'Linux/x86_64 CPython3.14.4 R02; exact copied standard library and recursive declared ELF closure. No GUI, external network/DNS or arbitrary third-party dlopen qualification.',
        'old_disposable_locators':[{ 'path':r['path'],'currently_present':Path(r['path']).exists(),'original_digest':r['sha256']} for r in old['inputs'] if r['kind'] in {'interpreter','native-executable'}]}

def validate_structure(selection):
    expected={'schema_version','authority_effect','actual_owner_outcome','environment','execution_configuration','versions','inputs','elf_graph','wheel_members','wheel_elf_bindings','inspection_tool','original_bindings','excluded_stdlib_inputs','original_full_proof','excluded_protected_inputs','supported_scope','old_disposable_locators'}
    require(set(selection)==expected,'closed dependency closure required')
    require(selection['schema_version']=='lab-runtime-dependency-closure/v2-candidate' and selection['authority_effect']=='none' and selection['actual_owner_outcome'] is None,'closure cannot grant authority')
    e=selection['environment'];require(e['system']=='Linux' and e['machine']=='x86_64' and e['implementation']=='CPython' and e['python_version']=='3.14.4' and e['libc']==['glibc','2.43'],'unsupported dependency environment')
    require(set(e)=={'system','machine','implementation','python_version','libc','sqlite_version','interpreter_sha256'} and e['sqlite_version']=='3.46.1' and e['interpreter_sha256']=='52e0a13e60a981d8c4b6478be2ba5176f69da07948a056bf49cf6f077e30cb41','runtime/SQLite identity differs')
    require(selection['versions']=={'attrs':'25.4.0','cffi':'2.0.0','cryptography':'46.0.5','jsonschema':'4.23.0','jsonschema-specifications':'2023.12.1','pycparser':'2.23','referencing':'0.36.2','rpds-py':'0.27.1'},'original R02 package versions differ')
    require(selection['execution_configuration']==EXECUTION_CONFIG,'unsupported execution configuration')
    rows=selection['inputs'];destinations={r['destination']:r for r in rows}
    require(len(rows)==len(destinations),'duplicate installed destination')
    for row in rows:
        require(set(row)=={'kind','path','sha256','size_bytes','mode','destination','classification'}|({'soname'} if row['kind']=='host-abi' else set()),'closed dependency row required')
        kind=row['kind'];p=Path(row['path']);d=row['destination']
        require(kind in {'wheel','interpreter','native-executable','stdlib','host-abi'},'unknown dependency kind')
        require(row['classification']==('host-dependency-public-system-bytes' if kind=='host-abi' else 'public-installation-bytes'),'dependency disclosure class differs')
        if kind=='wheel':require(p.parent==ROOT/'product/lab/release-candidates/v1/packaging/R02/packages/0003/wheels' and d=='wheels/'+p.name,'wheel outside selected original R02')
        elif kind=='stdlib':require(p.is_relative_to(STDLIB) and d=='lib/python3.14/'+p.relative_to(STDLIB).as_posix(),'stdlib outside selected root')
        elif kind=='host-abi':require(p.parent==ABI and d=='lib/abi/'+row['soname'] and '/' not in row['soname'],'ABI outside selected root')
        else:require(p==V1/'installations/0001/bin'/('python' if kind=='interpreter' else 'lab-context-native-reader') and d=='bin/'+p.name and row['mode']==0o755,'retained execution locator differs')
    require(sum(r['kind']=='wheel' for r in rows)==8 and sum(r['kind']=='interpreter' for r in rows)==1 and sum(r['kind']=='native-executable' for r in rows)==1,'original execution closure incomplete')
    require('lib/python3.14/lib-dynload/_sqlite3.cpython-314-x86_64-linux-gnu.so' in destinations and 'lib/abi/libsqlite3.so.0' in destinations,'SQLite closure missing')
    graph=selection['elf_graph'];require('bin/python' in graph and 'bin/lab-context-native-reader' in graph,'execution graph missing')
    for destination,info in graph.items():
        require(destination in destinations or destination in selection['wheel_members'],'unselected ELF graph node')
        require(set(info)=={'needed','interpreter'},'closed ELF graph node required')
        for name in info['needed']+([info['interpreter']] if info['interpreter'] else []):require('lib/abi/'+name in graph,'transitive ELF dependency missing')
    require(selection['original_full_proof']=={'source_manifest_sha256':'8ac40a51e23b8e528178807792b8ae477aa9c46cd50d92a5b1522c82945413c7','rows':24497,'retained_original_manifest':True,'rows_elided':False,'private_original_paths_opened':False},'full original proof binding differs')
    return destinations

def load_selection(path,pin):
    path=Path(path);require(not any(p.is_symlink() for p in [path,*path.parents]),'selection symlink refused')
    raw=path.read_bytes();require(sha(raw)==pin,'independent closure selection differs')
    selected=IO.parse(raw);validate_structure(selected);return selected,raw

def preflight(path,pin):
    selection,raw=load_selection(path,pin)
    require(platform.system()=='Linux' and platform.machine()=='x86_64' and list(platform.libc_ver())==selection['environment']['libc'],'actual host ABI differs')
    tool=selection['inspection_tool'];require(tool['path']==str(READELF),'inspection tool differs');S.selected_bytes(tool)
    observed=[]
    for row in selection['inputs']:observed.append(IO.anchored_read(row['path'],expected_sha256=row['sha256'],expected_size=row['size_bytes'],expected_mode=row['mode']))
    actual_paths,_=stdlib_files();require(set(map(str,actual_paths))=={r['path'] for r in selection['inputs'] if r['kind']=='stdlib'},'standard library inventory differs')
    graph={};wheel_members={}
    for row in selection['inputs']:
        if row['kind']=='wheel':
            members=S.wheel_files(S.selected_bytes(row))
            for n,b in members.items():
                require('deps/'+n not in wheel_members,'wheel output collision')
                wheel_members['deps/'+n]={'sha256':sha(b),'size_bytes':len(b),'mode':0o644}
        else:
            info=elf(row['path'])
            if info:graph[row['destination']]=info
    for row in selection['wheel_elf_bindings']:
        S.selected_bytes(row);info=elf(row['path']);require(info is not None,'wheel ELF absent');graph[row['destination']]=info
    require(wheel_members==selection['wheel_members'],'wheel membership differs')
    actual_wheel_elf={n for n in wheel_members if S.selected_bytes({'path':str(V1/'installations/0001'/n),**wheel_members[n]})[:4]==b'\x7fELF'}
    require(actual_wheel_elf=={r['destination'] for r in selection['wheel_elf_bindings']},'wheel ELF closure omitted')
    require(graph==selection['elf_graph'],'actual ELF dependency graph differs')
    for row in selection['original_bindings']:IO.anchored_read(ROOT/row['path'],expected_sha256=row['sha256'])
    require(Path(path).read_bytes()==raw,'selection changed')
    return {'result':'PASS','selection_sha256':pin,'verified_inputs':observed,'elf_nodes':len(graph),'original_full_proof':selection['original_full_proof'],'authority_effect':'none','execution_authorized':False}

def installed_files(selection):
    files={r['destination']:{'sha256':r['sha256'],'size_bytes':r['size_bytes'],'mode':0o755 if r['kind'] in {'interpreter','native-executable'} else 0o644} for r in selection['inputs']}
    files.update(selection['wheel_members']);files['lib/abi/'+LOADER]['mode']=0o755
    return files

def verify_installed(destination,selection):
    expected=installed_files(selection);destination=Path(destination)
    require(not any(p.is_symlink() for p in [destination,*destination.parents]),'installation ancestry symlink refused')
    require(destination.stat().st_uid==os.geteuid() and stat.S_IMODE(destination.stat().st_mode)==0o700,'installation ownership differs')
    for relative,row in expected.items():IO.anchored_read(destination/relative,expected_sha256=row['sha256'],expected_size=row['size_bytes'],expected_mode=row['mode'])
    actual=set()
    for directory,subdirs,names in os.walk(destination,followlinks=False):
        for name in subdirs+names:require(not (Path(directory)/name).is_symlink(),'installed symlink refused')
        for name in names:actual.add((Path(directory)/name).relative_to(destination).as_posix())
    require(actual==set(expected)|({'installation.json'} if (destination/'installation.json').exists() else set()),'unexpected installed dependency bytes')
    return expected

def python_command(destination,code,args=()):
    destination=Path(destination)
    # -I finds the bundled lib/python3.14 relative to the executable; neither
    # PYTHONHOME nor the global host site-packages can extend the selected path.
    return [str(destination/'lib/abi'/LOADER),'--inhibit-cache','--library-path',str(destination/'lib/abi'),str(destination/'bin/python'),*EXECUTION_CONFIG['python_flags'],'-c',code,*map(str,args)]

def cold_probe(destination,selection):
    verify_installed(destination,selection)
    code="""import sys,json,sqlite3,importlib.metadata,hashlib,ssl,bz2,lzma,ctypes,asyncio,uuid,resource,fcntl,zipfile
from pathlib import Path
root=Path(sys.argv[1]);sys.path.insert(0,str(root/'deps'))
import jsonschema,cryptography,cffi,rpds,referencing,attr
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
k=Ed25519PrivateKey.generate();message=b'owned runtime dependency cold check';k.public_key().verify(k.sign(message),message)
jsonschema.Draft202012Validator({'type':'integer'}).validate(7)
assert sys.flags.utf8_mode==1 and sys.getfilesystemencoding()=='utf-8'
db=sqlite3.connect(':memory:');db.execute('CREATE TABLE probe(value INTEGER, text_value TEXT)');db.execute('INSERT INTO probe VALUES(?, ?)',(7,'Laboratório 研究'));assert db.execute('SELECT value, text_value FROM probe').fetchone()==(7,'Laboratório 研究');db.close()
assert bz2.decompress(bz2.compress(message))==message and lzma.decompress(lzma.compress(message))==message
modules={name:str(Path(value.__file__).resolve()) for name,value in list(sys.modules.items()) if getattr(value,'__file__',None) and not str(value.__file__).startswith('<')}
assert all(Path(p).is_relative_to(root) for p in modules.values()),'external Python module loaded'
maps=sorted({line.split()[-1] for line in Path('/proc/self/maps').read_text().splitlines() if len(line.split())>=6 and line.split()[-1].startswith('/')})
assert all(Path(p).is_relative_to(root) for p in maps),'external ELF mapping loaded'
print(json.dumps({'python_version':sys.version.split()[0],'sqlite_version':sqlite3.sqlite_version,'versions':{n:importlib.metadata.version(n) for n in json.loads(sys.argv[2])},'python_paths':sys.path,'module_origins':modules,'mapped_files':maps,'sqlite_transaction':True,'utf8_roundtrip':True,'ed25519_signature':True,'schema_validation':True,'compression_roundtrips':True}))
"""
    result=subprocess.run(python_command(destination,code,[destination,json.dumps(list(selection['versions']))]),env=ENV,capture_output=True,timeout=60)
    require(result.returncode==0,'cold bundled Python probe failed: '+result.stderr.decode('utf-8',errors='replace')[-1500:])
    probe=IO.parse(result.stdout);require(probe['versions']==selection['versions'] and probe['python_version']==selection['environment']['python_version'] and probe['sqlite_version']==selection['environment']['sqlite_version'],'cold selected versions differ')
    native=subprocess.run([str(Path(destination)/'lib/abi'/LOADER),'--inhibit-cache','--library-path',str(Path(destination)/'lib/abi'),str(Path(destination)/'bin/lab-context-native-reader')],env=ENV,capture_output=True,timeout=10)
    require(native.returncode==1 and native.stdout==b'' and native.stderr==b'usage: lab-context-native-reader semantic-dir governance-dir request.json\n','cold native entrypoint differs')
    verify_installed(destination,selection)
    return {'result':'PASS','python':probe,'native_usage':{'exit_code':1,'expected_usage':True},'native_history_replay_proven':False,'full_lab_startup_proven':False,'protected_inputs_provisioned':False}

def install(path,pin,parent,parent_identity,name):
    require(name and len(name)<=64 and name.replace('-','').isalnum(),'bounded owned generation name required')
    verification=preflight(path,pin);selection,_=load_selection(path,pin)
    handles,parent_fd=S.owned_directory(parent,parent_identity)
    try:
        os.mkdir(name,mode=0o700,dir_fd=parent_fd)
        child_fd=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent_fd);handles.append(child_fd)
        child_identity=IO.directory_identity(os.fstat(child_fd));anchored=Path('/proc/self/fd')/str(child_fd)
        for row in selection['inputs']:
            raw=S.selected_bytes(row);mode=installed_files(selection)[row['destination']]['mode']
            S.write_file(anchored,row['destination'],raw,mode)
            if row['kind']=='wheel':
                for relative,value in S.wheel_files(raw).items():S.write_file(anchored,'deps/'+relative,value,0o644)
        destination=Path(parent)/name
        require(IO.directory_identity(destination.stat(follow_symlinks=False))==child_identity,'installed root changed')
        probe=cold_probe(destination,selection)
        preflight(path,pin)
        report={'schema_version':'lab-runtime-dependency-install/v2-candidate','result':'PASS','selection_sha256':pin,'destination':str(destination),'directory_identity':list(child_identity),'installed_files':installed_files(selection),'cold_probe':probe,'preflight':verification,'original_provenance_retained':True,'old_source_locators_rewritten':False,'private_inputs_shipped':False,'authority_effect':'none','task_complete':False,'remaining':'Final frozen API17 startup and separately provisioned protected-input integration require coordinator evidence.'}
        S.write_file(anchored,'installation.json',(json.dumps(report,sort_keys=True,indent=2)+'\n').encode(),0o600)
        os.fsync(child_fd);os.fsync(parent_fd);return report
    finally:
        for fd in reversed(handles):os.close(fd)
