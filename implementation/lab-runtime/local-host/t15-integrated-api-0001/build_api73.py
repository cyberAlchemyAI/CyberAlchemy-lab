"""Seal one coherent resolver, learning, Session and Machine successor."""
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
BASE = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v71-t15-integrated-closure-0001'
NEW = BASE.parent / 'api-integration-v73-t15-learning-selector-0001'
T03 = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T03/local-lifecycle-actual-clock-0001'
DELTA = ROOT / 'implementation/lab-runtime/local-host/t22-native-agent-contest-0001/integrated-resolver-delta-0001'
SOURCE = 'c05e64221236ce7e3be16d9560014f0d98e37ad36c82e842ca9934a54a85cbab'
PROFILE = 'f70913d3c3fbc1189646dcb4cad3dce379a9ca8ad0fdfa5ba4c96e263356611e'
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
encoded = lambda value: (json.dumps(value,sort_keys=True,indent=2)+'\n').encode()
binding = lambda path: {'path':Path(path).relative_to(ROOT).as_posix(),'sha256':sha(path)}


def need(value, reason):
    if not value:
        raise ValueError(reason)


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def methods(folder):
    result = {}
    for path in [*folder.glob('test_*.py'),*folder.glob('run_*checks.py')]:
        for cls in ast.parse(path.read_text()).body:
            if isinstance(cls,ast.ClassDef):
                for node in cls.body:
                    if isinstance(node,ast.FunctionDef) and node.name.startswith('test_'):
                        result[path.name+':'+cls.name+'.'+node.name] = ast.dump(node,include_attributes=False)
    return result


def owned_files():
    return [path for path in NEW.rglob('*') if path.is_file()
            and '__pycache__' not in path.parts and 'receipts' not in path.parts
            and path.suffix != '.pyc' and path.name not in ('source-manifest.json','rebind-receipt.json')]


