#!/usr/bin/env python3
"""Five separately admitted AC04/N08 coverage roles; no native calls here."""
import json
from ac_runtime import read, sha, require
from ac_provenance_fidelity_runtime_v18 import Runtime as PreviousRuntime
from ac_coverage_runtime_v10 import CoverageRuntime as OriginalLiteralRuntime
from ac_outer_review_runtime_v14 import replace_outer, REVIEW
from ac_future_budget import FutureBudgetMixin

NONREVIEW = ('Emit exactly these13 top-level keys: job_id, strategy_id, arm, case_id, '
             'operation_trace, candidates, attack, handoff, budget_used, limits, selection, '
             'method_card, revision. Copy identity values from payload.job. Irrelevant '
             'selection/method_card/revision use the schema defaults. One exclusive first '
             'save; no output repair or native retry. Source-bound refusal is allowed.')


class Runtime(PreviousRuntime):
    def n08_plan(self):
        return read(self.p('coverage/n08-matched/PLAN.v19.json'))

    def coverage_plan(self):
        return super().coverage_plan() + self.n08_plan()

    def integrity(self):
        super().integrity()
        for path, digest in read(self.p('coverage/n08-matched/FREEZE.v19.json'))['sources'].items():
            require(sha(path) == digest, 'N08 matched-comparison source drift: ' + path)
        return True

    def budget(self):
        b = super().budget()
        contract = read(self.p('coverage/n08-matched/BUDGET.v19.json'))
        require(contract['authority'] == 'root-authored prospective protocol' and
                contract['later_cumulative_ceiling'] == b['ceiling'], 'Prospective root budget authority')
        actual_audits = sum(v['purpose'] == 'completion_audit' and
                           v['outcome'] == 'actual_spawn_observed' for v in self.invocations())
        additional = max(0, contract['required_total_completion_audit_spawns'] - actual_audits)
        b['prospective_total'] += additional - b['required_auditors_reserved']
        b['required_auditors_reserved'] = additional
        b['required_total_completion_audit_spawns'] = contract['required_total_completion_audit_spawns']
        return b

    def payload(self, j):
        v = super().payload(j)
        if j.get('n08_matched_coverage'):
            v['separate_n08_comparison_scope'] = {
                'prior_raw_outputs_and_grades_preserved': True,
                'earlier_method_id': 'N:N08',
                'unchanged_later_treatment_chain': 'COV-AC04-T-J0-*',
                'ordinary_ordering_control_method_id': 'O',
                'resource_limit': 'Matched declared caps and initial count, not equal hidden compute.'}
            if j['role'] != 'review':
                v['comparison_resource_contract'] = {
                    'search_slots': 6, 'proposal_candidate_count': 3,
                    'final_builder_candidate_cap': 1, 'condition': j['arm'],
                    'meaning': 'Separate prospective N08 comparison to unchanged valid later T chain.'}
        return v

    def literal(self, j, v):
        if not j.get('n08_matched_coverage'):
            return super().literal(j, v)
        s = OriginalLiteralRuntime.literal(self, j, v)
        if j['role'] != 'review':
            old = ('For AC04 create-exclusive sidecar raw/' + j['job_id'] +
                   '.arrangements.json before any function interpretation, then interpret, '
                   'swap local assembly/interpretation concerns once and record rejected arrangement;')
            s = s.replace(old, 'For this older N08 comparison, specify the required function first, '
                          'cross two mechanisms at a named interface and predict their interaction '
                          'benefit; produce exactly three initial candidates without an '
                          'arrangement-first sidecar or role swap;')
        return replace_outer(s, REVIEW if j['role'] == 'review' else NONREVIEW)

    def validate(self, j, v):
        super().validate(j, v)
        if j.get('n08_matched_coverage') and j['role'] == 'proposal':
            require(len(v['candidates']) == 3, 'Prospectively matched N08 initial candidate count is three')

    def start(self, jid):
        require(jid in {j['job_id'] for j in self.n08_plan()}, 'N08 coverage role IDs only')
        previous = PreviousRuntime(self.root)
        require(all(previous.state(j['job_id'])['terminal'] for j in previous.plan()),
                'Every previously admitted scored disposition must close')
        require(read(self.p('coverage/n08-matched/ADMISSION.v19.json'))['admit'] is True,
                'Actual-evidence N08 admission required')
        for k in ['a', 'b']:
            require(read(self.p('receipts/completion-audit-' + k + '.final.json'))['observation']
                    == 'actual_FINAL', 'Actual first completion round FINAL witness required')
        out = FutureBudgetMixin.admit_later(self, jid)
        out['task_name'] = 'acn08_' + str([j['job_id'] for j in self.n08_plan()].index(jid))
        return out

    def n08_status(self):
        states = {j['job_id']: self.state(j['job_id']) for j in self.n08_plan()}
        return {'counts': {k: sum(s['disposition'] == k for s in states.values())
                           for k in ['pending', 'admitted', 'spawned', 'finished', 'failed', 'gated']},
                'valid_finished': sum(s['valid'] for s in states.values()),
                'terminal': all(s['terminal'] for s in states.values()), 'budget': self.budget(),
                'ready': {k: [jid for jid in ids if jid in states] for k, ids in self.ready().items()}}


if __name__ == '__main__':
    import ac_source_completion_runtime_v16 as cli
    cli.Runtime = Runtime
    Runtime.source_completion_status = Runtime.n08_status
    cli.main()
