"""Exact accepted StoreFactory origin, never an alias of the old class."""
import inspect,sys,types
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
ORIGIN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T32/native-original55-execution-preparation-0002/factory/selected_store.py'
PIN='4d8f345cd7d4eb27e7dd291bc039197fc90471f1ab762bfa8fba319ffa7487bd'
# The same immutable capture bytes are selected locally, not imported under a
# historical module filename. No work or factory constructor runs at import.
from .loader import capture_path

def _verify_original_factory(factory):
    cls=type(factory)
    if cls.__name__!='StoreFactory' or Path(inspect.getsourcefile(cls))!=ORIGIN:
        raise ValueError('actual accepted native StoreFactory origin required')
    module=sys.modules.get(cls.__module__)
    if module is None or getattr(module,'StoreFactory',None)is not cls or Path(module.__file__)!=ORIGIN:
        raise ValueError('actual independently loaded StoreFactory class identity required')
    raw=capture_path(ORIGIN,PIN)
    # Class/file labels alone do not recognize an arbitrary in-memory class.
    # Compare every actual selected method code object with the exact source
    # compiled at its original filename; ignore only source line tables.
    compiled=compile(raw,str(ORIGIN),'exec')
    expected=next(c for c in compiled.co_consts if isinstance(c,types.CodeType)and c.co_name=='StoreFactory')
    code=lambda c:(c.co_argcount,c.co_posonlyargcount,c.co_kwonlyargcount,c.co_nlocals,c.co_stacksize,c.co_flags,c.co_code,c.co_names,c.co_varnames,c.co_freevars,c.co_cellvars,tuple(code(v)if isinstance(v,types.CodeType)else v for v in c.co_consts))
    methods={c.co_name:c for c in expected.co_consts if isinstance(c,types.CodeType)}
    if set(methods)!={k for k,v in cls.__dict__.items()if isinstance(v,types.FunctionType)} or any(code(cls.__dict__[k].__code__)!=code(v)for k,v in methods.items()):
        raise ValueError('selected factory implementation differs from captured original code')
    for name,function in cls.__dict__.items():
        if isinstance(function,types.FunctionType):
            bound=getattr(factory,name)
            if getattr(bound,'__func__',None)is not function or getattr(bound,'__self__',None)is not factory or function.__globals__ is not module.__dict__:
                raise ValueError('selected factory callback identity differs from actual captured class')
    for expected_function in compiled.co_consts:
        if isinstance(expected_function,types.CodeType)and expected_function.co_name!='StoreFactory':
            function=module.__dict__.get(expected_function.co_name)
            if not isinstance(function,types.FunctionType)or function.__globals__ is not module.__dict__ or code(function.__code__)!=code(expected_function):
                raise ValueError('selected factory producer function differs from captured original code')
    factory.guard()
    return factory


import contextvars
from contextlib import contextmanager
_factory_context=contextvars.ContextVar('original55_private_factory_context',default=None)
@contextmanager
def selected_test_factory(factory):
    verify_factory(factory)
    if _factory_context.get()is not None:raise ValueError('one explicit factory context required')
    token=_factory_context.set(factory)
    try:yield factory
    finally:
        # Reset even when independent factory/Source/custody proof refuses.
        try:verify_factory(factory)
        finally:_factory_context.reset(token)
def create_selected_store(translator,executable,executable_sha256):
    factory=verify_factory(_factory_context.get())
    return factory.create(translator,executable,executable_sha256)
def require_selected_instance(value):
    factory=verify_factory(_factory_context.get())
    return factory.owns_exact(value)


# The original complete factory method/global-code guard above is retained.
# A maintained call additionally requires this exact explicitly entered runtime
# context; possessing a similarly named class never selects a capability.
import contextlib
from . import loader
_runtime_context=contextvars.ContextVar('maintained_native57_selected_runtime',default=None)
GENERATION=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T32/native-original55-execution-preparation-0002/factory/generation_store.py'
GENERATION_SHA='18166ca54455cdaa0005113c07c8e0eabb5369d8431daa204595d5aa0c1e8982'
def _shape(c):
    return(c.co_argcount,c.co_posonlyargcount,c.co_kwonlyargcount,c.co_nlocals,c.co_stacksize,c.co_flags,c.co_code,c.co_names,c.co_varnames,c.co_freevars,c.co_cellvars,tuple(_shape(v)if isinstance(v,types.CodeType)else v for v in c.co_consts))
def _function(function,expected,module,*,contextmanager=False):
    if contextmanager:
        sample=contextlib.contextmanager(lambda:None);wrapped=getattr(function,'__wrapped__',None)
        if type(function)is not types.FunctionType or _shape(function.__code__)!=_shape(sample.__code__)or function.__globals__ is not vars(contextlib)or function.__closure__ is None or len(function.__closure__)!=1 or function.__closure__[0].cell_contents is not wrapped:raise ValueError('exact original contextmanager wrapper required')
        function=wrapped
    if type(function)is not types.FunctionType or function.__globals__ is not vars(module)or _shape(function.__code__)!=_shape(expected):raise ValueError('selected runtime method/global implementation differs from captured original')
