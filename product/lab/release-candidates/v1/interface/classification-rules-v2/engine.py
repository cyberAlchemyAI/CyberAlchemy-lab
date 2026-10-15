"""Closed declared-rule evaluators over independently selected original bytes.

This pure kernel checks annotation consistency. Its caller must supply a
verified source cut and independently selected records. It does not authenticate
that caller, establish a live Agent, or construct a ChangeProposal by itself.
"""
from dataclasses import dataclass
import hashlib
import json


class Refusal(ValueError):
    pass


class NotEvaluable(ValueError):
    pass


def require(value, reason):
    if not value:
        raise Refusal(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class ExactRecord:
    version_ref: str
    raw: bytes
    byte_sha256: str

    def body(self):
        require(type(self.raw) is bytes and sha(self.raw) == self.byte_sha256,
                'selected original record bytes changed')
        def unique_members(pairs):
            value = {}
            for key, item in pairs:
                require(key not in value, 'duplicate JSON member in exact record')
                value[key] = item
            return value
        def finite_token(token):
            raise Refusal('nonfinite JSON token in exact record')
        try:
            value = json.loads(self.raw, object_pairs_hook=unique_members,
                               parse_constant=finite_token)
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise Refusal('invalid exact record JSON bytes') from error
        require(type(value) is dict and type(value.get('node_id')) is str,
                'selected record identity is unavailable')
        require(self.version_ref.startswith(value['node_id'] + '@')
                and len(self.version_ref) > len(value['node_id']) + 1,
                'selected record revision differs from identity')
        return value


class ExactRecords:
    def __init__(self, records, scope_ref):
        require(type(scope_ref) is str and bool(scope_ref), 'selected scope required')
        self.scope_ref = scope_ref
        self.records = tuple(records)
        versions = set()
        for record in self.records:
            require(type(record) is ExactRecord, 'exact original-byte record required')
            body = record.body()
            require(body['scope_ref'] == scope_ref, 'selected record scope differs')
            require(record.version_ref not in versions, 'duplicate selected revision')
            versions.add(record.version_ref)

    def resolve(self, reference, kind=None):
        require(type(reference) is str and bool(reference), 'exact reference required')
        candidates = [record for record in self.records
                      if record.version_ref == reference or record.body()['node_id'] == reference]
        require(len(candidates) == 1, 'reference is missing or ambiguous in selected cut')
        record = candidates[0]
        body = record.body()
        require(kind is None or body['kind'] == kind, 'reference has the wrong semantic kind')
        return record, body


def _same_reference(records, reference, selected, kind=None):
    resolved, body = records.resolve(reference, kind)
    require(resolved == selected, 'declared reference selects another exact revision')
    return body


def _cardinality(context, runtime=False):
    subject, scheme, axis = context['subject'], context['scheme'], context['axis']
    if runtime:
        require(subject.body()['kind'] == 'agent-instance',
                'runtime posture applies only to an Agent Instance')
        if axis != 'axis:actor-kind':
            raise NotEvaluable('runtime posture cardinality has no selected meaning on this independent axis')
    for existing in context['existing']:
        record, body = context['records'].resolve(existing, 'classification-assignment')
        payload = body['payload']
        status = payload['status']
        if status in ('historical', 'retired', 'withdrawn', 'expired'):
            continue
        if status not in ('active', 'candidate-annotation'):
            raise NotEvaluable('existing assignment status has no selected evaluator')
        selected_subject, _ = context['records'].resolve(payload['subject_version_ref'])
        selected_scheme, _ = context['records'].resolve(payload['scheme_version_ref'], 'classification-scheme')
        selected_value, existing_value = context['records'].resolve(payload['value_ref'], 'classification-value')
        _same_reference(context['records'], existing_value['payload']['scheme_ref'], selected_scheme, 'classification-scheme')
        require(existing_value['payload']['axis_ref'] == payload['axis_ref'],
                'existing assignment Value and axis differ')
        same_slot = selected_subject == subject and selected_scheme == scheme
        if same_slot and payload['axis_ref'] == axis:
            raise Refusal('an active assignment already occupies the declared classification slot')


def _annotation(context):
    require(context['candidate']['authority_effect'] == 'none',
            'classification annotation cannot grant authority')


def _session(context):
    subject = context['subject'].body()
    require(subject['kind'] == 'agent-instance', 'machine boundary applies only to an Agent Instance')
    selected, session = context['records'].resolve(subject['payload']['session_ref'], 'agent-session')
    _same_reference(context['records'], session['payload']['agent_instance_ref'], context['subject'], 'agent-instance')
    # Declared identity coupling only: this does not assert an active resource,
    # authenticate an Agent, prove a timer or observe actual RAM disposal.
    matches = []
    for record in context['records'].records:
        body = record.body()
        if body['kind'] == 'agent-session':
            agent, _ = context['records'].resolve(body['payload']['agent_instance_ref'], 'agent-instance')
            if agent == context['subject']:
                matches.append(record)
    require(matches == [selected], 'Agent identity is reused across selected Sessions')
    return session


def _memory(context):
    session = _session(context)
    require(session['payload']['session_memory']['expires_with_session'] is True,
            'declared Session memory does not expire with its Session')


RULES = {
    ('cardinality', 'one-active-value-per-subject-axis'): _cardinality,
    ('cardinality', 'one-runtime-posture-per-agent-instance'): lambda c: _cardinality(c, runtime=True),
    ('compatibility', 'annotation-never-grants-authority'): _annotation,
    ('compatibility', 'machine-agent-requires-ephemeral-instance'): _session,
    ('compatibility', 'session-memory-expires-with-session'): _memory,
}


def evaluate(records, *, subject_ref, scheme_ref, value_ref, axis_ref,
             candidate, basis_bindings, material_bytes, existing_assignment_refs):
    """Check all declared rules; never interpret an unknown rule as success.

    Existing assignments must be the complete host-selected set for this cut.
    Basis bindings preserve exact evidence bytes, without claiming their truth,
    effectiveness or a causal conclusion. Live runtime proof is separate.
    """
    require(type(records) is ExactRecords, 'host-selected exact records required')
    subject, body = records.resolve(subject_ref)
    scheme, scheme_body = records.resolve(scheme_ref, 'classification-scheme')
    value, value_body = records.resolve(value_ref, 'classification-value')
    require(type(candidate) is dict and candidate['kind'] == 'classification-assignment',
            'assignment candidate required')
    require(candidate['scope_ref'] == records.scope_ref and candidate['authority_effect'] == 'none',
            'candidate scope or authority boundary differs')
    sp, vp, payload = scheme_body['payload'], value_body['payload'], candidate['payload']
    require(axis_ref in sp['axis_refs'] and vp['axis_ref'] == axis_ref == payload['axis_ref'],
            'Scheme, Value and candidate axes differ')
    _same_reference(records, vp['scheme_ref'], scheme, 'classification-scheme')
    membership = [records.resolve(reference, 'classification-value')[0] for reference in sp['value_refs']]
    require(value in membership, 'Value is outside the exact Scheme')
    require(payload['subject_ref'] == body['node_id'] and payload['subject_version_ref'] == subject.version_ref,
            'candidate subject identity or revision differs')
    require(payload['scheme_version_ref'] == scheme.version_ref,
            'candidate Scheme revision differs')
    _same_reference(records, payload['value_ref'], value, 'classification-value')
    require(type(payload['basis']) is str and bool(payload['basis'].strip()), 'classification basis required')
    require(type(basis_bindings) is list and bool(basis_bindings), 'exact basis bindings required')
    for binding in basis_bindings:
        require(set(binding) == {'ref', 'sha256'}, 'closed basis binding required')
        raw = material_bytes.get(binding['ref'])
        require(type(raw) is bytes and sha(raw) == binding['sha256'], 'original basis bytes differ')
    require(bool(payload['evidence_refs']), 'candidate evidence references required')
    for reference in payload['evidence_refs']:
        if reference in material_bytes:
            require(any(binding['ref'] == reference
                        and binding['sha256'] == sha(material_bytes[reference])
                        for binding in basis_bindings),
                    'candidate document evidence is outside the exact selected basis')
            continue
        record, evidence = records.resolve(reference)
        require(any(binding['sha256'] == record.byte_sha256 for binding in basis_bindings),
                'candidate evidence is outside the exact selected basis')
    checks = []
    context = {'records': records, 'subject': subject, 'scheme': scheme, 'axis': axis_ref,
               'candidate': candidate, 'existing': tuple(existing_assignment_refs)}
    for category, field in [('cardinality', 'cardinality_rules'), ('compatibility', 'compatibility_rules')]:
        names = sp[field]
        require(type(names) is list and len(names) == len(set(names)), 'duplicate or invalid declared rule')
        for name in names:
            evaluator = RULES.get((category, name))
            if evaluator is None:
                checks.append({'category': category, 'rule': name, 'result': 'not-evaluable',
                               'reason': 'No selected evaluator for this exact declared rule.'})
                continue
            try:
                evaluator(context)
            except NotEvaluable as error:
                checks.append({'category': category, 'rule': name, 'result': 'not-evaluable', 'reason': str(error)})
            except Refusal as error:
                checks.append({'category': category, 'rule': name, 'result': 'fail', 'reason': str(error)})
            else:
                checks.append({'category': category, 'rule': name, 'result': 'pass'})
    require(bool(checks), 'Scheme has no declared evaluable rule obligations')
    return {'schema_version': 'lab-classification-rule-checks/v1-candidate',
            'result': 'fail' if any(row['result'] == 'fail' for row in checks)
                      else 'not-evaluable' if any(row['result'] == 'not-evaluable' for row in checks) else 'pass',
            'subject_version_ref': subject.version_ref, 'scheme_version_ref': scheme.version_ref,
            'value_version_ref': value.version_ref, 'axis_ref': axis_ref,
            'checks': checks, 'basis_bindings': basis_bindings,
            'authority_effect': 'none', 'actual_owner_outcome': None,
            'runtime_conformance_proven': False, 'causality_proven': False,
            'claim_ceiling': 'Declared annotation consistency over exact selected bytes only. Host source-cut completeness, live Agent authentication, timers, memory disposal, candidate schema/core closure and ChangeProposal construction require separate verification.'}
