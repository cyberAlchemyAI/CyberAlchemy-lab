"""Validate only reviewed public receipt metadata, then retain exact originals.

The separately enrolled selected provider verifies authority and observations.
These checks establish scope, phase completeness, disclosure and durable evidence;
they cannot manufacture a grant, real observation, or private-body access.
"""
from lab_contracts.codec import Refusal, canonical, need, parse, sha
from lab_contracts.validation import validate


class EffectEvidenceRefusal(Refusal):
    def __init__(self, reason, effect_state, detail=None):
        super().__init__(reason)
        self.effect_state = effect_state
        self.detail = detail or {}


def _locator(binding, locator):
    need(binding['kind'] in ('evidence', 'public-package') and
         all(binding[k] == locator[k] for k in ('kind', 'root_id', 'relative_path')) and
         binding['size_bytes'] <= locator['max_bytes'], 'PUBLIC_RECEIPT_LOCATOR')


def _public(value):
    if isinstance(value, dict):
        if set(value) == {'kind', 'root_id', 'relative_path', 'sha256', 'size_bytes'}:
            need(value['kind'] != 'protected-input', 'PRIVATE_RECEIPT_METADATA')
        for child in value.values():
            _public(child)
    elif isinstance(value, list):
        for child in value:
            _public(child)


def phase_requirements(request):
    admission, terminal = [], []
    gates = []
    for check in request['gate_checks']:
        validate('GateCheck', check)
        gate = check['gate']; gates.append(gate)
        for phase in ('start_inputs', 'before_effect'):
            admission += [(gate, phase, requirement, None) for requirement in check[phase]]
        for row in check['consumed_outputs']:
            need(row['producer'] != request['unit'], 'OWN_FUTURE_ADMISSION')
            admission.append((gate, 'consumed_outputs', row['output'], row['producer']))
        terminal += [(gate, requirement) for requirement in check['terminal_outputs']]
    need(sorted(gates) == request['required_gates'] and len(gates) == len(set(gates)), 'GATE_PHASE_COVERAGE')
    return admission, terminal


