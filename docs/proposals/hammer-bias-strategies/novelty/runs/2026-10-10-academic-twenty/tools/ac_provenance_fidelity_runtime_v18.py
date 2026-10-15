#!/usr/bin/env python3
"""Separate eight-role provenance transmission coverage; no model calls here."""
import json
from ac_runtime import read, sha, require
from ac_source_completion_runtime_v17 import Runtime as PreviousRuntime
from ac_coverage_runtime_v10 import CoverageRuntime as OriginalLiteralRuntime
from ac_outer_review_runtime_v14 import replace_outer, REVIEW
from ac_future_budget import FutureBudgetMixin

NONREVIEW = ('Emit exactly these13 top-level keys: job_id, strategy_id, arm, case_id, '
             'operation_trace, candidates, attack, handoff, budget_used, limits, selection, '
             'method_card, revision. Copy identity values from payload.job. Store the '
             'provenance capsule inside the existing handoff.summary JSON string, never '
             'as an added top-level field. Irrelevant selection/method_card/revision '
             'use existing empty defaults. One exclusive first save; no repair or retry.')


class Runtime(PreviousRuntime):
    def provenance_plan(self):
        return read(self.p('coverage/provenance-fidelity/PLAN.v18.json'))

    def coverage_plan(self):
        return super().coverage_plan() + self.provenance_plan()

    def integrity(self):
        super().integrity()
        for path, digest in read(self.p('coverage/provenance-fidelity/FREEZE.v18.json'))['sources'].items():
            require(sha(path) == digest, 'Provenance fidelity source drift: ' + path)
        return True

    def budget(self):
        b = super().budget()
        amendment = read(self.p('coverage/BUDGET-AMENDMENT.v2.json'))
        require(amendment['authority'] == 'root-authored prospective protocol',
                'Separate root-owned budget authority required')
        b['previous_later_ceiling_preserved'] = b['ceiling']
        b['ceiling'] = amendment['later_cumulative_ceiling']
        return b

    def payload(self, j):
        v = super().payload(j)
        if j.get('provenance_fidelity_coverage'):
            v['provenance_fidelity_scope'] = {
                'separate_later_coverage': True,
                'previous_raw_outputs_and_grades_unchanged': True,
                'summary_only_builder': True,
                'resource_limit': 'Larger text cap transports unchanged literal provenance; not matched efficacy evidence.'}
            if j['role'] == 'exchange':
                v['required_transmission_capsule'] = read(self.p(
                    'coverage/provenance-fidelity/capsules/' + j['arm'] + '.json'))
        return v

    def literal(self, j, v):
        if not j.get('provenance_fidelity_coverage'):
            return super().literal(j, v)
        return replace_outer(OriginalLiteralRuntime.literal(self, j, v),
                             REVIEW if j['role'] == 'review' else NONREVIEW)

    def validate_summary(self, j, v, received_text=None):
        if j.get('provenance_fidelity_coverage') and j['role'] in ['exchange', 'builder']:
            summary = json.loads(v['handoff']['summary'])
            require(isinstance(summary, dict) and set(summary) ==
                    {'capsule', 'construction', 'audit', 'limits'},
                    'Selected summary must contain exactly capsule/construction/audit/limits')
            expected = read(self.p('coverage/provenance-fidelity/capsules/' + j['arm'] + '.json'))
            require(summary['capsule'] == expected,
                    'Exact precursor arrays and source provenance must survive the selected summary')
            require(isinstance(summary['construction'], str) and summary['construction'].strip(),
                    'Construction or source-bound refusal required')
            require(isinstance(summary['audit'], str) and summary['audit'].strip(),
                    'Actual source/overlap assessment required')
            require(isinstance(summary['limits'], list) and summary['limits'],
                    'Explicit interpretation limits required')
            if j['role'] == 'builder':
                require(received_text is not None and json.loads(received_text)['capsule'] == summary['capsule'],
                        'Builder must retain the actually received capsule')

    def validate(self, j, v):
        super().validate(j, v)
        received_text = None
        if j.get('provenance_fidelity_coverage') and j['role'] == 'builder':
            packet = read(self.p('prompts/' + j['job_id'] + '.payload.json'))
            require('received_roles' not in packet and 'required_transmission_capsule' not in packet,
                    'Builder receives only the selected summary, not full upstream roles or expected capsule')
            received_text = packet['received_handoffs'][j['dependencies'][0]]
        self.validate_summary(j, v, received_text)

    def start(self, jid):
        require(jid in {j['job_id'] for j in self.provenance_plan()}, 'Provenance role IDs only')
        previous = PreviousRuntime(self.root)
        require(all(previous.state(j['job_id'])['terminal'] for j in previous.plan()),
                'All earlier phases must actually close')
        require(read(self.p('coverage/provenance-fidelity/ADMISSION.v18.json'))['admit'] is True,
                'Actual-evidence provenance admission required')
        require(read(self.p('receipts/SOURCE-COMPLETION-CLOSURE.v17.json'))['all_scheduled_terminal'],
                'Actual previous source closure required')
        out = FutureBudgetMixin.admit_later(self, jid)
        out['task_name'] = 'acprov_' + str([j['job_id'] for j in self.provenance_plan()].index(jid))
        return out

    def provenance_status(self):
        states = {j['job_id']: self.state(j['job_id']) for j in self.provenance_plan()}
        return {'counts': {k: sum(s['disposition'] == k for s in states.values())
                           for k in ['pending', 'admitted', 'spawned', 'finished', 'failed', 'gated']},
                'valid_finished': sum(s['valid'] for s in states.values()),
                'terminal': all(s['terminal'] for s in states.values()), 'budget': self.budget(),
                'ready': {k: [jid for jid in ids if jid in states] for k, ids in self.ready().items()}}


if __name__ == '__main__':
    import ac_source_completion_runtime_v16 as cli
    cli.Runtime = Runtime
    # Reuse the existing CLI without changing prior runtime bytes.
    Runtime.source_completion_status = Runtime.provenance_status
    cli.main()
