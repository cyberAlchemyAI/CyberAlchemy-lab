"""Finite Draft 2020-12 schema vocabulary for LC-U01-02.

Policy internals are exact ByteBindings to independently reviewed contracts;
this unit does not invent host values or authoritative identity joins.
"""
from .codec import MIN_INTEGER, MAX_INTEGER

STRING = {'type': 'string', 'minLength': 1, 'maxLength': 4096}
DIGEST = {'type': 'string', 'pattern': '^[0-9a-f]{64}$', 'minLength': 64, 'maxLength': 64}
INTEGER = {'type': 'integer', 'minimum': 0, 'maximum': MAX_INTEGER}
POSITIVE = {'type': 'integer', 'minimum': 1, 'maximum': MAX_INTEGER}
OS_ID = {'type': 'integer', 'minimum': 0, 'maximum': 2 ** 32 - 2}
TIME = {'type': 'string', 'format': 'date-time', 'maxLength': 64}
NULL = {'type': 'null'}
PATH = {'type': 'string', 'minLength': 1, 'maxLength': 4096,
        'pattern': r'^(?!/)(?!.*(?:^|/)\.{1,2}(?:/|$))(?!.*//)(?!.*[\\\u0000])[^/]+(?:/[^/]+)*$'}


def obj(fields):
    return {'type': 'object', 'additionalProperties': False,
            'required': list(fields), 'properties': fields}


def arr(item, minimum=0, maximum=1000000, unique=False):
    return {'type': 'array', 'items': item, 'minItems': minimum,
            'maxItems': maximum, 'uniqueItems': unique}


def ref(name):
    return {'$ref': '#/$defs/' + name}


def nullable(value):
    return {'oneOf': [value, NULL]}


def record(name, fields):
    return obj({'schema_version': {'const': 'lab-completion-' + name + '/v1'}, **fields})


B = ref('ByteBinding')
DEFS = {}
DEFS['ByteBinding'] = obj({'kind': {'enum': ['execution', 'semantic', 'evidence',
    'public-package', 'protected-input']}, 'root_id': STRING, 'relative_path': PATH,
    'sha256': DIGEST, 'size_bytes': INTEGER})
DEFS['SemanticSelection'] = obj({'binding': B, 'identity': STRING, 'version': STRING,
    'carrier_binding': B, 'schema_binding': B, 'schema_selector': STRING,
    'source_cut': STRING})
DEFS['ProtectedDescriptor'] = record('protected-descriptor', {'opaque_locator': STRING,
    'permission_locator': STRING, 'metadata_review_binding': B,
    'public_metadata_binding': B, 'authority_effect': {'const': 'none'}})
DEFS['CodeSelection'] = record('code-selection', {
    'selection_id': STRING, 'predecessor_binding': B, 'file_manifest_binding': B,
    'schema_selection_binding': B, 'environment_binding': B,
    'branch_bindings': arr(B, unique=True), 'dependency_binding': B,
    'original_accounting_binding': B, 'authority_effect': {'const': 'none'}})
DEFS['FamilySelection'] = record('family-selection', {
    'family_id': STRING, 'source_identity': STRING, 'reader_identity': STRING,
    'mapper_identity': STRING, 'context_producer_identity': STRING,
    'lesson_selection_binding': B, 'signed_period_binding': B,
    'code_selection_binding': B, 'source_cut': STRING, 'custody_selection_binding': B,
    'slot_epoch': POSITIVE, 'predecessor_disposition_binding': B,
    'signature_bindings': arr(B, 1, unique=True)})
DEFS['AllowedVariations'] = obj({'credential_contract_binding': nullable(B),
    'session_contract_binding': nullable(B), 'attempt_contract_binding': nullable(B),
    'lesson_input_contract_binding': nullable(B)})
DEFS['ExecutionSelection'] = record('execution-selection', {
    'execution_id': STRING, 'code_selection_binding': B, 'family_selection_binding': B,
    'profile_binding': B, 'environment_binding': B,
    'workflow_plan_descriptor_binding': B, 'namespace_selection_binding': B,
    'provisioner_selection_binding': B, 'branch_selection_bindings': arr(B, unique=True),
    'allowed_attempt_variations': ref('AllowedVariations'),
    'original_obligation_inventory_binding': B})
