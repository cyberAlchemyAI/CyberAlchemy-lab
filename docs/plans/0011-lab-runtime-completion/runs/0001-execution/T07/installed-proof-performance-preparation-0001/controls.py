"""Owned real-filesystem controls, no actual installation/Source/native calls.

Tracing schedules real fixture mutations at selected helper boundaries; no
original function or filesystem function is replaced. Audit counts only opens
inside measured bounded fixture invocations, never actual1011 or wall clocks.
"""
import ast,hashlib,importlib.util,json,os,stat,sys,tempfile
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');HERE=Path(__file__).parent
ORIGINAL=ROOT/'product/lab/release-candidates/v1/interface/composite-operator-v1-completion-0001/revision-0003/control.py'
OLD_SHA='4e9351138e5fa27a3f0c99f72264e5fab63e00a686fcb8c63fdd558b87a84692'
NEW_SHA='a212cf5352ce7994e6a041ccc69f8f5924f01b2be2e9067c066e082ee9a9a5dd'
checks=[];audit_count=None

def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(name,path,pin):
    raw=path.read_bytes();need(sha(raw)==pin,'independently selected control code differs')
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);sys.modules[name]=value
    exec(compile(raw,str(path),'exec'),value.__dict__);return value
OLD=load('_cal_installed_original_control',ORIGINAL,OLD_SHA)
NEW=load('_cal_installed_candidate_control',HERE/'control.py',NEW_SHA)

def audited(event,args):
    global audit_count
    if audit_count is not None and event=='open':
        flags=args[2]
        if type(flags)is int:audit_count['directory'if flags&os.O_DIRECTORY else'leaf']+=1
sys.addaudithook(audited)

def traced(fn,hook):
    previous=sys.gettrace();need(previous is None,'standalone owned tracing context required')
    def trace(frame,event,arg):
        if frame.f_code.co_filename==str(HERE/'control.py'):hook(frame,event,arg)
        return trace
    sys.settrace(trace)
    try:return fn()
    finally:sys.settrace(previous)

def check(name,fn,*,reject=False):
    before=len(os.listdir('/proc/self/fd'))
    try:fn()
    except (ValueError,OSError,KeyError):
        if not reject:raise
        outcome='REFUSED-as-required'
    else:
        need(not reject,'expected owned fixture refusal: '+name);outcome='PASS'
    after=len(os.listdir('/proc/self/fd'));need(before==after,'owned control descriptor imbalance: '+name)
    checks.append({'name':name,'result':outcome,'fd_delta':after-before})

def fixture(parent):
    root=Path(tempfile.mkdtemp(prefix='installation-',dir=parent));os.chmod(root,0o700)
    (root/'a/b').mkdir(parents=True,mode=0o700);os.chmod(root/'a',0o700)
    originals={'a/b/payload.bin':b'known-payload-0001','a/second.txt':b'fresh-second-file','top.bin':b'root-payload'}
    expected={}
    for name,raw in originals.items():
        p=root/name;p.write_bytes(raw);p.chmod(0o644);expected[name]={'sha256':sha(raw),'size_bytes':len(raw),'mode':0o644}
    (root/'installation.json').write_bytes(b'{"OWNED-INERT-RECEIPT":true}\n');(root/'installation.json').chmod(0o600)
    return root,expected,originals

