"""Exact staged metadata-prefix AST, real helper/parser, own physical replacement."""
import ast,hashlib,importlib.util,json,os,sys,tempfile,types
from pathlib import Path
ROOT=Path(__file__).resolve().parents[7];RUN=Path(__file__).parent;HERE=ROOT/'product/lab/release-candidates/v1/interface/source-input-capture-v1-completion-0001'
spec=importlib.util.spec_from_file_location('_T03_capture_checks_support',HERE/'checks.py');support=importlib.util.module_from_spec(spec);spec.loader.exec_module(support)
selection=json.loads((RUN/'development-selection.json').read_bytes());pin=selection['capture']['sha256'];K=support.load_capture(HERE/'capture.py',pin,'_T03_metadata_capture_kernel')
source=ROOT/'product/lab/release-candidates/v1/interface/current-session-fixtures-v1-completion-0001/instances/diagnostic-0004/source';name='_T03_actual_source_parser';spec=importlib.util.spec_from_file_location(name,source/'__init__.py',submodule_search_locations=[str(source)]);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);B=__import__(name+'.base',fromlist=['parse'])
class ObservedParse(Exception):pass
cases=[]
for suffix,function,parse_variable in [('source/base.py','verify_source','m'),('reader/reader.py','guard','manifest'),('mapped/base.py','verify_source','m'),('context/base.py','preflight','m'),('context/generation.py','selected_mapping','m')]:
    file=RUN/'postimages'/suffix;tree=ast.parse(file.read_text());fn=next((n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==function),None)
    if fn is None:fn=next(n for cls in tree.body if isinstance(cls,ast.ClassDef) for n in cls.body if isinstance(n,ast.FunctionDef) and n.name==function)
    body=[]
    for node in fn.body:
        if suffix=='context/generation.py' and isinstance(node,ast.Expr) and ast.unparse(node).startswith('MAPPED.guard('):continue
        body.append(node)
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id==parse_variable for t in node.targets):break
    root=Path(tempfile.mkdtemp(prefix='cal-T03-owned-metadata-'));os.chmod(root,0o700);folder=root/'input';folder.mkdir(mode=0o700);(folder/'packages').mkdir(mode=0o700);(folder/'packages/0001').mkdir(mode=0o700)
    path=folder/'packages/0001/manifest.json' if function=='selected_mapping' else folder/'source-manifest.json'
    original=json.dumps({'files':[{'path':'selected-original-row','sha256':'a'*64}],'owned_metadata_only':True},sort_keys=True).encode();support.put(path,original);expected=hashlib.sha256(original).hexdigest();namespace={'ROOT':root,'HERE':folder,'ADAPTER_ROOT':folder,'original':lambda row:K.capture_one(root,row,code_sha256=pin),'parse':B.parse,'load_bytes':B.parse,'source':types.SimpleNamespace(parse=B.parse),'MAPPED':types.SimpleNamespace(HERE=folder),'MAPPED_SOURCE_SHA':'0'*64}
    prefix=ast.FunctionDef(name='selected_metadata_prefix',args=fn.args,body=body,decorator_list=[]);module=ast.fix_missing_locations(ast.Module(body=[prefix],type_ignores=[]));exec(compile(module,str(file),'exec'),namespace)
    observed=[];mid=4
    def start(code,offset):
        if code is B.parse.__code__:
            path.rename(path.with_name('owned-original-retained.json'));support.put(path,b'{"files":[{"path":"unselected-row","sha256":"0000000000000000000000000000000000000000000000000000000000000000"}]}')
    def returned(code,offset,value):
        if code is B.parse.__code__:observed.append(value);raise ObservedParse()
    sys.monitoring.use_tool_id(mid,'T03 physical metadata replacement at actual parser entry');sys.monitoring.register_callback(mid,sys.monitoring.events.PY_START,start);sys.monitoring.register_callback(mid,sys.monitoring.events.PY_RETURN,returned);sys.monitoring.set_local_events(mid,B.parse.__code__,sys.monitoring.events.PY_START|sys.monitoring.events.PY_RETURN)
    try:
        try:namespace['selected_metadata_prefix'](types.SimpleNamespace(adapter_pin=expected)) if function=='guard' else namespace['selected_metadata_prefix'](expected)
        except ObservedParse:pass
        else:raise AssertionError('expected parse observation missing')
    finally:
        sys.monitoring.set_local_events(mid,B.parse.__code__,0);sys.monitoring.register_callback(mid,sys.monitoring.events.PY_START,None);sys.monitoring.register_callback(mid,sys.monitoring.events.PY_RETURN,None);sys.monitoring.free_tool_id(mid)
    assert observed==[json.loads(original)] and json.loads(path.read_bytes())!=observed[0] and not getattr(K._ACTIVE,'value',False)
    cases.append({'case':suffix+' exact metadata prefix parses pinned captured original despite physical replacement at parser entry','result':'PASS','staged_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'owned_root':str(root),'whole_original_domain_guard_executed':False})
value={'schema_version':'lab-T03-bound-metadata-prefix-proof/v1-candidate','result':'PASS','cases':cases,'kernel_sha256':pin,'scope':'Exact new staged metadata-selection prefix AST ending at real unchanged Source parser; skipped mapping preguard and stopped before all subsequent domain checks. Real original callbacks not replaced. Only owned inert metadata mutated. No actual Source producer or Session constructed.','authority_effect':'none','task_complete':False};out=RUN/'metadata-capture-evidence.json';support.put(out,json.dumps(value,indent=2,sort_keys=True).encode()+b'\n');print(json.dumps({'result':'PASS','cases':len(cases),'report':str(out)}),flush=True)
