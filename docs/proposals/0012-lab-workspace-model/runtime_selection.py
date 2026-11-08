#!/usr/bin/env python3
"""Pure candidate runtime/profile selection. Never installs or invokes a runtime.

Matching context and compatibility here are configuration checks, not native
authentication or authorization. A real host must enforce its own operation gate.
"""
import copy
import json
from pathlib import Path

import jsonschema

HERE = Path(__file__).resolve().parent


class SelectionRefusal(ValueError):
    pass


def require(condition, code):
    if not condition:
        raise SelectionRefusal(code)


def validate_selection(selection):
    schema = json.loads((HERE / 'model/runtime-selection.schema.json').read_text())
    require(jsonschema.Draft202012Validator(schema).is_valid(selection), 'runtime-selection-schema')


def resolve(workspace, selection, policy, model_version, context, catalog):
    """Resolve references only; the caller supplies its explicitly selected catalog."""
    validate_selection(selection)
    require(policy['default_execution_mode'] == 'shared' and policy['default_behavior_mode'] == 'inherited',
        'shared-default-required')
    require(not policy['per_workspace_runtime_required'] and not policy['copy_runtime_required'], 'runtime-replication-required')
    for key in ('workspace_ref', 'project_ref', 'scope_ref'):
        require(context.get(key) == workspace[key], 'context-' + key + '-mismatch')
    require(context.get('workspace_revision') == workspace['revision'], 'context-revision-mismatch')
    require(selection['workspace_ref'] == workspace['workspace_ref'] and
        selection['workspace_revision_ref'] == workspace['workspace_ref'] + '@' + workspace['revision'], 'selection-workspace-mismatch')
    runtime_ref = selection['runtime_ref']
    if selection['mode'] == 'shared' and runtime_ref is None:
        runtime_ref = catalog.get('default_shared_runtime_ref')
    require(runtime_ref is not None, 'runtime-target-unselected')
    target = catalog.get('runtimes', {}).get(runtime_ref)
    require(target is not None, 'runtime-target-unavailable')
    require(target['mode'] == selection['mode'], 'runtime-placement-mismatch')
    require(model_version in target['supported_model_versions'], 'runtime-model-incompatible')
    require(workspace['workspace_ref'] in target['supported_workspace_refs'], 'runtime-workspace-unsupported')
    if selection['mode'] == 'dedicated':
        require(target.get('bound_workspace_ref') == workspace['workspace_ref'], 'dedicated-workspace-mismatch')
    overrides = {}
    if selection['behavior'] == 'inherited':
        require(selection['specialization_ref'] is None, 'unexpected-specialization')
    else:
        require(selection['specialization_ref'] is not None, 'specialization-unselected')
        specialized = catalog.get('specializations', {}).get(selection['specialization_ref'])
        require(specialized is not None, 'specialization-unavailable')
        require(specialized['workspace_ref'] == workspace['workspace_ref'], 'specialization-workspace-mismatch')
        require(specialized['parent_model_version_ref'] == model_version, 'specialization-model-incompatible')
        overrides = specialized['configuration_overrides']
        require(set(overrides) <= {'context_budget_tokens', 'operator_note'}, 'specialization-outside-configuration')
        if 'context_budget_tokens' in overrides:
            require(type(overrides['context_budget_tokens']) is int and 0 < overrides['context_budget_tokens'] <= 32768,
                'specialization-budget')
        if 'operator_note' in overrides:
            require(isinstance(overrides['operator_note'], str) and len(overrides['operator_note']) <= 160,
                'specialization-note')
    return {'runtime_ref': runtime_ref, 'placement': selection['mode'], 'behavior': selection['behavior'],
        'workspace_ref': workspace['workspace_ref'], 'project_ref': workspace['project_ref'],
        'scope_ref': workspace['scope_ref'], 'workspace_revision': workspace['revision'],
        'state_namespace_ref': workspace['workspace_ref'], 'model_version_ref': model_version,
        'configuration_overrides': copy.deepcopy(overrides), 'operational_authorization': 'not-evaluated',
        'runtime_created': False, 'runtime_code_copied': False, 'authority_effect': 'none'}


def check_model(bundle):
    policy, selected = bundle['runtime_policy'], bundle['runtime_selection']
    validate_selection(selected)
    require(policy['default_execution_mode'] == 'shared' and policy['default_behavior_mode'] == 'inherited', 'shared-default-required')
    require(policy['specialization_requires_dedicated_runtime'] is False and
        policy['per_workspace_runtime_required'] is False and policy['copy_runtime_required'] is False, 'runtime-replication-required')
    workspace = bundle['workspace']
    require(selected['workspace_ref'] == workspace['workspace_ref'] and
        selected['workspace_revision_ref'] == workspace['workspace_ref'] + '@' + workspace['revision'], 'selection-workspace-mismatch')
    require(selected['mode'] == 'shared' and selected['behavior'] == 'inherited' and
        selected['runtime_ref'] is None, 'candidate-default-selection')
    require(selected['runtime_provisioned'] is False and selected['copy_runtime'] is False and
        selected['authority_grants'] == [], 'candidate-runtime-effect')