def main():
    global audit_count
    fd0=len(os.listdir('/proc/self/fd'))
    old_ast=ast.parse(ORIGINAL.read_bytes());new_ast=ast.parse((HERE/'control.py').read_bytes())
    fun=lambda tree:{n.name:ast.dump(n,include_attributes=False)for n in tree.body if isinstance(n,ast.FunctionDef)}
    a=fun(old_ast);b=fun(new_ast)
    check('all14-other-original-functions-AST-identical',lambda:need(a.keys()==b.keys()and{n for n in a if a[n]!=b[n]}=={'installed'}and len(a)==15,'unreviewed original helper change'))
    def nonfunction(tree):
        return [ast.dump(n,include_attributes=False)for n in tree.body if not isinstance(n,ast.FunctionDef)and not(isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='ROOT'for t in n.targets))]
    check('top-level-only-ROOT-true-origin-adaptation',lambda:need(nonfunction(old_ast)==nonfunction(new_ast)and OLD.ROOT==NEW.ROOT==ROOT,'undeclared top-level adaptation'))
    measured={}
    with tempfile.TemporaryDirectory(prefix='cal-installed-proof-controls-')as tmp:
        top=Path(tmp)
        root,expected,raws=fixture(top)
        for label,module in [('original',OLD),('successor',NEW)]:
            def run(module=module,label=label):
                global audit_count
                audit_count={'directory':0,'leaf':0}
                try:need(module.installed(root,expected)==len(expected),'bounded exact count differs')
                finally:measured[label]=audit_count;audit_count=None
            check('bounded-three-payload-positive-'+label,run)
        check('bounded-directory-open-count-reduced-with-double-fresh-leaves',lambda:need(measured['successor']['directory']<measured['original']['directory']and measured['successor']['leaf']==measured['original']['leaf']==2*len(expected),'descriptor reuse removed a leaf read or did not reduce directory opens'))
        reads=[]
        def observe(frame,event,arg):
            if frame.f_code.co_name=='_prove_leaf'and event=='call':reads.append(frame.f_locals['name'])
        check('each-selected-payload-proved-twice-with-fresh-leaf-open',lambda:need(traced(lambda:NEW.installed(root,expected),observe)==3 and reads==list(expected)*2,'two fresh complete payload proofs missing'))
        # Original receipt content is independently guarded by its caller. This
        # helper preserves exact regular-file membership instead of inventing
        # a receipt digest or silently omitting the receipt from inventory.
        root,expected,_=fixture(top);(root/'empty/nested').mkdir(parents=True);(root/'empty').chmod(0o755)
        for label,module in [('original',OLD),('successor',NEW)]:check('extra-empty-directory-acceptance-parity-'+label,lambda module=module:need(module.installed(root,expected)==3,'empty-directory parity differs'))
        root,expected,_=fixture(top);(root/'installation.json').chmod(0o000)
        for label,module in [('original',OLD),('successor',NEW)]:check('receipt-content-remains-separate-inventory-parity-'+label,lambda module=module:need(module.installed(root,expected)==3,'receipt inventory changed to unselected content proof'))
        root,expected,_=fixture(top);(root/'zero.bin').write_bytes(b'');(root/'zero.bin').chmod(0o644);expected['zero.bin']={'sha256':sha(b''),'size_bytes':0,'mode':0o644}
        check('zero-byte-selected-payload-supported',lambda:need(NEW.installed(root,expected)==4,'zero-byte proof differs'))
        root,expected,_=fixture(top);os.link(root/'top.bin',root/'same.bin');expected['same.bin']=dict(expected['top.bin'])
        for label,module in [('original',OLD),('successor',NEW)]:check('selected-identical-hardlink-parity-'+label,lambda module=module:need(module.installed(root,expected)==4,'declared hardlink byte proof changed'))
        root,expected,_=fixture(top);expected['installation.json']={'sha256':sha((root/'installation.json').read_bytes()),'size_bytes':(root/'installation.json').stat().st_size,'mode':0o600}
        check('explicit-receipt-row-also-gets-two-fresh-proofs',lambda:need(NEW.installed(root,expected)==4,'explicit selected receipt payload differs'))
        root=top/'empty-installation';root.mkdir();(root/'installation.json').write_bytes(b'{}')
        for label,module in [('original',OLD),('successor',NEW)]:check('zero-payload-receipt-membership-parity-'+label,lambda module=module:need(module.installed(root,{})==0,'empty expected scope differs'))
        mutations=[
          ('unknown-foreign-regular-leaf',lambda r,e:(r/'foreign.bin').write_bytes(b'foreign')),
          ('unknown-nested-regular-leaf',lambda r,e:(r/'a/foreign.bin').write_bytes(b'foreign')),
          ('missing-selected-payload',lambda r,e:(r/'top.bin').unlink()),
          ('wrong-selected-digest',lambda r,e:(r/'top.bin').write_bytes(b'X'*e['top.bin']['size_bytes'])),
          ('wrong-selected-size',lambda r,e:(r/'top.bin').write_bytes(b'larger-than-selected-size')),
          ('wrong-selected-mode',lambda r,e:(r/'top.bin').chmod(0o600)),
          ('unreadable-selected-mode',lambda r,e:(r/'top.bin').chmod(0o000)),
          ('selected-leaf-symlink',lambda r,e:((r/'top.bin').unlink(),(r/'top.bin').symlink_to(r/'a/second.txt'))),
          ('selected-parent-symlink',lambda r,e:((r/'a').rename(r/'a-retained'),(r/'a').symlink_to(r/'a-retained',target_is_directory=True))),
          ('unknown-symlink-leaf',lambda r,e:(r/'alias').symlink_to(r/'top.bin')),
          ('unknown-FIFO-special-leaf',lambda r,e:os.mkfifo(r/'unknown-fifo',0o600)),
          ('selected-FIFO-special-leaf',lambda r,e:((r/'top.bin').unlink(),os.mkfifo(r/'top.bin',0o644))),
          ('missing-receipt',lambda r,e:(r/'installation.json').unlink()),
          ('receipt-symlink',lambda r,e:((r/'installation.json').unlink(),(r/'installation.json').symlink_to(r/'top.bin'))),
          ('receipt-is-directory',lambda r,e:((r/'installation.json').unlink(),(r/'installation.json').mkdir())),
        ]
        for name,mutate in mutations:
            root,expected,_=fixture(top);mutate(root,expected)
            check('real-FS-refuses-'+name,lambda root=root,expected=expected:NEW.installed(root,expected),reject=True)
        root,expected,_=fixture(top);alias=top/'root-alias';alias.symlink_to(root,target_is_directory=True)
        check('selected-root-symlink-refuses',lambda:NEW.installed(alias,expected),reject=True)
        for bad in('../top.bin','a//second.txt','/absolute','.',''):
            root,expected,_=fixture(top);expected[bad]=dict(expected['top.bin'])
            check('noncanonical-selected-locator-'+repr(bad),lambda root=root,expected=expected:NEW.installed(root,expected),reject=True)
        # Deterministic trace boundaries mutate only owned real fixture paths;
        # no original/new helper or os function is monkeypatched.
        root,expected,_=fixture(top);fired=[]
        def between(frame,event,arg):
            if frame.f_code.co_name=='_inventory'and event=='return'and not fired:
                fired.append(True);(root/'a/b/payload.bin').write_bytes(b'X'*expected['a/b/payload.bin']['size_bytes'])
        check('mutation-between-first-and-second-fresh-proof-refuses',lambda:traced(lambda:NEW.installed(root,expected),between),reject=True);need(fired,'between-phase fixture mutation not reached')
        root,expected,_=fixture(top);fired=[]
        def leaf_detach(frame,event,arg):
            if frame.f_code.co_name=='_read_exact'and event=='call'and not fired:
                fired.append(True);path=root/'a/b/payload.bin';raw=path.read_bytes();path.rename(root/'retained-leaf');path.write_bytes(raw);path.chmod(0o644)
        check('same-byte-leaf-detach-during-read-refuses',lambda:traced(lambda:NEW.installed(root,expected),leaf_detach),reject=True);need(fired,'leaf detach not reached')
        root,expected,_=fixture(top);fired=[]
        def changed_read(frame,event,arg):
            if frame.f_code.co_name=='_read_exact'and event=='return'and not fired:
                fired.append(True);(root/'a/b/payload.bin').write_bytes(b'Z'*expected['a/b/payload.bin']['size_bytes'])
        check('real-byte-mutation-after-read-before-return-refuses',lambda:traced(lambda:NEW.installed(root,expected),changed_read),reject=True);need(fired,'read mutation not reached')
        root,expected,_=fixture(top);fired=[]
        def parent_detach(frame,event,arg):
            if frame.f_code.co_name=='_read_exact'and event=='call'and not fired:
                fired.append(True);(root/'a').rename(root/'a-detached');(root/'a/b').mkdir(parents=True);(root/'a/b/payload.bin').write_bytes(b'known-payload-0001')
        check('held-intermediate-directory-detach-refuses',lambda:traced(lambda:NEW.installed(root,expected),parent_detach),reject=True);need(fired,'parent detach not reached')
        root,expected,_=fixture(top);fired=[]
        def root_detach(frame,event,arg):
            if frame.f_code.co_name=='_prove_leaf'and event=='call'and not fired:
                fired.append(True);root.rename(Path(str(root)+'-retained'));root.mkdir()
        check('held-root-ancestor-attachment-detach-refuses',lambda:traced(lambda:NEW.installed(root,expected),root_detach),reject=True);need(fired,'root detach not reached')
        root,expected,_=fixture(top);fired=[]
        def late_foreign(frame,event,arg):
            if frame.f_code.co_name=='_prove_leaf'and event=='return'and frame.f_locals['name']=='top.bin':
                fired.append(True)
                if len(fired)==2:(root/'late-foreign').write_bytes(b'late foreign')
        check('foreign-leaf-created-after-second-fresh-read-refuses',lambda:traced(lambda:NEW.installed(root,expected),late_foreign),reject=True);need(len(fired)==2,'final inventory fixture mutation not reached')
        root,expected,_=fixture(top);fired=[]
        def scope_change(frame,event,arg):
            if frame.f_code.co_name=='_inventory'and event=='return'and not fired:
                fired.append(True);expected['top.bin']['sha256']='0'*64
        check('expected-selection-mutation-between-phases-refuses',lambda:traced(lambda:NEW.installed(root,expected),scope_change),reject=True);need(fired,'selection mutation not reached')
        root,expected,_=fixture(top);fired=[]
        def root_mode(frame,event,arg):
            if frame.f_code.co_name=='_read_exact'and event=='call'and not fired:fired.append(True);root.chmod(0o755)
        check('held-root-mode-change-refuses',lambda:traced(lambda:NEW.installed(root,expected),root_mode),reject=True);need(fired,'root mode mutation not reached')
        # The next new call must do real fresh reads; no successful prior
        # invocation can supply later byte or stat evidence.
        root,expected,_=fixture(top);NEW.installed(root,expected);(root/'top.bin').write_bytes(b'bad')
        check('later-call-does-not-reuse-earlier-proof',lambda:NEW.installed(root,expected),reject=True)
    need(OLD.capture(ORIGINAL,OLD_SHA)==ORIGINAL.read_bytes()and OLD.capture(HERE/'control.py',NEW_SHA)==(HERE/'control.py').read_bytes(),'control source changed during bounded run')
    fd1=len(os.listdir('/proc/self/fd'));need(fd0==fd1,'full bounded control run descriptor imbalance')
    return {'schema_version':'lab-installed-proof-owned-controls/v1-candidate','result':'PASS','authority_effect':'none','candidate_sha256':NEW_SHA,'original_sha256':OLD_SHA,'check_count':len(checks),'checks':checks,'bounded_fixture_open_counts':measured,'fd_delta':fd1-fd0,'actual1011_performance_measured':False,'actual_installation_or_API_or_native_or_Source_or_lease_operation':False,'original_source_ELF_ABI_and_receipt_guards_unchanged':True,'cross_call_cache':False,'runtime_or_deadline_qualified':False,'task_complete':False}
if __name__=='__main__':
    try:result=main()
    except Exception as error:
        result={'result':'FAIL','exception_class':type(error).__name__,'message':str(error),'completed_checks':checks,'actual1011_or_native_or_API':False}
    print(json.dumps(result,sort_keys=True));raise SystemExit(0 if result['result']=='PASS'else 1)
