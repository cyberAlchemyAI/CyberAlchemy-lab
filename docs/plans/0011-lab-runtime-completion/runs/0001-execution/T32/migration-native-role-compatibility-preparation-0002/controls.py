"""Bounded stdlib-only static/inert checks; never calls native/probe/factory or live Source guard.

Synthetic child streams below are fixtures for evidence-parser controls only.
They cannot activate the null scope and are deleted with their owned temp root.
No API/Source guard/installer/native/runtime imports or operations occur.
"""
import ast,base64,copy,hashlib,importlib.util,json,os,sys,tempfile,types
from pathlib import Path
HERE=Path(__file__).parent;ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
V=HERE.parent/'native-lifecycle-recovery-adoption-0003'
ORIGINAL=ROOT/'implementation/lab-ontology/candidates/v1/migration/adapters'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def parse(p):return ast.parse(p.read_bytes(),filename=str(p))
def methods(p,name):return {n.name:n for n in next(n for n in parse(p).body if isinstance(n,ast.ClassDef)and n.name==name).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
def shape(n):return ast.dump(n,include_attributes=False)
def need(ok,msg):
    if not ok:raise ValueError(msg)
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);sys.modules[name]=value
    exec(compile(path.read_bytes(),str(path),'exec'),value.__dict__);return value
pkg=types.ModuleType('_cal_o05_inert');pkg.__path__=[str(HERE)];sys.modules[pkg.__name__]=pkg
capture=module(pkg.__name__+'.capture',HERE/'capture.py')
contract=module(pkg.__name__+'.execution_contract',HERE/'execution_contract.py')
io=module(pkg.__name__+'.private_io',HERE/'private_io.py')
checks=[]
def check(name,fn):
    fn();checks.append(name)
def refusal(fn):
    try:fn()
    except (ValueError,KeyError,OSError):return
    raise AssertionError('expected inert refusal')

