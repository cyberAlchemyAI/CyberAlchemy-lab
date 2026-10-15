"""Actual host selection for lesson.select; no caller-selected facts or authority."""
import copy
import importlib
import importlib.util
from pathlib import Path
import sys
from datetime import datetime, timezone

from jsonschema import Draft202012Validator, FormatChecker

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
RULES = HERE.parent / 'lesson-selection-rules-v2'
RULE_SOURCE = 'ab4ea6a69df268ca2cc422d38128cc87ba282ad11b52d857317df163e8c7e6e6'
NAME = '_cal_lesson_selection_rules_v2'
if NAME not in sys.modules:
    spec = importlib.util.spec_from_file_location(NAME, RULES / 'rules.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[NAME] = module
    spec.loader.exec_module(module)
E = sys.modules[NAME]
assert Path(E.__file__).resolve() == RULES / 'rules.py'


def require(value, reason):
    if not value:
        raise ValueError(reason)


class LessonHost:
    def __init__(self, host, expected_host_source):
        module = sys.modules.get(type(host).__module__)
        require(module is not None and getattr(module, 'Service', None) is type(host), 'actual selected Service required')
        path = Path(module.__file__).resolve()
        require(path == HERE.parent / 'api-v67/service.py', 'unselected lesson host implementation')
        self.package = type(host).__module__.rsplit('.', 1)[0]
        self.P = importlib.import_module(self.package + '.protocol')
        self.MT = importlib.import_module(self.package + '.machine_transport')
        self.C = importlib.import_module(self.package + '.custody_context_sessions')
        self.G = importlib.import_module(self.package + '.guarded_reads')
        self.H = importlib.import_module(self.package + '.handlers')
        self.A = importlib.import_module(self.package + '.auth')
        self.W = importlib.import_module(self.package + '.workspace')
        self.host = host
        require(type(host.channel) is self.MT.MachinePeer and host.channel.service is host, 'actual authenticated Machine dispatcher required')
        self.peer = host.channel
        self.parent = self.peer.owner
        require(type(self.parent) is type(host) and type(self.parent.channel) is self.A.ReaderChannel, 'actual authenticated parent host required')
        self.resource = self.peer.resource
        self.view = host.handlers.view
        self.source = self.view.custody_signed_sources
        self.originals = {}
        self.generated = {}
        self.rule_engine = E.Rules()
        require(self.rule_engine.source_sha256 == RULE_SOURCE, 'unselected lesson rule source')
        selected = {'path': (path.parent/'source-manifest.json').relative_to(ROOT).as_posix(),
                    'sha256': E.sha((path.parent/'source-manifest.json').read_bytes())}
        require(expected_host_source == selected, 'independent host source selection differs')
        self.host_source = selected
        self.guard()
        selected = self.peer.policy_guard().get('lesson_control')
        require(selected is not None, 'independent lesson read permission is absent')
        self.plan_binding = copy.deepcopy(selected['plan_binding'])
        self.plan_raw = self.host.vault.material(self.plan_binding)
        self.plan = E.parse(self.plan_raw)
        schema = E.parse((HERE/'plan.schema.json').read_bytes())
        Draft202012Validator(schema, registry=self.rule_engine.registry, format_checker=FormatChecker()).validate(self.plan)

    def guard(self):
        self.peer.guard()
        self.host.schemas.guard()
        self.host.vault.guard()
        require(self.peer.service is self.host and self.peer.owner is self.parent
                and self.parent.handlers.view is self.view and self.host.schemas is self.parent.schemas,
                'actual host or shared source selection changed')
        require(type(self.parent.sessions) is self.C.ContextSessions and not self.parent.sessions.closed
                and self.parent.sessions.live.get(self.peer.row['session_ref']) is self.resource
                and type(self.resource) is self.C.LiveReader and self.resource.source is self.source
                and self.resource.bridge is self.parent.sessions.bridge,
                'foreign, disposed or reconstructed Session refused')
        self.resource.guard()
        row = self.parent.sessions.selected(self.peer.row['session_ref'])
        context = self.peer.context
        require(row['posture'] == 'active' and row['source_cut'] == self.H.cut(self.view)
                and row['session_ref'] == self.resource.session['node_id'] == context['session_ref']
                and row['agent_instance_ref'] == self.resource.agent['node_id'] == context['agent_instance_ref']
                and row['assignment'] == self.peer.row['assignment']
                and row['assignment']['version_ref'] == context['assignment_ref'], 'live Session source or Actor differs')
        require(self.resource.agent['owner_ref'] == context['principal_ref']
                and self.resource.agent['payload']['accountable_principal_ref'] == context['principal_ref']
                and context['role_assignment_bindings'] == [] and context['limits']['max_actions'] == 0,
                'Machine accountability or read-only scope differs')
        require('lesson.select' in self.peer.policy['allowed_operations']
                and 'lesson.select' in self.parent.channel.policy_guard()['allowed_operations'], 'parent has not explicitly granted lesson read')
        require(E.source_guard() == RULE_SOURCE, 'rule implementation changed')
        if hasattr(self, 'plan_binding'):
            require(self.peer.policy_guard().get('lesson_control', {}).get('plan_binding') == self.plan_binding
                    and self.host.vault.material(self.plan_binding) == self.plan_raw, 'independent lesson plan changed')
        return row

    def read(self, selected):
        key = (selected['ref'], selected['sha256'])
        if key in self.generated:
            return self.generated[key]
        if selected['ref'] in self.host.vault.inputs:
            return self.host.vault.material(selected)
        if key in self.originals:
            return self.originals[key]
        baseline = self.view.data['baseline']['materials']
        require(baseline.get(selected['ref']) == selected['sha256'], 'lesson reference is outside independently selected original material closure')
        raw = self.P.source.original({'path': selected['ref'], 'sha256': selected['sha256']})
        require(E.sha(raw) == selected['sha256'], 'original source binding changed')
        return raw

    def generated_binding(self, label, value):
        raw = E.encoded(value)
        selected = E.binding(label+':'+E.sha(raw), raw)
        self.generated[(selected['ref'], selected['sha256'])] = raw
        return selected

    def original_ref(self, ref):
        matches = [s for s in self.view.subjects.values()
                   if ref in (s['identity'], s['version_ref']) and s['effective_state'] in self.C.D.reader.adapter.CURRENT]
        if matches:
            require(len(matches) == 1, 'ambiguous current lesson dependency')
            subject = matches[0]
            raw, _, _, _ = self.C.D.reader.adapter.model.record_bytes(self.view, subject)
            self.view.handle.operations.validate_record(subject['record'], subject['carrier_ref'], self.view.data['projection'])
            self.C.EL.no_private_memory(E.parse(raw))
            selected = E.binding(ref, raw)
            self.originals[(ref, selected['sha256'])] = raw
            return selected
        selected = self.host.vault.inputs.get(ref)
        if selected is not None:
            selected = {'ref': ref, 'sha256': selected['sha256']}
            self.read(selected)
            return selected
        require(ref in self.view.data['baseline']['materials'], 'unresolved lesson evidence or counterevidence')
        selected = {'ref': ref, 'sha256': self.view.data['baseline']['materials'][ref]}
        self.read(selected)
        return selected

    def inventory(self):
        # Use declared semantics and projected kinds independently. An unknown
        # current Lesson is a closure failure, never a zero-sized catalog.
        rows = []
        contracts = self.view.data['projection']['contracts']
        for subject in sorted(self.view.subjects.values(), key=lambda item: item['version_ref']):
            if subject['effective_state'] not in self.C.D.reader.adapter.CURRENT:
                continue
            contract = contracts.get(subject.get('carrier_ref'))
            if not ((contract is not None and contract.get('semantic_kind') == 'operational-lesson')
                    or subject['kind'] == 'operational-lesson'):
                continue
            require(contract is not None and subject['carrier_ref'] == 'cal.artifact-type.operational-lesson/v1'
                    and contract['semantic_kind'] == 'operational-lesson'
                    and contract['lifecycle_state'] == 'admitted-current' and contract['schema_selector'] is None,
                    'unresolved current Lesson carrier contract')
            require(self.view.data['baseline']['materials'].get(contract['schema_path']) == contract['schema_sha256'],
                    'Lesson schema is outside exact captured closure')
            raw, _, _, _ = self.C.D.reader.adapter.model.record_bytes(self.view, subject)
            self.view.handle.operations.validate_record(subject['record'], subject['carrier_ref'], self.view.data['projection'])
            self.C.EL.no_private_memory(E.parse(raw))
            artifact = self.C.D.reader.adapter.model.artifact_ref(self.view, subject)
            rows.append((subject, artifact, raw))
        require(len(rows) <= 1000, 'complete Lesson inventory exceeds bound')
        return rows

    def calculate(self, message, request, outer):
        require(message['source_cut'] == outer == self.source.source_cut == self.plan['source_cut'], 'lesson source cut differs')
        require(message['assignment'] == self.plan['assignment'] == self.peer.row['assignment']
                and message['work'] == self.plan['work'] and message['coordination_context'] == self.plan['coordination_context'],
                'lesson Assignment, Work or Coordination Context differs')
        require(message['actor'] == self.host.sessions.bridge.actor(), 'lesson Actor differs from authenticated Machine')
        inventory = self.inventory()
        artifacts = [a for _, a, _ in inventory]
        require([row['lesson'] for row in self.plan['lessons']] == artifacts, 'lesson plan must cover complete current inventory exactly')
        known = {a['version_ref']: a for a in artifacts}
        preflight = copy.deepcopy(message)
        preflight['selectors'] = []
        for artifact in message['selectors']:
            if artifact['version_ref'] in known:
                require(artifact == known[artifact['version_ref']] and not {artifact['identity_ref'], artifact['version_ref']} & set(message['exclusions']), 'requested Lesson selector is changed or excluded')
            else:
                preflight['selectors'].append(artifact)
        with self.G.participation_snapshot(self.source, self.C.D) as snapshot:
            authority = self.C.EL.SessionEligibility(snapshot, self.host.sessions.bridge.permission, self.host.sessions.bridge.permission_guard)
            eligibility = authority.context_plan(preflight, message['actor'], self.plan['profile'])
        profile = eligibility['profile'].artifact
        require(self.resource.agent['payload']['profile_ref'] == profile['version_ref'], 'actual Machine Profile differs from participation')
        project = E.parse(eligibility['work'].original)['payload']['project_ref']
        require(project == self.plan['project_ref'], 'independent lesson Project differs from current Work')
        instruction = E.parse(self.read(self.plan['instruction_policy_binding']))
        require(set(instruction) == set('schema_version source_cut assignment work coordination_context instruction_refs tags veto_lesson_influence authority_effect actual_owner_outcome'.split())
                and instruction['schema_version'] == 'lab-lesson-instruction-policy/v1-candidate'
                and instruction['source_cut'] == outer and instruction['assignment'] == message['assignment']
                and instruction['work'] == message['work'] and instruction['coordination_context'] == message['coordination_context']
                and instruction['authority_effect'] == 'none' and instruction['actual_owner_outcome'] is None,
                'independent instruction policy context differs')
        require(type(instruction['veto_lesson_influence']) is bool
                and isinstance(instruction['instruction_refs'], list) and isinstance(instruction['tags'], list)
                and len(instruction['instruction_refs']) <= 1000 and len(instruction['tags']) <= 1000
                and all(isinstance(x, str) and x for x in instruction['instruction_refs'] + instruction['tags']), 'instruction policy bounds differ')
        self.read(self.plan['source_binding'])
        facts = []
        for (subject, artifact, raw), planned in zip(inventory, self.plan['lessons']):
            body = E.parse(raw)
            review = None
            if planned['review_binding'] is not None:
                require(planned['review_disposition'] is not None and type(planned['fixture_only']) is bool, 'independent review disposition unresolved')
                review = E.ReviewFact(planned['review_binding'], planned['review_disposition'], subject['effective_state'], planned['fixture_only'])
            else:
                require(planned['review_disposition'] is None and planned['fixture_only'] is None, 'missing review cannot invent a disposition')
            exclusions = []
            for row in planned['exclusions']:
                if row['assessment_binding'] is None:
                    require(row['excluded'] is None, 'missing exclusion assessment cannot assert eligibility')
                else:
                    expected = {'lesson': artifact, 'source_cut': outer, 'exclusion_text': row['text'],
                                'excluded': row['excluded'], 'authority_effect': 'none'}
                    require(E.parse(self.read(row['assessment_binding'])) == expected, 'exact independent exclusion assessment differs')
                exclusions.append((row['text'], row['excluded']))
            fact = E.LessonFact(artifact, raw, body['scope_ref'], True, review, planned['applicability_rule_binding'],
                planned['retention_binding'], tuple(exclusions),
                tuple(self.original_ref(ref) for ref in body['payload']['evidence_refs']),
                tuple(self.original_ref(ref) for ref in body['payload']['counterevidence_refs']),
                bool({artifact['identity_ref'], artifact['version_ref']} & set(message['exclusions'])))
            facts.append(fact)
        session = {'session_ref': self.peer.context['session_ref'], 'assignment': message['assignment'], 'source_cut': outer, 'authority_effect': 'none'}
        session_b = self.generated_binding('session-facts', session)
        inventory_b = self.generated_binding('lesson-inventory', {'source_cut': outer, 'lessons': artifacts, 'complete': True, 'authority_effect': 'none'})
        instruction_b = self.generated_binding('lesson-instruction-precedence', {**session,
            'instruction_refs': instruction['instruction_refs'], 'veto_lesson_influence': instruction['veto_lesson_influence']})
        basis_b = self.generated_binding('lesson-context-basis', {**session, 'project_ref': project, 'family': self.plan['family'],
            'source_binding': self.plan['source_binding'], 'tags': instruction['tags']})
        domain = {**self.plan['domain_profile'], 'schema_version': 'lab-lesson-selection-domain/v1-candidate',
                  'scope_ref': project, 'source_cut': outer, 'context_basis_binding': basis_b,
                  'selection_method_binding': E.binding('lesson-selection-rules-v2/rules.py', (RULES/'rules.py').read_bytes()),
                  'authority_effect': 'none', 'actual_owner_outcome': None}
        domain_b = self.generated_binding('lesson-domain-profile', domain)
        routing = {'schema_version': 'lab-lesson-selection-routing/v1-candidate', 'source_cut': outer, 'assignment': message['assignment'],
            'session_binding': session_b, 'instruction_precedence_binding': instruction_b, 'inventory_binding': inventory_b,
            'domain_profile_binding': domain_b, 'lessons': [{'lesson': f.artifact, 'review_binding': None if f.review is None else f.review.original_binding,
            'applicability_rule_binding': f.rule_binding} for f in facts], 'authority_effect': 'none', 'actual_owner_outcome': None}
        selected = E.ContextFacts('lesson-selection:'+self.peer.context['session_ref']+':'+request['sha256'], self.peer.context['session_ref'],
            message['assignment'], outer, project, self.plan['family'], self.plan['source_binding'], tuple(instruction['instruction_refs']),
            tuple(instruction['tags']), instruction['veto_lesson_influence'], datetime.now(timezone.utc),
            session_b, inventory_b, basis_b, instruction_b, tuple(facts))
        return self.rule_engine.select(E.encoded(routing), selected, self.read)

    def select(self, message, request, outer, raw, effective, ceiling):
        require(self.host.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:context-query:v1-candidate', message)
                and self.P.frame_parse(raw) == message and message['budget']['max_actions'] == 0, 'original lesson Context Query differs')
        try:
            with self.parent.sessions.mutex:
                self.guard()
                effective = min(effective, self.resource.expires)
                bridge = self.parent.sessions.bridge
                require(bridge.channel is self.parent.channel and self.resource.bridge is bridge,
                        'live Session parent reader channel differs')
                with self.C.BOUNDARIES.read_scope(self.source, self.C.EL, bridge, producer=self.C.D,
                        package_checks=[(self.C.D.preflight, self.C.DELIVERY_PIN)]):
                    self.peer.guard()
                    evaluated = self.calculate(message, request, outer)
                self.guard()
                require(self.A.now() < effective, 'strict lesson deadline expired')
                result = copy.deepcopy(evaluated.result)
                require(len(self.P.compact(result)) + 4096 <= ceiling, 'complete lesson result exceeds effective output budget')
                # These are bounded derived evidence objects, never domain writes
                # or operation claims. Writes happen after the full source exit.
                for row, (_, check_raw) in zip(result['items'], evaluated.checks):
                    selected = self.host.vault.object(check_raw)
                    require(selected['sha256'] == row['applicability_check_binding']['sha256'], 'materialized applicability bytes differ')
                    row['applicability_check_binding'] = selected
                result['claim_ceiling'] = 'Actual authenticated candidate lesson read from independently selected current source and live Session. No Application, effectiveness, action permission, canonical admission or genuine owner outcome.'
                require(self.host.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:lesson-selection:v1-candidate', result), 'original Lesson Selection output invalid')
                self.host.vault.object(self.P.compact(result))
                self.guard()
                require(self.A.now() < effective, 'lesson deadline expired before exposure')
                return result
        finally:
            self.originals.clear()
            self.generated.clear()