def scenario(bundle):
    check_model(bundle)
    first = bundle['workspace']
    second = {'workspace_ref': 'workspace:fixture:second', 'project_ref': 'project:fixture:second',
        'scope_ref': 'scope:fixture:second', 'revision': '1.0.0-fixture.1'}
    version = bundle['model']['payload']['version_ref']
    policy = bundle['runtime_policy']
    selected = bundle['runtime_selection']
    other = copy.deepcopy(selected)
    other['workspace_ref'] = second['workspace_ref']
    other['workspace_revision_ref'] = second['workspace_ref'] + '@' + second['revision']
    central, dedicated = 'fixture:runtime:shared-central', 'fixture:runtime:dedicated-craft'
    catalog = {'default_shared_runtime_ref': central, 'runtimes': {
        central: {'mode': 'shared', 'supported_model_versions': [version],
            'supported_workspace_refs': [first['workspace_ref'], second['workspace_ref']]},
        dedicated: {'mode': 'dedicated', 'supported_model_versions': [version],
            'supported_workspace_refs': [first['workspace_ref']], 'bound_workspace_ref': first['workspace_ref']}},
        'specializations': {'fixture:profile:craft': {'workspace_ref': first['workspace_ref'],
            'parent_model_version_ref': version, 'configuration_overrides': {'context_budget_tokens': 4096}}}}
    def ctx(workspace):
        return {key: workspace[key] for key in ('workspace_ref', 'project_ref', 'scope_ref')} | {'workspace_revision': workspace['revision']}
    a = resolve(first, selected, policy, version, ctx(first), catalog)
    b = resolve(second, other, policy, version, ctx(second), catalog)
    require(a['runtime_ref'] == b['runtime_ref'] and a['state_namespace_ref'] != b['state_namespace_ref'], 'shared-scopes-not-distinct')
    specialized = copy.deepcopy(selected)
    specialized.update(behavior='specialized', specialization_ref='fixture:profile:craft',
        selection_state='proposed-explicit-not-a-deployment')
    c = resolve(first, specialized, policy, version, ctx(first), catalog)
    require(c['runtime_ref'] == central and c['configuration_overrides']['context_budget_tokens'] == 4096,
        'specialization-forced-dedicated')
    isolated = copy.deepcopy(selected)
    isolated.update(mode='dedicated', runtime_ref=dedicated, selection_state='proposed-explicit-not-a-deployment')
    d = resolve(first, isolated, policy, version, ctx(first), catalog)
    require(d['runtime_ref'] == dedicated and d['behavior'] == 'inherited', 'placement-forced-specialization')
    negative = []
    def rejects(name, selected_input, context_input, catalog_input, code):
        try:
            resolve(first, selected_input, policy, version, context_input, catalog_input)
        except SelectionRefusal as exc:
            require(str(exc) == code, 'wrong-refusal:' + name + ':' + str(exc))
            negative.append({'name': name, 'refusal': code, 'result': 'pass'})
        else:
            raise SelectionRefusal('accepted-invalid:' + name)
    for field in ('workspace_ref', 'project_ref', 'scope_ref'):
        bad = ctx(first); bad[field] = 'fixture:foreign'
        rejects('wrong ' + field, selected, bad, catalog, 'context-' + field + '-mismatch')
    bad = ctx(first); bad['workspace_revision'] = 'stale'
    rejects('stale workspace context', selected, bad, catalog, 'context-revision-mismatch')
    bad = copy.deepcopy(selected); bad['mode'] = 'dedicated'
    rejects('implicit dedicated fallback', bad, ctx(first), catalog, 'runtime-target-unselected')
    bad_catalog = copy.deepcopy(catalog); bad_catalog['default_shared_runtime_ref'] = None
    rejects('missing actual target', selected, ctx(first), bad_catalog, 'runtime-target-unselected')
    bad_catalog = copy.deepcopy(catalog); bad_catalog['runtimes'][dedicated]['bound_workspace_ref'] = second['workspace_ref']
    rejects('foreign dedicated scope', isolated, ctx(first), bad_catalog, 'dedicated-workspace-mismatch')
    bad = copy.deepcopy(specialized); bad['specialization_ref'] = None
    rejects('unselected specialization', bad, ctx(first), catalog, 'specialization-unselected')
    bad_catalog = copy.deepcopy(catalog); bad_catalog['specializations']['fixture:profile:craft']['workspace_ref'] = second['workspace_ref']
    rejects('foreign specialization', specialized, ctx(first), bad_catalog, 'specialization-workspace-mismatch')
    bad_catalog = copy.deepcopy(catalog); bad_catalog['specializations']['fixture:profile:craft']['configuration_overrides'] = {'authority_grants': ['all']}
    rejects('semantic/authority override', specialized, ctx(first), bad_catalog, 'specialization-outside-configuration')
    bad_catalog = copy.deepcopy(catalog); bad_catalog['runtimes'][central]['supported_model_versions'] = ['unselected-version']
    rejects('incompatible runtime model', selected, ctx(first), bad_catalog, 'runtime-model-incompatible')
    return {'scope': 'pure configuration/reference resolver with synthetic catalog only',
        'shared_default_workspaces': 2, 'shared_default_targets': 1,
        'specialized_behavior_on_shared_target': True, 'dedicated_target_is_optional': True,
        'distinct_workspace_contexts': True, 'negative_cases': negative,
        'runtime_installations_created': 0, 'runtime_code_copies': 0, 'native_operations_executed': 0,
        'native_authorization_qualified': False, 'authority_effect': 'none'}
