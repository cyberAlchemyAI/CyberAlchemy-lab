"""Load captured true-origin role modules through private imports, no bare aliases."""
import cal_installed_runtime_selection_v1 as _INSTALL_SELECTION
_INSTALL_SELECTION.guard()
import builtins,hashlib,json,types,uuid
from pathlib import Path
ROOT=_INSTALL_SELECTION.root()
SUPPORT={'checked_io':{'path':'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/checked_io.py','sha256':'cf9871b52b91842efed22f10484a2d9084ca7aeee59f91d2e9b6277f2f35fd12'},'stage_io':{'path':'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/stage_io.py','sha256':'d16ec83b02a052b975dfba3d96cf848d32f0f9f2d706fe83fab375cdfda112ec'},'closure':{'path':'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/closure.py','sha256':'cae6610064a8f105e6e7ee9bbd5a5a0e07af239b6b43221d7e8b011f0e261a0a'}}
def need(v,s):
    if not v:raise ValueError(s)
def load(raw,pin,original,caller_guard):
    need(hashlib.sha256(raw).hexdigest()==pin,'independently selected Context role JSON differs')
    value=json.loads(raw);ports={};namespace='_cal_fresh_legacy_role_'+uuid.uuid4().hex
    def imported(name,globals=None,locals=None,fromlist=(),level=0):
        if level==0 and name in ports:return ports[name]
        return builtins.__import__(name,globals,locals,fromlist,level)
    def captured(key,row):
        caller_guard();body=original(row);caller_guard()
        m=types.ModuleType(namespace+'_'+key);m.__file__=str(ROOT/row['path']);m.__builtins__={**vars(builtins),'__import__':imported}
        exec(compile(body,m.__file__,'exec',dont_inherit=True),m.__dict__);ports[key]=m;return m
    for key in ('checked_io','stage_io','closure'):captured(key,SUPPORT[key])
    deps=captured('dependencies',value['module_bindings']['dependencies'])
    control=captured('control',value['module_bindings']['control'])
    role=captured('context_native_role',value['role_code_binding'])
    executor=role.SelectedContextExecutor(raw,pin,deps,control)
    caller_guard();return executor
