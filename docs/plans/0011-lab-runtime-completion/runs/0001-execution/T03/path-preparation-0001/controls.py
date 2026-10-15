"""Pure path preparation candidate verification, no Lab runtime or mutation."""
import cProfile,hashlib,importlib.abc,importlib.util,json,os,re,stat,sys,time,uuid
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE=Path(__file__).absolute().parent
SELECTION_SHA='2f686bac96fa89d17be3acc7ecbc0f9e9eebfc68ccebcacdd103ffaf6ff2faef'

def need(value):
    if not value:raise ValueError('selected technical benchmark input differs')

def sha(raw):return hashlib.sha256(raw).hexdigest()
def stamp(s):return (s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def directory(s):return (s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid)
def exact(path,pin):
    """Capture the independently pinned bootstrap before executing its bytes."""
    handles=[];links=[]
    try:
        parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);handles.append(parent)
        for part in path.parts[1:-1]:
            child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent);handles.append(child)
            links.append((parent,part,child,directory(os.fstat(child))));parent=child
        fd=os.open(path.name,os.O_RDONLY|os.O_NONBLOCK|os.O_NOFOLLOW,dir_fd=parent);handles.append(fd);before=os.fstat(fd)
        need(stat.S_ISREG(before.st_mode));parts=[]
        while chunk:=os.read(fd,1024*1024):parts.append(chunk)
        raw=b''.join(parts)
        need(stamp(before)==stamp(os.fstat(fd))==stamp(os.stat(path.name,dir_fd=parent,follow_symlinks=False)))
        for parent,part,held,expected in links:need(directory(os.stat(part,dir_fd=parent,follow_symlinks=False))==directory(os.fstat(held))==expected)
        need(sha(raw)==pin);return raw
    finally:
        for fd in reversed(handles):os.close(fd)

selection=json.loads(exact(HERE/'input-selection.json',SELECTION_SHA))
helper=selection['helper_binding'];kernel=ROOT/helper['path'];PIN=helper['sha256'];code=exact(kernel,PIN)
class CapturedLoader(importlib.abc.SourceLoader):
    selected_source_sha256=PIN
    def get_filename(self,name):return str(kernel)
    def get_data(self,path):need(path==str(kernel));return code
    def get_code(self,name):return compile(code,str(kernel),'exec',dont_inherit=True)
name='_cal_T03_normal_verification_cost_'+uuid.uuid4().hex
spec=importlib.util.spec_from_file_location(name,kernel,loader=CapturedLoader());K=importlib.util.module_from_spec(spec);sys.modules[name]=K;spec.loader.exec_module(K)

def closed_inputs():
    need(sha(exact(HERE/'input-selection.json',SELECTION_SHA))==SELECTION_SHA)
    manifest=selection['source_manifest_binding']
    raw=K.capture_one(ROOT,manifest,code_sha256=PIN)
    rows=json.loads(raw)['files'];need(rows==selection['source_rows'] and len(rows)==1310)
    for r in selection['source_metadata']:
        p=ROOT/r['path'];s=p.lstat();need(stat.S_ISREG(s.st_mode) and s.st_size==r['size_bytes'] and stat.S_IMODE(s.st_mode)==r['mode'])
    return rows

def dependency_guard():
    binding=selection['dependency_selection_binding'];raw=K.capture_one(ROOT,binding,code_sha256=PIN);deps=json.loads(raw)
    expected={r['destination']:{'sha256':r['sha256'],'size_bytes':r['size_bytes'],'mode':0o755 if r['kind'] in {'interpreter','native-executable'} else 0o644} for r in deps['inputs']}
    expected.update(deps['wheel_members']);expected['lib/abi/ld-linux-x86-64.so.2']['mode']=0o755;need(len(expected)==1010)
    install=ROOT/selection['installation_path'];need(install.stat().st_uid==os.getuid() and stat.S_IMODE(install.stat().st_mode)==0o700)
    installed=[]
    for name,row in expected.items():
        p=install/name;s=p.lstat();need(stat.S_ISREG(s.st_mode) and s.st_uid==os.getuid() and stat.S_IMODE(s.st_mode)==row['mode'] and s.st_size==row['size_bytes'])
        installed.append({'path':str(p.relative_to(ROOT)),'sha256':row['sha256']})
    actual=set()
    for current,dirs,files in os.walk(install,followlinks=False):
        for name in dirs+files:need(not (Path(current)/name).is_symlink())
        actual.update(str((Path(current)/name).relative_to(install)) for name in files)
    need(actual==set(expected)|{'installation.json'})
    count=K.verify_all(ROOT,installed,code_sha256=PIN);need(count==1010)
    return {'fresh_installed_file_rows':count,'selection_sha256':binding['sha256'],'installed_bytes':sum(r['size_bytes'] for r in expected.values())}

