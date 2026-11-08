#!/usr/bin/env python3
"""Check candidate artifacts and exercise isolated profile creation/succession.

No native Craft runtime, installer, authority store or source migration is run.
Only --write-report writes inside this candidate's receipts directory.
"""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlsplit

import jsonschema
import runtime_selection

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
AREAS = ('product', 'project', 'work', 'authority', 'ontology', 'architecture', 'implementation', 'docs')
CONTRACT_REGISTRY = 'authority/admissions/project-state-bootstrap/v1/registries/artifact-type-registry.json'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False) + '\n').encode()


class Refusal(ValueError):
    pass


def need(condition, code):
    if not condition:
        raise Refusal(code)


def safe_relative(value):
    path = PurePosixPath(value)
    need(bool(value) and not path.is_absolute() and '..' not in path.parts and '\\' not in value,
        'unsafe-path')
    return path


def root_read(relative):
    path = ROOT / safe_relative(relative)
    need(path.resolve().is_relative_to(ROOT), 'source-escapes-repository')
    return path.read_bytes()


def load_bundle():
    def read(path):
        return json.loads((HERE / path).read_text())
    return {'definition': read('definition/lab-workspace/definition.json'),
        'model': read('model/model.json'), 'workspace': read('craft/workspace.json'),
        'binding': read('craft/binding.json'), 'reconciliation': read('craft/reconciliation.json'),
        'selection': read('craft/selection.json'), 'contracts': read('contracts.json'),
        'owners': read('owners.json'), 'profile': read('model/operating-profile.json'),
        'decision': read('review/decision.json'), 'runtime_policy': read('model/runtime-policy.json'),
        'runtime_selection': read('craft/runtime-selection.json')}


def checked_contracts(bundle, reader=root_read):
    registry = json.loads(reader(CONTRACT_REGISTRY))
    selected = {x['artifact_type_ref']: x for x in registry['admitted_contracts']
        if x['lifecycle_state'] == 'admitted-current'}
    schemas = {}
    for pinned in bundle['contracts']['contracts']:
        ref = pinned['artifact_type_ref']
        need(ref in selected, 'contract-not-current')
        entry = selected[ref]
        for key in ('schema_path', 'schema_sha256', 'artifact_path', 'artifact_sha256'):
            need(entry[key] == pinned[key], 'contract-selection-drift')
        need(digest(reader(entry['schema_path'])) == entry['schema_sha256'], 'contract-schema-drift')
        need(digest(reader(entry['artifact_path'])) == entry['artifact_sha256'], 'contract-descriptor-drift')
        schema = json.loads(reader(entry['schema_path']))
        jsonschema.Draft202012Validator.check_schema(schema)
        schemas[ref] = schema
    return schemas


def check_sources(bundle, reader=root_read):
    selection = bundle['selection']
    need(selection['scope'] == 'bounded-current-workspace-profile', 'source-scope-inflation')
    need(selection['full_craft_source_closure'] is False, 'source-closure-not-established')
    need(selection['copy_shared_runtimes'] is False, 'shared-runtime-copy')
    rows = selection['files']
    need(rows and len({r['path'] for r in rows}) == len(rows), 'duplicate-or-empty-source-selection')
    need(set(r['area'] for r in rows if r['area'] in AREAS) == set(AREAS), 'source-area-missing')
    for row in rows:
        raw = reader(row['path'])
        need(digest(raw) == row['sha256'] and len(raw) == row['byte_length'], 'selected-source-drift')
    pinned = {r['path']: r for r in rows}
    reconciliation = bundle['reconciliation']
    need(reconciliation['effect'] == 'proposed-primary-selection-only', 'reconciliation-effect')
    need(reconciliation['global_consumer_cutover'] is False, 'global-cutover')
    project = reconciliation['project']
    need(project['selected_path'] == 'craft/project/project.json', 'unexpected-project-primary')
    a, b = reader(project['selected_path']), reader(project['retained_duplicate'])
    need(a == b, 'project-duplicate-diverged')
    project_record = json.loads(a)
    need(project_record['project_id'] == bundle['workspace']['project_ref'], 'project-reference-mismatch')
    need(project['artifact_type_ref'] == 'cal.artifact-type.project-identity/v1', 'resolved-duplicate-project-carrier')
    product = reconciliation['product']
    current, old = json.loads(reader(product['selected_path'])), json.loads(reader(product['retained_predecessor']))
    need(current['product_id'] == old['product_id'] == bundle['workspace']['product_ref'], 'product-lineage-mismatch')
    need(current['version'] == product['selected_version'] and current['version'] != old['version'], 'product-version-selection')
    need(product['standing'] == 'candidate-unadmitted' and current['status'] == product['standing'], 'candidate-product-promotion')
    need(product['selection_effect'] == 'profile-only-no-admission-or-supersession', 'product-selection-effect')
    for path in (project['selected_path'], project['retained_duplicate'], product['selected_path'], product['retained_predecessor']):
        need(path in pinned, 'reconciliation-source-unpinned')
    goals = json.loads(reader('craft/project/goals.json'))['goals']
    linked = {r['goal_ref']: r['membership'] for r in goals}
    for goal in bundle['workspace']['goals']:
        need(goal['membership'] == linked.get(goal['goal_ref']), 'goal-membership-inflation')
    need({g['goal_ref'] for g in bundle['workspace']['goals']} == set(linked), 'goal-selection-incomplete')


