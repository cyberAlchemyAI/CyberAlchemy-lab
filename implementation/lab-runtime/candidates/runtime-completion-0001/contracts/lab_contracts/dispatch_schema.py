"""Acyclic host dispatch input: reviewed source → endorsement → receipt.

The endorsement digest is retained by the coordinator outside case authoring
and supplied through LAB_DISPATCH_ENDORSEMENT_SHA256. It is not self-derived.
"""
from .schema_catalog import obj, arr, ref, nullable, record, B, STRING, INTEGER, POSITIVE, PATH, DIGEST, DEFS, OS_ID

GATES = {'type': 'string', 'enum': ['G01', 'G02', 'G03', 'G04', 'G05', 'G06', 'G07', 'G08']}
EFFECT = obj({'root_id': STRING, 'relative_path': PATH,
    'kind': {'enum': ['inert-authoring', 'protected-read', 'deployment', 'candidate-effect',
                      'governed-effect', 'restore', 'operational', 'release']},
    'preimage_binding': nullable(B), 'expected_absent': {'type': 'boolean'},
    'owner_uid': OS_ID, 'mode': {'type':'integer','minimum':0,'maximum':4095}, 'authority_binding': nullable(B)})
DEFS['EffectEnvelope'] = EFFECT
PUBLIC_LOCATOR = obj({'kind': {'enum': ['evidence', 'public-package']}, 'root_id': STRING,
    'relative_path': PATH, 'max_bytes': {'type': 'integer', 'minimum': 1, 'maximum': 65536}})
EVIDENCE_ROLE = {'enum': ['gate-verification', 'currentness', 'effect', 'prestate', 'poststate', 'cleanup', 'output']}
DEFS['EffectEvidenceSlot'] = obj({'id': STRING, 'role': EVIDENCE_ROLE,
    'locator': PUBLIC_LOCATOR, 'subject_locators': arr(PUBLIC_LOCATOR, 0, 32, unique=True)})
DEFS['EffectEvidenceContract'] = record('effect-evidence-contract', {
    'slots': arr(ref('EffectEvidenceSlot'), 6, 32, unique=True),
    'max_total_bytes': {'type': 'integer', 'minimum': 1, 'maximum': 65536},
    'disclosure': {'const': 'reviewed-public-metadata-only'},
    'retention': {'const': 'exact-original-bytes-in-owned-attempt'}})
DEFS['PublicEffectReceipt'] = record('public-effect-receipt', {
    'role': {'enum': ['currentness', 'effect', 'prestate', 'poststate', 'cleanup', 'output']},
    'request_sha256': DIGEST, 'command_sha256': DIGEST, 'selection_binding': B,
    'enrollment_binding': B, 'effect_envelope': arr(EFFECT, unique=True),
    'original_input_bindings': arr(B, 1, unique=True), 'subject_bindings': arr(B, 0, 32, unique=True),
    'result': {'enum': ['PASS', 'FAIL', 'UNKNOWN']},
    'effect_state': {'enum': ['none', 'observed', 'unknown']},
    'cleanup': {'enum': ['clean', 'retained-owned', 'unknown']}})
DEFS['EffectEvidenceOriginal'] = obj({'slot_id': STRING, 'binding': B,
    'original_utf8': {'type': 'string', 'minLength': 1, 'maxLength': 65536}})
DEFS['GateCheck'] = obj({'gate': GATES, 'start_inputs': arr(STRING, unique=True),
    'before_effect': arr(STRING, unique=True), 'terminal_outputs': arr(STRING, unique=True),
    'consumed_outputs': arr(obj({'producer': STRING, 'output': STRING}), unique=True)})
DEFS['AdmissionCheck'] = obj({'gate': GATES,
    'phase': {'enum': ['start_inputs', 'before_effect', 'consumed_outputs']},
    'requirement': STRING, 'producer': nullable(STRING), 'evidence_bindings': arr(B, 1, 32, unique=True)})
DEFS['TerminalObligation'] = obj({'gate': GATES, 'requirement': STRING})
DEFS['TerminalCheck'] = obj({'gate': GATES, 'requirement': STRING, 'evidence_bindings': arr(B, 1, 32, unique=True)})
DEFS['EffectEvidence'] = record('effect-evidence', {
    'originals': arr(ref('EffectEvidenceOriginal'), 6, 32, unique=True),
    'terminal_checks': arr(ref('TerminalCheck'), 0, 256, unique=True)})