DEFS['RootIdentity'] = obj({'root_id': STRING, 'deployment_locator': STRING,
    'device': INTEGER, 'inode': POSITIVE, 'mount_id': POSITIVE,
    'owner_uid': OS_ID, 'owner_gid': OS_ID, 'mode': {'type': 'integer', 'minimum': 0, 'maximum': 4095},
    'ancestor_inventory_binding': B, 'acl_policy_binding': B,
    'writable_alias_disposition_binding': B})
limit_names = ['max_frame_bytes', 'max_member_bytes', 'max_member_count',
    'max_stage_bytes', 'max_retained_generation_bytes', 'max_retained_generation_count',
    'max_retained_orphan_bytes', 'max_retained_orphan_count', 'journal_control_reserve_bytes',
    'lock_timeout_ms', 'rpc_timeout_ms', 'phase_timeout_ms']
DEFS['Limits'] = obj({**{n: POSITIVE for n in limit_names}, 'max_inflight_operations': {'const': 1}})
DEFS['NamespaceCore'] = record('namespace-core', {'namespace_id': STRING,
    'roots': arr(ref('RootIdentity'), 1, unique=True), 'broker_executable_binding': B,
    'broker_dependency_binding': B, 'broker_uid': OS_ID, 'broker_gid': OS_ID,
    'workload_uid': OS_ID, 'workload_gid': OS_ID, 'credential_policy_binding': B,
    'administrator_policy_binding': B, 'confinement_policy_binding': B,
    'supervisor_policy_binding': B, 'ipc_policy_binding': B, 'issuer_enrollment_binding': B,
    'store_selection_binding': B, 'limits': ref('Limits'), 'deployment_observations_binding': B})
DEFS['NamespaceReview'] = record('namespace-review', {'core_binding': B,
    'reviewer_identity': STRING, 'command_bindings': arr(B, 1, unique=True),
    'subject_bindings': arr(B, 1, unique=True), 'terminal_evidence_bindings': arr(B, 1, unique=True),
    'outcome': {'enum': ['PASS', 'FAIL', 'UNKNOWN']}, 'limitations': arr(STRING)})
DEFS['NamespaceActivation'] = record('namespace-activation', {'core_binding': B,
    'review_binding': B, 'activation_permit_binding': B, 'activation_epoch': POSITIVE,
    'not_before': TIME, 'expires_at': TIME})
DEFS['Consumer'] = obj({'identity': STRING, 'relative_path': PATH, 'semantic_role': STRING,
    'reader_adapter_binding': B, 'writer_adapter_binding': B, 'commit_interpretation_binding': B})
DEFS['GenerationStoreSelection'] = record('generation-store-selection', {
    'logical_store_id': STRING, 'instance_id': STRING, 'broker_writer_domain': STRING,
    'pointer_root_id': STRING, 'pointer_member': PATH, 'generations_root_id': STRING,
    'control_root_id': STRING, 'canonical_member_inventory_binding': B,
    'canonical_consumer_inventory': arr(ref('Consumer'), 1, unique=True),
    'filesystem_profile_binding': B, 'limits': ref('Limits'), 'schema_binding': B, 'codec_binding': B})
DEFS['GenerationManifest'] = record('generation-manifest', {'logical_store_id': STRING,
    'creation_instance_id': STRING, 'writer_epoch': POSITIVE, 'sequence': POSITIVE,
    'generation_id': STRING, 'predecessor_pointer_binding': nullable(B),
    'operation_fingerprint': DIGEST, 'member_bindings': arr(B, 1, unique=True),
    'source_cut': STRING, 'reader_inventory_binding': B, 'expected_replay_result_binding': B})
DEFS['PointerRecord'] = record('pointer-record', {'logical_store_id': STRING,
    'writer_epoch': POSITIVE, 'sequence': POSITIVE, 'predecessor_pointer_binding': nullable(B),
    'generation_manifest_binding': B, 'operation_id': STRING})
