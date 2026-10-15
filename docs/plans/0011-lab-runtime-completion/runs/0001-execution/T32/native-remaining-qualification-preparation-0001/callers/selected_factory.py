"""Exact accepted StoreFactory origin, never an alias of the old class."""
import inspect,sys,types
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
ORIGIN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T32/native-store-guard-composition-preparation-0001/selected_store.py'
PIN='83bd3d974c2e7d8e4f7b060b9b1678f8bb796a3ffac2bc5d10f1dd58af6f3a8f'
# The same immutable capture bytes are selected locally, not imported under a
# historical module filename. No work or factory constructor runs at import.
from ..migration827.capture import capture_path

def verify_factory(factory):
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
    factory.guard()
    return factory