def check_model(bundle):
    model, workspace, binding = bundle['model'], bundle['workspace'], bundle['binding']
    payload = bundle['profile']
    need(payload['version_ref'] == model['payload']['version_ref'], 'model-profile-version')
    root_ref = HERE.relative_to(ROOT).as_posix()
    need(model['payload']['contract_ref'] == root_ref + '/model/operating-profile.json', 'model-profile-contract')
    runtime_selection.check_model(bundle)
    need(payload['runtime_policy_ref'] == root_ref + '/model/runtime-policy.json', 'runtime-policy-reference')
    need(workspace['local_configuration']['runtime_selection_ref'] == root_ref + '/craft/runtime-selection.json', 'runtime-selection-reference')
    rules = json.loads((HERE / 'model/rules.json').read_text())
    need(model['payload']['rule_refs'] == [root_ref + '/model/rules.json#/' + key for key in rules], 'model-rule-references')
    need(model['payload']['extension_policy_ref'] == root_ref + '/model/operating-profile.json#/allowed_local_configuration', 'extension-policy-reference')
    need(payload['model_kind'] == 'lab-workspace-operating-model', 'wrong-model-kind')
    need(payload['definition_ref'] == bundle['definition']['definition_id'] + '@' + bundle['definition']['version'], 'workspace-definition-binding')
    need(set(payload['areas']) == set(AREAS) and len(payload['areas']) == len(AREAS), 'model-area-set')
    need(set(workspace['areas']) == set(AREAS), 'workspace-area-set')
    need(workspace['project_ref'] != workspace['product_ref'], 'identity-collapse')
    need(workspace['adoption']['model_ref'] == model['node_id'], 'parent-model-reference')
    need(workspace['adoption']['model_version_ref'] == payload['version_ref'], 'parent-version-mismatch')
    need(binding['parent_model_ref'] == model['node_id'] and binding['parent_model_version_ref'] == payload['version_ref'], 'binding-parent-mismatch')
    need(binding['instance_ref'] == workspace['workspace_ref'] + '@' + workspace['revision'], 'binding-instance-revision')
    need(binding['node_id'] == workspace['adoption']['binding_ref'], 'binding-reference')
    need(binding['binding_state'] == 'proposed' and workspace['actual_adoption_outcome'] is None, 'adoption-not-authorized')
    need(binding['parent_authority_scope'] != binding['instance_authority_scope'], 'authority-collapse')
    need(binding['parent_authority_scope'] == model['scope_ref'] and
        binding['instance_authority_scope'] == workspace['scope_ref'], 'authority-scope-reference')
    need(binding['parent_owner_route'] == model['owner_ref'], 'parent-owner-mismatch')
    need(binding['instance_owner_route'] == workspace['owner_route'], 'instance-owner-mismatch')
    need(binding['local_override_refs'] == [], 'unreviewed-override')
    inherited = {root_ref + '/model/workspace.schema.json', *payload['inherited_definition_refs']}
    need(set(binding['inherited_contract_refs']) == inherited, 'inherited-contract-closure')
    need(workspace['shared_runtime_policy'] == 'reference-only-no-copy-no-shared-writes', 'shared-runtime-policy')
    need(workspace['current_location'] == 'craft' and workspace['proposed_location'] == 'workspaces/craft', 'location-profile')
    allowed = set(payload['allowed_local_configuration'])
    need(set(workspace['local_configuration']) <= allowed, 'configuration-outside-extension-scope')
    need(set(binding['extension_scope']) == allowed, 'binding-extension-scope')
    need(workspace['local_configuration']['context_budget_tokens'] > 0, 'invalid-context-budget')
    need(workspace['recursion']['max_depth'] == 1 and bool(workspace['recursion']['stop']), 'unbounded-recursion')
    need(payload['prohibited_inferences'] == ['authority-from-location', 'identity-from-folder',
        'goal-workspace-recursion', 'silent-source-repin', 'global-runtime-cutover'], 'missing-inference-guard')
    expected_relation = {'relation_kind_ref': 'relation.declares-effect-on', 'direction': 'target',
        'counterpart_kind': 'decision', 'counterpart_ref': bundle['decision']['node_id']}
    need(model['relation_refs'] == [expected_relation] and workspace['global_relation_effects'] == [], 'unqualified-global-relation')
    need(bundle['decision']['payload']['subject_refs'] == [model['node_id']], 'authoring-decision-subject')
    need(bundle['decision']['lifecycle_state'] == 'candidate' and bundle['decision']['authority_effect'] == 'none', 'authoring-decision-inflation')
    need(bundle['decision']['scope_ref'] == 'scope:workspace-package-authoring-only' and
        bundle['decision']['payload']['declared_effect_refs'] == ['proposal-effect:lab-workspace:first-package:authoring'],
        'authoring-decision-effect-scope')
    owners = bundle['owners']
    need(all(r['assignment_state'] == 'route-only-not-an-activated-assignment' for r in owners['routes']), 'invented-owner-assignment')
    need(set((model['owner_ref'], workspace['owner_route'], bundle['definition']['semantic_owner_ref'])) <=
        {r['ref'] for r in owners['routes']}, 'owner-route-not-declared')
    need(workspace['workspace_ref'] != workspace['project_ref'], 'workspace-project-collapse')
    expected_homes = {HERE.relative_to(ROOT).as_posix() + '/craft/homes/' + area + '/package.json' for area in AREAS}
    need(set(workspace['canonical_home_refs']) == expected_homes, 'canonical-home-selection')
    for area in AREAS:
        data = workspace['areas'][area]
        need(data['source_home'] == 'craft/' + area, 'area-source-selection')
        selection_path = ROOT / safe_relative(data['selection_home']) / 'selection.json'
        selected = json.loads(selection_path.read_text())
        need(selected['area'] == area and selected['source_relocation_executed'] is False, 'area-selection-scope')
        need(selected['lifecycle_owner_route'] == data['owner_route'], 'selection-owner-route')
        need(selected['source_refs'] == [r['path'] for r in bundle['selection']['files'] if r['area'] == area],
            'area-selection-reference-closure')


