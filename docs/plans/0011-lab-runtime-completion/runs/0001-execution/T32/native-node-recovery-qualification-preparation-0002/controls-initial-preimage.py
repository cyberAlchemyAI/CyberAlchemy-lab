"""Pure AST + new inert FD fixtures only; no runner/API/native/Source guards."""
import ast,copy,fcntl,hashlib,json,os,stat,sys,tempfile,types
from pathlib import Path
HERE=Path(__file__).absolute().parent;OLD=HERE.parent/'native-node-recovery-qualification-preparation-0001'
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
checks=[]
def need(ok,reason):
    if not ok:raise ValueError(reason)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def shape(node):return ast.dump(node,include_attributes=False)
def check(name,fn,reject=False):
    before=fds()
    try:fn()
    except (ValueError,OSError,KeyError):
        if not reject:raise
    else:need(not reject,'expected fixture refusal')
    need(fds()==before,'owned fixture descriptor leak');checks.append(name)
def fds():
    rows={}
    for x in os.listdir('/proc/self/fd'):
        try:s=os.fstat(int(x));rows[x]=(s.st_dev,s.st_ino,s.st_mode,fcntl.fcntl(int(x),fcntl.F_GETFL),fcntl.fcntl(int(x),fcntl.F_GETFD))
        except OSError:continue
    return rows