def main():
    before=len(os.listdir('/proc/self/fd'))
    paths=[p for p in HERE.glob('*.py')]
    entries=json.loads((HERE/'input-selection.json').read_bytes())['inputs']
    saved={str(p):sha(capture.capture_path(p,maximum=32*1024*1024))for p in paths}
    for row in entries:
        p=ROOT/row['path'];raw=capture.capture_path(p,row['sha256'],maximum=32*1024*1024)
        need(len(raw)==row['size_bytes'],'named public source size differs');saved[str(p)]=sha(raw)
    check('all-selected-staged-Python-parses',lambda:[parse(p)for p in paths])
    old=methods(V/'postimages/migration.py','SourceTranslation');new=methods(HERE/'migration.py','SourceTranslation')
    check('all10-original-translator-methods-retained',lambda:need(set(old)==set(new)and len(old)==10,'original translator method set differs'))
    check('8-original-translator-algorithms-AST-identical',lambda:need(all(shape(old[k])==shape(new[k])for k in old if k not in{'__init__','guard'}),'original translator algorithm differs'))
    oldtests=methods(ORIGINAL/'test_import.py','ImportGuards');newtests=methods(HERE/'import_guards.py','ImportGuards')
    check('all48-original-hostile-methods-AST-identical',lambda:need(all(k in newtests and shape(v)==shape(newtests[k])for k,v in oldtests.items()if k.startswith('test_'))and sum(k.startswith('test_')for k in oldtests)==48,'original hostile test changed'))
    check('all-original-hostile-support-methods-except-bootstrap-identical',lambda:need(all(k in newtests and shape(v)==shape(newtests[k])for k,v in oldtests.items()if k!='setUpClass'),'original hostile support method changed'))
    of={n.name:n for n in parse(V/'postimages/migration.py').body if isinstance(n,ast.FunctionDef)};nf={n.name:n for n in parse(HERE/'migration.py').body if isinstance(n,ast.FunctionDef)}
    check('all-five-original-pure-draft-pointer-serialization-functions-identical',lambda:need(all(shape(of[k])==shape(nf[k])for k in('record_bytes','pointer','schema','semantic_draft','governance_draft')),'original draft helper differs'))
    ow=next(n for n in of['build'].body if isinstance(n,ast.With));nw=copy.deepcopy(next(n for n in nf['build'].body if isinstance(n,ast.With)))
    class Normalize(ast.NodeTransformer):
        def visit_Call(self,n):
            self.generic_visit(n)
            if isinstance(n.func,ast.Name)and n.func.id=='SourceTranslation':n.keywords=[k for k in n.keywords if k.arg!='execution_contract']
            return n
        def visit_Constant(self,n):
            if n.value=='native_role':n.value='native_executable'
            elif n.value=='explicitv2 current native role differs':n.value='original native source/execution bytes differ'
            return n
    nw=Normalize().visit(nw)
    check('entire-original-build-algorithm-preserved-after-explicit-constructor-and-role-join',lambda:need(shape(ow)==shape(nw),'undeclared migration build algorithm delta'))
    original_scope=json.loads((ORIGINAL/'build-scope.json').read_bytes())
    check('historical480-scope-exact',lambda:need(sha((ORIGINAL/'build-scope.json').read_bytes())==contract.HISTORICAL['sha256']and original_scope['native_executable']['sha256']==contract.OLD_NATIVE,'historical scope changed'))
    # Execute only the actual guard's path predicate and original need() call.
    # No contract/native/factory invocation and no candidate output is created.
    g=methods(HERE/'execution_contract.py','MigrationExecutionContract')['guard']
    path_guard=next(n for n in g.body if isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)
        and len(n.value.args)>1 and isinstance(n.value.args[1],ast.Constant)
        and n.value.args[1].value=='explicit distinct successor output root required')
    statement=ast.Module(body=[path_guard],type_ignores=[]);ast.fix_missing_locations(statement)
    predicate_code=compile(statement,str(HERE/'execution_contract.py'),'exec')
    def path_gate(value):
        env={'Path':Path,'output':Path(value),'s':{'output_root':value},'old':original_scope,'need':contract.need}
        exec(predicate_code,env)
    old_output=Path(original_scope['output_root'])
    check('MIG01-sibling-output-positive',lambda:path_gate(str(old_output.with_name('0002-inert-not-created'))))
    check('MIG01-textual-prefix-sibling-positive',lambda:path_gate(str(old_output.with_name(old_output.name+'0-inert-not-created'))))
    for label,value in [('equal',str(old_output)),('nested-descendant',str(old_output/'inert-not-created')),
                        ('ancestor',str(old_output.parent)),('absolute',str(ROOT/old_output.with_name('0002-inert-not-created'))),
                        ('parent-traversal',str(old_output.parent/'..'/'inert-not-created')),
                        ('noncanonical',str(old_output.parent)+'//0002-inert-not-created')]:
        check('MIG01-'+label+'-refuses',lambda value=value:refusal(lambda:path_gate(value)))
    old_package=ROOT/old_output
    original_package={p.relative_to(old_package).as_posix():sha(capture.capture_path(p,maximum=32*1024*1024))
                      for p in old_package.rglob('*')if p.is_file()}
    check('historical-v3-strict-native-equality-preserved',lambda:need("pin = translator.scope['native_executable']"in(V/'postimages/migration.py').read_text()and 'original native source/execution bytes differ'in(V/'postimages/migration.py').read_text(),'old native route broadened'))
    scope_pin={'path':(HERE/'scope-template.json').relative_to(ROOT).as_posix(),'sha256':sha((HERE/'scope-template.json').read_bytes())}
    check('inactive-template-refuses-without-factory-or-native',lambda:refusal(lambda:contract.MigrationExecutionContract(scope_pin,scope_pin['sha256'],None)))
    check('missing-explicit-scope-refuses',lambda:refusal(lambda:contract.MigrationExecutionContract(None,'0'*64,None)))
    check('duplicate-contract-key-refuses',lambda:refusal(lambda:contract.parse(b'{"a":1,"a":2}')))
    check('nonfinite-contract-value-refuses',lambda:refusal(lambda:contract.parse(b'{"a":NaN}')))
    check('old-execution-role-is-distinct-from-selected574',lambda:need(contract.NATIVE!=contract.OLD_NATIVE and json.loads(contract.bytes_for(contract.EXECUTION))['ontology_role']['sha256']==contract.NATIVE,'distinct execution selection lost'))
    archive_row=next({k:r[k]for k in('path','sha256')}for r in entries if r['path'].endswith('migration/candidate/0001/native.snapshot'))
    archive=json.loads(contract.bytes_for(archive_row));families={k:[]for k in('semantic','governance')};event_bytes={}
    for family in families:
        for i in range(1,89):
            name=f'{family}/{i:08d}-ontology-{family}:O05:{i}.json';b=archive['files'][name];raw=base64.b64decode(b['base64_original_bytes'],validate=True)
            need(sha(raw)==b['sha256'],'fixture historical event bytes differ');families[family].append(json.loads(raw));event_bytes[name]=sha(raw)
    with tempfile.TemporaryDirectory(prefix='cal-O05-inert-controls-')as tmp:
        root=Path(tmp);counter=[0]
        def stream(value):
            p=root/str(counter[0]);counter[0]+=1;raw=value if type(value)is bytes else contract.canonical(value);io.write(p,raw)
            return {'path':str(p),'sha256':sha(raw)}
        replay={'result':'PASS','checkpoint_parity':'PASS','authority_effect':'none','semantic_events':families['semantic'],'governance_events':families['governance']}
        drafts=copy.deepcopy(families)
        for events in drafts.values():
            for event in events:event['event_digest']='0'*64
        rows=[]
        for mode,request,out,before_files,after_files in [('read',None,replay,event_bytes,event_bytes),('seal',drafts,families,{},{}),('append',families,{'result':'PASS','authority_effect':'none'},{},event_bytes),('read',None,replay,event_bytes,event_bytes)]:
            rows.append({'mode':mode,'returncode':0,'request_binding':stream(request)if request is not None else None,'stdout_binding':stream(out),'stderr_binding':stream(b''),'files_before':copy.deepcopy(before_files),'files_after':copy.deepcopy(after_files)})
        value={'schema_version':'lab-O05-native-byte-compatibility/v1-candidate','authority_effect':'none','actual_owner_outcome':None,
            'execution_selection_binding':contract.EXECUTION,'historical_scope_binding':contract.HISTORICAL,'input_selection_binding':contract.INPUTS,
            'probe_module_binding':contract.bind(HERE/'compatibility_probe.py'),'captured_at':'2026-10-15T00:00:00+00:00','historical_archive_binding':archive_row,'event_bytes':event_bytes,'observations':rows}
        verify=lambda v:contract.evidence(v,runtime_bindings=[contract.bind(HERE/'compatibility_probe.py')])
        check('inert-synthetic-full176-evidence-parser-positive',lambda:verify(value))
        mutations=[('failed-child',lambda v:v['observations'][0].update(returncode=1)),('partial-native-byte-set',lambda v:v['event_bytes'].pop(next(iter(v['event_bytes'])))),('old-native-role-selection',lambda v:v['execution_selection_binding'].update(sha256=contract.OLD_NATIVE)),('wrong-historical-scope',lambda v:v['historical_scope_binding'].update(sha256='0'*64)),('dropped-observation',lambda v:v['observations'].pop()),('append-not-exact176',lambda v:v['observations'][2].update(files_after={})),('cold-replay-mutation',lambda v:v['observations'][3].update(files_after={})),('invented-authority',lambda v:v.update(authority_effect='admit')),('unclosed-evidence',lambda v:v.update(accepted=True)),('wrong-producer-origin',lambda v:v['probe_module_binding'].update(path='fake.py'))]
        for name,mutate in mutations:
            changed=copy.deepcopy(value);mutate(changed);check('inert-evidence-refuses-'+name,lambda changed=changed:refusal(lambda:verify(changed)))
        changed=copy.deepcopy(value);bad=copy.deepcopy(families);bad['semantic'][0]['event_digest']='0'*64;changed['observations'][1]['stdout_binding']=stream(bad)
        check('inert-seal-altered-semantic-event-refuses',lambda:refusal(lambda:verify(changed)))
        changed=copy.deepcopy(value);bad=copy.deepcopy(replay);bad['governance']=bad.pop('governance_events');changed['observations'][0]['stdout_binding']=stream(bad)
        check('inert-incompatible-replay-wire-schema-refuses',lambda:refusal(lambda:verify(changed)))
        # Fresh fixture directory only; deliberately detach an intermediate held
        # ancestor, observe refusal before effects, then restore for clean exit.
        a=root/'a';a.mkdir();(a/'b').mkdir()
        with io.held_directory(a/'b')as(fd,attached):
            a.rename(root/'moved');check('held-publisher-intermediate-detach-refuses',lambda:refusal(attached));(root/'moved').rename(a)
        (root/'alias').symlink_to(a,target_is_directory=True)
        def alias():
            try:
                with io.held_directory(root/'alias/b'):pass
            except OSError:return
            raise AssertionError('symlink accepted')
        check('held-publisher-symlink-refuses',alias)
    check('MIG01-original-recursive-package-exact-after-inert-controls',lambda:need(original_package=={
        p.relative_to(old_package).as_posix():sha(capture.capture_path(p,maximum=32*1024*1024))
        for p in old_package.rglob('*')if p.is_file()},'original package recursively changed'))
    for name,pin in saved.items():need(sha(capture.capture_path(Path(name),pin,maximum=32*1024*1024))==pin,'named entry/exit bytes differ')
    after=len(os.listdir('/proc/self/fd'));need(before==after,'inert descriptor leak')
    return {'result':'PASS','mode':'pure-static-and-inert-fixtures-only','checks':checks,'check_count':len(checks),'selected_public_rows':len(entries),'entry_exit_unique_files':len(saved),'fd_delta':after-before,
        'native_or_API_or_Source_guard_or_installation_executed':False,'synthetic_streams_are_empirical_evidence':False,'compatibility_or_runtime_qualified':False}

if __name__=='__main__':
    try:result=main()
    except Exception as error:
        result={'result':'FAIL','exception_class':type(error).__name__,'message':str(error),'completed_checks':checks,'native_executed':False}
    print(json.dumps(result,sort_keys=True));raise SystemExit(0 if result['result']=='PASS'else 1)
