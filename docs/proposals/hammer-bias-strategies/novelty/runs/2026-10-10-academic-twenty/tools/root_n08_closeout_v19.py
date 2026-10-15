#!/usr/bin/env python3
"""Pure root closeout after actual native FINAL observations; no model calls."""
import json
from ac_runtime import read, save, sha, require, now
from ac_n08_matched_runtime_v19 import Runtime

r = Runtime()
plan = r.n08_plan()
require(len(plan) == 5 and all(r.state(j['job_id'])['terminal'] for j in r.plan()),
        'All earlier and five new dispositions must be terminal')
states, witnesses, locks = {}, {}, {}
for j in plan:
    jid = j['job_id']
    state = r.state(jid)
    states[jid] = state
    if state['disposition'] == 'finished':
        path = r.p('receipts/jobs/' + jid + '.native-final.json')
        witness = read(path)
        require(witness['observation'] == 'actual_FINAL' and witness['handle'] == state['handle'],
                'Actual FINAL witness required: ' + jid)
        witnesses[jid] = {'path': str(path), 'sha256': sha(path), 'handle': witness['handle']}
        lock = r.p('locks/' + jid + '.first-bytes')
        if lock.exists():
            locks[jid] = {'path': str(lock), 'sha256': sha(lock)}
    else:
        require(state['disposition'] in ['gated', 'failed'], 'Unsupported terminal state')
verification = r.verify()
require(verification['status'] == 'pass', 'Source and first-save integrity required')
budget = r.budget()
require(budget['prospective_total'] <= budget['ceiling'], 'Live budget within310 required')
closure = {'utc': now(), 'observation': 'actual_root_coordinated_closure',
           'phase': 'n08_matched', 'scheduled_count': 5, 'all_scheduled_terminal': True,
           'actual_states': states, 'actual_final_witnesses': witnesses,
           'first_locks': locks, 'verification': verification, 'budget': budget,
           'limits': ['Fresh matched N08 comparison against unchanged later T chain.',
                      'Original 3-versus2 and later methodO ordering control remain distinct.',
                      'Actual root observations, not independently authenticated platform events.',
                      'Declared allowances do not attest equal hidden compute.']}
save(r.p('receipts/N08-MATCHED-CLOSURE.v19.json'), closure)
print(json.dumps({'scheduled_count': 5, 'valid_finished': sum(s['valid'] for s in states.values()),
                  'budget': budget}))
