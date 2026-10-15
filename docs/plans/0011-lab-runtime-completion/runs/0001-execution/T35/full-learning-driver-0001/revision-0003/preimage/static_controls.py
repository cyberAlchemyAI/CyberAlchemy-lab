"""Pure owned software/observer controls; no Lab runtime constructors."""
import ast,hashlib,importlib.util,json,os,sys,tempfile,types
from unittest.mock import patch
from pathlib import Path
HERE=Path(__file__).resolve().parent

def require(value,message):
    if not value:raise AssertionError(message)

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module

def check():
    cases=[];C=load('_T35_pure_capture',HERE/'capture.py');O=load('_T35_pure_observe',HERE/'observe.py')
    root=Path(tempfile.mkdtemp(prefix='cal-T35-pure-owned-'));root.chmod(0o700);file=root/'record.json';file.write_bytes(b'{"owned":true}');file.chmod(0o600)
    selected=[root.stat().st_dev,root.stat().st_ino,root.stat().st_uid,root.stat().st_mode&0o777]
    require(C.read_owned(file,root,selected)==file.read_bytes(),'owned capture differs');cases.append('typed owned observation succeeds under exact root custody')
    for name,callback in [('non-null software pin',lambda:C.read(file,None)),('wrong owned root identity',lambda:C.read_owned(file,root,[0,0,os.getuid(),0o700])),('outside owned root',lambda:C.read_owned(Path('/etc/hostname'),root,selected)),('private key excluded',lambda:C.read_owned(root/'private.pem',root,selected))]:
        try:callback()
        except (ValueError,OSError):cases.append(name+' refuses')
        else:raise AssertionError(name+' accepted')
    file.rename(root/'retained-record.json');file.symlink_to(root/'retained-record.json')
    try:C.read_owned(file,root,selected)
    except (ValueError,OSError):cases.append('owned symlink refuses before leaf body read')
    else:raise AssertionError('owned symlink accepted')
    file.unlink();(root/'retained-record.json').rename(file)
    cases.append('all draft Python source parses')
    for path in HERE.glob('*.py'):ast.parse(path.read_bytes())
    # Exact original-security function transformed only by four source/method
    # substitutions; positive additionally removes one seven-line negative.
    pre=(HERE/'lifecycle-preimage.py').read_text();expected=pre.replace("'source8-lesson-fixture-participation'",'SOURCE_NAME').replace("P.ROOT/'product/lab/release-candidates/v1/interface/lesson-application-v3-action-0148/preparation.py'",'APPLICATION_METHOD').replace("method.parent.parent/'lesson-assessment-v2-action-0148/preparation.py'",'ASSESSMENT_METHOD').replace('tempfile.TemporaryDirectory(','OWNED_TEMPORARY(')
    security=(HERE/'security_lifecycle.py').read_text();require(security[security.index('def source8_lifecycle'):]==expected,'security extraction altered original logic')
    a=expected.index(' bad=copy.deepcopy(attachment)');b=expected.index(' application=M[',a);positive=(expected[:a]+expected[b:]).replace("return ['foreign-Session-attachment',",'return [')
    actual=(HERE/'positive_lifecycle.py').read_text();require(actual[actual.index('def source8_lifecycle'):]==positive,'positive delta changed original action path')
    cases.extend(['security exact original function plus four explicit selection substitutions','positive removes only declared seven-line negative and its label'])
    events=[];observer=O.Observer(HERE,events.append,False);observer.start()
    try:
        def swallowed():
            try:raise ValueError('DO-NOT-RECORD-PRIVATE-SENTINEL')
            except ValueError:return 'handled'
        require(observer.measure('synthetic-broad-catch',swallowed,lambda:{'metadata':True})=='handled','observer changed callback')
        require(any(e.get('monitor_event')=='raise' and e.get('exception_class')=='ValueError' for e in events),'actual raise code event missing')
        require(any(e.get('monitor_event')=='handled' and e.get('exception_class')=='ValueError' for e in events),'actual handled code event missing')
        require('DO-NOT-RECORD-PRIVATE-SENTINEL' not in json.dumps(events),'exception args leaked')
        require(any(e.get('sanitized_code_frames') for e in events if e.get('monitor_event')=='handled'),'code-only handled traceback missing')
        cases.append('actual sys.monitoring raise/handled observes class/code locations and omits exception args')
        def failing():raise RuntimeError('PRIMARY-PRIVATE-SENTINEL')
        def unavailable():raise LookupError('SECONDARY-PRIVATE-SENTINEL')
        try:observer.measure('synthetic-metadata-failure',failing,unavailable)
        except RuntimeError:cases.append('metadata failure preserves original primary exception')
        else:raise AssertionError('primary exception overwritten')
        require(observer.metadata_errors>0 and 'PRIMARY-PRIVATE-SENTINEL' not in json.dumps(events) and 'SECONDARY-PRIVATE-SENTINEL' not in json.dumps(events),'metadata/private exception trace leak')
        require(observer.callback_errors==0 and observer.dropped==0,'observer callback failed')
    finally:observer.close()
    # This substitutes only the observer's own instrumentation registration in
    # a pure process with no Lab callbacks/resources. Tool ownership must unwind.
    tool=next(i for i in [5,4] if sys.monitoring.get_tool(i) is None)
    original_register=sys.monitoring.register_callback;counter=0
    def interrupted_register(*args):
        nonlocal counter
        counter+=1
        if counter==2:raise RuntimeError('owned synthetic registration failure')
        return original_register(*args)
    partial=O.Observer(HERE,events.append,False)
    try:
        with patch.object(sys.monitoring,'register_callback',interrupted_register):partial.start()
    except RuntimeError:pass
    else:raise AssertionError('partial registration fixture did not fail')
    require(partial.tool is None and sys.monitoring.get_tool(tool) is None,'partial monitor registration leaked owned tool')
    cases.append('partial owned instrumentation registration cleans up own tool id')
    driver=load('_T35_pure_driver_import',HERE/'driver.py')
    episode=types.SimpleNamespace(root_managers={})
    managed=driver.OwnedTemporary(episode,'cal-T35-pure-managed-')
    with managed as name:
        owned=Path(name);(owned/'journal.json').write_bytes(b'{"pending":true}');(owned/'journal.json').chmod(0o600);managed.keep=True
    require(owned.exists() and (owned/'journal.json').exists(),'uncertain original was automatically deleted')
    cases.append('managed new owned original survives failed later retention and context exit')
    (owned/'journal.json').unlink();owned.rmdir()
    return {'schema_version':'lab-full-learning-pure-controls/v1-candidate','result':'PASS-pure-controls','checks':cases,'checks_count':len(cases),'Lab_runtime_constructors_executed':False,'real_Source_or_native_Reader_or_Service_or_Session_constructed':False,'authority_effect':'none','task_complete':False}

if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
