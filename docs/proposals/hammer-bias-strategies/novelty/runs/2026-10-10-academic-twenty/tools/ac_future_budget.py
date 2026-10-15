"""Prospective later-phase admission; immutable primary compiler stays intact.

No native calls. A separately frozen root protocol must authorize the ceiling.
"""
from ac_runtime import read, save, sha, require, now


class FutureBudgetMixin:
    def budget(self):
        amendment = read(self.p('coverage/BUDGET-AMENDMENT.v1.json'))
        require(amendment['authority'] == 'root-authored prospective protocol',
                'Expected explicit later-phase budget authority')
        actual = self.invocations()
        pending = sum(self.state(j['job_id'])['disposition'] in ['pending', 'admitted']
                      for j in self.plan())
        audits = max(0, 2 - sum(v['purpose'] == 'completion_audit' and
                               v['outcome'] == 'actual_spawn_observed' for v in actual))
        grammar_reserved = 0 if self.p('coverage/grammar/ADMISSION.v11.json').exists() else 14
        grammar_coordinator = 0 if any(v['invocation_id'] == 'grammar-coordinator-v11' and
                                       v['outcome'] == 'actual_spawn_observed' for v in actual) else 1
        return {'actual_native_calls': len(actual), 'remaining_scheduled_calls': pending,
                'required_auditors_reserved': audits, 'coordinator_remaining': 0,
                'conditional_grammar_roles_reserved': grammar_reserved,
                'conditional_grammar_coordinator_reserved': grammar_coordinator,
                'ceiling': amendment['later_cumulative_ceiling'],
                'original_protocol_ceiling_preserved': 260,
                'prospective_total': len(actual) + pending + audits + grammar_reserved + grammar_coordinator}

    def reserve_overhead(self, iid, purpose):
        require(purpose in ['coordinator', 'completion_audit', 'unplanned'], 'Overhead purpose')
        b = self.budget()
        reserved = purpose == 'completion_audit' and b['required_auditors_reserved'] > 0
        reserved |= iid == 'grammar-coordinator-v11' and b['conditional_grammar_coordinator_reserved'] > 0
        require(b['prospective_total'] + (0 if reserved else 1) <= b['ceiling'],
                'Later cumulative native-call ceiling exceeded')
        save(self.p('receipts/reservations/overhead-' + iid + '.json'), {
            'invocation_id': iid, 'purpose': purpose, 'status': 'pre_call_reserved_only',
            'utc_reserved': now(), 'budget_before_call': b, 'actual_call_not_yet_observed': True})
        return {'overhead_reserved': iid, 'purpose': purpose, 'budget': b}

    def admit_later(self, jid):
        self.integrity()
        require(all(self.state(j['job_id'])['terminal'] for j in self.original_plan()),
                'All original dispositions must close before later admission')
        require(jid not in {j['job_id'] for j in self.original_plan()},
                'Prospective adapter cannot admit or alter an original role')
        require(jid in self.ready()['ready'], 'Job not ready')
        b = self.budget()
        require(b['prospective_total'] <= b['ceiling'], 'Later cumulative budget exceeded')
        require(sum(self.state(j['job_id'])['disposition'] in ['admitted', 'spawned']
                    for j in self.plan()) < 2, 'Two live child-worker ceiling')
        j = self.job(jid)
        payload = self.payload(j)
        prompt = self.literal(j, payload)
        save(self.p('prompts/' + jid + '.payload.json'), payload)
        save(self.p('prompts/' + jid + '.txt'), prompt.encode())
        save(self.p('receipts/jobs/' + jid + '.admitted.json'), {
            'job_id': jid, 'utc': now(), 'terminal': False, 'valid': False,
            'prompt_sha256': sha(self.p('prompts/' + jid + '.txt')),
            'payload_sha256': sha(self.p('prompts/' + jid + '.payload.json'))})
        save(self.p('receipts/reservations/score-' + jid + '.json'), {
            'invocation_id': 'score-' + jid, 'job_id': jid, 'utc_reserved': now(),
            'status': 'pre_call_reserved_only', 'purpose': 'scheduled_job', 'budget_before_call': b})
        require(not j.get('followup_of'), 'Later coverage roles require fresh native handles')
        return {'job_id': jid,
                'task_name': 'accov_' + str([q['job_id'] for q in self.plan()].index(jid)),
                'message': 'Read ' + str(self.p('prompts/' + jid + '.txt')) +
                ' and perform exactly that one bounded native role. Save assigned JSON exclusively and return actual FINAL. No helpers or extra turns.',
                'call_type': 'spawn', 'target': None}
