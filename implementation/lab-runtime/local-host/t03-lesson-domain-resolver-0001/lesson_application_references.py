"""Exact Lesson Application reference closure for the local current-legacy Session.

Integration target: copy this module into the next selected common API package,
construct LessonApplicationReferences only for the v2 local application policy,
and expose it as WorkflowCandidateHandlers.resolution_references. The existing
CandidateHandlers.validate hook then records an exact-resolution-reference
check; every unsupported carrier/state continues through its existing
not-evaluable path. This module grants no admission or external Tool action.
"""
import copy
import importlib
from pathlib import Path

CARRIER = 'cal.artifact-type.lesson-application/v1'
POLICY = 'lab-local-lesson-application-policy/v2-candidate'
RELATION = 'relation.applies-lesson'
LESSON = 'cal.artifact-type.operational-lesson/v1'


def need(value, reason):
    if not value:
        raise ValueError(reason)


def supported(target, policy):
    """Scope support to one current local candidate, leaving other cases unresolved."""
    record = target.get('record') or {}
    payload = record.get('payload') or {}
    return (policy.get('schema_version') == POLICY
            and target.get('carrier_ref') == CARRIER
            and target.get('operation') == 'admit'
            and payload.get('conflict_refs') == []
            and payload.get('override_refs') == []
            and record.get('successor_refs') == [])


def validate_selected(target, proposal, *, owner, cut, attachment,
                      selection, applicability, instruction, lesson, routing):
    """Pure shape and reference check over separately authenticated originals."""
    record = target['record']; payload = record['payload']
    need(record['schema_version'] == 'cyberalchemy-lab-lesson-application/v1'
         and record['kind'] == 'lesson-application'
         and record['lifecycle_state'] == 'candidate'
         and record['authority_effect'] == 'none',
         'Lesson Application candidate kind/state differs')
    need(proposal['base_cut'] == cut == attachment['source_cut'], 'Lesson Application source cut differs')
    need(record['scope_ref'] == proposal['scope_ref'] == lesson['scope_ref'], 'Lesson Application scope differs')
    need(record['owner_ref'] == owner == attachment['principal_ref'], 'Lesson Application owner differs')
    need(payload['session_ref'] == selection['session_ref'] == attachment['session_ref'], 'Lesson Application live Session differs')
    need(selection['assignment'] == instruction['assignment'] == attachment['assignment'],
         'Lesson Application live Assignment differs')
    need(selection['source_cut'] == applicability['source_cut'] == instruction['source_cut'] == cut,
         'Lesson selection/applicability/instruction source cut differs')
    need(selection['instruction_precedence_binding'] == attachment['instruction_precedence_binding'],
         'selected instruction binding differs')
    need(instruction['session_ref'] == attachment['session_ref'] and instruction['veto_lesson_influence'] is False,
         'instruction belongs to another Session or vetoes influence')
    need(payload['applicability_assessment_ref'] == attachment['applicability_binding']['ref'],
         'Lesson Application applicability reference differs')
    need(applicability['lesson'] == lesson and applicability['expired'] is False
         and applicability['posture'] == 'selected' and applicability['conflict_refs'] == [],
         'Lesson Application applicability is not the selected current Lesson')
    matches = [item for item in selection['items'] if item['lesson'] == lesson]
    need(len(matches) == 1 and len(selection['items']) == 1 and matches[0]['posture'] == 'selected'
         and matches[0]['expired'] is False and matches[0]['conflict_refs'] == []
         and matches[0]['applicability_check_binding'] == attachment['applicability_binding'],
         'Lesson Application selection differs or is ambiguous')
    need(payload['lesson_revision_ref'] == lesson['version_ref'], 'Lesson Application revision differs')
    need(payload['intended_influence'] == routing['intended_influence']
         and bool(payload['intended_influence'])
         and payload['application_posture'] == 'candidate-attributed-no-tool-dispatch'
         and routing['authority_effect'] == 'none'
         and routing['source_cut'] == cut
         and routing['scope_ref'] == record['scope_ref']
         and routing['selection_binding'] == attachment['selection_binding']
         and routing['applicability_binding'] == attachment['applicability_binding']
         and routing['instruction_precedence_binding'] == attachment['instruction_precedence_binding'],
         'Lesson Application routing or attributed influence differs')
    need(record['evidence_refs'] == [lesson['version_ref']], 'Lesson Application has unclosed evidence references')
    need(record['relation_refs'] == [{'relation_kind_ref': RELATION, 'direction': 'source',
                                     'counterpart_kind': 'operational-lesson',
                                     'counterpart_ref': lesson['version_ref']}],
         'Lesson Application relation target differs')
    need(payload['conflict_refs'] == payload['override_refs'] == [] and record['successor_refs'] == [],
         'unsupported conflict, override or successor references')
    need(target['version_ref'] in [t['artifact']['version_ref'] for t in proposal['targets']]
         and len([t for t in proposal['targets'] if t['artifact']['version_ref'] == target['version_ref']]) == 1,
         'Lesson Application proposal target missing or ambiguous')
    refs = [{'source_version_ref': target['version_ref'], 'selector': selector,
             'requested_ref': lesson['version_ref'], 'resolved_ref': copy.deepcopy(lesson),
             'posture': 'resolved'}
            for selector in ('/payload/lesson_revision_ref', '/evidence_refs/0',
                             '/relation_refs/0/counterpart_ref')]
    return refs


