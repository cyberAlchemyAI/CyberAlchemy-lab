"""Independent negative probe of a private owned copy of the public T03 draft."""
import hashlib,importlib.abc,importlib.util,json,sys,tempfile
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).absolute().parents[6]
HERE=Path(__file__).absolute().parent
source=ROOT/'product/lab/release-candidates/v1/interface/source-input-capture-v1-completion-0001/capture.py'
raw=source.read_bytes();pin=hashlib.sha256(raw).hexdigest()
results=[]
with tempfile.TemporaryDirectory(prefix='cal-root-T03-draft-') as scratch:
    root=Path(scratch);root.chmod(0o700);code=root/'capture.py';code.write_bytes(raw)
    payload=root/'payload.bin';payload.write_bytes(b'owned probe input')
    row={'path':'payload.bin','sha256':hashlib.sha256(payload.read_bytes()).hexdigest()}
    class Loader(importlib.abc.SourceLoader):
        selected_source_sha256=pin
        def get_filename(self,name):return str(code)
        def get_data(self,path):
            assert path==str(code)
            return raw
        def get_code(self,name):return compile(raw,str(code),'exec',dont_inherit=True)
    def load(label):
        name='_root_T03_draft_probe_'+label
        spec=importlib.util.spec_from_file_location(name,code,loader=Loader())
        m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
        return m
    control=load('control');assert control.verify_all(root,[row],code_sha256=pin)==1
    results.append({'case':'fresh-byte-control','result':'PASS'})
    ordinary=load('ordinary_refusal')
    bad=dict(row,sha256='0'*64)
    try:ordinary.verify_all(root,[bad],code_sha256=pin)
    except ValueError:results.append({'case':'changed-byte-digest','result':'REFUSED'})
    else:raise AssertionError('ordinary corrupt digest was accepted')
    mutated=load('need_callback_replaced');mutated.need=lambda *args:None
    try:mutated.verify_all(root,[bad],code_sha256=pin)
    except ValueError as error:results.append({'case':'need-callback-substitution-plus-corrupt-input','result':'REFUSED','exception_class':type(error).__name__})
    else:results.append({'case':'need-callback-substitution-plus-corrupt-input','result':'ACCEPTED-CORRUPT-INPUT'})
receipt={'schema_version':'lab-T03-root-draft-callback-probe/v1-candidate',
 'source_binding':{'path':str(source.relative_to(ROOT)),'sha256':pin},
 'scope':'Exact public draft bytes executed under independently supplied loader SHA at true owned temporary copy origin; only the new copied module and owned payload mutated.',
 'source_or_original_modules_mutated':False,'authority_effect':'none','task_complete':False,
 'results':results,'checked_at':datetime.now(timezone.utc).isoformat()}
out=HERE/'root-draft-callback-probe-0001.json'
with out.open('x') as f:json.dump(receipt,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps({'path':str(out),'source_sha256':pin,'results':results}))
