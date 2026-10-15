"""W06 scoped drafting and explicit expiry, instruction, conflict and review selection."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from adapter import *
from evaluator import timestamp

RETENTION = 'protocol:W06-retain-project-evidence-exclude-session-notes@1'
FAMILY = 'hypothesis-inline-candidate-preparation'
PREDICTION = 'The exact inline-only repair produces thirteen schema-valid preparation records and preserves original source bytes.'
CAUSAL_CEILING = 'One controlled later application only; corrected preparation had succeeded before this lesson. No general benefit or confirmed causal effectiveness.'


@dataclass(frozen=True)
class ReviewedLesson:
    revision_ref: str
    original_sha256: str
    disposition: str
    source_head: str
    scope_ref: str
    review_original_ref: str
    effective_state: str
    fixture_only: bool


@dataclass(frozen=True)
class Applicability:
    family: str
    effect: str
    source_sha256: str
    project_ref: str
    required_instruction: str
    exclusion_tags: frozenset[str]
    counterevidence_posture: str


@dataclass(frozen=True)
class CaseContext:
    session_ref: str
    project_ref: str
    task_ref: str
    family: str
    source_sha256: str
    instruction_effects: frozenset[str]
    tags: frozenset[str]
    source_head: str
    context_view_ref: str
    ontology_view_ref: str


@dataclass(frozen=True)
class Selection:
    original_ref: str
    selected_refs: tuple[str, ...]
    conflicts: tuple[tuple[str, str], ...]
    context: CaseContext


class LessonService:
    def __init__(self, sources, *, review_reader):
        require(isinstance(sources, CandidateSources) and callable(review_reader), 'trusted lesson source/review readers required')
        self.e, self.review_reader = sources, review_reader
        self.rules = {}
        self.selections = {}
        self.selection_rules = {}

    def exact_review(self, ref):
        review = self.review_reader(ref)
        if not isinstance(review, ReviewedLesson):
            return None
        original = parse(self.e.original(review.review_original_ref))
        require(original['lesson_ref'] == review.revision_ref and original['lesson_sha256'] == review.original_sha256
            and original['source_head'] == review.source_head and original['scope_ref'] == review.scope_ref
            and original['disposition'] == review.disposition and original['fixture_only'] == review.fixture_only,
            'review original bytes differ from trusted durable disposition')
        return review

    def draft(self):
        e = self.e
        w = e.W05_refs
        observation = e.get(w['observation'], 'operational-observation')
        assessment = e.get(w['assessment'], 'failure-assessment')
        source_action = e.get(w['action'], 'agent-action')
        require(assessment['payload']['cause_hypothesis_refs'] and e.get(w['cause'])['payload']['disposition'] == 'open', 'source cause posture changed')
        original = parse(e.original(e.manifest_ref))
        require(original['controlled'] and original['failed_preparations'] == 1 and original['observations'][1]['result']['validated_records'] == 13, 'attributable source observation changed')
        reflection = e.put(e.make('agent-reflection', 'inline-preparation-reflection', {
            'source_session_ref': source_action['payload']['session_ref'], 'source_action_refs': [w['action']],
            'observation_refs': [w['observation']], 'interpretation': 'The retained builder attempted an inline Hypothesis role outside its carrier schema; the corrected builder prepared successfully in a separate controlled run.',
            'repair_hypothesis': 'Replace only the unsupported Hypothesis inline role with the current carrier-supported Evidence Set role; keep unrelated semantics unchanged.',
            'counterevidence_refs': [e.manifest_ref], 'disposition': 'candidate-scoped-reflection'},
            ('derives-from','source','failure-assessment',w['assessment'])))
        value = e.make('operational-lesson', 'inline-role-preflight', {
            'lesson_statement': 'Before preparing this Hypothesis carrier, choose its declared inline Evidence Set role; a global Experiment Design tests-hypothesis connection uses its separate typed relation contract.',
            'scope_refs': list(dict.fromkeys([SCOPE, e.scope])), 'applicability': FAMILY,
            'exclusions': ['production operation', 'another schema/version or source family', 'automatic semantic or performance acceptance'],
            'predicted_benefit': PREDICTION, 'falsifier': 'The exact inline-only repair remains schema-invalid, changes unrelated source bytes, or fails to prepare thirteen validated records.',
            'evidence_refs': [reflection,w['assessment'],w['observation']],
            'counterevidence_refs': [e.manifest_ref],
            'retention_policy_ref': RETENTION, 'expires_at': utc(e.host.now[0]+3600),
            'classification_assignment_refs': [], 'status': 'candidate'},
            ('derives-from','source','agent-reflection',reflection))
        lesson = e.put(value)
        self.rules[lesson] = Applicability(FAMILY, 'inline-only-repair', e.sources[OLD], SCOPE,
            'allow-controlled-source-repair', frozenset({'production','different-carrier'}), 'limits-causality-not-this-repair')
        e.edge('reflection-source-assessment','derives-from',reflection,w['assessment'],{'derivation_role':'observed-preparation-reflection'})
        e.edge('reflection-source-observation','derives-from',reflection,w['observation'],{'derivation_role':'original-controlled-manifest'})
        e.edge('lesson-reflection','derives-from',lesson,reflection,{'derivation_role':'scoped-repair-hypothesis'})
        e.edge('lesson-source-assessment','derives-from',lesson,w['assessment'],{'derivation_role':'independent-failure-assessment'})
        e.blob('retention-policy.json', encoded({'policy_ref':RETENTION,'owner':'scoped Project state and original source artifacts',
            'retain':['immutable lesson revisions','assessed observations','counterevidence','superseded review/disposition evidence'],
            'exclude':['Session short memory','private signing keys','unselected private sources'],
            'at_expiry':'exclude from current selection; preserve evidence without automatic deletion',
            'authority_effect':'none','actual_owner_outcome':None}))
        return reflection, lesson

    def register_rule(self, ref, rule):
        self.e.get(ref,'operational-lesson')
        require(isinstance(rule,Applicability) and ref not in self.rules, 'exact host applicability rule required')
        self.rules[ref] = rule

    def select(self, refs, context):
        e = self.e
        e.check()
        require(isinstance(context,CaseContext) and context.session_ref == e.host.session.session_ref, 'current later Session context required')
        require(context.source_head == e.host.status['head'] and context.project_ref == SCOPE, 'lesson selection Project/cut differs')
        require(refs and len(refs) == len(set(refs)), 'nonempty unique lesson revisions required')
        rows = []; eligible = []
        for ref in refs:
            v = e.get(ref,'operational-lesson'); p = v['payload']; reason = None
            rule = self.rules.get(ref); review = self.exact_review(ref)
            if not isinstance(review,ReviewedLesson) or review.revision_ref != ref or review.original_sha256 != e.records[ref][1]:
                reason = 'exact-durable-review-absent-or-changed'
            elif not review.fixture_only or review.disposition != 'reviewed-for-controlled-use' or review.effective_state != 'local-admitted-current':
                reason = 'only-current-exact-owned-fixture-review-supported'
            elif review.source_head != context.source_head or review.scope_ref != e.scope:
                reason = 'review-current-cut-or-scope-differs'
            elif p['status'] != 'candidate' or p['retention_policy_ref'] != RETENTION:
                reason = 'unsupported-status-or-retention-policy'
            elif rule is None:
                reason = 'applicability-rule-unresolved'
            else:
                try:
                    if e.host.now[0] >= timestamp(p['expires_at']): reason = 'expired'
                except Exception:
                    reason = 'expiry-unresolved'
                if reason is None:
                    if rule.project_ref != context.project_ref or context.project_ref not in p['scope_refs']: reason = 'project-scope-excluded'
                    elif rule.family != context.family or p['applicability'] != context.family: reason = 'family-excluded'
                    elif rule.source_sha256 != context.source_sha256: reason = 'source-version-excluded'
                    elif rule.exclusion_tags & context.tags: reason = 'explicit-exclusion'
                    elif rule.required_instruction not in context.instruction_effects or 'leave-source-unchanged' in context.instruction_effects: reason = 'current-instruction-precedence'
                    elif rule.counterevidence_posture == 'contradicts-this-repair': reason = 'counterevidence-contradicts-use'
                    elif rule.counterevidence_posture not in {'limits-causality-not-this-repair','none-observed'}: reason = 'counterevidence-unresolved'
            rows.append({'lesson_ref':ref,'review_original_ref':review.review_original_ref if review else None,
                'disposition':'excluded' if reason else 'eligible','reason':reason or 'exact-reviewed-current-applicable',
                'counterevidence_refs':p['counterevidence_refs'],'applied':False})
            if reason is None: eligible.append(ref)
        conflicts = []
        for i, a in enumerate(eligible):
            for b in eligible[i+1:]:
                if self.rules[a].family == self.rules[b].family and self.rules[a].effect != self.rules[b].effect:
                    conflicts.append((a,b))
        conflicted = {r for pair in conflicts for r in pair}
        for row in rows:
            if row['lesson_ref'] in conflicted:
                row.update(disposition='blocked-conflict',reason='incompatible-influence-with-another-applicable-lesson')
        selected = tuple(r for r in eligible if r not in conflicted)
        detail = {'schema_version':'lab-W06-lesson-selection/v1-candidate','authority_effect':'none','actual_owner_outcome':None,
            'session_ref':context.session_ref,'project_ref':context.project_ref,'task_ref':context.task_ref,
            'source_head':context.source_head,'context_view_ref':context.context_view_ref,'ontology_view_ref':context.ontology_view_ref,
            'selected_refs':list(selected),'rows':rows,'conflicts':[list(pair) for pair in conflicts],'applications_created':0,
            'instruction_precedence':'current explicit instruction and host action permission precede non-governing lesson advice'}
        token = e.blob('selection-'+str(len(self.selections)+1)+'.json',encoded(detail))
        result = Selection(token,selected,tuple(conflicts),context)
        self.selections[token] = result
        self.selection_rules[token] = {ref:self.rules[ref] for ref in selected}
        return result

    def selected_for_application(self, selection, ref):
        require(isinstance(selection,Selection) and self.selections.get(selection.original_ref) == selection, 'trusted exact selection required')
        self.e.original(selection.original_ref)
        require(ref in selection.selected_refs and not selection.conflicts, 'lesson was not selected or has unresolved conflict')
        require(self.rules.get(ref) == self.selection_rules[selection.original_ref][ref], 'selected applicability rule changed')
        # Re-run current checks without converting a stale selection into authority.
        v = self.e.get(ref,'operational-lesson'); review = self.exact_review(ref)
        require(isinstance(review,ReviewedLesson) and review.original_sha256 == self.e.records[ref][1]
            and review.revision_ref == ref and review.disposition == 'reviewed-for-controlled-use' and review.fixture_only
            and review.scope_ref == self.e.scope and review.effective_state == 'local-admitted-current'
            and review.source_head == self.e.host.status['head'], 'lesson review became stale')
        require(self.e.host.now[0] < timestamp(v['payload']['expires_at']), 'lesson expired before application')
        require(selection.context.session_ref == self.e.host.session.session_ref and selection.context.source_head == self.e.host.status['head'], 'selection Session/cut became stale')
        return v