def validate_bundle(bundle, reader=root_read):
    schemas = checked_contracts(bundle, reader)
    for key, ref in [('definition', 'cal.artifact-type.definition/v2'),
        ('model', 'cal.artifact-type.governed-model/v1'), ('binding', 'cal.artifact-type.model-instance-binding/v1'),
        ('decision', 'cal.artifact-type.decision/v1')]:
        try:
            jsonschema.Draft202012Validator(schemas[ref]).validate(bundle[key])
        except jsonschema.ValidationError as exc:
            raise Refusal('native-schema:' + key) from exc
    local = json.loads((HERE / 'model/workspace.schema.json').read_text())
    try:
        jsonschema.Draft202012Validator(local).validate(bundle['workspace'])
    except jsonschema.ValidationError as exc:
        raise Refusal('workspace-profile-schema') from exc
    definition = bundle['definition']
    need(definition['schema_digest'] == digest(reader('authority/artifact-types/definition/v2/schema.json')), 'definition-schema-pin')
    need(definition['source_direction']['generator_sha256'] == digest(reader('authority/artifact-types/definition/v2/generator.py')), 'definition-generator-pin')
    for ref in definition['source_refs']:
        need(digest(reader(ref['source_ref'])) == ref['content_sha256'], 'definition-source-pin')
    check_model(bundle)
    check_sources(bundle, reader)
    try:
        jsonschema.Draft202012Validator(schemas['cal.artifact-type.project-identity/v1']).validate(
            json.loads(reader(bundle['reconciliation']['project']['selected_path'])))
        for goal in bundle['workspace']['goals']:
            jsonschema.Draft202012Validator(schemas['cal.artifact-type.goal/v1']).validate(json.loads(reader(goal['path'])))
    except jsonschema.ValidationError as exc:
        raise Refusal('source-identity-schema') from exc
    return schemas


