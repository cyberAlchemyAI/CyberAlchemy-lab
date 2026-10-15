"""UNRUN selected native controls. Genuine fixture store and runtime only."""
import copy
from dataclasses import replace

def exercise(runtime,store):
    runtime.require_store(store);checks=[]
    actual=store.read()
    assert runtime.original.digest(actual)==store.pins.projection_digest
    checks.append('actual original native history request projection and cursors through selected loader')
    def refuses(label,fn):
        try:fn()
        except Exception:checks.append(label);return
        raise AssertionError(label)
    def selected(request,pins):
        return runtime.launch_module.SelectedNativeReadStore(runtime.original,runtime.bindings['native_module'],runtime.launch.root,
            runtime.launch,store.semantic_directory,store.governance_directory,request,store.executable,pins)
    refuses('wrong original executable SHA refuses',lambda:selected(store.request,replace(store.pins,executable_sha256='0'*64)).read())
    request=copy.deepcopy(store.request);request['selector']['semantic_cursor']+=1
    refuses('Project or changed cursor cannot substitute native request',lambda:selected(request,store.pins).read())
    request=copy.deepcopy(store.request);request['governance_cursor']=max(0,request['governance_cursor']-1)
    pins=replace(store.pins,request_sha256=runtime.original.byte_digest(runtime.original.encoded(request)),governance_cursor=request['governance_cursor'])
    refuses('new request pin cannot conceal incompatible governance prefix',lambda:selected(request,pins).read())
    changed=copy.deepcopy(runtime.launch.value);changed['mode']='ambient-host-fallback'
    raw=runtime.original.encoded(changed)
    refuses('unsupported loader mode refuses before execution',lambda:runtime.launch_module.SelectedNativeLaunch(raw,runtime.original.byte_digest(raw),
        runtime.launch.root,runtime.dependencies,runtime.bindings['dependency_module']))
    refuses('old original NativeReadStore is not accepted as selected store',lambda:runtime.require_store(runtime.original.NativeReadStore(
        store.semantic_directory,store.governance_directory,store.request,store.executable,store.pins)))
    runtime.guard()
    return {'result':'PASS-focused-actual-native-selected-route-only','checks':checks,'original_native_projection_digest':store.pins.projection_digest,
            'no_mock_native_output':True,'whole36_C08_or_runtime_qualified':False,'authority_effect':'none'}
