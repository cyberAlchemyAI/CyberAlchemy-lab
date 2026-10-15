"""Inactive Root-selected serial current-host build/test observer; no work at import."""
import argparse, datetime, hashlib, importlib.util, json, os, re, signal, stat, struct, subprocess, sys, time, traceback, types
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE=Path(__file__).absolute().parent
INSTALL=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
OWNED=Path('/tmp/cal-T32-rust-provenance-root-0001')
CONTROL=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/installed-proof-performance-preparation-0001/control.py'
CONTROL_SHA='a212cf5352ce7994e6a041ccc69f8f5924f01b2be2e9067c066e082ee9a9a5dd'
SOURCE='ee969cc8c6b539aa3247d81c82322cb9e7aefd42188d63db0195e381cdad4cb1'
PROFILE='9c8c3018226abb9077c6a99ee3cbc9dd0174c148b332b9488fd4a3a9cd30418b'
MODE='Root-exclusive-current-host-five-commands'
def need(value,why):
    if not value:raise ValueError(why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def parse(raw):
    def pairs(rows):
        result={}
        for key,value in rows:
            need(key not in result,'duplicate selected JSON key');result[key]=value
        return result
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('nonfinite JSON')))
def closed(value,keys):need(type(value)is dict and set(value)==set(keys),'closed selected object required')
def path_of(row):
    p=Path(row['path']);need('..'not in p.parts and str(p)==row['path'],'canonical selected path required')
    return p if p.is_absolute()else ROOT/p
def diagnostic():
    kind,error,tb=sys.exc_info()
    return {'exception_class':kind.__name__,'message':str(error),'frames':[{'path':f.filename,'line':f.lineno,'function':f.name}for f in traceback.extract_tb(tb)]}
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def group_alive(pid):
    try:os.killpg(pid,0);return True
    except ProcessLookupError:return False
def stop_owned_group(child,actions):
    """Only the recorded start_new_session process group; never scan other PIDs."""
    for sig in(signal.SIGTERM,signal.SIGKILL):
        if not group_alive(child.pid):break
        try:os.killpg(child.pid,sig);actions.append({'process_group':child.pid,'signal':sig.name})
        except ProcessLookupError:break
        until=time.monotonic()+5
        while group_alive(child.pid)and time.monotonic()<until:
            child.poll();time.sleep(0.05)
    child.poll()
    need(not group_alive(child.pid)and child.returncode is not None,'owned command group or direct child remains; Root must retain handle')

class OwnedOutput:
    """Hold every ancestor and selected root throughout this synchronous episode."""
    def __init__(self,root_identity,observations_identity):
        self.handles=[];self.links=[];self.fd=None
        try:
            parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC);self.handles.append(parent)
            for name in (OWNED/'observations').parts[1:]:
                child=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent);self.handles.append(child)
                s=os.fstat(child);self.links.append((parent,name,child,self.identity(s)));parent=child
                if name==OWNED.name:need(self.selected(s)==root_identity,'selected setup root changed')
            self.fd=parent;s=os.fstat(parent)
            need(self.selected(s)==observations_identity and s.st_uid==os.getuid()and stat.S_IMODE(s.st_mode)==0o700,'owned observations custody differs')
            self.guard();need(os.listdir(parent)==[],'observations must start empty')
        except BaseException:self.close();raise
    @staticmethod
    def identity(s):return (s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode)
    @staticmethod
    def selected(s):return [s.st_dev,s.st_ino,s.st_uid,stat.S_IMODE(s.st_mode)]
    def guard(self):
        for parent,name,child,pin in self.links:
            need(self.identity(os.stat(name,dir_fd=parent,follow_symlinks=False))==self.identity(os.fstat(child))==pin,'owned output ancestor detached')
    def create(self,name):
        need(type(name)is str and Path(name).name==name and name not in('.','..'),'flat owned output required');self.guard()
        fd=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=self.fd)
        os.fchmod(fd,0o600);return fd
    def finish(self,name,fd):
        os.fsync(fd);a=os.fstat(fd);b=os.stat(name,dir_fd=self.fd,follow_symlinks=False)
        need(self.identity(a)==self.identity(b)and a.st_size==b.st_size and stat.S_ISREG(a.st_mode)and a.st_uid==os.getuid()and stat.S_IMODE(a.st_mode)==0o600,'owned stream attachment differs')
        self.guard();os.fsync(self.fd)
    def emit(self,name,value):
        fd=self.create(name)
        try:
            raw=canonical(value);offset=0
            while offset<len(raw):
                count=os.write(fd,raw[offset:]);need(count>0,'owned terminal write stalled');offset+=count
            self.finish(name,fd)
        finally:os.close(fd)
    def close(self):
        for fd in reversed(self.handles):os.close(fd)
        self.handles=[]