DEFS['SlotReceipt'] = record('slot-receipt', {'slot_id': STRING, 'epoch': POSITIVE,
    'holder_identity': STRING, 'lock_identity': STRING, 'namespace_binding': B,
    'family_intent_binding': B, 'prior_family_disposition_binding': B,
    'acquired_at_utc': TIME, 'containment_binding': B,
    'state': {'enum': ['reserved', 'active', 'closing', 'closed', 'quarantined']},
    'terminal_binding': nullable(B)})
DEFS['PhaseCap'] = obj({'phase_id': STRING, 'hard_cap_ms': POSITIVE, 'max_staged_effect_bytes': INTEGER})
DEFS['DiagnosticBounds'] = record('diagnostic-bounds', {'attempt_id': STRING,
    'phase_caps': arr(ref('PhaseCap'), 1, unique=True), 'total_cap_ms': POSITIVE,
    'cleanup_reserve_ms': POSITIVE, 'load_binding': B, 'justification_binding': B,
    'review_binding': B, 'kill_reap_policy_binding': B, 'no_extra_effects': {'const': True}})
DEFS['MeasuredBudget'] = record('measured-budget', {'attempt_id': STRING,
    'phase_caps': arr(ref('PhaseCap'), 1, unique=True), 'total_cap_ms': POSITIVE,
    'cleanup_reserve_ms': POSITIVE, 'load_binding': B, 'sample_bindings': arr(B, 1, unique=True),
    'complete_path_binding': B, 'review_binding': B})
DEFS['PhasePermit'] = record('phase-permit', {'phase_id': STRING,
    'mode': {'enum': ['diagnostic', 'qualification']}, 'diagnostic_bounds_binding': nullable(B),
    'measured_budget_binding': nullable(B), 'intent_binding': B, 'execution_selection_binding': B,
    'slot_receipt_binding': B, 'prior_receipt_bindings': arr(B, unique=True),
    'input_bindings': arr(B, unique=True), 'allowed_output_roots': arr(STRING, 1, unique=True),
    'expected_output_names': arr(PATH, unique=True), 'effect_kind': STRING,
    'principal_permission_binding': B, 'reviewer_acceptance_binding': B,
    'not_before': TIME, 'expires_at': TIME, 'cleanup_reserve_seconds': POSITIVE})
DEFS['TypedLessonField'] = obj({'field': STRING,
    'kind': {'enum': ['observation-checklist', 'parameter-constraint']},
    'data_schema_binding': B})
DEFS['LessonConsumerPolicy'] = record('lesson-consumer-policy', {
    'consumer_binding': B, 'producer_binding': B, 'allowed_fields': arr(ref('TypedLessonField'), 1, unique=True),
    'applicability_rule_binding': B, 'conflict_rule_binding': B, 'review_rule_binding': B,
    'source_constraint_binding': B, 'profile_constraint_binding': B,
    'late_input_schema_binding': nullable(B), 'max_payload_bytes': POSITIVE})
DEFS['LessonInput'] = record('lesson-input', {'lesson_original_binding': B,
    'failure_evidence_binding': B, 'eligibility_review_binding': B, 'source_identity': STRING,
    'work_ref': STRING, 'not_before': TIME, 'expires_at': TIME,
    'typed_data_binding': B, 'principal_ref': STRING, 'scope_ref': STRING,
    'producer_operation_id': STRING, 'policy_binding': B})
DEFS['LateInputContract'] = record('late-input-contract', {'source_identity': STRING,
    'source_schema_binding': B, 'profile_schema_binding': B,
    'source_instance_selector': STRING, 'profile_instance_selector': STRING})
DEFS['Freeze'] = record('freeze', {'execution_selection_binding': B,
    'acceptance_binding': B, 'predecessor_evidence_bindings': arr(B, 1, unique=True)})


def schema(name):
    if name not in DEFS:
        raise KeyError(name)
    return {'$schema': 'https://json-schema.org/draft/2020-12/schema',
            '$id': 'urn:lab-completion:contract:' + name + ':v1',
            '$defs': DEFS, '$ref': '#/$defs/' + name}
