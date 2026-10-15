"""Root-only focused complete14 Machine runner; not final qualification."""
import argparse,ast,hashlib,importlib.util,json,os,re,stat,sys,types,unittest,uuid
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE=Path(__file__).absolute().parent
API='product/lab/release-candidates/v1/interface/api-integration-v17'
INSTALL='product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
DEP='docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json'
SOURCE='ee969cc8c6b539aa3247d81c82322cb9e7aefd42188d63db0195e381cdad4cb1'
PROFILE='9c8c3018226abb9077c6a99ee3cbc9dd0174c148b332b9488fd4a3a9cd30418b'
DEP_SHA='2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'
ROLES={'runner':'run_machine_development_v3.py','tests':'owned_machine_tests.py','observer':'owned_observer.py','output':'owned_output.py','capture':'capture.py','parent':'owned_parent_sessions.py'}
FIELDS={'schema_version','authority_effect','mode','api_source_binding','api_profile_binding','dependency_selection_binding','dependency_installation','owned_code_bindings','original_bindings','output_custody','runtime_coordinator_receipt_binding','expected_tests','expected_operations','original_source_expiry','max_session_seconds','final_qualification'}
def need(ok,reason):
    if not ok:raise ValueError(reason)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def parse(raw):
    def pairs(items):
        out={}
        for k,v in items:need(k not in out,'duplicate JSON key');out[k]=v
        return out
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:need(False,'nonfinite JSON'))
def binding(row):
    need(type(row)is dict and set(row)=={'path','sha256'},'closed binding required')
    p=row['path'];need(type(p)is str and p and '\\' not in p and '\0' not in p and Path(p).as_posix()==p and not Path(p).is_absolute() and '..' not in Path(p).parts and p!='.','canonical relative origin required')
    need(type(row['sha256'])is str and re.fullmatch('[a-f0-9]{64}',row['sha256']),'independent SHA required')
def capture_path(path,expected_sha256=None,*,maximum=32*1024*1024,required_uid=None):
    path=Path(path)
    need(path.is_absolute() and '..' not in path.parts and path.as_posix()==str(path),'canonical absolute captured origin required')
    need(expected_sha256 is None or type(expected_sha256)is str and re.fullmatch('[a-f0-9]{64}',expected_sha256),'independent exact capture SHA required')
    need(type(maximum)is int and 0<maximum<=32*1024*1024,'bounded capture required')
    handles=[];links=[]
    def directory_identity(s):return (s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode)
    def stamp(s):return (*directory_identity(s),s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    try:
        parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC);handles.append(parent)
        for part in path.parts[1:-1]:
            child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent);handles.append(child)
            selected=directory_identity(os.fstat(child))
            need(directory_identity(os.stat(part,dir_fd=parent,follow_symlinks=False))==selected,'capture ancestor detached while opening')
            links.append((parent,part,child,selected));parent=child
        leaf_parent=parent
        fd=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=leaf_parent);handles.append(fd);before=os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_size<=maximum,'bounded regular captured input required')
        need(required_uid is None or before.st_uid==required_uid,'captured input owner differs')
        parts=[];total=0
        while block:=os.read(fd,min(1024*1024,maximum-total+1)):
            total+=len(block);need(total<=before.st_size and total<=maximum,'captured input grew');parts.append(block)
        raw=b''.join(parts)
        need(total==before.st_size and stamp(before)==stamp(os.fstat(fd))==stamp(os.stat(path.name,dir_fd=leaf_parent,follow_symlinks=False)),'captured file changed/detached')
        need(expected_sha256 is None or hashlib.sha256(raw).hexdigest()==expected_sha256,'independent captured input digest differs')
        for ancestor,name,held,selected in links:
            need(directory_identity(os.stat(name,dir_fd=ancestor,follow_symlinks=False))==directory_identity(os.fstat(held))==selected,'held capture ancestor detached')
        need(stamp(before)==stamp(os.fstat(fd))==stamp(os.stat(path.name,dir_fd=leaf_parent,follow_symlinks=False)),'capture leaf changed before return')
        return raw
    finally:
        for fd in reversed(handles):os.close(fd)

def exact(row):
    binding(row);p=ROOT/row['path'];return capture_path(p,row['sha256'])

