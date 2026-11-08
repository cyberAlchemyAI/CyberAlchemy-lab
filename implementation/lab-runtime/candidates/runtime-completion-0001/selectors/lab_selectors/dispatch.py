"""Trusted host endorsement validation and complete nested gate expansion."""
from pathlib import Path
import hashlib
import os
from lab_contracts.codec import canonical, closed, need, parse, sha
from lab_contracts.validation import validate
from lab_contracts import dispatch_schema  # registers finite dispatch schemas
from .anchors import AnchoredReader, RootAnchor, legacy_json, relative

BASELINE_SHA = 'e3541b1f668375686b0c9e6c871acbeb1258830a1ac5ee84f025efd976343b3d'
ACCEPTANCE_SHA = '7e166ba3c174b7973f45e1f88752eb07c8733db72568a6de6522d8509b217b99'
KINDS = {'code', 'namespace-core', 'diagnostic', 'final-predecessor', 'final'}


def unique_bindings(bindings):
    result = {}
    for b in bindings:
        key = (b['root_id'], b['relative_path'])
        need(key not in result or result[key] == b, 'CONFLICTING_BINDINGS')
        result[key] = b
    return list(result.values())


def endorsement_reader(endorsement):
    validate('DispatchEndorsement', endorsement)
    roots = [RootAnchor(r['root_id'], r['path'], r['identity']) for r in endorsement['roots']]
    bindings = list(endorsement['source_bindings']) + list(endorsement['gate_input_bindings'])
    for key in ('baseline_binding', 'predecessor_acceptance_binding', 'selection_binding',
                'case_manifest_binding', 'plan_manifest_binding', 'freeze_binding',
                'expected_execution_binding', 'provider_binding', 'issuer_enrollment_binding'):
        if endorsement[key] is not None:
            bindings.append(endorsement[key])
    for command in endorsement['commands']:
        bindings.extend(command['program_bindings'])
    return AnchoredReader(roots, unique_bindings(bindings))


def verify_endorsement(raw, externally_retained_sha256):
    need(type(externally_retained_sha256) is str and len(externally_retained_sha256) == 64,
         'MISSING_EXTERNAL_DISPATCH_ANCHOR')
    need(sha(raw) == externally_retained_sha256, 'DISPATCH_ANCHOR_MISMATCH')
    value = validate('DispatchEndorsement', parse(raw, 64 * 1024 * 1024))
    reader = endorsement_reader(value)
    need(value['baseline_binding']['sha256'] == BASELINE_SHA and
         value['predecessor_acceptance_binding']['sha256'] == ACCEPTANCE_SHA, 'PREDECESSOR_ANCHOR')
    baseline = legacy_json(reader.read(value['baseline_binding']))
    acceptance = legacy_json(reader.read(value['predecessor_acceptance_binding']))
    need(baseline['runtime_eligible'] is False and acceptance['result'] == 'PASS'
         and acceptance['unit'] == 'LC-U01-01', 'BASELINE_CLAIM')
    for b in value['source_bindings']:
        need(b['kind'] != 'protected-input', 'CODE_CLOSURE_PRIVATE')
        reader.read(b)
    return value, reader


def _effect_keys(effects):
    return {canonical(e) for e in effects}