def save(name,value):
    p=HERE/name
    with p.open('x') as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    return {'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes())}

def event(value):
    value={'observed_at':datetime.now(timezone.utc).isoformat(),**value}
    with (HERE/'events.jsonl').open('a') as f:f.write(json.dumps(value,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(value,sort_keys=True),flush=True)

def fd_count():return len(list(Path('/proc/self/fd').iterdir()))

def selected_helper(binding):
    path=ROOT/binding['path'];raw=exact(path,binding['sha256'])
    class Loader(importlib.abc.SourceLoader):
        selected_source_sha256=binding['sha256']
        def get_filename(self,name):return str(path)
        def get_data(self,filename):need(filename==str(path));return raw
        def get_code(self,name):return compile(raw,str(path),'exec',dont_inherit=True)
    name='_cal_T03_backend_cost_defensive_'+uuid.uuid4().hex
    spec=importlib.util.spec_from_file_location(name,path,loader=Loader());m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def main():
    import ast,tempfile
    from pathlib import PurePosixPath
    candidate=selected_helper(selection['candidate_helper_binding']);companion=selected_helper(selection['caller_contract_binding']);pin=selection['candidate_helper_binding']['sha256'];cases=[];before=fd_count();deps_entry=dependency_guard();rows=closed_inputs();need(K.verify_all(ROOT,rows,code_sha256=PIN)==1310)
    def passed(label,**metadata):cases.append({'case':label,'result':'PASS',**metadata})
    def refused(label,callback):
        try:callback()
        except (ValueError,OSError):passed(label);return
        raise AssertionError('expected bounded fixture refusal')
    # Compare actual immutable original selector, including prepared-root and
    # backward-compatible root-string calls, without changing any functions.
    selectors=[{'path':p,'sha256':'a'*64} for p in ['a','a/b','a/.b','/a','//a','//','///a','a//b','a/./b','../a','a/../b','.','/','','a/','a\\b','a\0b']]
    selectors += [None,[],{}, {'path':'a','sha256':'A'*64},{'path':'a','sha256':'0'*63},{'path':1,'sha256':'0'*64},{'path':'a','sha256':'0'*64,'extra':False}]
    roots=['/','//','/tmp','//tmp','/tmp//nested','.','relative','relative/..']
    def outcome(fn):
        try:return ('value',fn())
        except (ValueError,TypeError,AttributeError) as error:return ('exception',type(error).__name__)
    for root in roots:
        for row in selectors:
            for external in [(),[row]]:
                original=outcome(lambda:K.selected(root,row,external))
                direct=outcome(lambda:candidate.selected(root,row,external));prepared=outcome(lambda:candidate.selected(PurePosixPath(root),row,external))
                need(original==direct==prepared)
    passed('actual-selector-parity-valid-invalid-external-double-slash-and-relative-root',roots=len(roots),selectors=len(selectors),external_variants=2,comparisons=len(roots)*len(selectors)*2)
    old=ast.parse(exact(ROOT/selection['helper_binding']['path'],PIN));new=ast.parse(exact(ROOT/selection['candidate_helper_binding']['path'],pin))
    functions=lambda module:{n.name:ast.dump(n,include_attributes=False) for n in module.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
    a=functions(old);b=functions(new);need([name for name in a if a[name]!=b[name]]==['selected','verify_all','capture_one'])
    need([ast.dump(n,include_attributes=False) for n in old.body if not isinstance(n,(ast.FunctionDef,ast.ClassDef))]==[ast.dump(n,include_attributes=False) for n in new.body if not isinstance(n,(ast.FunctionDef,ast.ClassDef))])
    passed('all-other-helper-AST-global-state-and-kernel-index9-preserved')
    contracts={}
    for label,module,binding in [('baseline',K,selection['helper_binding']),('candidate',candidate,selection['candidate_helper_binding'])]:
        contract=companion.select(module,expected_path=ROOT/binding['path'],expected_sha256=binding['sha256']);companion.check(contract,module);contracts[label]=contract
        passed(label+'-independent-caller-held-contract')
    # Audit only owned fixture open names in this controls process. No hook is
    # installed in the separately executed timing process and no callback is
    # replaced. The observed order comes from actual verify_all file opens.
    observed=[];audit_enabled=[False]
    def audit(event,args):
        if audit_enabled[0] and event=='open' and isinstance(args[0],str) and args[0] in ['case-a','case-b']:observed.append(args[0])
    sys.addaudithook(audit)
    for label,module,binding in [('baseline',K,selection['helper_binding']),('candidate',candidate,selection['candidate_helper_binding'])]:
        selected_pin=binding['sha256']
        with tempfile.TemporaryDirectory(prefix='cal-T03-path-prep-'+label+'-') as tmp:
            root=Path(tmp);(root/'branch').mkdir();data_a=b'bounded fixture a\n'*2048;data_b=b'bounded fixture b\n'*1024
            a=root/'branch/case-a';b=root/'branch/case-b';a.write_bytes(data_a);b.write_bytes(data_b)
            row_a={'path':'branch/case-a','sha256':sha(data_a)};row_b={'path':'branch/case-b','sha256':sha(data_b)}
            need(module.capture_one(root,row_a,code_sha256=selected_pin)==data_a);passed(label+'-capture-exact-owned-bytes')
            observed.clear();audit_enabled[0]=True
            try:need(module.verify_all(root,[row_b,row_a],code_sha256=selected_pin)==2)
            finally:audit_enabled[0]=False
            need(observed==['case-b','case-a']);passed(label+'-actual-row-open-order-preserved')
            refused(label+'-duplicate-row',lambda:module.verify_all(root,[row_a,row_a],code_sha256=selected_pin))
            absolute={'path':str(a),'sha256':sha(data_a)}
            refused(label+'-unselected-external',lambda:module.capture_one(root,absolute,code_sha256=selected_pin))
            need(module.capture_one(root,absolute,code_sha256=selected_pin,selected_external=[absolute])==data_a);passed(label+'-explicit-external-capture')
            refused(label+'-relative-absolute-same-locator-alias',lambda:module.verify_all(root,[row_a,absolute],code_sha256=selected_pin,selected_external=[absolute]))
            refused(label+'-wrong-file-digest',lambda:module.capture_one(root,{**row_a,'sha256':'0'*64},code_sha256=selected_pin))
            refused(label+'-wrong-helper-pin',lambda:module.capture_one(root,row_a,code_sha256='0'*64))
            refused(label+'-noncanonical-root',lambda:module.verify_all(str(root)+'/',[row_a],code_sha256=selected_pin))
            def nested():
                with module.scope(root,selected_pin):
                    with module.scope(root,selected_pin):pass
            refused(label+'-nested-batch',nested);need(not module._ACTIVE.value);passed(label+'-nested-refusal-clears-scope')
            def leaf_replace(same):
                with module.scope(root,selected_pin) as batch:
                    need(batch.read(a.parts[1:],sha(data_a))==data_a)
                    q=root/'replacement';q.write_bytes(data_a if same else b'changed owned fixture');os.replace(q,a)
            refused(label+'-same-byte-leaf-replacement',lambda:leaf_replace(True));a.write_bytes(data_a)
            refused(label+'-different-byte-leaf-replacement',lambda:leaf_replace(False));a.write_bytes(data_a)
            def parent_replace():
                with module.scope(root,selected_pin) as batch:
                    batch.read(a.parts[1:],sha(data_a));(root/'branch').rename(root/'old-branch');(root/'branch').mkdir();a.write_bytes(data_a)
            refused(label+'-owned-ancestor-replacement',parent_replace)
            def exceptional():
                with module.scope(root,selected_pin) as batch:
                    batch.read(a.parts[1:],sha(data_a));raise RuntimeError('owned control exception')
            try:exceptional()
            except RuntimeError:passed(label+'-exceptional-owned-scope-cleanup')
            need(not module._ACTIVE.value);companion.check(contracts[label],module);passed(label+'-held-integrity-current-after-filesystem-controls')
    need(K.verify_all(ROOT,closed_inputs(),code_sha256=PIN)==1310);need(candidate.verify_all(ROOT,closed_inputs(),code_sha256=pin)==1310);deps_exit=dependency_guard();need(fd_count()==before);passed('all-owned-directories-removed-and-zero-FD-delta')
    report={'schema_version':'lab-T03-path-preparation-pure-controls/v1-candidate','result':'PASS-bounded-selector-and-filesystem-controls','checks':cases,'case_count':len(cases),'input_selection_sha256':SELECTION_SHA,'baseline_binding':selection['helper_binding'],'candidate_binding':selection['candidate_helper_binding'],'source_entry_exit_rows':1310,'candidate_full1310_table_verified':True,'dependency_entry':deps_entry,'dependency_exit':deps_exit,'file_descriptor_delta':0,'function_primitive_clock_or_original_module_mutation':False,'private_or_native_Lab_runtime_or_lease_executed':False,'owned_filesystem_fixture_replacement_only':True,'authority_effect':'none','task_complete':False,'whole_API_qualified':False}
    binding=save('controls-result.json',report);event({'event':'controls-terminal','result':report['result'],'result_binding':binding,'case_count':len(cases)})

if __name__=='__main__':main()

