"""Owned deterministic successor authoring; no runner/native execution."""
from pathlib import Path
import hashlib,json
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');BASE=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T32'
OLD=BASE/'native-node-recovery-qualification-preparation-0001';NEW=Path(__file__).parent
raw=(OLD/'qualify.py').read_text()
bootstrap='''# Earliest practical bootstrap: only os/stat/fcntl imported before raw snapshot.
# No API, Source, runtime, ctypes, argument parser or current-module imports yet.
import os, stat, fcntl

def fd_snapshot():
    """Stable descriptor identities and flags; no file contents or target paths."""
    rows={}
    for name in sorted(os.listdir('/proc/self/fd'),key=int):
        fd=int(name)
        try:
            before=os.fstat(fd);flags=fcntl.fcntl(fd,fcntl.F_GETFL);fdflags=fcntl.fcntl(fd,fcntl.F_GETFD)
            after=os.fstat(fd)
        except OSError as error:
            # listdir's own transient directory FD has already been closed.
            if error.errno==9 and not os.path.lexists('/proc/self/fd/'+name):continue
            raise
        def value(s):return {'device':s.st_dev,'inode':s.st_ino,'uid':s.st_uid,'gid':s.st_gid,
                             'mode':s.st_mode,'rdev':s.st_rdev,'status_flags':flags,'descriptor_flags':fdflags}
        if value(before)!=value(after):raise ValueError('descriptor changed during snapshot')
        rows[name]=value(before)
    return rows

RAW_BOOTSTRAP_FDS=fd_snapshot()
'''
raw=raw.replace('import argparse, copy, datetime, hashlib, importlib, importlib.abc, importlib.util, json, os',bootstrap+'\nimport argparse, copy, datetime, hashlib, importlib, importlib.abc, importlib.util, json')
needle="PROFILE='9c8c3018226abb9077c6a99ee3cbc9dd0174c148b332b9488fd4a3a9cd30418b'"
raw=raw.replace(needle,needle+"\nEXECUTION={'path':'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/installed-proof-Root-comparison-0001/execution-selection.json','sha256':'365e3270842dd33e1aa9e5f621f072210d317255155d024078cab049adb20373'}\nCONTROL=RUN/'T07/installed-proof-performance-preparation-0001/control.py'\nCONTROL_SHA='a212cf5352ce7994e6a041ccc69f8f5924f01b2be2e9067c066e082ee9a9a5dd'\nFFI_PATH=INSTALL/'lib/abi/libffi.so.8'\nFFI_SHA='1a0dc86f787f73e025a6e521056360afcbe70f2a82cd808132fefc2b4ee95daa'\nFFI_SIZE=64184")
helpers='''
def classify_initialization(raw,current,verified_addition):
    """Only one independently verified exact libffi descriptor may be added."""
    need(all(k in current and current[k]==v for k,v in raw.items()),'preexisting descriptor removed or changed during initialization')
    added={k:v for k,v in current.items()if k not in raw}
    need(len(added)<=1,'multiple unexpected retained initialization descriptors')
    if added:
        need(type(verified_addition)is dict and added==verified_addition,'unverified retained initialization descriptor')
    else:need(verified_addition is None,'initialization descriptor verification has no added descriptor')
    return {'raw_initialization_delta':len(current)-len(raw),'accepted_initialization_descriptor':added or None,
            'scope':'Only exact selected0004 libffi readonly+CLOEXEC initialization; not an operational FD allowance.'}

def verify_libffi_descriptor(fd,capture):
    """Verify exact selected public body through the actual retained read FD."""
    before=os.fstat(fd);flags=fcntl.fcntl(fd,fcntl.F_GETFL);fdflags=fcntl.fcntl(fd,fcntl.F_GETFD)
    need(stat.S_ISREG(before.st_mode)and before.st_uid==os.getuid()and stat.S_IMODE(before.st_mode)==0o644
         and before.st_size==FFI_SIZE and flags&os.O_ACCMODE==os.O_RDONLY and fdflags&fcntl.FD_CLOEXEC,
         'retained initialization descriptor is not selected readonly+CLOEXEC libffi')
    selected=capture(FFI_PATH,FFI_SHA,maximum=FFI_SIZE,required_uid=os.getuid())
    identity=lambda s:(s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    need(identity(FFI_PATH.lstat())==identity(before),'retained initialization descriptor differs from selected libffi inode')
    parts=[];total=0
    while total<FFI_SIZE:
        block=os.pread(fd,min(65536,FFI_SIZE-total),total)
        need(block,'retained selected library truncated');total+=len(block);parts.append(block)
    need(not os.pread(fd,1,total),'retained selected library exceeds bound')
    body=b''.join(parts)
    need(body==selected and sha(body)==FFI_SHA and identity(before)==identity(os.fstat(fd))==identity(FFI_PATH.lstat()),
         'retained selected library bytes or attachment changed')
    need(flags==fcntl.fcntl(fd,fcntl.F_GETFL)and fdflags==fcntl.fcntl(fd,fcntl.F_GETFD),'retained library flags changed')
    return {'path':str(FFI_PATH),'sha256':FFI_SHA,'size_bytes':FFI_SIZE,'inode':before.st_ino,'device':before.st_dev,
            'read_only':True,'close_on_exec':True,'body_read_by':'bounded pread preserving original descriptor offset'}

def runtime_initialization(raw,current,capture):
    added={k:v for k,v in current.items()if k not in raw};proof=None
    need(len(added)<=1,'multiple unexpected initialization descriptors')
    if added:proof=verify_libffi_descriptor(int(next(iter(added))),capture)
    evidence=classify_initialization(raw,current,added if proof is not None else None)
    need(fd_snapshot()==current,'initialization verification changed descriptor map')
    return {**evidence,'verified_selected_library':proof}

def operational_fd_check(expected,observations,label):
    current=fd_snapshot();observations.append({'phase':label,'FD_delta':len(current)-len(expected),'fds':current})
    need(current==expected,'operational descriptor map changed')
    return current
'''
raw=raw.replace('\ndef run(packet,packet_binding,capture):',helpers+'\ndef run(packet,packet_binding,capture):')
raw=raw.replace("    mods=packet['module_bindings']", "    need(packet['ontology_execution_selection_binding']==EXECUTION,'exact reviewed Root successor executor selection required')\n    exact(EXECUTION)\n    mods=packet['module_bindings']")
raw=raw.replace("'control':ROOT/'product/lab/release-candidates/v1/interface/composite-operator-v1-completion-0001/revision-0003/control.py'", "'control':CONTROL")
raw=raw.replace("    required_active={tuple(sorted(v.items()))for v in [*own.values(),*mods.values()]}","    need(mods['control']=={'path':str(CONTROL.relative_to(ROOT)),'sha256':CONTROL_SHA},'exact reviewed successor control required')\n    required_active={tuple(sorted(v.items()))for v in [*own.values(),*mods.values()]}")
raw=raw.replace("    guard=None;entered=False;store=None;boundary=None;events=[];failure=None;exit_errors=[];fd0=len(os.listdir('/proc/self/fd'))", "    guard=None;entered=False;store=None;boundary=None;executor=None;events=[];failure=None;exit_errors=[]\n    operational_fds=None;initialization=None;initialization_fds=None;fd_observations=[];final_fds=None\n    emit('bootstrap-resources.json',{'raw_fds':RAW_BOOTSTRAP_FDS,'snapshot_point':'after only os/stat/fcntl imports; before argparse/importlib/fullSource/selectedruntime/ctypes imports'})")
raw=raw.replace("    try:\n        guard=module('_T32_current_guard_", "    try:\n        sys.path.insert(0,str(INSTALL/'deps')) # Selected vendor metadata precedes original API guard.verify.\n        guard=module('_T32_current_guard_")
raw=raw.replace("        sys.path.insert(0,str(INSTALL/'deps'))\n        for name", "        for name")
raw=raw.replace("        factory=selected_store.StoreFactory(original,generation,executor,boundary,selection)\n        def record", "        factory=selected_store.StoreFactory(original,generation,executor,boundary,selection)\n        initialization_fds=fd_snapshot()\n        initialization=runtime_initialization(RAW_BOOTSTRAP_FDS,initialization_fds,capture)\n        operational_fds=initialization_fds\n        emit('runtime-initialization-resources.json',{'raw_fds':RAW_BOOTSTRAP_FDS,'initialized_fds':initialization_fds,\n            'initialization':initialization,'operational_baseline_point':'after full selected Source/runtime/generation_store ctypes/boundary/factory initialization; before signedcatalog and native store effects'})\n        operational_fd_check(operational_fds,fd_observations,'before-four-case-block')\n        def record")
raw=raw.replace("        def record(label,value):\n            events.append({'case':label,**value});emit('case-%02d.json'%len(events),events[-1])", "        def record(label,value):\n            operational_fd_check(operational_fds,fd_observations,'after-case-'+label+'-before-receipt')\n            events.append({'case':label,**value});emit('case-%02d.json'%len(events),events[-1])\n            operational_fd_check(operational_fds,fd_observations,'after-case-'+label+'-receipt')")
raw=raw.replace("        if store is not None:\n            store.close()\n            if not(store.closed and store.root.is_dir()):exit_errors.append({'exception_class':'RetainedStorePostconditionFailure'})", "        if store is not None:\n            try:\n                store.close()\n                need(store.closed and store.root.is_dir(),'retained store close postcondition failed')\n            except BaseException:exit_errors.append(diagnostic(sys.exc_info()))")
raw=raw.replace("        if boundary is not None:\n", "        if executor is not None:\n            # Original complete installed/source/ABI executor proof is independent\n            # of expired technical operation authority and always runs on exit.\n            try:executor.guard()\n            except BaseException:exit_errors.append(diagnostic(sys.exc_info()))\n        if boundary is not None:\n")
raw=raw.replace("        fd_delta=len(os.listdir('/proc/self/fd'))-fd0\n        passed=failure is None and not exit_errors and len(events)==4 and fd_delta==0", "        try:\n            final_fds=fd_snapshot()\n            if operational_fds is not None:operational_fd_check(operational_fds,fd_observations,'after-all-exit-guards')\n        except BaseException:exit_errors.append(diagnostic(sys.exc_info()))\n        fd_delta=None if operational_fds is None or final_fds is None else len(final_fds)-len(operational_fds)\n        raw_total_delta=None if final_fds is None else len(final_fds)-len(RAW_BOOTSTRAP_FDS)\n        passed=failure is None and not exit_errors and len(events)==4 and operational_fds is not None and final_fds==operational_fds and fd_delta==0")
raw=raw.replace("            'FD_delta':fd_delta,", "            'FD_delta':fd_delta,'operational_FD_map_unchanged':operational_fds is not None and final_fds==operational_fds,\n            'raw_bootstrap_fds':RAW_BOOTSTRAP_FDS,'initialization_fds':initialization_fds,'initialization_evidence':initialization,\n            'raw_total_FD_delta':raw_total_delta,'final_fds':final_fds,'operational_fd_observations':fd_observations,\n            'old_attempt_FD_cause_directly_proven':False,")
(NEW/'qualify.py').write_text(raw)
