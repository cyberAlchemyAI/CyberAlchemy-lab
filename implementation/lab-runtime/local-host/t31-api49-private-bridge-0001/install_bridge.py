"""Select a private T31 all-28 output plan before reader-policy signing.

The caller owns the actual /tmp workspace and source/policy fixture. This
bootstrap only supplies exact material bytes and a genuine five-module
CompletionBridge selector. It does not dispatch a producer or grant authority.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import types

from jsonschema import Draft202012Validator

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v49-t31-current-guard-0002'
SOURCE_SHA = 'e283b71d9947be8f1dde8ce714664eefd3743fc2f872add5b586fb9bcf86cae1'
PROFILE_SHA = 'dc0106126515b58907fa299987c52e9b4afb79ca4c482fb9428f3d12a453cbb5'
ADAPTER = {'path': 'implementation/lab-runtime/local-host/t31-api49-current-guard-bootstrap-0002/bootstrap.py',
           'sha256': '8eb20c56a330cdb05fdaea7287901e6605b252f776aedaf2ebd6ac6d515a0325'}
PLAN_REF = 'private:T31:workflow-output-plan-v4'
BRIDGE_REF = 'private:T31:workflow-output-bridge-v3'


def sha(raw): return hashlib.sha256(raw).hexdigest()


def exact(path, expected):
    path = Path(path)
    if (not path.is_absolute() or not path.is_relative_to(ROOT) or
            path.is_symlink() or any(part.is_symlink() for part in path.parents)):
        raise ValueError('selected bridge source path differs')
    raw = path.read_bytes()
    if sha(raw) != expected:
        raise ValueError('selected bridge source byte differs')
    return raw


def selected_rows():
    manifest = json.loads(exact(API / 'source-manifest.json', SOURCE_SHA))
    profile = json.loads(exact(API / 'contract-profile.json', PROFILE_SHA))
    source = {row['path']: row['sha256'] for row in manifest['files']}
    files = {row['path']: row['sha256'] for row in profile['files']}
    if len(source) != 208 or len(files) != 33425:
        raise ValueError('selected bridge source/profile inventory differs')
    return source, files


def bridge_modules_binding():
    source, files = selected_rows()
    name = (API / 'host-bridge.schema.json').relative_to(ROOT).as_posix()
    if source.get(name) is None:
        raise ValueError('selected host bridge schema is absent')
    schema = json.loads(exact(ROOT / name, source[name]))
    bindings = schema['properties']['module_bindings']['const']
    if set(bindings) != {'protected_inputs', 'semantic_graph', 'environment',
                         'dependencies', 'private_content'}:
        raise ValueError('closed actual bridge modules differ')
    for binding in bindings.values():
        if files.get(binding['path']) != binding['sha256']:
            raise ValueError('trusted bridge module absent from API profile')
        exact(ROOT / binding['path'], binding['sha256'])
    return schema, bindings


def owned(path):
    path = Path(path)
    if (not path.is_absolute() or not path.is_relative_to('/tmp') or
            path.is_symlink() or any(item.is_symlink() for item in path.parents)):
        raise ValueError('actual private bridge root differs')
    info = os.stat(path, follow_symlinks=False)
    if (not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or
            stat.S_IMODE(info.st_mode) != 0o700):
        raise ValueError('private bridge root owner/mode differs')
    return path


def prepare_materials(*, owned_root, principal_ref, scope_ref, source_cut,
                      first_api_custody=None):
    """Return (materials, descriptor binding, plan binding) before manifest seal.

    `first_api_custody` may identify an independently authenticated read
    Service's actual Vault root. If absent, that first invocation remains
    unexecutable until a new private plan is selected by a new policy.
    """
    root = owned(owned_root)
    source, files = selected_rows()
    schema, bindings = bridge_modules_binding()
    spec = importlib.util.spec_from_file_location('t31_selected_plan_constructor',
        ROOT / 'implementation/lab-runtime/local-host/working/t31-private-output-plan-draft-0001/prepare.py')
    plan_module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = plan_module
    spec.loader.exec_module(plan_module)
    if len({row['invocation_ref'] for row in json.loads(exact(plan_module.TEMPLATE,
             plan_module.TEMPLATE_SHA))['transitions'].values()}) != 21:
        raise ValueError('original invocation group inventory differs')
    refs = sorted({row['invocation_ref'] for row in json.loads(
        exact(plan_module.TEMPLATE, plan_module.TEMPLATE_SHA))['transitions'].values()})
    groups = root / 'output-custody'
    groups.mkdir(mode=0o700)
    custody = {}
    scopes = {}
    for index, ref in enumerate(refs):
        folder = groups / f'group-{index:02d}'
        folder.mkdir(mode=0o700)
        (folder / 'objects').mkdir(mode=0o700)
        custody[ref] = (folder, ['objects'])
        scopes[ref] = scope_ref
    if first_api_custody is not None:
        custody['T31:api-context'] = (owned(first_api_custody), ['objects'])
    late = root / 'late-invocation-inputs'
    late.mkdir(mode=0o700)
    for name in ('invocations', 'materials'):
        (late / name).mkdir(mode=0o700)
    plan_raw, selected_materials = plan_module.prepare(
        api_dir=API, source_sha=SOURCE_SHA, profile_sha=PROFILE_SHA,
        adapter_binding=ADAPTER, principal_ref=principal_ref, scope_ref=scope_ref,
        source_cut=source_cut, custody_by_invocation=custody,
        output_scope_by_invocation=scopes,
        late_input_custody=(late, ['invocations', 'materials']),
        material_prefix='private:T31:bridge-v1')
    plan_binding = {'ref': PLAN_REF, 'sha256': sha(plan_raw)}
    descriptor = {'schema_version': 'lab-installation-release-host-bridge/v3-candidate',
                  'module_bindings': bindings, 'protected_inputs': None,
                  'composite_environment': None, 'native_launch_binding': None,
                  'workflow_output_binding': plan_binding, 'authority_effect': 'none'}
    Draft202012Validator(schema).validate(descriptor)
    descriptor_raw = json.dumps(descriptor, sort_keys=True, separators=(',', ':')).encode()
    descriptor_binding = {'ref': BRIDGE_REF, 'sha256': sha(descriptor_raw)}
    selected_materials.update({PLAN_REF: plan_raw, BRIDGE_REF: descriptor_raw})
    if len(selected_materials) != 69:
        raise ValueError('closed bridge/private output material inventory differs')
    return selected_materials, descriptor_binding, plan_binding


def _selected_module(name, binding, files):
    path = ROOT / binding['path']
    if files.get(binding['path']) != binding['sha256']:
        raise ValueError('actual selected trusted module is absent')
    raw = exact(path, binding['sha256'])
    module = importlib.util.module_from_spec(importlib.util.spec_from_loader(name, loader=None))
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(raw, str(path), 'exec', dont_inherit=True), module.__dict__)
    if exact(path, binding['sha256']) != raw:
        raise ValueError('trusted bridge module changed during import')
    return module


def bind_service(service, protocol, descriptor_binding):
    """Install the exact CompletionBridge on an authenticated selected host."""
    source, files = selected_rows()
    schema, bindings = bridge_modules_binding()
    if (type(service).__module__ != protocol.__name__.rsplit('.', 1)[0] + '.service' or
            getattr(service, 'completion_bridge', None) is not None):
        raise ValueError('actual unbound selected Service required')
    raw = service.vault.material(descriptor_binding)
    if sha(raw) != descriptor_binding['sha256']:
        raise ValueError('private bridge descriptor changed')
    descriptor = json.loads(raw)
    Draft202012Validator(schema).validate(descriptor)
    if descriptor['module_bindings'] != bindings:
        raise ValueError('trusted bridge module selection differs')
    dependencies = bindings['dependencies']
    dependency_path = ROOT / dependencies['path']
    for name in ('checked_io', 'stage_io', 'closure'):
        dependency = dependency_path.with_name(name + '.py')
        relative = dependency.relative_to(ROOT).as_posix()
        if files.get(relative) is None:
            raise ValueError('trusted dependency base absent from selected profile')
        _selected_module(name, {'path': relative, 'sha256': files[relative]}, files)
    proof_folder = (ROOT / bindings['protected_inputs']['path']).parent
    proof_init = proof_folder / '__init__.py'
    proof_init_relative = proof_init.relative_to(ROOT).as_posix()
    if files.get(proof_init_relative) is None:
        raise ValueError('trusted proof package initializer absent from selected profile')
    proof_name = '_cal_t31_bridge_release_proof_0001'
    proof_raw = exact(proof_init, files[proof_init_relative])
    proof = types.ModuleType(proof_name)
    proof.__file__ = str(proof_init)
    proof.__path__ = [str(proof_folder)]
    proof.__package__ = proof_name
    sys.modules[proof_name] = proof
    modules = {}
    for key, binding in bindings.items():
        name = (proof_name + '.' + key if key in ('protected_inputs', 'semantic_graph')
                else '_cal_t31_bridge_' + key)
        modules[key] = _selected_module(name, binding, files)
    exec(compile(proof_raw, str(proof_init), 'exec', dont_inherit=True), proof.__dict__)
    if exact(proof_init, files[proof_init_relative]) != proof_raw:
        raise ValueError('trusted proof package initializer changed during import')
    component = __import__(protocol.__name__.rsplit('.', 1)[0] + '.completion_bridges',
                           fromlist=['CompletionBridge'])
    selected = component.CompletionBridge(raw, descriptor_binding, ROOT, modules, None)
    service.completion_bridge = selected
    factory = __import__(protocol.__name__.rsplit('.', 1)[0] + '.workflow_output_factory',
                         fromlist=['selected_plan'])
    plan = factory.selected_plan(service)
    if plan is None or len(plan['transitions']) != 28:
        raise ValueError('actual selected private all-28 plan unavailable')
    return plan
