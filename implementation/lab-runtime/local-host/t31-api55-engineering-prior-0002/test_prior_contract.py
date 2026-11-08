import copy
import importlib.util
from pathlib import Path
import unittest


PATH = Path(__file__).resolve().parents[4] / ('product/lab/release-candidates/v1/interface/'
    'api-integration-v55-t31-engineering-prior-0002/workflow_prior_input.py')
spec = importlib.util.spec_from_file_location('t31_prior_contract_test', PATH)
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)


def witness():
    body = {'kind': 'generated-output', 'node_id': 'generated-output:local-design',
            'scope_ref': 'project:local', 'authority_effect': 'none', 'payload': {}}
    raw = P.canonical(body)
    header = {'scope_ref': 'project:local', 'identity_ref': body['node_id'],
              'version_ref': body['node_id'] + '@candidate.1',
              'carrier_ref': 'cal.artifact-type.generated-output/v2',
              'byte_sha256': P.sha(raw)}
    cut = {'store_ref': 'local-source'}
    actor = {'principal_ref': 'principal:local'}
    event = {'run_ref': 'workflow-run:local', 'source_cut': cut, 'actor': actor,
             'transition_ref': 'transition:engineering:designed',
             'from_state': 'prepared', 'to_state': 'designed',
             'output_artifact_refs': [header]}
    event_sha = P.sha(P.canonical(event))
    run = {'run_ref': event['run_ref'], 'state': 'designed', 'source_cut': cut,
           'actor': actor, 'work': {'version_ref': 'work:local@1'},
           'event_bindings': [{'ref': 'workflow-event:' + event_sha,
                               'sha256': event_sha}]}
    current_raw = P.canonical(run)
    message = {'transition_ref': 'transition:engineering:implemented',
               'source_cut': cut, 'run_binding': {'sha256': P.sha(current_raw)}}
    transaction = {'sequence': 1, 'event': event,
                   'next_run_sha256': P.sha(current_raw),
                   'before_run_sha256': 'a' * 64,
                   'producer_receipt_bindings': [{'ref': 'receipt:design', 'sha256': 'b' * 64}],
                   'output_artifact_refs': [header]}
    head = {'sequence': 1, 'run_sha256': P.sha(current_raw)}
    class Result:
        state = 'completed-sealed'
        route_refs = ('transition:engineering:designed',)
        run_binding = {'sha256': 'a' * 64}
        work_ref = 'work:local@1'
        source_cut = cut
    row = {'artifact': header, 'original_binding': {'sha256': P.sha(raw)}, 'raw': raw}
    receipts = [{'original_binding': {'ref': 'receipt:design', 'sha256': 'b' * 64}}]
    return {'message': message, 'run': run, 'head': head,
            'current_raw': current_raw, 'transaction': transaction,
            'result': Result(), 'producer_principal': 'principal:local',
            'row': row, 'receipts': receipts, 'header': header}


class PriorContractTests(unittest.TestCase):
    def test_exact_committed_private_original(self):
        self.assertEqual(P.verify_prior_design(**witness())['node_id'],
                         'generated-output:local-design')

    def test_uncommitted_or_foreign_output_refused(self):
        for mutation in ('zero_sequence', 'foreign_event', 'wrong_slot',
                         'changed_bytes', 'wrong_work', 'wrong_cut', 'wrong_principal',
                         'wrong_receipt'):
            with self.subTest(mutation=mutation):
                row = witness()
                if mutation == 'zero_sequence': row['head']['sequence'] = 0
                if mutation == 'foreign_event':
                    row['transaction']['event']['output_artifact_refs'] = []
                if mutation == 'wrong_slot': row['result'].route_refs = ('transition:research:designed',)
                if mutation == 'changed_bytes': row['row']['raw'] += b' '
                if mutation == 'wrong_work': row['result'].work_ref = 'work:foreign@1'
                if mutation == 'wrong_cut': row['result'].source_cut = {'store_ref': 'foreign'}
                if mutation == 'wrong_principal': row['producer_principal'] = 'principal:foreign'
                if mutation == 'wrong_receipt':
                    row['receipts'][0]['original_binding']['sha256'] = 'c' * 64
                with self.assertRaises(ValueError):
                    P.verify_prior_design(**row)

    def test_source_current_is_not_implied(self):
        row = witness()
        self.assertNotIn('admitted', P.verify_prior_design(**row)['authority_effect'])


if __name__ == '__main__': unittest.main()