def test_accounting(raw,names):
    rows=re.findall(rb'^test ([A-Za-z0-9_:]+) \.\.\. ([^\r\n]+)$',raw,re.M)
    observed=[(name.decode(),result.decode())for name,result in rows]
    need(len(observed)==23 and {name for name,_ in observed}==set(names)and all(result=='ok'for _,result in observed),'full23 exact named original tests did not all pass')
    summaries=re.findall(rb'^test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',raw,re.M)
    need(sorted(int(r[0])for r in summaries if int(r[0]))==[3,20]and all(all(int(v)==0 for v in r[1:])for r in summaries),'test cohort failed, ignored, measured or filtered')
    return {'named_results':observed,'summary_rows':[[int(v)for v in r]for r in summaries],'all23_pass':True}

def elf_metadata(raw):
    """Read ELF64 little-endian public metadata without executing any tool/binary."""
    need(raw[:6]==b'\x7fELF\x02\x01','expected ELF64 little-endian output')
    def unpack(fmt,offset):need(0<=offset and offset+struct.calcsize(fmt)<=len(raw),'ELF range');return struct.unpack_from(fmt,raw,offset)
    def string(table,offset):need(0<=offset<len(table),'ELF string offset');end=table.find(b'\0',offset);need(end>=offset,'ELF string terminator');return table[offset:end].decode('utf8','replace')
    head=unpack('<16sHHIQQQIHHHHHH',0);phoff,shoff=head[5:7];phsize,phnum,shsize,shnum,shstr=head[9:14]
    need(phsize==56 and shsize==64 and phnum<256 and 0<shnum<4096 and shstr<shnum,'ELF tables')
    sections=[unpack('<IIQQQQIIQQ',shoff+i*shsize)for i in range(shnum)]
    def section(row):start,size=row[4:6];need(start+size<=len(raw),'ELF section range');return raw[start:start+size]
    labels=section(sections[shstr]);needed=[];comment=[];interpreter=None
    for i in range(phnum):
        ph=unpack('<IIQQQQQQ',phoff+i*phsize)
        if ph[0]==3:need(ph[2]+ph[5]<=len(raw),'ELF interpreter range');interpreter=raw[ph[2]:ph[2]+ph[5]].rstrip(b'\0').decode()
    for row in sections:
        name=string(labels,row[0])
        if name=='.comment':comment=[x.decode('utf8','replace')for x in section(row).split(b'\0')if x]
        if row[1]==6:
            need(row[6]<shnum and row[5]%16==0,'ELF dynamic table');table=section(sections[row[6]]);data=section(row)
            for off in range(0,len(data),16):
                kind,value=struct.unpack_from('<qQ',data,off)
                if kind==1:needed.append(string(table,value))
    return {'class':2,'endianness':1,'type':head[1],'machine':head[2],'interpreter':interpreter,'needed':sorted(needed),'comment':comment}