def manifest_errors(data, root, schema):
    errors = []
    try:
        jsonschema.Draft202012Validator(schema).validate(data)
    except jsonschema.ValidationError:
        return ['package-schema']
    if data['package_root'] != root.relative_to(ROOT).as_posix(): errors.append('manifest-root')
    entries = data['surface_entries']
    if len({r['path'] for r in entries}) != len(entries): errors.append('duplicate-surface')
    declared = set()
    for row in entries:
        safe_relative(row['path'])
        target = root / row['path']
        planned_report = target == HERE / 'receipts/validation.json' and row['role'] == 'evidence'
        if not target.exists() and row['role'] != 'transient-state' and not planned_report:
            errors.append('missing-surface')
        if target.is_file(): declared.add(target.relative_to(root).as_posix())
    nested = []
    for child in data['nested_packages']:
        target = ROOT / safe_relative(child['manifest_ref'])
        if not target.is_file(): errors.append('missing-nested-manifest'); continue
        other = json.loads(target.read_text())
        if child['package_ref'] != other['package_id']: errors.append('nested-package-reference')
        if child['relation_kind'] != 'local:package-home:contains': errors.append('nested-relation-scope')
        if not target.parent.is_relative_to(root) or target.parent == root: errors.append('nested-home-location')
        nested.append(target.parent)
    for path in root.rglob('*'):
        if not path.is_file() or '__pycache__' in path.parts: continue
        if any(path.is_relative_to(n) for n in nested): continue
        if path.relative_to(root).as_posix() not in declared: errors.append('unclassified-owned-file')
    return errors


def check_packages(schemas):
    manifests = sorted(HERE.rglob('package.json'))
    for path in manifests:
        errors = manifest_errors(json.loads(path.read_text()), path.parent,
            schemas['cal.artifact-type.canonical-package-manifest/v1'])
        need(not errors, 'manifest:' + str(path.relative_to(HERE)) + ':' + ','.join(errors))
        data = json.loads(path.read_text())
        for row in data['surface_entries']:
            if row['role'] == 'canonical-instance':
                need(row['artifact_type_ref'] in schemas, 'unknown-canonical-carrier')
                try:
                    jsonschema.Draft202012Validator(schemas[row['artifact_type_ref']]).validate(
                        json.loads((path.parent / row['path']).read_text()))
                except jsonschema.ValidationError as exc:
                    raise Refusal('canonical-carrier-schema') from exc
    return len(manifests)


def check_navigation():
    count = 0
    for doc in HERE.rglob('*.md'):
        count += 1
        for raw in re.findall(r'\[[^\]]*\]\(([^)]+)\)', doc.read_text()):
            value = urlsplit(raw.strip('<>'))
            if value.scheme or raw.startswith('//'): continue
            target = (doc.parent / unquote(value.path)).resolve() if value.path else doc
            need(target.exists() or target == HERE / 'receipts/validation.json',
                'broken-link:' + str(doc.relative_to(HERE)) + ':' + raw)
    return count