def shape(p):
    need(type(p)is dict and set(p)==FIELDS,'closed execution selection required')
    need(p['schema_version']=='lab-T05-owned-machine-development/v3-candidate' and p['authority_effect']=='none' and p['mode']=='focused-development-complete14' and p['final_qualification'] is False,'focused development only')
    need(p['api_source_binding']=={'path':API+'/source-manifest.json','sha256':SOURCE} and p['api_profile_binding']=={'path':API+'/contract-profile.json','sha256':PROFILE},'independently supplied final API pins differ')
    need(p['dependency_selection_binding']=={'path':DEP,'sha256':DEP_SHA} and p['dependency_installation']==INSTALL,'exact installed0004 selection required')
    need(p['expected_tests']==14 and type(p['expected_tests'])is int and p['expected_operations']==['lab.status','catalog.get','artifact.inspect','artifact.query','context.get','session.inspect','operation.inspect'],'complete original14/seven selection required')
    need(p['original_source_expiry']=='2026-10-15T04:24:34.499247+00:00' and p['max_session_seconds']==900 and type(p['max_session_seconds'])is int,'original periods/bounds unchanged')
    need(type(p['owned_code_bindings'])is dict and set(p['owned_code_bindings'])==set(ROLES),'closed owned code required')
    for role,leaf in ROLES.items():
        r=p['owned_code_bindings'][role];binding(r);need(ROOT/r['path']==HERE/leaf,'true owned code origin required')
    need(type(p['original_bindings'])is dict and set(p['original_bindings'])=={'original_tests','parent_tests','original_observer','machine_helper','dependency_control','legacy_period','api_guard','api_bootstrap'},'closed original inputs required')
    for r in p['original_bindings'].values():binding(r)
    original_paths={'original_tests':API+'/test_machine_transport.py','parent_tests':API+'/test_custody_sessions.py','original_observer':API+'/fixture_observation.py','machine_helper':'product/lab/release-candidates/v1/interface/machine-context-scope-v2-completion-0001/generation.py','dependency_control':'product/lab/release-candidates/v1/interface/composite-operator-v1-completion-0001/revision-0003/control.py','legacy_period':'product/lab/release-candidates/v1/interface/current-session-fixtures-v1-completion-0001/instances/legacy-diagnostic-0001/source/packages/0001/period.json','api_guard':API+'/guard.py','api_bootstrap':API+'/__init__.py'}
    need(all(p['original_bindings'][k]['path']==v for k,v in original_paths.items()),'exact original input origins required')
    binding(p['runtime_coordinator_receipt_binding'])
    c=p['output_custody'];need(type(c)is dict and set(c)=={'root','identity'} and type(c['root'])is str and type(c['identity'])is list,'Root must close output custody before activation')
    return p

