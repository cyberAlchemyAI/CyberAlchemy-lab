"""Actual pure import/global-resolution proof. No original constructor callbacks."""
import ast,builtins,dis,hashlib,importlib.util,inspect,json,os,stat,sys,types
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution';HERE=Path(__file__).absolute().parent
INSTALL=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
DEPENDENCY_SHA='2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'
def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def need(value, reason):
    if not value:
        raise ValueError(reason)

def dependency_guard():
    selection_path = RUN / 'T07/revision-0002/dependency-selection-0002.json'
    raw = selection_path.read_bytes(); need(sha(raw) == DEPENDENCY_SHA, 'independent full dependency selection differs')
    selected = json.loads(raw)
    rows = {r['destination']: {'sha256': r['sha256'], 'size_bytes': r['size_bytes'],
                             'mode': 0o755 if r['kind'] in {'interpreter', 'native-executable'} else 0o644}
            for r in selected['inputs']}
    rows.update(selected['wheel_members']); rows['lib/abi/ld-linux-x86-64.so.2']['mode'] = 0o755
    need(len(rows) == 1010, 'full installed closure required')
    for name, row in rows.items():
        path = INSTALL / name
        need(not any(p.is_symlink() for p in (path, *path.parents)), 'unsafe selected dependency')
        before = path.lstat()
        need(stat.S_ISREG(before.st_mode) and before.st_uid == os.getuid()
             and stat.S_IMODE(before.st_mode) == row['mode'] and before.st_size == row['size_bytes'], 'selected dependency identity differs')
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        try:
            actual = os.fstat(fd); need((actual.st_dev, actual.st_ino, actual.st_mtime_ns, actual.st_ctime_ns)
                                        == (before.st_dev, before.st_ino, before.st_mtime_ns, before.st_ctime_ns), 'dependency attachment differs')
            digest = hashlib.sha256()
            while chunk := os.read(fd, 1024 * 1024):
                digest.update(chunk)
            after = os.fstat(fd); current = path.lstat()
            fields = lambda x: (x.st_dev, x.st_ino, x.st_mode, x.st_uid, x.st_size, x.st_mtime_ns, x.st_ctime_ns)
            need(fields(before) == fields(after) == fields(current) and digest.hexdigest() == row['sha256'], 'dependency bytes changed')
        finally:
            os.close(fd)
    return {'status': 'PASS', 'installed_files': 1010, 'selection_sha256': DEPENDENCY_SHA}
def binding(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes())}
entry=dependency_guard()
context=RUN/'T02/optimized-context-revision-0002/context'
name='_cal_T02_context_parser_composition_revision_0002'
assert name not in sys.modules
spec=importlib.util.spec_from_file_location(name,context/'__init__.py',submodule_search_locations=[str(context)])
module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
generation=__import__(name+'.generation',fromlist=['*']);base=__import__(name+'.base',fromlist=['*']);control=__import__(name+'.control',fromlist=['*'])
assert Path(generation.__file__).absolute()==context/'generation.py'
assert callable(generation.reader.adapter.source.parse) and generation.reader.adapter.source.parse is base.load_bytes
assert not hasattr(control,'load_bytes')
assert generation.selected_mapping.__globals__['reader'] is base.reader
findings=[];checked=[]
def inspect_code(code,namespace,label):
    reads=sorted({i.argval for i in dis.get_instructions(code) if i.opname=='LOAD_GLOBAL'})
    missing=[k for k in reads if k not in namespace and not hasattr(builtins,k)]
    checked.append({'function':label,'globals_read':reads,'unresolved':missing})
    findings.extend((label,k) for k in missing)
    for child in code.co_consts:
        if isinstance(child,types.CodeType):inspect_code(child,namespace,label+'::'+child.co_name)
resolved_modules=[base,control,generation,sys.modules[base.MAPPED.__package__+'.base'],sys.modules[type(base.reader).__module__],base.reader.adapter.source,base.reader.adapter.source.B]
for m in resolved_modules:
 for key,value in vars(m).items():
    if inspect.isfunction(value) and value.__module__==m.__name__:inspect_code(value.__code__,value.__globals__,m.__name__+'.'+key)
    if inspect.isclass(value) and value.__module__==m.__name__:
     for k,method in vars(value).items():
      if isinstance(method,(staticmethod,classmethod)):method=method.__func__
      if inspect.isfunction(method):inspect_code(method.__code__,method.__globals__,m.__name__+'.'+value.__name__+'.'+k)
assert not findings,findings
oldgen=RUN/'T03/pure-source-capture-0001/postimages/context/generation.py';fix=RUN/'T03/context-parser-correction-0002/generation.py'
before="m=load_bytes(original({'path':p.relative_to(ROOT).as_posix(),'sha256':package_pin}))";after="m=reader.adapter.source.parse(original({'path':p.relative_to(ROOT).as_posix(),'sha256':package_pin}))"
assert fix.read_text().replace(after,before)==oldgen.read_text()
original=RUN/'T02/optimized-family-preparation-0001/preimages/construct_v4.py';current=HERE/'construct_optimized_v2.py'
def function_ast(p,k):return ast.dump(next(n for n in ast.parse(p.read_text()).body if isinstance(n,ast.FunctionDef) and n.name==k),include_attributes=False)
assert all(function_ast(original,k)==function_ast(current,k) for k in ['cold','reader'])
result={'schema_version':'lab-T02-corrected-parser-import-composition/v1-candidate','result':'PASS-pure-import-and-global-resolution','authority_effect':'none','actual_owner_outcome':None,'dependencies_entry':entry,'dependencies_exit':dependency_guard(),'actual_selected_runtime_Python':sys.version.split()[0],'true_imported_context_code':[binding(context/n) for n in ['base.py','control.py','generation.py']],'corrected_T03_postimage_binding':binding(fix),'exact_one_expression_parser_delta':True,'actual_export_chain_resolves_parser':True,'all_lexical_global_reads_in_actual_context_base_control_generation_mapper_base_reader_reader_reader_base_source_base_resolved':True,'actual_guard_only_CurrentFixtureReader_metadata_constructor_on_mapper_import':True,'actual_qualified_source_module_names':[m.__name__ for m in resolved_modules],'checked_functions_and_nested_code':checked,'original_cold_and_reader_AST_unchanged':True,'source_constructor_native_replay_Context_constructor_or_transport_permission_executed':False,'runtime_lock_acquired':False,'Context_only_preparation_disposition':'Insufficient for full-goal applicability; this import proof is prerequisite only.'}
p=HERE/'reports/composition-check-0002.json'
with p.open('x') as stream:json.dump(result,stream,sort_keys=True,indent=2);stream.write('\n')
print(json.dumps({'result':result['result'],'checked_function_code_objects':len(checked),'report_binding':binding(p)},sort_keys=True))
