"""Synthetic contract controls only; no real Source or authority/runtime proof."""
import ast,copy,hashlib,importlib.abc,importlib.util,json,os,stat,sys,threading,types,uuid
from contextlib import contextmanager
from pathlib import Path

ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');HERE=Path(__file__).absolute().parent
SELECTION_SHA='708602b3b28e5ec5947dad257c054353663daf610faa13ceb9808dc69ef222e8'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def require(value,reason='synthetic fixture differs'):
    if not value:raise ValueError(reason)
def encoded(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def stamp(s):return (s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def did(s):return (s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid)
def exact(path,pin):
    handles=[];links=[]
    try:
        parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);handles.append(parent)
        for part in path.parts[1:-1]:
            child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent);handles.append(child);links.append((parent,part,child,did(os.fstat(child))));parent=child
        fd=os.open(path.name,os.O_RDONLY|os.O_NONBLOCK|os.O_NOFOLLOW,dir_fd=parent);handles.append(fd);before=os.fstat(fd);require(stat.S_ISREG(before.st_mode));chunks=[]
        while chunk:=os.read(fd,1048576):chunks.append(chunk)
        raw=b''.join(chunks);require(stamp(before)==stamp(os.fstat(fd))==stamp(os.stat(path.name,dir_fd=parent,follow_symlinks=False)))
        for parent,part,held,expected in links:require(did(os.stat(part,dir_fd=parent,follow_symlinks=False))==did(os.fstat(held))==expected)
        require(sha(raw)==pin);return raw
    finally:
        for fd in reversed(handles):os.close(fd)

selection=json.loads(exact(HERE/'input-selection.json',SELECTION_SHA))
def binding_raw(binding):return exact(ROOT/binding['path'],binding['sha256'])
def captured(binding):
    path=ROOT/binding['path'];raw=binding_raw(binding)
    class Loader(importlib.abc.SourceLoader):
        selected_source_sha256=binding['sha256']
        def get_filename(self,name):return str(path)
        def get_data(self,name):require(name==str(path));return raw
        def get_code(self,name):return compile(raw,str(path),'exec',dont_inherit=True)
    name='_cal_pure_snapshot_fixture_'+uuid.uuid4().hex;spec=importlib.util.spec_from_file_location(name,path,loader=Loader());module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module

def dependency_guard():
    dep=json.loads(binding_raw(selection['dependency_selection_binding']));install=ROOT/selection['installation_path']
    expected={r['destination']:{'sha256':r['sha256'],'size_bytes':r['size_bytes'],'mode':0o755 if r['kind'] in {'interpreter','native-executable'} else 0o644} for r in dep['inputs']};expected.update(dep['wheel_members']);expected['lib/abi/ld-linux-x86-64.so.2']['mode']=0o755;require(len(expected)==1010)
    for name,row in expected.items():
        p=install/name;s=p.lstat();require(stat.S_ISREG(s.st_mode) and s.st_uid==os.getuid() and stat.S_IMODE(s.st_mode)==row['mode'] and s.st_size==row['size_bytes']);exact(p,row['sha256'])
    actual=set()
    for directory,dirs,files in os.walk(install,followlinks=False):
        for name in dirs+files:require(not (Path(directory)/name).is_symlink())
        actual.update(str((Path(directory)/name).relative_to(install)) for name in files)
    require(actual==set(expected)|{'installation.json'});return 1010

def entry_function(binding):
    # Compile exactly the independently selected function AST at its true file
    # origin; API imports/constructors never execute. Globals are explicitly
    # synthetic fixtures, so these controls cannot qualify production globals.
    tree=ast.parse(binding_raw(binding));node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='participation_snapshot')
    namespace={'contextmanager':contextmanager,'copy':copy,'source':types.SimpleNamespace(require=require,encoded=encoded,parse=json.loads)}
    exec(compile(ast.Module(body=[node],type_ignores=[]),str(ROOT/binding['path']),'exec'),namespace)
    return namespace['participation_snapshot']

class SyntheticSchema:
    carrier_ref='cal.artifact-type.synthetic-fixture/v1'
    original_schema=b'{"type":"object","required":["marker"],"properties":{"marker":{"const":"synthetic"}},"additionalProperties":false}'
    def validator(self):
        from jsonschema import Draft202012Validator
        return Draft202012Validator(json.loads(self.original_schema))

class SyntheticExactSources:
    created=0
    def __init__(self,scope_ref,source_cut,records,schemas,current_guard):
        type(self).created+=1;self.scope_ref=scope_ref;self.source_cut=copy.deepcopy(source_cut);self.records={r['ref']:copy.deepcopy(r) for r in records};self.schemas={s.carrier_ref:s for s in schemas};self.validators={k:s.validator() for k,s in self.schemas.items()};self.current_guard=current_guard;self.guard()
    def guard(self):require(self.current_guard() is True)
    def get(self,ref):
        self.guard();row=self.records[ref];require(sha(row['raw'])==row['sha256']);self.validators[SyntheticSchema.carrier_ref].validate(json.loads(row['raw']));return copy.deepcopy(row)

