"""Actual API33-derived CompletionBridge/InstallationRelease technical binding."""

from datetime import datetime, timedelta, timezone
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import time
import types

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE = Path(__file__).resolve().parent
RUNNER = ROOT / 'implementation/lab-runtime/local-host/t08-current-mixed-boundary-0001/run_boundary.py'
RUNNER_SHA = 'd9f2bb14c7f5eb5f2a2decbc1ca71afce9c20f0f4ea358d9936d2927e4dd6311'
API = 'product/lab/release-candidates/v1/interface/api-integration-v33-t08-mixed-0002'
SOURCE_SHA = 'c10ba1191a64ad65cdaa74ff66e7ae81f20b13bfd5109638a90af36ecfde864c'
PROFILE_SHA = 'e73bf41bc161fd6eb75102022bbe8dfb78dea3f1003337ce6f00751e1226c567'
CONTENT = 'implementation/lab-runtime/local-host/t08-current-mixed-bind-0001/current_content.py'
CONTENT_SHA = '89e676278d50dc91dc0fb975ca7ae3107635a19bed7b7580e3ec0955ea485e9e'
SCHEMA_SHA = '8f6c45d6f81ef8c1e728ebe881b29f843ba3d68631e0353660d820ead3019e30'


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def sample(schema):
    if 'const' in schema:
        return schema['const']
    if 'enum' in schema:
        return schema['enum'][0]
    if 'anyOf' in schema:
        return sample(schema['anyOf'][0])
    if 'oneOf' in schema:
        return sample(schema['oneOf'][0])
    kind = schema.get('type')
    if kind == 'null':
        return None
    if kind == 'object':
        return {key: sample(schema['properties'][key]) for key in schema.get('required', [])}
    if kind == 'array':
        return [sample(schema.get('items', {})) for _ in range(schema.get('minItems', 0))]
    if kind == 'integer':
        return schema.get('minimum', 0)
    if kind == 'boolean':
        return False
    if kind == 'string':
        return '0' * 64 if '64' in schema.get('pattern', '') else 'technical-T08'
    raise ValueError('unhandled private-plan schema shape')


def selected_runner():
    raw = RUNNER.read_bytes()
    need(sha(raw) == RUNNER_SHA, 'selected positive constructor changed')
    module = types.ModuleType('_cal_t08_builder_selected_constructor')
    module.__file__ = str(RUNNER)
    exec(compile(raw, module.__file__, 'exec'), module.__dict__)
    module.API = API
    module.SOURCE_SHA = SOURCE_SHA
    module.PROFILE_SHA = PROFILE_SHA
    module.BRIDGE = API + '/protected_bridge.py'
    module.CONTENT = CONTENT
    module.CONTENT_SHA = CONTENT_SHA
    return module