def check_projections():
    namespace = {'__name__': 'candidate_projection', '__file__': str(HERE / 'render.py')}
    exec(compile((HERE / 'render.py').read_text(), str(HERE / 'render.py'), 'exec'), namespace)
    for path, text in namespace['projections']():
        need(path.exists() and path.read_text() == text, 'projection-drift:' + str(path.relative_to(HERE)))


def transition(before, after, plan, pending=False):
    need(not pending, 'reconciliation-required')
    need(plan['before_sha256'] == digest(encoded(before)), 'stale-preimage')
    for key in ('workspace_ref', 'project_ref', 'product_ref', 'goals', 'areas', 'source_selection_ref',
        'shared_runtime_policy', 'owner_route', 'scope_ref', 'canonical_home_refs', 'runtime_installation_refs',
        'authority_grants', 'global_relation_effects', 'recursion'):
        need(before[key] == after[key], 'identity-or-history-change')
    need(before['revision'] != after['revision'], 'successor-revision-required')
    need(before['adoption']['binding_ref'] != after['adoption']['binding_ref'], 'successor-binding-required')
    need(after['adoption']['model_version_ref'] == plan['after_model_version_ref'], 'transition-parent-pin')
    need(set(after['local_configuration']) <= {'context_budget_tokens', 'operator_note', 'runtime_selection_ref'}, 'transition-override')
    need(after['actual_adoption_outcome'] is None and after['authority_effect'] == 'none', 'transition-authority-inflation')


def successor_fixture(bundle):
    after = copy.deepcopy(bundle)
    version = 'model:lab-workspace:operating-model@1.1.0-fixture'
    after['model']['payload']['version_ref'] = version
    after['profile']['version_ref'] = version
    after['workspace']['revision'] = '1.0.0-fixture.2'
    after['runtime_selection']['workspace_revision_ref'] = after['workspace']['workspace_ref'] + '@' + after['workspace']['revision']
    after['workspace']['adoption']['model_version_ref'] = version
    after['workspace']['adoption']['binding_ref'] += ':fixture-successor'
    after['workspace']['local_configuration']['operator_note'] = 'Fixture successor for profile validation only.'
    after['binding']['node_id'] = after['workspace']['adoption']['binding_ref']
    after['binding']['parent_model_version_ref'] = version
    after['binding']['instance_ref'] = after['workspace']['workspace_ref'] + '@' + after['workspace']['revision']
    plan = {'before_sha256': digest(encoded(bundle['workspace'])), 'after_model_version_ref': version,
        'predecessor_binding_ref': bundle['binding']['node_id'], 'after_binding_ref': after['binding']['node_id'],
        'authority_effect': 'none', 'scope': 'isolated-candidate-profile-fixture'}
    return after, plan


def scenario(bundle):
    after, plan = successor_fixture(bundle)
    validate_bundle(after)
    transition(bundle['workspace'], after['workspace'], plan)
    with tempfile.TemporaryDirectory(prefix='lab-workspace-model-profile-') as directory:
        root = Path(directory)
        history = []
        def publish(name, value):
            path = root / name
            path.mkdir(exist_ok=False)
            (path / 'workspace.json').write_bytes(encoded(value))
            history.append({'generation': name, 'sha256': digest(encoded(value))})
            (root / 'HEAD.next').write_text(name)
            os.replace(root / 'HEAD.next', root / 'HEAD')
        publish('generation-1', bundle['workspace'])
        original = (root / 'generation-1/workspace.json').read_bytes()
        publish('generation-2', after['workspace'])
        reader_code = ('from pathlib import Path; import sys; root=Path(sys.argv[1]); '
            'sys.stdout.buffer.write((root/(root/"HEAD").read_text()/"workspace.json").read_bytes())')
        restarted = json.loads(subprocess.check_output([sys.executable, '-B', '-c', reader_code, str(root)]))
        need(restarted == after['workspace'], 'restart-profile-read')
        need((root / 'generation-1/workspace.json').read_bytes() == original, 'predecessor-overwritten')
        (root / 'JOURNAL.json').write_bytes(encoded({'plan': plan, 'history': history}))
        need(len(json.loads((root / 'JOURNAL.json').read_text())['history']) == 2, 'journal-history')
        # This fixture declares no irreversible state change; retained-reader restoration is valid only here.
        (root / 'HEAD.next').write_text('generation-1')
        os.replace(root / 'HEAD.next', root / 'HEAD')
        need((root / (root / 'HEAD').read_text() / 'workspace.json').read_bytes() == original, 'retained-reader')
    return {'created_generations': 2, 'fresh_process_read': 'pass', 'predecessor_preserved': True,
        'retained_reader_fixture': 'pass', 'temporary_state_removed': True,
        'native_runtime_upgrade': False, 'actual_workspace_adoption': False}


