"""Bounded passive public-byte and owned real-FS reader compatibility controls."""
import ast,copy,hashlib,json,os,runpy,sys,tempfile,types
from pathlib import Path
HERE=Path(__file__).absolute().parent
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
CONTROL=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/installed-proof-performance-preparation-0001/control.py'
PIN='a212cf5352ce7994e6a041ccc69f8f5924f01b2be2e9067c066e082ee9a9a5dd'
CARGO=Path('/home/vlad_/.rustup/toolchains/1.98.1-x86_64-unknown-linux-gnu/bin/cargo')
CARGO_SHA='da77c8b33849312255ccde3179198ada4c8deb370488d050286146b1d1b27e14'
CARGO_SIZE=40680304

def need(v,s):
    if not v:raise ValueError(s)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def fds():
    result={}
    for n in os.listdir('/proc/self/fd'):
        try:s=os.fstat(int(n));result[n]=(s.st_dev,s.st_ino,s.st_mode)
        except OSError:continue
    return result

def main():
    initial=fds();checks=[]
    def check(name,fn,refusal=False):
        before=fds()
        try:fn()
        except (ValueError,OSError):
            if not refusal:raise
        else:need(not refusal,'expected refusal: '+name)
        need(fds()==before,'descriptor leak: '+name);checks.append(name)
    cap=types.ModuleType('_T32_public_controls_original_capture')
    exec(compile((HERE/'capture.py').read_bytes(),str(HERE/'capture.py'),'exec'),cap.__dict__)
    raw=cap.capture_path(CONTROL,PIN)
    control=types.ModuleType('_T32_public_controls_exact_control');control.__file__=str(CONTROL)
    exec(compile(raw,str(CONTROL),'exec'),control.__dict__)
    # Execute only the actual nested reader body, never run()/API/native/guards.
    tree=ast.parse((HERE/'qualify.py').read_bytes())
    runner=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='run')
    selected=next(n for n in runner.body if isinstance(n,ast.FunctionDef)and n.name=='selected_public')
    scope={'Path':Path,'ROOT':ROOT,'need':need,'capture':cap.capture_path,'public_control':control}
    unit=ast.Module(body=[copy.deepcopy(selected)],type_ignores=[]);ast.fix_missing_locations(unit)
    exec(compile(unit,str(HERE/'qualify.py'),'exec'),scope);read=scope['selected_public']
    row={'path':str(CARGO),'sha256':CARGO_SHA,'size_bytes':CARGO_SIZE}
    check('actual-selected-40680304-byte-Cargo-positive',lambda:need(len(read(row))==CARGO_SIZE,'actual Cargo capture failed'))
    check('actual-selected-Cargo-second-fresh-read-positive',lambda:need(sha(read(row))==CARGO_SHA,'second actual Cargo capture failed'))
    check('actual-Cargo-wrong-digest-refuses',lambda:read({**row,'sha256':'0'*64}),True)
    check('actual-Cargo-wrong-size-refuses',lambda:read({**row,'size_bytes':CARGO_SIZE-1}),True)
    occurrences=[]
    packet=json.loads((HERE/'execution-selection-INACTIVE.json').read_bytes())
    for k,count in [('adoption_manifest',153),('execution_manifest',176)]:
        binding=packet['reference_bindings'][k]
        body=cap.capture_path(ROOT/binding['path'],binding['sha256'])
        rows=json.loads(body)['files'];need(len(rows)==count,'scope count changed')
        for r in rows:
            p=Path(r['path']);p=p if p.is_absolute()else ROOT/p
            large=r['size_bytes']>32*1024*1024
            need(not large or(p==CARGO and r['sha256']==CARGO_SHA and r['size_bytes']==CARGO_SIZE),'selected row outside reader domain')
            occurrences.append({'scope':k,'path':str(p),'sha256':r['sha256'],'size_bytes':r['size_bytes'],'reader':'exact-Cargo-reviewed-control'if p==CARGO else 'unchanged32MiB-capture'})
    check('all329-row-occurrences-inside-explicit-reader-domain',lambda:need(len(occurrences)==329 and sum(r['size_bytes']>32*1024*1024 for r in occurrences)==1,'domain mismatch'))
    # Real FS mutation scheduling traces an existing reviewed helper; it never
    # replaces any original function, reader, global constant or OS primitive.
    def during_return(path,pin,mutation):
        fired=[]
        def trace(frame,event,arg):
            if frame.f_code is control._read_exact.__code__ and event=='return'and not fired:
                fired.append(True);mutation()
            return trace
        previous=sys.gettrace();sys.settrace(trace)
        try:control.capture(path,pin,limit=65536,size=65536)
        finally:sys.settrace(previous);need(fired==[True],'owned mutation schedule did not execute')
    with tempfile.TemporaryDirectory(prefix='cal-T32-reader4-inert-')as tmp:
        base=Path(tmp);leaf=base/'owned-small';body=b'a'*65536;leaf.write_bytes(body);pin=sha(body)
        check('ordinary-small-selected-file-positive',lambda:need(read({'path':str(leaf),'sha256':pin,'size_bytes':len(body)})==body,'ordinary capture failed'))
        foreign=base/'foreign-33MiB'
        with foreign.open('wb')as out:out.truncate(33*1024*1024)
        check('foreign33MiB-refuses-without-general-cap-widening',lambda:read({'path':str(foreign),'sha256':'0'*64,'size_bytes':33*1024*1024}),True)
        symlink=base/'symlink';symlink.symlink_to(leaf)
        check('ordinary-symlink-leaf-refuses',lambda:read({'path':str(symlink),'sha256':pin,'size_bytes':len(body)}),True)
        check('ordinary-wrong-size-refuses',lambda:read({'path':str(leaf),'sha256':pin,'size_bytes':len(body)-1}),True)
        def grow():
            with leaf.open('ab')as out:out.write(b'x')
        check('reviewed-large-reader-growth-after-byte-read-refuses',lambda:during_return(leaf,pin,grow),True);leaf.write_bytes(body)
        def mutate():
            with leaf.open('r+b')as out:out.write(b'b')
        check('reviewed-large-reader-same-size-mutation-refuses',lambda:during_return(leaf,pin,mutate),True);leaf.write_bytes(body)
        held=base/'parent';held.mkdir();child=held/'input';child.write_bytes(body)
        def detach():
            held.rename(base/'detached');held.mkdir();(held/'input').write_bytes(body)
        check('reviewed-large-reader-intermediate-detachment-refuses',lambda:during_return(child,pin,detach),True)
        check('reviewed-large-reader-symlink-refuses',lambda:control.capture(symlink,pin,limit=len(body),size=len(body)),True)
        check('reviewed-large-reader-missing-refuses',lambda:control.capture(base/'missing',pin,limit=len(body),size=len(body)),True)
        check('reviewed-large-reader-preexisting-size-mismatch-refuses',lambda:control.capture(leaf,pin,limit=len(body),size=len(body)-1),True)
    need(fds()==initial and 'ctypes'not in sys.modules,'public controls leaked/imported runtime initialization')
    result={'result':'PASS-passive-public-and-owned-real-FS-only','checks':checks,'check_count':len(checks),'declared_occurrences':occurrences,'all329_reader_domains_eligible':True,'actual_large_public_file_read':True,'actual_API_Source_native_executor_boundary_installation_lease_or_runtime_used':False,'FD_delta':0,'ctypes_imported':False}
    return result
if __name__=='__main__':
    result=main()
    with(HERE/'public-controls-result.json').open('x')as out:json.dump(result,out,sort_keys=True,indent=2);out.write('\n')
    print(json.dumps({k:v for k,v in result.items()if k!='declared_occurrences'},sort_keys=True))
