"""Independent exact-byte T32 review wrapper; runs only reviewed inert controls."""
import ast
import contextlib
import hashlib
import importlib.abc
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import sys
import traceback
import types

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
BASE = ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T32'
P = BASE/'native-lifecycle-recovery-adoption-0002'
OWN = Path(__file__).parent
HH = 'ca485b44ece84fdd27aa3798bd34ffc7cfb48caf2dfdcba37d62a14161e4fc00'
MF = '1585783f766fcc3192248335ac6d05893f406816efc07c762c658f700191224a'
CP = 'b41f1914e0d6a9be125e228525ca92d1b28d853be79c118adffc040bcf01f0fa'

def sha(raw): return hashlib.sha256(raw).hexdigest()
def need(v, why):
    if not v: raise ValueError(why)
def output(name, value):
    with (OWN/name).open('xb') as stream:
        stream.write((json.dumps(value,sort_keys=True,indent=2)+'\n').encode())
def bootstrap_capture():
    path=P/'capture.py'
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        a=os.fstat(fd);raw=os.read(fd,65536);b=os.fstat(fd)
        need(stat.S_ISREG(a.st_mode) and a.st_size==len(raw)<65536 and
             (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==
             (b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns) and sha(raw)==CP,
             'independent capture helper bootstrap differs')
    finally: os.close(fd)
    module=types.ModuleType('_independent_T32_capture')
    module.__file__=str(path)
    exec(compile(raw,str(path),'exec'),module.__dict__)
    need(module.capture_path(path,CP)==raw,'helper anchored origin differs')
    return module.capture_path

def main():
    before=len(os.listdir('/proc/self/fd'))
    capture=bootstrap_capture()
    handoff_raw=capture(P/'HANDOFF.json',HH)
    manifest_raw=capture(P/'source-manifest.json',MF)
    handoff=json.loads(handoff_raw);manifest=json.loads(manifest_raw)
    rows=manifest['files'];need(len(rows)==110,'110 selected rows required')
    cache={};ledger=[]
    for row in rows:
        path=Path(row['path'])
        if not path.is_absolute(): path=ROOT/path
        need(str(path) not in cache,'duplicate selected origin')
        raw=capture(path,row['sha256'])
        need(len(raw)==row['size_bytes'],'selected size differs')
        cache[str(path)]=raw
        ledger.append({'path':row['path'],'sha256':sha(raw),'size_bytes':len(raw)})
    original=json.loads(cache[str(P/'original-component-manifest.json')])
    mapping=json.loads(cache[str(P/'parent-declaration-map.json')])['declarations']
    need(len(mapping)==61,'all61 original declarations required')
    represented=[]
    for entry in mapping:
        row=entry['original_declaration'];table=entry['original_table'];index=entry['original_index']
        need(original[table][index]==row,'original declaration mapping differs')
        selected=entry['selected_same_origin'];p=Path(row['path'])
        if not p.is_absolute():p=ROOT/p
        target=Path(selected['path'])
        if not target.is_absolute():target=ROOT/target
        need(p==target and selected['sha256']==row['sha256'] and
             selected['size_bytes']==row['size_bytes'],'original origin or bytes relabeled')
        raw=cache[str(p)]
        need(sha(raw)==row['sha256'] and len(raw)==row['size_bytes'],'original bytes not captured')
        if 'mode' in row:need(stat.S_IMODE(p.stat().st_mode)==row['mode'],'original mode differs')
        represented.append((table,index))
    need(len(set(represented))==61,'duplicate original declaration mapping')
    oldp=BASE/'native-lifecycle-recovery-adoption-0001'
    prior=json.loads(cache[str(oldp/'source-manifest.json')])
    actual={(r['path'],r['sha256'],r['size_bytes'])for r in rows}
    need(all((r['path'],r['sha256'],r['size_bytes'])in actual for r in prior['files']),
         'predecessor selected row dropped')
    extra_current=[]
    for original_row in json.loads(cache[str(P/'ORIGINAL-INPUTS.json')]):
        origin=ROOT/original_row['path']
        raw=capture(origin,original_row['sha256'])
        need(raw==cache[str(ROOT/original_row['preimage_path'])],
             'original lifecycle preimage or current source differs')
        extra_current.append({'path':original_row['path'],'sha256':sha(raw),'size_bytes':len(raw)})
    class CapturedLoader(importlib.abc.Loader):
        def __init__(self,path):self.path=path
        def create_module(self,spec):return None
        def exec_module(self,module):
            module.__file__=str(self.path)
            exec(compile(cache[str(self.path)],str(self.path),'exec'),module.__dict__)
    class CapturedFinder(importlib.abc.MetaPathFinder):
        def find_spec(self,fullname,path=None,target=None):
            if fullname.startswith('_Root_T32_inert_')and '.'in fullname:
                leaf=fullname.split('.',1)[1]
                need(leaf in {'private_io','capture','selected_store'},'unreviewed inert import')
                p=P/(leaf+'.py')
                return importlib.util.spec_from_loader(fullname,CapturedLoader(p),origin=str(p))
            return None
    finder=CapturedFinder();sys.meta_path.insert(0,finder)
    namespace={'__file__':str(P/'inert_controls.py'),'__name__':'_independent_T32_controls'}
    stdout=io.StringIO();failure=None
    try:
        with contextlib.redirect_stdout(stdout):
            exec(compile(cache[str(P/'inert_controls.py')],str(P/'inert_controls.py'),'exec'),namespace)
            namespace['main']()
    except BaseException:
        failure=traceback.format_exc()
    finally:
        sys.meta_path.remove(finder)
    post=[]
    for row in rows:
        path=Path(row['path'])
        if not path.is_absolute():path=ROOT/path
        raw=capture(path,row['sha256'])
        need(raw==cache[str(path)],'selected bytes changed across inert controls')
        post.append({'path':row['path'],'sha256':sha(raw),'size_bytes':len(raw)})
    for selected in extra_current:
        need(len(capture(ROOT/selected['path'],selected['sha256']))==selected['size_bytes'],'current original changed across controls')
    need(capture(P/'HANDOFF.json',HH)==handoff_raw and capture(P/'source-manifest.json',MF)==manifest_raw,
         'frozen package metadata changed')
    after=len(os.listdir('/proc/self/fd'))
    need(after==before,'review wrapper FD imbalance')
    parsed=json.loads(stdout.getvalue())if failure is None else None
    if parsed is not None:need(parsed['result']=='PASS-owned-inert-only'and len(parsed['checks'])==7,'actual inert results differ')
    receipt={'schema_version':'lab-T32-independent-inert-review/v1','authority_effect':'none',
        'result':'FAIL'if failure else 'PASS-owned-inert-only','handoff_sha256':HH,'source_manifest_sha256':MF,
        'selected_rows_entry':len(ledger),'selected_rows_exit':len(post),'all110_current_bytes_conserved':True,
        'original_declarations':61,'extra_current_originals':extra_current,'predecessor_selected_rows':len(prior['files']),
        'captured_code_executed_at_true_origins':True,'actual_control_stdout':stdout.getvalue(),
        'actual_control_result':parsed,'initial_failure':failure,'FD_delta':after-before,
        'API_native_installer_permission_constructors_called':False,'native_recovery_qualified':False,
        'runtime_or_task_complete':False}
    output('selected-rows-entry-exit-0001.json',{'entry':ledger,'exit':post})
    output('controls-result-0001.json',receipt)
    print(json.dumps({k:receipt[k]for k in ('result','selected_rows_entry','selected_rows_exit','original_declarations','FD_delta','initial_failure')},sort_keys=True))
    if failure:raise SystemExit(1)

if __name__=='__main__':main()