class SyntheticSignedSources:
    def __init__(self):
        self.guard_calls=0;self.fail_call=None;self.closed=False;self.source_cut={'synthetic-cut':'fixture-1'}
        self.sources=types.SimpleNamespace(scope_ref='project:synthetic',source_cut=copy.deepcopy(self.source_cut),records={'fixture:1':{'ref':'fixture:1','raw':b'{"marker":"synthetic"}','sha256':sha(b'{"marker":"synthetic"}')}},schemas={SyntheticSchema.carrier_ref:SyntheticSchema()},current_guard=self.guard)
    def guard(self):
        self.guard_calls+=1
        if self.fail_call==self.guard_calls:raise ValueError('synthetic full guard failure')
        require(not self.closed);return True
    @staticmethod
    def record_stamp(rows):return encoded([{'ref':r['ref'],'actual_sha':sha(r['raw']),'expected_sha':r['sha256']} for r in rows])
    @staticmethod
    def schema_stamp(rows):return encoded([{'carrier':r.carrier_ref,'raw_sha':sha(r.original_schema)} for r in rows])

class SyntheticChannel:
    def __init__(self,parent):self.source=parent;self.guard_calls=0
    def guard(self):self.guard_calls+=1;return True

def fixture(kernel):
    parent=SyntheticSignedSources();channel=SyntheticChannel(parent);EL=types.SimpleNamespace(ExactSources=SyntheticExactSources,parse=json.loads)
    adapter=types.SimpleNamespace(SignedSources=SyntheticSignedSources,eligibility=EL);delivery=types.SimpleNamespace(reader=types.SimpleNamespace(adapter=adapter),EL=EL,FACT_SCOPE=kernel,encoded=encoded)
    return parent,channel,delivery

