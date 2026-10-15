"""Pure path preparation candidate verification, no Lab runtime or mutation."""
import cProfile,hashlib,importlib.abc,importlib.util,json,os,re,stat,sys,time,uuid
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE=Path(__file__).absolute().parent
SELECTION_SHA='7fb19388d18d539a98690a821a07d9cb9a0b35313295f893251242651b5c6c0b'

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
    with (HERE/'benchmark-events.jsonl').open('a') as f:f.write(json.dumps(value,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
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
    import ast,tempfile,types
    candidate=selected_helper(selection['candidate_helper_binding']);oldcaller=selected_helper(selection['caller_contract_binding']);newcaller=selected_helper(selection['candidate_caller_binding']);checks=[]
    def passed(name,**details):checks.append({'case':name,'result':'PASS',**details})
    # Compare only ordinary inert metadata values. No live callback, code,
    # function globals, defaults or actual selected closure is changed.
    kw_cases=[None,{}, {'x':1},{'x':None},{'z':(), 'a':False},{'x':[]},{'x':{'nested':'value'}}]
    snapshots=[(),(('x',1),),(('x',None),),(('x',[]),),[],None]
    count=0
    for current in kw_cases:
        for recorded in snapshots:
            original=tuple(sorted((current or {}).items()))!=recorded
            new=(() if current is None else tuple(sorted((current or {}).items())))!=recorded
            need(original==new);count+=1
    passed('None-empty-and-content-different-keyword-dictionary-metadata-expression-parity',comparisons=count)
    names_cases=[{}, {'a':object()},{'a':1,'b':2},{'b':2,'c':3}];name_sets=[frozenset(),frozenset(['a']),frozenset(['a','b']),frozenset(['z'])]
    for namespace in names_cases:
        for names in name_sets:need((set(namespace)!=names)==(namespace.keys()!=names))
    passed('dictionary-keys-view-versus-captured-frozenset-names-exact-parity',comparisons=16)
    sentinels=[object(),object()]
    class Cell:
        def __init__(self,value):self.cell_contents=value
    class EmptyCell:
        @property
        def cell_contents(self):raise ValueError('inert empty metadata cell')
    current_closures=[None,(),(Cell(sentinels[0]),),(Cell(sentinels[1]),),(Cell(sentinels[0]),Cell(sentinels[1])),(EmptyCell(),)]
    recorded_cells=[(),(sentinels[0],),(sentinels[1],),(sentinels[0],sentinels[1])]
    def result(callback):
        try:return ('value',bool(callback()))
        except ValueError:return ('exception','ValueError')
    for closure in current_closures:
        for cells in recorded_cells:
            original=result(lambda:any(cell.cell_contents is not expected for cell,expected in zip(closure or (),cells)))
            new=result(lambda:cells and any(cell.cell_contents is not expected for cell,expected in zip(closure or (),cells)))
            need(original==new)
    passed('empty-present-content-different-and-empty-cell-metadata-closure-expression-parity',comparisons=24)
    old=ast.parse(exact(ROOT/selection['helper_binding']['path'],PIN));new=ast.parse(exact(ROOT/selection['candidate_helper_binding']['path'],selection['candidate_helper_binding']['sha256']))
    dump=lambda n:ast.dump(n,include_attributes=False)
    nodes=lambda t:{n.name:n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
    a=nodes(old);b=nodes(new);need(set(a)==set(b) and [n for n in a if dump(a[n])!=dump(b[n])]==['_check_integrity_state'])
    need([dump(n) for n in old.body if not isinstance(n,(ast.FunctionDef,ast.ClassDef))]==[dump(n) for n in new.body if not isinstance(n,(ast.FunctionDef,ast.ClassDef))])
    # Every preexisting guard/integrity call site remains at exactly its old AST.
    for name in ['selected','verify_all','capture_one','kernel_guard','kernel_digest','scope','Batch']:need(dump(a[name])==dump(b[name]))
    passed('only-helper-state-comparison-function-changes-all-row-hash-path-kernel-scope-attachment-cleanup-initializers-identical')
    oldc=ast.parse(exact(ROOT/selection['caller_contract_binding']['path'],selection['caller_contract_binding']['sha256']));newc=ast.parse(exact(ROOT/selection['candidate_caller_binding']['path'],selection['candidate_caller_binding']['sha256']))
    need(set(nodes(oldc))==set(nodes(newc))=={'select','check'})
    for name in ['select','check']:need(dump(nodes(oldc)[name].args)==dump(nodes(newc)[name].args))
    passed('companion-functions-and-signatures-retained-new-exact-sixfield-owned-contract-only')
    before=fd_count();contracts={}
    for label,module,caller,binding in [('baseline',K,oldcaller,selection['helper_binding']),('candidate',candidate,newcaller,selection['candidate_helper_binding'])]:
        contract=caller.select(module,expected_path=ROOT/binding['path'],expected_sha256=binding['sha256']);caller.check(contract,module);contracts[label]=contract
        need(len(contract)==(5 if label=='baseline' else 6));need(module._CALLBACKS[9] is module.kernel_guard)
        passed(label+'-true-origin-loader-and-external-held-code-context-contract')
        with tempfile.TemporaryDirectory(prefix='owned-inert-metadata-',dir=HERE) as folder:
            root=Path(folder);data=b'own ordinary metadata fixture\n';leaf=root/'file';leaf.write_bytes(data);row={'path':'file','sha256':sha(data)}
            need(module.capture_one(root,row,code_sha256=binding['sha256'])==data)
            need(module.verify_all(root,[row],code_sha256=binding['sha256'])==1)
            absolute={'path':str(leaf),'sha256':sha(data)};need(module.capture_one(root,absolute,code_sha256=binding['sha256'],selected_external=[absolute])==data)
            for rows in [[row,row],[{**row,'sha256':'0'*64}],[{**row,'extra':False}]]:
                try:module.verify_all(root,rows,code_sha256=binding['sha256'])
                except ValueError:pass
                else:raise AssertionError('original metadata refusal missing')
            need(not module._ACTIVE.value);caller.check(contract,module)
        passed(label+'-normal-owned-capture-all-rows-external-and-closed-hash-duplicate-refusals')
    deps_entry=dependency_guard();rows=closed_inputs();need(K.verify_all(ROOT,rows,code_sha256=PIN)==1310)
    need(candidate.verify_all(ROOT,rows,code_sha256=selection['candidate_helper_binding']['sha256'])==1310)
    for label,module,caller in [('baseline',K,oldcaller),('candidate',candidate,newcaller)]:caller.check(contracts[label],module)
    deps_exit=dependency_guard();need(deps_entry==deps_exit and before==fd_count())
    passed('fresh-explicit1310-public-source-and1010-installed-dependency-entryexit-zero-descriptor-delta')
    for p in HERE.glob('*.py'):ast.parse(p.read_bytes())
    value={'schema_version':'lab-T03-comparison-preparation-controls/v1-candidate','authority_effect':'none','result':'PASS-normal-metadata-and-owned-files-only','checks':checks,'count':len(checks),'helper_binding':selection['helper_binding'],'candidate_helper_binding':selection['candidate_helper_binding'],'candidate_caller_binding':selection['candidate_caller_binding'],'source_selection_sha256':SELECTION_SHA,'dependency_entry':deps_entry,'dependency_exit':deps_exit,'fresh_source_rows_each_helper':1310,'descriptor_delta':0,'original_callbacks_clocks_codeobjects_or_globals_mutated':False,'Lab_native_Source_reader_mapper_Context_Service_Session_or_lease_constructed':False,'task_complete':False}
    save('controls-result.json',value);print(json.dumps({'result':value['result'],'checks':len(checks),'descriptor_delta':0}))
if __name__=='__main__':main()