def adversarial_cases(bundle, schemas):
    cases = []
    def reject(name, operation, expected):
        try:
            operation()
        except Refusal as exc:
            need(str(exc) == expected, 'wrong-refusal:' + name + ':' + str(exc))
            cases.append({'name': name, 'expected_refusal': expected, 'result': 'pass'})
        else:
            raise Refusal('accepted-invalid:' + name)
    def changed(name, edit, code):
        bad = copy.deepcopy(bundle)
        edit(bad)
        reject(name, lambda: validate_bundle(bad), code)
    changed('missing area', lambda b: b['workspace']['areas'].pop('ontology'), 'workspace-profile-schema')
    changed('Project/Product collapse', lambda b: b['workspace'].__setitem__('product_ref', b['workspace']['project_ref']), 'identity-collapse')
    changed('wrong parent revision', lambda b: b['workspace']['adoption'].__setitem__('model_version_ref', 'unselected'), 'parent-version-mismatch')
    changed('parent/local authority collapse', lambda b: b['binding'].__setitem__('instance_authority_scope', b['binding']['parent_authority_scope']), 'authority-collapse')
    changed('silent override', lambda b: b['binding']['local_override_refs'].append('override:goal-meaning'), 'unreviewed-override')
    changed('inherited contract removed', lambda b: b['binding']['inherited_contract_refs'].pop(), 'inherited-contract-closure')
    changed('invented parent authority scope', lambda b: b['binding'].__setitem__('parent_authority_scope', 'scope:unselected-parent'), 'authority-scope-reference')
    changed('authoring decision broadened', lambda b: b['decision']['payload'].__setitem__('declared_effect_refs', ['effect:admit-model']), 'authoring-decision-effect-scope')
    changed('premature adoption', lambda b: b['binding'].__setitem__('binding_state', 'active'), 'adoption-not-authorized')
    changed('runtime copy', lambda b: b['selection'].__setitem__('copy_shared_runtimes', True), 'shared-runtime-copy')
    changed('full-source closure claim', lambda b: b['selection'].__setitem__('full_craft_source_closure', True), 'source-closure-not-established')
    changed('Goal membership inflation', lambda b: b['workspace']['goals'][1].__setitem__('membership', 'existing-source-reference'), 'goal-membership-inflation')
    changed('candidate Product promoted', lambda b: b['reconciliation']['product'].__setitem__('standing', 'admitted'), 'candidate-product-promotion')
    changed('resolved duplicate Project carrier', lambda b: b['reconciliation']['project'].__setitem__('artifact_type_ref', 'cal.artifact-type.project/v1'), 'resolved-duplicate-project-carrier')
    changed('unbounded recursion', lambda b: b['workspace']['recursion'].__setitem__('max_depth', 2), 'workspace-profile-schema')
    changed('invented role assignment', lambda b: b['owners']['routes'][0].__setitem__('assignment_state', 'active'), 'invented-owner-assignment')
    changed('unqualified global relation', lambda b: b['model']['relation_refs'].append({'relation_kind_ref': 'relation.conforms-to', 'counterpart_ref': 'fixture:unselected', 'counterpart_kind': 'capability-instance', 'direction': 'target'}), 'unqualified-global-relation')
    bad = copy.deepcopy(bundle)
    bad['selection']['files'][0]['sha256'] = '0' * 64
    reject('changed selected bytes', lambda: validate_bundle(bad), 'selected-source-drift')
    def diverged(path):
        data = root_read(path)
        if path == 'coordination/projects/craft/v1/project.json': return data + b' '
        return data
    bad = copy.deepcopy(bundle)
    for row in bad['selection']['files']:
        if row['path'] == 'coordination/projects/craft/v1/project.json':
            raw = diverged(row['path']); row.update(sha256=digest(raw), byte_length=len(raw))
    reject('repinned divergent duplicate', lambda: validate_bundle(bad, diverged), 'project-duplicate-diverged')
    reject('traversal', lambda: safe_relative('../outside'), 'unsafe-path')
    after, plan = successor_fixture(bundle)
    reject('uncertain transition redispatch', lambda: transition(bundle['workspace'], after['workspace'], plan, pending=True), 'reconciliation-required')
    stale = dict(plan, before_sha256='0' * 64)
    reject('stale upgrade preimage', lambda: transition(bundle['workspace'], after['workspace'], stale), 'stale-preimage')
    altered = copy.deepcopy(after['workspace']); altered['project_ref'] = 'another-project'
    reject('identity rewritten during upgrade', lambda: transition(bundle['workspace'], altered, plan), 'identity-or-history-change')
    altered = copy.deepcopy(after['workspace']); altered['owner_route'] = 'role:craft-product-owner'
    reject('owner changed during compatible upgrade', lambda: transition(bundle['workspace'], altered, plan), 'identity-or-history-change')
    altered = copy.deepcopy(after['workspace']); altered['adoption']['binding_ref'] = bundle['workspace']['adoption']['binding_ref']
    reject('same binding for new endpoint', lambda: transition(bundle['workspace'], altered, plan), 'successor-binding-required')
    manifest_path = HERE / 'craft/package.json'
    manifest = json.loads(manifest_path.read_text())
    manifest['surface_entries'].append(copy.deepcopy(manifest['surface_entries'][1]))
    reject('duplicate manifest member', lambda: need(not manifest_errors(manifest, manifest_path.parent,
        schemas['cal.artifact-type.canonical-package-manifest/v1']), 'invalid-package'), 'invalid-package')
    return cases


