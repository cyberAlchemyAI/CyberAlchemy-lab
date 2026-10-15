"""Static v4 authoring checks only; no stager or Lab constructor calls."""
import ast,hashlib,json,sys,types
from pathlib import Path
HERE=Path(__file__).absolute().parent
ROOT=HERE.parents[6]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def main():
    raw=(HERE/'recipe-selection.json').read_bytes();assert sha(raw)==sys.argv[1];recipe=json.loads(raw);checks=[]
    for row in recipe['files']:assert sha((ROOT/row['path']).read_bytes())==row['sha256']
    assert not (HERE/'instances').exists();checks.append({'case':'all-current-recipe-inputs-fresh-no-instance-created','rows':len(recipe['files']),'result':'PASS'})
    p=HERE/'recipe_inputs_v4.py';inputs=types.ModuleType('_cal_T02_v4_pure_inputs');inputs.__file__=str(p)
    exec(compile(p.read_bytes(),str(p),'exec',dont_inherit=True),inputs.__dict__);baseline=inputs.verify_baseline()
    assert baseline['parent_recipe_row_count']==159
    parent_recipe=json.loads(inputs.exact(baseline['parent_recipe_binding']));assert len(parent_recipe['files'])==159
    retained={r['original']['path']:r for r in baseline['rows']}
    for row in parent_recipe['files']:
        assert retained[row['path']]['original']==row and inputs.exact(retained[row['path']]['preimage'])==inputs.exact(row)
    checks.append({'case':'all159-parent-recipe-rows-preserved-exactly-and162-unique-baseline-origins-fresh','result':'PASS'})
    parent=ROOT/baseline['parent_independent_review_binding']['path'];review=json.loads(inputs.exact(baseline['parent_independent_review_binding']))
    assert review['result']=='PASS-scoped-prepared-candidate';parent=parent.parent
    opt=json.loads((HERE/'optimization-selection.json').read_bytes())
    from jsonschema import Draft202012Validator
    validator=Draft202012Validator(json.loads((HERE/'optimization-selection.schema.json').read_bytes()));validator.validate(opt)
    assert not validator.is_valid({**opt,'ambient_pin':False})
    assert not validator.is_valid({**opt,'helper_code_binding':{'path':opt['helper_code_binding']['path'],'sha256':'0'*64}})
    caller_review=json.loads(inputs.exact(opt['caller_review_binding']));assert caller_review['result']=='PASS-scoped-helper-only-candidate'
    helper_review=json.loads(inputs.exact(opt['helper_review_binding']));assert opt['helper_code_binding']['sha256']=='eba3611c44fb76d89c7e741aac36ebcf52d3dc59786006af044d0ad98dc34962'
    assert opt['companion_code_binding']['sha256']=='4222b3ac165fa5ee8a9bed801290ffe42f63e69002ced521d4ac7e9e84bb7135'
    checks.append({'case':'closed-newcaller4-selection-and-explicit-arrived-peer8a9-newhelper7fc9-unchanged4222','result':'PASS'})
    closure={}
    for key,row in opt.items():
        if key.endswith('_binding'):inputs.exact(row);closure[row['path']]=row
    for key in ('helper_manifest_binding','caller_integration_manifest_binding','companion_manifest_binding'):
        mf=json.loads(inputs.exact(opt[key]))
        for row in mf['files']:
            raw=inputs.exact({'path':row['path'],'sha256':row['sha256']});assert 'size_bytes'not in row or len(raw)==row['size_bytes']
            expected={'path':row['path'],'sha256':row['sha256']};assert closure.get(row['path'],expected)==expected;closure[row['path']]=expected
    checks.append({'case':'all-three-helper-caller-companion-manifest-rows-in-complete-future-role-inputs','unique_rows':len(closure),'result':'PASS'})
    # Compare complete scripts to parent text after only explicit v4 namespace,
    # filename, exclusive instance/prefix and independently pinned input rebases.
    oldopt=sha((parent/'optimization-selection.json').read_bytes());newopt=sha((HERE/'optimization-selection.json').read_bytes())
    oldcommon=sha((parent/'recipe_inputs_v3.py').read_bytes());newcommon=sha((HERE/'recipe_inputs_v4.py').read_bytes())
    for name in ('build_family_optimized','construct_optimized','stage_optimized_family','stage_runtime_optimized'):
        expected=(parent/(name+'_v3.py')).read_text().replace('v3','v4').replace('optimized-0003','optimized-0004').replace('completion-optimized-source8-0003-','completion-optimized-source8-0004-').replace(oldcommon,newcommon)
        if name=='stage_optimized_family':expected=expected.replace('caller-integration-0003/postimages','caller-integration-0004/postimages').replace('T03/path-preparation-0001/capture.py','T03/integrity-comparison-preparation-0001/capture.py').replace(oldopt,newopt)
        current=(HERE/(name+'_v4.py')).read_text();assert expected==current;compile(current,str(HERE/(name+'_v4.py')),'exec',dont_inherit=True)
    checks.append({'case':'every-core-script-exact-parent-text-after-only-declared-namespace-filename-instance-prefix-input-rebases-no-domain-guard-change','result':'PASS'})
    current=json.loads(inputs.exact(baseline['current_API_source_binding']));assert baseline['current_API_source_binding']['sha256']=='e41772f7478253fa2ede056afaa08461a962cc2e1063e541f5f2921f7ebe1195'
    rows={r['path']:r['sha256'] for r in current['files']}
    for row in baseline['current_runtime_API_bindings']:assert rows[row['path']]==row['sha256'];inputs.exact(row)
    old=json.loads(inputs.exact(baseline['fixed_runtime_descriptor_binding']));assert baseline['fixed_runtime_descriptor_binding']['sha256']=='6004ecf7533954ee180f87186f46339b4e66a9c816252c40edf6ed2f98ea13bd'
    checks.append({'case':'current-runtime-five-preimage-pins-proven-by-exact-e417-declaration-and-original6004descriptor-not-ambient-derived','result':'PASS'})
    selected=json.loads(inputs.exact(opt['caller_selection_binding']));assert len(opt['postimages'])==5
    for row in opt['postimages']:
        peer=next(v for v in selected['postimages'] if v['target']==row['relative_target']);assert row['postimage_binding']==peer['postimage'];inputs.exact(row['original_binding']);inputs.exact(row['postimage_binding'])
    checks.append({'case':'exact-five-caller4-postimages-and-original-diagnostic-provenance-retained','result':'PASS'})
    rpath=HERE/'stage_runtime_optimized_v4.py';runtime=types.ModuleType('_cal_T02_v4_pure_runtime');runtime.__file__=str(rpath)
    exec(compile(rpath.read_bytes(),str(rpath),'exec',dont_inherit=True),runtime.__dict__)
    synthetic={key:{'sha256':'e'*64} for key in runtime.FAMILY_FIELDS};newroot=(HERE/'instances/optimized-0004').relative_to(ROOT).as_posix()
    dump=lambda n:ast.dump(n,include_attributes=False)
    class Structure(ast.NodeTransformer):
        def visit_Constant(self,node):
            if isinstance(node.value,str):node.value='<string>'
            return node
    for row in baseline['current_runtime_API_bindings']:
        raw=inputs.exact(row);name=Path(row['path']).name;text=runtime.transform(raw.decode(),name,old,synthetic,newroot)
        if name=='current_machine_context_scope.py':assert text.encode()==raw
        elif name.endswith('.py'):assert dump(Structure().visit(ast.parse(raw)))==dump(Structure().visit(ast.parse(text)))
        else:assert text.count(runtime.NEW_PUBLIC)==4
    checks.append({'case':'only-inmemory-synthetic-runtime-rebase-preserves-guard-AST-structure-and-machine-context-bytes-no-output','result':'PASS'})
    parent_common=(parent/'recipe_inputs_v3.py').read_text();new_common=(HERE/'recipe_inputs_v4.py').read_text()
    expected=parent_common.replace("BASELINE_PIN='9632f298d7faccf903aaa2adbea41c09fe00ca28fd92f06a6f58fc8ba249a742'","BASELINE_PIN="+repr(inputs.BASELINE_PIN)).replace("parent_recipe_row_count']==28","parent_recipe_row_count']==159").replace('optimized-0003','optimized-0004')
    assert expected==new_common
    activation=json.loads((HERE/'activation-selection.template.json').read_bytes());assert activation['status']=='pending-margin-and-observer-merge' and activation['instance']=='optimized-0004' and activation['margin_merge_binding'] is activation['observer_merge_binding'] is None
    assert recipe['source_period_hours']==24 and recipe['reader_permission_max_seconds']==1800 and recipe['Session_permission_max_seconds']==900
    checks.append({'case':'original-composition-preload-interface-gate-clocks-lifetimes-and-exclusive-instance-retained-pending-inputs-refuse','result':'PASS'})
    inputs.verify_baseline();assert not (HERE/'instances').exists()
    for row in recipe['files']:assert sha((ROOT/row['path']).read_bytes())==row['sha256']
    checks.append({'case':'all-parent-shared-frozen-inputs-still-exact-at-exit-zero-native-or-runtime-instance','result':'PASS'})
    result={'schema_version':'lab-T02-v4-actual-author-static-checks/v1-candidate','authority_effect':'none','result':'PASS-pure-preparation-only','checks':checks,'count':len(checks),'recipe_sha256':sys.argv[1],
            'actual_installed_interpreter':sys.executable,'Source_native_reader_mapper_Context_Service_Session_or_lease_assembly_executed':False,
            'shared_API_capture3_parent_or_private_state_modified':False,'synthetic_pin_checks_not_runtime_speed_or_margin_qualification':True,'task_complete':False}
    with (HERE/'STATIC-CHECKS.json').open('x') as f:json.dump(result,f,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'result':result['result'],'checks':result['count'],'recipe_sha256':sys.argv[1]}))
if __name__=='__main__':main()
