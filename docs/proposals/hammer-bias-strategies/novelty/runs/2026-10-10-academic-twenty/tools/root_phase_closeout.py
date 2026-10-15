#!/usr/bin/env python3
"""Root bookkeeping after actual observed FINALs; performs no model calls."""
import argparse
import json
from ac_runtime import read, save, sha, require, now


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('phase', choices=['post', 'source', 'provenance'])
    args = ap.parse_args()
    if args.phase == 'post':
        from ac_post_invalid_complete_runtime_v15 import Runtime
        r = Runtime()
        plan = r.post_invalid_plan()
        target = 'receipts/POST-INVALID-CLOSURE.v13.json'
        expected = 5
    elif args.phase == 'source':
        from ac_source_completion_runtime_v17 import Runtime
        r = Runtime()
        plan = r.source_completion_plan()
        target = 'receipts/SOURCE-COMPLETION-CLOSURE.v17.json'
        expected = 10
    else:
        from ac_provenance_fidelity_runtime_v18 import Runtime
        from verify_ac_provenance_v18 import check
        r = Runtime()
        plan = r.provenance_plan()
        target = 'receipts/PROVENANCE-FIDELITY-CLOSURE.v18.json'
        expected = 8
        transmission = check(r)
    require(len(plan) == expected, 'Exact admitted phase size required')
    require(all(r.state(j['job_id'])['terminal'] for j in r.plan()),
            'Every earlier and current admitted disposition must be terminal')
    states, witnesses, locks = {}, {}, {}
    for job in plan:
        jid = job['job_id']
        state = r.state(jid)
        states[jid] = state
        if state['disposition'] == 'finished':
            path = r.p('receipts/jobs/' + jid + '.native-final.json')
            witness = read(path)
            require(witness['observation'] == 'actual_FINAL' and
                    witness['handle'] == state['handle'],
                    'Actual native FINAL witness required: ' + jid)
            witnesses[jid] = {'path': str(path), 'sha256': sha(path),
                              'handle': witness['handle']}
            lock = r.p('locks/' + jid + '.first-bytes')
            if lock.exists():
                locks[jid] = {'path': str(lock), 'sha256': sha(lock)}
        elif state['disposition'] == 'gated':
            require(not state['actual_native_invocation'], 'Uncalled gate required')
        else:
            require(state['disposition'] == 'failed', 'Unsupported terminal state')
    verification = r.verify()
    require(verification['status'] == 'pass', 'Actual source/first-save integrity')
    budget = r.budget()
    require(budget['prospective_total'] <= budget['ceiling'], 'Binding live budget')
    closure = {'utc': now(), 'observation': 'actual_root_coordinated_closure',
               'phase': args.phase, 'scheduled_count': expected,
               'all_scheduled_terminal': True, 'actual_states': states,
               'actual_final_witnesses': witnesses, 'first_locks': locks,
               'verification': verification, 'budget': budget,
               'limits': ['Root directly coordinated native calls and observed FINALs; '
                          'no independently authenticated platform event export.',
                          'First invalids and gates remain preserved, not repairs.']}
    if args.phase == 'post':
        closure['all_five_terminal'] = True
    if args.phase == 'provenance':
        save(r.p('reports/PROVENANCE-FIDELITY-VERIFICATION.v1.json'), transmission)
        closure['literal_transmission_verification'] = transmission
        closure['checker_path'] = str(r.p('tools/verify_ac_provenance_v18.py'))
        closure['checker_sha256'] = sha(r.p('tools/verify_ac_provenance_v18.py'))
    save(r.p(target), closure)
    print(json.dumps({'saved': target, 'scheduled_count': expected,
                      'valid_finished': sum(s['valid'] for s in states.values()),
                      'budget': budget}))


if __name__ == '__main__':
    main()