DEFS['SelectedCommand'] = obj({'id': STRING, 'argv': arr(STRING, 1, 1024),
    'environment': arr(obj({'name': STRING, 'value': {'type': 'string', 'maxLength': 4096}}), 0, 128),
    'cwd': PATH, 'program_bindings': arr(B, 1, unique=True),
    'required_gates': arr(GATES, unique=True), 'gate_checks': arr(ref('GateCheck'), 0, 8, unique=True), 'effects': arr(EFFECT, unique=True),
    'timeout_ms': POSITIVE, 'max_output_bytes': POSITIVE,
    'terminal_protocol': {'const': 'lab-case-command-result/v1'},
    'effect_evidence_contract': nullable(ref('EffectEvidenceContract')),
    'produced_terminal_checks': arr(ref('TerminalObligation'), 0, 256, unique=True)})
DEFS['CaseStep'] = obj({'command_id': STRING, 'declared_gates': arr(GATES, unique=True),
                      'declared_effects': arr(EFFECT, unique=True)})
DEFS['CaseManifest'] = record('case-manifest', {'unit': STRING,
    'selection_kind': {'enum': ['code', 'namespace-core', 'diagnostic', 'final-predecessor', 'final']},
    'stage': {'enum': ['inert', 'fixture', 'actual']},
    'cases': arr(obj({'id': STRING, 'declared_gates': arr(GATES, unique=True),
        'declared_effects': arr(EFFECT, unique=True),
        'setup': arr(ref('CaseStep')), 'commands': arr(ref('CaseStep'), 1),
        'cleanup': arr(ref('CaseStep'), 1)}), 1, 10000)})
DEFS['DispatchEndorsement'] = record('dispatch-endorsement', {
    'unit': STRING, 'repository': STRING,
    'roots': arr(obj({'root_id': STRING, 'path': STRING,
        'identity': obj({'device': INTEGER, 'inode': POSITIVE, 'uid': OS_ID,
                         'gid': OS_ID, 'mode': {'type':'integer','minimum':0,'maximum':4095}})}), 1, unique=True),
    'baseline_binding': B, 'predecessor_acceptance_binding': B,
    'selection_binding': B, 'case_manifest_binding': B,
    'plan_manifest_binding': B, 'source_bindings': arr(B, 1, unique=True),
    'commands': arr(ref('SelectedCommand'), 1, unique=True),
    'run_root': PATH, 'selection_kind': {'enum': ['code', 'namespace-core', 'diagnostic', 'final-predecessor', 'final']},
    'stage': {'enum': ['inert', 'fixture', 'actual']},
    'freeze_binding': nullable(B), 'expected_execution_binding': nullable(B),
    'provider_binding': nullable(B), 'provider_command_id': nullable(STRING),
    'provider_kind': {'enum': ['none', 'fixture', 'actual']},
    'issuer_enrollment_binding': nullable(B), 'gate_input_bindings': arr(B, unique=True),
    'external_write_envelope': arr(EFFECT, unique=True),
    'authority_effect': {'const': 'none'}})
DEFS['CommandResult'] = obj({'schema_version': {'const': 'lab-case-command-result/v1'},
    'result': {'enum': ['PASS', 'FAIL', 'ERROR', 'NOT_RUN', 'UNKNOWN']},
    'checks': INTEGER, 'effect_state': {'enum': ['none', 'owned-inert', 'observed', 'unknown']},
    'cleanup': {'enum': ['clean', 'retained-owned', 'unknown']}})
DEFS['GateVerification'] = record('gate-verification', {'request_sha256': DIGEST,
    'verified_gate_ids': arr(GATES, unique=True), 'original_input_bindings': arr(B, 1, unique=True),
    'enrollment_binding': B, 'effect_envelope': arr(EFFECT, unique=True),
    'verdict': {'const': 'PERMITTED'}, 'currentness_witness_binding': B,
    'admission_checks': arr(ref('AdmissionCheck'), 0, 256, unique=True)})
