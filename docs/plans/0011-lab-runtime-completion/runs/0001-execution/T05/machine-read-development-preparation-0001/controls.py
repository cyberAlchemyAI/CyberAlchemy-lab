"""Pure controls for Root after timed learning; never import API/Lab/native."""
import ast,copy,hashlib,importlib.util,json,os,tempfile
from pathlib import Path
HERE=Path(__file__).absolute().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
    R=load('_T05_pure_runner_shape',HERE/'run_machine_development_v1.py')
    O=load('_T05_pure_output',HERE/'owned_output.py')
    p=json.loads((HERE/'execution-selection-template.json').read_bytes());checks=[]
    original=R.exact(p['original_bindings']['original_tests']);owned=(HERE/'owned_machine_tests.py').read_bytes()
    assert R.methods(original,'MachineTransport')==R.methods(owned,'MachineTransport') and len(R.methods(owned,'MachineTransport'))==14;checks.append('all14 original test method ASTs identical')
    for role,row in p['owned_code_bindings'].items():assert hashlib.sha256((R.ROOT/row['path']).read_bytes()).hexdigest()==row['sha256']
    checks.append('true selected owned code4 pins exact')
    def refusal(label,fn):
        try:fn()
        except (ValueError,OSError):checks.append(label)
        else:raise AssertionError(label+' accepted')
    refusal('inactive output/coordinator template refuses',lambda:R.shape(p))
    active=copy.deepcopy(p);active['output_custody']={'root':'/tmp/cal-T05-pure-shape-unused','identity':[1,1,os.getuid(),0o700]};active['runtime_coordinator_receipt_binding']={'path':'owned-not-opened.json','sha256':'0'*64}
    R.shape(active);checks.append('closed active shape accepted without executing runtime')
    for key,value in [('expected_tests',7),('max_session_seconds',901),('final_qualification',True),('api_source_binding',active['api_profile_binding']),('mode','final-qualified')]:
        q=copy.deepcopy(active);q[key]=value;refusal('closed shape refuses '+key,lambda q=q:R.shape(q))
    q=copy.deepcopy(active);q['actor']={};refusal('unknown authority/input field refuses',lambda:R.shape(q))
    fd0=len(os.listdir('/proc/self/fd'))
    with tempfile.TemporaryDirectory(prefix='cal-T05-pure-output-') as tmp:
        path=Path(tmp);path.chmod(0o700);st=path.stat();c={'root':tmp,'identity':[st.st_dev,st.st_ino,st.st_uid,0o700]}
        output=O.Output(c)
        try:
            output.write('result.json',{'OWNED_INERT':True});output.observe({'OWNED_INERT':True})
            assert (path/'result.json').stat().st_mode&0o777==0o600;checks.append('exclusive anchored600 own output')
            refusal('same leaf refuses preserves first bytes',lambda:output.write('result.json',{'FOREIGN':True}))
            assert json.loads((path/'result.json').read_bytes())=={'OWNED_INERT':True}
            refusal('child path refuses',lambda:output.write('../foreign.json',{}))
        finally:output.close()
        refusal('uncertain prior attempt cannot automatically retry',lambda:O.Output(c))
    with tempfile.TemporaryDirectory(prefix='cal-T05-pure-conflict-') as tmp:
        path=Path(tmp);path.chmod(0o700);st=path.stat();c={'root':tmp,'identity':[st.st_dev,st.st_ino,st.st_uid,0o700]};(path/'unrelated').write_bytes(b'OWNED_INERT')
        refusal('occupied root refuses before selected output/runtime',lambda:O.Output(c));assert list(path.iterdir())==[path/'unrelated']
        q=copy.deepcopy(c);q['identity'][1]+=1;refusal('wrong custody inode refuses',lambda:O.Output(q))
    assert len(os.listdir('/proc/self/fd'))==fd0;checks.append('owned descriptor balance')
    print(json.dumps({'result':'PASS-pure-T05-component-controls','checks':checks,'FD_delta':0,'API_or_Lab_or_native_imported':False,'runtime_tests_executed':False,'whole14_runtime_or_task_qualified':False,'authority_effect':'none'},sort_keys=True))
if __name__=='__main__':main()
