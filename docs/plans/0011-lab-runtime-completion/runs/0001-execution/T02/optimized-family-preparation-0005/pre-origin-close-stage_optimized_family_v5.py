"""Prepare a distinct candidate family from independently frozen T03 inputs.

This command only stages owned files. It never invokes a source/native/context
constructor, opens a Session, acquires the runtime lock, or edits an API.
"""
import argparse
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[6]
RECIPE4=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T02/optimized-family-preparation-0004'
DIAGNOSTIC = ROOT / 'product/lab/release-candidates/v1/interface/current-session-fixtures-v1-completion-0001/instances/diagnostic-0004'
POSTIMAGES = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T03/caller-integration-0004/postimages'
TARGETS = {'source/base.py', 'reader/reader.py', 'mapped/base.py', 'context/base.py', 'context/generation.py'}
CORRECTED_GENERATION = POSTIMAGES / 'context/generation.py'
CAPTURE_PATH = 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T03/integrity-comparison-preparation-0001/capture.py'
OPTIMIZATION_PIN='e221709e67a4e0f717486a4f31d93ecaaf971adf4d5a18621c5bf62be1b478e1'


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def parse(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'duplicate selected JSON key'); result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda _: need(False, 'nonfinite selected JSON'))


def exact(binding, limit=16 * 1024 * 1024):
    need(type(binding) is dict and set(binding) == {'path', 'sha256'}, 'closed exact binding required')
    relative = Path(binding['path'])
    need(not relative.is_absolute() and relative.as_posix() == binding['path'] and '..' not in relative.parts,
         'canonical repository locator required')
    path = ROOT / relative; descriptors = [os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)]
    links = []
    try:
        parent = descriptors[-1]
        for part in path.parts[1:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            descriptors.append(child); info = os.fstat(child)
            links.append((parent, part, child, (info.st_dev, info.st_ino, info.st_mode, info.st_uid)))
            parent = child
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        try:
            before = os.fstat(fd)
            need(stat.S_ISREG(before.st_mode) and before.st_size <= limit, 'bounded selected regular input required')
            def stamp(value):
                return (value.st_dev, value.st_ino, value.st_mode, value.st_uid, value.st_size, value.st_mtime_ns, value.st_ctime_ns)
            parts = []; size = 0
            while block := os.read(fd, min(1024 * 1024, limit + 1 - size)):
                parts.append(block); size += len(block); need(size <= limit, 'selected input grew beyond limit')
            raw = b''.join(parts)
            need(stamp(before) == stamp(os.fstat(fd)) == stamp(os.stat(path.name, dir_fd=parent, follow_symlinks=False))
                 and sha(raw) == binding['sha256'], 'selected bytes or attachment changed')
            for anchor, name, held, identity in reversed(links):
                a = os.stat(name, dir_fd=anchor, follow_symlinks=False); h = os.fstat(held)
                need((a.st_dev, a.st_ino, a.st_mode, a.st_uid) == (h.st_dev, h.st_ino, h.st_mode, h.st_uid) == identity,
                     'selected ancestor detached')
            return raw
        finally:
            os.close(fd)
    finally:
        for fd in reversed(descriptors):
            os.close(fd)


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())}


def fixed_literal(text, name, replacement):
    tree = ast.parse(text)
    assignments = [node for node in tree.body if isinstance(node, ast.Assign)
                   and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id == name]
    need(len(assignments) == 1, 'closed phase pin assignment unavailable: ' + name)
    node = assignments[0]; value = ast.literal_eval(node.value)
    need(type(value) is str, 'phase pin must be a literal string')
    lines = text.splitlines(keepends=True)
    start = sum(len(line) for line in lines[:node.value.lineno - 1]) + node.value.col_offset
    end = sum(len(line) for line in lines[:node.value.end_lineno - 1]) + node.value.end_col_offset
    return text[:start] + repr(replacement) + text[end:]


def selected_recipe_inputs():
    import types,sys
    path=HERE/'recipe_inputs_v5.py';raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!='392789f6da9d870f059d7a7cfec2b4127c88ff3970b283cf27c54e3d1c53ae04':raise ValueError('independently selected v5 preparation code differs')
    name='_cal_T02_v5_selected_recipe_inputs_'+__name__.replace('.','_')
    module=types.ModuleType(name);module.__file__=str(path)
    exec(compile(raw,str(path),'exec',dont_inherit=True),module.__dict__)
    return module