def main():
    before=len(os.listdir('/proc/self/fd'));deps_entry=dependency_guard();sys.path.insert(0,str(ROOT/selection['installation_path']/'deps'))
    original=entry_function(selection['preimage_binding']);candidate=entry_function(selection['candidate_binding']);kernel=captured(selection['facts_scope_bindings'][0]);cases=[]
    def passed(label,**extra):cases.append({'case':label,'result':'PASS-synthetic-contract-only',**extra})
    def refused(label,fn):
        try:fn()
        except ValueError:passed(label);return
        raise AssertionError('expected synthetic contract refusal')
    tree_a=ast.parse(binding_raw(selection['preimage_binding']));tree_b=ast.parse(binding_raw(selection['candidate_binding']));items=lambda tree:{n.name:ast.dump(n,include_attributes=False) for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
    a=items(tree_a);b=items(tree_b);require([name for name in a if a[name]!=b[name]]==['participation_snapshot']);require([ast.dump(n,include_attributes=False) for n in tree_a.body if not isinstance(n,(ast.FunctionDef,ast.ClassDef))]==[ast.dump(n,include_attributes=False) for n in tree_b.body if not isinstance(n,(ast.FunctionDef,ast.ClassDef))]);passed('only-participation-snapshot-AST-changed')
    for label,fn in [('original',original),('candidate',candidate)]:
        parent,channel,D=fixture(kernel);n=SyntheticExactSources.created
        with fn(parent,D) as facts:
            require(facts.get('fixture:1')['raw']==b'{"marker":"synthetic"}');require(facts is not parent.sources)
        require(parent.guard_calls==3 and SyntheticExactSources.created==n+1);passed(label+'-absent-scope-generic-copy-three-full-guards')
        refused(label+'-generic-copy-closed-after-exit',facts.guard)
        parent,channel,D=fixture(kernel)
        try:
            with fn(parent,D):raise RuntimeError('synthetic consumer failure')
        except RuntimeError:pass
        require(parent.guard_calls==3);passed(label+'-generic-consumer-exception-full-exit')
    parent,channel,D=fixture(kernel)
    with kernel.read_scope(parent,D.EL,channel,producer=D) as outer:
        n=SyntheticExactSources.created;guards=parent.guard_calls
        with original(parent,D) as original_copy:require(original_copy is not outer and original_copy.get('fixture:1')['raw']==b'{"marker":"synthetic"}')
        require(parent.guard_calls-guards==3 and SyntheticExactSources.created==n+1 and kernel.active_scope().snapshot is outer);passed('original-active-scope-still-builds-second-copy-three-full-guards')
        n=SyntheticExactSources.created;guards=parent.guard_calls
        with candidate(parent,D) as facts:require(facts is outer and facts.get('fixture:1')['raw']==b'{"marker":"synthetic"}')
        require(parent.guard_calls-guards==3 and SyntheticExactSources.created==n and kernel.active_scope().snapshot is outer);outer.guard();passed('borrowed-exact-existing-copy-three-full-guards-no-new-validator-copy-no-close')
        guards=parent.guard_calls
        try:
            with candidate(parent,D) as facts:raise RuntimeError('synthetic consumer failure')
        except RuntimeError:pass
        require(parent.guard_calls-guards==3 and kernel.active_scope().snapshot is outer);passed('borrowed-consumer-exception-full-exit-outer-preserved')
        wrong=SyntheticSignedSources();refused('conflicting-active-parent-fails-closed',lambda:_consume(candidate,wrong,D));require(wrong.guard_calls==2 and kernel.active_scope().snapshot is outer);passed('conflicting-parent-still-full-exit-without-generic-fallback')
        other=copy.copy(D);guards=parent.guard_calls;refused('conflicting-producer-fails-closed',lambda:_consume(candidate,parent,other));require(parent.guard_calls-guards==2);passed('producer-refusal-full-exit')
        other=copy.copy(D);other.EL=types.SimpleNamespace(ExactSources=SyntheticExactSources,parse=json.loads);refused('conflicting-eligibility-fails-closed',lambda:_consume(candidate,parent,other))
        thread_observations=[]
        def worker():
            try:
                with candidate(parent,D) as facts:thread_observations.append(facts is not outer)
            except BaseException as error:thread_observations.append(type(error).__name__)
        thread=threading.Thread(target=worker);thread.start();thread.join();require(thread_observations==[True] and kernel.active_scope().snapshot is outer);passed('other-thread-does-not-borrow-main-thread-copy')
        # Invalid synthetic copy metadata is confined to this newly owned
        # fixture. Production function objects/callbacks are never rewritten.
        own=outer.records['fixture:1'];old_raw=own['raw'];own['raw']=b'{"marker":"changed"}';guards=parent.guard_calls
        refused('changed-synthetic-copied-record-fails-before-borrow',lambda:_consume(candidate,parent,D));require(parent.guard_calls-guards==2);own['raw']=old_raw;outer.guard();passed('copied-record-refusal-full-exit-and-owned-fixture-restored')
        old_cut=copy.deepcopy(outer.source_cut);outer.source_cut={'synthetic-cut':'other'};refused('changed-synthetic-cut-fails-closed',lambda:_consume(candidate,parent,D));outer.source_cut=old_cut;outer.guard()
        require(kernel.active_scope().snapshot is outer);passed('nested-helper-never-clears-registered-outer-copy')
    require(kernel.active_scope() is None);passed('only-outer-owner-clears-registry-and-closes-copy')
    refused('borrowed-copy-closes-only-after-outer-exit',outer.guard)
    parent,channel,D=fixture(kernel)
    with kernel.read_scope(parent,D.EL,channel,producer=D) as outer:
        guards=parent.guard_calls;parent.fail_call=guards+2
        refused('second-full-parent-guard-failure-retains-final-full-guard',lambda:_consume(candidate,parent,D));require(parent.guard_calls-guards==3);parent.fail_call=None;outer.guard()
    deps_exit=dependency_guard();require(len(os.listdir('/proc/self/fd'))==before)
    report={'schema_version':'lab-T03-participation-snapshot-reuse-synthetic-controls/v1-candidate','result':'PASS-synthetic-contract-controls-production-composition-pending','checks':cases,'case_count':len(cases),'input_selection_sha256':SELECTION_SHA,'candidate_binding':selection['candidate_binding'],'preimage_binding':selection['preimage_binding'],'dependency_entry_rows':deps_entry,'dependency_exit_rows':deps_exit,'file_descriptor_delta':0,'actual_original_v1_scope_algorithm_used_with_synthetic_Source_EL_channel_fixtures':True,'full_API_module_import_or_real_native_Source_reader_Context_Service_Session_constructor':False,'selected_function_AST_compiled_with_explicit_synthetic_globals':True,'real_family_source_permission_or_admission_proven':False,'original_functions_primitives_clocks_or_shared_registry_replaced':False,'raw_private_body_reads':False,'no_lease_or_cross_invocation_cache':True,'production_composition_equivalence_qualified':False,'authority_effect':'none','whole_API_qualified':False,'task_complete':False}
    p=HERE/'controls-result-0002.json'
    with p.open('x') as f:json.dump(report,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'result':report['result'],'cases':len(cases),'sha256':sha(p.read_bytes()),'dependency_entry_exit_rows':1010}))

def _consume(fn,parent,D):
    with fn(parent,D):pass

if __name__=='__main__':main()