def run(selection,selection_binding,control,self_binding):
    closed(selection,('schema_version','authority_effect','mode','input_selection_binding','setup_binding','root_dispatch_binding'))
    need(selection['schema_version']=='lab-T32-rust-execution-selection/v1-candidate'and selection['authority_effect']=='none'and selection['mode']==MODE,'inactive/unsupported Root selection')
    def exact(row,**kwargs):closed(row,('path','sha256'));return control.capture(path_of(row),row['sha256'],**kwargs)
    need(path_of(selection['input_selection_binding'])==HERE/'inputs.json','actual frozen input origin required')
    inputs=parse(exact(selection['input_selection_binding']));refs=inputs['references'];mods=inputs['module_bindings']
    need(refs['source']['sha256']==SOURCE and refs['profile']['sha256']==PROFILE,'current Source/profile cannot change')
    proposal=parse(exact(refs['proposal']));original_inputs=parse(exact(refs['inputs110']));cache=parse(exact(refs['cache']))
    need(len(original_inputs['files'])==110 and len(proposal['commands'])==5,'exact reviewed110/five commands required')
    for row in original_inputs['files']:need(row in inputs['files'],'original110 declaration pruned')
    def all_inputs():
        for row in inputs['files']:control.capture(path_of(row),row['sha256'],size=row['size_bytes'])
        for row in (self_binding,selection_binding,selection['input_selection_binding'],selection['root_dispatch_binding'],selection['setup_binding']):exact(row)
        control.capture(OWNED/'commands.json',sha(canonical(proposal['commands'])),owner=os.getuid(),mode=0o600)
    all_inputs()
    setup=parse(exact(selection['setup_binding'],owner=os.getuid(),mode=0o600));dispatch=parse(exact(selection['root_dispatch_binding']))
    closed(dispatch,('schema_version','authority_effect','mode','owned_root','observations_identity','setup_binding','command_timeout_seconds'))
    need(dispatch['schema_version']=='lab-T32-rust-Root-dispatch/v1-candidate'and dispatch['authority_effect']=='none'and dispatch['mode']==MODE,'Root serial technical dispatch required')
    need(dispatch['setup_binding']==selection['setup_binding']and path_of(selection['setup_binding'])==OWNED/'SETUP.json','actual independently selected SETUP required')
    need(setup['schema_version']=='lab-T32-owned-rust-setup/v1-candidate'and setup['authority_effect']=='none'and setup['setup_sha256']==refs['setup_recipe']['sha256']and setup['root']==dispatch['owned_root']and setup['locked_cache_files']==65 and setup['all5_commands_unexecuted']is True and setup['all_copied_sha_size_mode']=='PASS'and setup['inputs110_entry_exit']=='PASS','reviewed exact setup correspondence required')
    need(dispatch['owned_root']['path']==str(OWNED)and dispatch['owned_root']['identity'][2:]==[os.getuid(),0o700],'owned root contract')
    timeout=dispatch['command_timeout_seconds'];need(type(timeout)in(int,float)and 0<timeout<float('inf'),'Root must explicitly bound each command')
    command_bytes=control.capture(OWNED/'commands.json',sha(canonical(proposal['commands'])),owner=os.getuid(),mode=0o600)
    need(command_bytes==canonical(proposal['commands']),'setup commands differ from reviewed five')
    for target in proposal['new_targets']:need(not os.path.lexists(target),'both exact build targets must start absent')
    out=OwnedOutput(dispatch['owned_root']['identity'],dispatch['observations_identity'])
    loaded={};events=[];phases=[];errors=[];failure=None;accepted={};guard=None;deps=None;base=None;capture_output=None
    def measure(label,fn):
        start=time.monotonic();success=False
        try:value=fn();success=True;return value
        finally:phases.append({'phase':label,'success':success,'seconds':time.monotonic()-start})
    def configurations():
        for parent in (ROOT,*ROOT.parents):
            for name in ('config','config.toml'):need(not os.path.lexists(parent/'.cargo'/name),'unselected ancestor Cargo config')
        for name in ('config','config.toml'):need(not os.path.lexists(OWNED/'cargo-home'/name),'unselected fresh Cargo config')
    def cache_guard(initial=False):
        copies=[(row[key+'_destination'],row[key+'_binding'])for row in cache['packages']for key in ('archive','index')]
        copies.append((cache['index_config']['destination'],cache['index_config']['source_binding']))
        need(len(copies)==65,'complete selected cache65 required')
        for destination,row in copies:control.capture(OWNED/'cargo-home'/destination,row['sha256'],size=row['size_bytes'],owner=os.getuid(),mode=0o600)
        if initial:
            observed=set()
            for directory,subdirs,names in os.walk(OWNED/'cargo-home',followlinks=False):
                for name in subdirs+names:need(not(Path(directory)/name).is_symlink(),'new cache symlink')
                for name in names:observed.add(str((Path(directory)/name).relative_to(OWNED/'cargo-home')))
            need(observed=={name for name,_ in copies},'new cache must contain only exact copied65 files')
        configurations();out.guard()
    def load(name,binding):
        need(name not in sys.modules,'fresh selected module name required');path=path_of(binding);raw=exact(binding)
        spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;exec(compile(raw,str(path),'exec'),module.__dict__);return module
    def installed():
        need(base is not None and deps is not None,'dependency initialization incomplete')
        anchor=inputs['base_anchor'];s=INSTALL.stat(follow_symlinks=False)
        need([s.st_dev,s.st_ino,s.st_uid,stat.S_IMODE(s.st_mode)]==[anchor[k]for k in('device','inode','uid','mode')],'original0004 root identity differs')
        deps.preflight(path_of(refs['base_selection']),refs['base_selection']['sha256'])
        observed=deps.verify_installed(INSTALL,base);need(len(observed)==1010,'full original1010 required');exact(refs['base_receipt'])
    def output_bytes(path,mode):
        need(capture_output is not None,'selected output capture not initialized');out.guard()
        raw=capture_output(path,required_uid=os.getuid())
        need(control.capture(path,sha(raw),owner=os.getuid(),mode=mode)==raw,'fresh output bytes differ');out.guard();return raw
    try:
        out.emit('started.json',{'authority_effect':'none','selection_binding':selection_binding,'self_binding':self_binding,'started_utc':utc(),'commands':proposal['commands']})
        sys.path.insert(0,str(INSTALL/'deps'))
        for name in('checked_io','stage_io','closure'):loaded[name]=load(name,mods[name])
        deps=load('_T32_rust_dependencies',mods['dependencies']);guard=load('_T32_rust_api_guard',mods['api_guard'])
        capture_output=load('_T32_rust_output_capture',mods['output_capture']).capture_path
        base,_=deps.load_selection(path_of(refs['base_selection']),refs['base_selection']['sha256'])
        measure('entry-current-full28597-Source',lambda:guard.verify(SOURCE));exact(refs['profile'])
        measure('entry-full720-77ELF-1010-and-receipt',installed);measure('entry-complete-selected-inputs-and-cache65',lambda:(all_inputs(),cache_guard(initial=True)))
        for index,command in enumerate(proposal['commands'],1):
            configurations();out.guard()
            stdout=Path(command['stdout_path']);stderr=Path(command['stderr_path'])
            need(stdout.parent==stderr.parent==OWNED/'observations'and command['cwd']==str(ROOT),'original raw stream/cwd origin differs')
            streams=[];child=None;rc=None;timed_out=False;child_failure=None;stream_errors=[];termination_actions=[];cleanup_errors=[];residual_group=False;start=utc();mono=time.monotonic()
            try:
                for stream in(stdout,stderr):streams.append(out.create(stream.name))
                child=subprocess.Popen(command['argv'],cwd=command['cwd'],env=dict(command['environment']),stdin=subprocess.DEVNULL,stdout=streams[0],stderr=streams[1],close_fds=True,start_new_session=True)
                out.emit(command['id']+'.started.json',{'pid':child.pid,'process_group':child.pid,'started_utc':start,'argv':command['argv'],'environment':command['environment'],'cwd':command['cwd']})
                try:rc=child.wait(timeout=timeout)
                except subprocess.TimeoutExpired:timed_out=True;raise
            except BaseException:child_failure=diagnostic()
            finally:
                if child is not None:
                    try:
                        residual_group=group_alive(child.pid)
                        if residual_group:stop_owned_group(child,termination_actions)
                        need(child.poll()is not None and not group_alive(child.pid),'owned child/group not reaped')
                    except BaseException:cleanup_errors.append(diagnostic())
                if child is not None:rc=child.returncode
                for stream,fd in zip((stdout,stderr),streams):
                    try:out.finish(stream.name,fd)
                    except BaseException:stream_errors.append(diagnostic())
                    finally:os.close(fd)
                terminal={'id':command['id'],'pid':None if child is None else child.pid,'process_group':None if child is None else child.pid,'started_utc':start,'terminal_utc':utc(),'seconds':time.monotonic()-mono,'returncode':rc,'timed_out':timed_out,'failure':child_failure,'stream_errors':stream_errors,'termination_actions':termination_actions,'cleanup_errors':cleanup_errors,'group_remained_after_wait':residual_group,'owned_group_gone':child is not None and not group_alive(child.pid),'stdout':None,'stderr':None}
                for key,stream in(('stdout',stdout),('stderr',stderr)):
                    if os.path.lexists(stream):
                        try:raw=output_bytes(stream,0o600);terminal[key]={'path':str(stream),'sha256':sha(raw),'size_bytes':len(raw)}
                        except BaseException:stream_errors.append(diagnostic())
                events.append(terminal);out.emit(command['id']+'.terminal.json',terminal)
            need(child_failure is None and not stream_errors and not cleanup_errors and not residual_group and rc==0,'original command failed or left a process group; later commands remain unexecuted')
            raw=output_bytes(stdout,0o600)
            if index==1:need(b'rustc 1.98.1 'in raw and b'commit-hash: 48a229ceaefd4985c50990b14116b6d856af0985'in raw and b'host: x86_64-unknown-linux-gnu'in raw,'actual Rust report differs')
            if index==2:need(raw.startswith(b'cargo ')and b'host: x86_64-unknown-linux-gnu'in raw,'actual Cargo report missing')
            if index==4:accepted['original23']=test_accounting(raw,[name for names in original_inputs['original_test_names'].values()for name in names])
            if index in(3,5):
                expected=command['expected_outputs'][0];messages=[parse(line)for line in raw.splitlines()if line.startswith(b'{')]
                artifacts=[r for r in messages if r.get('reason')=='compiler-artifact'and r.get('executable')==expected and r.get('target',{}).get('name')=='lab-ontology-native']
                need(len(artifacts)==1 and artifacts[0]['target']['src_path']==str(path_of(cache['lock_binding']).parent/'src/main.rs')and artifacts[0]['fresh']is False and any(r.get('reason')=='build-finished'and r.get('success')is True for r in messages),'fresh selected source compiler artifact missing')
                body=output_bytes(expected,None);output_mode=stat.S_IMODE(Path(expected).stat(follow_symlinks=False).st_mode);need(output_mode&0o100,'built output not owner-executable')
                accepted[command['id']]={'path':expected,'sha256':sha(body),'size_bytes':len(body),'observed_mode':output_mode,'ELF':elf_metadata(body),'equals_current574':sha(body)=='57416d01d3479238f9e76a967c0275f1af04466efeb130fc0125bcb94e3a3399','artifact':artifacts[0]}
        accepted['two_fresh_binary_SHA_equal']=accepted['03-fresh-build']['sha256']==accepted['05-independent-target-build']['sha256']
    except BaseException:failure=diagnostic()
    finally:
        checks=[('exit-current-full28597-Source',lambda:need(guard is not None,'Source guard was not initialized')or guard.verify(SOURCE)),('exit-profile',lambda:exact(refs['profile'])),('exit-full720-77ELF-1010-and-receipt',installed),('exit-complete-selected-inputs-and-custody',all_inputs),('exit-cache65-config-custody',cache_guard)]
        for label,fn in checks:
            try:measure(label,fn)
            except BaseException:errors.append({'phase':label,**diagnostic()})
        result={'schema_version':'lab-T32-current-host-rust-observation/v1-candidate','authority_effect':'none','result':'PASS-bounded-current-host-observation'if failure is None and not errors and len(events)==5 else 'FAIL-preserved-owned-attempt','commands':events,'unexecuted_command_ids':[c['id']for c in proposal['commands'][len(events):]],'failure':failure,'exit_errors':errors,'phases':phases,'accepted_observations':accepted,'hermetic_or_complete_toolchain_closure_proved':False,'historical480_recovered':False,'all25_historical_missing_inputs_remain_REFUSED':True,'existing574_replaced':False,'migration_or_owner_or_whole_runtime_qualified':False}
        try:out.emit('result.json',result)
        finally:out.close()
    return 0 if result['result']=='PASS-bounded-current-host-observation'else 1

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--executor-sha256',required=True);parser.add_argument('--selection',required=True);parser.add_argument('--selection-sha256',required=True);args=parser.parse_args()
    need(Path(sys.executable)==INSTALL/'bin/python'and sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode,'selected0004 isolated -B -S executor required')
    raw=CONTROL.read_bytes();need(sha(raw)==CONTROL_SHA,'exact reviewed bootstrap helper differs')
    control=types.ModuleType('_T32_rust_capture');control.__file__=str(CONTROL);exec(compile(raw,str(CONTROL),'exec'),control.__dict__)
    need(control.capture(CONTROL,CONTROL_SHA)==raw,'bootstrap attachment changed')
    self_binding={'path':str(Path(__file__).absolute()),'sha256':args.executor_sha256};control.capture(path_of(self_binding),self_binding['sha256'])
    binding={'path':args.selection,'sha256':args.selection_sha256};selection=parse(control.capture(path_of(binding),binding['sha256']))
    return run(selection,binding,control,self_binding)
if __name__=='__main__':raise SystemExit(main())
