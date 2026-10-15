"""Pure selector checks; no family creation, shared writes or lease activation."""
import argparse, ast, hashlib, json, types
from pathlib import Path

HERE = Path(__file__).absolute().parent
ROOT = HERE.parents[6]
RECIPE = ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T02/optimized-family-preparation-0004'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def exact(row):
    if type(row) is not dict or set(row) != {'path','sha256'}:
        raise ValueError('closed control binding required')
    raw = (ROOT/row['path']).read_bytes()
    if sha(raw) != row['sha256']:
        raise ValueError('selected control input changed')
    return raw

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--selection-sha256', required=True)
    args = parser.parse_args()
    selection = json.loads(exact({'path':(HERE/'selection.json').relative_to(ROOT).as_posix(),'sha256':args.selection_sha256}))
    original_raw = exact(selection['original_stager_binding'])
    corrected_raw = exact(selection['corrected_stager_binding'])
    manifest = json.loads(exact(selection['recipe_manifest_binding']))
    declared = {row['path']:row for row in manifest['files']}
    baseline_row = selection['baseline_binding']
    if declared[baseline_row['path']]['sha256'] != baseline_row['sha256']:
        raise ValueError('baseline is not selected by retained recipe')
    baseline = json.loads(exact(baseline_row))
    old_descriptor = json.loads(exact(baseline['fixed_runtime_descriptor_binding']))
    path = ROOT/selection['corrected_stager_binding']['path']
    module = types.ModuleType('_cal_runtime_stager_correction_controls')
    module.__file__ = str(path)
    exec(compile(corrected_raw,str(path),'exec',dont_inherit=True),module.__dict__)
    cases = []
    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        cases.append({'case':name,'result':'PASS'})
    check('true corrected filename and explicit retained recipe origin', module.transform.__code__.co_filename == str(path) and module.RECIPE == RECIPE)
    original_ast = ast.parse(original_raw)
    corrected_ast = ast.parse(corrected_raw)
    original_functions = {node.name:node for node in original_ast.body if isinstance(node,ast.FunctionDef)}
    corrected_functions = {node.name:node for node in corrected_ast.body if isinstance(node,ast.FunctionDef)}
    check('original callable set conserved', set(original_functions) == set(corrected_functions))
    for name in ('sha','binding','write','main'):
        check('unchanged callable '+name,ast.dump(original_functions[name]) == ast.dump(corrected_functions[name]))
    class RecipeOrigin(ast.NodeTransformer):
        def visit_Name(self,node):
            if node.id == 'HERE':
                return ast.copy_location(ast.Name(id='RECIPE',ctx=node.ctx),node)
            return node
    for name in ('inputs','stage'):
        check('all original checks retained in '+name,ast.dump(RecipeOrigin().visit(original_functions[name])) == ast.dump(corrected_functions[name]))
    new_descriptor = {'context_source_binding':{'sha256':'f'*64},'mapper_package_binding':{'sha256':'e'*64}}
    future = RECIPE.relative_to(ROOT).as_posix()+'/instances/optimized-0004'
    for row in baseline['current_runtime_API_bindings']:
        raw = exact(row).decode(); name = Path(row['path']).name
        result = module.transform(raw,name,old_descriptor,new_descriptor,future)
        if name == 'current_machine_context_scope.py':
            check('machine context scope remains byte identical',result == raw)
        else:
            check('future selector origin and identity '+name,module.OLD_FAMILY not in result and module.OLD_PUBLIC not in result and module.NEW_PUBLIC in result)
        if name == 'source_bridge.py':
            check('actual source bridge namespace selects family4', '_cal_api17_current_source8_optimized_0004' in result and '_cal_api17_current_source8_optimized_0003' not in result)
    for name,raw in [('unselected.py','x=1'),('source_bridge.py','x=1'),('authentication.schema.json','{}')]:
        try:
            module.transform(raw,name,old_descriptor,new_descriptor,future)
        except ValueError:
            cases.append({'case':'reject unresolved or unselected input '+name,'result':'PASS'})
        else:
            raise AssertionError('unresolved transform accepted')
    value = {'schema_version':'lab-T02-runtime-stager-correction-controls/v1-candidate','authority_effect':'none','result':'PASS-scoped-pure-transform','cases':cases,'actual_family_constructed':False,'selectors_published':False,'shared_API_modified':False,'lease_opened':False,'task_complete':False}
    with (HERE/'controls-result.json').open('x') as stream:
        stream.write(json.dumps(value,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'result':value['result'],'controls':len(cases),'runtime_executed':False}))

if __name__ == '__main__':
    main()
