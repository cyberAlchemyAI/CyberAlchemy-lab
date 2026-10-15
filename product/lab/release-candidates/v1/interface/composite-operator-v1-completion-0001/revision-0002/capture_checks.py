"""Actual owned replacements observed at production helper entry, no substitution."""
import importlib.util,json,os,stat,sys,tempfile
from pathlib import Path
import control as K
import composite as C
HERE=Path(__file__).resolve().parent
RUN=K.ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/revision-0002'
def put(p,raw=b'owned inert public bytes',mode=0o600):
    fd=os.open(p,os.O_CREAT|os.O_EXCL|os.O_WRONLY,mode)
    with os.fdopen(fd,'wb') as out:out.write(raw)
def fixture():
    root=Path(tempfile.mkdtemp(prefix='cal-T06-capture-controls-'));os.chmod(root,0o700)
    (root/'nested').mkdir(mode=0o700);(root/'nested/deep').mkdir(mode=0o700)
    leaf=root/'nested/deep/input.json';put(leaf)
    return root,leaf,{'path':str(leaf),'sha256':K.sha(leaf.read_bytes()),'identity':K.ident(leaf.stat())}
def monitor(target,ordinal,mutation,operation):
    monitor_id=4;seen=0;performed=False
    def observe(code,offset):
        nonlocal seen,performed
        if code is target:
            seen+=1
            if seen==ordinal:mutation();performed=True
    sys.monitoring.use_tool_id(monitor_id,'T06 actual replacement observer')
    sys.monitoring.register_callback(monitor_id,sys.monitoring.events.PY_START,observe)
    sys.monitoring.set_local_events(monitor_id,target,sys.monitoring.events.PY_START)
    try:operation()
    finally:
        sys.monitoring.set_local_events(monitor_id,target,0);sys.monitoring.register_callback(monitor_id,sys.monitoring.events.PY_START,None);sys.monitoring.free_tool_id(monitor_id)
        if not performed:raise AssertionError('actual production checkpoint not reached')
