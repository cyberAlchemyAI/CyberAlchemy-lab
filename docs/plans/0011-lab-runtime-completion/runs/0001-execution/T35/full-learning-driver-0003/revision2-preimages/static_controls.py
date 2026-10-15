"""Pure owned software/observer controls; no Lab runtime constructors."""
import ast,hashlib,importlib.util,json,os,shutil,sys,tempfile,types
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
    old=(HERE/'preimage/driver.py').read_text();new=(HERE/'driver.py').read_text()
    a=old.index('        self.W.privacy(reply);decision=B.classify(reply)');b=old.index('    def pair(',a)
    require(old[a:b]==new[new.index('        self.W.privacy(reply);decision=B.classify(reply)'):new.index('    def pair(')],'caller handling body changed')
    cases.append('exact original caller handling body moved intact into timed qualification method')
    a=old.index("        if self.cohort=='security':",old.index('    def pair('));b=old.index('        return self.invoke(surface,request',a)
    body='\n'.join(line[4:] for line in old[a:b].splitlines()[1:])+'\n'
    a=new.index('    def security_negative(');a=new.index('\n',a)+1;b=new.index('    def append(',a)
    require(new[a:b]==body,'security negative construction/order changed')
    cases.append('exact original security negative body moved intact into separate timed qualification method')
    for filename in ['capture.py','positive_lifecycle.py','security_lifecycle.py','selection.schema.json','lifecycle-preimage.py','caller-lines-322-411-preimage.txt']:
        require((HERE/filename).read_bytes()==(HERE/'preimage'/filename).read_bytes(),'preserved lifecycle/custody input changed')
    cases.append('six complete lifecycle/custody/selection originals retained byte for byte')

    events=[];source_rows={'static_controls.py':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()};observer=O.Observer(HERE,events.append,False,source_rows,C.read);observer.start()
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
    # Exercise actual retention method without constructing any Lab resource.
    for fail_snapshot in [False,True]:
        episode=driver.Episode.__new__(driver.Episode)
        episode.root_managers={};episode.roots=[];episode.root_identities={};episode.retained=[]
        metadata=[];episode.emit=metadata.append
        managed=driver.OwnedTemporary(episode,'cal-T35-pure-retention-')
        outside=Path(tempfile.mkdtemp(prefix='cal-T35-pure-inert-outside-'));outside.chmod(0o700)
        outside_file=outside/'inert.json';outside_file.write_bytes(b'INERT-DO-NOT-COPY');outside_file.chmod(0o600)
        try:
            with managed as name:
                owned=Path(name);episode.roots.append(owned);episode.root_identities[owned]=driver.identity(owned.stat())
                journal=owned/'journal.json';journal.write_bytes(b'{"pending":true}');journal.chmod(0o600)
                if fail_snapshot:journal.unlink();journal.symlink_to(outside_file)
                before_copies=set(Path('/tmp').glob('cal-T35-private-pending-*'))
                try:episode.preserve_pending(owned)
                except (ValueError,OSError):require(fail_snapshot,'unexpected anchored observation failure')
                else:require(not fail_snapshot,'symlink observation accepted')
                require(managed.keep and episode.retained[0]['original_retained'],'retention not marked before observation')
                require(before_copies==set(Path('/tmp').glob('cal-T35-private-pending-*')),'redundant copy directory created')
                require(outside_file.read_bytes()==b'INERT-DO-NOT-COPY' and len(list(outside.iterdir()))==1,'retention wrote outside original')
            require(owned.exists(),'uncertain original deleted at managed context exit')
            if not fail_snapshot:
                require(metadata[-1]['optional_second_copy_created'] is False and metadata[-1]['files']==1,'anchored retention metadata differs')
                require('INERT-DO-NOT-COPY' not in json.dumps(metadata),'private observation body leaked')
            cases.append('actual original-only retention '+('refuses bad observation while preserving original' if fail_snapshot else 'records anchored metadata without destination writes'))
        finally:shutil.rmtree(managed.path);shutil.rmtree(outside)
    return {'schema_version':'lab-full-learning-pure-controls/v1-candidate','result':'PASS-pure-controls','checks':cases,'checks_count':len(cases),'Lab_runtime_constructors_executed':False,'real_Source_or_native_Reader_or_Service_or_Session_constructed':False,'authority_effect':'none','task_complete':False}

if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