def prepare(endorsement, reader):
    manifest = validate('CaseManifest', parse(reader.read(endorsement['case_manifest_binding']), 64 * 1024 * 1024))
    for field in ('unit', 'stage', 'selection_kind'):
        need(manifest[field] == endorsement[field], 'CASE_DISPATCH_SCOPE')
    plan = legacy_json(reader.read(endorsement['plan_manifest_binding']))
    units = [u for u in plan['units'] if u['id'] == endorsement['unit']]
    need(len(units) == 1, 'UNIT_SELECTION')
    unit = units[0]
    need(unit['selection_kind'] == manifest['selection_kind'], 'UNIT_SELECTOR_KIND')
    minimum_gates = set(unit['external_gates'])
    # Phase-specific gates still apply before their corresponding effects, not
    # as future terminal prerequisites. The provider receives all phase rows.
    need(endorsement['run_root'].startswith(unit['evidence_root'].rstrip('/') + '/'), 'RUN_ROOT_SCOPE')
    relative(endorsement['run_root'])
    commands = {c['id']: c for c in endorsement['commands']}
    need(len(commands) == len(endorsement['commands']), 'COMMAND_ID_DUPLICATE')
    ids = [c['id'] for c in manifest['cases']]
    need(len(ids) == len(set(ids)), 'CASE_ID_DUPLICATE')
    selection_raw = reader.read(endorsement['selection_binding'])
    kind = manifest['selection_kind']
    if kind == 'code':
        need(endorsement['selection_binding'] == endorsement['baseline_binding'], 'CODE_BASELINE_BINDING')
        if manifest['stage'] == 'actual':
            need(unit.get('verification_kind') in ('semantic-review', 'authority-review'), 'CODE_ACTUAL_REFUSED')
            need(all(e['kind'] in ('inert-authoring', 'protected-read')
                     for e in endorsement['external_write_envelope']), 'CODE_REVIEW_RUNTIME_EFFECT')
    elif kind == 'namespace-core':
        validate('NamespaceCore', parse(selection_raw))
    else:
        validate('ExecutionSelection', parse(selection_raw))
    if kind == 'final':
        need(endorsement['freeze_binding'] is not None and
             endorsement['expected_execution_binding'] == endorsement['selection_binding'], 'FINAL_SELECTOR')
        freeze = validate('Freeze', parse(reader.read(endorsement['freeze_binding'])))
        need(freeze['execution_selection_binding'] == endorsement['selection_binding'], 'FINAL_FREEZE_MISMATCH')
    else:
        need(endorsement['freeze_binding'] is None, 'UNEXPECTED_FREEZE')
    if manifest['stage'] == 'actual':
        need(endorsement['provider_kind'] == 'actual' and endorsement['provider_binding'] is not None
             and endorsement['issuer_enrollment_binding'] is not None, 'ACTUAL_PROVIDER_REQUIRED')
    else:
        need(endorsement['provider_kind'] != 'actual', 'FIXTURE_ACTUAL_PROVIDER')
    approved_effects = _effect_keys(endorsement['external_write_envelope'])
    expanded = []
    terminal_required = set()
    terminal_produced = []
    for case in manifest['cases']:
        required = set(minimum_gates)
        effects = set()
        gate_checks = {g['gate']: validate('GateCheck', g) for g in unit['gate_checks']}
        need(set(gate_checks) == minimum_gates, 'UNIT_GATE_PHASES')
        for phase in ('setup', 'commands', 'cleanup'):
            for step in case[phase]:
                need(step['command_id'] in commands, 'UNSELECTED_COMMAND')
                command = commands[step['command_id']]
                need(set(step['declared_gates']) == set(command['required_gates']) and
                     _effect_keys(step['declared_effects']) == _effect_keys(command['effects']),
                     'NESTED_GATE_OR_EFFECT_UNDERSTATEMENT')
                selected_checks = {g['gate']: validate('GateCheck', g) for g in command['gate_checks']}
                need(len(selected_checks) == len(command['gate_checks']) and
                     set(selected_checks) == set(command['required_gates']), 'COMMAND_GATE_PHASES')
                for gate, check in selected_checks.items():
                    need(gate not in gate_checks or gate_checks[gate] == check, 'CONFLICTING_GATE_PHASES')
                    gate_checks[gate] = check
                required.update(command['required_gates'])
                effects |= _effect_keys(command['effects'])
                terminal_produced += [(r['gate'], r['requirement']) for r in command['produced_terminal_checks']]
                for b in command['program_bindings']:
                    need(b in endorsement['source_bindings'], 'PROGRAM_OUTSIDE_REVIEWED_CLOSURE')
                    reader.read(b)
                program_paths = {str(Path(reader.roots[b['root_id']].path) / b['relative_path'])
                                 for b in command['program_bindings']}
                need(command['argv'][0] in program_paths, 'EXECUTABLE_OUTSIDE_REVIEWED_CLOSURE')
                for arg in command['argv'][1:]:
                    if arg.endswith(('.py', '.sh', '.rs')):
                        actual = str(Path(arg) if Path(arg).is_absolute() else
                                     Path(endorsement['repository']) / command['cwd'] / arg)
                        need(actual in program_paths, 'ENTRYPOINT_OUTSIDE_REVIEWED_CLOSURE')
                if manifest['stage'] != 'actual':
                    need(not command['required_gates'] and all(e['kind'] == 'inert-authoring'
                         and e['authority_binding'] is None for e in command['effects']), 'INERT_EFFECT_ESCALATION')
                else:
                    need(command['effect_evidence_contract'] is not None, 'ACTUAL_EVIDENCE_CONTRACT_REQUIRED')
                    if kind == 'code':
                        need(all(e['kind'] in ('inert-authoring', 'protected-read') for e in command['effects']),
                             'CODE_REVIEW_RUNTIME_EFFECT')
                        need(all(e['kind'] != 'inert-authoring' or (e['root_id'] == 'repository' and any(
                             e['relative_path'] == scope.rstrip('/') or (scope.endswith('/') and
                             e['relative_path'].startswith(scope)) for scope in unit['write_scope']))
                             for e in command['effects']), 'CODE_REVIEW_OWNED_OUTPUT')
                    need(all(e['authority_binding'] is not None for e in command['effects']), 'EFFECT_AUTHORITY_MISSING')
        need(set(case['declared_gates']) == required and _effect_keys(case['declared_effects']) == effects,
             'CASE_GATE_OR_EFFECT_UNDERSTATEMENT')
        need(effects <= approved_effects, 'UNENDORSED_EFFECT')
        need(manifest['stage'] == 'actual' or not required, 'INERT_GATES')
        terminal_required.update((g['gate'], requirement) for g in gate_checks.values() for requirement in g['terminal_outputs'])
        expanded.append({'case': case, 'required_gates': sorted(required),
                         'effects': case['declared_effects'], 'gate_checks': [gate_checks[g] for g in sorted(gate_checks)]})
    need(len(terminal_produced) == len(set(terminal_produced)) and set(terminal_produced) == terminal_required,
         'UNIT_TERMINAL_PRODUCER_COVERAGE')
    return manifest, commands, expanded