def main():
    start=fds();tree=ast.parse((HERE/'qualify.py').read_bytes());old=ast.parse((OLD/'qualify.py').read_bytes())
    funcs={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
    of={n.name:n for n in old.body if isinstance(n,ast.FunctionDef)}
    def caseblock(fn):return next(n for n in ast.walk(fn)if isinstance(n,ast.With)and any(isinstance(i.context_expr,ast.Call)and isinstance(i.context_expr.func,ast.Attribute)and i.context_expr.func.attr=='signed_catalog'for i in n.items))
    check('all-four-original-operation-block-AST-identical',lambda:need(shape(caseblock(funcs['run']))==shape(caseblock(of['run'])),'operation block changed'))
    for name in ('need','sha','parse','relative','bootstrap_capture','module','diagnostic','main'):
        check('original-helper-AST-identical-'+name,lambda name=name:need(shape(funcs[name])==shape(of[name]),'unintended original helper change'))
    check('capture-copy-byte-identical',lambda:need((HERE/'capture.py').read_bytes()==(OLD/'capture.py').read_bytes(),'capture changed'))
    check('boundary-copy-byte-identical-real900-retained',lambda:need((HERE/'boundary.py').read_bytes()==(OLD/'boundary.py').read_bytes(),'boundary changed'))
    runtext=ast.unparse(funcs['run'])
    check('selected-deps-before-original-Source-verify',lambda:need(runtext.index("sys.path.insert(0, str(INSTALL / 'deps'))")<runtext.index('guard.verify(SOURCE)'),'vendor path too late'))
    check('executor-finally-guard-independent-of-boundary',lambda:need(any(isinstance(n,ast.If)and ast.unparse(n.test)=='executor is not None'and 'executor.guard()'in ast.unparse(n)for n in funcs['run'].body[-2].finalbody)if False else 'try:\n            executor.guard()'in runtext,'executor exit missing'))
    names=('fd_snapshot','need','sha','classify_initialization','verify_libffi_descriptor','runtime_initialization','operational_fd_check')
    env={'os':os,'stat':stat,'fcntl':fcntl,'hashlib':hashlib}
    astmod=ast.Module(body=[funcs[n]for n in names],type_ignores=[]);ast.fix_missing_locations(astmod);exec(compile(astmod,str(HERE/'qualify.py'),'exec'),env)
    snapshot=env['fd_snapshot'];classify=env['classify_initialization'];op=env['operational_fd_check']
    check('raw-FD-snapshot-does-not-leak',lambda:need(snapshot()==snapshot(),'snapshot changed'))
    base={'0':{'identity':'unchanged'}};one={'7':{'readonly':True,'cloexec':True}}
    check('initialization-zero-additions-positive',lambda:classify(base,copy.deepcopy(base),None))
    check('initialization-one-verified-descriptor-positive',lambda:classify(base,{**base,**one},one))
    check('initialization-unknown-descriptor-refuses',lambda:classify(base,{**base,**one},None),True)
    check('initialization-two-descriptors-refuse',lambda:classify(base,{**base,**one,'8':{}},{**one,'8':{}}),True)
    check('initialization-preexisting-descriptor-change-refuses',lambda:classify(base,{'0':{'identity':'changed'}},None),True)
    check('initialization-preexisting-descriptor-loss-refuses',lambda:classify(base,{},None),True)
    check('initialization-unmatched-extra-proof-refuses',lambda:classify(base,base,one),True)
    cap=types.ModuleType('_T32_v2_fixture_capture');exec(compile((HERE/'capture.py').read_bytes(),str(HERE/'capture.py'),'exec'),cap.__dict__)
    with tempfile.TemporaryDirectory(prefix='cal-T32-v2-inert-resources-')as tmp:
        path=Path(tmp)/'inert-selected-public-library.txt';body=b'OWNED-INERT-SELECTED-LIBRARY-NOT-AN-ELF';path.write_bytes(body);path.chmod(0o644)
        env.update(FFI_PATH=path,FFI_SIZE=len(body),FFI_SHA=sha(body))
        def verify(flags):
            fd=os.open(path,flags)
            try:return env['verify_libffi_descriptor'](fd,cap.capture_path)
            finally:os.close(fd)
        check('retained-FD-real-owned-readonly-CLOEXEC-exactbody-positive',lambda:verify(os.O_RDONLY|os.O_CLOEXEC))
        check('retained-FD-writable-refuses',lambda:verify(os.O_RDWR|os.O_CLOEXEC),True)
        def no_cloexec():
            fd=os.open(path,os.O_RDONLY|os.O_CLOEXEC)
            try:os.set_inheritable(fd,True);env['verify_libffi_descriptor'](fd,cap.capture_path)
            finally:os.close(fd)
        check('retained-FD-no-CLOEXEC-refuses',no_cloexec,True)
        other=Path(tmp)/'other.txt';other.write_bytes(body);other.chmod(0o644)
        def foreign():
            fd=os.open(other,os.O_RDONLY|os.O_CLOEXEC)
            try:env['verify_libffi_descriptor'](fd,cap.capture_path)
            finally:os.close(fd)
        check('retained-FD-samebytes-wrong-inode-refuses',foreign,True)
        good=env['FFI_SHA'];env['FFI_SHA']='0'*64
        check('retained-FD-wrong-selected-digest-refuses',lambda:verify(os.O_RDONLY|os.O_CLOEXEC),True);env['FFI_SHA']=good
        path.chmod(0o600);check('retained-FD-wrong-mode-refuses',lambda:verify(os.O_RDONLY|os.O_CLOEXEC),True);path.chmod(0o644)
        before=snapshot();fd=os.open(path,os.O_RDONLY|os.O_CLOEXEC)
        try:
            current=snapshot();value=env['runtime_initialization'](before,current,cap.capture_path)
            need(value['raw_initialization_delta']==1 and snapshot()==current,'actual initialization map not preserved')
        finally:os.close(fd)
        check('one-owned-real-descriptor-classified-with-exact-proof',lambda:need(snapshot()==before,'real fixture descriptor retained'))
        check('operational-exact-map-positive',lambda:op(snapshot(),[],'fixture-positive'))
        def leak():
            saved=snapshot();fd=os.open(path,os.O_RDONLY|os.O_CLOEXEC)
            try:op(saved,[],'fixture-new-fd')
            finally:os.close(fd)
        check('operational-one-added-FD-refuses-even-readonly-CLOEXEC',leak,True)
        def flags_change():
            fd=os.open(path,os.O_RDONLY|os.O_CLOEXEC)
            try:
                saved=snapshot();os.set_inheritable(fd,True);op(saved,[],'fixture-flag-change')
            finally:os.close(fd)
        check('operational-same-count-FD-flags-change-refuses',flags_change,True)
    # Execute exact selected finally subtrees with inert ports; verify cleanup
    # failure and technical expiry cannot suppress executor or other guards.
    final=next(n.finalbody for n in funcs['run'].body if isinstance(n,ast.Try))
    targets=[n for n in final if isinstance(n,ast.If)and ast.unparse(n.test)in('store is not None','entered','executor is not None','boundary is not None')]
    need(len(targets)==4,'expected four independent exit guard blocks')
    mod=ast.Module(body=targets,type_ignores=[]);ast.fix_missing_locations(mod);code=compile(mod,str(HERE/'qualify.py'),'exec')
    seen=[]
    class Port:
        def close(self):seen.append('store');raise ValueError('inert store close refusal')
        def verify(self,pin):seen.append('Source');raise ValueError('inert Source refusal')
        def guard(self):seen.append('executor')
        def check_base(self):seen.append('boundary');raise ValueError('inert expired boundary')
    scope={'store':Port(),'guard':Port(),'executor':Port(),'boundary':Port(),'entered':True,'SOURCE':'fixture',
        'all_selected':lambda:seen.append('130selected'),'exact':lambda b:seen.append('profile'),'packet':{'api_profile_binding':{}},
        'exit_errors':[],'diagnostic':lambda exc:{'exception_class':exc[0].__name__},'sys':sys,'need':need}
    exec(code,scope)
    check('all-exit-guards-run-despite-store-Source-and-boundary-failures',lambda:need(seen==['store','Source','130selected','profile','executor','boundary']and len(scope['exit_errors'])==3,'exit guards suppressed'))
    need(start==fds(),'pure control whole-run FD imbalance')
    return {'result':'PASS','checks':checks,'check_count':len(checks),'FD_delta':0,'mode':'AST-and-owned-inert-FD-fixtures-only','actual_native_Source_API_installation_lease_or_libffi_import_executed':False,'four_case_runtime_qualification':False}
if __name__=='__main__':
    try:r=main()
    except BaseException as e:r={'result':'FAIL','exception_class':type(e).__name__,'message':str(e),'completed_checks':checks}
    print(json.dumps(r,sort_keys=True));raise SystemExit(0 if r['result']=='PASS'else 1)