def package_fingerprints():
    return [{'path': p.relative_to(HERE).as_posix(), 'sha256': digest(p.read_bytes()), 'byte_length': p.stat().st_size}
        for p in sorted(HERE.rglob('*')) if p.is_file() and '__pycache__' not in p.parts
        and not p.is_relative_to(HERE / 'receipts')]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    report = {'status': 'fail', 'authority_effect': 'none', 'runtime_tests_run': False,
        'scope': 'candidate-record/schema/source/manifest checks and isolated profile fixture only'}
    try:
        initial = package_fingerprints()
        bundle = load_bundle()
        schemas = validate_bundle(bundle)
        manifest_count = check_packages(schemas)
        check_projections()
        navigation = check_navigation()
        fixture = scenario(bundle)
        shared_runtime_fixture = runtime_selection.scenario(bundle)
        negative = adversarial_cases(bundle, schemas)
        define_workflow = None
        process_checker = HERE / 'define-process/check_process.py'
        if process_checker.exists():
            namespace = {'__name__': 'recorded_define_process_check', '__file__': str(process_checker)}
            exec(compile(process_checker.read_text(), str(process_checker), 'exec'), namespace)
            define_workflow = namespace['check']()
        need(initial == package_fingerprints(), 'candidate-changed-during-validation')
        # Refuse a successful report if selected external inputs changed during the run.
        validate_bundle(bundle)
        report.update(status='pass', contract_count=len(schemas), package_manifest_count=manifest_count,
            markdown_files=navigation, selected_source_files=len(bundle['selection']['files']),
            scenario=fixture, shared_runtime_scenario=shared_runtime_fixture, negative_cases=negative, package_fingerprints=initial,
            define_workflow=define_workflow,
            completed_at_utc=datetime.now(timezone.utc).isoformat())
    except (Refusal, OSError, KeyError, ValueError, jsonschema.SchemaError) as exc:
        report['error'] = str(exc)
    if args.write_report:
        (HERE / 'receipts').mkdir(exist_ok=True)
        (HERE / 'receipts/validation.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ('package_fingerprints', 'negative_cases')}, indent=2))
    if 'negative_cases' in report: print('Negative cases passed:', len(report['negative_cases']))
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    sys.exit(main())