def _class(cls,name,row,*,contextmanager_methods=()):
    path=loader.path(row);module=sys.modules.get(cls.__module__)
    if module is None or Path(module.__file__)!=path or getattr(module,name,None)is not cls or Path(inspect.getsourcefile(cls))!=path:raise ValueError('true original runtime class/module required')
    compiled=compile(capture_path(path,row['sha256']),str(path),'exec');body=next(c for c in compiled.co_consts if isinstance(c,types.CodeType)and c.co_name==name);expected={c.co_name:c for c in body.co_consts if isinstance(c,types.CodeType)}
    for key,code in expected.items():
        member=cls.__dict__.get(key);function=member.fget if isinstance(member,property)else member
        _function(function,code,module,contextmanager=key in contextmanager_methods)
    for code in compiled.co_consts:
        if isinstance(code,types.CodeType)and code.co_name!=name and not any(isinstance(v,types.CodeType)and v.co_name=='__init__'for v in code.co_consts):
            function=module.__dict__.get(code.co_name)
            if isinstance(function,types.FunctionType):_function(function,code,module)
def _strict_runtime_factory(factory,runtime):
    _class(type(runtime),'RuntimeSelection',runtime.value['own_modules']['loader.py'],contextmanager_methods=('selected_environment',))
    runtime.auxiliary_guard(kind=None);_verify_original_factory(factory);value=runtime.value
    if factory.selection['generation_module_binding']!={'path':str(GENERATION.relative_to(ROOT)),'sha256':GENERATION_SHA}or Path(factory.generation.__file__)!=GENERATION:raise ValueError('exact qualified18166 generation module required')
    _class(factory.generation.GenerationStore,'GenerationStore',factory.selection['generation_module_binding'],contextmanager_methods=('lock',));_class(factory.original.NativeCandidateStore,'NativeCandidateStore',factory.selection['original_store_binding']);_class(type(factory.executor),'SelectedOntologyExecutor',factory.selection['executor_class_binding']['code_binding']);_class(type(factory.boundary),'OwnedTechnicalBoundary',factory.selection['boundary_class_binding']['code_binding'])
    _class(factory.generation.NativeRejection,'NativeRejection',factory.selection['generation_module_binding'])
    if factory.generation.NativeRejection.__bases__!=(ValueError,):raise ValueError('exact original typed native rejection required')
    for instance in[runtime,factory.executor,factory.boundary,*[record[0].committed for record in factory._created.values()]]:
        if any(name in instance.__dict__ for base in type(instance).__mro__ for name,member in base.__dict__.items()if isinstance(member,(types.FunctionType,property))):raise ValueError('selected executor/boundary/generation callbacks may not be shadowed')
    if factory.selection['original_store_binding']!=value['original_modules']['native_store']or factory.executor.pin!=value['production_selection']['sha256']or factory.boundary.packet['ontology_execution_selection_binding']!=value['production_selection']or factory.boundary.packet['api_source_binding']!=value['source']or factory.boundary.packet['api_profile_binding']!=value['profile']:raise ValueError('current maintained Source/runtime/factory provenance differs')
    return factory
def verify_factory(factory):
    runtime=_runtime_context.get()
    if type(runtime)is not loader.RuntimeSelection or _factory_context.get()is not factory:raise ValueError('explicit current maintained factory context required')
    runtime.code_guard();return _strict_runtime_factory(factory,runtime)
@contextmanager
def runtime_factory(factory,runtime):
    if type(runtime)is not loader.RuntimeSelection or _factory_context.get()is not None or _runtime_context.get()is not None:raise ValueError('one exact maintained runtime/factory context required')
    _strict_runtime_factory(factory,runtime);runtime.full_guard();before=runtime.fd_snapshot();known=set(factory._created);ft=_factory_context.set(factory);rt=_runtime_context.set(runtime);primary=None;errors=[]
    try:yield factory
    except BaseException:primary=sys.exc_info()
    finally:
        try:records=list(factory._created.items())
        except BaseException as error:records=[];errors.append({'phase':'enumerate-new-owned-stores','exception_class':type(error).__name__})
        for identity,record in records:
            if identity not in known:
                try:
                    value=record[0]
                    if not value.closed:type(value).close(value)
                    if not value.closed or not value.root.is_dir():raise ValueError('selected store must close with retained original generations')
                except BaseException as error:errors.append({'phase':'close-new-owned-store','exception_class':type(error).__name__})
        for phase,fn in[('strict-factory',lambda:_strict_runtime_factory(factory,runtime)),('full-Source-installed-and329',runtime.full_guard),('operational-FD',lambda:loader.need(runtime.fd_snapshot()==before,'maintained context FD map differs'))]:
            try:fn()
            except BaseException as error:errors.append({'phase':phase,'exception_class':type(error).__name__})
        try:_runtime_context.reset(rt)
        finally:_factory_context.reset(ft)
    if primary is not None:
        primary[1].maintained_exit_errors=errors
        if errors:BaseException.add_note(primary[1],'independent maintained native exits='+loader.encoded(errors).decode())
        raise primary[1].with_traceback(primary[2])
    if errors:raise ValueError('independent maintained native exits refused '+loader.encoded(errors).decode())