def run(*, full):
    started = time.monotonic()
    R = selected_runner()
    p, g, tests, bridge_module, content = R.modules()
    source_path = API + '/source-manifest.json'
    profile_path = API + '/contract-profile.json'
    source_raw = R.selected(source_path, SOURCE_SHA)
    profile_raw = R.selected(profile_path, PROFILE_SHA)
    # The frozen positive selector constructor uses this public path constant;
    # the recut port verifies the same path from the signed Source at runtime.
    content.ACCOUNT_PATH = API + '/INPUT-ACCOUNTING.json'
    source_binding = {'ref': source_path, 'sha256': SOURCE_SHA}
    profile_binding = {'ref': profile_path, 'sha256': PROFILE_SHA}
    cut = {'branch_ref': 'technical:T08-current-mixed/branch',
           'store_ref': 'technical:T08-current-mixed/store', 'commit_sequence': 0,
           'commit_sha256': sha(b'T08-current-mixed-technical-branch'),
           'source_profile_sha256': PROFILE_SHA, 'streams': []}
    with tempfile.TemporaryDirectory(prefix='cal-t08-mixed-builder-', dir='/tmp') as location:
        parent = Path(location)
        parent.chmod(0o700)
        template = parent / 'template'
        template.mkdir(mode=0o700)
        private = parent / 'private'
        private.mkdir(mode=0o700)
        policy, eligibility, physical = R.policy_material(
            tests, template, source_binding, profile_binding, cut)
        _, _, selector, roots, policy_raw, eligibility_raw, _ = R.make_reader(
            p, source_raw, profile_raw, source_binding, profile_binding,
            cut, policy, eligibility, physical, private)
        semantic = {'anchor': {
            'policy_binding': {'ref': 'technical:T08-mixed/policy', 'sha256': sha(policy_raw)},
            'eligibility_binding': {'ref': 'technical:T08-mixed/eligibility',
                                    'sha256': sha(eligibility_raw)},
            'source_binding': source_binding, 'profile_binding': profile_binding,
            'source_cut': cut, 'allowed_states': ['candidate-current']},
            'policy_file_id': 'policy', 'declared_edges': [R.EDGE],
            'root_refs': [R.EDGE['source']]}
        reader, anchor, scope_binding, scope, selector = R.full_content_reader(
            p, content, None, selector, roots, semantic,
            source_binding, profile_binding, cut, private)
        guard_path = API + '/guard.py'
        source = p.parse(source_raw)
        guard_digest = next(row['sha256'] for row in source['files'] if row['path'] == guard_path)
        guard_raw = R.selected(guard_path, guard_digest)
        guard = types.ModuleType('_cal_t08_recut_source_guard')
        guard.__file__ = str(ROOT / guard_path)
        exec(compile(guard_raw, guard.__file__, 'exec'), guard.__dict__)
        guard.verify(SOURCE_SHA)
        selection = {
            'custody_anchor': {key: getattr(anchor, key) for key in bridge_module.ANCHOR_FIELDS},
            'control_roots': list(roots.values()), 'binding_routes': [],
            'semantic_selection': semantic,
            'readiness_version': bridge_module.REVIEW_VERSION,
            'observation_schema_binding': {
                'path': API + '/typed-review-observation.schema.json',
                'sha256': sha((ROOT / API / 'typed-review-observation.schema.json').read_bytes())},
            'historical_original_proof': {
                'status': 'REFUSED', 'unavailable_binding': {
                    'path': 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/accounting-0001/unavailable-original-inputs.json',
                    'sha256': '4408c5433d41119a92660f86f856d6847be24171ddb1dab368e22c63ee294e7a'},
                'unavailable_count': 25},
            'historical_content': {'scope_binding': scope_binding,
                                   'scope_file_id': scope['scope_file_id']}}
        package = '_cal_t08_mixed_current_api_0001'
        need(package in sys.modules, 'selected recut API package missing')
        completion = importlib.import_module(package + '.completion_bridges')
        release = importlib.import_module(package + '.installation_release')
        schema_raw = R.selected(API + '/host-bridge.schema.json', SCHEMA_SHA)
        schema = json.loads(schema_raw)
        bindings = schema['properties']['module_bindings']['const']
        need(bindings['private_content'] == {'path': CONTENT, 'sha256': CONTENT_SHA},
             'recut bridge schema does not select current content')
        environment = types.ModuleType('_cal_t08_unexecuted_environment')
        environment.__file__ = str(ROOT / bindings['environment']['path'])
        dependencies = types.ModuleType('_cal_t08_unexecuted_dependencies')
        dependencies.__file__ = str(ROOT / bindings['dependencies']['path'])
        modules = {'protected_inputs': p, 'semantic_graph': g,
                   'private_content': content, 'environment': environment,
                   'dependencies': dependencies}
        descriptor = {'schema_version': 'lab-installation-release-host-bridge/v3-candidate',
                      'module_bindings': bindings, 'protected_inputs': selection,
                      'composite_environment': None, 'native_launch_binding': None,
                      'authority_effect': 'none'}
        descriptor_raw = p.canonical(descriptor)
        descriptor_binding = {'ref': 'candidate:T08-mixed/host-bridge',
                              'sha256': sha(descriptor_raw)}
        try:
            selected = completion.CompletionBridge(descriptor_raw, descriptor_binding,
                                                   ROOT, modules, None)
        except Exception as error:
            if type(error).__name__ == 'ValidationError':
                issues = sorted({('/'.join(map(str, item.absolute_path)), item.validator)
                                 for item in getattr(error, 'context', [])})
                raise ValueError('recut host schema rejected at ' + repr(issues[:12])) from None
            raise
        plan_schema = p.parse(R.selected(API + '/private-plan-v2.schema.json',
                            next(row['sha256'] for row in source['files']
                                 if row['path'] == API + '/private-plan-v2.schema.json')))
        plan = sample(plan_schema)
        plan.update(schema_version='lab-installation-release-plan/v2-candidate',
                    principal_ref=anchor.principal_ref, source_cut=cut,
                    bridge_binding=descriptor_binding, authority_effect='none',
                    actual_owner_outcome=None)
        plan_raw = p.canonical(plan)
        plan_binding = {'ref': 'candidate:T08-mixed/private-plan',
                        'sha256': sha(plan_raw)}
        materials = {plan_binding['ref']: plan_raw,
                     descriptor_binding['ref']: descriptor_raw}
        calls = {'vault_guard': 0, 'schemas_guard': 0, 'handlers_current': 0}
        def vault_guard():
            calls['vault_guard'] += 1
        def schema_guard():
            calls['schemas_guard'] += 1
            guard.verify(SOURCE_SHA)
        def current():
            calls['handlers_current'] += 1
            guard.verify(SOURCE_SHA)
            return True
        def material(binding):
            raw = materials[binding['ref']]
            need(sha(raw) == binding['sha256'], 'private selected material changed')
            return raw
        host = types.SimpleNamespace(
            vault=types.SimpleNamespace(guard=vault_guard, material=material),
            channel=types.SimpleNamespace(
                context={'principal_ref': anchor.principal_ref},
                policy_guard=lambda: {'installation_release_control':
                                      {'plan_binding': plan_binding}}),
            schemas=types.SimpleNamespace(
                profile_binding=profile_binding, profile_path=ROOT / profile_path,
                guard=schema_guard),
            handlers=types.SimpleNamespace(current=current),
            completion_bridge=selected)
        builder = release.InstallationRelease(
            host, 'release.prepare', datetime.now(timezone.utc) + timedelta(minutes=30))
        need(type(builder.completion) is completion.BoundCompletionBridge and
             builder.completion.protected.anchor.source_binding == source_binding and
             builder.completion.protected.content_module is content,
             'genuine InstallationRelease/CompletionBridge binding differs')
        bad_plan = dict(builder.plan, source_cut={'unexpected': True})
        builder.plan = bad_plan
        try:
            try:
                builder.completion.protected.bind(builder)
            except ValueError as error:
                need(str(error) == 'trusted host principal/profile/cut/operation differs',
                     'changed builder cut caused unrelated refusal: ' + str(error))
                wrong_cut_refused = True
            else:
                raise ValueError('changed builder source cut accepted')
        finally:
            builder.plan = plan
        need(wrong_cut_refused, 'changed builder cut did not refuse')
        result = None
        if full:
            with builder.completion.protected.verified_boundary(semantics=True) as (bound_reader, historical):
                need(bound_reader is not None and historical['content_identity_closure'] == 'PASS'
                     and historical['original_locator_physical_closure'] == 'REFUSED'
                     and historical['declared_unique_inputs'] == 24503,
                     'actual bound mixed boundary differs')
            result = historical
        guard.verify(SOURCE_SHA)
        need(sha((ROOT / CONTENT).read_bytes()) == CONTENT_SHA and
             sha(RUNNER.read_bytes()) == RUNNER_SHA,
             'technical source code changed during bound run')
        return {'schema_version': 'lab-T08-current-mixed-builder-bind/v2-candidate',
                'result': 'PASS-full-bound-builder' if full else 'PASS-builder-constructor-only',
                'source_sha256': SOURCE_SHA, 'profile_sha256': PROFILE_SHA,
                'host_schema_sha256': SCHEMA_SHA, 'current_content_sha256': CONTENT_SHA,
                'source_rows': len(source['files']), 'profile_rows': len(p.parse(profile_raw)['files']),
                'selected_files': len(reader.files), 'historical_coverage_rows': len(scope['coverage']),
                'original_installation_release_class_constructed': True,
                'completion_bridge_class_constructed': True,
                'protected_bridge_bound_to_builder': True,
                'wrong_builder_cut_refused': wrong_cut_refused,
                'full_bound_reader_entry_exit_verified': full,
                'historical_content_verified': full,
                'historical_content': result,
                'actual_semantic_graph_executed': full,
                'real_service_or_authenticated_channel_used': False,
                'environment_dependencies_executed': False,
                'installation_effect_requested': False,
                'source_guard_calls': calls,
                'original_locator_physical_closure': 'REFUSED',
                'original_full_proof_status': 'REFUSED',
                'private_body_exported': False,
                'authority_effect': 'none', 'T08_complete': False,
                'elapsed_seconds': round(time.monotonic() - started, 3)}


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) == 2 else None
    need(mode in ('--preflight', '--full'), 'bounded builder mode required')
    print(json.dumps(run(full=mode == '--full'), sort_keys=True, indent=2, allow_nan=False))
