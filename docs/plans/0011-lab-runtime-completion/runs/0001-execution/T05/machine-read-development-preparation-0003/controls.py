"""Pure controls for Root after timed learning; never import API/Lab/native."""
import ast,copy,hashlib,importlib.util,json,os,tempfile
from pathlib import Path
HERE=Path(__file__).absolute().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
    R=load('_T05_pure_runner_shape',HERE/'run_machine_development_v3.py')
    O=load('_T05_pure_output',HERE/'owned_output.py')
    p=json.loads((HERE/'execution-selection-template.json').read_bytes());checks=[]
    original=R.exact(p['original_bindings']['original_tests']);owned=(HERE/'owned_machine_tests.py').read_bytes()
    assert R.methods(original,'MachineTransport')==R.methods(owned,'MachineTransport') and len(R.methods(owned,'MachineTransport'))==14;checks.append('all14 original test method ASTs identical')
    for role,row in p['owned_code_bindings'].items():assert hashlib.sha256((R.ROOT/row['path']).read_bytes()).hexdigest()==row['sha256']
    checks.append('true selected owned code6 pins exact')
    def class_methods(raw,classname):
        tree=ast.parse(raw)
        return {n.name:n for c in tree.body if isinstance(c,ast.ClassDef) and c.name==classname for n in c.body if isinstance(n,ast.FunctionDef) and not n.name.startswith('test_')}
    parent_raw=R.exact(p['original_bindings']['parent_tests']);parent_owned=(HERE/'owned_parent_sessions.py').read_bytes()
    old=class_methods(parent_raw,'Sessions');new=class_methods(parent_owned,'Sessions')
    assert set(old)==set(new)
    assert all(ast.dump(old[k],include_attributes=False)==ast.dump(new[k],include_attributes=False) for k in old if k!='invoke')
    # Normalize only the two explicitly reviewed observer-plumbing AST changes.
    expected=copy.deepcopy(old['invoke'])
    for node in ast.walk(expected):
        if isinstance(node,ast.ImportFrom) and node.module=='fixture_observation':node.module='owned_observer'
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='record':node.args.insert(0,ast.Attribute(value=ast.Name(id='self',ctx=ast.Load()),attr='OWNED_OUTPUT',ctx=ast.Load()))
    assert ast.dump(expected,include_attributes=False)==ast.dump(new['invoke'],include_attributes=False)
    tree=ast.parse(owned)
    imports=[n for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
    assert any(n.level==1 and n.module=='owned_parent_sessions' for n in imports)
    assert any(n.level==1 and n.module=='owned_observer' for n in imports)
    for raw in (owned,parent_owned):
        assert not any(isinstance(n,ast.ImportFrom) and n.module and 'fixture_observation' in n.module for n in ast.walk(ast.parse(raw)))
    function=lambda raw:next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef) and n.name=='capture_path')
    assert ast.get_source_segment((HERE/'capture.py').read_text(),function((HERE/'capture.py').read_bytes()))==ast.get_source_segment((HERE/'run_machine_development_v3.py').read_text(),function((HERE/'run_machine_development_v3.py').read_bytes()))
    checks.append('owned parent helper ASTs retained; only invoke observer import/call plumbing changes')
    checks.append('both actual fixture-call routes select owned observer; capture helper and inline source identical')
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
    C=load('_T05_pure_capture',HERE/'capture.py')
    with tempfile.TemporaryDirectory(prefix='cal-T05-pure-capture-') as tmp:
        root=Path(tmp);leaf=root/'metadata.json';raw=b'{"OWNED_INERT":true}\n';leaf.write_bytes(raw);pin=hashlib.sha256(raw).hexdigest()
        assert C.capture_path(leaf,pin)==raw;checks.append('anchored exact original bytes returned once with final leaf-parent FD retained')
        refusal('wrong captured digest refuses',lambda:C.capture_path(leaf,'0'*64))
        refusal('bounded capture refuses',lambda:C.capture_path(leaf,pin,maximum=1))
        link=root/'leaf-link';link.symlink_to(leaf);refusal('leaf symlink refuses before body return',lambda:C.capture_path(link,pin))
        folder=root/'folder';folder.mkdir();(folder/'metadata').write_bytes(raw);alias=root/'parent-link';alias.symlink_to(folder,target_is_directory=True);refusal('ancestor symlink refuses before body return',lambda:C.capture_path(alias/'metadata',pin))
        assert R.exact(p['owned_code_bindings']['runner'])==(HERE/'run_machine_development_v3.py').read_bytes();checks.append('runner own exact uses descriptor anchored byte capture')
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
