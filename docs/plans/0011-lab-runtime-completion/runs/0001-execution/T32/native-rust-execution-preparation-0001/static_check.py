"""Read frozen public inputs and run pure controls; never import executor/guards."""
import hashlib,json,os,runpy,sys,types
from pathlib import Path
HERE=Path(__file__).absolute().parent
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
def fds():
    rows={}
    for name in os.listdir('/proc/self/fd'):
        try:s=os.fstat(int(name));rows[name]=(s.st_dev,s.st_ino,s.st_mode)
        except OSError:continue
    return rows
before=fds()
inputs=json.loads((HERE/'inputs.json').read_bytes());binding=inputs['module_bindings']['control'];path=ROOT/binding['path'];raw=path.read_bytes()
assert hashlib.sha256(raw).hexdigest()==binding['sha256']
control=types.ModuleType('_T32_static_capture');control.__file__=str(path);exec(compile(raw,str(path),'exec'),control.__dict__)
def guard():
    assert control.capture(path,binding['sha256'])==raw
    for row in inputs['files']:
        p=Path(row['path']);p=p if p.is_absolute()else ROOT/p
        control.capture(p,row['sha256'],size=row['size_bytes'])
guard()
result=runpy.run_path(str(HERE/'pure_controls.py'),run_name='_owned_pure_controls')['main']()
guard()
assert before==fds()and 'ctypes'not in sys.modules
result.update({'all_selected_public_input_rows_entry_exit':len(inputs['files']),'FD_delta':0,'ctypes_imported':False})
with(HERE/'static-result.json').open('x')as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps(result,sort_keys=True))