def main(report_name="capture-evidence-0002.json"):
    cases=[];roots=[]
    def refuse(label,operation):
        try:operation()
        except ValueError as error:cases.append({'case':label,'result':'PASS-refused','error_type':type(error).__name__})
        else:raise AssertionError(label+' accepted')
    root,leaf,selection=fixture();roots.append(str(root));before=K.protected(selection,str(root),K.ident(root.stat()));assert before==leaf.read_bytes();cases.append({'case':'protected returns same selected captured bytes','result':'PASS'})
    for level in ['leaf','nested','deep','root']:
        for phase,target,ordinal in [('after file open',K._read_exact.__code__,1),('after exact bytes captured',K._attachments.__code__,2)]:
            root,leaf,selection=fixture();roots.append(str(root));root_identity=K.ident(root.stat());digest=selection['sha256']
            def replace(level=level,root=root,leaf=leaf):
                original=leaf if level=='leaf' else root if level=='root' else root/level if level=='nested' else root/'nested/deep'
                retained=original.with_name(original.name+'-retained');original.rename(retained)
                if level=='leaf':put(original,retained.read_bytes())
                else:original.mkdir(mode=0o700)
            refuse('protected '+level+' same-byte/inode replacement '+phase,lambda:monitor(target,ordinal,replace,lambda:K.protected(selection,str(root),root_identity)))
    root,leaf,selection=fixture();roots.append(str(root));identity=K.ident(root.stat())
    refuse('protected owned nested directory mode replaced after read',lambda:monitor(K._attachments.__code__,2,lambda:os.chmod(root/'nested',0o755),lambda:K.protected(selection,str(root),identity)))
    root,leaf,selection=fixture();roots.append(str(root));identity=K.ident(root.stat());retained=leaf.with_name('retained.json');leaf.rename(retained);leaf.symlink_to(retained)
    refuse('protected symlink before read',lambda:K.protected(selection,str(root),identity))
    root,leaf,selection=fixture();roots.append(str(root));identity=K.ident(root.stat())
    refuse('protected independently selected digest mismatch',lambda:K.protected(selection|{'sha256':'0'*64},str(root),identity))
    refuse('protected capture bound before any body read',lambda:K.protected(selection,str(root),identity,limit=1))
    # Public wrapper uses actual unchanged repository root and a newly owned
    # public inert file; it never reads a key, credential or protected body.
    public_dir=RUN/('owned-public-capture-controls-'+report_name.removesuffix('.json'));public_dir.mkdir(mode=0o700)
    for phase,target,ordinal in [('after open',K._read_exact.__code__,1),('after capture',K._attachments.__code__,2)]:
        name=public_dir/('public-'+str(len(cases))+'.json');put(name,mode=0o644);binding={'path':str(name.relative_to(K.ROOT)),'sha256':K.sha(name.read_bytes())}
        def replace(name=name):name.rename(name.with_suffix('.retained'));put(name,mode=0o644)
        refuse('public same-byte new inode '+phase,lambda:monitor(target,ordinal,replace,lambda:K.public(binding)))
    for phase,target,ordinal in [('after open',K._read_exact.__code__,1),('after capture',K._attachments.__code__,2)]:
        directory=public_dir/('nested-public-'+str(len(cases)));directory.mkdir(mode=0o700);leaf=directory/'input.json';put(leaf,mode=0o644);binding={'path':str(leaf.relative_to(K.ROOT)),'sha256':K.sha(leaf.read_bytes())}
        def replace(directory=directory):directory.rename(directory.with_name(directory.name+'-retained'));directory.mkdir(mode=0o700)
        refuse('public nested ancestor replaced '+phase,lambda:monitor(target,ordinal,replace,lambda:K.public(binding)))
    need_read=K.public({'path':str(name.relative_to(K.ROOT)),'sha256':K.sha(name.read_bytes())});assert need_read==name.read_bytes();cases.append({'case':'public returns exact single captured bytes','result':'PASS'})
    for name in ['../escape','./escape','absolute\\escape','/absolute']:
        refuse('public refuses noncanonical locator '+name,lambda name=name:K.public({'path':name,'sha256':'0'*64}))
    # Real complete selected installed closure, not a synthetic count.
    count=C.dependency_guard({'selection':{'path':C.DEPENDENCY_SELECTION,'sha256':C.DEPENDENCY_SHA},'installation':str(C.INSTALL)});assert count==1010;cases.append({'case':'all 1010 actual retained dependencies pass two fresh no-follow byte guards and closed enumeration','result':'PASS','files':count})
    for mutation in ['extra','mode','symlink','wrong-digest']:
        root=Path(tempfile.mkdtemp(prefix='cal-T06-install-controls-'));os.chmod(root,0o700);roots.append(str(root));leaf=root/'library.so';put(leaf,mode=0o644);put(root/'installation.json',b'{}',mode=0o644)
        expected={'library.so':{'sha256':K.sha(leaf.read_bytes()),'mode':0o644,'size_bytes':leaf.stat().st_size}}
        if mutation=='extra':put(root/'foreign-extra',b'unknown',mode=0o644)
        elif mutation=='mode':os.chmod(leaf,0o600)
        elif mutation=='symlink':leaf.rename(root/'retained');leaf.symlink_to(root/'retained')
        else:expected['library.so']['sha256']='0'*64
        refuse('installed refuses '+mutation,lambda:K.installed(root,expected))
    # Actual launcher capture function, with production body unchanged.
    spec=importlib.util.spec_from_file_location('_T06_launch_capture',HERE/'launch.py');L=importlib.util.module_from_spec(spec);spec.loader.exec_module(L)
    root,leaf,selection=fixture();roots.append(str(root));assert L._capture_exact(root,{'path':str(leaf.relative_to(root)),'sha256':selection['sha256']})==leaf.read_bytes();cases.append({'case':'launch bootstrap exact no-follow capture returns selected bytes','result':'PASS'})
    report={'schema_version':'lab-T06-capture-controls/v2-candidate','result':'PASS','cases':cases,'owned_roots':roots,'instrumentation':'sys.monitoring PY_START observer makes actual owned replacements at production helper entry; no function/clock/guard substitution','actual_full34_construction':False,'task_complete':False,'authority_effect':'none'}
    out=RUN/report_name;put(out,json.dumps(report,indent=2,sort_keys=True).encode()+b'\n');print(json.dumps({'result':'PASS','cases':len(cases),'report':str(out)}))
if __name__=='__main__':main()
