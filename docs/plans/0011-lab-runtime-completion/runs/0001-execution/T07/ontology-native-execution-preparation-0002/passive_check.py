"""Pinned public ELF/ABI metadata and AST only; never import an executor/guard."""
import ast,copy,hashlib,json,os,struct,sys,types
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
HERE=Path(__file__).absolute().parent
OLD=HERE.parent/'ontology-native-execution-preparation-0001'
INSTALL=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
FRESH='82713671f1c1271f92b7ae675ccee531c0ee972828e25899c0c19e64015025f6'
def need(value,why):
    if not value:raise ValueError(why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def fds():
    result={}
    for name in os.listdir('/proc/self/fd'):
        try:s=os.fstat(int(name));result[name]=(s.st_dev,s.st_ino,s.st_mode)
        except OSError:continue
    return result
def elf(raw):
    need(raw[:6]==b'\x7fELF\x02\x01','ELF64 little-endian required')
    def unpack(fmt,offset,data=raw):need(0<=offset and offset+struct.calcsize(fmt)<=len(data),'ELF field range');return struct.unpack_from(fmt,data,offset)
    def string(data,offset):need(0<=offset<len(data),'ELF string range');end=data.find(b'\0',offset);need(end>=offset,'ELF string terminator');return data[offset:end].decode('utf8','strict')
    header=unpack('<16sHHIQQQIHHHHHH',0);phoff,shoff=header[5:7];phsize,phnum,shsize,shnum,shstr=header[9:14]
    need(phsize==56 and shsize==64 and phnum<256 and 0<shnum<4096 and shstr<shnum,'ELF table shape')
    entries=[unpack('<IIQQQQIIQQ',shoff+i*shsize)for i in range(shnum)]
    def section(entry):start,size=entry[4:6];need(start+size<=len(raw),'ELF section range');return raw[start:start+size]
    labels=section(entries[shstr]);sections={string(labels,row[0]):row for row in entries}
    dynstr=section(sections['.dynstr']);needed=[];interpreter=None
    for offset in range(0,len(section(sections['.dynamic'])),16):
        tag,value=unpack('<qQ',offset,section(sections['.dynamic']))
        if tag==1:needed.append(string(dynstr,value))
    for index in range(phnum):
        row=unpack('<IIQQQQQQ',phoff+index*phsize)
        if row[0]==3:need(row[2]+row[5]<=len(raw),'ELF interpreter range');interpreter=raw[row[2]:row[2]+row[5]].rstrip(b'\0').decode()
    requires={};defines={};requirements=[];definitions=[]
    if '.gnu.version_r'in sections:
        data=section(sections['.gnu.version_r']);offset=0
        for _ in range(1024):
            version,count,file,aux,next=unpack('<HHIII',offset,data);need(version==1 and count<1024,'ELF verneed shape');provider=string(dynstr,file);position=offset+aux
            for _ in range(count):
                _,flags,index,name,advance=unpack('<IHHII',position,data);label=string(dynstr,name);requires[index&0x7fff]={'provider':provider,'version':label};requirements.append({'provider':provider,'version':label,'flags':flags});position+=advance
            if not next:break
            offset+=next
        else:raise ValueError('unbounded version requirements')
    if '.gnu.version_d'in sections:
        data=section(sections['.gnu.version_d']);offset=0
        for _ in range(1024):
            version,flags,index,count,_,aux,next=unpack('<HHHHIII',offset,data);need(version==1 and 0<count<1024,'ELF verdef shape');name,_=unpack('<II',offset+aux,data);label=string(dynstr,name);defines[index&0x7fff]=label;definitions.append(label)
            if not next:break
            offset+=next
        else:raise ValueError('unbounded version definitions')
    symbols=section(sections['.dynsym']);versions=section(sections['.gnu.version'])if '.gnu.version'in sections else b'';imports=[];exports=[]
    need(len(symbols)%24==0 and (not versions or len(versions)==len(symbols)//12),'ELF dynamic symbol/version count')
    for index in range(len(symbols)//24):
        name,info,other,defined,_,_=unpack('<IBBHQQ',24*index,symbols)
        if not name:continue
        name=string(dynstr,name);version=unpack('<H',index*2,versions)[0]&0x7fff if versions else 1
        if defined==0:
            if version>=2:need(version in requires,'undefined symbol version missing')
            imports.append({'name':name,'weak':info>>4==2,**requires.get(version,{'provider':None,'version':None})})
        elif info>>4 in(1,2)and other&3 in(0,3):exports.append((name,defines.get(version)if version>=2 else None))
    comments=[s.decode()for s in section(sections['.comment']).split(b'\0')if s]if '.comment'in sections else []
    return {'metadata':{'class':2,'endianness':1,'type':header[1],'machine':header[2],'interpreter':interpreter,'needed':sorted(needed),'comment':comments},'version_requirements':requirements,'version_definitions':sorted(definitions),'imports':imports,'exports':exports}
def main():
    baseline=fds();controlpath=RUN/'T07/installed-proof-performance-preparation-0001/control.py';raw=controlpath.read_bytes();need(sha(raw)=='a212cf5352ce7994e6a041ccc69f8f5924f01b2be2e9067c066e082ee9a9a5dd','selected passive capture helper differs')
    control=types.ModuleType('_T07_827_passive_capture');control.__file__=str(controlpath);exec(compile(raw,str(controlpath),'exec'),control.__dict__);need(control.capture(controlpath,sha(raw))==raw,'helper attachment changed')
    old=ast.parse((OLD/'native_executor.py').read_bytes());new=ast.parse((HERE/'native_executor.py').read_bytes());normalized=copy.deepcopy(new);changes=[]
    for node in normalized.body:
        if isinstance(node,ast.Assign)and isinstance(node.targets[0],ast.Name)and node.targets[0].id in('VERSION','ONTOLOGY_SHA'):
            name=node.targets[0].id;oldnode=next(n for n in old.body if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id==name);changes.append({'constant':name,'old':oldnode.value.value,'new':node.value.value});node.value=copy.deepcopy(oldnode.value)
    need(ast.dump(normalized,include_attributes=False)==ast.dump(old,include_attributes=False),'executor changed beyond two literal constants')
    functions=sum(isinstance(n,ast.FunctionDef)for n in ast.walk(old));need(functions==23,'original helper count differs')
    resultpath=Path('/tmp/cal-T32-rust-provenance-root-0001/observations/result.json');result=json.loads(control.capture(resultpath,'b126e629fc314325391dffcf3a93609196ad6218e6efaf54ff4e98ffaae0fe5a'))
    need(result['result']=='PASS-bounded-current-host-observation'and result['accepted_observations']['original23']['all23_pass']and len(result['commands'])==5 and not result['exit_errors'],'Root current-host terminal differs')
    builds=[]
    for key in('03-fresh-build','05-independent-target-build'):
        row=result['accepted_observations'][key];need(row['sha256']==FRESH and row['size_bytes']==20843752,'fresh binding differs');body=control.capture(row['path'],FRESH,size=row['size_bytes'],owner=os.getuid(),mode=0o755);builds.append(elf(body))
    need(builds[0]==builds[1],'fresh ELF/symbol metadata differ')
    archivepath=RUN/'T32/native-rust-Root-execution-0001/bin/lab-ontology-native';archive=control.capture(archivepath,FRESH,size=20843752,owner=os.getuid(),mode=0o755)
    need(elf(archive)==builds[0],'Root archive metadata differs from actual fresh builds')
    basepath=RUN/'T07/revision-0002/dependency-selection-0002.json';base=json.loads(control.capture(basepath,'2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'));rows={r['destination']:r for r in base['inputs']};graph=base['elf_graph'];providers={};provider_bindings=[]
    for soname in builds[0]['metadata']['needed']:
        name='lib/abi/'+soname;row=rows[name];mode=0o755 if soname=='ld-linux-x86-64.so.2'else 0o644;path=INSTALL/name;body=control.capture(path,row['sha256'],size=row['size_bytes'],owner=os.getuid(),mode=mode);providers[soname]=elf(body);provider_bindings.append({'path':str(path),'sha256':row['sha256'],'size_bytes':row['size_bytes'],'mode':mode})
        need(providers[soname]['metadata']['machine']==62 and providers[soname]['metadata']['class']==2,'selected provider architecture differs')
        for dependency in graph[name]['needed']+([graph[name]['interpreter']]if graph[name]['interpreter']else[]):need('lib/abi/'+dependency in graph and 'lib/abi/'+dependency in rows,'selected provider dependency outside original graph')
    matched=[];unversioned=[]
    for row in builds[0]['imports']:
        if row['provider']is None:
            supported=any(any(name==row['name']for name,_ in p['exports'])for p in providers.values());need(row['weak']or supported,'unresolved strong unversioned symbol');unversioned.append({**row,'provided':supported});continue
        need(row['provider']in providers and (row['name'],row['version'])in providers[row['provider']]['exports'],'selected provider missing required symbol/version');matched.append(row)
    existing=ROOT/'product/lab/release-candidates/v1/interface/native-batch-recovery-v1-completion-0001/bin-production/lab-ontology-native';prior=elf(control.capture(existing,'57416d01d3479238f9e76a967c0275f1af04466efeb130fc0125bcb94e3a3399',size=20839640,mode=0o755))
    need(fds()==baseline and 'ctypes'not in sys.modules,'passive check resources differ')
    value={'schema_version':'lab-T07-827-passive-ELF-role-check/v1-candidate','result':'PASS-static-role-specialization-and-ELF-provider-matches','two_literal_changes':changes,'original_direct_function_method_bodies_AST_identical':19,'all_functions_including_nested_AST_identical':functions,'full_other_module_AST_identical_after_literal_normalization':True,'fresh_SHA':FRESH,'fresh_size':20843752,'fresh_mode':0o755,'fresh_ELF':builds[0]['metadata'],'version_requirements':builds[0]['version_requirements'],'matched_versioned_import_symbols':matched,'unversioned_imports':unversioned,'selected_original_ABI_provider_bindings':provider_bindings,'additional_ABI_inputs_needed_by_static_graph':[],'retained574_ELF_metadata_equal':prior['metadata']==builds[0]['metadata'],'retained574_byte_SHA_equal':False,'binary_difference_cause':'unproven','Root_actual_result_binding':{'path':str(resultpath),'sha256':'b126e629fc314325391dffcf3a93609196ad6218e6efaf54ff4e98ffaae0fe5a'},'FD_delta':0,'ctypes_imported':False,'actual_Source_guard_executor_API_native_compiler_installation_or_lease_executed':False,'native_runtime_ABI_or_schema_semantics_qualified':False}
    with(HERE/'passive-result.json').open('x')as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'result':value['result'],'functions':functions,'providers':len(providers),'versioned_symbols':len(matched),'FD_delta':0},sort_keys=True))
if __name__=='__main__':main()