def stage(instance, optimization_binding, recipe_binding, activation_binding):
    inputs=selected_recipe_inputs();baseline=inputs.verify_baseline();composition=inputs.check_activation(activation_binding,instance)
    need(optimization_binding=={'path':(HERE/'optimization-selection.json').relative_to(ROOT).as_posix(),'sha256':OPTIMIZATION_PIN},'exact independently selected v5 optimization required')
    optimization = parse(exact(optimization_binding))
    need(set(optimization)==set(['actual_owner_outcome', 'authority_effect', 'caller_integration_handoff_binding', 'caller_integration_manifest_binding', 'caller_review_binding', 'caller_selection_binding', 'companion_code_binding', 'companion_handoff_binding', 'companion_manifest_binding', 'helper_code_binding', 'helper_handoff_binding', 'helper_manifest_binding', 'helper_review_binding', 'postimages', 'schema_version', 'status']),'closed v5 selection required')
    need(optimization['schema_version']=='lab-optimized-source8-capture-selection/v5-candidate'
         and optimization['status']=='frozen-reviewed-components-candidate-recipe-review-pending'
         and optimization['authority_effect']=='none' and optimization['actual_owner_outcome'] is None,'scoped reviewed component selection required')
    helper_raw=exact(optimization['helper_code_binding'])
    need(optimization['helper_code_binding']['path']==CAPTURE_PATH,'true reviewed helper origin required')
    selected_inputs={}
    def collect(binding):
        raw=exact(binding);need(selected_inputs.get(binding['path'],binding)==binding,'conflicting independently selected optimized input')
        selected_inputs[binding['path']]=binding
        return raw
    for key in optimization:
        if key.endswith('_binding'):collect(optimization[key])
    for key in ('helper_manifest_binding','caller_integration_manifest_binding','companion_manifest_binding'):
        manifest=parse(collect(optimization[key]))
        need(manifest['authority_effect']=='none','component cannot grant authority')
        for row in manifest['files']:
            need(set(row) in ({'path','sha256'},{'path','sha256','size_bytes'}),'closed component row required')
            raw=collect({'path':row['path'],'sha256':row['sha256']})
            if 'size_bytes' in row:need(len(raw)==row['size_bytes'],'declared component size differs')
    need(optimization['helper_code_binding'] in selected_inputs.values() and optimization['companion_code_binding'] in selected_inputs.values(),'helper and companion exact closures required')
    rows = optimization['postimages']
    need(type(rows) is list and len(rows) == 5 and {row['relative_target'] for row in rows} == TARGETS,
         'all five exact optimized postimages required')
    captured = {}
    for row in rows:
        need(set(row) == {'relative_target', 'original_binding', 'postimage_binding'}, 'closed postimage selection required')
        target = row['relative_target']
        need(row['original_binding']['path'] == (DIAGNOSTIC / target).relative_to(ROOT).as_posix()
             and row['postimage_binding']['path'] == (CORRECTED_GENERATION if target == 'context/generation.py' else POSTIMAGES / target).relative_to(ROOT).as_posix(),
             'true diagnostic predecessor and new T03 origin required')
        collect(row['original_binding']); captured[target] = collect(row['postimage_binding']).decode('utf-8')
        ast.parse(captured[target])
    source_tree = ast.parse(captured['source/base.py'])
    capture_pin = next(ast.literal_eval(node.value) for node in source_tree.body
                       if isinstance(node, ast.Assign) and len(node.targets) == 1
                       and isinstance(node.targets[0], ast.Name) and node.targets[0].id == '_CAPTURE_PIN')
    need(capture_pin == optimization['helper_code_binding']['sha256'] == sha(helper_raw), 'independent capture code pin differs')
    recipe = parse(exact(recipe_binding))
    need(recipe['authority_effect'] == 'none' and recipe['runtime_executed'] is False, 'prepared recipe cannot grant authority')
    need(recipe['parent_recipe_binding']==baseline['parent_recipe4_binding'] and recipe['original_recipe_declarations']==baseline['original_recipe_declarations'] and recipe['declaration_mapping']==baseline['declaration_mapping'],'complete original declarations and true recipe4 dependency required')
    recipe_rows = recipe['files']
    need(not {row['path'] for row in recipe_rows}&inputs.FORBIDDEN_LIVE_API_INPUTS,'live mutable API preparation input in technical recipe')
    code = {}
    for row in recipe_rows:
        raw = exact(row)
        if row['path'].endswith('build_family_optimized_v5.py'):
            code['builder'] = raw
    need('builder' in code, 'exact true owned builder missing')
    name = '_cal_owned_optimized_family_stager_v5'
    need(name not in sys.modules, 'new recipe namespace required')
    path = HERE / 'build_family_optimized_v5.py'
    spec = importlib.util.spec_from_loader(name, loader=None, origin=str(path))
    builder = importlib.util.module_from_spec(spec); builder.__file__ = str(path); sys.modules[name] = builder
    exec(compile(code['builder'], str(path), 'exec'), builder.__dict__)
    selection = builder.stage(instance,activation_binding)
    family = HERE / 'instances' / instance
    need(not any((family / role / 'source-manifest.json').exists() for role in ('source', 'reader', 'mapped', 'context')),
         'only unselected fresh roles may be changed')
    old_prefix = 'completion-current-session-0001-diagnostic-0004'
    old_family = DIAGNOSTIC.relative_to(ROOT).as_posix(); new_family = family.relative_to(ROOT).as_posix()
    adopted = []
    for target, text in captured.items():
        text = text.replace('HERE.parents[8]', 'HERE.parents[9]')
        text = text.replace(old_family, new_family).replace(old_prefix, selection['prefix'])
        text = text.replace('_cal_completion_diagnostic_0004', '_cal_completion_' + instance.replace('-', '_'))
        if target == 'mapped/base.py':
            for field, token in [('SOURCE_PIN', '__OPT_SOURCE_MANIFEST_PIN__'), ('PACKAGE_PIN', '__OPT_SOURCE_PACKAGE_PIN__'),
                                 ('ADAPTER_PIN', '__OPT_READER_MANIFEST_PIN__')]:
                text = fixed_literal(text, field, token)
        elif target == 'context/base.py':
            for field, token in [('MAPPED_PIN', '__OPT_MAPPER_MANIFEST_PIN__'), ('MAPPED_PACKAGE_PIN', '__OPT_MAPPER_PACKAGE_PIN__')]:
                text = fixed_literal(text, field, token)
        elif target == 'context/generation.py':
            text = fixed_literal(text, 'MAPPED_SOURCE_SHA', '__OPT_MAPPER_MANIFEST_PIN__')
        need(old_family not in text and old_prefix not in text and '_cal_completion_diagnostic_0004' not in text,
             'optimized successor retained a former family execution selector')
        ast.parse(text); path = family / target
        prior = bind(path)
        retained = family / 'staged-preimages' / target
        retained.parent.mkdir(parents=True, exist_ok=True)
        with retained.open('xb') as stream:
            stream.write(path.read_bytes())
        path.write_text(text)
        for template_row in selection['template_rows']:
            if template_row['new']['path'] == path.relative_to(ROOT).as_posix():
                template_row['new'] = bind(path)
                template_row['changed'] = True
        adopted.append({'relative_target': target, 'prior_unselected_stage_selector': prior,
                        'preserved_stage_preimage_binding': bind(retained), 'new_binding': bind(path),
                        'frozen_optimized_postimage_binding': next(row['postimage_binding'] for row in rows if row['relative_target'] == target),
                        'permitted_rebases': ['new true root depth', 'new family namespace/principal prefixes and reader entrypoint',
                                             'independent future phase pins only before each role snapshot']})
    selection['optimized_capture_selection_binding'] = optimization_binding
    collect(optimization_binding)
    for binding in (activation_binding,composition['margin_merge_binding'],composition['observer_merge_binding']):collect(binding)
    selection['optimized_input_bindings'] = [selected_inputs[name] for name in sorted(selected_inputs)]
    selection['optimized_input_closure_component_manifests'] = [optimization[key] for key in ('helper_manifest_binding','caller_integration_manifest_binding','companion_manifest_binding')]
    selection['future_composition_prerequisite_binding'] = activation_binding
    selection['preserved_preparation_baseline_binding']={'path':(HERE/'preparation-baseline.json').relative_to(ROOT).as_posix(),'sha256':inputs.BASELINE_PIN}
    selection['optimized_recipe_bindings'] = [recipe_binding, *recipe_rows]
    selection['optimized_recipe_declaration_mapping']=baseline['declaration_mapping']
    selection['mutable_API_preparation_snapshot_pairs']=baseline['mutable_snapshot_pairs']
    selection['preserved_recipe4_binding']=baseline['parent_recipe4_binding']
    need(not {row['path'] for row in selection['optimized_recipe_bindings']+selection['optimized_input_bindings']}&inputs.FORBIDDEN_LIVE_API_INPUTS,'construction selected a live mutable preparation locator')
    selection['optimized_postimage_adoption'] = adopted
    selection['runtime_executed'] = False; selection['native_construction_executed'] = False
    selection['template_bindings_are_unqualified_staging_state_not_final_role_snapshots'] = True
    # Only this new unsnapshotted owned selection is replaced. Frozen parents
    # and every earlier family/source/period/authority record remain untouched.
    (family / 'construction-selection.json').write_text(json.dumps(selection, sort_keys=True, indent=2) + '\n')
    for row in recipe_rows:
        exact(row)
    exact(optimization_binding)
    print(json.dumps({'status': 'STAGED-new-optimized-family-UNQUALIFIED', 'construction_selection_binding': bind(family / 'construction-selection.json'),
                      'native_or_runtime_executed': False, 'shared_API_modified': False, 'authority_effect': 'none'}, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--instance', required=True)
    parser.add_argument('--optimization-selection', required=True); parser.add_argument('--optimization-selection-sha256', required=True)
    parser.add_argument('--recipe-selection', required=True); parser.add_argument('--recipe-selection-sha256', required=True)
    parser.add_argument("--activation-selection",required=True);parser.add_argument("--activation-selection-sha256",required=True)
    args = parser.parse_args()
    stage(args.instance, {'path': args.optimization_selection, 'sha256': args.optimization_selection_sha256},
          {'path': args.recipe_selection, 'sha256': args.recipe_selection_sha256},
          {'path':args.activation_selection,'sha256':args.activation_selection_sha256})


if __name__ == '__main__':
    main()
