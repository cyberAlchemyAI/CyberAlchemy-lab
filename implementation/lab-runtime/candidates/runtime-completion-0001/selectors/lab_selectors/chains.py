"""Byte-bound acyclic selection joins. Structural acceptance is not activation."""
from lab_contracts.codec import need, parse, sha
from lab_contracts.validation import validate


def selected(reader, binding, name, independent_expected):
    need(binding == independent_expected, 'INDEPENDENT_SELECTION_DIFFERS')
    raw = reader.read(binding)
    value = validate(name, parse(raw))
    return value


def code_family_execution(reader, expected):
    need(set(expected) == {'code', 'family', 'execution'}, 'CHAIN_ANCHORS')
    code = selected(reader, expected['code'], 'CodeSelection', expected['code'])
    family = selected(reader, expected['family'], 'FamilySelection', expected['family'])
    execution = selected(reader, expected['execution'], 'ExecutionSelection', expected['execution'])
    need(family['code_selection_binding'] == execution['code_selection_binding'] == expected['code'],
         'CODE_CHAIN')
    need(execution['family_selection_binding'] == expected['family'], 'FAMILY_CHAIN')
    need(execution['environment_binding'] == code['environment_binding'], 'ENVIRONMENT_CHAIN')
    return code, family, execution


def namespace_chain(reader, expected):
    need(set(expected) == {'core', 'review', 'activation'}, 'NAMESPACE_ANCHORS')
    core = selected(reader, expected['core'], 'NamespaceCore', expected['core'])
    review = selected(reader, expected['review'], 'NamespaceReview', expected['review'])
    activation = selected(reader, expected['activation'], 'NamespaceActivation', expected['activation'])
    need(review['core_binding'] == activation['core_binding'] == expected['core']
         and activation['review_binding'] == expected['review'], 'NAMESPACE_CHAIN')
    need(review['outcome'] == 'PASS', 'NAMESPACE_REVIEW_REFUSED')
    # Current deployed identities, enrollment and permission remain the provider's job.
    return core, review, activation


def consumer_mapping(store, expected_consumers, observed_consumers):
    validate('GenerationStoreSelection', store)
    wanted = store['canonical_consumer_inventory']
    need(wanted == expected_consumers == observed_consumers, 'CONSUMER_INVENTORY')
    ids = [v['identity'] for v in wanted]
    need(len(ids) == len(set(ids)), 'DUPLICATE_CONSUMER')
    return len(ids)


def late_lesson(execution, family, policy, lesson, *, expected_policy_binding,
                reader, expected_late_input_binding, expected_family_lesson_binding):
    validate('ExecutionSelection', execution)
    validate('FamilySelection', family)
    validate('LessonConsumerPolicy', policy)
    need(selected(reader, expected_policy_binding, 'LessonConsumerPolicy', expected_policy_binding) == policy,
         'LESSON_POLICY_BYTES')
    validate('LessonInput', lesson)
    need(family['lesson_selection_binding'] == expected_family_lesson_binding, 'IMMUTABLE_FAMILY_LESSON')
    need(policy['late_input_schema_binding'] is not None, 'NEW_FAMILY_REQUIRED')
    contract = selected(reader, policy['late_input_schema_binding'], 'LateInputContract', expected_late_input_binding)
    need(contract['source_identity'] == family['source_identity']
         and contract['source_schema_binding'] == policy['source_constraint_binding']
         and contract['profile_schema_binding'] == policy['profile_constraint_binding'], 'LATE_INPUT_ORIGINAL_SCHEMA')
    need(execution['allowed_attempt_variations']['lesson_input_contract_binding'] ==
         lesson['policy_binding'] == expected_policy_binding, 'LESSON_POLICY')
    need(lesson['source_identity'] == family['source_identity'], 'LESSON_SOURCE')
    data = parse(reader.read(lesson['typed_data_binding'], max_bytes=policy['max_payload_bytes']))
    from jsonschema import Draft202012Validator
    from referencing import Registry
    def no_remote(_):
        from lab_contracts.codec import Refusal
        raise Refusal('LATE_SCHEMA_EXTERNAL_REF')
    for prefix in ('source', 'profile'):
        original = parse(reader.read(contract[prefix + '_schema_binding']))
        pointer = contract[prefix + '_instance_selector']
        need(pointer.startswith('#/'), 'LATE_SCHEMA_SELECTOR')
        fragment = original
        try:
            for part in pointer[2:].split('/'):
                fragment = fragment[part.replace('~1', '/').replace('~0', '~')]
            need(type(fragment) is dict and fragment.get('type') == 'object'
                 and fragment.get('additionalProperties') is False, 'NEW_FAMILY_REQUIRED')
            Draft202012Validator.check_schema(fragment)
            need(Draft202012Validator(fragment, registry=Registry(retrieve=no_remote)).is_valid(data),
                 'LATE_INPUT_SCHEMA_REFUSED')
        except (KeyError, TypeError, IndexError):
            from lab_contracts.codec import Refusal
            raise Refusal('NEW_FAMILY_REQUIRED') from None
    return {'structural_compatibility': True, 'eligibility_and_permission_required': True}


def final_selection(execution_binding, freeze, independently_expected_freeze):
    validate('Freeze', freeze)
    need(freeze == independently_expected_freeze
         and freeze['execution_selection_binding'] == execution_binding, 'FINAL_FREEZE_MISMATCH')
    return True


def phase_remaining(permit, reader, expected_budget_binding, elapsed_ms, phase_id, remaining_utc_ms):
    validate('PhasePermit', permit)
    selected_binding = permit['diagnostic_bounds_binding'] if permit['mode'] == 'diagnostic' else permit['measured_budget_binding']
    need(selected_binding == expected_budget_binding, 'INDEPENDENT_BUDGET_BINDING')
    budget = selected(reader, selected_binding,
        'DiagnosticBounds' if permit['mode'] == 'diagnostic' else 'MeasuredBudget', expected_budget_binding)
    need(type(elapsed_ms) is int and elapsed_ms >= 0 and type(remaining_utc_ms) is int,
         'TIMING_INPUT')
    matches = [p for p in budget['phase_caps'] if p['phase_id'] == phase_id == permit['phase_id']]
    need(len(matches) == 1, 'UNSELECTED_PHASE')
    reserve = max(budget['cleanup_reserve_ms'], permit['cleanup_reserve_seconds'] * 1000)
    cap = matches[0]['hard_cap_ms']
    need(elapsed_ms + cap + reserve < budget['total_cap_ms']
         and cap + reserve < remaining_utc_ms, 'INSUFFICIENT_WHOLE_ATTEMPT_BUDGET')
    return cap
