"""Pure lesson applicability evaluation; supplied facts confer no authority.

The host must independently resolve the live Session, signed complete inventory,
review dispositions and permission before supplying these facts, and guard all of
them again before exposing a result. This module opens no Session or store, grants
no permission, writes no evidence and creates no Lesson Application.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import copy
from pathlib import Path
from typing import Callable

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Resource
from referencing.jsonschema import DRAFT202012

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
CONTRACTS = HERE.parent / 'lesson-selection-contract-v1'
PROTOCOL = ROOT / 'docs/proposals/0007-lab-integrated-schema-package'
MAX_BYTES = 4194304


class SelectionFault(ValueError):
    """Exact source, schema or closure failure; never silently an empty catalog."""


def require(condition, reason):
    if not condition:
        raise SelectionFault(reason)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def binding(ref, raw):
    return {'ref': ref, 'sha256': sha(raw)}


def parse(raw):
    require(type(raw) is bytes and 0 < len(raw) <= MAX_BYTES, 'bounded original bytes required')
    def pairs(rows):
        result = {}
        for key, value in rows:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    def nonfinite(value):
        raise SelectionFault('nonfinite JSON number')
    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=nonfinite)
    except (UnicodeError, ValueError, RecursionError) as error:
        raise SelectionFault('invalid original JSON') from error


def instant(value):
    require(isinstance(value, str), 'expiry unresolved')
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
        require(result.tzinfo is not None and result.utcoffset() is not None, 'expiry timezone unresolved')
        return result.astimezone(timezone.utc)
    except (ValueError, OverflowError) as error:
        raise SelectionFault('expiry unresolved') from error


def source_guard():
    """Verify this frozen candidate and every selected offline schema dependency."""
    manifest = parse((HERE / 'source-manifest.json').read_bytes())
    rows = manifest['files'] + manifest['input_bindings']
    require(len({row['path'] for row in rows}) == len(rows), 'duplicate source binding')
    for row in rows:
        path = ROOT / row['path']
        require(path.is_relative_to(ROOT) and path.resolve() == path and path.is_file(), 'source path custody differs')
        require(sha(path.read_bytes()) == row['sha256'], 'selected source changed: ' + row['path'])
    require(sha(encoded(rows)) == manifest['source_sha256'], 'source selection digest differs')
    return manifest['source_sha256']


@dataclass(frozen=True)
class ReviewFact:
    """Independently resolved disposition plus its exact original witness."""
    original_binding: dict
    disposition: str
    effective_state: str
    fixture_only: bool


@dataclass(frozen=True)
class LessonFact:
    artifact: dict
    original: bytes
    domain_scope_ref: str
    current: bool
    review: ReviewFact | None
    rule_binding: dict | None
    retention_binding: dict | None
    # One independent assessment per literal exclusion, in original order.
    # None is unresolved; False does not assert that the lesson is generally safe.
    exclusions: tuple[tuple[str, bool | None], ...]
    evidence_bindings: tuple[dict, ...]
    counterevidence_bindings: tuple[dict, ...]


@dataclass(frozen=True)
class ContextFacts:
    """Host-selected facts; constructing this dataclass authenticates nothing."""
    selection_ref: str
    session_ref: str
    assignment: dict
    source_cut: dict
    project_ref: str
    family: str
    source_binding: dict
    instructions: tuple[str, ...]
    tags: tuple[str, ...]
    instruction_veto: bool
    now: datetime
    session_binding: dict
    inventory_binding: dict
    context_basis_binding: dict
    instruction_binding: dict
    lessons: tuple[LessonFact, ...]


@dataclass(frozen=True)
class Evaluation:
    result: dict
    checks: tuple[tuple[dict, bytes], ...]
    applications_created: int = 0
    authority_effect: str = 'none'


class Rules:
    def __init__(self):
        self.source_sha256 = source_guard()
        spec = importlib.util.spec_from_file_location('_lesson_selected_schema_resources', PROTOCOL / 'resources.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        registry = module.build_registry()
        self.schemas = {}
        for name in ('routing', 'applicability', 'domain-profile'):
            schema = parse((CONTRACTS / (name + '.schema.json')).read_bytes())
            registry = registry.with_resource(schema['$id'], Resource.from_contents(schema, default_specification=DRAFT202012))
            self.schemas[name] = schema
        for name in ('lesson-selection', 'common'):
            self.schemas[name] = parse((PROTOCOL / 'schemas' / (name + '.schema.json')).read_bytes())
        self.schemas['lesson'] = parse((ROOT / 'authority/artifact-types/operational-lesson/v1/schema.json').read_bytes())
        self.registry = registry

    def valid(self, name, value):
        validator = Draft202012Validator(self.schemas[name], registry=self.registry, format_checker=FormatChecker())
        try:
            validator.validate(value)
        except Exception as error:
            raise SelectionFault('schema failed: ' + name) from error

    def select(self, routing_raw: bytes, facts: ContextFacts, read: Callable[[dict], bytes]) -> Evaluation:
        require(source_guard() == self.source_sha256, 'candidate source selection changed')
        require(isinstance(facts, ContextFacts) and callable(read), 'selected context facts and exact reader required')
        facts = copy.deepcopy(facts)
        require(isinstance(facts.now, datetime) and facts.now.tzinfo is not None, 'host clock required')
        require(type(facts.instruction_veto) is bool and facts.selection_ref and facts.session_ref, 'bounded Session facts required')
        require(len(facts.lessons) <= 1000, 'complete lesson inventory exceeds bound')
        require(len(facts.instructions) == len(set(facts.instructions)) and len(facts.tags) == len(set(facts.tags)), 'duplicate context facts')
        total = len(routing_raw)
        cache = {}
        def original_bytes(b):
            nonlocal total
            require(isinstance(b, dict) and set(b) == {'ref', 'sha256'}, 'exact binding required')
            key = (b['ref'], b['sha256'])
            if key not in cache:
                try:
                    raw = read(dict(b))
                except Exception as error:
                    raise SelectionFault('original witness unresolved') from error
                require(type(raw) is bytes and 0 < len(raw) <= MAX_BYTES and sha(raw) == b['sha256'], 'original binding changed or unresolved')
                total += len(raw)
                require(total <= MAX_BYTES, 'complete input exceeds bound')
                cache[key] = raw
            return cache[key]
        def original(b):
            return parse(original_bytes(b))
        def exact(b, value, reason):
            require(original(b) == value, reason)
        routing = parse(routing_raw)
        self.valid('routing', routing)
        require(routing['source_cut'] == facts.source_cut and routing['assignment'] == facts.assignment, 'routing cut or Assignment differs')
        for field, selected in [('session_binding', facts.session_binding), ('inventory_binding', facts.inventory_binding),
                                ('instruction_precedence_binding', facts.instruction_binding)]:
            require(routing[field] == selected, 'routing independent binding differs: ' + field)
        refs = [item.artifact for item in facts.lessons]
        keys = [encoded(ref) for ref in refs]
        require(len(keys) == len(set(keys)), 'duplicate current lesson revision')
        identities = [(ref['scope_ref'], ref['identity_ref']) for ref in refs]
        require(len(identities) == len(set(identities)), 'multiple current versions of one lesson')
        require([row['lesson'] for row in routing['lessons']] == refs, 'routing must cover complete ordered current inventory')
        exact(facts.inventory_binding, {'source_cut': facts.source_cut, 'lessons': refs, 'complete': True, 'authority_effect': 'none'}, 'independent inventory differs')
        exact(facts.session_binding, {'session_ref': facts.session_ref, 'assignment': facts.assignment,
                                    'source_cut': facts.source_cut, 'authority_effect': 'none'}, 'selected Session witness differs')
        exact(facts.instruction_binding, {'session_ref': facts.session_ref, 'assignment': facts.assignment,
              'source_cut': facts.source_cut, 'instruction_refs': list(facts.instructions),
              'veto_lesson_influence': facts.instruction_veto, 'authority_effect': 'none'}, 'independent instruction precedence differs')
        profile = original(routing['domain_profile_binding'])
        self.valid('domain-profile', profile)
        require(profile['scope_ref'] == facts.project_ref and profile['source_cut'] == facts.source_cut
                and profile['context_basis_binding'] == facts.context_basis_binding, 'domain profile context differs')
        require(profile['selection_method_binding'] == binding('lesson-selection-rules-v1/rules.py', Path(__file__).read_bytes()), 'selection method identity differs')
        exact(facts.context_basis_binding, {'session_ref': facts.session_ref, 'assignment': facts.assignment,
              'source_cut': facts.source_cut, 'project_ref': facts.project_ref, 'family': facts.family,
              'source_binding': facts.source_binding, 'tags': list(facts.tags), 'authority_effect': 'none'}, 'independent context basis differs')
        original_bytes(facts.source_binding)
        items = []
        evidence = []
        eligible = []
        for fact, route in zip(facts.lessons, routing['lessons']):
            total += len(fact.original)
            require(total <= MAX_BYTES and fact.current is True, 'unresolved or noncurrent lesson inventory')
            require(sha(fact.original) == fact.artifact['byte_sha256'], 'lesson original digest differs')
            body = parse(fact.original)
            self.valid('lesson', body)
            require(body['node_id'] == fact.artifact['identity_ref'] and body['scope_ref'] == fact.domain_scope_ref,
                    'lesson original identity or domain scope differs')
            payload = body['payload']
            for field, selected in [('review_binding', None if fact.review is None else fact.review.original_binding),
                                    ('applicability_rule_binding', fact.rule_binding)]:
                require(route[field] == selected, 'lesson independent route differs: ' + field)
            require([row[0] for row in fact.exclusions] == payload['exclusions']
                    and all(type(row[1]) is bool or row[1] is None for row in fact.exclusions), 'literal exclusion assessment closure differs')
            require([b['ref'] for b in fact.evidence_bindings] == payload['evidence_refs'], 'lesson evidence closure differs')
            require([b['ref'] for b in fact.counterevidence_bindings] == payload['counterevidence_refs'], 'lesson counterevidence closure differs')
            require(len(payload['counterevidence_refs']) == len(set(payload['counterevidence_refs'])), 'ambiguous repeated counterevidence')
            for b in fact.evidence_bindings + fact.counterevidence_bindings:
                original_bytes(b)
            posture, reason, expired, rule = 'selected', 'exact-reviewed-current-applicable', False, None
            def block(message):
                return 'blocked', message
            if fact.review is None:
                posture, reason = block('exact-durable-review-absent')
            else:
                review = fact.review
                require(type(review.fixture_only) is bool, 'independent review fixture posture unresolved')
                exact(review.original_binding, {'lesson': fact.artifact, 'source_cut': facts.source_cut,
                      'domain_scope_ref': fact.domain_scope_ref, 'disposition': review.disposition,
                      'effective_state': review.effective_state, 'fixture_only': review.fixture_only,
                      'authority_effect': 'none'}, 'review original and independent disposition differ')
                if {'disposition': review.disposition, 'effective_state': review.effective_state,
                    'fixture_only': review.fixture_only} not in profile['reviewed_use_postures']:
                    posture, reason = block('unsupported-reviewed-use-posture')
            if posture == 'selected' and (payload['status'] not in profile['supported_lesson_statuses']
                    or payload['retention_policy_ref'] not in profile['supported_retention_policy_refs']):
                posture, reason = block('unsupported-status-or-retention-policy')
            if posture == 'selected':
                if fact.retention_binding is None:
                    posture, reason = block('retention-witness-unresolved')
                else:
                    policy = original(fact.retention_binding)
                    require(policy == {'policy_ref': payload['retention_policy_ref'], 'retain_project_evidence': True,
                            'exclude_session_memory': True, 'authority_effect': 'none'}, 'retention original differs')
            if posture == 'selected':
                if fact.rule_binding is None:
                    posture, reason = block('applicability-rule-unresolved')
                else:
                    rule = original(fact.rule_binding)
                    self.valid('applicability', rule)
                    require(rule['lesson'] == fact.artifact and rule['source_cut'] == facts.source_cut, 'applicability lesson identity or cut differs')
                    require([row['binding'] for row in rule['counterevidence']] == list(fact.counterevidence_bindings), 'rule counterevidence coverage differs')
                    for row in rule['counterevidence']:
                        exact(row['assessment_binding'], {'lesson': fact.artifact, 'source_cut': facts.source_cut,
                              'counterevidence_binding': row['binding'], 'posture': row['posture'],
                              'authority_effect': 'none'}, 'counterevidence assessment differs')
            if posture == 'selected':
                try:
                    expired = facts.now >= instant(payload['expires_at'])
                    if expired:
                        posture, reason = 'omitted', 'expired'
                except SelectionFault:
                    posture, reason = block('expiry-unresolved')
            if posture == 'selected':
                if rule['project_ref'] != facts.project_ref or facts.project_ref not in payload['scope_refs']:
                    posture, reason = 'omitted', 'project-scope-excluded'
                elif rule['family'] != facts.family or payload['applicability'] != facts.family:
                    posture, reason = 'omitted', 'family-excluded'
                elif rule['source_binding'] != facts.source_binding:
                    posture, reason = 'omitted', 'source-version-excluded'
                elif any(row[1] is True for row in fact.exclusions) or set(rule['excluded_tags']) & set(facts.tags):
                    posture, reason = 'omitted', 'explicit-exclusion'
                elif any(row[1] is None for row in fact.exclusions):
                    posture, reason = block('literal-exclusion-unresolved')
                elif facts.instruction_veto or 'leave-source-unchanged' in facts.instructions or not set(rule['required_instruction_refs']) <= set(facts.instructions):
                    posture, reason = 'omitted', 'current-instruction-precedence'
                elif any(row['posture'] == 'contradicts-use' for row in rule['counterevidence']):
                    posture, reason = 'omitted', 'counterevidence-contradicts-use'
                elif any(row['posture'] == 'unresolved' for row in rule['counterevidence']):
                    posture, reason = block('counterevidence-unresolved')
            items.append({'lesson': fact.artifact, 'posture': posture, 'reason': reason, 'expired': expired, 'conflict_refs': []})
            evidence.append({'lesson': fact.artifact, 'source_cut': facts.source_cut, 'review_binding': route['review_binding'],
                             'rule_binding': fact.rule_binding, 'evidence_bindings': list(fact.evidence_bindings),
                             'counterevidence_bindings': list(fact.counterevidence_bindings),
                             'literal_exclusions': [[text, verdict] for text, verdict in fact.exclusions], 'authority_effect': 'none'})
            if posture == 'selected':
                eligible.append((len(items)-1, rule))
        for position, (a, left) in enumerate(eligible):
            for b, right in eligible[position+1:]:
                if left['family'] == right['family'] and left['influence_ref'] != right['influence_ref']:
                    items[a]['conflict_refs'].append(items[b]['lesson'])
                    items[b]['conflict_refs'].append(items[a]['lesson'])
        checks = []
        for row, witness in zip(items, evidence):
            if row['conflict_refs']:
                row.update(posture='blocked', reason='incompatible-influence-with-another-applicable-lesson')
            raw = encoded({**witness, **row, 'applications_created': 0})
            selected = binding('lesson-check:' + facts.selection_ref + ':' + sha(raw), raw)
            row['applicability_check_binding'] = selected
            checks.append((selected, raw))
        result = {'schema_version': 'lab-lesson-selection/v1-candidate', 'selection_ref': facts.selection_ref,
                  'session_ref': facts.session_ref, 'assignment': facts.assignment, 'source_cut': facts.source_cut,
                  'items': items, 'instruction_precedence_binding': facts.instruction_binding,
                  'claim_ceiling': 'Pure selection from supplied facts only. No Application, effectiveness, permission, admission or live Session qualification.',
                  'authority_effect': 'none'}
        self.valid('lesson-selection', result)
        require(len(encoded(result)) + sum(len(raw) for _, raw in checks) <= MAX_BYTES, 'complete output exceeds bound')
        require(source_guard() == self.source_sha256, 'candidate source changed before return')
        return Evaluation(result, tuple(checks))
