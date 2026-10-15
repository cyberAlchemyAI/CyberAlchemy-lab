"""Authoring checks only: no stage(), constructor, native or lease call."""
import ast,copy,hashlib,json,sys,types
from pathlib import Path
HERE=Path(__file__).absolute().parent
ROOT=HERE.parents[6]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def main():
    raw=(HERE/'recipe-selection.json').read_bytes();assert sha(raw)==sys.argv[1];recipe=json.loads(raw);checks=[]
    assert not (HERE/'instances').exists()
    for row in recipe['files']:assert sha((ROOT/row['path']).read_bytes())==row['sha256']
    checks.append({'case':'every-exact-recipe-input-fresh-and-no-instance-created','rows':len(recipe['files']),'result':'PASS'})
    # This independently selected preparation helper imports standard library
    # only, and its baseline verifier does not execute any original software.
    p=HERE/'recipe_inputs_v3.py';module=types.ModuleType('_cal_T02_v3_pure_author_inputs');module.__file__=str(p)
    exec(compile(p.read_bytes(),str(p),'exec',dont_inherit=True),module.__dict__)
    baseline=module.verify_baseline();assert baseline['parent_recipe_row_count']==28
    checks.append({'case':'all28-parent-recipe-rows-and63-unique-baseline-preimages-fresh','rows':len(baseline['rows']),'result':'PASS'})
    opt=json.loads((HERE/'optimization-selection.json').read_bytes())
    from jsonschema import Draft202012Validator
    validator=Draft202012Validator(json.loads((HERE/'optimization-selection.schema.json').read_bytes()));validator.validate(opt)
    assert not validator.is_valid({**opt,'ambient_expected_pin':False})
    assert not validator.is_valid({**opt,'helper_code_binding':{'path':opt['helper_code_binding']['path'],'sha256':'0'*64}})
    checks.append({'case':'exact-closed-optimization-schema-and-wrong-pin-refusal','result':'PASS'})
    closure={}
    for key in opt:
        if key.endswith('_binding'):
            row=opt[key];assert sha((ROOT/row['path']).read_bytes())==row['sha256'];closure[row['path']]=row
    for key in ('helper_manifest_binding','caller_integration_manifest_binding','companion_manifest_binding'):
        manifest=json.loads((ROOT/opt[key]['path']).read_bytes())
        for row in manifest['files']:
            raw=(ROOT/row['path']).read_bytes();assert sha(raw)==row['sha256'];assert 'size_bytes'not in row or len(raw)==row['size_bytes']
            binding={'path':row['path'],'sha256':row['sha256']};assert closure.get(row['path'],binding)==binding;closure[row['path']]=binding
    assert opt['helper_code_binding'] in closure.values() and opt['companion_code_binding'] in closure.values()
    checks.append({'case':'all-three-helper-caller-companion-component-manifest-rows-captured','unique_rows':len(closure),'result':'PASS'})
    def tree(path):return ast.parse(path.read_bytes())
    def function(t,name):return next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name==name)
    dump=lambda n:ast.dump(n,include_attributes=False)
    old=ROOT/baseline['parent_recipe_binding']['path'];parent=old.parent
    oldc=(parent/'construct_optimized_v2.py').read_text().replace("'_cal_T02_current_","'_cal_T02_optimized_v3_current_")
    a=ast.parse(oldc);b=tree(HERE/'construct_optimized_v3.py')
    original=[n for n in a.body if isinstance(n,ast.FunctionDef) and n.name!='main']
    for n in original:assert dump(n)==dump(function(b,n.name))
    checks.append({'case':'every-original-construction-function-AST-preserved-after-only-namespace-rebase','functions':len(original),'result':'PASS'})
    oldbuilder=tree(parent/'build_family_optimized_v2.py');newbuilder=tree(HERE/'build_family_optimized_v3.py')
    original=copy.deepcopy(function(oldbuilder,'stage'));original.name='_stage_original'
    class Prefix(ast.NodeTransformer):
        def visit_Constant(self,node):
            if isinstance(node.value,str):node.value=node.value.replace('completion-optimized-source8-0002-','completion-optimized-source8-0003-')
            return node
    original=Prefix().visit(original);assert dump(original)==dump(function(newbuilder,'_stage_original'))
    checks.append({'case':'full-original-builder-domain-AST-preserved-after-name-and-prefix-rebase','result':'PASS'})
    stager=tree(HERE/'stage_optimized_family_v3.py')
    for name in ('need','sha','parse','exact','bind','fixed_literal'):
        assert dump(function(tree(parent/'stage_optimized_family_v2.py'),name))==dump(function(stager,name))
    selected=json.loads((ROOT/opt['caller_selection_binding']['path']).read_bytes())
    assert len(opt['postimages'])==5
    for row in opt['postimages']:
        peer=next(r for r in selected['postimages'] if r['target']==row['relative_target']);assert row['postimage_binding']==peer['postimage']
        assert sha((ROOT/row['postimage_binding']['path']).read_bytes())==row['postimage_binding']['sha256']
    checks.append({'case':'all-five-exact-caller0003-postimages-and-original-exact-capture-guards','result':'PASS'})
    capture=function(b,'capture');assert any(isinstance(n,ast.Subscript) and ast.unparse(n)=="selection['optimized_input_bindings']" for n in ast.walk(capture))
    assert 'companion_manifest_binding' in ast.unparse(function(stager,'stage')) and 'caller_integration_manifest_binding' in ast.unparse(function(stager,'stage'))
    checks.append({'case':'every-role-inherits-full-optimized-input-closure','result':'PASS'})
    runtime=types.ModuleType('_cal_T02_v3_pure_author_runtime');runtime.__file__=str(HERE/'stage_runtime_optimized_v3.py')
    exec(compile((HERE/'stage_runtime_optimized_v3.py').read_bytes(),runtime.__file__,'exec',dont_inherit=True),runtime.__dict__)
    olddescriptor=json.loads(module.exact(baseline['fixed_runtime_descriptor_binding']));synthetic={k:{'sha256':'e'*64} for k in runtime.FAMILY_FIELDS}
    newroot=(HERE/'instances/optimized-0003').relative_to(ROOT).as_posix()
    for row in baseline['current_runtime_API_bindings']:
        raw=module.exact(row);name=Path(row['path']).name;result=runtime.transform(raw.decode(),name,olddescriptor,synthetic,newroot)
        if name=='current_machine_context_scope.py':assert result.encode()==raw
        elif name.endswith('.py'):
            # Replace only selected constants in original source, then verify
            # complete AST parity with the transformation's returned text.
            ast.parse(result)
            oldtree=ast.parse(raw);newtree=ast.parse(result)
            class Structure(ast.NodeTransformer):
                def visit_Constant(self,node):
                    if isinstance(node.value,str):node.value='<string>'
                    return node
            assert dump(Structure().visit(oldtree))==dump(Structure().visit(newtree))
        else:assert result.count(runtime.NEW_PUBLIC)==4
    checks.append({'case':'pure-inmemory-current002-runtime-rebase-preserves-all-guard-AST-structure-and-machine-scope-bytes','result':'PASS-synthetic-pins-only-no-selector-output'})
    template=json.loads((HERE/'activation-selection.template.json').read_bytes());assert template['status']!='merged-reviewed-ready-for-Root-coordination'
    for path in HERE.glob('*.py'):compile(path.read_bytes(),str(path),'exec',dont_inherit=True)
    assert recipe['source_period_hours']==24 and recipe['reader_permission_max_seconds']==1800 and recipe['Session_permission_max_seconds']==900
    assert not (HERE/'instances').exists();module.verify_baseline()
    for row in recipe['files']:assert sha((ROOT/row['path']).read_bytes())==row['sha256']
    checks.append({'case':'original-lifetime-limits-no-native-or-runtime-output-and-fresh-exit-baseline','result':'PASS'})
    value={'schema_version':'lab-T02-v3-actual-author-static-checks/v1-candidate','authority_effect':'none','result':'PASS-pure-preparation-only','checks':checks,'count':len(checks),'recipe_sha256':sys.argv[1],
           'actual_installed_interpreter':sys.executable,'native_family_assembly_Source_reader_mapper_Context_Service_Session_or_lease':False,
           'shared_API_or_capture3_or_parent_modified':False,'synthetic_selector_checks_not_runtime_or_performance_qualification':True,'task_complete':False}
    with (HERE/'STATIC-CHECKS.json').open('x') as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'result':value['result'],'checks':len(checks),'recipe_sha256':sys.argv[1]}))
if __name__=='__main__':main()