class LessonApplicationReferences:
    def __init__(self, host):
        self.host = host
        package = type(host).__module__.rsplit('.', 1)[0]
        self.P = importlib.import_module(package + '.protocol')
        self.M = importlib.import_module(package + '.artifact_model')
        self.H = importlib.import_module(package + '.handlers')
        self.G = importlib.import_module(package + '.guard')

    def supports(self, target, message):
        return supported(target, self.host.channel.policy)

    def resolve(self, target, message, post):
        host = self.host; P = self.P
        need(self.supports(target, message), 'unsupported Lesson Application resolution scope')
        policy = host.channel.policy_guard()
        attachment = host.session_attachment
        need(attachment is not None and attachment.host is host and attachment.parent is not host,
             'exact parent Session attachment required')
        attachment.material_guard()
        expected = attachment.expected
        need(policy['application_control']['runtime_identities']['session_ref'] == expected['session_ref'],
             'application grant selects another Session')
        routing = P.frame_parse(host.vault.object_read(policy['application_control']['routing_binding']))
        method = policy['application_control']['method_binding']
        authorization = P.ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
        need(set(routing) == {'schema_version', 'source_cut', 'scope_ref', 'proposal_binding',
                             'method_binding', 'selection_binding', 'applicability_binding',
                             'instruction_precedence_binding', 'intended_influence',
                             'action_bound_refs', 'override_bindings',
                             'authorization_basis_binding', 'authority_effect',
                             'actual_owner_outcome'}
             and routing['schema_version'] == 'lab-lesson-application-routing/v1-candidate'
             and routing['method_binding'] == method
             and routing['authorization_basis_binding'] == P.binding(
                 str(authorization.relative_to(P.ROOT)), authorization.read_bytes())
             and routing['actual_owner_outcome'] is None
             and routing['override_bindings'] == [],
             'Lesson Application selected routing/method/authorization differs')
        manifest = self.G.verify(expected['parent_source_binding']['sha256'])
        need({'path': method['ref'], 'sha256': method['sha256']} in manifest['files'],
             'Lesson Application method bytes are outside selected API Source')
        P.source.original({'path': method['ref'], 'sha256': method['sha256']})
        bounds = routing['action_bound_refs']
        need(type(bounds) is list and all(type(ref) is str for ref in bounds),
             'Lesson Application declared action bounds required')
        resource = attachment.resource
        with resource._lifetime_lock:
            attachment.material_guard()
            need(set(bounds) <= set(resource.bridge.permission().operations),
                 'Lesson Application action bounds exceed live Session delegation')
            attachment.material_guard()
        selected_proposal = P.frame_parse(host.vault.object_read(routing['proposal_binding']))
        need(P.compact(selected_proposal) == P.compact(message),
             'Lesson Application proposal differs from independently selected routing')
        view = host.handlers.view
        need(message['base_cut'] == self.H.cut(view) == expected['source_cut']
             and post is not view.data['projection'] and host.handlers.current(),
             'resolver requires exact pure current source projection')
        selection = P.frame_parse(attachment.material(expected['selection_binding']))
        applicability = P.frame_parse(attachment.material(expected['applicability_binding']))
        instruction = P.frame_parse(attachment.material(expected['instruction_precedence_binding']))
        need(selection['authority_effect'] == applicability['authority_effect'] == instruction['authority_effect'] == 'none',
             'selected parent witnesses claim an authority effect')
        need(len(selection['items']) == 1, 'exactly one actual selected Lesson required')
        lesson = selection['items'][0]['lesson']
        need(lesson['carrier_ref'] == LESSON, 'selected item is not an Operational Lesson')
        subject = host.handlers.resolve_exact(lesson)
        need(subject['effective_state'] in ('admitted-current', 'local-admitted-current')
             and subject['kind'] == 'operational-lesson', 'signed Lesson is not current')
        raw = self.M.record_bytes(view, subject)[0]
        need(P.source.sha(raw) == lesson['byte_sha256']
             and self.M.artifact_ref(view, subject) == lesson
             and P.frame_parse(raw)['scope_ref'] == routing['scope_ref'],
             'signed Lesson bytes/header differ from current selection')
        owner = host.channel.guard()['principal_ref']
        refs = validate_selected(target, message, owner=owner, cut=self.H.cut(view),
                                 attachment=expected, selection=selection,
                                 applicability=applicability, instruction=instruction,
                                 lesson=lesson, routing=routing)
        target_rows = [t for t in message['targets'] if t['artifact']['version_ref'] == target['version_ref']]
        need(len(target_rows) == 1 and target_rows[0]['artifact']['carrier_ref'] == CARRIER,
             'Lesson Application target differs')
        content = target_rows[0]['content']
        original = host.vault.material({'ref': content['content_ref'],
                                        'sha256': content['byte_sha256']})
        need(P.source.sha(original) == target_rows[0]['artifact']['byte_sha256']
             and P.frame_parse(original) == target['record'],
             'Lesson Application original target bytes differ')
        package_root = Path(__file__).resolve().parent
        repository = P.ROOT
        path = package_root / 'lesson_application_references.py'
        need(path.resolve() == Path(__file__).resolve(), 'resolver not installed under its selected package name')
        resolver_binding = P.binding(str(path.relative_to(repository)), path.read_bytes())
        need({'path': resolver_binding['ref'], 'sha256': resolver_binding['sha256']}
             in manifest['files'], 'Lesson Application resolver bytes are outside selected API Source')
        P.source.original({'path': resolver_binding['ref'], 'sha256': resolver_binding['sha256']})
        core = target_rows[0]['decision_core_binding']
        details = {'resolver_binding': resolver_binding,
                   'source_cut': copy.deepcopy(message['base_cut']),
                   'proposal_binding': copy.deepcopy(routing['proposal_binding']),
                   'exact_current_lesson': copy.deepcopy(lesson),
                   'live_parent_session_ref': expected['session_ref'],
                   'selection_binding': copy.deepcopy(expected['selection_binding']),
                   'applicability_binding': copy.deepcopy(expected['applicability_binding']),
                   'instruction_precedence_binding': copy.deepcopy(expected['instruction_precedence_binding']),
                   'resolved_reference_count': len(refs),
                   'tool_dispatches': 0, 'canonical_admission_granted': False,
                   'authority_effect': 'none',
                   'input_bindings': [resolver_binding, copy.deepcopy(routing['proposal_binding']),
                                      copy.deepcopy(core),
                                      copy.deepcopy(expected['selection_binding']),
                                      copy.deepcopy(expected['applicability_binding']),
                                      copy.deepcopy(expected['instruction_precedence_binding'])]}
        attachment.material_guard()
        return refs, details