def main():
    os.umask(0o077)
    need(not NEW.exists(), 'final common successor already exists')
    need(sha(BASE/'source-manifest.json') == SOURCE and sha(BASE/'contract-profile.json') == PROFILE, 'common predecessor differs')
    need(sha(DELTA/'DELTA-PINS.json') == 'a9125c6f6a81a374e5f7fc339a0f0fe77160747b8d9db36418cc59aebdf391b7', 'actual native resolver delta differs')
    delta = json.loads((DELTA/'DELTA-PINS.json').read_bytes())
    need(delta['predecessor_source_binding'] == binding(BASE/'source-manifest.json'), 'resolver selects another common predecessor')
    source = json.loads((BASE/'source-manifest.json').read_bytes())
    profile = json.loads((BASE/'contract-profile.json').read_bytes())
    for row in source['files']:
        need(sha(ROOT/row['path']) == row['sha256'], 'common predecessor member changed: '+row['path'])
    for row in delta['postimages']:
        need(sha(ROOT/row['path']) == row['sha256'], 'actual resolver postimage changed')
    portable = T03/'portable-margin-postimages-0002'
    portable_pins = {'observed_margin.py':'f4cf3692bec2dec828906edc27faa5be232e37f76f7716ee6bfc6fba9beae52e',
                     'margin_capture.py':'4d0cddc7d68729dcf929498e8873e5e789ced6bbe1275e0a5c15abbe32c9a07a'}
    for name,pin in portable_pins.items():
        need(sha(portable/name)==pin, 'portable exact role/receipt helper differs')
    selection_path = T03/'pure_learning_preflight_patch_0002.py'
    need(selection_path.is_file(), 'pure learning preflight patch missing')
    selection = module(selection_path, 'final_learning_selection_delta')
    machine_path = HERE/'final_machine_seal.py'
    machine = module(machine_path, 'final_machine_seal_delta')
    shutil.copytree(BASE,NEW,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    # Resolver postimages preserve original API71 origin pins and its exact
    # original validation-receipt path. They must never be blanket-retargeted.
    for row in delta['postimages']:
        relative = (ROOT/row['path']).relative_to(DELTA)
        target = NEW/relative
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/row['path'],target)
    for name in portable_pins:
        shutil.copyfile(portable/name,NEW/name)
    path = NEW/'service.py'
    path.write_text(selection.apply(path.read_text()))
    path = NEW/'machine_transport.py'
    path.write_text(machine.apply(path.read_text()))
    for name in ('source_bridge.py','workflow_output_registry.py'):
        path = NEW/name
        path.write_text(path.read_text().replace(BASE.name,NEW.name).replace('_cal_api71_','_cal_api73_'))
    path = NEW/'producer-inputs.json'
    inputs = json.loads(path.read_bytes())
    inputs['signed_baseline_members'] = [row['path'] for row in inputs['inputs']]
    inputs['separately_pinned_public_members'] = []
    path.write_bytes(encoded(inputs))
    source_symbols = {node.targets[0].id for node in ast.parse((NEW/'source_bridge.py').read_text()).body
                      if isinstance(node,ast.Assign) and len(node.targets)==1
                      and isinstance(node.targets[0],ast.Name) and node.targets[0].id.startswith('CURRENT_')}
    for path in NEW.rglob('*.py'):
        for node in ast.walk(ast.parse(path.read_text())):
            if (isinstance(node,ast.Attribute) and isinstance(node.value,ast.Name)
                and node.value.id=='source' and node.attr.startswith('CURRENT_')):
                need(node.attr in source_symbols, 'unknown selected Source symbol: '+node.attr)
    original = methods(BASE)
    need(len(original)==345 and methods(NEW)==original, 'inherited method AST changed')
    oldprefix = BASE.relative_to(ROOT).as_posix()+'/'
    def recut(row):
        if row['path'].startswith(oldprefix):
            return binding(NEW/row['path'][len(oldprefix):])
        return row
    profile['files'] = [row for row in profile['files'] if not row['path'].startswith(oldprefix)]
    profile['files'] += [binding(path) for path in owned_files() if path.name != 'contract-profile.json']
    profile['files'] = sorted(profile['files'],key=lambda row:row['path'])
    for key,value in list(profile.items()):
        if key!='files' and type(value) is dict and set(value)=={'path','sha256'}:
            profile[key] = recut(value)
    profile['claim_ceiling'] = 'One current local integrated API with exact observed native Agent origin, fixture defer resolver and bounded Lesson/Session execution; final behavioral qualification pending.'
    (NEW/'contract-profile.json').write_bytes(encoded(profile))
    source['files'] = [row for row in source['files'] if not row['path'].startswith(oldprefix)]
    source['files'] += [binding(path) for path in owned_files()]
    source['files'] = sorted(source['files'],key=lambda row:row['path'])
    source['profile_binding'] = binding(NEW/'contract-profile.json')
    source['predecessor_source_manifest_binding'] = binding(BASE/'source-manifest.json')
    source['claim_ceiling'] = profile['claim_ceiling']
    (NEW/'source-manifest.json').write_bytes(encoded(source))
    receipt = {'schema_version':'lab-integrated-native-resolver-successor/v1-candidate',
               'successor_package':NEW.relative_to(ROOT).as_posix(),
               'successor_manifest_sha256':sha(NEW/'source-manifest.json'),
               'successor_source_binding':binding(NEW/'source-manifest.json'),
               'successor_profile_binding':binding(NEW/'contract-profile.json'),
               'predecessor_source_binding':binding(BASE/'source-manifest.json'),
               'actual_native_resolver_delta':binding(DELTA/'DELTA-PINS.json'),
               'actual_native_submission_receipt':delta['native_submission_receipt'],
               'actual_native_observation_receipt':delta['native_observation_receipt'],
               'portable_margin_postimages':[binding(portable/name) for name in portable_pins],
               'pure_learning_preflight_delta':binding(selection_path),
               'machine_captured_basis_delta':binding(machine_path),
               'inherited_methods':345,'changed_method_asts':0,'full345_qualified':False,
               't15_frozen':False,'t16_complete':False,'authority_effect':'none','actual_owner_outcome':None}
    (NEW/'rebind-receipt.json').write_bytes(encoded(receipt))
    (HERE/'API73-BUILD-0001.json').write_bytes(encoded(receipt))
    print(json.dumps(receipt,sort_keys=True))


if __name__=='__main__':
    main()
