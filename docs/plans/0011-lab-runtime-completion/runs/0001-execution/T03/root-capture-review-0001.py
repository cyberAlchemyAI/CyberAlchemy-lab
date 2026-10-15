"""Independent physical and callback controls on independently pinned public bytes."""
import argparse,hashlib,importlib.abc,importlib.util,json,os,sys,tempfile
from contextlib import contextmanager
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).absolute().parents[6]
HERE=Path(__file__).absolute().parent
parser=argparse.ArgumentParser();parser.add_argument('--kernel-sha256',required=True);parser.add_argument('--output',required=True)
args=parser.parse_args()
kernel=ROOT/'product/lab/release-candidates/v1/interface/source-input-capture-v1-completion-0001/capture.py'
raw=kernel.read_bytes();assert hashlib.sha256(raw).hexdigest()==args.kernel_sha256
cases=[]
@contextmanager
def fixture(label):
    with tempfile.TemporaryDirectory(prefix='cal-root-T03-review-') as scratch:
        root=Path(scratch);root.chmod(0o700);code=root/'capture.py';code.write_bytes(raw)
        nested=root/'inputs';nested.mkdir();payload=nested/'value';payload.write_bytes(b'independent owned input')
        row={'path':'inputs/value','sha256':hashlib.sha256(payload.read_bytes()).hexdigest()}
        class Loader(importlib.abc.SourceLoader):
            selected_source_sha256=args.kernel_sha256
            def get_filename(self,name):return str(code)
            def get_data(self,path):
                assert path==str(code)
                return raw
            def get_code(self,name):return compile(raw,str(code),'exec',dont_inherit=True)
        name='_root_T03_independent_'+label
        spec=importlib.util.spec_from_file_location(name,code,loader=Loader());m=importlib.util.module_from_spec(spec)
        sys.modules[name]=m;spec.loader.exec_module(m)
        try:yield m,root,code,payload,row
        finally:sys.modules.pop(name,None)
def record(label,callback,refusal=False):
    before=len(os.listdir('/proc/self/fd'))
    try:callback()
    except (ValueError,OSError) as error:
        assert refusal,label
        result='REFUSED';error_class=type(error).__name__
    else:
        assert not refusal,label+' unexpected acceptance'
        result='PASS';error_class=None
    assert len(os.listdir('/proc/self/fd'))==before,label+' descriptor leak'
    cases.append({'case':label,'result':result,'exception_class':error_class,'FD_count_restored':True})

with fixture('bytes') as (m,root,code,payload,row):
    record('full fresh table',lambda: m.verify_all(root,[row],code_sha256=args.kernel_sha256))
    def same_bytes():assert m.capture_one(root,row,code_sha256=args.kernel_sha256)==payload.read_bytes()
    record('exact captured bytes',same_bytes)
    record('wrong independent digest',lambda:m.verify_all(root,[dict(row,sha256='0'*64)],code_sha256=args.kernel_sha256),True)
    record('wrong independent code pin',lambda:m.verify_all(root,[row],code_sha256='0'*64),True)
    record('duplicate locator',lambda:m.verify_all(root,[row,row],code_sha256=args.kernel_sha256),True)

for label in ['leaf-replaced-same-bytes','leaf-mutated-in-place','ancestor-replaced-same-bytes','kernel-changed','read-callback','check-callback','need-callback','nested-scope']:
    with fixture(label.replace('-','_')) as (m,root,code,payload,row):
        def attack():
            with m.scope(root,args.kernel_sha256) as batch:
                parts=tuple(payload.parts[1:]);batch.read(parts,row['sha256'])
                if label=='leaf-replaced-same-bytes':
                    new=payload.with_name('replacement');new.write_bytes(payload.read_bytes());new.replace(payload)
                elif label=='leaf-mutated-in-place':payload.write_bytes(b'changed owned input')
                elif label=='ancestor-replaced-same-bytes':
                    prior=root/'detached';payload.parent.rename(prior);(root/'inputs').mkdir();(root/'inputs/value').write_bytes((prior/'value').read_bytes())
                elif label=='kernel-changed':code.write_bytes(raw+b'\n# independent mutation\n')
                elif label=='read-callback':m.Batch.read=lambda *unused:None
                elif label=='check-callback':m.Batch.check=lambda *unused:None
                elif label=='need-callback':m.need=lambda *unused:None
                elif label=='nested-scope':
                    with m.scope(root,args.kernel_sha256):pass
        record(label,attack,True)

with fixture('exception') as (m,root,code,payload,row):
    def exception_then_fresh():
        try:
            with m.scope(root,args.kernel_sha256) as batch:
                batch.read(tuple(payload.parts[1:]),row['sha256']);raise RuntimeError('owned deliberate exception')
        except RuntimeError:pass
        assert not getattr(m._ACTIVE,'value',False)
        assert m.verify_all(root,[row],code_sha256=args.kernel_sha256)==1
    record('exception cleanup permits new fresh invocation',exception_then_fresh)

assert hashlib.sha256(kernel.read_bytes()).hexdigest()==args.kernel_sha256
out=HERE/args.output;assert out.parent==HERE and not out.exists()
receipt={'schema_version':'lab-T03-root-independent-capture-review/v1-candidate',
 'kernel_binding':{'path':str(kernel.relative_to(ROOT)),'sha256':args.kernel_sha256},
 'cases':cases,'status':'PASS-pure-helper-controls-only','authority_effect':'none','task_complete':False,
 'production_files_modified':False,'old_original_callbacks_modified':False,
 'scope':'Public selected helper exact byte copies executed at their true new owned origins under independently supplied loader SHA. Only owned fixture input/code and new copied-module callbacks changed. No producer, Session, effect, schema, policy or current runtime integration qualified.',
 'checked_at':datetime.now(timezone.utc).isoformat()}
with out.open('x') as f:json.dump(receipt,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps({'status':receipt['status'],'cases':len(cases),'path':str(out)}))