def methods(raw,classname):
    tree=ast.parse(raw)
    return {n.name:ast.dump(n,include_attributes=False) for c in tree.body if isinstance(c,ast.ClassDef) and c.name==classname for n in c.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def module(name,row,raw=None,package=False):
    # True selected filename, exact captured bytes, no pyc or code-origin alias.
    raw=exact(row) if raw is None else raw;path=ROOT/row['path']
    spec=importlib.util.spec_from_file_location(name,path,submodule_search_locations=[str(path.parent)] if package else None)
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m
    exec(compile(raw,str(path),'exec',dont_inherit=True),m.__dict__);return m

def execute(p,packet_binding):
    shape(p);need(Path(sys.executable)==ROOT/INSTALL/'bin/python','selected0004 interpreter required')
    own={role:exact(row) for role,row in p['owned_code_bindings'].items()}
    original={role:exact(row) for role,row in p['original_bindings'].items()}
    need(methods(own['tests'],'MachineTransport')==methods(original['original_tests'],'MachineTransport') and len(methods(own['tests'],'MachineTransport'))==14,'all14 original tests must remain identical')
    period=parse(original['legacy_period']);need(period['expires_at']==p['original_source_expiry'],'original source expiry differs')
    # The Root receipt is independent coordinator evidence, never a Lab grant.
    dispatch=parse(exact(p['runtime_coordinator_receipt_binding']))
    need(type(dispatch)is dict and set(dispatch)=={'schema_version','authority_effect','status','learning_terminal_binding','api_source_binding','api_profile_binding','output_custody'},'closed Root dispatch metadata required')
    need(dispatch['schema_version']=='lab-T05-Root-development-dispatch/v1-candidate' and dispatch['authority_effect']=='none' and dispatch['status']=='Root-selected-after-learning-terminal' and dispatch['api_source_binding']==p['api_source_binding'] and dispatch['api_profile_binding']==p['api_profile_binding'] and dispatch['output_custody']==p['output_custody'],'Root terminal dispatch correspondence differs')
    exact(dispatch['learning_terminal_binding'])
    prefix='_T05_owned3_'+uuid.uuid4().hex
    pkg=types.ModuleType(prefix);pkg.__path__=[str(HERE)];sys.modules[prefix]=pkg
    module(prefix+'.capture',p['owned_code_bindings']['capture'],own['capture'])
    outmod=module(prefix+'.owned_output',p['owned_code_bindings']['output'],own['output'])
    output=outmod.Output(p['output_custody'])
    cases=[];result=None;failure=None;guard=None;control=None;expected=None;entered=False
    def diagnostics(error):
        kind,_,tb=error;frames=[]
        while tb:
            path=Path(tb.tb_frame.f_code.co_filename)
            if path.is_relative_to(ROOT):frames.append({'path':str(path.relative_to(ROOT)),'function':tb.tb_frame.f_code.co_name,'line':tb.tb_lineno})
            tb=tb.tb_next
        return {'exception_class':kind.__name__,'frames':frames}
    try:
        exact(packet_binding)
        control=module(prefix+'.selected_dependency_control',p['original_bindings']['dependency_control'],original['dependency_control'])
        dep=parse(exact(p['dependency_selection_binding']))
        need(dep['schema_version']=='lab-runtime-dependency-closure/v2-candidate' and len(dep['inputs'])==720 and len(dep['original_bindings'])==5,'original dependency shape differs')
        expected={r['destination']:{'sha256':r['sha256'],'size_bytes':r['size_bytes'],'mode':0o755 if r['kind'] in {'interpreter','native-executable'} else 0o644} for r in dep['inputs']};expected.update(dep['wheel_members']);expected['lib/abi/ld-linux-x86-64.so.2']['mode']=0o755
        need(len(expected)==1010,'full1010 dependency closure required');control.installed(ROOT/INSTALL,expected)
        # Every later public input is captured by the existing full API guard.
        guard=module(prefix+'.selected_guard',p['original_bindings']['api_guard'],original['api_guard'])
        guard.verify(SOURCE);exact(p['api_profile_binding']);entered=True
        source=parse(exact(p['api_source_binding']));rows={(r['path'],r['sha256']) for r in source['files']}
        for row in p['original_bindings'].values():need((row['path'],row['sha256'])in rows,'original selected input absent from final Source')
        output.write('entry.json',{'authority_effect':'none','source_sha256':SOURCE,'profile_sha256':PROFILE,'dependency_rows':1010,'source_rows':len(rows),'result':'PASS'})
        # Original API package and dependencies keep real filenames/algorithms.
        need('_cal_T05_selected_actual_API17_0003' not in sys.modules,'fresh API module namespace required')
        api=module('_cal_T05_selected_actual_API17_0003',p['original_bindings']['api_bootstrap'],original['api_bootstrap'],package=True)
        module(prefix+'.owned_observer',p['owned_code_bindings']['observer'],own['observer'])
        module(prefix+'.owned_parent_sessions',p['owned_code_bindings']['parent'],own['parent'])
        tests=module(prefix+'.owned_machine_tests',p['owned_code_bindings']['tests'],own['tests'])
        tests.MachineTransport.EXPECTED_SOURCE_BINDING=p['api_source_binding'];tests.MachineTransport.EXPECTED_PROFILE_PIN=PROFILE;tests.MachineTransport.OWNED_OUTPUT=output
        class Result(unittest.TextTestResult):
            def _exc_info_to_string(self,error,test):return json.dumps(diagnostics(error),sort_keys=True)
            def addSuccess(self,test):super().addSuccess(test);cases.append({'test':test.id(),'result':'PASS'})
            def addFailure(self,test,error):super().addFailure(test,error);cases.append({'test':test.id(),'result':'FAIL','diagnostic':diagnostics(error)})
            def addError(self,test,error):super().addError(test,error);cases.append({'test':test.id(),'result':'ERROR','diagnostic':diagnostics(error)})
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(tests.MachineTransport);need(suite.countTestCases()==14,'complete14 required')
        result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite)
        output.write('machine-public-wire.json',{'authority_effect':'none','observations':tests.MachineTransport.machine_events,'source_sha256':SOURCE,'private_memory_exported':False})
    except BaseException:
        failure=diagnostics(sys.exc_info())
    finally:
        exit_errors=[]
        if entered:
            for fn in [lambda:guard.verify(SOURCE),lambda:control.installed(ROOT/INSTALL,expected),lambda:exact(packet_binding),lambda:[exact(r) for r in p['owned_code_bindings'].values()],lambda:[exact(r) for r in p['original_bindings'].values()]]:
                try:fn()
                except BaseException:exit_errors.append(diagnostics(sys.exc_info()))
        passed=failure is None and not exit_errors and result is not None and result.wasSuccessful() and result.testsRun==14
        try:
            output.write('machine-result.json',{'schema_version':'lab-T05-owned-machine-result/v1-candidate','authority_effect':'none','result':'PASS-complete14-focused-development' if passed else 'FAIL-preserved-owned-attempt','tests_run':None if result is None else result.testsRun,'cases':cases,'failure':failure,'exit_guard_errors':exit_errors,'source_sha256':SOURCE,'profile_sha256':PROFILE,'packet_binding':packet_binding,'per_call_observations':output.count,'task_complete':False,'final_T15_T18_qualification':False,'whole34_or_owner_qualified':False})
        finally:output.close()
    return 0 if passed else 1

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--selection',required=True);parser.add_argument('--selection-sha256',required=True);args=parser.parse_args()
    row={'path':args.selection,'sha256':args.selection_sha256};p=parse(exact(row));return execute(p,row)
if __name__=='__main__':raise SystemExit(main())
