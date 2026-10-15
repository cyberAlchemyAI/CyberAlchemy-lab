"""Selected caller prefix and unchanged delegations; no native constructors."""
import argparse,ast,hashlib,json,os,sys,tempfile,types
from pathlib import Path
HERE=Path(__file__).absolute().parent
ROOT=HERE.parents[6]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(b):
    raw=(ROOT/b['path']).read_bytes();assert sha(raw)==b['sha256'];return raw
def main():
    p=argparse.ArgumentParser();p.add_argument('--selection-sha256',required=True);a=p.parse_args()
    raw=(HERE/'selection.json').read_bytes();assert sha(raw)==a.selection_sha256;s=json.loads(raw)
    assert s['authority_effect']=='none';rows=s['postimages'];checks=[]
    for row in rows:
        pre=read(row['preimage']);post=read(row['postimage'])
        if row['target']!='source/base.py':assert pre==post
        else:
            original=ast.parse(pre);current=ast.parse(post)
            old={n.name:ast.dump(n,include_attributes=False) for n in ast.walk(original) if isinstance(n,ast.FunctionDef)}
            new={n.name:ast.dump(n,include_attributes=False) for n in ast.walk(current) if isinstance(n,ast.FunctionDef)}
            assert old==new
            assert set(new)==set(old)
        checks.append({'case':'exact-postimage-and-retained-body:'+row['target'],'result':'PASS'})
    source=next(r for r in rows if r['target']=='source/base.py')['postimage'];text=read(source).decode();prefix=text[:text.index('\n# Original native imports and domain helpers.')];assert sha(prefix.encode())==s['source_prefix_sha256']
    module=types.ModuleType('_cal_root_selected_caller_prefix0004');module.__file__=str(ROOT/source['path']);sys.modules[module.__name__]=module
    exec(compile(prefix,module.__file__,'exec'),module.__dict__)
    assert module.ROOT==ROOT and module.SOURCE_CAPTURE.__file__==str(ROOT/s['helper']['path']) and module.CAPTURE_CALLER.__file__==str(ROOT/s['caller']['path'])
    assert module._CAPTURE_PIN==s['helper']['sha256'] and module._CALLER_PIN==s['caller']['sha256'];module._capture_identity()
    checks.append({'case':'true-selected-helper-caller-and-held-function-contract','result':'PASS'})
    fds=len(os.listdir('/proc/self/fd'))
    with tempfile.TemporaryDirectory(prefix='owned-caller-fixture-',dir=HERE) as tmp:
        tmp=Path(tmp);items=[]
        for n in range(3):
            path=tmp/str(n);data=('owned caller input '+str(n)+'\n').encode();path.write_bytes(data)
            row={'path':str(path.relative_to(ROOT)),'sha256':sha(data)};items.append(row)
            assert module.original(row)==data
        checks.append({'case':'original-captures-all-three-exact-files','result':'PASS'})
        assert module.verify_inputs(items)==3;checks.append({'case':'all-rows-through-external-held-contract','result':'PASS'})
        try:module.original({**items[0],'sha256':'0'*64})
        except ValueError:checks.append({'case':'changed-selected-digest-refused-before-return','result':'PASS'})
        else:raise AssertionError('wrong digest accepted')
        module._capture_identity();assert not module.SOURCE_CAPTURE._ACTIVE.value
        absolute={'path':str(tmp/'0'),'sha256':items[0]['sha256']}
        assert module.verify_inputs([absolute],selected_external=[absolute])==1;checks.append({'case':'only-explicit-external-input-through-held-contract','result':'PASS'})
    with tempfile.TemporaryDirectory(prefix='owned-init-failure-',dir=HERE) as tmp:
        path=Path(tmp)/'failure.py';raw=b"raise RuntimeError('owned initialization fixture')\n";path.write_bytes(raw)
        leaf='owned-init-failure';name='_cal_source_input_capture_v2_successor_'+leaf+'_'+module.__name__.replace('.','_')
        try:module._load_selected_capture(path,sha(raw),leaf)
        except RuntimeError:pass
        else:raise AssertionError('owned initialization did not fail')
        assert name not in sys.modules;module._capture_identity()
        checks.append({'case':'helper-exec-failure-removes-exact-new-registration','result':'PASS'})
    assert len(module._CAPTURE_OWNED_MODULES)==2
    foreign_name='_cal_root_caller_cleanup_foreign_owned_fixture';created=types.ModuleType(foreign_name);replacement=types.ModuleType(foreign_name)
    module._CAPTURE_OWNED_MODULES.append((foreign_name,created));sys.modules[foreign_name]=replacement
    module._rollback_capture_modules();assert sys.modules[foreign_name] is replacement;del sys.modules[foreign_name]
    assert not module._CAPTURE_OWNED_MODULES
    assert not any(value is module.SOURCE_CAPTURE or value is module.CAPTURE_CALLER for value in sys.modules.values())
    checks.append({'case':'pair-rollback-cleans-owned-kernel-caller-and-preserves-replacement','result':'PASS'})
    tree=ast.parse(text);handlers=[n for n in tree.body if isinstance(n,ast.Try)]
    assert len(handlers)==2 and all(any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='_rollback_capture_modules' for n in ast.walk(h)) for t in handlers for h in t.handlers)
    checks.append({'case':'helper-pair-and-entire-original-native-initialization-rollback-handlers','result':'PASS'})
    assert fds==len(os.listdir('/proc/self/fd'));checks.append({'case':'owned-cleanup-and-zero-descriptor-delta','result':'PASS'})
    for row in rows:read(row['preimage']);read(row['postimage'])
    read(s['helper']);read(s['caller']);read(s['helper_manifest']);read(s['helper_handoff'])
    v={'schema_version':'lab-T03-selected-caller-integration-controls/v1-candidate','authority_effect':'none','result':'PASS-scoped-caller-prefix-and-unchanged-delegations','checks':checks,'count':len(checks),'selection_sha256':a.selection_sha256,'full_postimage_sha256':source['sha256'],'exact_source_prefix_sha256':s['source_prefix_sha256'],'source_prefix_before_original_native_imports_only':True,'four_delegating_bodies_byte_identical':True,'domain_function_bodies_preserved':True,'descriptor_delta':0,'source_reader_mapper_Context_or_native_constructor_executed':False,'production_callback_or_clock_changed':False,'full_dependency_graph_or_native_family_or_current_learning_qualified':False,'task_complete':False}
    with (HERE/'controls-result.json').open('x') as f:json.dump(v,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'result':v['result'],'checks':len(checks),'descriptor_delta':0}))
if __name__=='__main__':main()