def validate_and_retain(evidence, proof, result, request, command, endorsement, retain_original):
    """Callback must durably create no-replace owned files and return bindings.

    Each receipt is retained only after complete closed public metadata validation.
    Total original UTF-8 byte length is checked before any original is parsed.
    Provider transport separately caps the entire reply before JSON parsing.
    """
    contract = validate('EffectEvidenceContract', command['effect_evidence_contract'])
    validate('EffectEvidence', evidence)
    need(callable(retain_original), 'DURABLE_RECEIPT_RETENTION_REQUIRED')
    slots = {s['id']: s for s in contract['slots']}
    need(len(slots) == len(contract['slots']), 'DUPLICATE_RECEIPT_SLOT')
    locators = [(s['locator']['kind'], s['locator']['root_id'], s['locator']['relative_path']) for s in slots.values()]
    need(len(locators) == len(set(locators)), 'DUPLICATE_RECEIPT_LOCATOR')
    roles = [s['role'] for s in slots.values()]
    required_roles = ('gate-verification', 'currentness', 'effect', 'prestate', 'poststate', 'cleanup')
    need(all(roles.count(r) == 1 for r in required_roles), 'RECEIPT_ROLE_COVERAGE')
    originals = evidence['originals']
    need(len(originals) == len(slots) and len({o['slot_id'] for o in originals}) == len(slots)
         and {o['slot_id'] for o in originals} == set(slots), 'RECEIPT_SLOT_COVERAGE')
    raws = [o['original_utf8'].encode('utf-8') for o in originals]
    need(sum(map(len, raws)) <= contract['max_total_bytes'], 'RECEIPT_AGGREGATE_LIMIT')
    admission, unit_terminal = phase_requirements(request)
    terminal = [(row['gate'], row['requirement']) for row in request['produced_terminal_checks']]
    need(len(terminal) == len(set(terminal)) and set(terminal) <= set(unit_terminal), 'COMMAND_TERMINAL_SCOPE')
    admission_rows = proof['admission_checks']
    observed = [(a['gate'], a['phase'], a['requirement'], a['producer']) for a in admission_rows]
    need(len(observed) == len(set(observed)) and set(observed) == set(admission), 'ADMISSION_PHASE_COVERAGE')
    need(all(b in proof['original_input_bindings'] for a in admission_rows for b in a['evidence_bindings']),
         'ADMISSION_ORIGINAL_INPUT')
    need(proof['original_input_bindings'] == request['gate_input_bindings'], 'GATE_INPUT_COVERAGE')
    need(proof['request_sha256'] == sha(canonical(request)) and
         proof['verified_gate_ids'] == request['required_gates'] and
         proof['enrollment_binding'] == endorsement['issuer_enrollment_binding'] and
         proof['effect_envelope'] == request['effects'], 'GATE_PROOF_SCOPE')
    bindings_by_role = {}
    outcomes = [result['result']]
    effect_states = [result['effect_state']]
    cleanup_states = [result['cleanup']]
    for original, raw in zip(originals, raws):
        slot = slots[original['slot_id']]; binding = original['binding']
        _locator(binding, slot['locator'])
        need(binding['size_bytes'] == len(raw) and binding['sha256'] == sha(raw), 'RECEIPT_ORIGINAL_BYTES')
        document = parse(raw, max_bytes=slot['locator']['max_bytes'])
        _public(document)
        role = slot['role']; bindings_by_role.setdefault(role, []).append(binding)
        if role == 'gate-verification':
            validate('GateVerification', document)
            need(document == proof and not slot['subject_locators'], 'RETAINED_GATE_PROOF')
            continue
        validate('PublicEffectReceipt', document)
        need(document['role'] == role and document['request_sha256'] == proof['request_sha256'] and
             document['command_sha256'] == request['command_sha256'] and
             document['selection_binding'] == request['selection_binding'] and
             document['enrollment_binding'] == endorsement['issuer_enrollment_binding'] and
             document['effect_envelope'] == request['effects'] and
             document['original_input_bindings'] == proof['original_input_bindings'], 'RECEIPT_SCOPE')
        outcomes.append(document['result'])
        if role in ('effect', 'poststate', 'cleanup', 'output'):
            effect_states.append(document['effect_state'])
            cleanup_states.append(document['cleanup'])
        subjects = document['subject_bindings']; locators = slot['subject_locators']
        need(len(subjects) == len(locators), 'PUBLIC_SUBJECT_COVERAGE')
        for binding, locator in zip(subjects, locators):
            _locator(binding, locator)
    need(proof['currentness_witness_binding'] == bindings_by_role['currentness'][0], 'RETAINED_CURRENTNESS')
    terminal_rows = evidence['terminal_checks']
    observed = [(a['gate'], a['requirement']) for a in terminal_rows]
    need(len(observed) == len(set(observed)) and set(observed) <= set(terminal), 'TERMINAL_PHASE_COVERAGE')
    produced = sum((bindings_by_role.get(role, []) for role in ('effect', 'poststate', 'cleanup', 'output')), [])
    need(all(b in produced for a in terminal_rows for b in a['evidence_bindings']), 'TERMINAL_ORIGINAL_OUTPUT')
    verified_effect = effect_states[0] if len(set(effect_states)) == 1 else 'unknown'
    verified_cleanup = ('unknown' if 'unknown' in cleanup_states else
                        'retained-owned' if 'retained-owned' in cleanup_states else 'clean')
    evidence_result = ('UNKNOWN' if 'UNKNOWN' in outcomes or verified_effect == 'unknown' or verified_cleanup == 'unknown'
                       else 'FAIL' if any(outcome != 'PASS' for outcome in outcomes) else 'PASS')
    if evidence_result == 'PASS':
        need(set(observed) == set(terminal), 'TERMINAL_PHASE_COVERAGE')
    retained = []
    detail = {'retained_originals': retained, 'admission_checks': admission_rows,
              'terminal_checks': terminal_rows, 'gate_verification': proof,
              'retention': contract['retention'], 'evidence_result': evidence_result,
              'verified_effect_state': verified_effect, 'verified_cleanup': verified_cleanup}
    for number, (original, raw) in enumerate(zip(originals, raws), 1):
        try:
            stored = retain_original(number, raw)
            validate('ByteBinding', stored)
            need(stored['kind'] == 'evidence' and stored['sha256'] == sha(raw) and stored['size_bytes'] == len(raw),
                 'DURABLE_RECEIPT_BYTES')
        except Exception as exc:
            raise EffectEvidenceRefusal(str(exc) if isinstance(exc, Refusal) else 'RECEIPT_RETENTION_UNKNOWN',
                                        verified_effect, detail) from None
        retained.append({'slot_id': original['slot_id'], 'role': slots[original['slot_id']]['role'],
                         'original_binding': original['binding'], 'retained_binding': stored})
    return detail
